"""sanity.py — verify the embedding machinery BEFORE any target sampling.

Checks:
 A. phi_d(O) = e_{d-1} derived as the limit at O in F_p((u)): with u = X/Y
    the local parameter at O = [0:1:0] on the plane model, v = Z/Y solves
    v = u^3 + a u v^2 + b v^3, x = u/v, y = 1/v; the section values at O are
    the constant terms of u^d * (monomials). Expect (0,...,0,1).
 B. Basis independence: evaluation matrix of the d monomials at d random
    points has rank d (the functions are independent mod the curve relation).
 C. Dictionary (correct form, d = m+1): for P_1..P_m (multiplicities allowed,
    with Taylor columns) span(phi_d(P_i scheme)) contains phi_d(-sum P_i):
    exact containment. Also trivial containments phi_d(P_i) in span.
 D. Hook-literal (WRONG) form (d=6, m=3): phi_6(Q) with Q = +sum P_i should
    NOT be contained (only trivial containments). Also m=5 at d=6 works (C).
 E. Taylor columns agree with group-law tangency: multiplicity-2 dictionary
    test with a double point 2P + R = Q vs tangent column.
"""
import random
from ec import EC, phi, derivs, rank_p, MONOMIALS

# ---------------------------------------------------------------- power series
def series_inv(S, K, p):
    assert S[0] % p
    R = [0] * K
    R[0] = pow(S[0], -1, p)
    for n in range(1, K):
        acc = 0
        for i in range(1, n + 1):
            acc = (acc - S[i] * R[n - i]) % p
        R[n] = acc * R[0] % p
    return R


def series_mul(A, B, K, p):
    C = [0] * K
    for i in range(K):
        if A[i]:
            for j in range(K - i):
                if B[j]:
                    C[i + j] = (C[i + j] + A[i] * B[j]) % p
    return C


def limit_at_O(E, d, K=20):
    """constant terms of u^d * s_i for the basis monomials, in F_p((u))."""
    p = E.p
    # solve v = u^3 + a u v^2 + b v^3  mod u^K
    v = [0] * K
    for n in range(3, K):
        # coeff of u^n in RHS
        v2 = series_mul(v, v, K, p)
        v3 = series_mul(v2, v, K, p)
        c = (1 if n == 3 else 0) + E.a * (v2[n - 1] if n >= 1 else 0) + E.b * v3[n]
        v[n] = c % p
    w = v[3:] + [0] * 3          # v = u^3 * w(u); w(0) = 1
    W = series_inv(w, K, p)      # x = u^-2 W, y = u^-3 W (W in u, shifted)
    # represent W as series in u (W(u) = 1/w(u), w(u) = sum w_k u^k)
    Xs = [0] * 2 + W             # x = u^-2 W -> as Laurent stored at index+2
    Ys = [0] * 3 + W
    out = []
    for (i, j) in MONOMIALS[d]:
        # monomial = u^{-2i-3j} * W^{i+j}; u^d * monomial -> ct
        s = [1] + [0] * (K - 1)
        for _ in range(i + j):
            s = series_mul(s, W, K, p)
        pw = 2 * i + 3 * j       # pole order
        e = d - pw               # shift: u^e * W^{i+j}; ct exists iff e == 0
        out.append(s[0] % p if e == 0 else 0)
    return out


