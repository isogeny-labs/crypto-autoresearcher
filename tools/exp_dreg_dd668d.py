#!/usr/bin/env python3
"""Instrument for EXP-DREG-dd668d (LADDER-W-v1, rung n=1, one F_4 edge).

Governing text: experiments/EXP-DREG-dd668d/specification.yaml plus the additive
amendment AMD-EXP-DREG-dd668d-20261102-glsample (approved by
DEC-20261102-0dedaa). This file implements; it does not interpret results and
claims nothing. One execution emits exactly one outcome label.

Pipeline
  1. F_4 = F_2[z]/(z^2+z+1); elements are ints a0 + 2*a1 (coefficient of 1 first).
  2. Base curve: first ordinary y^2+xy = x^3+a2 x^2+a6 (a6 != 0) in the
     frozen lexicographic order on (a2, a6); kernel T = (0, sqrt(a6)).
  3. Velu 2-isogeny, certified: phi(T)=O, additive on all F_4-points, same
     #E(F_4), dual by DUAL-FROB (Frobenius then explicit iso).
  4. S_3 derived by elimination from the group law (sympy, modulus 2), then
     certified on every triple of F_4-points of both models.
  5. Chained t=4 system over F_2 (8 boolean variables), degree-filtration rank
     profile r(d), d <= 4, falls, and a degree-capped boolean grevlex basis.
  6. Controls: GL-8, NEARBY-DEG2, IDENTITY, TRACE.
  7. One outcome label from the frozen rules; artifacts under --out.

Interpretive choices that the specification leaves open are recorded in the
manifest under `reading` and are not hidden: the element order of the base
curve search, and the boolean reading of delta.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import random
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

D_MAX = 4
SEED = 20260922
EXPERIMENT_ID = "EXP-DREG-dd668d"
AMENDMENT_ID = "AMD-EXP-DREG-dd668d-20261102-glsample"

# --------------------------------------------------------------------------
# F_4 and the curve family
# --------------------------------------------------------------------------


def f4mul(a: int, b: int) -> int:
    a0, a1, b0, b1 = a & 1, a >> 1, b & 1, b >> 1
    return ((a0 & b0) ^ (a1 & b1)) | (((a0 & b1) ^ (a1 & b0) ^ (a1 & b1)) << 1)


F4INV = {a: next(b for b in range(1, 4) if f4mul(a, b) == 1) for a in range(1, 4)}


def f4sq(a: int) -> int:
    return f4mul(a, a)


class Curve:
    """y^2 + x*y = x^3 + a2 x^2 + a4 x + a6 over F_4 (a1 = 1, a3 = 0)."""

    def __init__(self, a2: int, a4: int, a6: int):
        self.a2, self.a4, self.a6 = a2, a4, a6

    def key(self):
        return (self.a2, self.a4, self.a6)

    def on(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        lhs = f4sq(y) ^ f4mul(x, y)
        rhs = f4mul(f4sq(x), x) ^ f4mul(self.a2, f4sq(x)) ^ f4mul(self.a4, x) ^ self.a6
        return lhs == rhs

    def points(self):
        return [None] + [(x, y) for x in range(4) for y in range(4) if self.on((x, y))]

    @staticmethod
    def neg(P):
        return None if P is None else (P[0], P[1] ^ P[0])

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == y1 ^ x1 or x1 == 0:
                return None
            lam = x1 ^ f4mul(y1 ^ self.a4, F4INV[x1])
        else:
            lam = f4mul(y1 ^ y2, F4INV[x1 ^ x2])
        x3 = f4sq(lam) ^ lam ^ self.a2 ^ x1 ^ x2
        y3 = f4mul(lam ^ 1, x3) ^ y1 ^ f4mul(lam, x1)
        R = (x3, y3)
        assert self.on(R), "group law left the curve"
        return R

    def mul2(self, P):
        return self.add(P, P)

    def order_count(self) -> int:
        return len(self.points())


def trace(curve: Curve) -> int:
    return 5 - curve.order_count()


def element_name(a: int) -> str:
    return {0: "0", 1: "1", 2: "z", 3: "z+1"}[a]


def candidate_models(element_order: str):
    """Ordinary models (a2, 0, a6), a6 != 0, in the frozen search order."""
    if element_order == "coord-lex":  # (coef of 1, coef of z) lexicographic
        order = [0, 2, 1, 3]
    elif element_order == "int":  # a0 + 2*a1 ascending
        order = [0, 1, 2, 3]
    else:
        raise ValueError(element_order)
    out = []
    for a2 in order:
        for a6 in order:
            if a6 == 0:
                continue
            c = Curve(a2, 0, a6)
            if trace(c) % 2 != 0:
                out.append(c)
    return out


# --------------------------------------------------------------------------
# Velu 2-isogeny with kernel T = (0, s), s^2 = a6
# --------------------------------------------------------------------------


def velu_params(dom: Curve):
    s = next(s for s in range(1, 4) if f4sq(s) == dom.a6)
    cod = Curve(dom.a2, s, dom.a6 ^ s)  # A4 = a4 - 5t = s, A6 = a6 - b2 t = a6 + s
    return s, cod


def phi(s: int, P):
    """X = x + s/x ; Y = y + s (x + y + s) / x^2 ; T and O go to O."""
    if P is None:
        return None
    x, y = P
    if x == 0:
        return None
    X = x ^ f4mul(s, F4INV[x])
    Y = y ^ f4mul(f4mul(s, x ^ y ^ s), F4INV[f4sq(x)])
    return (X, Y)


def normalise_codomain(cod: Curve):
    """Isomorphism y'' = y + s'x + t (r = 0, u = 1) onto a4 = 0, smallest (s', t)."""
    for sp in range(4):
        for t in range(4):
            if cod.a4 ^ t != 0:
                continue
            tgt = Curve(cod.a2 ^ sp ^ f4sq(sp), 0, cod.a6 ^ f4sq(t))

            def m(P, sp=sp, t=t):
                return None if P is None else (P[0], P[1] ^ f4mul(sp, P[0]) ^ t)

            pts = cod.points()
            if all(tgt.on(m(P)) for P in pts) and len({m(P) for P in pts}) == len(pts):
                return tgt, {"s": sp, "t": t, "r": 0, "u": 1}, m
    raise AssertionError("no normalising isomorphism over F_4")


def silverman_transform(c: Curve, u: int, r: int, s: int, t: int):
    """Coefficients (a1,a2,a3,a4,a6) of the curve obtained from c (a1=1,a3=0)
    by x = u^2 x' + r, y = u^3 y' + u^2 s x' + t, in characteristic 2."""
    ui = F4INV[u]
    a1p = f4mul(ui, 1)  # a1 + 2s = 1
    a2p = f4mul(F4INV[f4sq(u)], c.a2 ^ s ^ r ^ f4sq(s))  # a2 - s a1 + 3r - s^2
    a3p = f4mul(F4INV[f4mul(f4sq(u), u)], f4mul(r, 1))  # a3 + r a1 + 2t
    a4p = f4mul(F4INV[f4sq(f4sq(u))],
                c.a4 ^ 0 ^ 0 ^ f4mul(t ^ f4mul(r, s), 1) ^ f4sq(r) ^ 0)
    # a4 - s a3 + 2 r a2 - (t + r s) a1 + 3 r^2 - 2 s t
    a6p = f4mul(F4INV[f4sq(f4mul(f4sq(u), u))],
                c.a6 ^ f4mul(r, c.a4) ^ f4mul(f4sq(r), c.a2) ^ f4mul(f4sq(r), r)
                ^ f4sq(t) ^ f4mul(f4mul(r, t), 1))
    return a1p, a2p, a3p, a4p, a6p


