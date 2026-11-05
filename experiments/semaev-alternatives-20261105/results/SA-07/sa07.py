import sys, os, json, random, time, itertools, pickle
from fractions import Fraction
import sympy as sp
from sympy import symbols, Poly, resultant, expand
from sympy.polys.polyfuncs import symmetrize
from fpylll import IntegerMatrix, LLL
from pyscipopt import Model, quicksum

A_, B_ = 0, 7  # y^2 = x^3 + 7
x1,x2,x3,X,T = symbols('x1 x2 x3 X T')
def S3e(u,v,w): return (u-v)**2*w**2 - 2*((u+v)*(u*v+A_)+2*B_)*w + (u*v-A_)**2 - 4*B_*(u+v)

_cache = {}
def sem(m):
    """Return dict with orbit reps->coefficient polys in X, and symmetrized form in e's."""
    if m in _cache: return _cache[m]
    if m == 2:
        S = expand(S3e(x1,x2,X)); xs=[x1,x2]
    else:
        S = expand(resultant(S3e(x1,x2,T), S3e(x3,X,T), T)); xs=[x1,x2,x3]
    P = Poly(S, *xs)
    orb = {}  # sorted-desc exponent tuple -> poly in X (coefficient of representative)
    for mon, c in P.terms():
        if list(mon) == sorted(mon, reverse=True):
            orb[mon] = Poly(c, X)
    sym, rem, defs = symmetrize(S, xs, formal=True)
    assert rem == 0
    es = [d[0] for d in defs]
    PS = Poly(sym, *es, X)
    _cache[m] = dict(orb=orb, esyms=es, symterms=[(mon,int(c)) for mon,c in PS.terms()], xs=xs, S=S)
    return _cache[m]

def orbit_monos(lam):
    return sorted(set(itertools.permutations(lam)))

