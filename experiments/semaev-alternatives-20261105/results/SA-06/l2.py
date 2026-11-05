# Extended-strategy search over convex shift regions K = P + [0,e]^n (continuum, asymptotic t->inf, greedy optimal levels).
# delta(K,a0) = int_K min(tau(alpha),1) d alpha / int_K sum(alpha) d alpha,
# tau(alpha)=max{tau: alpha - tau*a0 >=0, alpha - tau*a0 + tau*P subset K}.  K=P reproduces JM-basic.
import json, sys, math, itertools, numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import minimize
rng=np.random.default_rng(5)
def hull_vertices(pts):
    pts=np.array(pts,float); pts=pts-pts.min(0); u=np.unique(pts,axis=0)
    return u[ConvexHull(u).vertices]
def K_rep(V,e):
    n=V.shape[1]
    sc=V.max(); corners=np.array(list(itertools.product(*[[0,x*sc] for x in e])))
    pts=(V[:,None,:]+corners[None,:,:]).reshape(-1,n)
    H=ConvexHull(pts); return pts[H.vertices],H.equations
def objective(V,a0,e,U,emax):
    n=V.shape[1]
    KV,eq=K_rep(V,e)
    lo=np.zeros(n); hi=V.max(0)+np.max(e)*V.max()  # bbox
    A=lo+U*(hi-lo)
    s=-(A@eq[:,:n].T+eq[:,n])          # slack >=0 inside K
    inside=(s>=-1e-12).all(1)
    A=A[inside]; s=s[inside]
    Q=(V-a0)@eq[:,:n].T                   # (vertices x facets)
    Qf=Q.max(0)
    tau=np.ones(len(A))
    m=Qf>1e-12
    if m.any(): tau=np.minimum(tau,(s[:,m]/Qf[m]).min(1))
    pos=a0>1e-12
    if pos.any(): tau=np.minimum(tau,(A[:,pos]/a0[pos]).min(1))
    tau=np.clip(tau,0,1)
    return tau.mean()/A.sum(1).mean()
def best_for(V,nsamp=60000,nA0=3,iters=25,seed=0):
    n=V.shape[1]; U=np.random.default_rng(seed).random((nsamp,n))
    zero=np.zeros(n)
    base=[]
    # candidate leading vertices: those with extreme sums, plus random
    idx=list(np.argsort(-V.sum(1))[:2])+list(np.random.default_rng(seed).choice(len(V),size=min(nA0,len(V)),replace=False))
    idx=list(dict.fromkeys(idx))[:nA0]
    out=[]
    for i in idx:
        a0=V[i]
        b0=objective(V,a0,zero,U,0)
        f=lambda e: -objective(V,a0,np.clip(e,0,3),U,3)
        best=(b0,zero)
        for start in (np.full(n,0.3),np.full(n,0.8)):
            r=minimize(f,start,method="Nelder-Mead",options=dict(maxiter=iters,xatol=0.02,fatol=1e-5))
            if -r.fun>best[0]: best=(-r.fun,np.clip(r.x,0,3))
        out.append((i,b0,best[0],best[1]))
    return out
if __name__=="__main__":
    import reach_all
    cells=reach_all.load()
    want=[("generic",3,"target"),("generic",4,"target"),("generic",5,"target"),
          ("generic",3,"allsmall"),("j0",3,"allsmall"),("j1728",3,"allsmall"),
          ("generic",4,"allsmall"),("j0",4,"allsmall"),("j1728",4,"allsmall")]
    res=[]
    for name,n,mode,pts,_ in cells:
        if (name,n,mode) not in want: continue
        V=hull_vertices(pts)
        if V.shape[1]>4: continue
        t=0
        o=best_for(V,nsamp=60000 if V.shape[1]==4 else 100000)
        b=max(x[1] for x in o); bb=max(x[2] for x in o)
        dmax=max(V.max(0)) if mode=="target" else 1
        print(f"{name:7s} S{n} {mode:8s} nv={V.shape[1]} nvert={len(V)}  basic(MC)={b:.5f} best_ext(MC)={bb:.5f} gain={bb/b-1:+.3%}",flush=True)
        res.append(dict(cell=name,S=f"S{n}",mode=mode,basic_mc=b,ext_mc=bb,gain=bb/b-1,tried=[(int(i),float(b0),float(b1),list(map(float,e))) for i,b0,b1,e in o]))
    json.dump(res,open("l2_results.json","w"),indent=1)
