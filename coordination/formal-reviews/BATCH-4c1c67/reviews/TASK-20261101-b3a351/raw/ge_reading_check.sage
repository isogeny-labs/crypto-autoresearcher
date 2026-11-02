# J1 side check (reviewer-written): minimal degrees under the literal ">=" reading.
# true  d_F^{>=}(G)  = 1 + min{deg h : 0 != h in <G>}            (M>=2: Koszul syzygy lifts a product to any degree)
# fake  d'_F^{>=}(F) <= 1 + min{deg h : 0 != h in <F>+<S_fe>, h multilinear}, attained when a reduced product reaches >= d
for name, vars, F in [("A", "X,Y", ["X^2*Y", "X*Y+X"]),
                      ("B", "X1,X2,X3", ["X1*X2+X3", "X1*X3+X2"])]:
    R = PolynomialRing(GF(2), vars, order="degrevlex")
    G = [R(f) for f in F]
    fe = [v^2 + v for v in R.gens()]
    I = R.ideal(G); J = R.ideal(G + fe)
    gbI = I.groebner_basis(); gbJ = J.groebner_basis()
    print(name, "GB(<F>)       =", list(gbI), " mindeg =", min(g.degree() for g in gbI))
    print(name, "GB(<F>+S_fe)  =", list(gbJ), " mindeg =", min(g.degree() for g in gbJ))
    print(name, "1 in <F>+S_fe ?", J.is_one())
