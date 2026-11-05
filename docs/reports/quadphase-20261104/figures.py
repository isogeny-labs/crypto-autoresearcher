"""Q_EC vs its negation-closed null (min-max bar, mean tick) and the planted control, per curve."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
rows = [json.loads(l) for l in open("rows.jsonl")]; v = json.load(open("verdict.json")); ink, grid = "#3b3b3a", "#e4e3dd"
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.3), gridspec_kw=dict(width_ratios=[3, 1]))
for i, c in enumerate(v["per_curve"]):
    nul = [r["Q"] for r in rows if r["instance_id"] == c["instance"] and r["arm"] == "N_sym"]
    a1.vlines(i, min(nul), max(nul), color="#8a8985", lw=3, label="null min-max (negation-closed sets)" if i == 0 else None)
    a1.plot(i, sum(nul)/len(nul), "_", color=ink, ms=10)
    a1.plot(i, c["Q_EC"], "o", color="#eb6834", ms=7, label="small-x factor base (curve)" if i == 0 else None)
a1.set_xticks(range(len(v["per_curve"]))); a1.set_xticklabels([f"2^{c['L']}" for c in v["per_curve"]], fontsize=7.5, color=ink)
a1.axvspan(8.5, 9.5, color="#f3f2ee", zorder=0); a1.text(9, 3.7, "descriptive\n(5 draws)", ha="center", fontsize=7, color=ink)
a1.set_ylabel("Q = max |quadratic-phase sum| / sqrt|S|", color=ink); a1.set_ylim(3.6, 6)
a1.set_title(f"Quadratic-phase test: verdict {v['verdict']} (9/9 decisive curves inside the null's 90%)", fontsize=8.5, color=ink, loc="left")
a1.legend(frameon=False, fontsize=7, loc="upper left")
a2.bar(range(len(v["per_curve"])), [c["planted_ratio"] for c in v["per_curve"]], color="#2a78d6")
a2.axhline(3, color=ink, lw=1, ls="--"); a2.text(9.4, 2.6, "pass >= 3x", fontsize=7, color=ink, ha="right")
a2.set_xticks([]); a2.set_title("planted control / null max", fontsize=8.5, color=ink, loc="left")
for ax in (a1, a2):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
    ax.tick_params(colors=ink, labelsize=7.5)
fig.tight_layout(); fig.savefig("quadphase.svg")
