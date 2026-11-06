"""Run one command and sample its memory every 0.5 s; write samples and a summary.

usage: measure.py LABEL OUTDIR -- cmd...

Samples, for every process in the command's tree, VmRSS; for the `lean`
process, RssAnon, RssFile, VmSwap, VmHWM and Threads; and host MemAvailable
and SwapFree. If MemAvailable falls below FLOOR_KB the tree is killed so the
job survives, and the peak is then reported as a lower bound
(killed_by_watchdog=True). Standard library only.
"""
import json, os, resource, signal, subprocess, sys, time

FLOOR_KB = 300 * 1024
label, outdir = sys.argv[1], sys.argv[2]
cmd = sys.argv[sys.argv.index("--") + 1:]


def meminfo():
    d = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":", 1)
        d[k] = int(v.split()[0])
    return d


def tree(root):
    kids = {}
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                ppid = int(open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(p))
            except (OSError, IndexError, ValueError):
                pass
    out, stack = [], [root]
    while stack:
        q = stack.pop()
        out.append(q)
        stack += kids.get(q, [])
    return out


def status(pid):
    d = {}
    try:
        for line in open(f"/proc/{pid}/status"):
            k, _, v = line.partition(":")
            if k in ("Name", "VmRSS", "VmHWM", "RssAnon", "RssFile", "VmSwap", "Threads"):
                d[k] = v.split()[0] if v.split() else ""
    except OSError:
        pass
    return d


t0 = time.time()
log = open(f"{outdir}/{label}.log", "w")
p = subprocess.Popen(cmd, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
cols = ["t_s", "tree_rss_kb", "lean_rss_anon_kb", "lean_rss_file_kb", "lean_vm_swap_kb",
        "lean_vm_hwm_kb", "lean_threads", "mem_available_kb", "swap_free_kb"]
samples = open(f"{outdir}/{label}.samples.tsv", "w")
samples.write("\t".join(cols) + "\n")
peak = dict.fromkeys(cols[1:7], 0)
min_avail = min_swap_free = 1 << 62
killed = False
while p.poll() is None:
    row = dict.fromkeys(cols[1:7], 0)
    for q in tree(p.pid):
        s = status(q)
        row["tree_rss_kb"] += int(s.get("VmRSS") or 0)
        if s.get("Name") == "lean":
            row["lean_rss_anon_kb"] = max(row["lean_rss_anon_kb"], int(s.get("RssAnon") or 0))
            row["lean_rss_file_kb"] = max(row["lean_rss_file_kb"], int(s.get("RssFile") or 0))
            row["lean_vm_swap_kb"] = max(row["lean_vm_swap_kb"], int(s.get("VmSwap") or 0))
            row["lean_vm_hwm_kb"] = max(row["lean_vm_hwm_kb"], int(s.get("VmHWM") or 0))
            row["lean_threads"] = max(row["lean_threads"], int(s.get("Threads") or 0))
    mi = meminfo()
    for k in peak:
        peak[k] = max(peak[k], row[k])
    min_avail = min(min_avail, mi["MemAvailable"])
    min_swap_free = min(min_swap_free, mi.get("SwapFree", 0))
    samples.write("\t".join([f"{time.time() - t0:.1f}"] + [str(row[k]) for k in cols[1:7]]
                            + [str(mi["MemAvailable"]), str(mi.get("SwapFree", 0))]) + "\n")
    samples.flush()
    if mi["MemAvailable"] < FLOOR_KB and not killed:
        killed = True
        os.killpg(p.pid, signal.SIGKILL)
    time.sleep(0.5)
rc = p.wait()
summary = {"label": label, "cmd": cmd, "env_LEAN_NUM_THREADS": os.environ.get("LEAN_NUM_THREADS"),
           "exit": rc, "killed_by_watchdog": killed, "wall_s": round(time.time() - t0, 1),
           **{f"peak_{k}": v for k, v in peak.items()},
           "rusage_children_maxrss_kb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
           "min_mem_available_kb": min_avail, "min_swap_free_kb": min_swap_free}
json.dump(summary, open(f"{outdir}/{label}.summary.json", "w"), indent=1)
print(json.dumps(summary))
