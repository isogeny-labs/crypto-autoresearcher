# SA-23b Jacobi sums, exact in Z[zeta12] (group-ring vectors reduced mod Phi12 = x^4-x^2+1).
# chi = canonical order-12 character: chi(u)=zeta^m(u), u^((p-1)/12) = r^m, r = phi(zeta12) = i0^3*w0,
#   i0 = -a/b mod p for primary pi=a+bi (a odd,b even,a+b=1 mod 4,b>0); w0 = -a'/b' mod p for primary a'+b'w (a'=2,b'=0 mod 3, b'>0).
# Quartic symbol (u/p)_4 := m(u) mod 4 (i^m), cubic (v/p)_3 := m(v) mod 3 (w^m).
# mode 'g': chi(g)=zeta for smallest primitive root g (pre-freeze convention), for validation only.
import sys, json, math, numpy as np
from sympy import primerange, primitive_root
CAND=[1,2,3,4,6,8,9,12,18,24,27,36]; CAND=CAND+[-c for c in CAND]
PAIRS=[(b,k) for b in (4,8) for k in range(1,12) if (6+b+k)%12!=0]
def red(v):  # v len-12 int list -> len-4 reduced (Phi12 = x^4 - x^2 + 1), exact
    v=[int(x) for x in v]
    for n in range(11,3,-1):
        c=v[n]
        if c: v[n]=0; v[n-2]+=c; v[n-4]-=c
    return tuple(v[:4])
def cmul(a,b):
    r=np.zeros(12,dtype=object)
    for i in range(12):
        if a[i]:
            for j in range(12):
                if b[j]: r[(i+j)%12]+=a[i]*b[j]
    return r
def rot(a,s): return np.roll(a,s%12)
def conj(a): return np.array([a[(-i)%12] for i in range(12)],dtype=object)
def two_sq(p):
    for b in range(2,int(p**.5)+2,2):
        a2=p-b*b
        if a2>0:
            a=int(math.isqrt(a2))
            if a*a==a2 and a%2==1:
                if (a+b)%4!=1: a=-a
                return a,b
def cub(p):
    for c in range(1,int(math.isqrt(4*p//27))+2):
        l2=4*p-27*c*c
        if l2<0: break
        L=math.isqrt(l2)
        if L*L==l2:
            if L%3!=1: L=-L
            if L%3!=1: continue
            a=(L+3*c)//2; return a,3*c,L,c
def tables(p,mode):
    g=int(primitive_root(p)); n=p-1
    pw=np.ones(1,dtype=np.int64); gp=g
    while len(pw)<n:
        k=len(pw); pw=np.concatenate([pw,pw*pow(g,k,p)%p])
    pw=pw[:n]; ind=np.zeros(p,dtype=np.int64); ind[pw]=np.arange(n)
    info={}
    if mode=='g': jinv=1
    else:
        a,b=two_sq(p); i0=(-a*pow(b,-1,p))%p; assert i0*i0%p==p-1
        A,B,L,M=cub(p); w0=(-A*pow(B,-1,p))%p; assert (w0*w0+w0+1)%p==0
        r=pow(i0,3,p)*w0%p; assert pow(r,6,p)==p-1 and pow(r,4,p)!=1
        j=int(ind[r])//(n//12); assert math.gcd(j,12)==1 and int(ind[r])%(n//12)==0
        jinv=pow(j,-1,12); info=dict(a=a,b=b,L=L,M=M)
    m=(ind*jinv)%12
    return m,info
def analyse(p,mode='can'):
    m,info=tables(p,mode)
    u=np.arange(2,p); mu=m[u]; mv=m[(1-u)%p]; m1=int(m[p-1])
    cache={}
    def J2(a,k):
        if (a,k) not in cache:
            cache[(a,k)]=np.bincount((a*mu+k*mv)%12,minlength=12).astype(object)
        return cache[(a,k)]
    ex=[]; abs_ok=0
    for (b,k) in PAIRS:
        V=cmul(J2(6,b),J2((6+b)%12,k)); V=rot(V,(b+k)*m1)  # chi^b(-1)chi^k(-1)
        N=cmul(V,conj(V)); chk=red(N-np.eye(12,dtype=object)[0]*p*p)
        ok=(chk==(0,0,0,0)); abs_ok+=ok; e=None
        for s in range(12):
            if red(V-np.eye(12,dtype=object)[s]*p)==(0,0,0,0): e=s
        ex.append(e)
    info.update(p=p,abs_ok=abs_ok,exps=ex,R=sum(1 for e in ex if e==0),nroot=sum(1 for e in ex if e is not None))
    if mode=='can':
        info['s4']=[int(m[c%p])%4 for c in CAND]; info['s3']=[int(m[c%p])%3 for c in CAND]
    return info
if __name__=="__main__":
    if sys.argv[1]=='validate':
        for p in [13,37,61,73,97,109,157,181,193,229,241,277]:
            r=analyse(p,'g'); print(p,r['R'],r['nroot'],r['abs_ok'],".".join(['.' if e is None else "%x"%e for e in r['exps']]).replace('.','',0))
    else:
        lo,hi=int(sys.argv[2]),int(sys.argv[3]); out=open(sys.argv[4],'a')
        for p in primerange(lo,hi):
            if p%12==1: out.write(json.dumps(analyse(p))+"\n"); out.flush()
