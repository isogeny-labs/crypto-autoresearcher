#!/usr/bin/env python3
"""semaev_eval.py -- WP2 / G31-004.

Importable, dependency-free (stdlib only) evaluator for the Semaev summation
polynomials S_3 and S_4 in odd characteristic, specialised from the *stored*
universal polynomials over Z[a,b,x...] produced by WP1's census.py
(polynomials/{s3,s4}_universal_Z.json).  Nothing here recomputes a resultant.

Conventions (identical to WP1 validate.py / harness/semaev.py)
--------------------------------------------------------------
E: y^2 = x^3 + a x + b, char != 2,3.  With the cleared-denominator closed form

  S_3(x1,x2,x3) = (x1-x2)^2 x3^2
                  - 2((x1+x2)(x1 x2 + a) + 2b) x3
                  + (x1 x2 - a)^2 - 4b(x1+x2)

and S_4 = Res_t(S_3(x1,x2,t), S_3(x3,x4,t)).  S_m(x)=0 over F_p iff there are
lifts y_i (in F_p or F_p^2) with sum P_i = O.

S_3 is degree 2 in x3; S_4 is degree 4 in x4 (degree 4 in every x_i).

Public API (exact signatures)
-----------------------------
  load_sparse(path) -> (gens: list[str], terms: dict[tuple[int,...], int])
  specialize(terms, gens, subs, p) -> dict[tuple[int,...], int]
  s3_terms() / s4_terms() -> (gens, terms)          # universal, over Z
  s3_mod(a, b, p) -> dict[(e1,e2,e3), int]
  s4_mod(a, b, p) -> dict[(e1,e2,e3,e4), int]
  s4_grouped_by_x4(a, b, p, s4=None) -> dict[int, dict[(e1,e2,e3), int]]
  s3_coeffs(x1, x2, a, b, p) -> (A, B, C)           # S_3 = A x3^2 + B x3 + C
  s3_eval(x1, x2, x3, a, b, p) -> int
  s4_coeffs_in_x4(x1, x2, x3, a, b, p, grouped=None) -> (c0, c1, c2, c3, c4)
  s4_eval(x1, x2, x3, x4, a, b, p, grouped=None) -> int
  power_table(x, maxdeg, p) -> list[int]
  s3_eval_sparse(x1, x2, x3, terms, p) -> int
  s4_eval_sparse(x1, x2, x3, x4, terms, p) -> int
  Curve(p, a, b)  with .f .on_curve_x .neg .add .lift_ys
  selftest(verbose=True, nrand=400, seed=31004) -> dict

Run `python3 semaev_eval.py` for the p=101 self-test.
"""
from __future__ import annotations

import json
import os

POLY_DIR = ("/Volumes/SSD990-2/crypto-autoresearcher/notes/"
            "g31-004-odd-char-census-20261120/polynomials")

_S3_JSON = os.path.join(POLY_DIR, "s3_universal_Z.json")
_S4_JSON = os.path.join(POLY_DIR, "s4_universal_Z.json")
_S3_101 = os.path.join(POLY_DIR, "s3_mod101.json")
_S4_101 = os.path.join(POLY_DIR, "s4_mod101.json")


# --------------------------------------------------------------- loading
def load_sparse(path):
    """Read a census sparse JSON: {gens: [...], terms: [{exp, coeff}]}.

    Returns (gens, {exp_tuple: int coeff}).  Exponents are ordered as `gens`.
    """
    with open(path) as fh:
        d = json.load(fh)
    gens = list(d["gens"])
    terms = {}
    for t in d["terms"]:
        e = tuple(int(v) for v in t["exp"])
        c = int(t["coeff"])
        terms[e] = terms.get(e, 0) + c
    return gens, {e: c for e, c in terms.items() if c}


def s3_terms():
    return load_sparse(_S3_JSON)


def s4_terms():
    return load_sparse(_S4_JSON)


