# Jochemsz-May-style determinant-bound calculator for ONE modular polynomial, shift set = lattice points of k*Newt(f).
# delta(k) = sum_mu u(mu) / sum_mu <w,mu>, maximise over LM vertex a0 and k. Heuristic (algebraic independence assumed).
import itertools, numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from fractions import Fraction

def hull_eq(supp):
    pts=np.array(supp,dtype=float)
    d=pts.shape[1]
    if len(pts)<=d or np.linalg.matrix_rank(pts[1:]-pts[0])<d:
        raise ValueError("degenerate polytope")
    h=ConvexHull(pts)
    return h.equations, h.vertices
def lattice_points(supp,k):
    eq,_=hull_eq(supp)
    pts=np.array(supp); d=pts.shape[1]
    hi=pts.max(0)*k; lo=pts.min(0)*k
    rng=[range(int(l),int(h)+1) for l,h in zip(lo,hi)]
    grid=np.array(list(itertools.product(*rng)),dtype=float)
    ok=np.all(grid@eq[:,:-1].T+k*eq[:,-1]<=1e-9*max(1,k),axis=1)
    return {tuple(int(v) for v in g) for g in grid[ok]}
def is_lm_vertex(a0,supp):
    d=len(a0); others=[s for s in supp if tuple(s)!=tuple(a0)]
    if not others: return True
    # exists c>=1 with c.(a0-v)>=1 for all v
    A=[[-(a0[i]-v[i]) for i in range(d)] for v in others]
    r=linprog(np.zeros(d),A_ub=A,b_ub=[-1]*len(others),bounds=[(1,None)]*d,method='highs')
    return r.status==0
def reach(supp,w,kmax=8,verts_only=True):
    supp=[tuple(s) for s in supp]
    eq,vi=hull_eq(supp)
    pts=np.array(supp)
    verts=[tuple(int(v) for v in pts[i]) for i in vi]
    verts=[v for v in verts if is_lm_vertex(v,supp)]
    best=(0,None,None)
    LP={}
    for k in range(1,kmax+1): LP[k]=lattice_points(supp,k)
    LP[0]={tuple([0]*len(w))}
    wv=np.array(w,dtype=float)
    out={}
    for k in range(1,kmax+1):
        S=LP[k]; den=sum(float(np.dot(wv,mu)) for mu in S)
        for a0 in verts:
            a0=tuple(int(v) for v in a0)
            tot=0
            for mu in S:
                u=0
                for uu in range(k,0,-1):
                    nu=tuple(m-uu*a for m,a in zip(mu,a0))
                    if min(nu)>=0 and nu in LP[k-uu]: u=uu;break
                tot+=u
            dl=tot/den
            if dl>out.get(k,(0,))[0]: out[k]=(dl,a0,len(S))
    return out
