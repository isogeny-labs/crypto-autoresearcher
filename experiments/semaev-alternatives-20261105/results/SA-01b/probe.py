# single-delta LP probe: is LP gain >1 at delta? (reach_LP monotone => reach_LP < delta if not). prints Model size and LP value
import sys, time
from model import *
from run_ceilings import pres, leads
name=sys.argv[1]; m=int(sys.argv[2]); t=int(sys.argv[3]); dl=float(sys.argv[4])
n,sups,cf,om=pres(name,m); lam=leads(sups,om[:1])[0]
gens=[(list(s),l) for s,l in zip(sups,lam)]
t0=time.time(); M=Model(n,gens,t); print('built dim',M.nz,'vars',M.N,'rows',M.nrows,round(time.time()-t0,1),flush=True)
v=M.lp_ratio(cf(dl)); print(name,m,'t',t,'delta',dl,'LP ratio',v,'(>1 feasible)',round(time.time()-t0,1),flush=True)