def dual_frob_candidates(cod: Curve, dom: Curve):
    """DUAL-FROB: Frobenius E' -> E'^(2), then an explicit iso E'^(2) -> E.
    Returns (all attempts, chosen) ; each attempt records (u,r,s,t) and verdict."""
    frob_curve = Curve(f4sq(cod.a2), f4sq(cod.a4), f4sq(cod.a6))
    attempts = []
    chosen = None
    for u in range(1, 4):
        for r, s, t in itertools.product(range(4), repeat=3):
            a1p, a2p, a3p, a4p, a6p = silverman_transform(frob_curve, u, r, s, t)
            lands = (a1p, a2p, a3p, a4p, a6p) == (1, dom.a2, 0, dom.a4, dom.a6)
            if not lands:
                continue
            u2i = F4INV[f4sq(u)]
            u3i = F4INV[f4mul(f4sq(u), u)]

            def psi(P, u=u, r=r, s=s, t=t, u2i=u2i, u3i=u3i):
                if P is None:
                    return None
                x, y = P
                xe = f4mul(x ^ r, u2i)
                ye = f4mul(y ^ t ^ f4mul(f4mul(f4sq(u), s), xe), u3i)
                return (xe, ye)

            ok = True
            detail = []
            s_cod = velu_params(dom)[0]
            for P in dom.points():
                img = phi(s_cod, P)
                fr = None if img is None else (f4sq(img[0]), f4sq(img[1]))
                got = psi(fr)
                want = dom.mul2(P)
                if got != want or not dom.on(got):
                    ok = False
                    detail.append({"P": P, "got": got, "want": want})
            rec = {"construction": "DUAL-FROB", "u": u, "r": r, "s": s, "t": t,
                   "passes_2P_identity": ok, "failures": detail[:3]}
            attempts.append(rec)
            if ok and chosen is None:
                chosen = rec
    return attempts, chosen


