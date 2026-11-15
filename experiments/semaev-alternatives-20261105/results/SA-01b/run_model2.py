import sys, json, time
from model import *
from run_ceilings import pres, leads
name=sys.argv[1]; m=int(sys.argv[2]); ts=[int(z) for z in sys.argv[3].split(',')]; tl=float(sys.argv[4]); frac=float(sys.argv[5]) if len(sys.argv)>5 else 0.9
n,sups,cf,om=pres(name,m); lam=leads(sups,om[:1])[0]
gens=[(list(s),l) for s,l in zip(sups,lam)]
out=[]
for t in ts:
    t0=time.time(); M=Model(n,gens,t)
    print('built dim',M.nz,'N',M.N,round(time.time()-t0,1),flush=True)
    a,b=0.0,0.06
    while b-a>4e-4:
        mid=(a+b)/2; v=M.lp_ratio(cf(mid)); print('  lp',round(mid,5),v,round(time.time()-t0,1),flush=True)
        if v is not None and v>1+1e-9: a=mid
        else: b=mid
    rl=a; print('t',t,'LP upper',rl,round(time.time()-t0,1),flush=True)
    # MILP bracket [frac*rl, rl]; verify lo feasible, else widen
    lo=frac*rl; g,x,db=M.milp_gain(cf(lo),tl)
    while (g is None or g<=1e-7) and lo>1e-4:
        lo*=0.8; g,x,db=M.milp_gain(cf(lo),tl)
    hi=rl+0.0005
    while hi-lo>4e-4:
        mid=(lo+hi)/2; g,x,db=M.milp_gain(cf(mid),tl); print('  milp',round(mid,5),g,round(time.time()-t0,1),flush=True)
        if g is not None and g>1e-7: lo=mid
        else: hi=mid
    row=dict(pres=name,m=m,t=t,lp_upper=rl,milp_lower=lo,lam=lam,dim=M.nz,sec=round(time.time()-t0,1)); print(row,flush=True); out.append(row)
    json.dump(out,open(f'M2_{name}_m{m}_t{ts[0]}.json','w'))
