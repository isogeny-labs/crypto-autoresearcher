"""sens.py -- post-freeze sensitivity analysis for one disclosed deviation.

The frozen arm text says N3 = floor(p^(1/3)); the implementation (following
the pilot's convention) used round(p^(1/3)).  The two differ on 6 of the 20
curves, changing |B_G| by 0 or 2 points.  This re-runs the two affected cells
(17/N3, m=3 and m=4) under the floor definition, with the frozen targets and
fresh 50-draw symmetric nulls, to show the verdict does not depend on it.

NOT part of the decision family.
"""
import json
import math

import numpy as np
from scipy import stats

import replib as R

F = json.load(open("frozen_config.json"))
AN = json.load(open("analysis.json"))
out = {}
for m in (3, 4):
    zs = []
    for c in F["curves"]:
        if c["bits"] != 17:
            continue
        bits, slot = c["bits"], c["slot"]
        rec = R.make_curve(bits, slot)
        E, n, g = rec["E"], rec["n"], rec["g"]
        tab = R.log_table(E, n, g)
        N = int(math.floor(E.p ** (1 / 3)))
        logs = [tab[P] for P in R.window_points(E, N)]
        b = len(logs)
        cv, _ = R.counts(logs, n, m)
        trng = R.rng_for(R.MASTER, bits, slot, "targets")
        tlogs = [trng.randrange(1, n) for _ in range(F["n_targets_per_cell"])]
        fx = R.evaluate(cv, tlogs)["frac"]
        fr = []
        for j in range(F["n_null_draws"]):
            nl = R.null_logs(n, b, "symmetric",
                             R.rng_for(R.MASTER, bits, slot, "N3", m, "symmetric", j))
            c2, _ = R.counts(nl, n, m)
            fr.append(R.evaluate(c2, tlogs)["frac"])
        fr = np.array(fr)
        zs.append((fx - fr.mean()) / fr.std(ddof=1))
    zs = np.array(zs)
    cz = zs.mean() / (zs.std(ddof=1) / math.sqrt(len(zs)))
    p = float(2 * stats.t.sf(abs(cz), len(zs) - 1))
    out[f"m{m}"] = dict(cell_z=float(cz), p=p, mean_z=float(zs.mean()),
                        signs_pos=int((zs > 0).sum()),
                        signs_neg=int((zs < 0).sum()))
    print(f"17/N3/m={m} (floor): cell_z={cz:+.2f} raw p={p:.3f} "
          f"signs {int((zs>0).sum())}/{int((zs<0).sum())}")

for m in (3, 4):
    ref = [c for c in AN["cells"] if (c["bits"], c["arm"], c["m"]) == (17, "N3", m)][0]
    print(f"   frozen (round) cell_z={ref['nulls']['symmetric']['cell_z']:+.2f} "
          f"signs {ref['nulls']['symmetric']['sign_pos']}/{ref['nulls']['symmetric']['sign_neg']}")
json.dump(out, open("sensitivity.json", "w"), indent=1)
print("WROTE sensitivity.json")