# ---- elliptic curve
def ec_setup(p): return p
def lift(p, x):
    r = (x**3 + A_*x + B_) % p
    if pow(r, (p-1)//2, p) != 1: return None
    return (x, int(sp.sqrt_mod(r, p)))
def add(p, P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0]==Q[0] and (P[1]+Q[1])%p==0: return None
    if P==Q: l=(3*P[0]*P[0]+A_)*pow(2*P[1],-1,p)%p
    else: l=(Q[1]-P[1])*pow(Q[0]-P[0],-1,p)%p
    xr=(l*l-P[0]-Q[0])%p
    return (xr,(l*(P[0]-xr)-P[1])%p)
def make_p(bits, B, seed):
    p = sp.nextprime(2**bits + 7919*seed)
    while sum(1 for x in range(1,B+1) if lift(p,x)) < 3: p = sp.nextprime(p+1)
    return p
def plant(p, m, B, rng):
    while True:
        pts=[]
        while len(pts)<m:
            q=lift(p, rng.randrange(1,B+1))
            if q: pts.append(q if rng.random()<.5 else (q[0],(-q[1])%p))
        R=None
        for q in pts: R=add(p,R,q)
        if R is None: continue
        xs=sorted([q[0] for q in pts], reverse=True)
        return xs, R[0]

def coeffs(p, m, xR):
    d = sem(m)
    c = {}
    for lam, pol in d['orb'].items():
        v = int(pol.eval(xR)) % p
        if v > p//2: v -= p
        c[lam] = v
    return c

def verify(p, m, xv, xR):
    d=sem(m)
    val = int(d['S'].subs(dict(zip(d['xs'], xv))).subs(X, xR))
    return val % p == 0 and all(x>=1 for x in xv)

def mono_expr(vars_, lam):
    tot=0
    for e in orbit_monos(lam):
        t=1
        for v,k in zip(vars_, e):
            if k: t = t*(v**k)
        tot = tot + t
    return tot

def mono_range(lam, B):
    n=len(orbit_monos(lam))
    return n*1, n*B**sum(lam)

def build_lll(p, c, lams, B):
    n=len(lams); his=[mono_range(l,B)[1] for l in lams]
    j0 = next(j for j in range(n) if c[lams[j]] % p != 0)
    inv = pow(c[lams[j0]], -1, p)
    rows=[]
    for j in range(n):
        if j==j0: continue
        r=[0]*n; r[j]=1; r[j0]=(-c[lams[j]]*inv) % p; rows.append(r)
    r=[0]*n; r[j0]=p; rows.append(r)
    K=1<<30
    s=[max(1,K//h) for h in his]
    M=IntegerMatrix.from_matrix([[r[j]*s[j] for j in range(n)] for r in rows])
    U=IntegerMatrix.identity(n)
    LLL.reduction(M,U)
    Uy=[[U[i,j] for j in range(n)] for i in range(n)]
    basis=[[sum(Uy[i][k]*rows[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    return basis, j0

def solve(p, m, B, form, xR, tl, seed, planted=None):
    d=sem(m); c=coeffs(p,m,xR)
    lams=sorted(c.keys())
    t0=time.time()
    model=Model(); model.hideOutput() if not os.environ.get('SCIPV') else None
    model.setParam('limits/time', tl); model.setParam('timing/clocktype',1); model.setParam('limits/solutions',1)
    model.setParam('randomization/randomseedshift', seed)
    model.setParam('parallel/maxnthreads',1) if False else None
    model.setParam('lp/threads',1)
    model.setParam('display/verblevel',0)
    xv=[model.addVar(f'x{i}',vtype='I',lb=1,ub=B) for i in range(m)]
    for i in range(m-1): model.addCons(xv[i]>=xv[i+1])
    prep=0
    if form=='raw':
        F=quicksum(c[l]*mono_expr(xv,l) for l in lams)
        hi=sum(abs(c[l])*mono_range(l,B)[1] for l in lams)//p+1
        cv=model.addVar('c',vtype='I',lb=-hi,ub=hi)
        model.addCons(F - p*cv == 0)
    elif form=='lll':
        basis,j0=build_lll(p,c,lams,B)
        n=len(lams)
        his=[mono_range(l,B)[1] for l in lams]; los=[mono_range(l,B)[0] for l in lams]
        # exact inverse of basis (rational)
        from sympy.polys.matrices import DomainMatrix
        from sympy import QQ, ZZ
        Bi=DomainMatrix([[ZZ(v) for v in r] for r in basis],(n,n),ZZ).to_field().inv().to_Matrix()
        us=[]
        for k in range(n):
            lo=sum(min(Fraction(int(Bi[j,k].p),int(Bi[j,k].q))*los[j],Fraction(int(Bi[j,k].p),int(Bi[j,k].q))*his[j]) for j in range(n))
            hi=sum(max(Fraction(int(Bi[j,k].p),int(Bi[j,k].q))*los[j],Fraction(int(Bi[j,k].p),int(Bi[j,k].q))*his[j]) for j in range(n))
            import math
            us.append(model.addVar(f'u{k}',vtype='I',lb=math.floor(lo),ub=math.ceil(hi)))
        zs=[]
        for j,l in enumerate(lams):
            z=model.addVar(f'z{j}',vtype='C',lb=los[j],ub=his[j]); zs.append(z)
            model.addCons(z==quicksum(basis[k][j]*us[k] for k in range(n)))
            model.addCons(z==mono_expr(xv,l))
    elif form=='vieta':
        es=d['esyms']
        ev=[model.addVar(f'e{i}',vtype='I',lb=1,ub=sp.binomial(m,i+1)*B**(i+1)) for i in range(m)]
        model.addCons(ev[0]==quicksum(xv))
        if m==2:
            model.addCons(ev[1]==xv[0]*xv[1])
            w=model.addVar('w',vtype='I',lb=0,ub=B)
            model.addCons(ev[0]*ev[0]-4*ev[1]==w*w)
        else:
            model.addCons(ev[1]==xv[0]*xv[1]+xv[0]*xv[2]+xv[1]*xv[2])
            model.addCons(ev[2]==xv[0]*xv[1]*xv[2])
        tot=0; hi=0
        for mon,cf in d['symterms']:
            # mon exponents over es..., X
            cx=cf*(xR%p)**mon[-1]
            cx%=p
            if cx>p//2: cx-=p
            t=cx
            mx=1
            for v,k,i in zip(ev,mon[:-1],range(m)):
                if k: t=t*(v**k); mx*=(sp.binomial(m,i+1)*B**(i+1))**k
            tot=tot+t; hi+=abs(cx)*mx
        cv=model.addVar('c',vtype='I',lb=-int(hi//p+1),ub=int(hi//p+1))
        model.addCons(tot-p*cv==0)
    model.setObjective(0*xv[0])
    prep=time.time()-t0
    t1=time.time()
    model.optimize()
    st=model.getStatus(); el=model.getSolvingTime()
    nodes=model.getNNodes()
    ok=None; sol=None
    if model.getNSols()>0:
        sol=[int(round(model.getVal(v))) for v in xv]
        ok=verify(p,m,sol,xR)
    return dict(status=st,nodes=int(nodes),time=el,prep=prep,verified=ok,sol=sol,planted=planted)

if __name__=='__main__':
    m=int(sys.argv[1]); bits=int(sys.argv[2]); B=int(sys.argv[3]); form=sys.argv[4]; tl=float(sys.argv[5]); seed=int(sys.argv[6])
    p=make_p(bits,B,seed)
    rng=random.Random(1000*seed+bits*7+B)
    xs,xR=plant(p,m,B,rng)
    r=solve(p,m,B,form,xR,tl,seed,xs)
    print(json.dumps(r,default=str))
