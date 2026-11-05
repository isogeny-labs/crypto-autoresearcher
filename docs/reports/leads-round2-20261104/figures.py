"""D1 figure: recorded H-PSEUDO R vs what a negation-closed random set gives against the same asymmetric null."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
d1 = json.load(open("checks/d1.json")); ink, grid = "#3b3b3a", "#e4e3dd"
rec = {20: 1.334, 22: 1.280, 24: 1.275, 26: 1.342}   # EV-ECDLP-f83a17 as quoted in the memo
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.axhline(1, color=grid, lw=4); ax.text(16.6, 1.01, "no excess", color=ink, fontsize=7.5, va="bottom")
ax.plot(list(rec), list(rec.values()), "s", color="#eb6834", ms=7, label="recorded R, curve factor base (EV-ECDLP-f83a17)")
bits = {131071: 17, 1048573: 20}
ax.plot([bits[x["N"]] for x in d1], [x["R_sym_over_formula"] for x in d1], "o", color="#2a78d6", mfc="white", mew=1.6, ms=8,
        label="negation-closed RANDOM set, same asymmetric null (this check)")
ax.set_xlim(16.3, 26.7); ax.set_ylim(0.9, 1.45); ax.set_xlabel("log2 N", color=ink); ax.set_ylabel("R = C / C_null", color=ink)
ax.grid(color=grid, lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title("H-PSEUDO's constant offset R ~ 1.3 is reproduced by negation symmetry alone", fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.tight_layout(); fig.savefig("d1-symmetry.svg")
