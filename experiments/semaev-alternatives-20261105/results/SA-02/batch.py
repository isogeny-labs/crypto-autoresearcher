# Batch-window variant of the u-sieve: u (or x2 for the control) in a window of size V, small roots of a bivariate (e1,v) lattice mod p.
import random, time, json, sys, sympy as sp, numpy as np
from common import *
from bilat import solve
X1,V_,E1,U0=sp.symbols('X1 V E1 U0')
def poly_ctrl(p,xR,c):
    x2=c+V_
    e=sp.expand((X1-x2)**2*xR**2-2*((X1+x2)*(X1*x2)+14)*xR+(X1*x2)**2-28*(X1+x2))
    return {tuple(m):int(cf)%p for m,cf in sp.Poly(e,X1,V_).terms()}
_gen=None
def poly_conic(p,xR,u0):
    global _gen
    if _gen is None:
        xr=sp.symbols('xr'); u=U0+V_
        g=E1**4-8*xr*E1**3-2*u**2*E1**2+(8*xr*u**2-448)*E1+16*xr**2*u**2-448*xr+u**4
        _gen=(xr,sp.Poly(sp.expand(g),E1,V_,U0,xr))
    xr,P=_gen
    d={}
    for (i,j,k,l),cf in P.terms():
        key=(i,j); d[key]=(d.get(key,0)+int(cf)*pow(u0,k,p)*pow(xR,l,p))%p
    return {k:v for k,v in d.items() if v}
def trial(kind,p,B,V,t,rng):
    x1,x2,R=plant(p,B,rng); xR=R[0]
    if kind=='ctrl':
        # window on x2 (note the planted pair (x1,x2) could be labelled either way; use x2 as given)
        c=x2-rng.randrange(V); c=max(c,0)
        f=poly_ctrl(p,xR,c); Xb=B; Yb=V
        target=(x1,x2-c)
    else:
        u=abs(x1-x2); u0=max(u-rng.randrange(V),0)
        f=poly_conic(p,xR,u0); Xb=2*B; Yb=V
        target=(x1+x2,u-u0)
    if f.get((0,0),0)==0: return None,0
    t0=time.perf_counter(); s=solve(f,p,Xb,Yb,t); dt=time.perf_counter()-t0
    return target in s,dt
if __name__=='__main__':
    kind=sys.argv[1]; pbits=int(sys.argv[2]); t=int(sys.argv[3]); kmin=int(sys.argv[4]); kmax=int(sys.argv[5]); n=int(sys.argv[6])
    p=mkp(pbits); rng=random.Random(99); rows=[]
    for k in range(kmin,kmax+1):
        B=2**k; V=B
        while True:
            res=[trial(kind,p,B,V,t,rng) for _ in range(n)]
            ok=sum(1 for r,_ in res if r); tl=float(np.mean([d for _,d in res]))
            print(kind,'B',B,'V',V,'succ',ok,'/',n,'t_lat %.3f'%tl,flush=True)
            if ok>=0.8*n or V==1: break
            V//=2
        rng_range=B if kind=='ctrl' else B
        windows=-(-rng_range//V)
        rows.append(dict(kind=kind,pbits=pbits,t=t,B=B,Vstar=V,succ=ok,n=n,t_lat=tl,windows=windows,exp_time=(windows+1)/2*tl))
        print('  ->',rows[-1],flush=True)
    json.dump(rows,open(f'batch_{kind}_p{pbits}_t{t}.json','w'))
