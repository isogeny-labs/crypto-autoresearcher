# Asymptotic Jochemsz-May basic reach from Newton polytope: delta_A = 1/((m+1)*sum_i g_i), g = centroid of Newt(f) (translated to touch axes)
import json, math, numpy as np
from scipy.spatial import Delaunay
D=json.load(open("supports.json"))
def poly_stats(pts):
    pts=np.array(pts,float); pts=pts-pts.min(0); m=pts.shape[1]
    u=np.unique(pts,axis=0)
    tri=Delaunay(u)
    vol=0; cen=np.zeros(m)
    for s in tri.simplices:
        V=u[s]; v=abs(np.linalg.det(V[1:]-V[0]))/math.factorial(m)
        vol+=v; cen+=v*V.mean(0)
    return vol, cen/vol, u, pts.max(0)
if __name__=="__main__":
    rows=[]
    for key,v in D.items():
        name,S=key.split("|"); n=int(S[1:]); m=n-1
        sup=np.array(v["support"]); proj=np.unique(sup[:,:m],axis=0)
        vol,g,u,mx=poly_stats(proj)
        dA=1/((m+1)*g.sum())
        rows.append(dict(cell=name,S=S,m=m,full_monos=len(sup),proj_monos=len(proj),box=int(np.prod(mx+1)),maxdeg=mx.tolist(),vol_frac=vol/np.prod(mx),centroid=g.round(4).tolist(),sumg=float(g.sum()),delta_basic=dA))
        print(f"{name:9s} {S} m={m} proj_monos={len(proj):5d}/{int(np.prod(mx+1))} deg={mx.astype(int).tolist()} vol/box={vol/np.prod(mx):.3f} sum_g={g.sum():.3f} delta_basic={dA:.5f} (1/{1/dA:.1f})")
    json.dump(rows,open("reach_basic.json","w"),indent=1)
