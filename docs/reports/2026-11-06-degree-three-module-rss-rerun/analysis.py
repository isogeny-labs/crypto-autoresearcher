"""Frozen analysis for MEAS-20261106-degree3-module-rss-rerun, protocol v3 (written before any v3 data).

usage: analysis.py DATADIR  -> prints the result JSON on stdout

Reads <arm>.summary.json for arms default-a, threads1, default-b and host.json.
Primary metric (v3, amendment A2): peak_lean_anon_plus_swap_kb, the max over
0.5 s samples of the lean process's RssAnon + VmSwap: its anonymous footprint
whether resident or swapped. (v2 used RssAnon alone, which RAM caps once the
process swaps.) A run counts only if exit == 0, killed_by_watchdog is false
and a lean process was observed (peak > 0); otherwise its peak is a lower
bound and the claims it feeds are inconclusive.

C1 (exact): the peak of default-a, and of default-b, as measured.
C-aa: |default-a - default-b|; the noise floor for C2.
C2 (comparative, C-threads): threads1 lowers the peak if
    default-a - threads1 > max(C-aa spread, 256 MiB).
C3 (heuristic): margin_kb = host MemTotal_kb + SwapTotal_kb - max(default peaks);
    a margin under 1 GiB is reported as fragile. min_headroom_kb (lowest
    MemAvailable + SwapFree seen during the default arms) is reported beside it.
"""
import json, sys
from pathlib import Path

MIB = 1024
M = "peak_lean_anon_plus_swap_kb"
d = Path(sys.argv[1])
arms = {a: json.loads((d / f"{a}.summary.json").read_text()) for a in ("default-a", "threads1", "default-b")}
host = json.loads((d / "host.json").read_text())
valid = {a: s["exit"] == 0 and not s["killed_by_watchdog"] and s[M] > 0 for a, s in arms.items()}
peak = {a: s[M] for a, s in arms.items()}
out = {"valid": valid, M: peak,
       "peak_lean_rss_anon_kb": {a: s["peak_lean_rss_anon_kb"] for a, s in arms.items()},
       "peak_lean_vm_swap_kb": {a: s["peak_lean_vm_swap_kb"] for a, s in arms.items()},
       "killed_externally": {a: s["killed_externally"] for a, s in arms.items()},
       "min_headroom_kb": {a: s["min_headroom_kb"] for a, s in arms.items()},
       "wall_s": {a: s["wall_s"] for a, s in arms.items()}}
out["C1"] = {"verdict": "supported_within_scope" if valid["default-a"] and valid["default-b"] else "inconclusive",
             "peak_default_a_kb": peak["default-a"], "peak_default_b_kb": peak["default-b"]}
aa = abs(peak["default-a"] - peak["default-b"])
out["C_aa_spread_kb"] = aa
thr = max(aa, 256 * MIB)
diff = peak["default-a"] - peak["threads1"]
if not (valid["default-a"] and valid["threads1"] and valid["default-b"]):
    c2 = "invalid_measurement"
elif diff > thr:
    c2 = "supported_within_scope"
else:
    c2 = "within_control_distribution"
out["C2"] = {"verdict": c2, "default_minus_threads1_kb": diff, "threshold_kb": thr}
if valid["default-a"] and valid["default-b"]:
    m = host["MemTotal_kb"] + host["SwapTotal_kb"] - max(peak["default-a"], peak["default-b"])
    out["C3"] = {"margin_kb": m, "fragile": m < 1024 * MIB,
                 "MemTotal_kb": host["MemTotal_kb"], "SwapTotal_kb": host["SwapTotal_kb"],
                 "min_headroom_default_kb": min(arms["default-a"]["min_headroom_kb"],
                                                arms["default-b"]["min_headroom_kb"])}
else:
    out["C3"] = {"verdict": "inconclusive"}
print(json.dumps(out, indent=1))
