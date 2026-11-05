import random, sys, json, time, math
import sympy
from lab import *
import sympy
from run_ceilings import pres
A_,B_=3,5
def mkprime(bits,rng):
    while True:
        p=rng.getrandbits(bits)|(1<<(bits-1))|3
        if p%4==3 and sympy.isprime(p): return p
def sqrt_mod(v,p):
    r=pow(v,(p+1)//4,p); return r if r*r%p==v%p else None
def add(P,Q,p):
    (xp,yp),(xq,yq)=P,Q
    l=(yq-yp)*pow(xq-xp,-1,p)%p; xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
def instance(p,Bd,rng):
    while True:
        x1=rng.randrange(1,Bd+1); x2=rng.randrange(1,Bd+1)
        if x1==x2: continue
        y1=sqrt_mod((x1**3+A_*x1+B_)%p,p); y2=sqrt_mod((x2**3+A_*x2+B_)%p,p)
        if y1 is None or y2 is None: continue
        xr,yr=add((x1,y1),(x2,y2),p); return x1,x2,xr,yr
def poly_x(xr,p):
    x1,x2=sympy.symbols('x1 x2')
    S=(x1-x2)**2*xr**2-2*((x1+x2)*(x1*x2+A_)+2*B_)*xr+(x1*x2-A_)**2-4*B_*(x1+x2)
    P=sympy.Poly(sympy.expand(S),x1,x2); return {m:int(c)%p for m,c in P.terms()}
def poly_e(xr,p):
    e1,e2=sympy.symbols('e1 e2')
    S=xr**2*(e1**2-4*e2)-2*xr*(e1*e2+A_*e1+2*B_)+e2**2-2*A_*e2+A_**2-4*B_*e1
    P=sympy.Poly(sympy.expand(S),e1,e2); return {m:int(c)%p for m,c in P.terms()}
def monic(poly,lam,p):
    inv=pow(poly[lam],-1,p); return {e:c*inv%p for e,c in poly.items()}
def recover(basis_rows, M, X, root, n=2):
    """after LLL: polys h_i; keep those vanishing at root; check two independent -> recovery"""
    good=[]
    for r in basis_rows:
        h={M[j]:int(r[j])//X_pow(X,M[j]) for j in range(len(M)) if r[j]!=0}
        # exact division check
        ok=all(int(r[j])%X_pow(X,M[j])==0 for j in range(len(M)))
        if not ok: continue
        v=sum(c*math.prod(root[k]**e[k] for k in range(n)) for e,c in h.items())
        if v==0: good.append(h)
        if len(good)>=14: break
    return good
def X_pow(X,e): return math.prod(X[k]**e[k] for k in range(len(e)))
def indep(h1,h2):
    a,b=sympy.symbols('a b')
    P1=sum(c*a**e[0]*b**e[1] for e,c in h1.items()); P2=sum(c*a**e[0]*b**e[1] for e,c in h2.items())
    R=sympy.resultant(P1,P2,b)
    return R!=0
def trial(kind,p,delta,t,M,lev,lams,rng):
    Bd=int(p**delta)
    if Bd<2: return None
    x1,x2,xr,yr=instance(p,Bd,rng)
    if kind=='x': f=poly_x(xr,p); root=(x1,x2); X=(Bd,Bd)
    else: f=poly_e(xr,p); root=(x1+x2,x1*x2); X=(2*Bd,Bd*Bd)
    f=monic(f,lams[0],p)
    rows=build_lattice(2,[f],lams,M,lev,t,p,X)
    Mx=to_matrix(rows,M,X)
    LLL.reduction(Mx)
    R=[[Mx[i,j] for j in range(len(M))] for i in range(len(M))]
    good=recover(R,M,X,root)
    if len(good)<2: return 0
    for j in range(1,len(good)):
        if indep(good[0],good[j]): return 1
    return 0
if __name__=="__main__":
    kind=sys.argv[1]; bits=int(sys.argv[2]); t=int(sys.argv[3]); trials=int(sys.argv[4]); deltas=[float(z) for z in sys.argv[5:]]
    n,sups,cf,om=pres('i' if kind=='x' else 'ii',2)
    lam=[(2,2)] if kind=='x' else [(2,0)]
    gens=[(sups[0],lam[0])]
    rng=random.Random(11)
    p=mkprime(bits,rng)
    out=[]
    for dl in deltas:
        t0=time.time()
        # M depends on delta: use LP at this delta
        import os
        cert=float(os.environ.get('CERT','1'))
        val,M,lev=extract_M_milp(n,gens,cf(min(dl,cert)),t)
        if M is None:
            print('no feasible M at',dl); continue
        res=[]
        for _ in range(trials):
            r=trial(kind,p,dl,t,M,lev,lam,rng)
            if r is not None: res.append(r)
        row=dict(kind=kind,bits=bits,t=t,delta=dl,dim=len(M),lp_val=val,succ=sum(res),trials=len(res),sec=round(time.time()-t0,1))
        print(row,flush=True); out.append(row)
    json.dump(out,open(f'plant_{kind}_{bits}_t{t}.json','w'))
