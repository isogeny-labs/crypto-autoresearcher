import sys, json, time
from model import *
from run_ceilings import pres, leads, omegas_for
name=sys.argv[1]; m=int(sys.argv[2]); ts=[int(z) for z in sys.argv[3].split(',')]
nom=int(sys.argv[4]); tl=float(sys.argv[5]) if len(sys.argv)>5 else 60
n,sups,cf,om=pres(name,m); om=om[:nom]
out=[]
for t in ts:
    t0=time.time(); best=dict(lp=-1,milp=-1,lam=None)
    for lam in leads(sups,om):
        gens=[(list(s),l) for s,l in zip(sups,lam)]
        try: M=Model(n,gens,t)
        except Exception as e: print("model fail",e); continue
        rl=reach_lp(M,cf,tol=2e-4,hi=0.3)
        rm=(rl if name in ('i','v') else reach_milp(M,cf,hi=rl+0.0005,tol=3e-4,tl=tl)) if rl>0.002 else 0.0
        if rm>best['milp'] or (rm==best['milp'] and rl>best['lp']): best=dict(lp=rl,milp=rm,lam=lam,dim=M.nz)
    row=dict(pres=name,m=m,t=t,lp_upper=best['lp'],milp_lower=best['milp'],lam=best['lam'],sec=round(time.time()-t0,1)); print(row,flush=True); out.append(row)
    json.dump(out,open(f'M_{name}_m{m}.json','w'))
