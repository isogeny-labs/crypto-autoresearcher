import json,glob,math,sys,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def mink(K,kind):
    A=2*K
    S=[(u,v) for u in range(A+1) for v in range(A+1) if kind=='box' or u+v<=A+K]
    return sum(min(K,min(a,b)//2) for a,b in S)/sum(a+b for a,b in S)
def cross(ds,ys):
    # smallest delta where y (= l - hg) crosses from <0 to >=0, linear interpolation; None if no crossing in grid
    for i in range(len(ds)-1):
        if ys[i]<0<=ys[i+1]: return ds[i]+(0-ys[i])*(ds[i+1]-ds[i])/(ys[i+1]-ys[i])
    return None
res=[];fig,axs=plt.subplots(1,2,figsize=(11,4))
for f in sorted(glob.glob('raw/*.json')):
    R=json.load(open(f))
    if not R: continue
    bits,K,kind=R[0]['bits'],R[0]['K'],R[0]['kind']
    for pl in (True,False):
        ds=sorted({r['delta'] for r in R})
        def m(key): return [np.mean([r[key]-r['hg'] for r in R if r['delta']==d and r['planted']==pl]) for d in ds if any(r['delta']==d and r['planted']==pl for r in R)]
        dd=[d for d in ds if any(r['delta']==d and r['planted']==pl for r in R)]
        c2=cross(dd,m('l2')); c1=cross(dd,m('l1')); cg=cross(dd,[np.mean([r['gh']-r['hg'] for r in R if r['delta']==d and r['planted']==pl]) for d in dd])
        # excess of lambda_2 over Gaussian heuristic (log) at the crossing delta, and at fixed delta 0.15
        def at(d0,key):
            v=[np.mean([r[key] for r in R if r['delta']==d and r['planted']==pl]) for d in dd]; return float(np.interp(d0,dd,v))
        res.append(dict(bits=bits,K=K,kind=kind,planted=pl,n=R[0]['n'],mink=mink(K,kind),cross_l1=c1,cross_l2=c2,cross_gh=cg,
            l2_minus_gh_at_015=at(0.15,'l2')-at(0.15,'gh'),l1_minus_gh_at_015=at(0.15,'l1')-at(0.15,'gh'),ntr=len([r for r in R if r['delta']==dd[0] and r['planted']==pl])))
json.dump(res,open('crossings.json','w'),indent=1)
with open('crossing_table.md','w') as f:
    f.write("| bits | K | support | n | planted | Minkowski delta_K | GH crossing | lambda_1 crossing | lambda_2 crossing | log(lam2/GH) at d=.15 |\n|---|---|---|---|---|---|---|---|---|---|\n")
    fm=lambda x:'n/a' if x is None else '%.4f'%x
    for r in sorted(res,key=lambda r:(r['kind'],r['bits'],r['K'],not r['planted'])):
        f.write(f"| {r['bits']} | {r['K']} | {r['kind']} | {r['n']} | {r['planted']} | {r['mink']:.4f} | {fm(r['cross_gh'])} | {fm(r['cross_l1'])} | {fm(r['cross_l2'])} | {r['l2_minus_gh_at_015']:.2f} |\n")
print(open('crossing_table.md').read())
