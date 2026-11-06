import time
from model import *
from run_ceilings import pres
for name in ('i','ii'):
    n,sups,cf,om=pres(name,2)
    lam=(2,2) if name=='i' else (2,0)
    for t in (3,4,6,8):
        t0=time.time(); M=Model(n,[(sups[0],lam)],t)
        rl=reach_lp(M,cf); rm=reach_milp(M,cf,tl=30)
        print(name,t,"LP",round(rl,4),"MILP",round(rm,4),round(time.time()-t0,1),flush=True)
