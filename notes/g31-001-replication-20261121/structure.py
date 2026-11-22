"""structure.py -- post-freeze DESCRIPTIVE analysis (not part of the decision).

For the 4 informative cells, per curve:
  * |2B|, |3B|, |4B| for the x-window base and for 10 random symmetric and 10
    random uniform bases of the same size;
  * the b^2/2 "no-collision" pair-count reference;
  * per-curve effect z (symmetric null) and its correlation with b, b/N,
    |D| (CM discriminant), and the measured sumset/coverage structure.
Exploratory: labelled as such in RESULTS.md.
"""
import json
import math

import numpy as np
from scipy import stats

import replib as R

RES = json.load(open("results.json"))
AN = json.load(open("analysis.json"))
KEY = {(13, "N3"): "13/N3", (17, "N3"): "17/N3"}
NREP = 10

zmap = {}
for c in AN["cells"]:
    if c["testable"]:
        for slot, z in zip([x for x in range(10)], c["nulls"]["symmetric"]["z"]):
            zmap[(c["bits"], c["arm"], c["m"], slot)] = z

rows = []
for c in RES["curves"]:
    bits, slot = c["bits"], c["slot"]
    if bits not in (13, 17):
        continue
    rec = R.make_curve(bits, slot)
    E, n, g = rec["E"], rec["n"], rec["g"]
    tab = R.log_table(E, n, g)
    arm = "N3"
    N = int(round(E.p ** (1 / 3)))
    logs = [tab[P] for P in R.window_points(E, N)]
    b = len(logs)
    a = R.indicator(logs, n)
    sup = {}
    for m in (2, 3, 4):
        cv, _ = R.counts(logs, n, m, a=a)
        sup[m] = int(np.count_nonzero(cv))
    ref = {}
    for m in (2, 3, 4):
        st = {"symmetric": [], "uniform": []}
        for kind in ("symmetric", "uniform"):
            for j in range(NREP):
                rng = R.rng_for(R.MASTER, bits, slot, arm, m, kind, "struct", j)
                nl = R.null_logs(n, b, kind, rng)
                cv, _ = R.counts(nl, n, m)
                st[kind].append(int(np.count_nonzero(cv)))
        ref[m] = {k: float(np.mean(v)) for k, v in st.items()}
    row = dict(bits=bits, slot=slot, j=c["j"], absD=c["cm"]["absD"], p=c["p"],
               n=n, b=b, N=N, b_over_N=b / N,
               sup2=sup[2], sup3=sup[3], sup4=sup[4],
               sup2_sym=ref[2]["symmetric"], sup2_uni=ref[2]["uniform"],
               sup3_sym=ref[3]["symmetric"], sup3_uni=ref[3]["uniform"],
               sup4_sym=ref[4]["symmetric"], sup4_uni=ref[4]["uniform"],
               pairs_no_collision=b * (b + 1) / 2, b2_half=b * b / 2,
               z3=zmap.get((bits, arm, 3, slot)), z4=zmap.get((bits, arm, 4, slot)))
    rows.append(row)
    print(f"{bits}/{slot:>2} b={b:>3} j={c['j']:>7} |D|={c['cm']['absD']:>6} "
          f"|2B|={sup[2]:>5}(S {ref[2]['symmetric']:.0f},U {ref[2]['uniform']:.0f}) "
          f"|4B|={sup[4]:>6}(S {ref[4]['symmetric']:.0f},U {ref[4]['uniform']:.0f}) "
          f"z3={row['z3']:+.2f} z4={row['z4']:+.2f}")

out = {}
for m, zk in ((3, "z3"), (4, "z4")):
    z = np.array([r[zk] for r in rows])
    for name, x in (("b", [r["b"] for r in rows]),
                    ("b_over_N", [r["b_over_N"] for r in rows]),
                    ("log_absD", [math.log(r["absD"]) for r in rows]),
                    ("absD", [r["absD"] for r in rows]),
                    ("sup_ratio_S", [r[f"sup{m}_sym"] and r[f"sup{m}"] / r[f"sup{m}_sym"] for r in rows]),
                    ("sup_ratio_U", [r[f"sup{m}"] / r[f"sup{m}_uni"] for r in rows])):
        rho, p = stats.spearmanr(x, z)
        out[f"m{m}_{name}"] = dict(rho=float(rho), p=float(p))
        print(f"  m={m}  z ~ {name:<12} Spearman rho={rho:+.3f} p={p:.3f}")

# symmetry gap in support at fixed size: uniform - symmetric (should be > 0)
for m, sk in ((2, "sup2"), (4, "sup4")):
    gap = np.array([r[f"sup{m}_uni"] - r[f"sup{m}_sym"] for r in rows])
    rel = gap / np.array([r[f"sup{m}_sym"] for r in rows])
    print(f"|{m}B|: uniform minus symmetric = {gap.mean():+.1f} "
          f"({100*rel.mean():+.2f}% of symmetric support), "
          f"sign +{(gap>0).sum()}/{len(gap)}")
    out[f"support_gap_m{m}"] = dict(mean=float(gap.mean()),
                                    rel=float(rel.mean()),
                                    pos=int((gap > 0).sum()), n=int(len(gap)))
# x-window support vs symmetric null support
for m in (2, 4):
    rel = np.array([r[f"sup{m}"] / r[f"sup{m}_sym"] - 1 for r in rows])
    print(f"|{m}B|: x-window vs symmetric null = {100*rel.mean():+.2f}% "
          f"(sd {100*rel.std(ddof=1):.2f}), sign +{(rel>0).sum()}/{len(rel)}")
    out[f"x_vs_sym_support_m{m}"] = dict(mean_rel=float(rel.mean()),
                                         sd_rel=float(rel.std(ddof=1)),
                                         pos=int((rel > 0).sum()), n=int(len(rel)))

json.dump(dict(rows=rows, correlations=out), open("structure.json", "w"), indent=1)
print("WROTE structure.json")

# ---- within-cell correlations (10 curves each), the statistically honest unit
print("\nwithin-cell Spearman (n=10 curves per cell):")
within = {}
for bits in (13, 17):
    for m in (3, 4):
        rs = [r for r in rows if r["bits"] == bits]
        z = np.array([r[f"z{m}"] for r in rs])
        rec = {}
        for name, x in (("b", [r["b"] for r in rs]),
                        ("b_over_N", [r["b_over_N"] for r in rs]),
                        ("log_absD", [math.log(r["absD"]) for r in rs]),
                        ("sup_ratio_S", [r[f"sup{m}"] / r[f"sup{m}_sym"] for r in rs])):
            rho, p = stats.spearmanr(x, z)
            rec[name] = dict(rho=float(rho), p=float(p))
        within[f"{bits}/m{m}"] = rec
        print(f"  {bits}/m{m}: " + "  ".join(f"{k}:{v['rho']:+.2f}(p={v['p']:.2f})"
                                             for k, v in rec.items()))
sj = json.load(open("structure.json"))
sj["within_cell_correlations"] = within
json.dump(sj, open("structure.json", "w"), indent=1)
