"""Asymptotic JM-basic reach from the (weighted) Newton polytope, SA-06 formula generalised to weighted bounds.
Bound for variable j: X_j = p^(c0_j + c1_j*delta). Condition (n+1)*sum_j (c0_j + c1_j delta) g_j < 1, g = centroid of P.
P = Newton polytope (conv of support) or its down-closure hull; best (largest delta) reported. Exact rational where possible."""
import json, itertools, numpy as np
from fractions import Fraction as F
from scipy.spatial import ConvexHull, Delaunay
def centroid_vol(pts):
    pts=np.array(sorted(set(map(tuple,pts))),float)
    hull=ConvexHull(pts); d=Delaunay(pts[hull.vertices])
    V=0; G=np.zeros(pts.shape[1])
    for s in d.simplices:
        P=pts[hull.vertices][s]; M=P[1:]-P[0]
        v=abs(np.linalg.det(M)); import math; v/=math.factorial(pts.shape[1])
        V+=v; G+=v*P.mean(0)
    return V,G/V
def downclose(pts):
    out=set()
    for q in pts:
        for r in itertools.product(*[range(e+1) for e in q]): out.add(r)
    return out
def reach(pts,c0,c1):
    best=None
    for lab,S in (("newton",pts),("downclosed",downclose(pts))):
        V,g=centroid_vol(S); n=len(c0)
        A=(n+1)*sum(c0[j]*g[j] for j in range(n)); B=(n+1)*sum(c1[j]*g[j] for j in range(n))
        d=(1-A)/B if B>0 else float('inf'); d=max(d,0.0)
        row=dict(hull=lab,vol=round(V,6),centroid=[round(x,5) for x in g],delta=d)
        if best is None or d>best['delta']: best=row
    return best
SV=json.load(open('supports_vieta.json'))
out=[]
for m in (2,3,4):
    d=2**(m-1)
    box=[tuple(c) for c in itertools.product((0,d),repeat=m)]
    r=reach(box,[0]*m,[1]*m); out.append(dict(pres='i',m=m,**r,exact=str(F(2,m*(m+1)*d))))
    sv=[tuple(c) for c in SV[str(m)]]
    r=reach(sv,[0]*m,[k+1 for k in range(m)]); out.append(dict(pres='ii',m=m,**r))
    # (vi) integer lift: support box corner x (d..d) , c^1, origin; X_c = p^((d-1)+Dtop*delta) per run_ceilings
    Dtop={2:2,3:6,4:12}[m]
    vi=[tuple(list(c)+[0]) for c in box]+[tuple([0]*m+[1])]
    r=reach(vi,[0]*m+[d-1],[1]*m+[Dtop]); out.append(dict(pres='vi',m=m,**r))
    # (v) naive product S(x,xR)S(x,xR+T): box 2d (not the SA-06 symmetrisation)
    box2=[tuple(c) for c in itertools.product((0,2*d),repeat=m)]
    r=reach(box2,[0]*m,[1]*m); out.append(dict(pres='v_naive_product',m=m,**r))
for r in out: print(r)
json.dump(out,open('analytic_reach.json','w'),indent=1)
