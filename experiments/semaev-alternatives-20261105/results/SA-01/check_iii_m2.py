# Check: for m=2 the norm system's ideal contains alpha - L(e1,e2) (alpha linear in the small unknowns) and its elimination ideal is the Vieta conic.
import sympy as sp
p=1000003; a_,b_=3,5
# find point on curve y^2=x^3+3x+5 mod p
for xr in range(2,200):
    v=(xr**3+a_*xr+b_)%p
    r=sp.sqrt_mod(v,p)
    if r: yr=int(r); break
al,e1,e2=sp.symbols('al e1 e2'); x=sp.symbols('x')
beta=yr-al*xr
N=sp.expand((al*x+beta)**2-(x**3+a_*x+b_))
prod=sp.expand((x-xr)*(x**2-e1*x+e2)*(-1))
D=sp.Poly(sp.expand(N-prod),x)
eqs=[D.coeff_monomial(x**j) for j in range(3)]
G=sp.groebner(eqs,al,e2,e1,modulus=p,order='lex')
for g in G.exprs: print(sp.Poly(g,al,e2,e1,modulus=p).as_expr())
