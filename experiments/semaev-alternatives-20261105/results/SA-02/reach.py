# Heuristic Jochemsz-May / Coppersmith asymptotic reach calculator for bivariate f mod p
# (substitute for cuso / Feng et al. calculators, which are not installable here).
# Lattice: rows m' f^k p^(t-k), all monomials in M, triangular w.r.t. a linear order whose max on supp(f) is vertex LM.
import sympy as sp, numpy as np, itertools, json, sys
from fractions import Fraction

def sumset(A,B): return {(a[0]+b[0],a[1]+b[1]) for a in A for b in B}

def hull_points(P, t):
    from scipy.spatial import ConvexHull
    pts=np.array(sorted(P),float)
    h=ConvexHull(pts)
    eq=h.equations
    mx=max(p[0] for p in P)*t; my=max(p[1] for p in P)*t
    out=set()
    for i in range(mx+1):
        for j in range(my+1):
            if all(e[0]*i/t+e[1]*j/t+e[2]<=1e-9 for e in eq): out.add((i,j))
    return out

def vertices(P):
    from scipy.spatial import ConvexHull
    pts=np.array(sorted(P),float); h=ConvexHull(pts)
    return [tuple(int(v) for v in pts[i]) for i in h.vertices]

def build(P,t,LM,mode):
    # returns (sum k(mu), sum mu1, sum mu2, |M|)
    if mode=='sumset':
        M={(0,0)}
        for _ in range(t): M=sumset(M,P)
    else:
        M=hull_points(P,t)
    K=[{(0,0)}]
    for k in range(1,t+1): K.append(sumset(K[-1],P))
    sK=0;s1=0;s2=0;n=0
    for mu in M:
        best=None
        for k in range(t,-1,-1):
            m=(mu[0]-k*LM[0],mu[1]-k*LM[1])
            if m[0]<0 or m[1]<0: continue
            if all((m[0]+c[0],m[1]+c[1]) in M for c in K[k]): best=k;break
        if best is None: return None
        sK+=best;s1+=mu[0];s2+=mu[1];n+=1
    return sK,s1,s2,n

def reach(P,t,a,b,mode='sumset'):
    bestd=0;bestLM=None
    for LM in vertices(P):
        r=build(P,t,LM,mode)
        if r is None: continue
        sK,s1,s2,n=r
        d=sK/(a*s1+b*s2)
        if d>bestd: bestd,bestLM=d,LM
    return bestd,bestLM

x1,x2,e1,e2,u,w,X=sp.symbols('x1 x2 e1 e2 u w X')
A_,B_=0,7
def S3(x1,x2,X,a=A_,b=B_):
    return (x1-x2)**2*X**2-2*((x1+x2)*(x1*x2+a)+2*b)*X+(x1*x2-a)**2-4*b*(x1+x2)
XR=sp.Integer(123457)
def supp(expr,vars_):
    pl=sp.Poly(sp.expand(expr),*vars_)
    return {tuple(m) for m in pl.monoms()}
pres={}
pres['P1 (x1,x2) bounds (1,1)']=(supp(S3(x1,x2,XR),(x1,x2)),(1,1))
pres['P1b (x1,v=x1-x2) bounds (1,1)']=(supp(S3(x1,x1-u,XR),(x1,u)),(1,1))
pres['P2 (e1,u) bounds (1,1)']=(supp(S3((e1+u)/2,(e1-u)/2,XR),(e1,u)),(1,1))
pres['P3 conic (e1,e2) bounds (1,2)']=(supp(S3(x1,x2,XR).subs({}) if False else (XR**2*(e1**2-4*e2)-2*XR*(e1*e2+A_*e1+2*B_)+e2**2-2*A_*e2+A_**2-4*B_*e1),(e1,e2)),(1,2))
pres['P4 (e1,w=u^2) bounds (1,2)']=(supp(S3((e1+u)/2,(e1-u)/2,XR).subs(u,sp.sqrt(w)),(e1,w)),(1,2))
if __name__=='__main__':
    out={}
    for name,(P,(a,b)) in pres.items():
        print(name,'|P|=',len(P),'vertices',vertices(P),flush=True)
        out[name]={'support':sorted(P),'vertices':vertices(P)}
        for mode in ('sumset','hull'):
            for t in (2,4,6,8,10,12):
                d,LM=reach(P,t,a,b,mode)
                out[name][f'{mode}_t{t}']=[d,LM]
                print(f'  {mode:7s} t={t:2d} delta*={d:.5f} LM={LM}',flush=True)
    json.dump(out,open('reach_rows.json','w'),indent=1)
