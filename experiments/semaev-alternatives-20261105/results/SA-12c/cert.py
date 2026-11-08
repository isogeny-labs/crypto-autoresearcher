"""Certified-reach calculator for a shift family on S_3(x1,x2,xR) mod p.
Lattice L = span{ p^(t-i) * m * h * f^i } + p^t Z^support, coordinates scaled by X1^a X2^b with X1=X2=B=p^delta.
det(L_scaled)=p^e * B^D, D = sum over support monomials of (a+b); e = exponent from Smith form over Z/p^t.
Howgrave-Graham: root found when det < p^(t n)  =>  delta* = (t n - e)/D  (poly factors dropped, asymptotic).
"""
import random, sympy as sp
from functools import lru_cache
P_BITS=48
NCAP=90
NROWS=160
def make_instance(seed=1, a=0, b=7, pbits=P_BITS):
    rnd=random.Random(seed)
    p=int(sp.nextprime(rnd.getrandbits(pbits)|(1<<(pbits-1))))
    xR=rnd.randrange(p)
    x1,x2=sp.symbols('x1 x2')
    S=(x1-x2)**2*xR**2-2*((x1+x2)*(x1*x2+a)+2*b)*xR+(x1*x2-a)**2-4*b*(x1+x2)
    f={m:int(c)%p for m,c in sp.Poly(sp.expand(S),x1,x2).terms()}
    return dict(p=p,a=a,b=b,xR=xR,f=f)
def pmul(A,B,mod):
    out={}
    for (a1,b1),c1 in A.items():
        for (a2,b2),c2 in B.items():
            k=(a1+a2,b1+b2); out[k]=(out.get(k,0)+c1*c2)%mod
    return out
class Cert:
    def __init__(s,inst,tmax=7):
        s.p=inst['p']; s.inst=inst; s.tmax=tmax; s.mod=s.p**tmax
        s.fp=[{(0,0):1}]
        for i in range(tmax): s.fp.append(pmul(s.fp[-1],inst['f'],s.mod))
        a,b=inst['a'],inst['b']
        # non-monomial multiplier library (small integer coefficients)
        s.H=[ {(0,0):1},                       # 1
              {(1,0):1,(0,1):-1},              # x1-x2
              {(3,0):1,(1,0):a,(0,0):b},       # f(x1) curve eq
              {(0,3):1,(0,1):a,(0,0):b},       # f(x2)
              {(1,0):1,(0,1):1},               # x1+x2 (e1)
              {(1,1):1},                       # x1x2 (e2)
              {(2,0):1,(1,1):-2,(0,2):1},      # (x1-x2)^2 leading coeff of S3 in X
              {(2,0):1,(1,1):-4,(0,2):1}]      # discriminant-like e1^2-4e2 up to relabel
        s.H[7]={(2,0):1,(1,1):2,(0,2):1}       # e1^2 ; keeps library diverse
        s.cache={}
    def reach(s,shifts):
        """shifts: iterable of (i,a,b,h). returns (delta*, n, D, e, t)."""
        shifts=sorted(set(shifts))
        if not shifts: return (0.0,0,0,0,0)
        t=max(i for i,_,_,_ in shifts)
        if t==0: return (0.0,0,0,0,0)
        p=s.p; M=p**t
        rows=[]; supp=set()
        for (i,a,b,h) in shifts:
            base=pmul(s.fp[i],s.H[h],M) if h else dict(s.fp[i])
            row={}
            mult=p**(t-i)
            for (u,v),c in base.items():
                c=(c*mult)%M
                if c: row[(u+a,v+b)]=c; supp.add((u+a,v+b))
            rows.append(row)
        supp=sorted(supp); n=len(supp)
        if len(rows)>NROWS: return (-1.0,n,0,0,t)
        if n>NCAP: return (-1.0,n,0,0,t)
        idx={m:j for j,m in enumerate(supp)}
        mat=[[0]*n for _ in rows]
        for r,row in enumerate(rows):
            for m,c in row.items(): mat[r][idx[m]]=c
        e=smith_exp(mat,p,t,n)
        D=sum(u+v for u,v in supp)
        d=(t*n-e)/D if D else 0.0
        return (max(d,0.0),n,D,e,t)
def val(x,p,t):
    if x==0: return t
    v=0
    while x%p==0 and v<t: x//=p; v+=1
    return v
def smith_exp(mat,p,t,n):
    M=p**t
    rows=[r[:] for r in mat]; cols=list(range(n)); e=0; npiv=0
    vals=lambda r,c: val(r[c],p,t)
    while rows and cols:
        best=None
        for v in range(t):
            pk=p**(v+1)
            for ri,r in enumerate(rows):
                for c in cols:
                    if r[c]%pk:
                        best=(v,ri,c); break
                if best: break
            if best: break
        if best is None: break
        v,ri,c=best
        prow=rows.pop(ri); e+=v; npiv+=1
        pv=prow[c]//p**v; inv=pow(pv,-1,M)
        nz=[cc for cc in cols if prow[cc]]
        pv_=p**v
        for r in rows:
            if r[c]%M:
                q=(r[c]//pv_)*inv%M
                if q:
                    for cc in nz:
                        r[cc]=(r[cc]-q*prow[cc])%M
        cols.remove(c)
    e+=t*(n-npiv)
    return e
# --- baseline convex families ---
def convex_box(t,Ai,Bi):
    """Jochemsz-May style: for each i<=t multipliers x1^a x2^b with a<=A(i), b<=B(i)."""
    return [(i,a,b,0) for i in range(t+1) for a in range(Ai(i)+1) for b in range(Bi(i)+1)]
if __name__=="__main__":
    import time
    c=Cert(make_instance())
    for t in (1,2,3,4):
        for k in range(0,6):
            sh=[(i,a,b,0) for i in range(t+1) for a in range(k+1) for b in range(k+1)]
            t0=time.time(); r=c.reach(sh); print(t,k,r,round(time.time()-t0,2))