# --------------------------------------------------------------------------
# S_3 by elimination, and its certificate
# --------------------------------------------------------------------------


def derive_s3_by_elimination():
    """Eliminate y1, y2 from  P1, P2 on E  and  x(P1+P2) = x3  (a1=1, a3=a4=0).
    Returns (elimination polynomial text, S3 text) after dividing the spurious
    (x1+x2)^2 factor, and asserts the quotient is Semaev's closed form."""
    from sympy import Poly, groebner, symbols

    x1, x2, x3, y1, y2, a2, a6 = symbols("x1 x2 x3 y1 y2 a2 a6")

    def f(x, y):
        return y**2 + x * y + x**3 + a2 * x**2 + a6

    g = (x1 + x2) ** 2 * (x3 + a2 + x1 + x2) + (y1 + y2) ** 2 + (y1 + y2) * (x1 + x2)
    G = groebner([f(x1, y1), f(x2, y2), g], y1, y2, x1, x2, x3, a2, a6,
                 modulus=2, order="lex")
    elim = [p for p in G.exprs if Poly(p, y1, y2).total_degree() == 0]
    assert len(elim) == 1, f"expected one y-free generator, got {len(elim)}"
    gens = (x1, x2, x3, a2, a6)
    E = Poly(elim[0], *gens, modulus=2)
    closed = Poly((x1 * x2 + x1 * x3 + x2 * x3) ** 2 + x1 * x2 * x3 + a6, *gens, modulus=2)
    spurious = Poly((x1 + x2) ** 2, *gens, modulus=2)
    assert E == closed * spurious, "elimination ideal != (x1+x2)^2 * S3"
    return str(E.as_expr()), str(closed.as_expr())


def s3_value(a6: int, x1: int, x2: int, x3: int) -> int:
    t = f4mul(x1, x2) ^ f4mul(x1, x3) ^ f4mul(x2, x3)
    return f4sq(t) ^ f4mul(f4mul(x1, x2), x3) ^ a6


def certify_s3(curve: Curve):
    """S_3(x1,x2,x3)=0  iff  P1 +- P2 +- P3 = O for some signs, on all triples
    of affine F_4-points."""
    pts = curve.points()[1:]
    total = bad = 0
    for p, q, r in itertools.product(pts, repeat=3):
        total += 1
        rel = any(curve.add(curve.add(p, a(q)), b(r)) is None
                  for a in (lambda z: z, Curve.neg) for b in (lambda z: z, Curve.neg))
        if (s3_value(curve.a6, p[0], q[0], r[0]) == 0) != rel:
            bad += 1
    return {"triples": total, "mismatches": bad, "passed": bad == 0}


# --------------------------------------------------------------------------
# Boolean polynomials: frozenset of square-free monomials (bitmasks)
# --------------------------------------------------------------------------

Poly2 = frozenset


def pmul(A, B):
    out = set()
    for ma in A:
        for mb in B:
            out ^= {ma | mb}
    return Poly2(out)


def padd(*terms):
    out = set()
    for t in terms:
        out ^= t
    return Poly2(out)


def pdeg(A) -> int:
    return max((bin(m).count("1") for m in A), default=-1)


def var(i: int):
    return Poly2({1 << i})


ZERO = Poly2()
ONE = Poly2({0})

# F_4-valued boolean expression: pair (c0, c1) of boolean polynomials


def e_const(a: int):
    return (ONE if a & 1 else ZERO, ONE if a & 2 else ZERO)


def e_add(a, b):
    return (padd(a[0], b[0]), padd(a[1], b[1]))


def e_mul(a, b):
    a0, a1 = a
    b0, b1 = b
    c0 = padd(pmul(a0, b0), pmul(a1, b1))
    c1 = padd(pmul(a0, b1), pmul(a1, b0), pmul(a1, b1))
    return (c0, c1)


