"""addendum.py -- POST-FREEZE addendum (NOT part of the frozen decision).

Re-measures the pilot's own four N3 cells (same curves, reproduced through
the pilot's find_curve) with (a) fresh 1000-target sets and (b) 50 symmetric
+ 50 uniform null draws, i.e. the same protocol as the replication.  This is
the direct test of the pilot's single cell that lay outside its symmetric
null band (p = 1060981, m = 3), and of its "both directions" claim.
"""
import json
import math

import numpy as np
from scipy import stats

import replib as R
from pilot_run import find_curve

PILOT = json.load(open("/Volumes/SSD990-2/crypto-autoresearcher/notes/"
                       "g31-001-terracini-pilot-20261120/results.json"))
CELLS = [(13, 31011), (17, 31001), (18, 31002), (20, 31003)]
NREP = 50
NT = 1000
out = []


class _L:
    def __call__(self, *a):
        pass


for bits, seed in CELLS:
    E, nE, c, n, g = find_curve(bits, seed, _L())
    tab = R.log_table(E, n, g)
    N = int(round(E.p ** (1 / 3)))
    raw = [P for P in E.points_x_window(N) if P is not None]
    Bset = {}
    for P in raw:
        cP = E.mul(c, P)
        if cP is not None:
            Bset[cP] = None
    B = list(Bset)
    logs = [tab[P] for P in B]
    b = len(logs)
    st = set(logs)
    assert b % 2 == 0 and all((-k) % n in st for k in logs)
    trng = R.rng_for(R.MASTER, "addendum", bits, seed, "targets")
    tlogs = [trng.randrange(1, n) for _ in range(NT)]
    rec = dict(bits=bits, seed=seed, p=E.p, nE=nE, cofactor=c, n=n, N=N, b=b,
               pilot=dict(), measured=dict())
    for pc in PILOT["cells"]:
        if pc.get("bits") == bits and pc.get("seed") == seed and pc.get("arm") == "N3" \
                and pc.get("m") in (3, 4):
            rec["pilot"][pc["m"]] = dict(frac=pc["frac_dec"], mean_r=pc["mean_r"],
                                         nT=pc["nT"])
            for ch in PILOT["cells"]:
                if ch.get("bits") == bits and ch.get("seed") == seed and \
                        ch.get("arm") == "N3" and ch.get("charter", {}).get("m") == pc["m"]:
                    pass
    # pilot charter nulls (10 draws) live in separate cells with 'charter'
    for ch in PILOT["cells"]:
        ch2 = ch.get("charter")
        if ch2 and ch.get("bits") == bits and ch.get("seed") == seed and \
                ch.get("arm") == "N3" and ch2["m"] in (3, 4):
            rec["pilot"].setdefault(ch2["m"], {})[ch2["kind"]] = dict(
                frac=ch2["frac_dec"], nT=ch2.get("n_targets"))
    for m in (3, 4):
        a = R.indicator(logs, n)
        cv, _ = R.counts(logs, n, m, a=a)
        ev = R.evaluate(cv, tlogs)
        mrec = dict(frac=ev["frac"], mean_r=ev["mean_r"],
                    lam_ordered=b ** m / n,
                    frac_pred=1 - math.exp(-b ** m / (math.factorial(m) * n)))
        for kind in ("symmetric", "uniform"):
            fr = []
            for j in range(NREP):
                rng = R.rng_for(R.MASTER, "addendum", bits, seed, m, kind, j)
                nl = R.null_logs(n, b, kind, rng)
                c2, _ = R.counts(nl, n, m)
                fr.append(R.evaluate(c2, tlogs)["frac"])
            fr = np.array(fr)
            d = ev["frac"] - fr.mean()
            mrec[kind] = dict(mean=float(fr.mean()), sd=float(fr.std(ddof=1)),
                              z=float(d / fr.std(ddof=1)) if fr.std(ddof=1) > 0 else 0.0,
                              d=float(d))
        rec["measured"][m] = mrec
        print(f"p={E.p} c={c} b={b} m={m}: frac={ev['frac']:.4f} "
              f"pred={mrec['frac_pred']:.4f} | S {mrec['symmetric']['mean']:.4f}"
              f"±{mrec['symmetric']['sd']:.4f} z={mrec['symmetric']['z']:+.2f} | "
              f"U {mrec['uniform']['mean']:.4f}±{mrec['uniform']['sd']:.4f} "
              f"z={mrec['uniform']['z']:+.2f}")
    out.append(rec)

json.dump(out, open("addendum.json", "w"), indent=1)
print("WROTE addendum.json")
