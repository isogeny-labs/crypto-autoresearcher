# Check: lattice I^K ∩ Z^R (I=(p,f), support in R=[0,A]^2) has determinant prod_{a in R} p^(K-kappa(a)),  kappa=min(K,floor(min(a,b)/2)).
# i.e. no extra "hidden" integral auxiliary polynomials beyond the leading-monomial-triangular Coppersmith family.
import cypari2, random, itertools, sympy as sp, json
pari=cypari2.Pari(); pari.allocatemem(400*10**6)
def poly_f(p,a,b,r):
    x,y=sp.symbols('x y')
    f=(r**2*(x-y)**2-2*r*(x*y*(x+y)+a*(x+y)+2*b)+(x*y)**2-2*a*x*y+a*a-4*b*(x+y))
    return sp.Poly(sp.expand(f),x,y)
def mul(P,Q,N):  # dict polys
    out={}
    for (i,j),c in P.items():
        for (k,l),d in Q.items(): out[(i+k,j+l)]=out.get((i+k,j+l),0)+c*d
    return out
def test(p,A,K,Abig,seed):
    random.seed(seed); r=random.randrange(2,p); a,b=random.randrange(p),random.randrange(p)
    F=poly_f(p,a,b,r); fd={m:int(c)%p for m,c in F.terms()}
    fk=[{(0,0):1}]
    for k in range(K): fk.append(mul(fk[-1],fd,0))
    gens=[]
    Rbig=[(i,j) for i in range(Abig+1) for j in range(Abig+1)]
    ib={m:n for n,m in enumerate(Rbig)}
    # order columns: outside-R monomials first, then R monomials
    inR=lambda m: m[0]<=A and m[1]<=A
    order=[m for m in Rbig if inR(m)]+[m for m in Rbig if not inR(m)]
    col={m:n for n,m in enumerate(order)}
    rows=[]
    for k in range(K+1):
        for i in range(Abig+1):
            for j in range(Abig+1):
                v=[0]*len(order); ok=True
                for (u,w),c in fk[k].items():
                    if i+u>Abig or j+w>Abig: ok=False;break
                    v[col[(i+u,j+w)]]=c*p**(K-k)
                if ok: rows.append(v)
    # add p^K * monomials not reachable (already covered by k=0 shifts)
    M=pari.matrix(len(order),len(rows),[rows[c][r_] for r_ in range(len(order)) for c in range(len(rows))])
    H=pari.mathnf(M)   # columns HNF; use flag-free
    H=[[int(H[r_,c]) for c in range(H.ncols())] for r_ in range(H.nrows())]
    n_out=len(order)-(A+1)**2
    # lattice intersect Z^R = vectors with zero in first n_out coords. HNF (column-style, lower triangular, pivots by row from top?) 
    return H,n_out,order
def det_from_hnf(H,n_out):
    # PARI mathnf: upper-triangular column HNF; coordinate rows 0..n-1. Vectors with zero first n_out coords = columns whose pivot row >= n_out
    n=len(H); ncol=len(H[0]); d=1
    for c in range(ncol):
        piv=max(r for r in range(n) if H[r][c]!=0)
        pass
    return None
if __name__=="__main__":
    out=[]
    for (p,A,K,Abig) in [(101,4,2,8),(101,4,3,8),(65537,4,2,8)]:
        H,n_out,order=test(p,A,K,Abig,1)
        n=len(H)
        # upper triangular: column c has pivot row c (diagonal), entries below zero. Sublattice with zero in first n_out coords: columns c>=n_out
        diag=[H[c][c] for c in range(n)]
        det_R=1
        for c in range(0,n-n_out): det_R*=diag[c]
        pred=1
        for a in range(A+1):
            for b in range(A+1):
                kap=min(K,min(a,b)//2); pred*=p**(K-kap)
        # also verify triangular structure
        tri=all(H[r][c]==0 for c in range(n) for r in range(c+1,n))
        out.append(dict(p=p,A=A,K=K,det_measured=det_R==pred,tri=tri,log_det=float(sp.log(det_R,p)),log_pred=float(sp.log(pred,p))))
        print(out[-1],flush=True)
    json.dump(out,open("gb_check.json","w"),indent=1)
