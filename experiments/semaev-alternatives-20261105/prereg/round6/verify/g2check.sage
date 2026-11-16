# Bielliptic genus-2 cover C: y^2 = g(x^2), g = (X - r^2) h(X); E1: Y^2 = g(X); E2: Y^2 = X^3 g(1/X).
# Check (1) #Jac(C)(F_p) = #E1 * #E2 ; (2) odd model via x = r + 1/z ; (3) pullback is a homomorphism.
import time
set_random_seed(23)
for p in [1009, 65537]:
    F = GF(p); R.<X> = F[]
    while True:
        r = F.random_element(); h = X^2 + F.random_element()*X + F.random_element()
        g = (X - r^2)*h
        if r != 0 and g.is_squarefree() and h(r^2) != 0 and g(0) != 0: break
    S.<x> = F[]
    f6 = g(x^2)
    C6 = HyperellipticCurve(f6)
    E1 = EllipticCurve_from_cubic if False else None
    # E1: Y^2 = g(X) (cubic, monic) ; E2: Y^2 = X^3 g(1/X) = reversed cubic
    a = g.list()  # constant term first
    E1 = EllipticCurve(F, [0, a[2], 0, a[1], a[0]])
    rev = R(list(reversed(g.list())))   # c0 X^3 + c1 X^2 + c2 X + 1  (leading = g(0))
    c = rev.leading_coefficient()
    # Y^2 = c X^3 + ... ; scale to monic: X = u/c, Y = v/c^2  -> v^2 = u^3 + rev1 c u^2 + ...
    rr = rev.list()
    E2 = EllipticCurve(F, [0, rr[2], 0, rr[1]*c, rr[0]*c^2])
    # odd model: x = r + 1/z, y = w / z^3
    T.<z> = F[]
    num = (f6((r*z + 1)/z) * z^6).numerator() if False else None
    Fz = sum(f6.list()[i]*(r*z+1)^i * z^(6-i) for i in range(7))
    Fz = T(Fz); assert Fz.degree() == 5, Fz.degree()
    C5 = HyperellipticCurve(Fz)
    t0=time.time(); NJ = C5.frobenius_polynomial()(1); t1=time.time()
    print(p, "#Jac =", NJ, " #E1*#E2 =", E1.order()*E2.order(), "match:", NJ == E1.order()*E2.order(), "(%.1fs)"%(t1-t0))
    # pullback homomorphism in the odd model: P=(X0,Y0) on E1 -> points x=+-sqrt(X0), y=Y0 -> z=1/(x-r), w=y z^3
    J = C5.jacobian(); JF = J(F)
    def pull(P):
        X0, Y0 = P.xy()
        # divisor with x^2 = X0 : in z, x = r + 1/z  =>  (r z + 1)^2 = X0 z^2  => (r^2 - X0) z^2 + 2 r z + 1 = 0
        u = T((r^2 - X0)*z^2 + 2*r*z + 1); u = u / u.leading_coefficient()
        # w = Y0 z^3 on that divisor: reduce mod u to degree < 2
        v = T(Y0*z^3) % u
        return JF([u, v])
    ok = 0; n = 0
    for _ in range(20):
        P = E1.random_point(); Q = E1.random_point()
        if P == 0 or Q == 0 or P+Q == 0 or P == Q: continue
        try:
            lhs = pull(P+Q); rhs = pull(P) + pull(Q)
            n += 1; ok += (lhs == rhs) or (lhs == -rhs)
        except Exception as e:
            print("  skip:", type(e).__name__, e); 
    print("   pullback homomorphism checks:", ok, "/", n)
