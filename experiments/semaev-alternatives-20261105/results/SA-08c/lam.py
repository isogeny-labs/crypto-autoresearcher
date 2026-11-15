# lambda_1, lambda_2 of Rees lattice (S_3, m=2) for planted / random instances; support = box [0,2K]^2 or total-degree simplex.
import sys, json, random, time, math, sympy as sp
sys.path.insert(0,'/home/user/semaev-runs/SA-08')
from planted import S3_dict, pmul
from fpylll import IntegerMatrix, LLL, BKZ, GSO
from fpylll.algorithms.bkz2 import BKZReduction
def support(K,kind):
    A=2*K
    if kind=='box': return [(u,v) for u in range(A+1) for v in range(A+1)]
    if kind=='simplex': return [(u,v) for u in range(A+1) for v in range(A+1) if u+v<=A+K]  # down-closed, cuts the top corner
    raise
def build(fd,p,K,B,mons):
    ci={m:n for n,m in enumerate(mons)}
    fd={m:c%p for m,c in fd.items()}
    fk=[{(0,0):1}]
    for k in range(1,K+1): fk.append({m:c%p**k for m,c in pmul(fk[-1],fd).items()})
    M=IntegerMatrix(len(mons),len(mons)); logdet=0.0
    for n,(a,b) in enumerate(mons):
        k=min(K,min(a,b)//2)
        for (u,w),c in fk[k].items():
            m=(a-2*k+u,b-2*k+w)
            if m in ci: M[n,ci[m]]=c*p**(K-k)*B**(m[0]+m[1])
            else: raise Exception("not closed")
        logdet+=(K-k)*math.log(p)+(a+b)*math.log(B)
    return M,logdet
def norms(M,beta,big=False):
    LLL.reduction(M)
    if beta>2:
        par=BKZ.Param(block_size=beta,max_loops=4,flags=BKZ.MAX_LOOPS)
        BKZ.reduction(M,par,float_type='mpfr',precision=300) if big else BKZ.reduction(M,par)
    return sorted(math.sqrt(sum(int(x)**2 for x in M[i])) for i in range(M.nrows))[:3]
def inst(p,B,K,kind,planted,rng,A0=0,B0=7):
    while True:
        x1=rng.randrange(1,B+1);x2=rng.randrange(1,B+1)
        if x1==x2: continue
        if not planted:
            r=rng.randrange(p); break
        ys=[];ok=True
        for x in (x1,x2):
            rhs=(x**3+A0*x+B0)%p
            if pow(rhs,(p-1)//2,p)!=1: ok=False;break
            ys.append(int(sp.sqrt_mod(rhs,p)))
        if ok:
            l=(ys[1]-ys[0])*pow(x2-x1,-1,p)%p; r=(l*l-x1-x2)%p; break
    return S3_dict(A0,B0,r)
if __name__=="__main__":
    bits=int(sys.argv[1]);K=int(sys.argv[2]);kind=sys.argv[3];ntr=int(sys.argv[4]);beta=int(sys.argv[5])
    deltas=[float(s) for s in sys.argv[6].split(',')]
    out=sys.argv[7]
    p=int(sp.nextprime(2**bits)); mons=support(K,kind); n=len(mons); rows=[]
    for d in deltas:
        B=int(p**d)
        for planted in (True,False):
            for t in range(ntr):
                rng=random.Random(hash((bits,K,kind,d,planted,t))%2**31)
                fd=inst(p,B,K,kind,planted,rng); M,ld=build(fd,p,K,B,mons)
                t0=time.time(); l=norms(M,beta,bits*K>=130)
                hg=K*math.log(p)-0.5*math.log(n)
                gh=0.5*math.log(n/(2*math.pi*math.e))+ld/n
                rows.append(dict(bits=bits,K=K,kind=kind,n=n,delta=d,B=B,planted=planted,t=t,
                  l1=math.log(l[0]),l2=math.log(l[1]),l3=math.log(l[2]),hg=hg,gh=gh,sec=round(time.time()-t0,2)))
        print(bits,K,kind,d,[ (r['planted'],round(r['l1']-r['hg'],2),round(r['l2']-r['hg'],2),round(r['gh']-r['hg'],2)) for r in rows[-2*ntr:]][:2*ntr:ntr],flush=True)
        json.dump(rows,open(out,'w'))
