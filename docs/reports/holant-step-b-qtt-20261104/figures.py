"""Figure for holant step (b'): interleaved QTT r_max by arm against the rank ceiling 2^L.
Reads verdict.json (frozen analysis output). Deterministic."""
import json, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
plt.rcParams["svg.fonttype"] = "none"
v = json.load(open("verdict.json"))["per_curve"]
ink, grid = "#3b3b3a", "#e4e3dd"
fig, ax = plt.subplots(figsize=(7, 3.8))
Ls = sorted({c["L"] for c in v}); ps = {c["L"]: c["p"] for c in v}
ax.plot(Ls, [2**L for L in Ls], color="#efeee9", lw=6, solid_capstyle="round", zorder=0)
ax.text(Ls[-1] + 0.12, 2**Ls[-1], "ceiling 2^L", color=ink, fontsize=8, va="center")
off = {"N": -0.12, "X": 0.0, "LOG": 0.12, "SH": 0.0}
for c in v:
    ax.vlines(c["L"] + off["N"], c["null_min"], c["null_max"], color="#5e5d59", lw=2)
ax.plot([], [], color="#5e5d59", lw=2, label="random relabelling, 99 draws (min to max)")
for arm, col, mk, lab in [("X", "#eb6834", "s", "x-coordinate labelling (candidate)"),
                          ("LOG", "#2a78d6", "o", "discrete-log labelling (positive control)"),
                          ("SH", "#1baf7a", "^", "shift matrix (detector check)")]:
    ax.plot([c["L"] + off[arm] for c in v], [c[arm] for c in v], mk, ms=6, color=col,
            mfc="white" if arm != "X" else col, mew=1.5, ls="none", label=lab)
ax.set_yscale("log", base=2); ax.set_xticks(Ls); ax.set_xticklabels([f"L={L}\np={ps[L]}" for L in Ls])
ax.set_ylabel("max interleaved QTT rank", color=ink)
ax.grid(axis="y", color=grid, lw=0.8); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color(grid)
ax.tick_params(colors=ink, labelsize=8)
ax.set_title("Transfer matrix M: x-labelling is as complex as a random labelling (3 curves per size)",
             fontsize=9, color=ink, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="upper left")
fig.tight_layout(); fig.savefig("qtt-rank.svg")
