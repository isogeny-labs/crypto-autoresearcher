"""
Automated-shift ceiling calculator (substitute for cuso / sumset calculator).
Class: lattices spanned by p^{t-|k|} x^s prod_i g_i^{k_i} (|k|<=t), monomial set M down-closed in N^n,
triangular basis w.r.t. a monomial order with leading monomials lam_i of the generators g_i.
Asymptotic condition (HG/LLL): sum_{y in M} cost(y) < sum_{y in M} level(y), cost(y)=sum_j e_j y_j  (e_j = log_p X_j).
level(y)=max |k| with y - sum k_i lam_i >=0 and  (y - sum k_i lam_i) + sum k_i*Max(g_i) subset M.
Because M is down-closed, the latter is: y' = y - sum k_i lam_i; all points y'+ c, c in MaxSum(k) lie in M.
LP (Charnes-Cooper): maximise sum_y level subject to sum_y cost*z_y = 1, z down-closed in [0,tau]; delta* = optimum value
(integer M gives lower bound on reach, LP relaxation gives upper bound for the class).
exps: for each variable, tuple (a,b): X_j = p^(a*delta+b).
"""
import numpy as np, itertools, scipy.sparse as sp
from scipy.optimize import linprog

def maxelems(pts):
    pts=sorted(set(pts))
    out=[]
    for q in pts:
        if not any(r!=q and all(r[i]>=q[i] for i in range(len(q))) for r in pts): out.append(q)
    return out
def sumset_max(A,B):
    return maxelems([tuple(a[i]+b[i] for i in range(len(a))) for a in A for b in B])
def powers_max(C,kmax):
    P=[tuple([0]*len(C[0]))]; res=[[P[0]]]
    cur=[P[0]]
    for k in range(1,kmax+1):
        cur=sumset_max(cur,C); res.append(cur)
    return res   # res[k] = max elements of k-fold sumset
def compositions(r,t):
    for ks in itertools.product(range(t+1),repeat=r):
        if 0<sum(ks)<=t: yield ks

def build_and_solve(n, gens, cost, t, ub=None, integer=False):
    """gens: list of (support_points, lam) ; cost: list of n floats (exponent of X_j in log_p units)
    returns optimum of max sum level s.t. sum cost*z=1  (=delta-type ratio: >1 means feasible)"""
    r=len(gens)
    maxs=[maxelems(g[0]) for g in gens]
    lam=[g[1] for g in gens]
    pw=[powers_max(maxs[i],t) for i in range(r)]
    # grid extents
    ext=[0]*n
    for ks in compositions(r,t):
        for j in range(n):
            ext[j]=max(ext[j], sum(ks[i]*max(c[j] for c in maxs[i]) for i in range(r)))
    if ub is not None: ext=[min(e,u) for e,u in zip(ext,ub)]
    shape=[e+1 for e in ext]
    idx=lambda y: int(np.ravel_multi_index(y,shape))
    npts=int(np.prod(shape))
    pts=list(itertools.product(*[range(s) for s in shape]))
    # variables: z (npts), tau, v_{y,ks}
    vlist=[]  # (yindex, ks, closure idx list)
    for y in pts:
        for ks in compositions(r,t):
            yp=[y[j]-sum(ks[i]*lam[i][j] for i in range(r)) for j in range(n)]
            if min(yp)<0: continue
            # closure points
            combos=[()]
            sets=[pw[i][ks[i]] for i in range(r) if ks[i]>0]
            cl=[tuple([0]*n)]
            for S_ in sets: cl=sumset_max(cl,S_)
            cps=[tuple(yp[j]+c[j] for j in range(n)) for c in cl]
            if any(cp[j]>ext[j] for cp in cps for j in range(n)): continue
            vlist.append((idx(y),ks,[idx(cp) for cp in cps],sum(ks)))
    nv=len(vlist); nz=npts; N=nz+1+nv
    TAU=nz
    c=np.zeros(N)
    for q,(yi,ks,cl,lev) in enumerate(vlist): c[nz+1+q]=-lev
    rows=[];cols=[];vals=[];rhs=[];ri=0
    # v_{y,ks} <= z_cp   -> v - z <=0
    for q,(yi,ks,cl,lev) in enumerate(vlist):
        for cp in cl:
            rows+= [ri,ri]; cols+=[nz+1+q,cp]; vals+=[1,-1]; rhs.append(0); ri+=1
    # sum_ks v_{y,ks} <= z_y... (one composition per y, and v<=z_y(implied by closure, include y) ) -> sum v <= z_y
    byy={}
    for q,(yi,ks,cl,lev) in enumerate(vlist): byy.setdefault(yi,[]).append(q)
    for yi,qs in byy.items():
        for q in qs: rows.append(ri); cols.append(nz+1+q); vals.append(1)
        rows.append(ri); cols.append(yi); vals.append(-1); rhs.append(0); ri+=1
    # down-closure z_{y+e_j} <= z_y
    for y in pts:
        for j in range(n):
            if y[j]+1<shape[j]:
                y2=list(y); y2[j]+=1
                rows+=[ri,ri]; cols+=[idx(tuple(y2)),idx(y)]; vals+=[1,-1]; rhs.append(0); ri+=1
    # z_y <= tau
    for y in pts:
        rows+=[ri,ri]; cols+=[idx(y),nz]; vals+=[1,-1]; rhs.append(0); ri+=1
    A=sp.csr_matrix((vals,(rows,cols)),shape=(ri,N))
    # equality sum cost*z =1
    ce=np.zeros(N)
    for y in pts: ce[idx(y)]=sum(cost[j]*y[j] for j in range(n))
    # allow tiny weight so that z at origin has cost 0 -> need normalisation to bound; origin cost=0: bound z_origin<=tau, tau<=? add tau<=1e6
    Aeq=sp.csr_matrix(ce.reshape(1,-1))
    bounds=[(0,None)]*nz+[(0,1e3)]+[(0,1)]*nv
    res=linprog(c,A_ub=A,b_ub=np.array(rhs),A_eq=Aeq,b_eq=[1],bounds=bounds,method='highs')
    if res.status!=0: return None,None
    return -res.fun, dict(npts=npts,nv=nv,rows=ri,x=res.x,nz=nz,shape=shape,vlist=vlist,pts=pts)

def reach(n, gens, cost_fn, t, lo=0.0, hi=1.0, tol=1e-4, ub=None):
    """bisection on delta: feasible iff LP optimum >1 (det<p^{t dim})"""
    for _ in range(40):
        mid=(lo+hi)/2
        val,info=build_and_solve(n,gens,cost_fn(mid),t,ub)
        if val is None: hi=mid; continue
        if val>1: lo=mid
        else: hi=mid
        if hi-lo<tol: break
    return lo
