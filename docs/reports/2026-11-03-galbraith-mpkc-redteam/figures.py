"""Figures for the Galbraith MPKC v2 red-team report (counts transcribed from
the report tables; Wiener data from evidence/lead/wiener_result.json)."""
import json, math, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
cats = ["false as printed", "missing hypothesis /\nill-posed", "proof gap", "constant / units /\ntypo", "survived"]
colors = ["#c0392b", "#e67e22", "#8e44ad", "#2980b9", "#7f8c8d"]
rows = {"Ch. 2 (next formal tranche)": [12, 15, 3, 4, 32],
        "Ch. 13-15 (DLP / IC bounds)": [7, 1, 3, 4, 40]}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
ax = axes[0]
y = list(range(len(rows)))
left = [0] * len(rows)
for k, c in enumerate(cats):
    vals = [v[k] for v in rows.values()]
    ax.barh(y, vals, left=left, color=colors[k], label=c.replace("\n", " "))
    for i, v in enumerate(vals):
        if v: ax.text(left[i] + v / 2, i, str(v), ha="center", va="center", color="white", fontsize=9)
    left = [l + v for l, v in zip(left, vals)]
ax.set_yticks(y, list(rows)); ax.invert_yaxis(); ax.set_xlabel("rows examined (as reported)")
ax.set_title("Verdicts on literal statements, Galbraith MPKC v2")
ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
w = json.load(open(here / "evidence/lead/wiener_result.json"))
ax = axes[1]
labels = ["d < N^(1/4)/sqrt6\n(corrected bound)", "N^(1/4)/sqrt6 <= d < N^(1/4)/sqrt3\n(printed v2 bound)"]
rates = [w["control_failures"] / w["control_cases"], w["window_failures"] / w["window_cases"]]
ax.bar(labels, [100 * r for r in rates], color=["#7f8c8d", "#c0392b"])
for i, (r, n, f) in enumerate(zip(rates, [w["control_cases"], w["window_cases"]], [w["control_failures"], w["window_failures"]])):
    ax.text(i, 100 * r / 2 + 0.05, f"{f}/{n}", ha="center", color="black" if i == 0 else "white")
ax.set_ylabel("% instances where Euclid misses d")
ax.set_title("Thm 24.5.2 (Wiener): printed proof route fails\ninside the printed bound (p<q<2p<4000)")
fig.tight_layout()
for ext in ("svg", "png"): fig.savefig(here / f"verdicts.{ext}", dpi=72)
# Keep the PNG under the artifact policy's 64 KiB data-file limit.
from PIL import Image
Image.open(here / "verdicts.png").convert("P", palette=Image.ADAPTIVE, colors=64).save(here / "verdicts.png", optimize=True)