def chained_system(a6: int):
    """Generators of the t=4, k=1 chained system (Weil-restricted to F_2).
    Variable order: x1,x2,x3,x4 (one bit each, value in V={0,1}), u1=(b4,b5),
    u2=(b6,b7)."""
    X = [(var(i), ZERO) for i in range(4)]
    U1 = (var(4), var(5))
    U2 = (var(6), var(7))
    RX = e_const(1)
    c6 = e_const(a6)

    def S3(p, q, r):
        t = e_add(e_add(e_mul(p, q), e_mul(p, r)), e_mul(q, r))
        return e_add(e_add(e_mul(t, t), e_mul(e_mul(p, q), r)), c6)

    eqs = [S3(U1, X[0], X[1]), S3(U1, U2, X[2]), S3(U2, X[3], RX)]
    gens = []
    for e in eqs:
        gens.extend([e[0], e[1]])
    return gens


# --------------------------------------------------------------------------
# Degree-filtration rank profile
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def monomials_upto(nvars: int, d: int):
    out = []
    for k in range(d + 1):
        for comb in itertools.combinations(range(nvars), k):
            out.append(sum(1 << i for i in comb))
    return tuple(sorted(out, key=lambda m: (bin(m).count("1"), m)))


def matrix_rows(gens, nvars: int, d: int):
    cols = monomials_upto(nvars, d)
    index = {m: i for i, m in enumerate(cols)}
    rows = []
    for g in gens:
        dg = pdeg(g)
        if dg < 0 or dg > d:
            continue
        for m in monomials_upto(nvars, d - dg):
            row = 0
            for t in g:
                row ^= 1 << index[m | t]
            if row:
                rows.append(row)
    return rows, cols


def echelon(rows):
    basis = {}
    for row in rows:
        while row:
            h = row.bit_length() - 1
            if h in basis:
                row ^= basis[h]
            else:
                basis[h] = row
                break
    return basis


def rank_profile(gens, nvars: int = 8, dmax: int = D_MAX):
    r, fall_dims, unit_at = [], [], None
    for d in range(dmax + 1):
        rows, cols = matrix_rows(gens, nvars, d)
        basis = echelon(rows)
        r.append(len(basis))
        # dim(V_d ∩ W_{<d}) = number of pivots whose monomial has degree < d
        low = sum(1 for h in basis if bin(cols[h]).count("1") < d)
        fall_dims.append(low)
        if unit_at is None and 0 in basis and basis[0] == 1:
            unit_at = d
    falls = []
    for d in range(1, dmax + 1):
        if fall_dims[d] > r[d - 1]:
            falls.append(d)
    return {
        "r": r,
        "first_fall": falls[0] if falls else None,
        "last_fall": falls[-1] if falls else None,
        "falls": falls,
        "unit_ideal_at_degree": unit_at,
        "generator_degrees": [pdeg(g) for g in gens],
        "generator_terms": [len(g) for g in gens],
        "has_inhomogeneous_generator": any(len({bin(t).count("1") for t in g}) > 1 for g in gens),
    }


def count_solutions(gens, nvars: int = 8) -> int:
    """Common zeros over F_2^nvars. In the quotient ring F_2[b]/(b^2+b) an ideal is
    the unit ideal exactly when this is 0, whatever degree 1 first enters at."""
    n = 0
    for a in range(1 << nvars):
        if all(sum(1 for m in g if (a & m) == m) % 2 == 0 for g in gens):
            n += 1
    return n


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------


def substitute(gens, forms):
    """b_i -> forms[i] (a boolean polynomial), square-free reduced."""
    out = []
    for g in gens:
        acc = set()
        for mono in g:
            term = ONE
            i = 0
            m = mono
            while m:
                if m & 1:
                    term = pmul(term, forms[i])
                m >>= 1
                i += 1
            acc ^= term
        out.append(Poly2(acc))
    return out


def linear_forms(M):
    return [Poly2({1 << j for j in range(len(M)) if (row >> j) & 1}) for row in M]


def gf2_rank(rows):
    return len(echelon(list(rows)))


def gl_sample(v: int, count: int = 8, seed: int = SEED):
    N = 4 * v * v
    rng = random.Random(seed)
    mats, record, attempts_failed = [], [], 0
    for k in range(count):
        attempt = 0
        while True:
            attempt += 1
            if attempt > 100:
                return None, {"instrument_failure": f"matrix {k}: 100 singular attempts"}
            A = [1 << i for i in range(v)]
            discarded = done = 0
            while done < N:
                p = rng.randrange(v)
                t = rng.randrange(v)
                if p == t:
                    discarded += 1
                    continue
                A[t] ^= A[p]
                done += 1
            if gf2_rank(A) == v:
                break
            attempts_failed += 1
        mats.append(A)
        record.append({"k": k, "attempts": attempt, "discarded_pairs": discarded, "rows": list(A)})
    canon = json.dumps([m for m in mats], separators=(",", ":"))
    return mats, {"v": v, "N": N, "seed": seed, "constructor": f"random.Random({seed})",
                  "draw_call": "rng.randrange(v)", "matrices": record,
                  "sha256": hashlib.sha256(canon.encode()).hexdigest(),
                  "rejected_attempts": attempts_failed}


