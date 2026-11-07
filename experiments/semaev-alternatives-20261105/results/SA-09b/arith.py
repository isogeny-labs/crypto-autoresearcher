# Class-group (arithmetic) description of the Kolyvagin fibre structure.
# Pic(O_m), disc D m^2, as reduced forms in the same order as heegN.gp redforms; projection Pic(O_nl)->Pic(O_n).
import math, itertools
def redforms(Del):
    L=[]; a=1
    while 3*a*a<=-Del:
        for b in range(-a+1,a+1):
            if (b*b-Del)%(4*a)==0:
                c=(b*b-Del)//(4*a)
                if c>=a and not (c==a and b<0) and math.gcd(math.gcd(a,abs(b)),c)==1: L.append((a,b,c))
        a+=1
    return L
def reduce_form(f):
    a,b,c=f
    while True:
        if c<a: a,b,c=c,-b,a; continue
        if not (-a<b<=a):
            k=(a-b)//(2*a); b2=b+2*a*k; c=(b2*b2-(b*b-4*a*c))//(4*a); b=b2
            continue
        if c==a and b<0: b=-b
        return (a,b,c)
def coprime_rep(f,M):
    a,b,c=f
    for s in range(1,200):
        for x in range(-s,s+1):
            for y in range(0,s+1):
                if max(abs(x),y)==s and math.gcd(x,y)==1:
                    v=a*x*x+b*x*y+c*y*y
                    if v>0 and math.gcd(v,M)==1:
                        g,u0,v0=egcd(x,y)  # u0*x+v0*y=1 ; matrix [[x,-v0],[y,u0]] det 1
                        # substitute X=x*X'-v0*Y', Y=y*X'+u0*Y'
                        A=v
                        B=2*a*x*(-v0)+b*(x*u0+(-v0)*y)+2*c*y*u0
                        C=a*v0*v0-b*v0*u0+c*u0*u0
                        return (A,B,C)
    raise RuntimeError('no rep')
def egcd(a,b):
    if b==0: return (abs(a), (1 if a>=0 else -1), 0)
    g,x,y=egcd(b,a%b); return (g,y,x-(a//b)*y)
def project(f,D,n,l):
    """f reduced form of disc D (n l)^2 -> reduced form class of disc D n^2 (a coprime to 2 n l)"""
    A,B,C=coprime_rep(f,2*n*l)
    bp=(B*pow(l,-1,2*A))%(2*A)
    Dn=D*n*n
    assert (bp*bp-Dn)%(4*A)==0,(f,A,bp)
    cp=(bp*bp-Dn)//(4*A)
    return reduce_form((A,bp,cp))
class Tower:
    def __init__(self,D): self.D=D; self.cl={}; self.idx={}
    def classes(self,m):
        if m not in self.cl:
            self.cl[m]=redforms(self.D*m*m); self.idx[m]={f:i for i,f in enumerate(self.cl[m])}
        return self.cl[m]
    def fibres(self,n,l):
        """list over classes of level n (0-based) of lists of 0-based indices at level n*l"""
        m=n*l; Cn=self.classes(n); Cm=self.classes(m); self.idx[n]
        fib=[[] for _ in Cn]
        for g,f in enumerate(Cm):
            pf=project(f,self.D,n,l); fib[self.idx[n][pf]].append(g)
        return fib
