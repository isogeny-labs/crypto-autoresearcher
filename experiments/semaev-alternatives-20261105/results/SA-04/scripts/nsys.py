# Riemann-Roch norm system for y^2=x^3+ax+b over F_p. Verified on planted instances.
import random, sympy as sp
from sympy import symbols, Poly, GF

def inv(a,p): return pow(a%p,-1,p)
def ec_add(P,Q,a,p):
    if P is None: return Q
    if Q is None: return P
    (x1,y1),(x2,y2)=P,Q
    if x1==x2 and (y1+y2)%p==0: return None
    if P==Q: l=(3*x1*x1+a)*inv(2*y1,p)%p
    else: l=(y2-y1)*inv(x2-x1,p)%p
    x3=(l*l-x1-x2)%p
    return (x3,(l*(x1-x3)-y1)%p)
def neg(P,p): return None if P is None else (P[0],(-P[1])%p)
def sqrt_mod(n,p):
    n%=p
    if n==0: return 0
    if pow(n,(p-1)//2,p)!=1: return None
    return int(sp.sqrt_mod(n,p))

def random_curve(p,rng):
    while True:
        a=rng.randrange(1,p); b=rng.randrange(1,p)
        if (4*a**3+27*b*b)%p: return a,b

def basis_funcs(m):
    """pole orders 2..m+1 : returns list of (i,j) meaning x^i * y^j"""
    out=[]
    for k in range(2,m+2):
        out.append((k//2,0) if k%2==0 else ((k-3)//2,1))
    return out

def norm_Q(m,a,b,p,xR,yQ):
    """f=h_{m+1}+sum_{k=2..m} alpha_k h_k, h=g-g(Q). Return (alphas, Qs) with e_k=Q_k(alpha) mod p, k=1..m,
       plus lead sign. Uses exact division of N(f) by (X-xR)."""
    X=symbols('X'); al=symbols('al2:%d'%(m+1)) if m>=2 else ()
    al=list(symbols('a_%d'%k) for k in range(2,m+1))
    F=X**3+a*X+b
    bf=basis_funcs(m)
    def g(i,j,x,y): return x**i*y**j
    # f = A(X)+B(X) y
    A=0;Bc=0
    coefs=[1]+al  # for k=m+1 first then k=m..2 ; map
    funcs=list(reversed(bf))   # h_{m+1}, h_m, ..., h_2
    for c,(i,j) in zip(coefs,funcs):
        const=pow(xR,i,p)*pow(yQ,j,p)%p
        if j==0: A+=c*(X**i-const)
        else:
            # x^i y - const : the y part gives B contribution c*X^i, the constant goes into A
            Bc+=c*X**i; A+=-c*const
    N=sp.expand(A**2-Bc**2*F)
    PN=Poly(N,X)
    lead=PN.coeff_monomial(X**(m+1))
    # reduce coefficients mod p, divide by (X-xR) synthetic
    cs=[Poly(sp.expand(PN.coeff_monomial(X**k)),*al) for k in range(m+1,-1,-1)]
    # synthetic division
    q=[];carry=0
    for c in cs:
        carry=sp.expand(c.as_expr()+carry*xR); q.append(carry)
    rem=q.pop()
    return al,lead,q,rem

def reduce_p(expr,vars_,p):
    P=Poly(expr,*vars_) if vars_ else Poly(expr)
    return Poly({k:int(v)%p for k,v in P.terms()} and dict((k,int(v)%p) for k,v in P.terms()),*vars_) if vars_ else P

def esym(xs,k):
    from itertools import combinations
    s=0
    for c in combinations(xs,k):
        t=1
        for v in c: t*=v
        s+=t
    return s

def planted(m,p,B,rng,lo=1):
    while True:
        a,b=random_curve(p,rng)
        pts=[]
        xs=rng.sample(range(lo,B+1),m)
        ok=True
        for x in xs:
            y=sqrt_mod(x**3+a*x+b,p)
            if y is None: ok=False;break
            pts.append((x,y if rng.random()<.5 else (-y)%p))
        if not ok: continue
        R=None
        for P in pts: R=ec_add(R,P,a,p)
        if R is None: continue
        return a,b,pts,R
