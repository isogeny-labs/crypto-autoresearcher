# Planted check of the (a) bound at m=2: level-k Coppersmith lattices for (A) S_3(x1,x2,xR) and (B) the Vieta conic in (e1,e2),
# same shift rule as jm.py. Success proxy: >=2 LLL-reduced polynomials vanish at the planted root over Z.
import random, sys, json, time, sympy as sp
from fpylll import IntegerMatrix, LLL
from jm import *
from nsys import ec_add, sqrt_mod, random_curve
def polymul(f,g):
    r={}
    for m1,c1 in f.items():
        for m2,c2 in g.items():
            m=tuple(a+b for a,b in zip(m1,m2)); r[m]=r.get(m,0)+c1*c2
    return r
def lattice_test(f,p,X,k,a0,supp,root):
    """f dict mono->int (LM coeff already 1 mod p). returns (#vanishing reduced vectors, dim)"""
    LPs={kk:lattice_points(supp,kk) for kk in range(1,k+1)}
    LPs[0]={tuple([0]*len(X))}
    S=sorted(LPs[k]); idx={mu:i for i,mu in enumerate(S)}
    fp=[{tuple([0]*len(X)):1}]
    for u in range(1,k+1):
        fp.append({m:c%(p**k) for m,c in polymul(fp[-1],f).items()})
    n=len(S)
    sc=[]
    for mu in S:
        v=1
        for xx,e in zip(X,mu): v*=xx**e
        sc.append(v)
    M=IntegerMatrix(n,n)
    for i,mu in enumerate(S):
        u=0
        for uu in range(k,0,-1):
            nu=tuple(m-uu*a for m,a in zip(mu,a0))
            if min(nu)>=0 and nu in LPs[k-uu]: u=uu;break
        nu=tuple(m-u*a for m,a in zip(mu,a0))
        g=polymul({nu:1},fp[u]); mod=p**(k-u)
        for mono,c in g.items(): M[i,idx[mono]]=c*mod*sc[idx[mono]]
    LLL.reduction(M)
    van=0
    for i in range(n):
        tot=0
        for j,mu in enumerate(S):
            c=M[i,j]
            if c:
                assert c%sc[j]==0
                t=c//sc[j]
                for r,e in zip(root,mu): t*=r**e
                tot+=t
        if tot==0 and any(M[i,j] for j in range(n)): van+=1
    return van,n
def instance(pbits,B,rng):
    p=int(sp.nextprime(rng.getrandbits(pbits)|(1<<(pbits-1))))
    while True:
        a,b=random_curve(p,rng)
        x1,x2=rng.sample(range(1,B+1),2)
        y1=sqrt_mod(x1**3+a*x1+b,p); y2=sqrt_mod(x2**3+a*x2+b,p)
        if y1 is None or y2 is None: continue
        R=ec_add((x1,y1),(x2,y2),a,p)
        if R is None: continue
        return p,a,b,x1,x2,R[0]
def S3poly(a,b,xR,p):
    x1,x2=sp.symbols('x1 x2')
    S=sp.expand((x1-x2)**2*xR**2-2*((x1+x2)*(x1*x2+a)+2*b)*xR+((x1*x2-a)**2-4*b*(x1+x2)))
    P=sp.Poly(S,x1,x2)
    return {tuple(m):int(c)%p for m,c in P.terms()}
def conic(a,b,xR,p):
    # monomials (e1^i e2^j)
    return {(2,0):xR*xR%p,(0,1):(-4*xR*xR-2*a)%p,(1,1):(-2*xR)%p,(1,0):(-2*xR*a-4*b)%p,(0,0):(-4*xR*b+a*a)%p if False else (-4*xR*b+a*a)%p,(0,2):1}
def normalise(f,lm,p):
    inv=pow(f[lm],-1,p); return {m:c*inv%p for m,c in f.items()}
if __name__=="__main__":
    pbits=int(sys.argv[1]); k=int(sys.argv[2]); trials=int(sys.argv[3]); deltas=[float(x) for x in sys.argv[4].split(',')]
    outf=sys.argv[5]
    rng=random.Random(11)
    for d in deltas:
        B=int(2**(pbits*d))
        res={'S3':0,'conic':0}
        for t in range(trials):
            p,a,b,x1,x2,xR=instance(pbits,B,rng)
            # S3
            f=S3poly(a,b,xR,p)
            supp=[(i,j) for i in range(3) for j in range(3)]
            # check planted root
            assert sum(c*pow(x1,m[0],p)*pow(x2,m[1],p) for m,c in f.items())%p==0
            f=normalise(f,(2,2),p)
            van,n1=lattice_test(f,p,(B,B),k,(2,2),supp,(x1,x2))
            res['S3']+= van>=2
            # conic
            q=conic(a,b,xR,p)
            e1,e2=x1+x2,x1*x2
            assert sum(c*pow(e1,m[0],p)*pow(e2,m[1],p) for m,c in q.items())%p==0, "conic mismatch"
            supp2=[(2,0),(1,1),(1,0),(0,2),(0,1),(0,0)]
            van2,n2=lattice_test(q,p,(2*B,B*B),k,(0,2),supp2,(e1,e2))
            res['conic']+= van2>=2
        row=dict(pbits=pbits,k=k,delta=d,B=B,trials=trials,S3=res['S3'],conic=res['conic'],dimS3=n1,dimConic=n2)
        print(json.dumps(row),flush=True); open(outf,'a').write(json.dumps(row)+"\n")