def main():
    rng = random.Random(20261120)
    E = EC(1048583, 31415, 27182)  # any toy curve
    ok = True

    # A ------------------------------------------------------------------
    for d in (3, 4, 5, 6):
        lim = limit_at_O(E, d)
        exp = [0] * d
        exp[d - 1] = 1
        print(f"A d={d}: limit of phi_d at O = {lim}  expect {exp}")
        ok &= lim == exp
        assert phi(E, d, None) == exp

    # helper: random point
    def rpoint():
        while True:
            x = rng.randrange(E.p)
            P = E.lift_x(x)
            if P:
                return P

    # B ------------------------------------------------------------------
    for d in (3, 4, 5, 6):
        pts = []
        while len(pts) < d:
            P = rpoint()
            if P not in pts:
                pts.append(P)
        r = rank_p(E.p, [phi(E, d, P) for P in pts])
        print(f"B d={d}: eval-matrix rank at {d} random points = {r} (expect {d})")
        ok &= r == d

    # C ------------------------------------------------------------------
    def cols_with_mult(Ps, d):
        """columns for a multiset: multiplicity k at P -> Taylor cols 0..k-1."""
        from collections import Counter
        cols = []
        for P, k in Counter(Ps).items():
            cols.extend(derivs(E, d, P, k - 1))
        return cols

    for d, m in [(3, 2), (4, 3), (5, 4), (6, 5)]:
        n_pass = n_tot = 0
        n_rep_tot = 0
        for trial in range(40):
            Ps = [rpoint() for _ in range(m)]
            if trial % 4 == 1 and m >= 3:
                Ps[1] = Ps[0]          # force a double point
            if trial % 7 == 3 and m >= 4:
                Ps[2] = Ps[3]          # force another double
            S = None
            for P in Ps:
                S = E.add(S, P)
            cols = cols_with_mult(Ps, d)
            rk = rank_p(E.p, cols)
            # containment of phi(-S)
            c1 = rank_p(E.p, cols, phi(E, d, E.neg(S))) == rk
            # trivial containments
            c2 = all(rank_p(E.p, cols, phi(E, d, P)) == rk for P in Ps)
            n_tot += 1
            n_pass += 1 if (c1 and c2) else 0
            if any(a == b for i, a in enumerate(Ps) for b in Ps[i + 1:]):
                n_rep_tot += 1
            if not (c1 and c2):
                print(f"  C FAIL d={d} m={m} Ps={Ps} c1={c1} c2={c2}")
                ok = False
        print(f"C d={d} m={m}: containment phi(-sum) + trivial: {n_pass}/{n_tot} "
              f"(trials with repeats: {n_rep_tot})")

    # D ------------------------------------------------------------------
    # hook-literal: Q = +sum P_i contained in span at d=6 with m=3? expect NO.
    n_hit = 0
    n_tot = 0
    for _ in range(200):
        Ps = [rpoint() for _ in range(3)]
        S = E.add(E.add(Ps[0], Ps[1]), Ps[2])
        cols = [phi(E, 6, P) for P in Ps]
        rk = rank_p(E.p, cols)
        hit = rank_p(E.p, cols, phi(E, 6, S)) == rk
        n_hit += hit
        n_tot += 1
    print(f"D hook-literal d=6 m=3, Q=+sum: containments {n_hit}/{n_tot} (expect ~0)")

    # sanity: at d=6 the m=5 dictionary must pass exactly (done in C) and the
    # m=3 containment of -sum must FAIL at d=6 too (residual degree 3, no BP)
    n_hit = 0
    for _ in range(200):
        Ps = [rpoint() for _ in range(3)]
        S = E.add(E.add(Ps[0], Ps[1]), Ps[2])
        cols = [phi(E, 6, P) for P in Ps]
        rk = rank_p(E.p, cols)
        n_hit += rank_p(E.p, cols, phi(E, 6, E.neg(S))) == rk
    print(f"D d=6 m=3, Q=-sum: containments {n_hit}/200 (expect 0: dictionary "
          f"needs d=m+1)")

    # E: tangent / osculating column tests, multiplicities summing to m=d-1 -
    n_pass = n_tot = 0
    for _ in range(50):
        P = rpoint()
        # d=3, scheme {P,P}: tangent line contains phi_3(-2P)
        cols = derivs(E, 3, P, 1)
        rk = rank_p(E.p, cols)
        n_pass += rank_p(E.p, cols, phi(E, 3, E.neg(E.add(P, P)))) == rk
        n_tot += 1
        # d=4, scheme {P,P,R}
        R = rpoint()
        cols = derivs(E, 4, P, 1) + [phi(E, 4, R)]
        rk = rank_p(E.p, cols)
        tgt = E.neg(E.add(E.add(P, P), R))
        n_pass += rank_p(E.p, cols, phi(E, 4, tgt)) == rk
        n_tot += 1
        # d=4, scheme {P,P,P}: osculating plane contains phi_4(-3P)
        cols = derivs(E, 4, P, 2)
        rk = rank_p(E.p, cols)
        tgt = E.neg(E.add(E.add(P, P), P))
        n_pass += rank_p(E.p, cols, phi(E, 4, tgt)) == rk
        n_tot += 1
        # d=5, scheme {P,P,P,R}
        cols = derivs(E, 5, P, 2) + [phi(E, 5, R)]
        rk = rank_p(E.p, cols)
        tgt = E.neg(E.add(E.add(E.add(P, P), P), R))
        n_pass += rank_p(E.p, cols, phi(E, 5, tgt)) == rk
        n_tot += 1
    print(f"E tangent/osculating tests: {n_pass}/{n_tot}")
    ok &= n_pass == n_tot

    print("SANITY:", "ALL PASS" if ok else "FAILURES PRESENT")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
