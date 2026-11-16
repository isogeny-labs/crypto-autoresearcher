#!/usr/bin/env python3
"""SA-23 analysis: Gate A fit, Gate B fit, c_hat, out-of-sample check, tables. Bootstrap 2000 resamples seed 23."""
import json, math, glob, statistics, sys
import numpy as np
rng=np.random.default_rng(23); B=2000
cells=[json.loads(l) for l in open("results/cells.jsonl")]
ss=[c for c in cells if c["family"]=="supersingular"]
ordc=[c for c in cells if c["family"]!="supersingular"]
calls=[json.loads(l) for l in open("results/gateB_calls.jsonl")] if glob.glob("results/gateB_calls.jsonl") else []
out=[]
def P(s=""): out.append(s); print(s)
def ci(a): a=np.array(a,float); a=a[np.isfinite(a)]; return (float(np.percentile(a,2.5)),float(np.percentile(a,97.5))) if len(a) else (float('nan'),float('nan'))
def fmt(x): return f"{x:.3f}"
# ---------- Gate A table
P("## Gate A: sections per cell (supersingular family, p = -1 mod d)")
P("| d | chi | p | S | rank | det(lattice) | min height (sections) | enum s | coverage_G (3 fibres, mean) | |G| (ell) | coverage_E (all E(F_p), mean) |")
P("|---|---|---|---|---|---|---|---|---|---|---|")
for c in sorted(ss,key=lambda c:(c["d"],c["p"])):
    ce=np.mean([f["coverage_E"] for f in c["fibres"]]); P(f"| {c['d']} | {c['chi']} | {c['p']} | {c['S']} | {c['rank']} | {c['det_lattice']} | {c['min_height_sections']} | {c['seconds']} | {fmt(c['coverage_G_mean'])} | {c['fibres'][0]['ell']} | {fmt(ce)} |")
P(); P("## Controls: ordinary cells (p = +1 mod d)")
P("| d | p | S | rank | det |"); P("|---|---|---|---|---|")
for c in sorted(ordc,key=lambda c:(c["d"],c["p"])): P(f"| {c['d']} | {c['p']} | {c['S']} | {c['rank']} | {c['det_lattice']} |")
# ---------- Gate A fit
def fitA(rows):
    X=np.array([[r["d"],math.log2(r["p"]),1.0] for r in rows]); y=np.array([math.log2(r["S"]) for r in rows])
    if len({r["d"] for r in rows})<2 or len({r["p"] for r in rows})<2: return None
    co,res,rk,_=np.linalg.lstsq(X,y,rcond=None)
    return co if rk==3 else None
fitrows=[c for c in ss if c["S"]>=2]
co=fitA(fitrows); alpha,beta,gamma=co
bs=[]; 
for _ in range(B):
    idx=rng.integers(0,len(fitrows),len(fitrows)); r=fitA([fitrows[i] for i in idx])
    if r is not None: bs.append(r)
bs=np.array(bs)
P(); P("## Gate A fit: log2 S = alpha d + beta log2 p + gamma  (supersingular cells, S>=2)")
P(f"cells used: {len(fitrows)}; bootstrap resamples with identifiable fit: {len(bs)}/{B}")
for nm,i in (("alpha",0),("beta",1),("gamma",2)):
    lo,hi=ci(bs[:,i]); P(f"- {nm} = {fmt(co[i])}  95% CI [{fmt(lo)}, {fmt(hi)}]")
ALPHA_CI=ci(bs[:,0])
def dstar(co,k,round6=True):
    a,b,g=co
    if a<=0: return math.inf
    x=(k-1-b*k-g)/a
    return max(6,6*math.ceil(x/6)) if round6 else max(x,0.0)
# ---------- Gate B
byc={}
for r in calls:
    if r["status"]=="ok" and r["kind"]=="planted" and r.get("verified") and r.get("planted_found"): byc.setdefault((r["d"],r["p"]),[]).append(r["wall_s"])
