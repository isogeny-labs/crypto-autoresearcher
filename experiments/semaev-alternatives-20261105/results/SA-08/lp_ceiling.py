# Asymptotic determinant ceiling of the Rees-algebra (Coppersmith) lattice over ALL down-closed supports.
# f = S_{m+1}(x_1..x_m; r): degree d=2^(m-1) in each variable, monic leading monomial (x1..xm)^d.
# Basis g_a = x^(a-d*k) f^k p^(K-k), k=kappa(a)=floor(min_i a_i / d).  Condition: sum_{a in R} [delta*sum(a) - kappa(a)] < 0.
# Min over down-closed R = minimum-weight closure problem (LP is totally unimodular) -> scipy linprog (HiGHS).
import numpy as np, itertools, sys, json
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
_SUB={}
def cellmin(c):
    m=len(c); s=8
    if m not in _SUB:
        g=(np.arange(s)+0.5)/s
        _SUB[m]=np.array(list(itertools.product(g,repeat=m)))
    pts=_SUB[m]+np.array(c)
    return pts.min(axis=1).mean()
def min_closure(m, n, delta, d, cont=True):
    # cells indexed by integer vectors in [0,n)^m ; cost at cell centre (continuous kappa=min/d) 
    idx = {}
    cells = list(itertools.product(range(n), repeat=m))
    for i,c in enumerate(cells): idx[c]=i
    N=len(cells)
    cost=np.zeros(N)
    for i,c in enumerate(cells):
        # exact integral of delta*sum(a) over the unit cell, minus cell-average of min(a)/d (sub-sampled midpoint rule)
        cm=cellmin(c)
        cost[i]=delta*(sum(c)+m/2.0)-cm/d
    # constraints z(c) >= z(c+e_j)  (down-closed: if c+e_j in R then c in R)
    rows=[];cols=[];vals=[];r=0
    A=lil_matrix((N*m,N))
    k=0
    for c,i in idx.items():
        for j in range(m):
            if c[j]+1<n:
                c2=list(c);c2[j]+=1
                A[k,idx[tuple(c2)]]=1;A[k,i]=-1;k+=1
    A=A[:k].tocsr()
    res=linprog(cost,A_ub=A,b_ub=np.zeros(k),bounds=(0,1),method='highs')
    return res.fun, res.x, cells
def threshold(m,n,lo,hi,it=22):
    d=2**(m-1)
    for _ in range(it):
        mid=(lo+hi)/2
        f,_,_=min_closure(m,n,mid,d)
        if f< -1e-9: lo=mid
        else: hi=mid
    return lo
if __name__=="__main__":
    out={}
    for m,ns,lo,hi in [(2,[10,20,40],0.1,0.3),(3,[6,9,12],0.02,0.08)]:
        for n in ns:
            t=threshold(m,n,lo,hi,it=16)
            print("m",m,"grid",n,"delta*",round(t,5),"1/delta*",round(1/t,3),flush=True)
            out[f"{m}_{n}"]=t
    json.dump(out,open("lp_ceiling.json","w"),indent=1)
