import sys, json, time
from model import *
from run_ceilings import pres, leads
name=sys.argv[1]; m=int(sys.argv[2]); ts=[int(z) for z in sys.argv[3].split(',')]; nom=int(sys.argv[4])
n,sups,cf,om=pres(name,m); om=om[:nom]
out=[]
for t in ts:
    t0=time.time(); best=-1; bl=None
    for lam in leads(sups,om):
        gens=[(list(s),l) for s,l in zip(sups,lam)]
        M=Model(n,gens,t); rl=reach_lp(M,cf,tol=2e-4,hi=0.3)
        if rl>best: best=rl; bl=lam; dim=M.nz
        print(' lam',lam,rl,round(time.time()-t0,1),flush=True)
    row=dict(pres=name,m=m,t=t,lp_upper=best,lam=bl,dim=dim,sec=round(time.time()-t0,1)); print(row,flush=True); out.append(row)
    json.dump(out,open(f'LP_{name}_m{m}.json','w'))