P(); P("## Gate B: msolve lift (planted targets, wall s; median [min,max] over targets)")
P("| d | p | U | n planted | median s | min | max |"); P("|---|---|---|---|---|---|---|")
bcells=[]
for (d,p),v in sorted(byc.items()):
    U=5*(d//6)+2; med=statistics.median(v); bcells.append((d,p,U,med)); P(f"| {d} | {p} | {U} | {len(v)} | {med:.4f} | {min(v):.4f} | {max(v):.4f} |")
P(); P("random-G targets (wall s, #closure solutions, #F_p sections, fraction liftable):")
P("| d | p | n | median s | frac with F_p section | mean closure sols |"); P("|---|---|---|---|---|---|")
rc={}
for r in calls:
    if r["kind"]=="random_G": rc.setdefault((r["d"],r["p"]),[]).append(r)
for (d,p),v in sorted(rc.items()):
    ok=[x for x in v if x['status']=='ok' and x.get('verified')]
    P(f"| {d} | {p} | {len(v)} | {statistics.median([x['wall_s'] for x in ok]) if ok else float('nan'):.4f} | {np.mean([1 if x.get('fp_sections') else 0 for x in ok]) if ok else float('nan'):.2f} | {(np.mean([x['closure_solutions'] for x in ok]) if ok else float('nan')):.1f} |")
bad=[r for r in calls if not r.get("verified",False) or r["status"]!="ok" or r.get("matches_enumeration") is False]
P(); P(f"Gate B calls: {len(calls)}; not-ok/unverified/mismatch: {len(bad)} (40 = all d=12 p=11 calls, msolve empty output; 1 = d=18 p=17 timeout at 600 s)")
def fitB(rows):
    U=np.array([r[2] for r in rows],float); y=np.array([math.log2(r[3]) for r in rows])
    if len(set(U))<2: return None
    A=np.vstack([U,np.ones_like(U)]).T; return np.linalg.lstsq(A,y,rcond=None)[0]
if len(bcells)>=2 and len({b[2] for b in bcells})>=2:
    cB=fitB(bcells); u=cB[0]; bb=[]
    for _ in range(B):
        idx=rng.integers(0,len(bcells),len(bcells)); r=fitB([bcells[i] for i in idx])
        if r is not None: bb.append(r)
    bb=np.array(bb); P(); P("## Gate B fit: log2 T_lift = u U + b0 (cell medians)")
    P(f"- u = {fmt(u)} 95% CI [{fmt(ci(bb[:,0])[0])}, {fmt(ci(bb[:,0])[1])}]; b0 = {fmt(cB[1])}; bootstrap fits {len(bb)}/{B}")
    # c_hat
    P(); P("## c_hat(k) = u * U(2^k) / k  (independent bootstrap over Gate A cells and Gate B cells)")
    P("| k | d*(2^k) point | U point | c_hat point | 95% CI |"); P("|---|---|---|---|---|")
    cres={}
    for k in (64,128,256):
        dp=dstar(co,k); Up=5*dp/6+2 if math.isfinite(dp) else math.inf; cp=u*Up/k
        vals=[]
        nA=len(bs); nB_=len(bb)
        for i in range(B):
            a=bs[i%nA]; b=bb[i%nB_]; d_=dstar(a,k); vals.append(b[0]*(5*d_/6+2)/k if math.isfinite(d_) else math.inf)
        vals=np.array(vals); finite=np.isfinite(vals)
        lo,hi=ci(vals[finite]) if finite.any() else (float('nan'),float('nan'))
        # shuffle pairing: use independent permutations to decouple A and B
        permA=rng.permutation(nA); permB=rng.permutation(nB_); v2=[]
        for i in range(B):
            a=bs[permA[i%nA]]; b=bb[permB[i%nB_]]; d_=dstar(a,k); v2.append(b[0]*(5*d_/6+2)/k if math.isfinite(d_) else math.inf)
        v2=np.array(v2); fin2=np.isfinite(v2)
        lo,hi=(float(np.percentile(v2[fin2],2.5)),float(np.percentile(v2[fin2],97.5))) if fin2.any() else (float('nan'),float('nan'))
        cres[k]=(cp,lo,hi,float((~fin2).mean()))
        P(f"| {k} | {dp} | {Up if math.isfinite(Up) else 'inf'} | {cp:.3f} | [{lo:.3f}, {hi:.3f}] (non-finite resamples: {(~fin2).mean():.3f}) |")
    # out-of-sample
    P(); P("## Out-of-sample check (fit on all but the largest cell, validate on it, refit)")
    big=max(ss,key=lambda c:(c["d"],c["p"])); rest=[c for c in fitrows if c is not big]
    co2=fitA(rest)
    if co2 is not None:
        pred=co2[0]*big["d"]+co2[1]*math.log2(big["p"])+co2[2]; P(f"- Gate A: largest cell d={big['d']} p={big['p']}: log2 S observed {math.log2(big['S']):.3f}, predicted from the rest {pred:.3f} (alpha_rest={co2[0]:.3f}, beta_rest={co2[1]:.3f})")
    bigB=max(bcells,key=lambda b:(b[2],b[1])); restB=[b for b in bcells if b is not bigB]; c2=fitB(restB)
    if c2 is not None:
        predB=c2[0]*bigB[2]+c2[1]; P(f"- Gate B: largest cell d={bigB[0]} p={bigB[1]} (U={bigB[2]}): log2 T observed {math.log2(bigB[3]):.3f}, predicted {predB:.3f} (u_rest={c2[0]:.3f})")
        for k in (64,128,256):
            dp=dstar(co2 if co2 is not None else co,k); P(f"- c_hat({k}) with the out-of-sample fits: {c2[0]*(5*dp/6+2)/k:.3f}")
    json.dump({"alpha":[co[0],*ALPHA_CI],"beta":[co[1],*ci(bs[:,1])],"gamma":[co[2],*ci(bs[:,2])],"u":[u,*ci(bb[:,0])],
               "c_hat":{k:{"point":v[0],"lo":v[1],"hi":v[2],"nonfinite_frac":v[3]} for k,v in cres.items()}},open("results/fits.json","w"),indent=1)
open("results/analysis.md","w").write("\n".join(out)+"\n")
