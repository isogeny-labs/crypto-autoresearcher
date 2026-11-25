#!/usr/bin/env python3
"""L1 partial execution: the N=floor(p^(1/4)) arm at 2000 targets.

Uses the frozen G31-001 replication curves (10 per size, 20 total) and the
existing replib engine. This is the new N4 arm only; it is not the full
25-30-curve/cell L1 design.
"""
import json
import math
import time
import numpy as np
from scipy import stats

import replib as R

F = json.load(open("frozen_config.json"))
MASTER = F["master_seed"]
NT = 2000
N_NULL = 50
T0 = time.time()

def L(*a):
    print(" ".join(str(x) for x in a), flush=True)

OUT = dict(frozen_utc=F["frozen_utc"], run_start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           master_seed=MASTER, n_targets=NT, n_null_draws=N_NULL, arm="N4", curves=[], cells=[])

for c in F["curves"]:
    bits, slot = c["bits"], c["slot"]
    rec = R.make_curve(bits, slot)
    E, n, g = rec["E"], rec["n"], rec["g"]
    tab = R.log_table(E, n, g)
    trng = R.rng_for(MASTER, bits, slot, "targets")
    tlogs = [trng.randrange(1, n) for _ in range(NT)]
    N = math.isqrt(math.isqrt(E.p))
    while (N + 1) ** 4 <= E.p:
        N += 1
    while N ** 4 > E.p:
        N -= 1
    B = R.window_points(E, N)
    logs = [tab[P] for P in B]
    b = len(logs)
    OUT["curves"].append(dict(bits=bits, slot=slot, p=E.p, n=n, N=N, b=b))
    for m in (3, 4):
        cvec, resid = R.counts(logs, n, m)
        ev = R.evaluate(cvec, tlogs)
        cell = dict(bits=bits, slot=slot, arm="N4", m=m, p=E.p, n=n, b=b, N=N,
                    lam_ordered=b ** m / n, frac_pred=1 - math.exp(-b ** m / (math.factorial(m) * n)),
                    fft_resid=resid,
                    x=dict(frac=ev["frac"], mean_r=ev["mean_r"], nT=ev["nT"]), nulls={})
        for kind in ("symmetric", "uniform"):
            fr, mr = [], []
            t1 = time.time()
            for j in range(N_NULL):
                rng = R.rng_for(MASTER, bits, slot, "N4", m, kind, j)
                nl = R.null_logs(n, b, kind, rng)
                c2, _ = R.counts(nl, n, m)
                e2 = R.evaluate(c2, tlogs)
                fr.append(e2["frac"]); mr.append(e2["mean_r"])
            cell["nulls"][kind] = dict(fracs=fr, mean_rs=mr, secs=round(time.time() - t1, 2))
        OUT["cells"].append(cell)
        L(f"bits={bits} slot={slot} N4 m={m} b={b} x={ev['frac']:.4f} "
          f"sym={np.mean(cell['nulls']['symmetric']['fracs']):.4f} "
          f"uni={np.mean(cell['nulls']['uniform']['fracs']):.4f}")
    json.dump(OUT, open("l1_n4_20261124/results_n4.json", "w"), indent=1)
    L(f"curve {bits}/{slot} done  +{time.time()-T0:.1f}s")

# analysis over 4 cells (bits x m)
out = dict(run=dict(start=OUT["run_start"], end=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    n_targets=NT, n_null_draws=N_NULL, arm="N4"), cells=[])

def holm(pv):
    m = len(pv); order = sorted(range(m), key=lambda i: pv[i]); adj = [0.0]*m; prev = 0.0
    for rank, i in enumerate(order):
        adj[i] = min(1.0, max(prev, (m-rank)*pv[i])); prev = adj[i]
    return adj

for bits in (13, 17):
    for m in (3, 4):
        cs = sorted([c for c in OUT["cells"] if c["bits"] == bits and c["m"] == m], key=lambda c: c["slot"])
        row = dict(bits=bits, arm="N4", m=m, b=[c["b"] for c in cs], n=cs[0]["n"],
                   frac_pred=float(np.mean([c["frac_pred"] for c in cs])), nulls={})
        for kind in ("symmetric", "uniform"):
            zs, ds, sds = [], [], []
            for c in cs:
                fr = np.array(c["nulls"][kind]["fracs"])
                mu, sd = fr.mean(), fr.std(ddof=1)
                ds.append(c["x"]["frac"] - mu); sds.append(sd)
                zs.append((c["x"]["frac"] - mu) / sd if sd else 0.0)
            zs, ds = np.array(zs), np.array(ds)
            cellz = zs.mean() / (zs.std(ddof=1) / math.sqrt(len(zs)))
            p = float(2 * stats.t.sf(abs(cellz), len(zs) - 1))
            row["nulls"][kind] = dict(mean_frac=float(np.mean([np.mean(c["nulls"][kind]["fracs"]) for c in cs])),
                                      mean_sd=float(np.mean(sds)), d_mean=float(ds.mean()),
                                      d_sd=float(ds.std(ddof=1)), cell_z=float(cellz), p=p,
                                      sign_pos=int((ds > 0).sum()), sign_neg=int((ds < 0).sum()))
        out["cells"].append(row)

for kind in ("symmetric", "uniform"):
    adj = holm([c["nulls"][kind]["p"] for c in out["cells"]])
    for c, a in zip(out["cells"], adj):
        c["nulls"][kind]["p_holm4"] = float(a)

json.dump(out, open("l1_n4_20261124/analysis_n4.json", "w"), indent=1)
print(json.dumps(out, indent=1))
