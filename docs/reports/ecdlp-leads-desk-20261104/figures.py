"""Figure: exact evaluation-matrix rank vs the number of candidate logs (lowdeg_rank_check.json)."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = json.load(open("lowdeg_rank_check.json"))
ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.4))
for p, col, mk in [(101, "#2a78d6", "o"), (211, "#eb6834", "s")]:
    r = [x for x in rows if x["p"] == p]
    xs = list(range(len(r)))
    ax.plot(xs, [x["rank"] for x in r], mk + "-", color=col, lw=2, ms=6, label=f"rank, p = {p}")
    ax.axhline(r[0]["candidates"], color=col, lw=1, ls="--")
    ax.text(len(r) - 0.6, r[0]["candidates"] + 4, f"full rank = {r[0]['candidates']} candidates", color=ink, fontsize=7.5, ha="right")
labels = [f"t={x['t']}, D={x['D']}\n{x['monomials']} mon." for x in rows if x["p"] == 101]
ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=7.5)
ax.set_ylabel("rank over F_p", color=ink)
ax.grid(axis="y", color=grid, lw=0.8); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink)
ax.set_title("Low-degree tests: interpolation reaches full rank at p = 101 (t = 4, D = 3), not yet at p = 211", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig("lowdeg-rank.svg")
