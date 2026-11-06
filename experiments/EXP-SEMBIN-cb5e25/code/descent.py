"""Field F_{2^n}, binary curve, planted decompositions and the Weil descent of
the chained S_3 system EQS4(m, R) to a multilinear F_2 system.

Representation conventions (formats.md restates all of them):
  * field element = int, bit i = coefficient of t^i (polynomial basis);
  * a Boolean monomial = int mask, bit i = variable i; mask 0 is the constant 1;
  * a multilinear polynomial = sorted list of distinct masks (F_2 sum);
  * variable layout (DC-7): bits of X_1 (k of them), ..., bits of X_m, then bits
    of U_1 (n of them), ..., U_{m-2}; X_i = v_i + sum_b x_{i,b} t^b.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from itertools import combinations

import numpy as np

from rng import HashRng


# --------------------------------------------------------------------------
# F_2[t] helpers and the field polynomial
# --------------------------------------------------------------------------
def _pmod(a: int, f: int) -> int:
    df = f.bit_length() - 1
    while a.bit_length() - 1 >= df and a:
        a ^= f << (a.bit_length() - 1 - df)
    return a


def _pmulmod(a: int, b: int, f: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a.bit_length() > f.bit_length() - 1 and (a >> (f.bit_length() - 1)) & 1:
            a ^= f
    return r


def _pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, _pmod(a, b)
    return a


def is_irreducible(f: int) -> bool:
    """Rabin test over F_2."""
    n = f.bit_length() - 1
    if n < 1:
        return False
    x = 2
    # x^(2^n) == x mod f
    def frob(a, times):
        for _ in range(times):
            a = _pmulmod(a, a, f)
        return a
    if frob(x, n) != _pmod(x, f):
        return False
    primes = [q for q in range(2, n + 1) if n % q == 0 and all(q % p for p in range(2, q))]
    for q in primes:
        g = frob(x, n // q) ^ x
        if _pgcd(f, _pmod(g, f)) != 1:
            return False
    return True


@lru_cache(maxsize=None)
def field_poly(n: int) -> int:
    """Lowest-weight irreducible of degree n, lexicographically (= numerically)
    smallest among those of that weight. Includes the t^n bit."""
    if n < 2:
        raise ValueError("n >= 2")
    for weight in (3, 5, 7, 9):
        cands = []
        mid = weight - 2  # middle terms between t^n and 1
        for exps in combinations(range(n - 1, 0, -1), mid):
            f = (1 << n) | 1
            for e in exps:
                f |= 1 << e
            cands.append(f)
        for f in sorted(cands):
            if is_irreducible(f):
                return f
    raise RuntimeError("no low-weight irreducible found")


def poly_terms(f: int) -> list:
    return [i for i in range(f.bit_length()) if (f >> i) & 1]


class Field:
    """F_{2^n} = F_2[t]/(p_n)."""

    def __init__(self, n: int):
        self.n = n
        self.poly = field_poly(n)
        self.mask = (1 << n) - 1
        # trace mask: Tr(a) = parity(a & tmask)
        self.tmask = 0
        for i in range(n):
            if self._trace_slow(1 << i):
                self.tmask |= 1 << i
        # solver of z^2 + z = c
        self._qbasis = []  # (value, combo)
        for i in range(n):
            val = self.sqr(1 << i) ^ (1 << i)
            combo = 1 << i
            for bv, bc in self._qbasis:
                if val ^ bv < val:
                    val ^= bv
                    combo ^= bc
            if val:
                self._qbasis.append((val, combo))
                self._qbasis.sort(reverse=True)

    def mul(self, a: int, b: int) -> int:
        n, poly, r = self.n, self.poly, 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if (a >> n) & 1:
                a ^= poly
        return r

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r, b = 1, a
        while e:
            if e & 1:
                r = self.mul(r, b)
            b = self.mul(b, b)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, (1 << self.n) - 2)

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def _trace_slow(self, a: int) -> int:
        s, x = 0, a
        for _ in range(self.n):
            s ^= x
            x = self.sqr(x)
        assert s in (0, 1)
        return s

    def trace(self, a: int) -> int:
        return bin(a & self.tmask).count("1") & 1

    def solve_quad(self, c: int):
        """A root z of z^2 + z = c, or None. The other root is z ^ 1."""
        val, combo = c, 0
        for bv, bc in self._qbasis:
            if val ^ bv < val:
                val ^= bv
                combo ^= bc
        if val:
            return None
        z = combo
        assert self.sqr(z) ^ z == c
        return z

    def roots_quadratic(self, a2: int, a1: int, a0: int) -> list:
        """Sorted distinct roots in F of a2 U^2 + a1 U + a0."""
        mul = self.mul
        if a2 == 0:
            if a1 == 0:
                if a0 == 0:
                    raise ValueError("identically zero polynomial")
                return []
            return [mul(a0, self.inv(a1))]
        if a1 == 0:
            return [self.sqrt(mul(a0, self.inv(a2)))]
        s = mul(a1, self.inv(a2))                      # U = s z
        c = mul(mul(a0, a2), self.inv(mul(a1, a1)))     # z^2 + z = a0 a2 / a1^2
        z = self.solve_quad(c)
        if z is None:
            return []
        return sorted({mul(s, z), mul(s, z ^ 1)})

    def S3(self, x1: int, x2: int, x3: int, B: int) -> int:
        mul = self.mul
        t = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
        return self.sqr(t) ^ mul(mul(x1, x2), x3) ^ B

    def roots_S3(self, a: int, b: int, B: int) -> list:
        """All W with S3(a, b, W) = 0:  (a+b)^2 W^2 + ab W + (ab)^2 + B."""
        ab = self.mul(a, b)
        return self.roots_quadratic(self.sqr(a ^ b), ab, self.sqr(ab) ^ B)


# --------------------------------------------------------------------------
# curve y^2 + x y = x^3 + A x^2 + B
# --------------------------------------------------------------------------
class Curve:
    def __init__(self, F: Field, A: int, B: int):
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        F, (x, y) = self.F, P
        lhs = F.sqr(y) ^ F.mul(x, y)
        rhs = F.mul(F.sqr(x), x) ^ F.mul(self.A, F.sqr(x)) ^ self.B
        return lhs == rhs

    def neg(self, P):
        return None if P is None else (P[0], P[1] ^ P[0])

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == y1 ^ x1:
                return None            # Q = -P
            # doubling (P == Q, x1 != 0 here, since x1 = 0 forces y2 = y1 = -y1)
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sqr(lam) ^ lam ^ self.A
            y3 = F.sqr(x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sqr(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def y_roots(self, x: int):
        """The y with (x, y) on the curve, [] if the trace condition fails."""
        F = self.F
        if x == 0:
            return [F.sqrt(self.B)]
        c = x ^ self.A ^ F.mul(self.B, F.sqr(F.inv(x)))
        z = F.solve_quad(c)
        if z is None:
            return []
        y1, y2 = F.mul(x, z), F.mul(x, z ^ 1)
        return sorted({y1, y2})

    def count_points(self, fast: bool = None) -> int:
        """#E(F_{2^n}) by exact enumeration of x (1 point at infinity, 1 point
        at x = 0, 2 points per x != 0 with Tr(x + A + B/x^2) = 0). Uses
        log/exp tables (numpy) for n >= 10 and plain field arithmetic below;
        the two paths agree (tested)."""
        F = self.F
        if fast is None:
            fast = F.n >= 10
        if not fast:
            total = 2
            for x in range(1, 1 << F.n):
                c = x ^ self.A ^ F.mul(self.B, F.sqr(F.inv(x)))
                if F.trace(c) == 0:
                    total += 2
            return total
        n, q1 = F.n, (1 << F.n) - 1
        g = _generator(F)
        exp = np.zeros(q1, dtype=np.int64)
        log = np.zeros(1 << n, dtype=np.int64)
        x = 1
        for i in range(q1):
            exp[i] = x
            log[x] = i
            x = F.mul(x, g)
        xs = np.arange(1, 1 << n, dtype=np.int64)
        lb = int(log[self.B])
        t = exp[(lb - 2 * log[xs]) % q1]
        c = xs ^ self.A ^ t
        tm = np.int64(F.tmask)
        v = c & tm
        par = np.zeros_like(v)
        while np.any(v):
            par ^= v & 1
            v >>= 1
        return 2 + 2 * int(np.sum(par == 0))


def _generator(F: Field) -> int:
    q1 = (1 << F.n) - 1
    primes, m_, p = [], q1, 2
    while p * p <= m_:
        if m_ % p == 0:
            primes.append(p)
            while m_ % p == 0:
                m_ //= p
        p += 1
    if m_ > 1:
        primes.append(m_)
    for g in range(2, 1 << F.n):
        if all(F.pow(g, q1 // p) != 1 for p in primes):
            return g
    raise RuntimeError("no generator")


# --------------------------------------------------------------------------
# instance sampling
# --------------------------------------------------------------------------
def draw_curve(F: Field, rng: HashRng):
    """SHARED substream: A uniform in {0,1}, B uniform in F minus {0,1}."""
    A = rng.randbelow(2)
    B = 2 + rng.randbelow((1 << F.n) - 2)
    return A, B


def draw_shifts(F: Field, m: int, k: int, rng: HashRng):
    """v_1..v_m uniform among integers in [2^k, 2^n - 1] (degree in [k, n-1]),
    redrawing while V+v_i equals an earlier coset. Returns (v list, redraws)."""
    n = F.n
    v, redraws = [], 0
    while len(v) < m:
        cand = (1 << k) + rng.randbelow((1 << n) - (1 << k))
        if any(((cand ^ w) >> k) == 0 for w in v):
            redraws += 1
            continue
        v.append(cand)
    return v, redraws


def coset_has_point(curve: Curve, v_i: int, k: int) -> bool:
    return any(curve.y_roots(v_i ^ w) for w in range(1 << k))


def draw_shared(F: Field, m: int, k: int, rng: HashRng, max_tries: int = 10000):
    """SHARED substream: (A, B, v list). The (curve, shifts) draw is repeated
    (deterministically, counted) while some coset V + v_i contains no
    x-coordinate of an F_{2^n}-point, because no planted decomposition exists
    then (specification gap, see report). Returns (A, B, v, info)."""
    redraws = 0
    shift_redraws = 0
    for _ in range(max_tries):
        A, B = draw_curve(F, rng)
        v, sr = draw_shifts(F, m, k, rng)
        shift_redraws += sr
        curve = Curve(F, A, B)
        if all(coset_has_point(curve, vi, k) for vi in v) and valid_decomposition_exists(curve, v, k):
            return A, B, v, {"infeasible_redraws": redraws, "coset_collision_redraws": shift_redraws}
        redraws += 1
    raise RuntimeError("no feasible (curve, shifts)")


class PlantInfeasible(RuntimeError):
    pass


def valid_decomposition_exists(curve: Curve, v: list, k: int, cap: int = 20000) -> bool:
    """Exhaustive for small factor bases (product of coset point counts <= cap),
    otherwise assumed True. Valid: no partial sum is O, R != O, x(R) != 0."""
    pts = []
    for vi in v:
        P = [(x, y) for w in range(1 << k) for x in [vi ^ w] for y in curve.y_roots(x)]
        pts.append(P)
    total = 1
    for P in pts:
        total *= len(P)
    if total > cap:
        return True
    def rec(i, S):
        if i == len(pts):
            return S is not None and S[0] != 0
        for P in pts[i]:
            T = curve.add(S, P)
            if T is None:
                continue
            if rec(i + 1, T):
                return True
        return False
    return rec(0, None)


def plant(F: Field, curve: Curve, v: list, k: int, rng: HashRng, max_tries: int = 20000):
    """Planted decomposition (instance_specification.planted_decomposition).

    Returns dict(P, R, x_R, U, s, redraws=dict(...)). Whole decomposition is
    redrawn when a partial sum is O, R = O or x(R) = 0; per-point rejections of
    the trace condition are counted separately.
    """
    m = len(v)
    red = {"trace_rejections": 0, "partial_sum_O": 0, "R_is_O": 0, "xR_zero": 0}
    for _ in range(max_tries):
        P = []
        for i in range(m):
            while True:
                x = v[i] ^ rng.randbelow(1 << k)
                ys = curve.y_roots(x)
                if ys:
                    break
                red["trace_rejections"] += 1
            y = ys[rng.randbelow(len(ys))]
            P.append((x, y))
        partial, S, ok = [], None, True
        for j in range(m):
            S = curve.add(S, P[j])
            if S is None:
                ok = False
                red["R_is_O" if j == m - 1 else "partial_sum_O"] += 1
                break
            partial.append(S)
        if not ok:
            continue
        R = partial[-1]
        if R[0] == 0:
            red["xR_zero"] += 1
            continue
        U = [partial[j][0] for j in range(1, m - 1)]   # U_j = x(P_1 + ... + P_{j+1}), j = 1..m-2
        s = pack_solution(F.n, k, v, [p[0] for p in P], U)
        return {"P": P, "R": R, "x_R": R[0], "U": U, "s": s, "redraws": red}
    raise PlantInfeasible("no valid planted decomposition")


def pack_solution(n: int, k: int, v: list, xs: list, Us: list) -> int:
    m = len(v)
    s = 0
    for i in range(m):
        s |= (xs[i] ^ v[i]) << (i * k)
    for j, u in enumerate(Us):
        s |= u << (m * k + j * n)
    return s


def unpack_solution(n: int, k: int, v: list, s: int):
    m = len(v)
    xs = [v[i] ^ ((s >> (i * k)) & ((1 << k) - 1)) for i in range(m)]
    Us = [(s >> (m * k + j * n)) & ((1 << n) - 1) for j in range(m - 2)]
    return xs, Us


# --------------------------------------------------------------------------
# Weil descent
# --------------------------------------------------------------------------
# A "field polynomial" is {monomial mask: coefficient in F}; the n coordinate
# polynomials are read off at the end. Squaring is coefficient-wise Frobenius
# (mask | mask = mask in the Boolean ring).
def _fp_add(P, Q):
    R = dict(P)
    for m_, c in Q.items():
        x = R.get(m_, 0) ^ c
        if x:
            R[m_] = x
        else:
            R.pop(m_, None)
    return R


def _fp_mul(F, P, Q):
    R = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            key = m1 | m2
            R[key] = R.get(key, 0) ^ F.mul(c1, c2)
    return {k_: c for k_, c in R.items() if c}


def _fp_sqr(F, P):
    return {m_: F.sqr(c) for m_, c in P.items()}


def _fp_S3(F, P1, P2, P3, B):
    P12, P13, P23 = _fp_mul(F, P1, P2), _fp_mul(F, P1, P3), _fp_mul(F, P2, P3)
    t = _fp_add(_fp_add(P12, P13), P23)
    r = _fp_add(_fp_sqr(F, t), _fp_mul(F, P12, P3))
    return _fp_add(r, {0: B} if B else {})


def var_layout(m: int, n: int, k: int):
    """(N, x_var_index(i, b), u_var_index(j, a))."""
    N = m * k + (m - 2) * n
    return N, (lambda i, b: i * k + b), (lambda j, a: m * k + j * n + a)


def build_system(F: Field, B: int, v: list, k: int, x_R: int):
    """EQS4(m, R) (EQS2 when every v_i = 0) as M = (m-1)*n multilinear
    generators. Equation l*n + a is coordinate a of link l; link l is
    S3(X_1, X_2, U_1) (l=0), S3(U_l, X_{l+2}, U_{l+1}), S3(U_{m-2}, X_m, x_R)."""
    n, m = F.n, len(v)
    N, xv, uv = var_layout(m, n, k)
    X = []
    for i in range(m):
        p = {1 << xv(i, b): 1 << b for b in range(k)}
        if v[i]:
            p[0] = v[i]
        X.append(p)
    U = [{1 << uv(j, a): 1 << a for a in range(n)} for j in range(m - 2)]
    XR = {0: x_R} if x_R else {}
    links = [_fp_S3(F, X[0], X[1], U[0], B)]
    for t in range(1, m - 2):
        links.append(_fp_S3(F, U[t - 1], X[t + 1], U[t], B))
    links.append(_fp_S3(F, U[m - 3], X[m - 1], XR, B))
    assert len(links) == m - 1
    eqs = []
    for P in links:
        for a in range(n):
            eqs.append(sorted(m_ for m_, c in P.items() if (c >> a) & 1))
    return {"nv": N, "neq": (m - 1) * n, "eqs": eqs}


def eval_poly(mons, point: int) -> int:
    """F_2 value of the multilinear polynomial (list of masks) at the 0/1 point."""
    s = 0
    for m_ in mons:
        if m_ & ~point == 0:
            s ^= 1
    return s


def field_side_links(F: Field, B: int, v: list, k: int, x_R: int, point: int):
    """Field-side value (n-bit int) of every link at the 0/1 point."""
    m, n = len(v), F.n
    xs, Us = unpack_solution(n, k, v, point)
    vals = [F.S3(xs[0], xs[1], Us[0], B)]
    for t in range(1, m - 2):
        vals.append(F.S3(Us[t - 1], xs[t + 1], Us[t], B))
    vals.append(F.S3(Us[m - 3], xs[m - 1], x_R, B))
    return vals


def descent_check(F: Field, B: int, v: list, k: int, x_R: int, system: dict, s: int,
                  rng: HashRng, n_points: int = 64) -> dict:
    """Every generator vanishes at s; at n_points random points every generator
    equals the matching coordinate of the field-side S_3 (IR-1 on mismatch)."""
    n, N = F.n, system["nv"]
    eqs = system["eqs"]
    bad_s = [i for i, e in enumerate(eqs) if eval_poly(e, s)]
    mism = 0
    for _ in range(n_points):
        pt = rng.getrandbits(N)
        vals = field_side_links(F, B, v, k, x_R, pt)
        for l_, c in enumerate(vals):
            for a in range(n):
                if eval_poly(eqs[l_ * n + a], pt) != (c >> a) & 1:
                    mism += 1
    return {"vanish_at_s_failures": len(bad_s), "random_point_mismatches": mism,
            "points": n_points, "ok": not bad_s and mism == 0}


def poly_degree(mons) -> int:
    return max((bin(x).count("1") for x in mons), default=-1)


def degree_profile(eqs):
    """Per equation (count of monomials of degree 0,1,2,3,...)."""
    out = []
    for e in eqs:
        c = {}
        for x in e:
            d = bin(x).count("1")
            c[d] = c.get(d, 0) + 1
        out.append([c.get(d, 0) for d in range(max(c, default=0) + 1)])
    return out


def canonical_bytes(nv: int, eqs) -> bytes:
    """sembin-sys-v1 canonical serialisation (see formats.md)."""
    obj = {"schema": "sembin-sys-v1", "nv": nv, "neq": len(eqs),
           "eqs": [[list(_vars_of(x)) for x in sorted(e, key=lambda x: (bin(x).count("1"), list(_vars_of(x))))]
                   for e in eqs]}
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _vars_of(mask: int):
    i = 0
    out = []
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return tuple(out)


def system_sha256(nv: int, eqs) -> str:
    return hashlib.sha256(canonical_bytes(nv, eqs)).hexdigest()
