import sympy as sp, json
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
V=(a1,a2,e3,e2,e1)
G=sp.groebner(eqs,*V,modulus=p,order='lex')
out=[]
for g in G.exprs:
    P=sp.Poly(g,*V,modulus=p)
    sup=[list(m) for m,c in P.terms()]
    print(len(sup),"terms; vars in:",[str(v) for v in V if g.has(v)])
    out.append(sup)
# reorder exps to (a1,a2,e1,e2,e3)
perm=[0,1,4,3,2]
out=[[[m[i] for i in perm] for m in s] for s in out]
json.dump(out,open('gb_iii_m3.json','w'))
