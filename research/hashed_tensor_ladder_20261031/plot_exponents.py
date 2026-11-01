#!/usr/bin/env python3
"""Plot E/rho from compile-stats.json: counting exponent (unit constants) over the rho exponent, by slot count m."""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
rows = json.load(open(src))["rows"]
ms = sorted({r["m"] for r in rows})
ramp = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]
ink, muted, grid = "#1f2933", "#52606d", "#e4e7eb"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "sans-serif", "font.size": 10})
fig, ax = plt.subplots(figsize=(7.2, 4.2))
for m, col in zip(ms, ramp):
    pts = sorted((r["ell"], r["E_over_rho"]) for r in rows if r["m"] == m)
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=col, lw=2, marker="o", ms=5, mec="white", mew=1.2, zorder=3, label=f"m = {m}")
    if m in (ms[0], ms[-1]):
        ax.annotate(f"m={m}", (xs[-1], ys[-1]), xytext=(7, 0), textcoords="offset points", va="center",
                    color=ink, fontsize=9)
ax.axhline(1, color=ink, lw=1.2, ls=(0, (4, 3)), zorder=2)
ax.text(41, 1.25, "break-even with rho (E/rho = 1)", color=ink, fontsize=9, va="bottom")
ax.set_yscale("log")
ax.set_ylim(0.8, 3e4)
ax.set_xlim(37, 142)
ax.set_xticks([40, 48, 56, 64, 72, 80, 131])
ax.set_xlabel("field size ell (bits of p)", color=muted)
ax.set_ylabel("counting exponent / rho exponent", color=muted)
ax.set_title("Counting-algorithm exponent over rho exponent, all hidden constants set to 1",
             loc="left", color=ink, fontsize=11)
ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.33), ncol=3, frameon=False, fontsize=9,
          title="slots m", title_fontsize=9, labelcolor=ink)
ax.grid(axis="y", color=grid, lw=0.8, zorder=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(muted)
ax.tick_params(colors=muted)
fig.text(0.01, 0.005, "E = N / sqrt(log2 N), N = compiled Boolean variables (compile_stats.py). "
         "Every point is 1,480-10,110 times above break-even.", fontsize=8, color=muted)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(out, format="svg")
if len(sys.argv) > 3:
    fig.savefig(sys.argv[3], format="png", dpi=110)
