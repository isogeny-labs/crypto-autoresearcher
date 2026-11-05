"""Draw graph.svg for DEC-20261105-6e2616 from data.json (recorded values only)."""
import json, pathlib, matplotlib
matplotlib.use("svg"); import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text())
ip = d["integer_points"]; bp = d["band_points"]; bl = d["band_limits"]
em = {e["arm"]: e["exact_match"] for e in d["exact_match"]}
arms = ["primary", "CTL-1", "CTL-2"]
fig, ax = plt.subplots(1, 5, figsize=(14, 4.4))
for k, q in enumerate(["sample_sum", "sum_squares", "median"]):
    a = ax[k]; rows = {p["arm"]: p for p in ip if p["quantity"] == q}
    xs = range(3)
    a.axhline(rows["primary"]["preregistered"], ls="--", c="grey", lw=1, label="pass value")
    a.scatter(xs, [rows[m]["recorded"] for m in arms], c=["green" if em[m] else "red" for m in arms], s=45, zorder=3, label="recorded")
    a.scatter([x + 0.15 for x in xs], [rows[m]["blind_rederived"] for m in arms], facecolors="none", edgecolors="C1", marker="s", s=55, zorder=3, label="blind re-derived")
    a.scatter([x - 0.15 for x in xs], [rows[m]["preregistered"] for m in arms], c="k", marker="x", s=40, zorder=3, label="preregistered")
    a.set_xticks(list(xs)); a.set_xticklabels(arms); a.set_title(q, fontsize=10); a.ticklabel_format(axis="y", useOffset=False, style="plain")
    if k == 0: a.legend(fontsize=7)
for k, (f, lim, t) in enumerate([("cv_sq_decimal", "cv_sq", "CV^2 band [0.81, 1.21]"), ("median_ratio_decimal", "median_ratio", "median/mean band [0.6, 0.8]")]):
    a = ax[3 + k]; a.axhspan(bl[lim]["low_decimal"], bl[lim]["high_decimal"], color="0.9")
    a.scatter(range(3), [next(p[f] for p in bp if p["arm"] == m) for m in arms], c=["green" if em[m] else "red" for m in arms], s=45)
    a.set_xticks(range(3)); a.set_xticklabels(arms); a.set_title(t + "\n(descriptive only)", fontsize=9)
fig.suptitle("EXP-ICPERF-283a70: exact integers decide (green = exact_match true); all three arms sit inside both bands", fontsize=10)
fig.text(0.01, 0.005, "Runs RUN-ICPERF-f21eb1 (primary), 0ef41e (CTL-1 shifts 1,2,14), 74e9a2 (CTL-2 support 0). n = 64 draws per arm, seed 20261017, one execution per arm; exact integers, no error bars.", fontsize=7.5)
fig.tight_layout(rect=(0, 0.04, 1, 0.94)); fig.savefig(here / "graph.svg")
