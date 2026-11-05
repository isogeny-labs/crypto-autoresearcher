import sys, json, time
from run_ceilings import *
name=sys.argv[1]; m=int(sys.argv[2]); ts=[int(z) for z in sys.argv[3].split(',')]
nom=int(sys.argv[4]) if len(sys.argv)>4 else 8
tol=float(sys.argv[5]) if len(sys.argv)>5 else 3e-4
n,sups,cf,om=pres(name,m)
om=om[:nom]
out=[]
for t in ts:
    t0=time.time()
    r,lam=reach_best(n,sups,cf,t,om,hi=0.45,tol=tol)
    row=dict(pres=name,m=m,t=t,reach=r,lam=lam,sec=round(time.time()-t0,1)); print(row,flush=True); out.append(row)
    json.dump(out,open(f'ceilL_{name}_m{m}.json','w'))
