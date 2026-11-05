"""Draw the per-instance log2(candidate / chain) F4-cell ratios recorded in run-001's analysis.json."""
import json
import sys

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
a = json.load(open(src))
comps = [("C-mono", "monolithic / chain", "o", "#1f77b4"), ("C-tree", "tree / chain", "s", "#d62728"), ("C-aa", "chain-aa / chain (A/A)", "^", "#7f7f7f")]
primes = sorted(a["comparisons"]["C-mono"]["per_prime"], key=int)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
for k, (cid, label, marker, color) in enumerate(comps):
    for j, p in enumerate(primes):
        xs = a["comparisons"][cid]["per_prime"][p]["log2_ratios"]
        xpos = [j + (k - 1) * 0.22 + (i - len(xs) / 2) * 0.012 for i in range(len(xs))]
        ax.scatter(xpos, xs, marker=marker, s=18, color=color, label=label if j == 0 else None)
ax.axhline(0, color="grey", lw=0.8)
ax.set_xticks(range(len(primes)), [f"p = {p}" for p in primes])
ax.set_ylabel("log2(F4 matrix cells, arm / chain)")
ax.set_title("Per-instance F4 cells relative to chain, n = m = 3 over F_{p^3}\n(10 instances per prime; run-001)")
ax.legend(loc="center right", fontsize=8)
fig.tight_layout()
fig.savefig(out)
