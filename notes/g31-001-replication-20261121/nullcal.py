"""nullcal.py -- post-freeze calibration of the CELL-LEVEL statistic.

Under H0 the x-window base is exchangeable with a random negation-closed
base.  So replace it by a fresh random symmetric base and run the frozen
cell pipeline (per-curve z against the 50 recorded null draws, then
cell_z = mean/(sd/sqrt(10))).  Repeated 20x per cell, this measures the
false-positive rate of the frozen |cell_z| >= 2.5 bar directly.
"""
import json
import math

import numpy as np
from scipy import stats

import replib as R

RES = json.load(open("results.json"))
AN = json.load(open("analysis.json"))
REPS = 20
crit8 = float(stats.t.ppf(1 - 0.05 / 16, 9))
out = []

for cell in AN["cells"]:
    if not cell["testable"]:
        continue
    bits, arm, m = cell["bits"], cell["arm"], cell["m"]
    cs = sorted([c for c in RES["cells"] if (c["bits"], c["arm"], c["m"]) == (bits, arm, m)],
                key=lambda c: c["slot"])
    zlist = []
    for rep in range(REPS):
        zs = []
        for c in cs:
            rec = R.make_curve(bits, c["slot"])
            E, n, g = rec["E"], rec["n"], rec["g"]
            tab = R.log_table(E, n, g)
            rng = R.rng_for(R.MASTER, "nullcal", bits, c["slot"], arm, m, rep)
            nl = R.null_logs(n, c["b"], "symmetric", rng)
            cv, _ = R.counts(nl, n, m)
            trng = R.rng_for(R.MASTER, bits, c["slot"], "targets")
            tlogs = [trng.randrange(1, n) for _ in range(RES["n_targets"])]
            f = R.evaluate(cv, tlogs)["frac"]
            fr = np.array(c["nulls"]["symmetric"]["fracs"])
            zs.append((f - fr.mean()) / fr.std(ddof=1))
        zs = np.array(zs)
        zlist.append(zs.mean() / (zs.std(ddof=1) / math.sqrt(len(zs))))
    zl = np.array(zlist)
    row = dict(bits=bits, arm=arm, m=m, reps=REPS,
               cell_z_pseudo=[float(z) for z in zl],
               mean=float(zl.mean()), sd=float(zl.std(ddof=1)),
               frac_abs_ge_2_5=float((np.abs(zl) >= 2.5).mean()),
               frac_abs_ge_crit8=float((np.abs(zl) >= crit8).mean()))
    out.append(row)
    print(f"{bits}/{arm}/m{m}: pseudo cell_z sd={zl.std(ddof=1):.2f} "
          f"P(|z|>=2.5)={row['frac_abs_ge_2_5']:.2f} "
          f"P(|z|>={crit8:.2f})={row['frac_abs_ge_crit8']:.2f} "
          f"max={np.max(np.abs(zl)):.2f}")

allz = np.concatenate([np.array(r["cell_z_pseudo"]) for r in out])
print(f"pooled: n={len(allz)} sd={allz.std(ddof=1):.2f} "
      f"P(|z|>=2.5)={(np.abs(allz)>=2.5).mean():.3f} "
      f"P(|z|>={crit8:.2f})={(np.abs(allz)>=crit8).mean():.3f}")
json.dump(dict(reps_per_cell=REPS, crit8=crit8, cells=out,
               pooled=dict(n=int(len(allz)), sd=float(allz.std(ddof=1)),
                           p_abs_ge_2_5=float((np.abs(allz) >= 2.5).mean()),
                           p_abs_ge_crit8=float((np.abs(allz) >= crit8).mean()))),
          open("nullcal.json", "w"), indent=1)
print("WROTE nullcal.json")
