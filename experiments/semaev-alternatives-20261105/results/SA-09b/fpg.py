import json,sys,random,math
import cypari2
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
from sympy import nextprime

def find_primes(Dk,cond,lo,hi,count,bad=()):
    """primes p with 4p = X^2 + |D| cond^2 Y^2, X=Y mod 2 (split completely in ring class field of conductor cond; D odd)"""
    out=[]; p=nextprime(lo-1); A=-Dk*cond*cond
    while p<=hi and len(out)<count:
        if math.gcd(p,2*cond*(-Dk)*math.prod(bad or [1]))==1:
            y=1
            while A*y*y<=4*p:
                r=4*p-A*y*y; x=math.isqrt(r)
                if x*x==r and (x-y)%2==0: out.append(p);break
                y+=1
        p=nextprime(p)
    return out

class Fp:
    def __init__(self,p,data):
        self.p=p; self.d=data; Dk=data['D']
        self.s=int(pari(f'lift(sqrt(Mod({Dk},{p})))')); self.cache={}
    def K(self,q):
        un,ud,vn,vd=[int(z) for z in q]; p=self.p
        if ud%p==0 or vd%p==0: raise ZeroDivisionError('p | denominator')
        return (un*pow(ud,-1,p)+vn*pow(vd,-1,p)*self.s)%p
    def poly(self,lst): return [self.K(q) for q in lst]
    def ev(self,c,x):
        r=0
        for a in reversed(c): r=(r*x+a)%self.p
        return r
    def roots(self,m):
        Pc=self.poly(self.d['levels'][str(m)]['P'])
        r=pari(f'polrootsmod(Pol(Vecrev({Pc})),{self.p})')
        return [int(z) for z in r], Pc
    def edge(self,n,m):
        for e in self.d['edges']:
            if e['n']==n and e['m']==m: return e
    def points(self,m,rm):
        L=self.d['levels'][str(m)]; G=self.poly(L['G']); pts=[]
        for k,f in enumerate(L['F']):
            fc=self.cache.setdefault((m,k),self.poly(f))
            X=self.ev(fc,rm); Y=self.ev(G,X); pts.append((X,Y))
        return pts
    def Hval(self,n,m,rm):
        e=self.edge(n,m); key=('H',n,m)
        if key not in self.cache: self.cache[key]=self.poly(e['H'])
        return self.ev(self.cache[key],rm)

# curve 37a1: y^2+y=x^3-x ; model v^2=u^3+A u+B with u=4x, v=8y+4  (A=-16,B=16)
CA=-16
def to_short(P,p): return (4*P[0]%p,(8*P[1]+4)%p)
def add(P,Q,p,a=CA):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=(3*x1*x1+a)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def neg(P,p): return None if P is None else (P[0],(-P[1])%p)
def mul(k,P,p,a=CA):
    if k<0: return mul(-k,neg(P,p),p,a)
    R=None
    while k:
        if k&1: R=add(R,P,p,a)
        P=add(P,P,p,a); k>>=1
    return R

def rank_modq(rows,ncols,q=(1<<61)-1):
    M=[[x%q for x in r] for r in rows]; rk=0
    for c in range(ncols):
        piv=None
        for i in range(rk,len(M)):
            if M[i][c]: piv=i;break
        if piv is None: continue
        M[rk],M[piv]=M[piv],M[rk]; inv=pow(M[rk][c],-1,q)
        M[rk]=[x*inv%q for x in M[rk]]
        for i in range(len(M)):
            if i!=rk and M[i][c]:
                f=M[i][c]; M[i]=[(a-f*b)%q for a,b in zip(M[i],M[rk])]
        rk+=1
    return rk
