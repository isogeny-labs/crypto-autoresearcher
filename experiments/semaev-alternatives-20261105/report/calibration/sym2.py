import sympy as sp
x1,x2,X,e1,e2,a,b,t = sp.symbols('x1 x2 X e1 e2 a b t')
S3 = (x1-x2)**2*X**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*X + (x1*x2-a)**2 - 4*b*(x1+x2)
# eliminate properly: x2 = e1 - x1, then reduce modulo x1^2 - e1 x1 + e2
expr = sp.expand(S3.subs(x2, e1-x1))
q, r = sp.div(sp.Poly(expr, x1), sp.Poly(x1**2 - e1*x1 + e2, x1))
r = sp.Poly(r.as_expr(), x1)
print("remainder degree in x1 (must be 0 for a symmetric poly):", r.degree())
sym = sp.Poly(sp.expand(r.coeff_monomial(1)), e1, e2)
print("S3 in (e1,e2): total degree", sym.total_degree(), "monomials", sym.monoms())
print(sp.factor(sym.as_expr()))