def specialize(terms, gens, subs, p):
    """Substitute the variables named in `subs` by their integer values mod p.

    Remaining (x-)variables keep their exponent positions in the output key,
    in their original relative order.  Coefficients are reduced mod p and
    zero terms dropped (a=0 / b=0 specialisations lose support, as expected).
    """
    xpos = [i for i, g in enumerate(gens) if g not in subs]
    out = {}
    cache = {g: pow(v % p, 1, p) for g, v in subs.items()}
    for e, c in terms.items():
        cc = c
        for i, g in enumerate(gens):
            ei = e[i]
            if ei and g in subs:
                cc *= pow(cache[g], ei, p)
        if cc % p:
            key = tuple(e[i] for i in xpos)
            out[key] = (out.get(key, 0) + cc) % p
    return {k: v for k, v in out.items() if v}


def s3_mod(a, b, p):
    """S_3 coefficients mod p as {(e1,e2,e3): c} for E: y^2=x^3+ax+b."""
    gens, terms = s3_terms()
    return specialize(terms, gens, {"a": a, "b": b}, p)


def s4_mod(a, b, p):
    """S_4 coefficients mod p as {(e1,e2,e3,e4): c}."""
    gens, terms = s4_terms()
    return specialize(terms, gens, {"a": a, "b": b}, p)


def s4_grouped_by_x4(a, b, p, s4=None):
    """Group S_4 terms by their x4 exponent: {deg: {(e1,e2,e3): c}}.

    Evaluating the 5 groups at a fixed (x1,x2,x3) yields the coefficients of
    S_4 as a degree-<=4 polynomial in x4 -- the realistic sieve inner loop.
    """
    if s4 is None:
        s4 = s4_mod(a, b, p)
    groups = {d: {} for d in range(5)}
    for e, c in s4.items():
        d = e[3]
        key = (e[0], e[1], e[2])
        groups[d][key] = (groups[d].get(key, 0) + c) % p
    for d in groups:
        groups[d] = {k: v for k, v in groups[d].items() if v}
    return groups


# ------------------------------------------------------- closed-form S_3
def s3_coeffs(x1, x2, a, b, p):
    """(A,B,C) with S_3(x1,x2,x3) = A x3^2 + B x3 + C  (mod p)."""
    A = (x1 - x2) * (x1 - x2) % p
    B = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
    C = ((x1 * x2 - a) * (x1 * x2 - a) - 4 * b * (x1 + x2)) % p
    return A, B, C


def s3_eval(x1, x2, x3, a, b, p):
    A, B, C = s3_coeffs(x1, x2, a, b, p)
    return (A * x3 % p * x3 + B * x3 + C) % p


# ------------------------------------------------------------- S_4 eval
def s4_coeffs_in_x4(x1, x2, x3, a, b, p, grouped=None):
    """Coefficients (c0..c4) of S_4 as a polynomial in x4 at fixed (x1,x2,x3)."""
    if grouped is None:
        grouped = s4_grouped_by_x4(a, b, p)
    p1 = (1, x1 % p, x1 * x1 % p, x1 * x1 % p * x1 % p,
          x1 * x1 % p * x1 % p * x1 % p)
    p2 = (1, x2 % p, x2 * x2 % p, x2 * x2 % p * x2 % p,
          x2 * x2 % p * x2 % p * x2 % p)
    p3 = (1, x3 % p, x3 * x3 % p, x3 * x3 % p * x3 % p,
          x3 * x3 % p * x3 % p * x3 % p)
    out = []
    for d in range(5):
        acc = 0
        for (e1, e2, e3), c in grouped[d].items():
            acc += c * p1[e1] * p2[e2] * p3[e3]
        out.append(acc % p)
    return out


def s4_eval(x1, x2, x3, x4, a, b, p, grouped=None):
    c0, c1, c2, c3, c4 = s4_coeffs_in_x4(x1, x2, x3, a, b, p, grouped)
    return ((((c4 * x4 + c3) % p * x4 + c2) % p * x4 + c1) % p * x4 + c0) % p


