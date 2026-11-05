# Exact finite-t JM-basic ratio using lattice points of the real polytope P, M_k={a: a-k*a0 in (t-k)P}, vs centroid formula.
import json, itertools, numpy as np, math
from scipy.spatial import ConvexHull
import reach_all
D=json.load(open("supports.json"))
def exact(pts,t):
    pts=np.array(pts,float); pts=pts-pts.min(0); n=pts.shape[1]
    H=ConvexHull(pts); eq=H.equations
    mx=pts.max(0); a0=pts[np.argmax(pts@np.arange(1,n+1)*10+pts.sum(1))]
    grid=np.array(list(itertools.product(*[range(int(t*m)+1) for m in mx])),float)
    def inP(X,s): return (X@eq[:,:n].T+eq[:,n]*s<=1e-9).all(1)   # X in sP
    sk=0
    for k in range(1,t+1):
        if t-k==0: c=1
        else: c=inP(grid,t-k).sum()
        # shifted by k*a0 -> same count
        sk+=c
    M0=grid[inP(grid,t)]; sa=M0.sum()
    return sk/sa
for name in ("generic","j0","j1728"):
    sup=np.array(D[f"{name}|S3"]["support"])
    vol,g,u,mx=reach_all.poly_stats(sup)
    form=1/((sup.shape[1]+1)*g.sum())
    vals=[exact(sup,t) for t in (4,8,12)]
    rich=2*vals[2]-vals[1]  # crude 1/t extrapolation from t=8,12 would be (12*v12-8*v8)/4
    rich=(12*vals[2]-8*vals[1])/4
    print(name,"S3 all-small: exact t=4,8,12:",[round(v,5) for v in vals],"extrap",round(rich,5),"formula",round(form,5))
