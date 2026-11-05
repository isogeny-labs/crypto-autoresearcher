#!/usr/bin/env python3
"""Small derivation checks for TASK-20261105-9d65dc (RP-BATCH-9f090a).

Not an experiment: no hypothesis is tested, no research status depends on the
output.  Each check illustrates, on toy prime-order curves, a statement that
REVIEW.md proves by hand.  Deterministic (fixed seeds); stdlib + sympy only.

C1  Frobenius is F_p-rational of degree p, [m] has degree m^2, so
    End_{F_p}(E) != Z for every E/F_p (pure arithmetic: p is never a square).
C2  On a prime-order j=0 curve, phi(x,y)=(zeta x, y) acts on E(F_p) as [lam]
    with lam^2+lam+1 = 0 mod N; a label-only simulator needs <= 2*ceil(log2 N)
    group operations (double-and-add), not 0 and not lam (~N) operations.
C3  Incidence SEARCH, subset form (KN-FIND-b7e091 sentence reading): one query
    with factor base {2^i G} returns the binary digits of k.  DLP solved with
    ceil(log2 N)-1 group ops + 1 oracle query.
C4  Incidence SEARCH, fixed arity m (EXP-GGM-001 / KN-FIND-002 reading):
    base-B digit factor base, B ~ N^(1/(m+1)); k recovered with O(m N^(1/(m+1)))
    group ops + oracle queries.  m=1 is BSGS (exponent 1/2), m=2 gives 1/3.
C5  Incidence CHECK (KN-FIND-b7e091 source definition): one subset-sum
    equality per query; Shoup counting adds one linear form per query.
    (Illustrated by counting forms in a simulated transcript.)
C6  Jet oracle, Weierstrass reading: eps-coefficient of P+Q is a non-constant
    function of k for fixed public inputs -> not simulable from labels.
    Invariant-differential reading: t(P+Q) = t(P) + t(Q) exactly -> trivially
    simulable and carries no information.
"""
import math
import random

from sympy import isprime, sqrt_mod