# ------------------------------------------- generic sparse (reference) eval
def power_table(x, maxdeg, p):
    """[x^0, x^1, ..., x^maxdeg] mod p."""
    out = [1]
    for _ in range(maxdeg):
        out.append(out[-1] * x % p)
    return out


def _maxdeg(terms, nvars):
    md = [0] * nvars
    for e in terms:
        for i in range(nvars):
            if e[i] > md[i]:
                md[i] = e[i]
    return md


def s3_eval_sparse(x1, x2, x3, terms, p):
    """Direct 13-monomial accumulate with per-call power tables."""
    md = _maxdeg(terms, 3)
    pw = [power_table(v, md[i], p) for i, v in enumerate((x1, x2, x3))]
    acc = 0
    for e, c in terms.items():
        acc += c * pw[0][e[0]] * pw[1][e[1]] * pw[2][e[2]]
    return acc % p


def s4_eval_sparse(x1, x2, x3, x4, terms, p):
    """Direct ~439-monomial accumulate with per-call power tables."""
    md = _maxdeg(terms, 4)
    pw = [power_table(v, md[i], p) for i, v in enumerate((x1, x2, x3, x4))]
    acc = 0
    for e, c in terms.items():
        acc += (c * pw[0][e[0]] * pw[1][e[1]]
                * pw[2][e[2]] * pw[3][e[3]])
    return acc % p


