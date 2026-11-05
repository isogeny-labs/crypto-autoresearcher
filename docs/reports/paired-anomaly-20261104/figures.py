"""u distributions by class (fresh replication), with the earlier anomalous paired set for reference."""
import json, numpy as np, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.3))
names = [("E", "independent\nordinary (E)", "#8a8985"), ("D", "paired\nordinary (D)", "#eb6834"), ("A", "anomalous", "#2a78d6"), ("B", "small k", "#7f5ccf"), ("C", "j=0, zeta-\nstable FB", "#1baf7a")]
ax.axhline(0.5, color=grid, lw=3, zorder=0)
for i, (K, nm, col) in enumerate(names):
    u = [r["I1_u"] for r in rows if r["cls"] == K]
    ax.scatter(i + np.random.default_rng(i).uniform(-0.18, 0.18, len(u)), u, s=9, color=col, alpha=0.7)
    ax.plot([i - 0.3, i + 0.3], [np.mean(u)] * 2, color=ink, lw=2)
    ax.text(i, 1.04, f"n={len(u)}\nmean {np.mean(u):.2f}", ha="center", fontsize=7, color=ink)
ax.set_xticks(range(len(names))); ax.set_xticklabels([n for _, n, _ in names], fontsize=7.5, color=ink)
ax.set_ylabel("I1 within-null percentile u", color=ink); ax.set_ylim(-0.03, 1.15)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=7.5)
ax.set_title("Paired-curve anomaly NOT REPLICATED (D vs E, p = 0.65); j=0 zeta-stable FB sits low (p < 1e-5)", fontsize=8.5, color=ink, loc="left", pad=22)
fig.tight_layout(); fig.savefig("paired-replication.svg")
