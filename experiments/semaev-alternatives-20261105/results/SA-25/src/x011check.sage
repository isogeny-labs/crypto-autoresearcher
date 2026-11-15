# X0(11) = 11a1. Find j, j' = j(11 tau) as rational functions on the Weierstrass model from q-expansions,
# then verify Phi_11(j(s), j'(s)) = 0, Atkin-Lehner s + w(s) = const, and Hecke: sum of l+1 neighbours = a_l * s.
E = EllipticCurve(QQ, [0,-1,1,-10,-20]); prec = 120
phi = E.modular_parametrization()
xq, yq = phi.power_series(prec)
L = xq.parent(); q = L.gen()
from sage.modular.modform.j_invariant import j_invariant_qexp
jq = L(j_invariant_qexp(prec).laurent_polynomial() if hasattr(j_invariant_qexp(prec),'laurent_polynomial') else j_invariant_qexp(prec))
jq11 = jq(q^11)
def solve(target, den_x, degP0, degP1, nterms):
    # target * (x - den_x)^m = P0(x) + P1(x) y  -> linear system in coefficients
    lhs = target
    basis = [xq^i for i in range(degP0+1)] + [xq^i*yq for i in range(degP1+1)]
    v = lhs.valuation(); 
    rows = []; rhs = []
    for k in range(min(b.valuation() for b in basis+[lhs]), nterms):
        rows.append([b[k] for b in basis]); rhs.append(lhs[k])
    M = matrix(QQ, rows); bvec = vector(QQ, rhs)
    try:
        sol = M.solve_right(bvec)
    except ValueError:
        return None
    return sol
res = {}
for x0 in (5, 16):
    sj = solve(jq*(xq - x0)^11, x0, 11, 10, 60)
    sjp = solve(jq11*(xq - x0), x0, 6, 5, 60)
    print("x0 =", x0, "j solvable:", sj is not None, " j' solvable:", sjp is not None)
    if sj is not None and sjp is not None: res = (x0, sj, sjp)
x0, sj, sjp = res
print("denominator x -", x0, "; j numerator coeffs height (bits):", max(abs(c.numerator()).nbits() for c in sj))
save((x0, list(sj), list(sjp)), "jmaps_11a1.sobj")
a = {l: E.ap(l) for l in (2,3,5,7,13)}; print("a_l:", a)
for p in [1009, 4001]:
    F = GF(p); Ep = E.change_ring(F)
    def jv(P, s, dP0, dP1, m):
        xx, yy = P.xy()
        num = sum(F(s[i])*xx^i for i in range(dP0+1)) + yy*sum(F(s[dP0+1+i])*xx^i for i in range(dP1+1))
        return num / (xx - x0)^m
    pts = [P for P in Ep.points() if P != 0 and P.xy()[0] != x0]
    J = {P: (jv(P, sj, 11, 10, 11), jv(P, sjp, 6, 5, 1)) for P in pts}
    Phi11 = classical_modular_polynomial(11)
    R2.<A,B> = F[]; Phi11F = R2(Phi11)
    bad = sum(1 for P in pts if Phi11F(J[P][0], J[P][1]) != 0)
    print(p, "#pts", len(pts), " Phi11(j,j') != 0 at", bad, "points")
    key = {}
    for P in pts: key.setdefault(J[P], []).append(P)
    # Atkin-Lehner: w(s) has (j,j') swapped
    consts = set()
    for P in pts:
        Q = key.get((J[P][1], J[P][0]))
        if Q and len(Q) == 1: consts.add(P + Q[0])
    print("   AL: distinct values of s + w(s):", len(consts), list(consts)[:3])
    # Hecke T_2: neighbours j1 of j with Phi2(j,j1)=0 and j1' with Phi2(j',j1')=0, (j1,j1') a point
    for l in (2, 3):
        Phil = R2(classical_modular_polynomial(l)); Y = polygen(F)
        full = ok = 0
        for P in pts:
            j0, j0p = J[P]
            r1 = Phil(j0, Y).roots(multiplicities=False) if False else Phil.subs(A=j0).univariate_polynomial().roots(multiplicities=False)
            if len(r1) != l+1: continue
            r1p = Phil.subs(A=j0p).univariate_polynomial().roots(multiplicities=False)
            nb = []
            for j1 in r1:
                cand = [jp for jp in r1p if (j1, jp) in key]
                if len(cand) == 1 and len(key[(j1, cand[0])]) == 1: nb.append(key[(j1, cand[0])][0])
            if len(nb) != l+1: continue
            full += 1; ok += (sum(nb, Ep(0)) == a[l]*P)
        print("   T_%d: full rational neighbourhoods %d, relation sum = a_l*s holds in %d" % (l, full, ok))
