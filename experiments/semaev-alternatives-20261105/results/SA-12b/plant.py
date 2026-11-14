"""Planted recovery for a cert.py shift family. usage: plant.py family.json delta trials pbits seed"""
import sys, json, time, random, math
import sympy as sp
from fpylll import IntegerMatrix, LLL
import cert
from cert import Cert, pmul
cert.NCAP=10**6; cert.NROWS=10**6

def mkprime(bits,rng):
    while True:
        p=rng.getrandbits(bits)|(1<<(bits-1))|3
        if p%4==3 and sp.isprime(p): return p
def add(P,Q,p):
    (xp,yp),(xq,yq)=P,Q
    l=(yq-yp)*pow(xq-xp,-1,p)%p; xr=(l*l-xp-xq)%p; return (xr,(l*(xp-xr)-yp)%p)
def sqrt3(v,p):
    r=pow(v,(p+1)//4,p); return r if r*r%p==v%p else None
def planted(p,Bd,rng,a=0,b=7):
    while True:
        x1=rng.randrange(1,Bd+1); x2=rng.randrange(1,Bd+1)
        if x1==x2: continue
        y1=sqrt3((x1**3+a*x1+b)%p,p); y2=sqrt3((x2**3+a*x2+b)%p,p)
        if y1 is None or y2 is None: continue
        xr,_=add((x1,y1),(x2,y2),p); return x1,x2,xr
def trial(shifts,delta,p,rng):
    Bd=int(p**delta)
    x1,x2,xr=planted(p,Bd,rng)
    inst_x1,inst_x2=sp.symbols('x1 x2')
    a,b=0,7
    S=(inst_x1-inst_x2)**2*xr**2-2*((inst_x1+inst_x2)*(inst_x1*inst_x2+a)+2*b)*xr+(inst_x1*inst_x2-a)**2-4*b*(inst_x1+inst_x2)
    f={m:int(c)%p for m,c in sp.Poly(sp.expand(S),inst_x1,inst_x2).terms()}
    t=max(s[0] for s in shifts); C=Cert(dict(p=p,a=a,b=b,xR=xr,f=f),tmax=t)
    M=p**t; rows=[]; supp=set()
    for (i,u,v,h) in shifts:
        base=pmul(C.fp[i],C.H[h],M) if h else dict(C.fp[i])
        row={}; mult=p**(t-i)
        for (uu,vv),c in base.items():
            c=(c*mult)%M
            if c: row[(uu+u,vv+v)]=c; supp.add((uu+u,vv+v))
        rows.append(row)
    supp=sorted(supp); n=len(supp); idx={m:j for j,m in enumerate(supp)}
    sc=[Bd**(u+v) for (u,v) in supp]
    gen=[]
    for row in rows:
        r=[0]*n
        for m,c in row.items(): r[idx[m]]=c*sc[idx[m]]
        gen.append(r)
    for j in range(n):
        r=[0]*n; r[j]=M*sc[j]; gen.append(r)
    A=IntegerMatrix.from_matrix(gen)
    t0=time.time(); LLL.reduction(A); tl=time.time()-t0
    vec=[[int(A[i,j]) for j in range(n)] for i in range(A.nrows)]
    vec=[r for r in vec if any(r)]
    good=[]
    for r in vec[:40]:
        co=[r[j]//sc[j] for j in range(n)]
        val=sum(c*x1**u*x2**v for c,(u,v) in zip(co,supp))
        if val==0: good.append({supp[j]:co[j] for j in range(n) if co[j]})
    ok=0
    q=2147483647
    y=sp.symbols('y'); xs=[random.Random(5).randrange(2,q) for _ in range(2)]
    def ev(g,x0):
        d={}
        for (u,v),c in g.items(): d[v]=(d.get(v,0)+c*pow(x0,u,q))%q
        return sp.Poly(sum(c*y**v for v,c in d.items()),y,modulus=q)
    for i in range(min(len(good),40)):
        for j in range(i+1,min(len(good),40)):
            try:
                P1=ev(good[i],xs[0]); P2=ev(good[j],xs[0])
                if P1.degree()>0 and P2.degree()>0 and int(P1.resultant(P2))%q!=0: ok=1; break
            except Exception as e:
                print('res err',repr(e)[:80]); 
        if ok: break
    return dict(n=n,rows=len(gen),lll_s=round(tl,1),vanishing=len(good),success=ok,B=Bd)
if __name__=="__main__":
    fam=json.load(open(sys.argv[1])); delta=float(sys.argv[2]); trials=int(sys.argv[3]); pbits=int(sys.argv[4]); seed=int(sys.argv[5])
    shifts=[tuple(s) for s in fam['shifts']]
    rng=random.Random(seed); p=mkprime(pbits,rng); res=[]
    for k in range(trials):
        r=trial(shifts,delta,p,rng); res.append(r); print(k,r,flush=True)
    print('SUMMARY',sum(r['success'] for r in res),'/',len(res),'delta',delta,'p',p)
