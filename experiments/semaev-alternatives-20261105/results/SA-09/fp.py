import json,sys,random,math
import cypari2
pari=cypari2.Pari(); pari.allocatemem(200*10**6)
from fractions import Fraction

def find_primes(cond,lo,hi,count):
    """primes p in [lo,hi] that split completely in ring class field of conductor cond of Q(sqrt(-23)): 4p = t^2 + 23 cond^2 s^2 with p=x^2+xy+cy^2 principal form; test via Hilbert-class-poly-free criterion:
    p represented by principal form of disc -23 cond^2 (primitive, p prime to conductor)."""
    D=-23*cond*cond; c=(1-D)//4; out=[]
    p=lo
    from sympy import isprime, nextprime
    p=nextprime(lo-1)
    while p<=hi and len(out)<count:
        if math.gcd(p,6*cond*23)==1:
            # 4p = X^2 + |D| y^2 , y>=1
            ok=False
            y=1
            while 23*cond*cond*y*y<=4*p:
                r=4*p-23*cond*cond*y*y
                x=math.isqrt(r)
                if x*x==r and (x-y)%2==0:  # x=2a+y form needs parity: x ≡ y mod 2
                    ok=True;break
                y+=1
            if ok: out.append(p)
        p=nextprime(p)
    return out

class Fp:
    def __init__(self,p,data):
        self.p=p; self.d=data
        s=int(pari(f'lift(sqrt(Mod(-23,{p})))')); self.s=s
        self.cache={}
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
        L=self.d['levels'][str(m)]; G=self.poly(L['G'])
        pts=[]
        for f in L['F']:
            fc=self.cache.setdefault((m,id(f)),self.poly(f))
            X=self.ev(fc,rm); Y=self.ev(G,X); pts.append((X,Y))
        return pts
    def Hval(self,n,m,rm):
        e=self.edge(n,m); return self.ev(self.poly(e['H']),rm)

# EC arithmetic y^2=x^3+1 over F_p, None = infinity
def add(P,Q,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P;x2,y2=Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=3*x1*x1*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def neg(P,p): return None if P is None else (P[0],(-P[1])%p)
def mul(k,P,p):
    if k<0: return mul(-k,neg(P,p),p)
    R=None
    while k:
        if k&1: R=add(R,P,p)
        P=add(P,P,p); k>>=1
    return R

def rank_modq(rows,ncols,q=(1<<61)-1):
    M=[[x%q for x in r] for r in rows]; rk=0; 
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
