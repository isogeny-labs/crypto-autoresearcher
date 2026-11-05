# Verify: the e-only element of the lex Groebner basis of the m=3 norm system is the Vieta S_4 (vanishes on genuine 3-decompositions of R).
import sympy as sp, random
p=1000003; a_,b_=3,5
for xr in range(2,200):
    v=(xr**3+a_*xr+b_)%p; r=sp.sqrt_mod(v,p)
    if r: yr=int(r); break
a1,a2,e1,e2,e3=sp.symbols('a1 a2 e1 e2 e3'); x=sp.symbols('x')
a0=yr-a1*xr-a2*xr**2
N=sp.expand((a0+a1*x+a2*x**2)**2-(x**3+a_*x+b_))
prod=sp.expand(a2**2*(x-xr)*(x**3-e1*x**2+e2*x-e3))
D=sp.Poly(sp.expand(N-prod),x)
eqs=[D.coeff_monomial(x**j) for j in range(4)]
G=sp.groebner(eqs,a1,a2,e3,e2,e1,modulus=p,order='lex')
E=[g for g in G.exprs if not (g.has(a1) or g.has(a2))]
print("e-only elements:",len(E), "terms",len(sp.Poly(E[0],e3,e2,e1).terms()))
def add(P,Q):
    if P is None: return Q
    if Q is None: return P
    (x1,y1),(x2,y2)=P,Q
    if x1==x2:
        if (y1+y2)%p==0: return None
        l=(3*x1*x1+a_)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def rpt():
    while True:
        u=random.randrange(p); w=(u**3+a_*u+b_)%p; s=sp.sqrt_mod(w,p)
        if s is not None: return (u,int(s))
random.seed(7); ok=0; tot=0; okn=0
for _ in range(20):
    P1,P2=rpt(),rpt(); S=add(P1,P2)
    if S is None: continue
    P3=add((xr,yr),(S[0],(-S[1])%p))
    if P3 is None: continue
    X=[P1[0],P2[0],P3[0]]; E1=sum(X)%p; E2=(X[0]*X[1]+X[0]*X[2]+X[1]*X[2])%p; E3=X[0]*X[1]*X[2]%p
    val=sp.Poly(E[0],e3,e2,e1).eval({e3:E3,e2:E2,e1:E1})%p; tot+=1; ok+=(val==0)
    # negative control: random e's
    val2=sp.Poly(E[0],e3,e2,e1).eval({e3:random.randrange(p),e2:E2,e1:E1})%p; okn+=(val2==0)
print("vanishes on genuine decompositions: %d/%d ; on random-e3 control: %d/%d"%(ok,tot,okn,tot))