# ------------------------------------------------------------------ curve
class Curve:
    """Affine short-Weierstrass curve over F_p, plus F_{p^2} lifts for truth.

    F_{p^2} is represented as F_p[w]/(w^2 - ns) and an element is a tuple
    (u, v) meaning u + v*w.  `add` is the plain F_p group law (the reference
    timing target); `add2` is the same law over F_{p^2} and keeps both
    coordinates in F_{p^2} (a sum of lifts can have non-rational abscissa).
    """

    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a % p, b % p
        if (4 * self.a ** 3 + 27 * self.b ** 2) % p == 0:
            raise ValueError("singular curve")
        self.ns = self._nonresidue()

    def _nonresidue(self):
        p = self.p
        for ns in range(2, p):
            if pow(ns, (p - 1) // 2, p) == p - 1:
                return ns
        raise ValueError("no nonresidue found")

    def f(self, x):
        return (x * x % self.p * x + self.a * x + self.b) % self.p

    def on_curve_x(self, x):
        fx = self.f(x)
        return fx == 0 or pow(fx, (self.p - 1) // 2, self.p) in (0, 1)

    # ---- F_p arithmetic
    def neg(self, P):
        if P is None:
            return None
        return (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        """Affine point addition over F_p (realistic Python reference)."""
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = ((3 * x1 * x1 + self.a) * pow(2 * y1, -1, p)) % p
        else:
            lam = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    # ---- F_{p^2} arithmetic (for algebraic-closure truth)
    def _f2_mul(self, u, v):
        p, ns = self.p, self.ns
        return ((u[0] * v[0] + ns * u[1] * v[1]) % p,
                (u[0] * v[1] + u[1] * v[0]) % p)

    def _f2_inv(self, u):
        p, ns = self.p, self.ns
        den = (u[0] * u[0] - ns * u[1] * u[1]) % p
        di = pow(den, -1, p)
        return (u[0] * di % p, (-u[1]) * di % p)

    def lift_ys(self, x):
        """All y in F_{p^2} with y^2 = f(x), as (u,v) pairs (1 or 2 of them)."""
        p, ns = self.p, self.ns
        fx = self.f(x)
        if fx == 0:
            return [((0, 0))]
        if pow(fx, (p - 1) // 2, p) == 1:
            y = pow(fx, (p + 1) // 4, p) if p % 4 == 3 else self._sqrt_p1m4(fx)
            assert y * y % p == fx
            return [((y, 0)), ((-y) % p, 0)]
        g = self._sqrt_p1m4(fx * pow(ns, -1, p) % p)
        assert g * g % p == fx * pow(ns, -1, p) % p
        return [((0, g)), ((0, (-g) % p))]

    def _sqrt_p1m4(self, a):
        """Tonelli-Shanks, general odd prime."""
        p = self.p
        if a == 0:
            return 0
        if pow(a, (p - 1) // 2, p) != 1:
            raise ValueError("not a QR")
        if p % 4 == 3:
            return pow(a, (p + 1) // 4, p)
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = self._nonresidue()
        m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
        while t != 1:
            i, t2 = 0, t
            while t2 != 1:
                t2 = t2 * t2 % p
                i += 1
            bb = pow(c, 1 << (m - i - 1), p)
            m, c = i, bb * bb % p
            t, r = t * c % p, r * bb % p
        return r

    # ---- F_{p^2} point arithmetic.  Points are (x, y) with BOTH coordinates
    # elements of F_{p^2}: sums of lifts with non-rational y generally have a
    # non-rational abscissa too, so x must not be truncated to F_p.
    def _f2_add(self, u, v):
        p = self.p
        return ((u[0] + v[0]) % p, (u[1] + v[1]) % p)

    def _f2_sub(self, u, v):
        p = self.p
        return ((u[0] - v[0]) % p, (u[1] - v[1]) % p)

    def add2(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if self._f2_add(y1, y2) == (0, 0):
                return None
            num = self._f2_add(self._f2_mul((3 * x1[0] % p, 3 * x1[1] % p),
                                           x1), (self.a, 0))
            lam = self._f2_mul(self._f2_inv(self._f2_add(y1, y1)), num)
        else:
            lam = self._f2_mul(self._f2_sub(y2, y1),
                              self._f2_inv(self._f2_sub(x2, x1)))
        x3 = self._f2_sub(self._f2_sub(self._f2_mul(lam, lam),
                                       x1), x2)
        y3 = self._f2_sub(self._f2_mul(lam, self._f2_sub(x1, x3)), y1)
        return (x3, y3)

    def neg2(self, P):
        if P is None:
            return None
        p = self.p
        return (P[0], ((-P[1][0]) % p, (-P[1][1]) % p))


# --------------------------------------------------------- closure truths
def s3_truth_ext(C, tup):
    """Exist F_{p^2} lifts with P1+P2+P3 = O."""
    pts = [C.lift_ys(x) for x in tup]
    A = [((tup[0], 0), y) for y in pts[0]]
    B = [((tup[1], 0), y) for y in pts[1]]
    Cc = [((tup[2], 0), y) for y in pts[2]]
    for P in A:
        for Q in B:
            S = C.add2(P, Q)
            for R in Cc:
                if C.add2(S, R) is None:
                    return True
    return False


def s4_truth_ext(C, tup):
    """Exist F_{p^2} lifts with P1+P2+P3+P4 = O."""
    pts = [C.lift_ys(x) for x in tup]
    s12 = set()
    for y1 in pts[0]:
        for y2 in pts[1]:
            P = C.add2(((tup[0], 0), y1), ((tup[1], 0), y2))
            s12.add(None if P is None else (P[0], P[1]))
    s34 = set()
    for y3 in pts[2]:
        for y4 in pts[3]:
            P = C.add2(((tup[2], 0), y3), ((tup[3], 0), y4))
            s34.add(None if P is None else (P[0], P[1]))
    for S in s12:
        n = C.neg2(None if S is None else (S[0], S[1]))
        if n in s34:
            return True
    return False


# ---------------------------------------------------------------- selftest
def selftest(verbose=True, nrand=400, seed=31004):
    """Assert the specialised evaluators reproduce WP1's census/validation.

    Checks, all at p=101, a=b=1 (the WP1 curve):
      1. support sizes 13 / 439 and term-for-term equality with the stored
         s3_mod101.json / s4_mod101.json;
      2. S_3 sparse-from-universal == closed-form A,B,C on random tuples;
      3. S_4 from universal == the independent quadratic-resultant closed form
         (validate.py's mC / exhaustive path) on random tuples;
      4. zero sets agree with the F_{p^2} group-law truth on random tuples
         (validate.py's ext4_truth / exhaustive S_3 semantics).
    """
    import random
    p, a, b = 101, 1, 1
    rng = random.Random(seed)
    rep = {}

    g3, t3 = s3_terms()
    g4, t4 = s4_terms()
    rep["universal_monomials"] = {"S3": len(t3), "S4": len(t4)}
    assert len(t3) == 13, len(t3)
    assert len(t4) == 540, len(t4)
    assert g3 == ["x1", "x2", "x3", "a", "b"]
    assert g4 == ["x1", "x2", "x3", "x4", "a", "b"]

    s3p = s3_mod(a, b, p)
    s4p = s4_mod(a, b, p)
    rep["specialised_monomials_a1b1_p101"] = {"S3": len(s3p), "S4": len(s4p)}
    assert len(s3p) == 13
    assert len(s4p) == 439

    # term-for-term vs the stored mod-101 specialisations
    _, s3_ref = load_sparse(_S3_101)
    _, s4_ref = load_sparse(_S4_101)
    assert s3p == {e: c % p for e, c in s3_ref.items()}, "S3 != s3_mod101.json"
    assert s4p == {e: c % p for e, c in s4_ref.items()}, "S4 != s4_mod101.json"
    rep["equals_stored_mod101"] = True

    # closed-form S_3 (A,B,C) is definitionally the same polynomial; check the
    # *universal-specialised sparse* path against it.
    mm3 = 0
    for _ in range(nrand):
        x1, x2, x3 = (rng.randrange(p) for _ in range(3))
        A, B, Cc = s3_coeffs(x1, x2, a, b, p)
        v_abc = (A * x3 % p * x3 + B * x3 + Cc) % p
        v_sp = s3_eval_sparse(x1, x2, x3, s3p, p)
        mm3 += (v_abc != v_sp)
    assert mm3 == 0, mm3
    rep["S3_sparse_vs_closedform_mismatches"] = mm3

    # S_4 vs the quadratic-resultant closed form (AF-CD)^2-(AE-BD)(BF-CE)
    def res_formula(v1, v2, v3, v4):
        A1, B1, C1 = s3_coeffs(v1, v2, a, b, p)
        A2, B2, C2 = s3_coeffs(v3, v4, a, b, p)
        return (((A1 * C2 - C1 * A2) % p) ** 2
                - ((A1 * B2 - B1 * A2) % p)
                * ((B1 * C2 - C1 * B2) % p)) % p

    mm4 = 0
    for _ in range(nrand):
        tup = tuple(rng.randrange(p) for _ in range(4))
        mm4 += (s4_eval(*tup, a, b, p) != res_formula(*tup))
        mm4 += (s4_eval_sparse(*tup, s4p, p) != res_formula(*tup))
    assert mm4 == 0, mm4
    rep["S4_vs_resultant_formula_mismatches"] = mm4

    # zero sets vs F_{p^2} group-law truth
    C = Curve(p, a, b)
    z3 = mmz3 = 0
    for _ in range(nrand):
        tup = tuple(rng.randrange(p) for _ in range(3))
        z = s3_eval(*tup, a, b, p) == 0
        z3 += z
        mmz3 += (z != s3_truth_ext(C, tup))
    assert mmz3 == 0, mmz3
    z4 = mmz4 = 0
    for _ in range(nrand):
        tup = tuple(rng.randrange(p) for _ in range(4))
        z = s4_eval(*tup, a, b, p) == 0
        z4 += z
        mmz4 += (z != s4_truth_ext(C, tup))
    assert mmz4 == 0, mmz4
    rep["S3_zero_vs_grouptruth"] = {"samples": nrand, "zeros": z3,
                                    "mismatches": mmz3}
    rep["S4_zero_vs_grouptruth"] = {"samples": nrand, "zeros": z4,
                                    "mismatches": mmz4}
    rep["passed"] = True
    if verbose:
        print("selftest OK:", json.dumps(rep, indent=2, default=str))
    return rep


if __name__ == "__main__":
    selftest()
