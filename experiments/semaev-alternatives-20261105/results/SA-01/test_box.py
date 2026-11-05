import sys, time
from coppersmith_lp import *
# box polynomial [0,1]^n scaled (d=1): continuum check; reach = delta*(d=1)/d ; expect 2/(n(n+1))
for n in (2,3):
    for t in (2,3,4,5,6):
        t0=time.time()
        corner=tuple([1]*n)
        gens=[([corner,tuple([0]*n)],corner)]
        # d=1 box: use support = corner only (down-closed M means rest implied), lam=corner
        r=reach(n,gens,lambda dl:[dl]*n,t,hi=0.6,tol=2e-4)
        print(n,t,round(r,4),"cube prediction",round(2/(n*(n+1)),4),f"{time.time()-t0:.1f}s",flush=True)
