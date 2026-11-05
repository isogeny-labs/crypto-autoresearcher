"""Null distribution (40 draws) at the 2^16 curve with Q_EC and the earlier 5-draw max marked."""
import json, numpy as np, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; v = json.load(open("verdict.json")); ink, grid = "#3b3b3a", "#e4e3dd"
nul = [r["Q"] for r in rows if r["arm"] == "N_sym"]
fig, ax = plt.subplots(figsize=(7, 3.0))
ax.hist(nul, bins=14, color="#8a8985", edgecolor="white", linewidth=1.5, label="40 negation-closed null draws")
ax.axvline(v["Q_EC"], color="#eb6834", lw=2.5, label=f"small-x factor base Q = {v['Q_EC']:.3f} (u = {v['u']:.2f})")
ax.axvline(4.708, color="#2a78d6", lw=1.5, ls="--", label="max of the earlier 5 draws (4.708)")
ax.set_xlabel("Q", color=ink); ax.set_ylabel("draws", color=ink)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title("2^16 curve: the quadratic-phase maximum sits at the null median (verdict NULL)", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout(); fig.savefig("quadphase-2p16.svg")
