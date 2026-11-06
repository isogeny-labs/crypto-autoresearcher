# Exact JM-basic asymptotic reach via SA-06 formula delta = 1/((n+1) * sum_i w_i g_i), g = centroid of Newt(F),
# with weighted bounds e_k <= X^{w_k} (w = 1..m). Applied to the eliminated norm/Vieta relation F(e_1..e_m) and, as a
# check, to the S_{m+1} box [0,2^{m-1}]^m with unit weights.
import json, numpy as np, itertools, os
from scipy.spatial import ConvexHull, Delaunay
from fractions import Fraction
D=os.path.dirname(os.path.abspath(__file__))+'/../out/'
def centroid(pts):
    pts=np.array(pts,float); tri=Delaunay(pts); V=0; G=np.zeros(pts.shape[1])
    import math
    for s in tri.simplices:
        P=pts[s]; v=abs(np.linalg.det(P[1:]-P[0]))/math.factorial(pts.shape[1]); V+=v; G+=v*P.mean(0)
    return V,G/V
sup=json.load(open(D+'vieta_support.json')); out={}
for m in (2,3,4):
    S=sup[str(m)]['support']; w=np.arange(1,m+1)
    V,g=centroid(S); dv=1/((m+1)*float(w@g))
    # single polynomial box
    box=list(itertools.product([0,2**(m-1)],repeat=m)); Vb,gb=centroid(box); db=1/((m+1)*gb.sum())
    wd=max(int(np.dot(w,a)) for a in S)
    out[m]=dict(n_support=len(S),max_weighted_degree=wd,vol=V,centroid=g.tolist(),delta_norm=dv,delta_single=db,diff=dv-db)
    print(m,len(S),'wdeg',wd,'delta_norm',round(dv,6),'delta_single',round(db,6),'diff',dv-db)
json.dump(out,open(D+'reach_formula.json','w'),indent=1)
