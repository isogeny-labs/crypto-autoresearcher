#!/usr/bin/env python3
"""L1 N4 arm at 30 curves/size (full L1 curve count for this arm).

Extends the frozen 10/size curves with new deterministic slots (distinct j),
then runs N=floor(p^(1/4)), 2000 targets, 50 negation-closed null draws.
Symmetric null only (primary); the uniform secondary was already reported.
"""
import json, math, time
import numpy as np
from scipy import stats
import replib as R

F = json.load(open("frozen_config.json"))
MASTER = F["master_seed"]
NT, N_NULL = 2000, 50
T0 = time.time()

def log(*a): print(" ".join(str(x) for x in a), flush=True)

curves = []
for bits in (13, 17):
    seen = set()
    base = [c for c in F["curves"] if c["bits"] == bits]
    base.sort(key=lambda c: c["slot"])
    recs = []
    for c in base:
        rec = R.make_curve(bits, c["slot"])
        assert (rec["p"], rec["a"], rec["b"], rec["nE"], rec["j"]) == (c["p"], c["a"], c["b"], c["nE"], c["j"])
        recs.append(rec); seen.add(rec["j"])
    slot = 10
    while len(recs) < 30 and slot < 200:
        try:
            rec = R.make_curve(bits, slot)
        except RuntimeError:
            slot += 1; continue
        if rec["j"] not in seen:
            recs.append(rec); seen.add(rec["j"])
        slot += 1
    log(f"bits={bits}: {len(recs)} curves (last slot {slot-1})")
    curves.extend(recs)

OUT = dict(arm="N4", n_targets=NT, n_null_draws=N_NULL, run_start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), cells=[])
for ci, rec in enumerate(curves):
    bits = rec["bits"]; E, n, g = rec["E"], rec["n"], rec["g"]
    tab = R.log_table(E, n, g)
    trng = R.rng_for(MASTER, bits, rec["idx"], "targets")
    tlogs = [trng.randrange(1, n) for _ in range(NT)]
    N = math.isqrt(math.isqrt(E.p))
    while (N + 1) ** 4 <= E.p: N += 1
    while N ** 4 > E.p: N -= 1
    B = R.window_points(E, N)
    logs = [tab[P] for P in B]; b = len(logs)
    for m in (3, 4):
        cvec, resid = R.counts(logs, n, m)
        ev = R.evaluate(cvec, tlogs)
        fr = []
        for j in range(N_NULL):
            rng = R.rng_for(MASTER, bits, rec["idx"], "N4", m, "symmetric", j)
            nl = R.null_logs(n, b, "symmetric", rng)
            c2, _ = R.counts(nl, n, m)
            fr.append(R.evaluate(c2, tlogs)["frac"])
        OUT["cells"].append(dict(bits=bits, slot=rec["idx"], m=m, p=E.p, n=n, N=N, b=b,
                                 frac_pred=1-math.exp(-b**m/(math.factorial(m)*n)),
                                 x=dict(frac=ev["frac"], mean_r=ev["mean_r"]),
                                 null=dict(fracs=fr)))
    json.dump(OUT, open("results_n4_30.json", "w"), indent=1)
    if (ci + 1) % 5 == 0:
        log(f"{ci+1}/{len(curves)} curves  +{time.time()-T0:.0f}s")

def holm(pv):
    m=len(pv); order=sorted(range(m), key=lambda i: pv[i]); adj=[0.0]*m; prev=0.0
    for rank,i in enumerate(order):
        adj[i]=min(1.0,max(prev,(m-rank)*pv[i])); prev=adj[i]
    return adj

an = dict(run=dict(start=OUT["run_start"], end=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   n_targets=NT, n_null_draws=N_NULL, arm="N4"), cells=[])
for bits in (13,17):
    for m in (3,4):
        cs=[c for c in OUT["cells"] if c["bits"]==bits and c["m"]==m]
        ds=[]; zs=[]
        for c in cs:
            fr=np.array(c["null"]["fracs"]); mu=fr.mean(); sd=fr.std(ddof=1)
            d=c["x"]["frac"]-mu; ds.append(d); zs.append(d/sd if sd else 0.0)
        ds=np.array(ds); zs=np.array(zs)
        cellz=zs.mean()/(zs.std(ddof=1)/math.sqrt(len(zs)))
        p=float(2*stats.t.sf(abs(cellz),len(zs)-1))
        an["cells"].append(dict(bits=bits,arm="N4",m=m,ncurves=len(cs),
            b=[c["b"] for c in cs],pred=float(np.mean([c["frac_pred"] for c in cs])),
            d_pp=float(ds.mean()*100),d_sd_pp=float(ds.std(ddof=1)*100),
            cell_z=float(cellz),p=p,sign_pos=int((ds>0).sum()),sign_neg=int((ds<0).sum()),
            null_mean=float(np.mean([np.mean(c["null"]["fracs"]) for c in cs]))))
for c in an["cells"]:
    c["p_holm4"]=0.0
adj=holm([c["p"] for c in an["cells"]])
for c,a in zip(an["cells"],adj): c["p_holm4"]=float(a)
json.dump(an, open("analysis_n4_30.json","w"), indent=1)
print(json.dumps(an, indent=1))
