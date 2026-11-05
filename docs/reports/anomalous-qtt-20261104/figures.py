"""ECDF of within-null percentiles u_X (primary metric) for anomalous vs ordinary curves; motivating curve marked."""
import json, numpy as np, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
v = json.load(open("verdict.json")); ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot([0, 1], [0, 1], color=grid, lw=1.5, ls="--")
ax.text(0.62, 0.55, "uniform (no effect)", color=ink, fontsize=7.5, rotation=27)
for g, col in (("anomalous", "#2a78d6"), ("ordinary", "#eb6834")):
    u = np.sort([c["u_X"] for c in v["per_curve"] if c["group"] == g])
    ax.step(u, np.arange(1, len(u) + 1) / len(u), where="post", color=col, lw=2,
            label=f"{g} (n={len(u)}, mean u = {u.mean():.2f})")
m = v["motivating"][0]
ax.axvline(m["u_X"], color=ink, lw=1, ls=":")
ax.text(m["u_X"] + 0.01, 0.9, f"motivating curve p={m['p']} (excluded): u = {m['u_X']:.3f}", color=ink, fontsize=7.5)
ax.set_xlabel("within-null percentile of X's QTT parameter count (low = more structure)", color=ink)
ax.set_ylabel("fraction of curves", color=ink)
ax.grid(color=grid, lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title(f"Anomalous vs ordinary curves, primes 37-127: verdict {v['verdict']} (stratified permutation p = {v['p_perm']:.2f})", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig("anomalous-ecdf.svg")
