# Planted fpylll runs for the S_3 cells: JM-basic bivariate lattice (level t) for f(x1,x2)=S_3(x1,x2,x_R) mod p
# (plain: variables x_i<=B on curves with a=*,b=*; sym: variables u_i<=B for 2-torsion-symmetrised f(u1,u2)).
import sys, json, random, math, time, itertools
import numpy as np
import sympy as sp
from fpylll import IntegerMatrix, LLL
import cypari2
import symm2
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
CELLS={"generic":dict(a=3,b=5,sym=False),"j0":dict(a=0,b=7,sym=False),"j1728":dict(a=7,b=0,sym=False),
       "gen_2t":dict(a=2,b=-3,tau=1,sym=True),"j0_2t":dict(a=0,b=-8,tau=2,sym=True),"j1728_2t":dict(a=7,b=0,tau=0,sym=True)}
def S3poly(a,b,xr,p):
    # coefficients of f(x1,x2)=S_3(x1,x2,xr) mod p as dict (i,j)->c
    c={}
    def add(i,j,v): c[(i,j)]=(c.get((i,j),0)+v)%p
    # (x1-x2)^2 xr^2
    add(2,0,xr*xr);add(1,1,-2*xr*xr);add(0,2,xr*xr)
    # -2 xr ((x1+x2)(x1x2+a)+2b)
    add(2,1,-2*xr);add(1,2,-2*xr);add(1,0,-2*xr*a);add(0,1,-2*xr*a);add(0,0,-4*xr*b)
    # (x1x2-a)^2 -4b(x1+x2)
    add(2,2,1);add(1,1,-2*a);add(0,0,a*a);add(1,0,-4*b);add(0,1,-4*b)
    return c