# --------------------------------------------------------------------------
# Boolean grevlex Groebner basis with a degree cap
# --------------------------------------------------------------------------


def grevlex_key_factory(nvars: int):
    @lru_cache(maxsize=None)
    def key(m: int):
        return (bin(m).count("1"), tuple(-((m >> i) & 1) for i in range(nvars - 1, -1, -1)))
    return key


def grevlex_basis(gens, nvars: int = 8, cap: int = D_MAX):
    key = grevlex_key_factory(nvars)

    def lm(f):
        return max(f, key=key)

    def reduce(f, G):
        f = set(f)
        changed = True
        while changed and f:
            changed = False
            for t in sorted(f, key=key, reverse=True):
                for g, l in G:
                    if (l & t) == l:
                        mult = t & ~l
                        f ^= set(pmul(Poly2({mult}), g))
                        changed = True
                        break
                if changed:
                    break
        return Poly2(f)

    G = []
    queue = []

    def add_poly(f):
        l = lm(f)
        for g, lg in G:
            queue.append(((f, l), (g, lg)))
        for i in range(nvars):
            if (l >> i) & 1:
                queue.append(((f, l), None, i))
        G.append((f, l))

    seed = []
    for g in gens:
        g = Poly2(g)
        if g:
            seed.append(g)
    for g in seed:
        r = reduce(g, G)
        if r:
            add_poly(r)
    max_s_degree = 0
    while queue:
        item = queue.pop()
        if len(item) == 3:
            (f, l), _, i = item
            S = padd(f, pmul(Poly2({1 << i}), f))
        else:
            (f, lf), (g, lg) = item
            if lf & lg == 0:
                continue
            lcm = lf | lg
            S = padd(pmul(Poly2({lcm & ~lf}), f), pmul(Poly2({lcm & ~lg}), g))
        if not S:
            continue
        max_s_degree = max(max_s_degree, pdeg(S))
        if pdeg(S) > cap:
            return {"status": "unmeasured",
                    "reason": f"S-polynomial of degree {pdeg(S)} exceeds D_max={cap}",
                    "max_s_degree": max_s_degree}
        r = reduce(S, G)
        if r:
            add_poly(r)
    # reduced basis: keep one element per minimal leading monomial, then interreduce tails
    leads = list(G)
    minimal = [(g, l) for g, l in leads
               if not any(l2 != l and (l2 & l) == l2 for _, l2 in leads)]
    uniq, seen = [], set()
    for g, l in minimal:
        if l not in seen:
            seen.add(l)
            uniq.append((g, l))
    reduced = []
    for g, l in uniq:
        others = [(h, lh) for h, lh in uniq if lh != l]
        reduced.append(Poly2({l} | set(reduce(Poly2(set(g) - {l}), others))))
    unit = any(g == ONE for g in reduced)
    return {"status": "measured", "solving_degree": max(pdeg(g) for g in reduced),
            "basis_size": len(reduced), "unit_ideal": unit, "max_s_degree": max_s_degree}


# --------------------------------------------------------------------------
# delta: boolean degree of the cleared isogeny maps
# --------------------------------------------------------------------------


def anf_degrees(values):
    """Algebraic degree of each output bit of a function on 4 input bits."""
    degs = []
    for bit in range(2):
        f = [(v >> bit) & 1 for v in values]
        a = f[:]
        for i in range(4):
            for m in range(16):
                if m >> i & 1:
                    a[m] ^= a[m ^ (1 << i)]
        degs.append(max((bin(m).count("1") for m in range(16) if a[m]), default=0))
    return degs


