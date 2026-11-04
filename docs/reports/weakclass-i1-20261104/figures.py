"""I1 rerun: u per weak class vs paired ordinary (left), and the u histogram of 90 fresh ordinary curves vs uniform (right)."""
import json, numpy as np, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; ink, grid = "#3b3b3a", "#e4e3dd"
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw=dict(width_ratios=[1.2, 1]))
a1.axhspan(0.05, 0.95, color="#f3f2ee", zorder=0)
for j, (K, nm, col) in enumerate((("A", "anomalous", "#2a78d6"), ("B", "small k", "#eb6834"), ("C", "j=0", "#1baf7a"))):
    a1.scatter([j - .12]*9, [r["I1_u"] for r in rows if r["cls"] == K], color=col, s=22, zorder=3)
    a1.scatter([j + .12]*9, [r["I1_u"] for r in rows if r.get("pair") == K], facecolors="none", edgecolors="#8a8985", s=22, zorder=3)
a1.set_xticks(range(3)); a1.set_xticklabels(["anomalous", "small k", "j=0"], fontsize=8, color=ink)
a1.set_ylabel("within-null percentile u (200 draws)", color=ink); a1.set_title("weak (filled) vs paired ordinary (open)", fontsize=8.5, color=ink, loc="left")
E = [r["I1_u"] for r in rows if r["cls"] == "E"]
a2.hist(E, bins=np.linspace(0, 1, 11), color="#2a78d6", edgecolor="white", linewidth=2)
a2.axhline(len(E) / 10, color=ink, lw=1, ls="--"); a2.text(0.02, len(E)/10 + 0.3, "uniform", color=ink, fontsize=7.5)
a2.set_xlabel("u", color=ink); a2.set_title(f"{len(E)} fresh ordinary curves: calibrated", fontsize=8.5, color=ink, loc="left")
for ax in (a1, a2):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
    ax.tick_params(colors=ink, labelsize=7.5)
fig.tight_layout(); fig.savefig("i1-rerun.svg")
