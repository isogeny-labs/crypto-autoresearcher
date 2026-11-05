"""Matched presentations of Weil-descended Semaev systems (n = m = 3) under msolve F4.

Runs the frozen protocol in this directory: for every instance, every arm builds
the same decomposition system in its presentation (descent.py) and solves it
with the same msolve binary, flags and thread count; arms run in a per-instance
shuffled order.  Counted F4 matrix sizes are parsed from msolve's verbose
round table; relations are lifted and checked by point addition.

    PYTHONPATH=src python3 research/gag_presentation_matched_20261031/driver.py \
        --protocol research/gag_presentation_matched_20261031/protocol.json \
        --out research/gag_presentation_matched_20261031/runs/<fresh-run-id>

The output directory must not exist.  Nothing is resumed in place: a rerun is a
new directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

from crypto_autoresearcher.index_calculus import descent as dsc
from crypto_autoresearcher.index_calculus import msolve as ms

ROUND = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+x\s+(\d+)\s+([\d.]+)%")
FLAGS = ["-c", "0", "-P", "1", "-t", "1", "-v", "2"]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def instance(p: int, index: int):
    """The frozen instance rule (protocol.instance_rule)."""
    F = dsc.ExtField(p, 3, seed=index)
    E = dsc.ExtCurve.random(F, random.Random(f"curve|{p}|{index}"))
    R, xs = dsc.planted_target(E, 3, random.Random(f"target|{p}|{index}"))
    return F, E, R, xs


def parse_rounds(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        mt = ROUND.match(line)
        if mt:
            deg, sel, pairs, rows, cols, dens = mt.groups()
            out.append({"deg": int(deg), "sel": int(sel), "pairs": int(pairs),
                        "rows": int(rows), "cols": int(cols), "density_pct": float(dens)})
    return out


def execute(exe: str, E, R, arm: dict, inst_id: str, raw_dir: str, exec_id: str,
            max_attempts: int, timeout: float) -> dict:
    form_rng = random.Random(f"form|{arm['parameters']['form_seed']}|{inst_id}")
    topology = arm["parameters"]["topology"]
    attempts, rounds_all, wall = [], [], 0.0
    t0 = time.perf_counter()
    status, run = "failed", None
    for attempt in range(1, max_attempts + 1):
        tb = time.perf_counter()
        system = dsc.descent_system(E, R[0], 3, form_rng, topology)
        build = time.perf_counter() - tb
        with tempfile.TemporaryDirectory(prefix="gagpm-") as tmp:
            inp, outp = os.path.join(tmp, "in.ms"), os.path.join(tmp, "out.ms")
            with open(inp, "w") as fh:
                fh.write(system.render())
            ts = time.perf_counter()
            try:
                proc = subprocess.run([exe, *FLAGS, "-f", inp, "-o", outp],
                                      capture_output=True, text=True, timeout=timeout)
                rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired as exc:
                rc, stdout, stderr = None, exc.stdout or "", exc.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode(errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode(errors="replace")
            secs = time.perf_counter() - ts
            text = open(outp).read() if os.path.exists(outp) else ""
        base = os.path.join(raw_dir, f"{exec_id}.a{attempt}")
        with open(base + ".stdout", "w") as fh:
            fh.write(stdout)
        with open(base + ".stderr", "w") as fh:
            fh.write(stderr)
        with open(base + ".out", "w") as fh:
            fh.write(text)
        with open(base + ".in.sha256", "w") as fh:
            fh.write(hashlib.sha256(system.render().encode()).hexdigest() + "\n")
        rounds = parse_rounds(stdout)
        rounds_all.extend(rounds)
        wall += secs
        if rc is None:
            status = "timeout"
        elif rc != 0:
            status = "crashed"
        else:
            run = ms.parse_output(text, system.names, system.p)
            status = run.status
        attempts.append({"attempt": attempt, "status": status, "returncode": rc,
                         "msolve_seconds": secs, "build_seconds": build,
                         "f4_rounds": len(rounds),
                         "f4_cells": sum(r["rows"] * r["cols"] for r in rounds)})
        if status != "failed":
            break
    relations, unlifted = set(), 0
    if run is not None and status in ("ok", "no_solution"):
        for vals in run.solutions:
            rel = dsc.signed_relation(E, vals[:3], R)
            if rel is None:
                unlifted += 1
            else:
                relations.add(rel)
    return {
        "status": status,
        "attempts": attempts,
        "attempt_count": len(attempts),
        "f4_cells": sum(r["rows"] * r["cols"] for r in rounds_all),
        "f4_rows": sum(r["rows"] for r in rounds_all),
        "f4_rounds": len(rounds_all),
        "f4_max_deg": max((r["deg"] for r in rounds_all), default=None),
        "ideal_degree": run.degree if run is not None else None,
        "rational_solutions": len(run.solutions) if run is not None else None,
        "unlifted": unlifted,
        "relations": sorted([list(map(list, r)) for r in relations]),
        "msolve_seconds": wall,
        "execution_seconds": time.perf_counter() - t0,
    }


def environment(exe: str) -> dict:
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

    cpu = ""
    try:
        with open("/proc/cpuinfo") as fh:
            cpu = next((l.split(":", 1)[1].strip() for l in fh if l.startswith("model name")), "")
    except OSError:
        pass
    return {
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
        "python": sys.version,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "cpu_model": cpu,
        "nproc": os.cpu_count(),
        "msolve_path": exe,
        "msolve_sha256": sha256_file(exe),
        "msolve_flags": FLAGS,
        "loadavg_start": os.getloadavg(),
    }


def load_design(protocol_path: str, proto: dict) -> dict:
    """links.design is '<path> sha256:<hex>'; the file must match its frozen hash."""
    import hashlib
    import os
    path, digest = proto["links"]["design"].rsplit(" sha256:", 1)
    local = os.path.join(os.path.dirname(os.path.abspath(protocol_path)), os.path.basename(path))
    data = open(local, "rb").read()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit(f"design.json does not match its frozen sha256 {digest}")
    return json.loads(data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.protocol) as fh:
        proto = json.load(fh)
    if proto["freeze"]["status"] != "frozen":
        print("refusing: protocol is not frozen", file=sys.stderr)
        return 2
    if os.path.exists(args.out):
        print(f"refusing: {args.out} exists (runs are never resumed in place)", file=sys.stderr)
        return 2
    exe = ms.msolve_path()
    if exe is None:
        print("msolve not found", file=sys.stderr)
        return 2
    design = load_design(args.protocol, proto)
    pinned = design["msolve_sha256"]
    if sha256_file(exe) != pinned:
        print(f"refusing: msolve sha256 differs from the frozen {pinned}", file=sys.stderr)
        return 2
    raw_dir = os.path.join(args.out, "raw")
    os.makedirs(raw_dir)
    env = environment(exe)
    env["protocol_sha256"] = proto["freeze"]["protocol_sha256"]
    env["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    arms = {a["id"]: a for a in proto["arms"]}
    rows_path = os.path.join(args.out, "rows.jsonl")
    plan = [(design["warmup"]["prime"], design["warmup"]["index"], True)]
    plan += [(p, i, False) for p in design["primes"] for i in range(design["instances_per_prime"])]
    n = 0
    with open(rows_path, "w") as rows:
        for p, i, warm in plan:
            inst_id = f"p{p}-i{i}"
            F, E, R, xs = instance(p, i)
            planted = dsc.signed_relation(E, xs, R)
            order = sorted(arms)
            random.Random(f"order|{inst_id}").shuffle(order)
            for pos, arm_id in enumerate(order):
                n += 1
                exec_id = f"{n:04d}-{inst_id}-{arm_id}"
                res = execute(exe, E, R, arms[arm_id], inst_id, raw_dir, exec_id,
                              design["max_attempts"], proto["execution"]["timeout_seconds"])
                row = {"exec_id": exec_id, "arm": arm_id, "instance": inst_id, "prime": p,
                       "index": i, "warmup": warm, "order_position": pos,
                       "modulus": F.modulus, "planted_x": sorted(xs),
                       "planted_relation": list(map(list, planted)) if planted else None,
                       "planted_found": (list(map(list, planted)) in res["relations"])
                       if planted else False,
                       "loadavg": os.getloadavg(), **res}
                rows.write(json.dumps(row) + "\n")
                rows.flush()
                print(f"{exec_id} {res['status']} cells={res['f4_cells']} "
                      f"attempts={res['attempt_count']} t={res['msolve_seconds']:.3f}", flush=True)
    env["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    env["loadavg_end"] = os.getloadavg()
    env["executions"] = n
    with open(os.path.join(args.out, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2)
    shutil.copy(args.protocol, os.path.join(args.out, "protocol.used.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
