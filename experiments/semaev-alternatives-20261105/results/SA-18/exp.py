# Constructive determinant-method oracle for C_R: S_3(x1,x2,xR)=0 mod p, box [1,B]^2.
import sys, json, random, time, itertools
import sympy as sp
from fpylll import IntegerMatrix, LLL
import cypari2
pari=cypari2.Pari(); pari.allocatemem(400*10**6)

def mk_curve(bits, kind, rng):
    p=int(sp.nextprime(2**bits))
    if kind=='small': a,b=0,7
    else: a,b=rng.randrange(p),rng.randrange(p)
    return p,a,b
def sqrtm(v,p):
    return int(sp.sqrt_mod(v%p,p)) if pow(v%p,(p-1)//2,p)==1 else None
def add(P,Q,p):
    (xp,yp),(xq,yq)=P,Q
    l=(yq-yp)*pow(xq-xp,-1,p)%p
    xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
def S3poly(a,b,xR,p):
    # F(x,y)=S3(x,y,xR) as dict {(i,j):c} mod p
    e1={(1,0):1,(0,1):1}; 
    F={}
    def addt(i,j,c): F[(i,j)]=(F.get((i,j),0)+c)%p
    X=xR
    # xR^2 (x-y)^2
    addt(2,0,X*X);addt(0,2,X*X);addt(1,1,-2*X*X)
    # -2 xR ( (x+y)(xy+a) + 2b )
    addt(2,1,-2*X);addt(1,2,-2*X);addt(1,0,-2*X*a);addt(0,1,-2*X*a);addt(0,0,-4*X*b)
    # (xy-a)^2 -4b(x+y)
    addt(2,2,1);addt(1,1,-2*a);addt(0,0,a*a);addt(1,0,-4*b);addt(0,1,-4*b)
    return {k:v for k,v in F.items() if v}
def pmul(A,Bp,p):
    R={}
    for (i,j),c in A.items():
        for (k,l),d in Bp.items():
            R[(i+k,j+l)]=(R.get((i+k,j+l),0)+c*d)%p if p else R.get((i+k,j+l),0)+c*d
    return R
def build_lattice(F,p,N,t,B):
    mons=[(i,j) for i in range(N+1) for j in range(N+1)]
    idx={m:n for n,m in enumerate(mons)}
    Fp=[{(0,0):1}]
    for u in range(t): Fp.append(pmul(Fp[-1],F,p**t))
    s=len(mons); M=IntegerMatrix(s,s)
    # order rows by leading monomial; matrix need not be triangular for LLL
    for r,(i,j) in enumerate(mons):
        u=min(t,min(i,j)//2)
        poly=pmul(Fp[u],{(i-2*u,j-2*u):1},None) if True else None
        mult=p**(t-u)
        for (a,b),c in poly.items():
            M[r,idx[(a,b)]]=(c*mult)%(p**t) if False else c*mult
        # scale columns
    for r in range(s):
        for (a,b),n in idx.items():
            M[r,n]=M[r,n]*B**(a+b)
    return M,mons
def solve(polys,B,p,F,xR,a,b):
    """polys: list of dict (integer-vanishing). Return set of verified (x1,x2)."""
    def tostr(G): return "+".join(f"({c})*x^{i}*y^{j}" for (i,j),c in G.items())
    P=[pari(tostr(G)) for G in polys]
    sols=set()
    n=len(P)
    pairs=list(itertools.combinations(range(n),2))[:12]
    for i1,i2 in pairs:
        try:
            R=pari.polresultant(P[i1],P[i2],pari('y'))
        except Exception: continue
        if R==0: continue
        fac=pari.factor(R)
        for f in fac[0]:
            if pari.poldegree(f)==1:
                x1=-pari.polcoef(f,0)/pari.polcoef(f,1)
                if x1.denominator()!=1 if hasattr(x1,'denominator') else False: continue
                x1=int(x1)
                if not (1<=x1<=B): continue
                g=pari.gcd(pari.subst(P[i1],pari('x'),x1),pari.subst(P[i2],pari('x'),x1))
                for fy in pari.factor(g)[0]:
                    if pari.poldegree(fy)==1:
                        y=-pari.polcoef(fy,0)/pari.polcoef(fy,1)
                        try: y=int(y)
                        except: continue
                        if 1<=y<=B: sols.add((x1,y))
    return sols
def group_verify(x1,x2,xR,a,b,p):
    y1=sqrtm(x1**3+a*x1+b,p); y2=sqrtm(x2**3+a*x2+b,p)
    if y1 is None or y2 is None or x1==x2: return False
    for s2 in (y2,(-y2)%p):
        if add((x1,y1),(x2,s2),p)[0]==xR%p: return True
    return False
def trial(p,a,b,B,N,t,rng,plant=True,nullxR=None):
    f=lambda x:(x**3+a*x+b)%p
    if plant:
        for _ in range(100000):
            x1=rng.randrange(1,B+1);x2=rng.randrange(1,B+1)
            if x1!=x2 and sqrtm(f(x1),p) is not None and sqrtm(f(x2),p) is not None: break
        else: return None
        P1=(x1,sqrtm(f(x1),p));P2=(x2,sqrtm(f(x2),p))
        xR=add(P1,P2,p)[0]
    else: xR=nullxR
    F=S3poly(a,b,xR,p)
    if plant:
        assert sum(c*pow(x1,i,p)*pow(x2,j,p) for (i,j),c in F.items())%p==0
    Mx,mons=build_lattice(F,p,N,t,B)
    LLL.reduction(Mx,delta=0.99)
    s=len(mons); lim=p**t
    cert=[]
    for r in range(s):
        row=[Mx[r,c] for c in range(s)]
        l1=sum(abs(v) for v in row)
        if l1<lim:
            G={}
            for c,(i,j) in enumerate(mons):
                if row[c]:
                    assert row[c]%(B**(i+j))==0
                    G[(i,j)]=row[c]//B**(i+j)
            cert.append(G)
    sols=set()
    if len(cert)>=2: sols=solve(cert,B,p,F,xR,a,b)
    ok=False; fp=0
    for (u,v) in sols:
        if group_verify(u,v,xR,a,b,p):
            if plant and {u,v}=={x1,x2}: ok=True
            elif not plant: fp+=1
            elif {u,v}!={x1,x2}: pass  # another valid decomposition (also success)
            if plant and {u,v}!={x1,x2}: ok=True
    return dict(ncert=len(cert),ok=ok,fp=fp,nsol=len(sols))
if __name__=='__main__':
    bits=int(sys.argv[1]); kind=sys.argv[2]; t=int(sys.argv[3]); Ns=[int(v) for v in sys.argv[4].split(',')]
    deltas=[float(v) for v in sys.argv[5].split(',')]; trials=int(sys.argv[6]); tag=sys.argv[7]
    rng=random.Random(1000*bits+t); p,a,b=mk_curve(bits,kind,rng)
    rows=[]
    for N in Ns:
        for d in deltas:
            B=int(p**d)
            if B<8: continue
            t0=time.time(); res=[]
            for _ in range(trials):
                r=trial(p,a,b,B,N,t,rng)
                if r: res.append(r)
            row=dict(bits=bits,curve=kind,t=t,N=N,dim=(N+1)**2,delta=d,B=B,trials=len(res),
                     success=sum(r['ok'] for r in res),mean_ncert=sum(r['ncert'] for r in res)/max(1,len(res)),
                     frac_ge2=sum(r['ncert']>=2 for r in res)/max(1,len(res)),sec=round(time.time()-t0,1))
            print(json.dumps(row),flush=True); rows.append(row)
    json.dump(rows,open(f'raw_{tag}.json','w'),indent=1)
