# Asymptotic JM-basic reach for every cell and both conventions.
#  "target"  : decomposition of a random target; x_R is a full-size modular parameter, unknowns = m small variables.
#  "allsmall": all m+1 variables are windowed (tree-internal-node / free-relation setting); unknowns = m+1.
import json, math, numpy as np
from scipy.spatial import Delaunay, ConvexHull
def poly_stats(pts):
    pts=np.array(pts,float); pts=pts-pts.min(0); n=pts.shape[1]
    u=np.unique(pts,axis=0); u=u[ConvexHull(u).vertices]; tri=Delaunay(u)
    vol=0; cen=np.zeros(n)
    for s in tri.simplices:
        V=u[s]; v=abs(np.linalg.det(V[1:]-V[0]))/math.factorial(n); vol+=v; cen+=v*V.mean(0)
    return vol,cen/vol,u,pts.max(0)
def load():
    cells=[]
    P=json.load(open("supports.json")); S=json.load(open("supports_sym.json"))
    for key,v in P.items():
        name,Sx=key.split("|"); n=int(Sx[1:]); sup=np.array(v["support"])
        if name=="generic2": continue
        cells.append((name,n,"target",np.unique(sup[:,:n-1],axis=0),len(sup)))
        cells.append((name,n,"allsmall",sup,len(sup)))
    for key,v in S.items():
        name,Sx,mode=key.split("|"); n=int(Sx[1:]); sup=np.array(v["support"])
        cells.append((name,n,mode,sup,len(sup)))
    return cells
if __name__=="__main__":
    rows=[]
    for name,n,mode,pts,nf in load():
        nv=pts.shape[1]
        vol,g,u,mx=poly_stats(pts)
        mx=(pts-pts.min(0)).max(0)
        d=1/((nv+1)*g.sum())
        rows.append(dict(cell=name,S=f"S{n}",mode=mode,nvars=nv,monos=len(pts),box=int(np.prod(mx+1)),vol_frac=round(vol/np.prod(mx),4),sum_centroid=round(float(g.sum()),4),delta_basic=d,inv_delta=1/d,box_delta=1/((nv+1)*nv*mx.max()/2)))
        print(f"{name:9s} S{n} {mode:8s} nv={nv} monos={len(pts):6d}/{int(np.prod(mx+1)):6d} vol/box={vol/np.prod(mx):.3f} sumg={g.sum():7.3f}  delta={d:.5f}=1/{1/d:6.1f}")
    json.dump(rows,open("reach_all.json","w"),indent=1)