def jm_basic_rows(f,p,t,X):
    """Rows of the JM-basic lattice, columns=monomials (i,j) in [0,2t]^2, scaled by X^i X^j. f monic at (2,2)."""
    cols=[(i,j) for i in range(2*t+1) for j in range(2*t+1)]
    cidx={m:k for k,m in enumerate(cols)}
    # powers of f
    pw=[{(0,0):1}]
    for k in range(1,t+1):
        prev=pw[-1]; new={}
        for (i,j),c in prev.items():
            for (u,v),d in f.items():
                key=(i+u,j+v); new[key]=(new.get(key,0)+c*d)
        pw.append({k_:v%p**(t) for k_,v in new.items()})  # reduce mod p^t is harmless (we multiply by p^{t-k} later; keep exact below)
    # exact powers (no reduction) for correctness
    pe=[{(0,0):1}]
    for k in range(1,t+1):
        prev=pe[-1]; new={}
        for (i,j),c in prev.items():
            for (u,v),d in f.items():
                key=(i+u,j+v); new[key]=(new.get(key,0)+c*d)
        pe.append(new)
    rows=[]
    for (i,j) in cols:
        k=min(i//2,j//2,t)          # level: largest k with (i,j)>=(2k,2k)
        sh=(i-2*k,j-2*k)
        row=[0]*len(cols)
        for (u,v),c in pe[k].items():
            m=(u+sh[0],v+sh[1]); row[cidx[m]]=c*p**(t-k)
        rows.append(row)
    return cols,rows
def lattice_delta_t(t):
    cols=[(i,j) for i in range(2*t+1) for j in range(2*t+1)]
    sk=sum(min(i//2,j//2,t) for i,j in cols); sa=sum(i+j for i,j in cols)
    return sk/sa
def run_instance(cell,pbits,delta,t,rng,pr_cache={}):
    cfg=CELLS[cell]; a,b=cfg["a"],cfg["b"]
    key=(pbits)
    p=int(sp.nextprime(2**pbits))
    X=max(2,int(p**delta))
    def sqrtmod(n): 
        n%=p
        return int(sp.sqrt_mod(n,p)) if pow(n,(p-1)//2,p)==1 else None
    def add(P,Q_):
        (xp,yp),(xq,yq)=P,Q_
        l=(yq-yp)*pow(xq-xp,-1,p)%p
        xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
    if not cfg["sym"]:
        while True:
            x1=rng.randrange(1,X+1); x2=rng.randrange(1,X+1)
            y1=sqrtmod(x1**3+a*x1+b); y2=sqrtmod(x2**3+a*x2+b)
            if x1!=x2 and y1 is not None and y2 is not None: break
        xr=add((x1,y1),(x2,y2))[0]
        f=S3poly(a,b,xr,p); root=(x1,x2)
    else:
        tau=cfg["tau"]; c=(3*tau*tau+a)%p
        while True:
            u1=rng.randrange(1,X+1); u2=rng.randrange(1,X+1)
            pts=[]
            for u in (u1,u2):
                d=(u*u-4*c)%p; r=sqrtmod(d)
                if r is None: break
                w=(u+r)*pow(2,-1,p)%p      # root of w^2-u w+c
                x=(tau+w)%p; y=sqrtmod(x**3+a*x+b)
                if y is None: break
                pts.append((x,y))
            if len(pts)==2 and pts[0][0]!=pts[1][0]: break
        xr=add(pts[0],pts[1])[0]
        symm2.set_modulus(p)
        f=sym_f_cache(a,b,tau,xr,p)
        root=(u1,u2)
        # verify
        val=0
        for (i,j),cf in f.items(): val=(val+cf*pow(u1,i,p)*pow(u2,j,p))%p
        assert val==0,"planted sym root not a root"
    # monic at (2,2)
    inv=pow(f[(2,2)],-1,p); f={k:(v*inv)%p for k,v in f.items() if v%p}
    assert sum(cf*pow(root[0],i,p)*pow(root[1],j,p) for (i,j),cf in f.items())%p==0
    cols,rows=jm_basic_rows(f,p,t,X)
    n=len(cols)
    M=IntegerMatrix(n,n)
    for r in range(n):
        for k,(i,j) in enumerate(cols): M[r,k]=rows[r][k]*(X**(i+j))
    LLL.reduction(M)
    # recover polynomials
    polys=[]
    for r in range(n):
        h={}
        ok=True
        for k,(i,j) in enumerate(cols):
            v=M[r,k]
            if v%(X**(i+j)): ok=False;break
            if v: h[(i,j)]=v//(X**(i+j))
        if ok: polys.append(h)
    def ev(h): return sum(c*root[0]**i*root[1]**j for (i,j),c in h.items())
    vanish=[ev(h)==0 for h in polys[:8]]
    # real solver: resultant of pairs among first 5 reduced polys
    def pstr(h): return "+".join(f"({c})*x^{i}*y^{j}" for (i,j),c in h.items()) or "0"
    success=False
    for (i,j) in [(0,1),(0,2),(1,2),(0,3),(1,3),(2,3),(0,4),(1,4),(2,4),(3,4)]:
        if j>=len(polys): continue
        try:
            R=pari(f"polresultant({pstr(polys[i])},{pstr(polys[j])},y)")
        except Exception: continue
        if R==0: continue
        if pari(f"subst({R},x,{root[0]})")==0: success=True;break
    return dict(success=bool(success),nvanish=int(sum(vanish)),X=X,dim=n)
_symcache={}
def sym_f_cache(a,b,tau,xr,p):
    # symmetrised f(u1,u2) with target x_R fixed: interpolate mod p for this xr (cheap, 2 variables, degree 2)
    # re-implement with explicit xr (symm2 draws its own xR randomly), so inline a small interpolation here.
    d=2; Q=p
    c=(3*tau*tau+a)%Q
    pari(f"a=Mod({a},{Q});b=Mod({b},{Q});")
    rng=random.Random(11)
    W=[[rng.randrange(2,Q) for _ in range(d+1)] for _ in range(2)]
    U=[[(w+c*pow(w,-1,Q))%Q for w in Wi] for Wi in W]
    def ev(w1,w2):
        x1=(tau+w1)%Q; x2=(tau+w2)%Q; x1p=(tau+c*pow(w1,-1,Q))%Q
        s1=pari(f"S3(Mod({x1},{Q}),Mod({x2},{Q}),Mod({xr},{Q}))"); s2=pari(f"S3(Mod({x1p},{Q}),Mod({x2},{Q}),Mod({xr},{Q}))")
        return int((s1*s2).lift())*pow(pow(w2,d,Q),-1,Q)%Q
    F=np.empty((3,3),dtype=object)
    for i in range(3):
        for j in range(3): F[i,j]=ev(W[0][i],W[1][j])
    for ax in range(2):
        V=pari("matrix(3,3,i,j,Mod(%s[i]^(j-1),%d))"%(str(U[ax]).replace(" ",""),Q)); Vi=V**-1
        Vi=np.array([[int(Vi[i,j].lift()) for j in range(3)] for i in range(3)],dtype=object)
        F=np.moveaxis(np.tensordot(Vi,F,axes=([1],[ax]))%Q,0,ax)
    return {(i,j):int(F[i,j])%Q for i in range(3) for j in range(3) if int(F[i,j])%Q}
pari("S3(x,y,z)=(x-y)^2*z^2-2*((x+y)*(x*y+a)+2*b)*z+(x*y-a)^2-4*b*(x+y);")
if __name__=="__main__":
    pbits=int(sys.argv[1]); t=int(sys.argv[2]); trials=int(sys.argv[3]); cells=sys.argv[4].split(",")
    dt=lattice_delta_t(t)
    fr=[0.8,0.95,1.05,1.15,1.3,1.5]
    rng=random.Random(2026+pbits+t)
    out=[]
    print(f"t={t} dim={(2*t+1)**2} predicted JM-basic delta_t={dt:.4f} (asymptote 1/6)",flush=True)
    for cell in cells:
        for f_ in fr:
            d=dt*f_; ns=0; nv=0; t0=time.time()
            for _ in range(trials):
                r=run_instance(cell,pbits,d,t,rng); ns+=r["success"]; nv+=r["nvanish"]
            out.append(dict(cell=cell,pbits=pbits,t=t,frac=f_,delta=round(d,4),X=r["X"],trials=trials,success=ns,mean_vanishing=nv/trials,secs=round(time.time()-t0,1)))
            print(out[-1],flush=True)
    json.dump(out,open(f"planted_p{pbits}_t{t}.json","w"),indent=1)
