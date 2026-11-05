import sympy as sp, time
p=1000003; a_,b_=3,5
for xr in range(2,200):
    v=(xr**3+a_*xr+b_)%p
    r=sp.sqrt_mod(v,p)
    if r: yr=int(r); break
a1,a2,e1,e2,e3=sp.symbols('a1 a2 e1 e2 e3'); x=sp.symbols('x')
a0=yr-a1*xr-a2*xr**2
N=sp.expand((a0+a1*x+a2*x**2)**2-(x**3+a_*x+b_))
prod=sp.expand(a2**2*(x-xr)*(x**3-e1*x**2+e2*x-e3))
D=sp.Poly(sp.expand(N-prod),x)
eqs=[D.coeff_monomial(x**j) for j in range(4)]
t0=time.time()
G=sp.groebner(eqs,a1,a2,e3,e2,e1,modulus=p,order='grevlex')
print(len(G.exprs),time.time()-t0)
G2=sp.groebner(eqs,a1,a2,e3,e2,e1,modulus=p,order='lex')
print(time.time()-t0)
for g in G2.exprs:
    P=sp.Poly(g,a1,a2,e3,e2,e1,modulus=p)
    print("lead:",P.monoms()[0],"nterms",len(P.terms()),"deg in a1,a2:",sp.degree(g,a1),sp.degree(g,a2))
