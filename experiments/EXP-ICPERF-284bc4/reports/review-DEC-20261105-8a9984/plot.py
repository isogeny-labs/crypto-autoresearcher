"""Draw graph.svg for DEC-20261105-8a9984 from data.json (recorded values only)."""
import json, pathlib, matplotlib
from fractions import Fraction
matplotlib.use("svg"); import matplotlib.pyplot as plt
here = pathlib.Path(__file__).parent
d = json.loads((here / "data.json").read_text())
pts = d["ratio_points"]; bs = d["bsgs_points"]
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [2.3, 1]})
labels = [f"{p['run_id'][-6:]} {p['role'][:8]}\n{p['quantity']} {p['cell'] or ''}" for p in pts]
x = range(len(pts))
a.axhline(231.25, ls="--", c="grey", lw=1, label="preregistered success value 925/4 = 231.25")
a.scatter(x, [p["value"] for p in pts], c="C0", s=40, zorder=3, label="recorded (raw-result.json)")
a.scatter([i + 0.18 for i in x], [p["value"] for p in pts if True], facecolors="none", edgecolors="C1", marker="s", s=50, zorder=3,
          label="blind re-derived (TASK-20261105-b543c3), equal at every point")
pre = [(i, float(Fraction(str(p["preregistered"]).split()[0]))) for i, p in enumerate(pts) if p.get("preregistered") not in (None, "")]
a.scatter([i - 0.18 for i, _ in pre], [v for _, v in pre], c="k", marker="x", s=40, zorder=3, label="preregistered / control pass value")
a.set_yscale("log"); a.set_xticks(list(x)); a.set_xticklabels(labels, rotation=75, fontsize=6.5)
a.set_ylabel("reduced ratio IC online / BL online (dimensionless, assumed prices)")
a.set_title("A. Ratio per unit and cell (EXP-ICPERF-284bc4)", fontsize=10)
a.annotate("NEG-1 c_probe 371: 1855/8 = 231.875", (0.02, 0.93), xycoords="axes fraction", fontsize=7)
a.annotate("NEG-2 precomputation 10 steps: 185/42 = 4.405", (0.02, 0.87), xycoords="axes fraction", fontsize=7)
a.legend(fontsize=7, loc="lower left")
cx = range(len(bs)); cl = [p["cell"] for p in bs]
b.scatter(cx, [p["enumerated_worst_case"] for p in bs], c="C0", s=40, label="enumerated worst case (RUN-ICPERF-779d41)")
b.scatter([i - 0.15 for i in cx], [p["formula"] for p in bs], c="k", marker="x", s=40, label="probe formula r/(A*states)")
b.scatter([i + 0.15 for i in cx], [p["blind_bsgs_max"] for p in bs], facecolors="none", edgecolors="C1", marker="s", s=50, label="blind BSGS max")
b.scatter(cx, [p["bsgs_mean_red_team"] for p in bs], c="grey", marker="^", s=40, label="BSGS mean (red-team O4, not a run value)")
b.set_xticks(list(cx)); b.set_xticklabels(cl); b.set_xlabel("cell (r, A), 10 states"); b.set_ylabel("table lookups (count)")
b.set_title("B. CON-3: BSGS enumeration vs formula", fontsize=10); b.legend(fontsize=7)
fig.text(0.01, 0.005, "n = 1 deterministic execution per unit; exact rationals, no error bars; prices 370/2100/40 ns are assumed inputs, not measurements; no rho arm.", fontsize=7.5)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(here / "graph.svg")
