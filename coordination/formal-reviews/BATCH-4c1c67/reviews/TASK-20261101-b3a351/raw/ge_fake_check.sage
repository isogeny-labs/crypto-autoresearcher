# Exhibit fake falls at degree 2 under the ">=" reading (and equality) for the printed placement.
def red(p):
    R = p.parent()
    return sum((c*prod(v^min(e,1) for v,e in zip(R.gens(), m.exponents()[0])) for c,m in zip(p.coefficients(), p.monomials())), R(0))
for name, vars, F, g in [("A","X,Y",["X^2*Y","X*Y+X"],["1","1"]),
                         ("B","X1,X2,X3",["X1*X2+X3","X1*X3+X2"],["1","X1+1"])]:
    R = PolynomialRing(GF(2), vars); F=[R(f) for f in F]; g=[R(x) for x in g]
    prods=[red(gi*fi) for gi,fi in zip(g,F)]; s=red(sum(gi*fi for gi,fi in zip(g,F)))
    print(name, "reduced products", prods, "degs", [p.degree() for p in prods], "| red sum", s, "deg", s.degree())
