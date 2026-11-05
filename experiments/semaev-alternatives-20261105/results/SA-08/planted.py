# Planted S_3 decompositions vs Coppersmith/Rees lattice (shift family g_ab = x^(a-2k) y^(b-2k) f^k p^(K-k), k=min(K,floor(min(a,b)/2)), a,b<=2K).
import sys, json, random, time, sympy as sp, cypari2
from fpylll import IntegerMatrix, LLL
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
def curve(pbits,A0,B0):
    p=int(sp.nextprime(2**pbits)); return p
def S3_dict(A0,B0,r):
    # coefficients (integers, not reduced) of S_3(x,y,r) = r^2(x-y)^2 - 2r(xy(x+y)+A0(x+y)+2B0) + (xy)^2 - 2A0 xy + A0^2 - 4B0(x+y)
    d={}
    def add(m,c): d[m]=d.get(m,0)+c
    add((2,0),r*r);add((0,2),r*r);add((1,1),-2*r*r)
    add((2,1),-2*r);add((1,2),-2*r);add((1,0),-2*r*A0);add((0,1),-2*r*A0);add((0,0),-4*r*B0)
    add((2,2),1);add((1,1),-2*A0);add((0,0),A0*A0);add((1,0),-4*B0);add((0,1),-4*B0)
    return d
def pmul(P,Q):
    o={}
    for (i,j),c in P.items():
        for (k,l),e in Q.items(): o[(i+k,j+l)]=o.get((i+k,j+l),0)+c*e
    return o
def build(fd,p,K,B):
    A=2*K; mons=[(u,v) for u in range(A+1) for v in range(A+1)]; ci={m:n for n,m in enumerate(mons)}
    fd={m:c%p for m,c in fd.items()}   # f_red: f_red(x1,x2)=p*t exactly, so f_red^k(x)=p^k t^k; coefficients of f_red^k may be taken mod p^k
    fk=[{(0,0):1}]
    for k in range(1,K+1): fk.append({m:c%p**k for m,c in pmul(fk[-1],fd).items()})
    M=IntegerMatrix(len(mons),len(mons))
    for n,(a,b) in enumerate(mons):
        k=min(K,min(a,b)//2)
        for (u,w),c in fk[k].items():
            m=(a-2*k+u,b-2*k+w); M[n,ci[m]]=c*p**(K-k)*B**(m[0]+m[1])
    return M,mons
def trial(p,A0,B0,B,K,rng):
    while True:
        x1=rng.randrange(1,B+1);x2=rng.randrange(1,B+1)
        if x1==x2: continue
        ys=[]
        ok=True
        for x in (x1,x2):
            rhs=(x**3+A0*x+B0)%p
            if pow(rhs,(p-1)//2,p)!=1: ok=False;break
            ys.append(int(sp.sqrt_mod(rhs,p)))
        if ok: break
    (xp,yp),(xq,yq)=(x1,ys[0]),(x2,ys[1])
    l=(yq-yp)*pow(xq-xp,-1,p)%p; r=(l*l-xp-xq)%p
    fd=S3_dict(A0,B0,r)
    # sanity: f(x1,x2) = 0 mod p
    assert sum(c*pow(x1,i,p)*pow(x2,j,p) for (i,j),c in fd.items())%p==0
    M,mons=build(fd,p,K,B)
    LLL.reduction(M)
    n=len(mons); polys=[]
    for i in range(n):
        h={}
        for j,(u,v) in enumerate(mons):
            if M[i,j]!=0: h[(u,v)]=int(M[i,j])//B**(u+v)
        polys.append(h)
    ev=lambda h:sum(c*x1**i*x2**j for (i,j),c in h.items())
    vanish=[ev(h)==0 for h in polys[:6]]
    def topari(h):
        return pari('+'.join(f"({c})*x^{i}*y^{j}" for (i,j),c in h.items()))
    rec=False
    cand=[i for i in range(min(6,n)) if vanish[i]]
    for ia in range(len(cand)):
        for ib in range(ia+1,len(cand)):
            R=pari.polresultant(topari(polys[cand[ia]]),topari(polys[cand[ib]]),pari('y'))
            if R==0: continue
            rts=pari.nfroots(None,R) if pari.poldegree(R)>0 else []
            if any(int(z)==x1 for z in rts): rec=True;break
        if rec:break
    return dict(first_vanishes=bool(vanish[0]),n_vanish6=sum(vanish),recovered=rec)
if __name__=="__main__":
    bits=int(sys.argv[1]); K=int(sys.argv[2]); trials=int(sys.argv[3]); A0,B0=(0,7)
    deltas=[float(s) for s in sys.argv[4].split(',')]
    p=int(sp.nextprime(2**bits)); out=[]
    for d in deltas:
        B=int(p**d)
        if B<8: continue
        rng=random.Random(1000*bits+K); t0=time.time(); res=[trial(p,A0,B0,B,K,rng) for _ in range(trials)]
        row=dict(bits=bits,K=K,delta=d,B=B,trials=trials,recovered=sum(r['recovered'] for r in res),first_vanishes=sum(r['first_vanishes'] for r in res),sec=round(time.time()-t0,1))
        out.append(row);print(row,flush=True)
        json.dump(out,open(f"planted_{bits}_{K}.json","w"),indent=1)