def delta_report(s: int):
    """Cleared maps  X = Nx/Dx,  Y = Ny/Dy  as F_4-polynomials in (x, y);
    inputs encoded as bits (x0,x1,y0,y1), degree = ANF degree of the unique
    square-free polynomial of the function on F_4^2 (field equations applied)."""
    def table(fn):
        return [fn(i & 3, i >> 2) for i in range(16)]

    nx = lambda x, y: f4sq(x) ^ s
    dx = lambda x, y: x
    ny = lambda x, y: f4mul(f4sq(x), y) ^ f4mul(s, x) ^ f4mul(s, y) ^ f4sq(s)
    dy = lambda x, y: f4sq(x)
    out = {}
    for name, fn in (("Nx", nx), ("Dx", dx), ("Ny", ny), ("Dy", dy)):
        out[name] = max(anf_degrees(table(fn)))
    return {"numerator_degrees": {"Nx": out["Nx"], "Ny": out["Ny"]},
            "denominator_degrees": {"Dx": out["Dx"], "Dy": out["Dy"]},
            "delta": max(out["Nx"], out["Ny"]),
            "reading": "ANF degree of each Weil-restricted output bit of the cleared "
                       "F_4-polynomial maps (Nx=x^2+s, Dx=x, Ny=x^2 y+s x+s y+s^2, Dy=x^2), "
                       "square-free reduced; denominators recorded separately"}


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_experiment(element_order: str = "coord-lex", base_index: int = 0,
                   log=lambda *_: None):
    t0 = time.time()
    cert: dict = {"elements": {"0": 0, "1": 1, "z": 2, "z+1": 3,
                               "encoding": "int a0 + 2*a1, basis (1, z), z^2=z+1"}}
    models = candidate_models(element_order)
    cert["search_order"] = [{"a2": element_name(c.a2), "a6": element_name(c.a6),
                             "n_points": c.order_count(), "trace": trace(c)} for c in models]
    dom = models[base_index]
    s, cod = velu_params(dom)
    result = {"protocol_conformant": base_index == 0,
              "base_curve": {"a2": element_name(dom.a2), "a6": element_name(dom.a6),
                             "kernel": ["0", element_name(s)], "trace": trace(dom),
                             "n_points": dom.order_count()},
              "outcome_label": None, "notes": []}

    def finish(label, why):
        result["outcome_label"] = label
        result["label_reason"] = why
        result["wall_seconds"] = round(time.time() - t0, 3)
        return result, cert

    # ---- edge certificate -------------------------------------------------
    P = dom.points()
    edge = {}
    edge["kernel_to_infinity"] = phi(s, (0, s)) is None
    edge["image_on_codomain"] = all(cod.on(phi(s, p)) for p in P)
    edge["homomorphism"] = all(phi(s, dom.add(p, q)) == cod.add(phi(s, p), phi(s, q))
                               for p in P for q in P)
    edge["codomain_point_count"] = cod.order_count()
    edge["same_point_count"] = cod.order_count() == dom.order_count()
    norm, iso_params, iso_map = normalise_codomain(cod)
    edge["codomain_normalised"] = {"a2": element_name(norm.a2), "a6": element_name(norm.a6),
                                   "iso": iso_params}
    attempts, chosen = dual_frob_candidates(cod, dom)
    edge["dual_attempts"] = attempts
    edge["dual_chosen"] = chosen
    cert["edge"] = edge
    cert["trace_control"] = {"domain_points": dom.order_count(), "codomain_points": cod.order_count(),
                             "match": edge["same_point_count"]}
    if not (edge["kernel_to_infinity"] and edge["image_on_codomain"] and edge["homomorphism"]
            and edge["same_point_count"] and chosen is not None):
        return finish("no-certified-edge", "an edge-certificate item failed")

    # ---- S_3 derivation and certificates ---------------------------------
    elim, s3 = derive_s3_by_elimination()
    cert["s3"] = {"elimination_polynomial": elim, "s3_after_dividing_(x1+x2)^2": s3,
                  "domain_certificate": certify_s3(dom),
                  "codomain_normalised_certificate": certify_s3(norm)}
    if not (cert["s3"]["domain_certificate"]["passed"]
            and cert["s3"]["codomain_normalised_certificate"]["passed"]):
        return finish("no-certified-edge", "S_3 certificate failed; no rank was read")

    # ---- native ideals and profiles --------------------------------------
    g_dom = chained_system(dom.a6)
    g_cod = chained_system(norm.a6)
    pd_ = rank_profile(g_dom)
    pc_ = rank_profile(g_cod)
    metrics = {"r_domain": pd_["r"], "r_codomain": pc_["r"],
               "first_fall": {"domain": pd_["first_fall"], "codomain": pc_["first_fall"]},
               "last_fall": {"domain": pd_["last_fall"], "codomain": pc_["last_fall"]},
               "profile_domain": pd_, "profile_codomain": pc_}
    metrics["primary_max_abs_diff"] = max(abs(a - b) for a, b in zip(pd_["r"], pc_["r"]))
    metrics["solutions_over_F2"] = {"domain": count_solutions(g_dom), "codomain": count_solutions(g_cod)}
    result["metrics"] = metrics

    # ---- controls ---------------------------------------------------------
    ident = substitute(g_dom, linear_forms([1 << i for i in range(8)]))
    identity_ok = ident == [Poly2(g) for g in g_dom] and rank_profile(ident)["r"] == pd_["r"]
    mats, gl_rec = gl_sample(8)
    controls = {"IDENTITY": {"passed": identity_ok}, "TRACE": cert["trace_control"]}
    if mats is None:
        controls["GL-8"] = gl_rec
        result["controls"] = controls
        return finish("instrument", gl_rec["instrument_failure"])
    gl_results = []
    for k, M in enumerate(mats):
        prof = rank_profile(substitute(g_dom, linear_forms(M)))
        gl_results.append({"k": k, "r": prof["r"], "equal_to_native": prof["r"] == pd_["r"]})
    gl_ok = all(x["equal_to_native"] for x in gl_results)
    controls["GL-8"] = {"passed": gl_ok, "results": gl_results}
    forms = [var(i) for i in range(8)]
    forms[0] = padd(var(0), pmul(var(1), var(2)))
    near = rank_profile(substitute(g_dom, forms))
    controls["NEARBY-DEG2"] = {"r": near["r"], "moves_profile": near["r"] != pd_["r"],
                               "note": "may move r(d); not a gate"}
    result["controls"] = controls
    cert["gl_sample"] = gl_rec
    metrics["gl_check_passed"] = gl_ok

    # ---- secondary metrics ------------------------------------------------
    gv_d = grevlex_basis(g_dom)
    gv_c = grevlex_basis(g_cod)
    metrics["grevlex"] = {"domain": gv_d, "codomain": gv_c}
    delta = delta_report(s)
    metrics["delta"] = delta
    result["homogeneity_gate"] = {
        "triggered": not (pd_["has_inhomogeneous_generator"] or pc_["has_inhomogeneous_generator"]),
        "note": "square-free reduction b^2->b is applied; native generators are inhomogeneous"
                if (pd_["has_inhomogeneous_generator"] or pc_["has_inhomogeneous_generator"])
                else "all generators homogeneous: reduction made the system homogeneous"}

    label, why, note = decide_label(
        gl_ok=gl_ok, identity_ok=identity_ok,
        unit_dom=pd_["unit_ideal_at_degree"], unit_cod=pc_["unit_ideal_at_degree"],
        empty_dom=metrics["solutions_over_F2"]["domain"] == 0,
        empty_cod=metrics["solutions_over_F2"]["codomain"] == 0,
        homogeneous=result["homogeneity_gate"]["triggered"],
        diff=metrics["primary_max_abs_diff"], delta=delta["delta"], grevlex_dom=gv_d, grevlex_cod=gv_c)
    if note:
        result["notes"].append(note)
    return finish(label, why)


