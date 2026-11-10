#!/usr/bin/env python3
"""Leave-one-out A/A: each of the 20 null replicates of every curve as a pseudo-structured set against the
other 19, per powered cell (44 x 20 = 880 comparisons); flag rule of the spec (|kappa-1| >= 0.10 and |z| > 4);
also how many such pseudo-cells would satisfy |kappa-1| < 0.05 (null-like). usage: loo_check.py <jobs> <out>"""
import json, math, sys
from collections import defaultdict
cells = defaultdict(list)
for l in open(sys.argv[1]):
    r = json.loads(l)
    if r["status"] == "ok":
        cells[r["cell"]].append(r)
def mean(x): return sum(x) / len(x)
def svar(x):
    m = mean(x); return sum((v - m) ** 2 for v in x) / (len(x) - 1)
flags = comps = 0; maxabsz = 0; zs = []
for cid, recs in cells.items():
    if cid == "b20-r3-n4096":
        continue
    M_all = sum(mean(r["null_C"]) for r in recs)
    if M_all < 2500:
        continue
    for j in range(20):
        S = sum(r["null_C"][j] for r in recs)
        others = [[v for i, v in enumerate(r["null_C"]) if i != j] for r in recs]
        M = sum(mean(o) for o in others); V = sum(svar(o) for o in others)
        k = S / M; z = (S - M) / math.sqrt(V * (1 + 1 / 19))
        comps += 1; zs.append(z); maxabsz = max(maxabsz, abs(z))
        if abs(k - 1) >= 0.10 and abs(z) > 4:
            flags += 1
res = {"comparisons": comps, "flagged": flags, "max_abs_z": maxabsz, "mean_z2": sum(z * z for z in zs) / len(zs)}
json.dump(res, open(sys.argv[2], "w"), indent=1); print(res)