# ---------------------------------------------------------------- curve core
class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def on(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x ** 3 + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            l = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            l = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (l * l - x1 - x2) % p
        return (x3, (l * (x1 - x3) - y1) % p)

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def mul(self, k, P, counter=None):
        R, A = None, P
        k = int(k)
        first = True
        while k:
            if k & 1:
                if R is not None and counter is not None:
                    counter[0] += 1
                R = self.add(R, A)
            k >>= 1
            if k:
                A = self.add(A, A)
                if counter is not None:
                    counter[0] += 1
        return R

    def order(self):
        p, n = self.p, 1
        for x in range(p):
            r = (x ** 3 + self.a * x + self.b) % p
            if r == 0:
                n += 1
            elif pow(r, (p - 1) // 2, p) == 1:
                n += 2
        return n

    def point(self, rng):
        p = self.p
        while True:
            x = rng.randrange(p)
            r = (x ** 3 + self.a * x + self.b) % p
            if r and pow(r, (p - 1) // 2, p) == 1:
                y = sqrt_mod(r, p)
                return (x, int(y))


def prime_order_curve(bits, rng, j0=False):
    while True:
        p = rng.randrange(2 ** (bits - 1), 2 ** bits)
        if not isprime(p) or (j0 and p % 3 != 1):
            continue
        a = 0 if j0 else rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        E = Curve(p, a, b)
        N = E.order()
        if isprime(N) and N != p:
            return E, N


# ---------------------------------------------------------------- C1
def check_c1():
    print("C1 End_{F_p}(E) != Z: deg(pi)=p, deg([m])=m^2; p prime is never a square")
    bad = [p for p in range(3, 200000) if isprime(p) and math.isqrt(p) ** 2 == p]
    print(f"   primes p < 2e5 that are perfect squares: {bad}  (expected [])")
    rng = random.Random(1)
    E, N = prime_order_curve(14, rng)
    G = E.point(rng)
    frob = (pow(G[0], E.p, E.p), pow(G[1], E.p, E.p))
    print(f"   toy E: p={E.p} N={N}; pi(G)==G on E(F_p): {frob == G} "
          "(pi acts as [1] on E(F_p), yet pi != [1] as an isogeny: deg p vs 1)")


# ---------------------------------------------------------------- C2
def check_c2():
    print("C2 endomorphism image oracle on a prime-order j=0 curve")
    rng = random.Random(2)
    E, N = prime_order_curve(16, rng, j0=True)
    p = E.p
    zeta = next(z for z in range(2, p) if pow(z, 3, p) == 1)
    G = E.point(rng)
    phiG = (zeta * G[0] % p, G[1])
    assert E.on(phiG)
    # eigenvalue: roots of l^2+l+1 mod N; pick the one with [l]G == phi(G)
    lams = [l for l in (int(r) for r in sqrt_mod(-3, N, all_roots=True))]
    lams = [((-1 + r) * pow(2, -1, N)) % N for r in lams]
    lam = next(l for l in lams if E.mul(l, G) == phiG)
    ok = True
    for _ in range(50):
        k = rng.randrange(1, N)
        Q = E.mul(k, G)
        ok &= (zeta * Q[0] % p, Q[1]) == E.mul(lam, Q)
    cnt = [0]
    E.mul(lam, G, cnt)
    print(f"   p={p} N={N} lam={lam} lam^2+lam+1 mod N = {(lam*lam+lam+1) % N}")
    print(f"   phi(Q)==[lam]Q for 50 random Q: {ok}")
    print(f"   label-only simulator cost (double-and-add) = {cnt[0]} group ops;"
          f" bound 2*ceil(log2 N) = {2*math.ceil(math.log2(N))};"
          f" literal 'm group operations' with m=lam would be ~{lam}")


# ---------------------------------------------------------------- C3
def search_oracle_subsets(E, F, Q):
    """SEARCH: return every subset I of F (as index tuples) with sum == Q.
    Implemented by brute force; this is the ORACLE, not the adversary."""
    n = len(F)
    out = []
    # incremental Gray-code enumeration
    S, cur = None, 0
    if Q is None:
        out.append(())
    for i in range(1, 2 ** n):
        g = i ^ (i >> 1)
        bit = (g ^ cur).bit_length() - 1
        if g & (1 << bit):
            S = E.add(S, F[bit])
        else:
            S = E.add(S, E.neg(F[bit]))
        cur = g
        if S == Q:
            out.append(tuple(j for j in range(n) if g >> j & 1))
    return out


def check_c3():
    print("C3 incidence SEARCH (subset form) solves DLP in one query")
    rng = random.Random(3)
    E, N = prime_order_curve(14, rng)
    G = E.point(rng)
    n = N.bit_length()
    trials, wins = 5, 0
    for _ in range(trials):
        k = rng.randrange(1, N)
        Q = E.mul(k, G)
        ops = 0
        F = [G]
        for _i in range(1, n):
            F.append(E.add(F[-1], F[-1]))
            ops += 1
        sols = search_oracle_subsets(E, F, Q)
        kk = {sum(2 ** j for j in I) % N for I in sols}
        wins += (kk == {k})
    print(f"   p={E.p} N={N} ({n} bits): recovered k in {wins}/{trials} trials;"
          f" adversary cost = {n-1} group ops + 1 SEARCH query"
          f" (vs sqrt(N) ~ {int(math.isqrt(N))})")


# ---------------------------------------------------------------- C4
def search_oracle_arity(E, Flog, Fpts, R, m, N):
    """SEARCH, fixed arity m, multiset decompositions.  Oracle-side brute
    force over discrete logs (the oracle is unbounded); returns one
    decomposition as an index tuple, or None."""
    # oracle may use anything; we use logs for speed (oracle internals are free)
    import itertools
    target = None
    # compute log of R by table (oracle is all-powerful)
    return_idx = None
    for combo in itertools.combinations_with_replacement(range(len(Flog)), m):
        s = None
        for i in combo:
            s = E.add(s, Fpts[i])
        if s == R:
            return_idx = combo
            break
    return return_idx


def check_c4():
    print("C4 incidence SEARCH, fixed arity m: exponent 1/(m+1) in queries+ops")
    rng = random.Random(4)
    E, N = prime_order_curve(14, rng)
    G = E.point(rng)
    for m in (1, 2):
        B = math.ceil(N ** (1.0 / (m + 1)))
        wins, tot_ops, tot_q = 0, 0, 0
        trials = 3
        for _ in range(trials):
            k = rng.randrange(1, N)
            Q = E.mul(k, G)
            ops = 0
            Flog, Fpts = [], []
            for d in range(m):
                step = E.mul(B ** d, G)
                ops += 2 * (B ** d).bit_length()
                P = None
                for i in range(B):
                    Flog.append(i * B ** d)
                    Fpts.append(P)
                    P = E.add(P, step)
                    ops += 1
            giant = E.mul(B ** m, G)
            ops += 2 * (B ** m).bit_length()
            R, q, found = Q, 0, None
            for j in range(N // B ** m + 2):
                q += 1
                dec = search_oracle_arity(E, Flog, Fpts, R, m, N)
                if dec is not None:
                    found = (sum(Flog[i] for i in dec) + j * B ** m) % N
                    break
                R = E.add(R, E.neg(giant))
                ops += 1
            wins += (found == k)
            tot_ops += ops
            tot_q += q
        print(f"   m={m}: N={N}, B={B}, recovered {wins}/{trials};"
              f" mean group ops {tot_ops/trials:.0f} + mean queries {tot_q/trials:.0f}"
              f" ; N^(1/(m+1)) = {N**(1/(m+1)):.0f}, sqrt(N) = {N**0.5:.0f}")


# ---------------------------------------------------------------- C5
def check_c5():
    print("C5 incidence CHECK: Shoup form count (one new form per query)")
    # Formal model: labels are linear forms a + b*X over Z_N (X = unknown k).
    # A group op adds one form; a CHECK(I) query compares one new form
    # (sum of the I forms) with X and returns a bit, creating no label.
    rng = random.Random(5)
    N = 10007
    forms = [(1, 0), (0, 1)]  # G, Q
    gops = 0
    for _ in range(40):
        i, j = rng.randrange(len(forms)), rng.randrange(len(forms))
        forms.append(((forms[i][0] + forms[j][0]) % N, (forms[i][1] + forms[j][1]) % N))
        gops += 1
    compared = 0
    for _ in range(25):
        I = rng.sample(range(len(forms)), rng.randrange(1, len(forms)))
        compared += 1  # exactly one new form (sum over I) tested against X
    pairs = math.comb(len(forms), 2) + compared
    print(f"   {gops} group ops, 25 CHECK queries (|I| up to {len(forms)-1}):"
          f" distinct-form collision events bounded by {pairs} pairs;"
          f" failure prob <= {pairs}/N; CHECK contributes {compared}, i.e. 1 per"
          " query independent of |I|")


# ---------------------------------------------------------------- C6
def dual_add(E, P, dP, Q, dQ):
    """Add P+eps dP and Q+eps dQ on E over F_p[eps]/eps^2 (P != +-Q).
    Points are (x,y), tangent parts (dx,dy).  Returns (R, dR)."""
    p = E.p
    (x1, y1), (dx1, dy1) = P, dP
    (x2, y2), (dx2, dy2) = Q, dQ
    inv = pow(x2 - x1, -1, p)
    l0 = (y2 - y1) * inv % p
    l1 = ((dy2 - dy1) - l0 * (dx2 - dx1)) * inv % p  # derivative of lambda
    x3 = (l0 * l0 - x1 - x2) % p
    dx3 = (2 * l0 * l1 - dx1 - dx2) % p
    y3 = (l0 * (x1 - x3) - y1) % p
    dy3 = (l1 * (x1 - x3) + l0 * (dx1 - dx3) - dy1) % p
    return (x3, y3), (dx3, dy3)


def tangent(E, P, t):
    """tangent vector at P with invariant coordinate t: omega = dx/(2y)."""
    x, y = P
    p = E.p
    dx = 2 * y * t % p
    dy = (3 * x * x + E.a) * t % p  # from 2y dy = (3x^2+a) dx
    return (dx, dy)


def check_c6():
    print("C6 jet oracle: Weierstrass reading leaks k-dependent field data;"
          " invariant reading is additive")
    rng = random.Random(6)
    E, N = prime_order_curve(14, rng)
    G = E.point(rng)
    p = E.p
    vals, additive, yratio = set(), True, True
    for _ in range(200):
        k = rng.randrange(2, N - 1)
        Q = E.mul(k, G)
        if Q[0] == G[0]:
            continue
        # fixed, label-expressible query: tangent dx=1 at G, zero at Q
        dG = (1, (3 * G[0] ** 2 + E.a) * pow(2 * G[1], -1, p) % p)
        R, dR = dual_add(E, G, dG, Q, (0, 0))
        vals.add(dR[0])
        # post-read addition (C6b): the answer is exactly y(G+Q)/y(G), i.e. a
        # y-coordinate oracle on the instance point G+Q
        yratio &= (dR[0] == R[1] * pow(G[1], -1, p) % p)
        # invariant reading
        tG, tQ = rng.randrange(p), rng.randrange(p)
        R2, dR2 = dual_add(E, G, tangent(E, G, tG), Q, tangent(E, Q, tQ))
        tR = dR2[0] * pow(2 * R2[1], -1, p) % p
        additive &= (tR == (tG + tQ) % p)
    print(f"   p={p} N={N}: eps-coefficient dx(G+Q) took {len(vals)} distinct values"
          " over 200 random k for ONE fixed query -> depends on k -> no label-only"
          " simulator (labels are k-independent in distribution)")
    print(f"   C6b: answer == y(G+Q)/y(G) for all samples (a y-oracle on G+Q): {yratio}")
    print(f"   invariant coordinate t(G+Q) == t(G)+t(Q) for all samples: {additive}")


if __name__ == "__main__":
    check_c1()
    check_c2()
    check_c3()
    check_c4()
    check_c5()
    check_c6()