def decide_label(*, gl_ok, identity_ok, unit_dom, unit_cod, empty_dom, empty_cod, homogeneous,
                 diff, delta, grevlex_dom, grevlex_cod):
    """Frozen label rules, in the order the specification states them."""
    if not gl_ok or not identity_ok:
        return "instrument", "GL-8 or IDENTITY control changed r(d)", None
    if (unit_dom is not None and unit_dom <= 1) or (unit_cod is not None and unit_cod <= 1):
        return "degenerate-unit-ideal", "an ideal contains 1 in degree <= 1", None
    if empty_dom or empty_cod:
        # The success criterion requires that neither ideal is the unit ideal, at any degree;
        # an ideal with no common zero over F_2 is the unit ideal even if 1 first enters
        # the row space above degree 1.
        return ("degenerate-unit-ideal",
                "an ideal has no common zero over F_2^8 (unit ideal), first entering above degree 1",
                None)
    if homogeneous:
        return "homogeneous-no-op", "system homogeneous after reduction", None
    if delta == 1 and diff != 0:
        return "instrument", "delta = 1 and rank profiles differ", None
    if diff >= 1:
        return "filtration-gap", f"max_d |r_dom - r_cod| = {diff}", None
    both = grevlex_dom["status"] == grevlex_cod["status"] == "measured"
    if both and grevlex_dom["solving_degree"] != grevlex_cod["solving_degree"]:
        return ("order-artifact", "primary difference 0, grevlex solving degrees differ",
                f"would be {'linear' if delta == 1 else 'nonlinear-but-flat'} "
                "but grevlex solving degrees differ")
    return ("linear" if delta == 1 else "nonlinear-but-flat",
            "gl_check_passed, profiles agree for d <= 4", None)


