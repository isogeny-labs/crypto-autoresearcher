import random, sympy as sp, itertools
from sympy import Poly
from nsys import *
from macaulay import Ring

def padd(a,b,p,s=1):
    r=dict(a)
    for m,c in b.items():
        r[m]=(r.get(m,0)+s*c)%p
        if r[m]==0: del r[m]
    return r
def pmul(a,b,ring):
    p=ring.p; r={}
    for m1,c1 in a.items():
        for m2,c2 in b.items():
            m=ring.mmul(m1,m2); r[m]=(r.get(m,0)+c1*c2)%p
    return {m:c for m,c in r.items() if c}
def esym_poly(xs,k,ring):
    p=ring.p
    tot={}
    for comb in itertools.combinations(range(len(xs)),k):
        t={tuple([0]*ring.n):1}
        for i in comb: t=pmul(t,xs[i],ring)
        tot=padd(tot,t,p)
    return tot

def system(m,p,base,B,rng,null=False):
    """base='digit' (B=2^s) or 'V' (vanishing polys on 1..B).
       returns ring,gens,planted_point(dict var-> value list), meta"""
    # planted instance: x_i distinct in [1,B] (digit: [1,B-1]) on-curve
    hi=B-1 if base=='digit' else B
    a,b,pts,R=planted(m,p,hi,rng,lo=0 if base=='digit' else 1)
    xs0=[P[0] for P in pts]
    xR,yR=R; yQ=(-yR)%p
    al,lead,q,rem=norm_Q(m,a,b,p,xR,yQ)
    # alpha planted
    bf=basis_funcs(m); funcs=list(reversed(bf))
    def hval(i,j,P):
        x,y=P; return (pow(x,i,p)*pow(y,j,p)-pow(xR,i,p)*pow(yQ,j,p))%p
    rows=[[hval(i,j,P) for (i,j) in funcs[1:]] for P in pts]; rhs=[(-hval(*funcs[0],P))%p for P in pts]
    na=m-1
    sol=[int(v) for v in (sp.Matrix(rows[:na]).inv_mod(p)*sp.Matrix(rhs[:na])%p)]
    if base=='digit':
        s=B.bit_length()-1
        nv=na+m*s; bm=[False]*na+[True]*(m*s)
        ring=Ring(nv,bm,p)
        xlin=[]
        for i in range(m):
            d={}
            for j in range(s):
                mono=[0]*nv; mono[na+i*s+j]=1; d[tuple(mono)]=pow(2,j,p)
            xlin.append(d)
        planted_pt=sol+[ (x>>j)&1 for x in xs0 for j in range(s)]
    else:
        nv=na+m; bm=[False]*nv
        ring=Ring(nv,bm,p)
        xlin=[]
        for i in range(m):
            mono=[0]*nv; mono[na+i]=1; xlin.append({tuple(mono):1})
        planted_pt=sol+xs0
    zero=tuple([0]*nv)
    li=pow(int(lead),-1,p)
    gens=[]
    rngn=random.Random(rng.random())
    for k in range(1,m+1):
        ek=esym_poly(xlin,k,ring)
        Qd={}
        if not null:
            Pk=Poly(sp.expand(q[k]),*al)
            for mon,c in Pk.terms():
                Qd[tuple(mon)+tuple([0]*(nv-na))]=(int(c)*li*(-1)**k)%p
        else:
            # curve-free null: random quadratic in alpha (all monomials of degree<=2), constant fixed by planted point
            for mon in itertools.product(range(3),repeat=na):
                if sum(mon)<=2 and sum(mon)>0:
                    Qd[tuple(mon)+tuple([0]*(nv-na))]=rngn.randrange(p)
        gens.append(padd(ek,Qd,p,-1))
    if null:
        # fix constants so that planted point is a root
        for gi,g in enumerate(gens):
            val=evalpoly(g,planted_pt,p)
            g[zero]=(g.get(zero,0)-val)%p
    if base=='V':
        for i in range(m):
            v={tuple([0]*nv):1}
            for t in range(1,B+1):
                lin={tuple([0]*nv):(-t)%p}; mono=[0]*nv; mono[na+i]=1; lin[tuple(mono)]=1
                v=pmul(v,lin,ring)
            gens.append(v)
    # verify planted point is a root
    for g in gens: assert evalpoly(g,planted_pt,p)==0
    return ring,gens,planted_pt,dict(a=a,b=b,xs=xs0,alpha=sol)
def evalpoly(g,pt,p):
    tot=0
    for mon,c in g.items():
        t=c
        for v,e in zip(pt,mon):
            if e: t=t*pow(v,e,p)%p
        tot=(tot+t)%p
    return tot

def semaev_poly(m,a,b,xR,p):
    """S_{m+1}(x1..xm, xR) as sympy poly in x1..xm over Z (reduced mod p later). m=2: S_3; m=3: S_4 via resultant."""
    X=sp.symbols('x1:%d'%(m+1)); T=sp.Symbol('T')
    def S3(u,v,t): return sp.expand((u-v)**2*t**2-2*((u+v)*(u*v+a)+2*b)*t+((u*v-a)**2-4*b*(u+v)))
    if m==2: S=S3(X[0],X[1],xR)
    elif m==3: S=sp.expand(sp.resultant(S3(X[0],X[1],T),S3(X[2],xR,T),T))
    else: raise ValueError
    return X,Poly(S,*X)

def system_S(m,p,B,rng):
    """digit presentation of the single polynomial S_{m+1} on the SAME planted instance (baseline)."""
    a,b,pts,R=planted(m,p,B-1,rng,lo=0)
    xs0=[P[0] for P in pts]; xR=R[0]
    s=B.bit_length()-1; nv=m*s
    ring=Ring(nv,[True]*nv,p)
    xlin=[]
    for i in range(m):
        d={}
        for j in range(s):
            mono=[0]*nv; mono[i*s+j]=1; d[tuple(mono)]=pow(2,j,p)
        xlin.append(d)
    X,P=semaev_poly(m,a,b,xR,p)
    one={tuple([0]*nv):1}
    powc={}
    def xpow(i,e):
        if (i,e) not in powc:
            if e==0: powc[(i,e)]=one
            else: powc[(i,e)]=pmul(xpow(i,e-1),xlin[i],ring)
        return powc[(i,e)]
    tot={}
    for mon,c in P.terms():
        t={tuple([0]*nv):int(c)%p}
        for i,e in enumerate(mon): t=pmul(t,xpow(i,e),ring) if e else t
        tot=padd(tot,t,p)
    pt=[(x>>j)&1 for x in xs0 for j in range(s)]
    assert evalpoly(tot,pt,p)==0
    return ring,[tot],pt,dict(a=a,b=b)

def system_SV(m,p,B,rng):
    """baseline: single polynomial S_{m+1} + vanishing polys on 1..B (variables x_i only)."""
    a,b,pts,R=planted(m,p,B,rng,lo=1)
    xs0=[P[0] for P in pts]; xR=R[0]
    ring=Ring(m,[False]*m,p)
    X,P=semaev_poly(m,a,b,xR,p)
    g={mon:int(c)%p for mon,c in P.terms()}
    gens=[g]
    for i in range(m):
        v={tuple([0]*m):1}
        for t in range(1,B+1):
            lin={tuple([0]*m):(-t)%p}; mono=[0]*m; mono[i]=1; lin[tuple(mono)]=1
            v=pmul(v,lin,ring)
        gens.append(v)
    for gg in gens: assert evalpoly(gg,xs0,p)==0
    return ring,gens,xs0,dict(a=a,b=b)
