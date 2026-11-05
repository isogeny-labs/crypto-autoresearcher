"""rank / candidates against monomials / candidates for every cell, by arm (rows.jsonl)."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.axhline(1, color=grid, lw=4); ax.axvline(1, color=grid, lw=1, ls="--")
ax.text(0.36, 1.02, "full rank", color=ink, fontsize=7.5, ha="left", va="bottom")
for arm, col, mk, lab in [("null", "#8a8985", "x", "random points (null)"), ("rand", "#eb6834", "o", "random multipliers (candidate)"),
                          ("ap", "#2a78d6", "s", "small multipliers 1..t (reference)"), ("shift", "#1baf7a", "^", "shifts R+[i]P (positive control)")]:
    r = [x for x in rows if x["arm"] == arm]
    ax.scatter([x["monomials"] / x["candidates"] for x in r], [x["rank"] / x["candidates"] for x in r],
               s=16, marker=mk, color=col, facecolors="none" if mk in "os^" else col, linewidths=1.1, label=lab, alpha=0.85)
ax.set_xscale("log"); ax.set_xlabel("monomials / candidates", color=ink); ax.set_ylabel("rank / candidates", color=ink)
ax.grid(color=grid, lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title("Low-degree evaluation rank, p from 251 to 2039: random multipliers reach full rank at ratio ~2", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="center left", bbox_to_anchor=(0.0, 0.72))
fig.tight_layout(); fig.savefig("lowdeg-rank.svg")
