# sanity: the closed-form quartic in e1 (for fixed u) vanishes at the planted e1; also discriminant identity
import random
from common import *
import sympy as sp
p=mkp(64); rng=random.Random(1)
for B in (50,1000):
    for _ in range(20):
        x1,x2,R=plant(p,B,rng); xR=R[0]
        for (a_,b_) in ((x1,x2),):
            e1=x1+x2;u=abs(x1-x2)
            c=S3poly_e1_coeffs(p,xR,u)
            v=sum(ci*pow(e1,4-i,p) for i,ci in enumerate(c))%p
            assert v==0,(x1,x2)
print("quartic g_u(e1) vanishes at planted e1: OK (40 instances)")
# symbolic check against sym2.py conic
e1,e2,X,u=sp.symbols('e1 e2 X u')
Q=X**2*(e1**2-4*e2)-2*X*(e1*e2+7*0*e1+14)+e2**2-0*e2+0-28*e1
g=sp.expand(16*Q.subs(e2,(e1**2-u**2)/4))
print(sp.Poly(g,e1).all_coeffs())
# discriminant in w=u^2 : D/4 = 64 (X^3+7)(e1+X)
w=sp.symbols('w'); gw=sp.Poly(sp.expand(g.subs(u,sp.sqrt(w))),w)
a2,a1,a0=gw.all_coeffs(); print(sp.factor(sp.expand(a1**2-4*a2*a0)))
