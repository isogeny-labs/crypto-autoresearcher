"""Within-null percentile u per curve, by instrument and class (weak curves vs their paired ordinary curves)."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; ink, grid = "#3b3b3a", "#e4e3dd"
fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.2), sharey=True)
names = {"I1": "I1 character sum", "I2": "I2 m=2 sumset yield", "I3": "I3 QTT (p ~ 2^10)"}
cols = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
for ax, I in zip(axs, ("I1", "I2", "I3")):
    ax.axhspan(0.05, 0.95, color="#f3f2ee", zorder=0)
    for j, K in enumerate("ABC"):
        w = [r[f"{I}_u"] for r in rows if r["cls"] == K and f"{I}_u" in r]
        d = [r[f"{I}_u"] for r in rows if r.get("pair") == K and f"{I}_u" in r]
        ax.scatter([j - 0.12] * len(w), w, color=cols[K], s=22, zorder=3, label={"A": "anomalous", "B": "small embedding degree", "C": "j=0, zeta-stable FB"}[K] if I == "I1" else None)
        ax.scatter([j + 0.12] * len(d), d, facecolors="none", edgecolors="#8a8985", s=22, zorder=3, label="paired ordinary" if (I == "I1" and K == "A") else None)
    ax.set_xticks(range(3)); ax.set_xticklabels(["anomalous", "small k", "j=0"], fontsize=7.5, color=ink)
    ax.set_title(names[I], fontsize=8.5, color=ink, loc="left"); ax.tick_params(colors=ink, labelsize=7.5)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
axs[0].set_ylabel("within-null percentile u", color=ink)
fig.legend(frameon=False, fontsize=7.5, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Weak classes vs paired ordinary curves (shaded: the null's central 90%)", fontsize=9, color=ink, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.07, 1, 0.95)); fig.savefig("weakclass-u.svg")