def write_artifacts(out: Path, result, cert, args, repo: Path):
    out.mkdir(parents=True, exist_ok=True)
    spec = repo / "experiments" / EXPERIMENT_ID / "specification.yaml"
    amd = repo / "experiments" / EXPERIMENT_ID / "amendments" / f"{AMENDMENT_ID}.yaml"
    try:
        commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                                text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(repo), "status", "--porcelain",
                                     "--", "tools/exp_dreg_dd668d.py"],
                                    capture_output=True, text=True).stdout.strip())
    except OSError:
        commit, dirty = "unknown", True
    manifest = {
        "experiment_id": EXPERIMENT_ID, "amendment_id": AMENDMENT_ID,
        "decision_ids": ["DEC-20260922-0397f8", "DEC-20261102-0dedaa"],
        "command": " ".join([sys.executable] + sys.argv),
        "python": sys.version, "platform": platform.platform(),
        "runner": {"path": "tools/exp_dreg_dd668d.py",
                   "sha256": sha256_file(Path(__file__)), "repo_commit": commit,
                   "runner_dirty": dirty},
        "specification_sha256": sha256_file(spec) if spec.exists() else None,
        "amendment_sha256": sha256_file(amd) if amd.exists() else None,
        "rng": f"random.Random({SEED}); rng.randrange(v)",
        "reading": {
            "element_order": args.element_order,
            "element_order_note": "coord-lex orders an element by (coef of 1, coef of z) "
                                  "lexicographically: 0 < z < 1 < z+1 (the amendment's basis "
                                  "convention); 'int' orders by a0+2*a1: 0 < 1 < z < z+1. "
                                  "The specification does not say which; the choice changes the base curve.",
            "delta": result.get("metrics", {}).get("delta", {}).get("reading"),
            "grevlex_cap": "unmeasured when any boolean S-polynomial (pair or (1+x)g multiple) "
                           "has degree > D_max = 4 before reduction",
            "rung": "n=1 only (amendment A4)",
            "class_range": "not reported (single edge; stopping rule)"},
        "route": args.route, "executed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "protocol_conformant": result["protocol_conformant"],
    }
    import yaml
    (out / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    (out / "metrics.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=str))
    (out / "certificates.json").write_text(json.dumps(cert, indent=1, sort_keys=True, default=str))
    (out / "report.md").write_text(render_report(result, cert, manifest))


def render_report(result, cert, manifest) -> str:
    m = result.get("metrics", {})
    lines = [f"# {EXPERIMENT_ID} run report", "",
             f"- outcome_label: **{result['outcome_label']}** ({result.get('label_reason')})",
             f"- protocol_conformant: {result['protocol_conformant']}",
             f"- base curve: a2={result['base_curve']['a2']}, a6={result['base_curve']['a6']}, "
             f"#E(F_4)={result['base_curve']['n_points']}, trace {result['base_curve']['trace']}",
             f"- element order reading: {manifest['reading']['element_order']}", ""]
    if m:
        lines += ["## Primary", f"- r_domain   = {m['r_domain']}", f"- r_codomain = {m['r_codomain']}",
                  f"- max_d |r_dom - r_cod| = {m['primary_max_abs_diff']}",
                  f"- gl_check_passed = {m.get('gl_check_passed')}", "",
                  "## Secondary",
                  f"- first_fall: {m['first_fall']}", f"- last_fall: {m['last_fall']}",
                  f"- grevlex: {json.dumps(m.get('grevlex'))}",
                  f"- delta: {m.get('delta', {}).get('delta')}; numerator degrees "
                  f"{m.get('delta', {}).get('numerator_degrees')}; denominator degrees "
                  f"{m.get('delta', {}).get('denominator_degrees')}", ""]
    lines += ["## Controls", "```json", json.dumps(result.get("controls", {}), indent=1, default=str), "```", "",
              "## Claim ceiling",
              "Toy tier, one F_4 edge. No ECDLP exponent, no class-wide slope, and first-fall, "
              "last-fall and grevlex solving degree are not equated with a degree of regularity.", ""]
    for n in result.get("notes", []):
        lines.append(f"- note: {n}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="directory for metrics.json, report.md, "
                    "manifest.yaml, certificates.json")
    ap.add_argument("--element-order", choices=["coord-lex", "int"], default="coord-lex")
    ap.add_argument("--base-index", type=int, default=0,
                    help="debug only: use the k-th model of the search order instead of the first; "
                         "marks the run protocol_conformant=false and is refused under runs/")
    ap.add_argument("--route", default="unspecified", help="recorded in the manifest")
    args = ap.parse_args(argv)
    out = Path(args.out).resolve()
    if args.base_index != 0 and f"{EXPERIMENT_ID}/runs" in str(out):
        ap.error("--base-index != 0 may not write under the experiment's runs/ directory")
    repo = Path(__file__).resolve().parent.parent
    result, cert = run_experiment(args.element_order, args.base_index)
    write_artifacts(out, result, cert, args, repo)
    print(json.dumps({"outcome_label": result["outcome_label"],
                      "protocol_conformant": result["protocol_conformant"],
                      "out": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
