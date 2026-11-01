"""Gaudry/Diem point decomposition over F_{p^n} by Weil descent, solved with msolve.

Setting (Gaudry 2009, Diem 2011; KN-LIT-673219): E: y^2 = x^3 + a x + b over
F_q, q = p^n, factor base F = {P in E(F_q) : x(P) in F_p}.  A decomposition of
a target R is R = +/-P_1 +/- ... +/-P_m with every x(P_i) in F_p.  The Semaev
network of S_3 boxes (diagram.py) is written over F_q and Weil-descended: an
element of F_q is a vector of n coordinates over F_p in the basis 1, t, ...,
t^{n-1} of F_p[t]/(f), and every box S_3(a, b, c) = 0 becomes n equations over
F_p.  The x_i are F_p unknowns; an internal wire u_k (a partial sum's
x-coordinate) is n F_p unknowns u{k}c0..u{k}c{n-1}.

Presentations (diagram.TOPOLOGIES, LEAD-ICE-gag-contraction-planner):

``chain`` / ``tree``  descend every box, keep the wires: n(m-1) equations in
                      m + n(m-2) unknowns.
``monolithic``        contract the wire over F_q first (Res_u of two S_3, i.e.
                      S_{m+1}; m <= 3), then descend: n equations in m unknowns.

For n = m both are square.  msolve's F_p-rational solutions are lifted to
points of E(F_q) and every relation is checked by point addition, so the
returned relations do not depend on the presentation.  A rational solution of
the chained system has an F_q-rational wire; the monolithic system can also
return x-tuples whose partial sums are not F_q-rational (the 2-torsion channel
of KN-TECH-b18366); those fail the lift and are counted in ``unlifted``.

Everything here is pure Python (no Sage); msolve is the only external tool and
keeps its 2^16 bound on p (msolve.py).  The arithmetic is for toy sizes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import diagram, polyfp
from .msolve import Poly, System, run_msolve

Elem = tuple[int, ...]  # n coordinates over F_p, lowest power of t first


# -- the field F_{p^n} -----------------------------------------------------------

def is_irreducible(f: list[int], p: int) -> bool:
    """Ben-Or: monic f of degree n is irreducible iff gcd(x^{p^i} - x, f) = 1, i <= n/2."""
    n = len(f) - 1
    if n < 1:
        return False
    h = [0, 1]
    for _ in range(n // 2):
        h = polyfp.powmod(h, p, f, p)
        diff = _poly_sub(h, [0, 1], p)
        if len(polyfp.gcd(diff, f, p)) != 1:
            return False
    return True


class ExtField:
    """F_p[t]/(f) with f monic irreducible of degree n."""

    def __init__(self, p: int, n: int, modulus: list[int] | None = None, seed: int = 0):
        if p < 3 or n < 1:
            raise ValueError("need an odd prime p and n >= 1")
        self.p, self.n = p, n
        if modulus is None:
            rng = random.Random(f"modulus|{p}|{n}|{seed}")
            while True:
                f = [rng.randrange(p) for _ in range(n)] + [1]
                if n == 1 or is_irreducible(f, p):
                    break
            modulus = f
        modulus = polyfp.trim(modulus, p)
        if len(modulus) != n + 1 or modulus[-1] != 1:
            raise ValueError("modulus must be monic of degree n")
        if n > 1 and not is_irreducible(modulus, p):
            raise ValueError("modulus is reducible")
        self.modulus = modulus
        self.q = p ** n
        # t^k mod f for k < 2n - 1, as coordinate vectors (used by symbolic products)
        self.tpow = [self._vec(polyfp.mod([0] * k + [1], modulus, p)) for k in range(2 * n - 1)]

    def _vec(self, f: list[int]) -> Elem:
        f = list(f) + [0] * (self.n - len(f))
        return tuple(c % self.p for c in f[:self.n])

    def elem(self, coords) -> Elem:
        return self._vec(list(coords))

    def base(self, c: int) -> Elem:
        return self._vec([c])

    def zero(self) -> Elem:
        return (0,) * self.n

    def one(self) -> Elem:
        return self.base(1)

    def in_base_field(self, a: Elem) -> bool:
        return all(c == 0 for c in a[1:])

    def add(self, a: Elem, b: Elem) -> Elem:
        return tuple((x + y) % self.p for x, y in zip(a, b))

    def sub(self, a: Elem, b: Elem) -> Elem:
        return tuple((x - y) % self.p for x, y in zip(a, b))

    def neg(self, a: Elem) -> Elem:
        return tuple((-x) % self.p for x in a)

    def mul(self, a: Elem, b: Elem) -> Elem:
        return self._vec(polyfp.mod(polyfp.mul(list(a), list(b), self.p), self.modulus, self.p))

    def scale(self, a: Elem, c: int) -> Elem:
        return tuple(x * c % self.p for x in a)

    def inv(self, a: Elem) -> Elem:
        if not any(a):
            raise ZeroDivisionError("inverse of zero in F_q")
        # extended Euclid in F_p[t]
        p = self.p
        r0, r1 = list(self.modulus), polyfp.trim(list(a), p)
        s0, s1 = [], [1]
        while r1:
            q, r = polyfp.divmod_(r0, r1, p)
            r0, r1 = r1, r
            s0, s1 = s1, polyfp.trim(_poly_sub(s0, polyfp.mul(q, s1, p), p), p)
        c = pow(r0[0], -1, p)  # r0 is a nonzero constant
        return self._vec([x * c for x in s0])

    def pow(self, a: Elem, e: int) -> Elem:
        result, base = self.one(), a
        while e:
            if e & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            e >>= 1
        return result

    def is_square(self, a: Elem) -> bool:
        return not any(a) or self.pow(a, (self.q - 1) // 2) == self.one()

    def sqrt(self, a: Elem) -> Elem | None:
        """A square root (Tonelli-Shanks over F_q), normalised to the smaller of +/- y."""
        if not any(a):
            return self.zero()
        if not self.is_square(a):
            return None
        q = self.q
        s, Q = 0, q - 1
        while Q % 2 == 0:
            s, Q = s + 1, Q // 2
        rng = random.Random(f"nonresidue|{self.p}|{self.modulus}")
        while True:
            z = self.elem([rng.randrange(self.p) for _ in range(self.n)])
            if any(z) and not self.is_square(z):
                break
        M, c, t, R = s, self.pow(z, Q), self.pow(a, Q), self.pow(a, (Q + 1) // 2)
        one = self.one()
        while t != one:
            i, t2 = 0, t
            while t2 != one:
                t2, i = self.mul(t2, t2), i + 1
            b = c
            for _ in range(M - i - 1):
                b = self.mul(b, b)
            M, c = i, self.mul(b, b)
            t, R = self.mul(t, c), self.mul(R, b)
        return min(R, self.neg(R))

    def random(self, rng: random.Random) -> Elem:
        return self.elem([rng.randrange(self.p) for _ in range(self.n)])


def _poly_sub(f: list[int], g: list[int], p: int) -> list[int]:
    out = [0] * max(len(f), len(g))
    for i, c in enumerate(f):
        out[i] += c
    for i, c in enumerate(g):
        out[i] -= c
    return polyfp.trim(out, p)


# -- the curve over F_{p^n} -------------------------------------------------------

ExtPoint = tuple[Elem, Elem] | None  # None is the point at infinity


class ExtCurve:
    """y^2 = x^3 + a x + b over an ExtField (affine group law)."""

    def __init__(self, F: ExtField, a: Elem, b: Elem):
        disc = F.add(F.scale(F.mul(F.mul(a, a), a), 4), F.scale(F.mul(b, b), 27))
        if not any(disc):
            raise ValueError("singular curve")
        self.F, self.a, self.b = F, a, b
        self._lifts: dict[int, ExtPoint] = {}

    @classmethod
    def random(cls, F: ExtField, rng: random.Random) -> "ExtCurve":
        while True:
            try:
                return cls(F, F.random(rng), F.random(rng))
            except ValueError:
                continue

    def rhs(self, x: Elem) -> Elem:
        F = self.F
        return F.add(F.add(F.mul(F.mul(x, x), x), F.mul(self.a, x)), self.b)

    def lift_x(self, x: Elem) -> ExtPoint:
        """The point with this x and normalised y, or None if x is not an abscissa."""
        y = self.F.sqrt(self.rhs(x))
        return None if y is None else (x, y)

    def on_curve(self, P: ExtPoint) -> bool:
        return P is None or self.F.mul(P[1], P[1]) == self.rhs(P[0])

    def neg(self, P: ExtPoint) -> ExtPoint:
        return None if P is None else (P[0], self.F.neg(P[1]))

    def add(self, P: ExtPoint, Q: ExtPoint) -> ExtPoint:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2:
            if F.add(y1, y2) == F.zero():
                return None
            num = F.add(F.scale(F.mul(x1, x1), 3), self.a)
            lam = F.mul(num, F.inv(F.scale(y1, 2)))
        else:
            lam = F.mul(F.sub(y2, y1), F.inv(F.sub(x2, x1)))
        x3 = F.sub(F.sub(F.mul(lam, lam), x1), x2)
        return (x3, F.sub(F.mul(lam, F.sub(x1, x3)), y1))

    def factor_base_point(self, x: int) -> ExtPoint:
        """The normalised lift of an F_p abscissa (cached: square roots dominate otherwise)."""
        x %= self.F.p
        if x not in self._lifts:
            self._lifts[x] = self.lift_x(self.F.base(x))
        return self._lifts[x]


def planted_target(E: ExtCurve, m: int, rng: random.Random) -> tuple[ExtPoint, list[int]]:
    """R = sum of m random signed factor-base points, and their x-coordinates."""
    xs, R = [], None
    while len(xs) < m:
        P = E.factor_base_point(rng.randrange(E.F.p))
        if P is None:
            continue
        xs.append(P[0][0])
        R = E.add(R, P if rng.random() < 0.5 else E.neg(P))
    return R, xs


# -- symbolic F_q-valued polynomials and descent ---------------------------------
# An ExtPoly is a list of n Poly (one per coordinate), each over F_p in nv variables.

def _const(F: ExtField, c: Elem, nv: int) -> list[Poly]:
    zero = (0,) * nv
    return [{zero: v} if v else {} for v in c]


def _var(F: ExtField, i: int, nv: int) -> list[Poly]:
    out: list[Poly] = [{} for _ in range(F.n)]
    out[0] = {tuple(1 if k == i else 0 for k in range(nv)): 1}
    return out


def _wire(F: ExtField, first: int, nv: int) -> list[Poly]:
    return [{tuple(1 if k == first + j else 0 for k in range(nv)): 1} for j in range(F.n)]


def _eadd(F: ExtField, f: list[Poly], g: list[Poly]) -> list[Poly]:
    return [diagram.padd(a, b, F.p) for a, b in zip(f, g)]


def _escale(F: ExtField, f: list[Poly], c: int) -> list[Poly]:
    return [diagram.pscale(a, c % F.p, F.p) for a in f]


def _emul(F: ExtField, f: list[Poly], g: list[Poly]) -> list[Poly]:
    p, n = F.p, F.n
    conv: list[Poly] = [{} for _ in range(2 * n - 1)]
    for i, a in enumerate(f):
        if not a:
            continue
        for j, b in enumerate(g):
            if b:
                conv[i + j] = diagram.padd(conv[i + j], diagram.pmul(a, b, p), p)
    out: list[Poly] = [{} for _ in range(n)]
    for k, c in enumerate(conv):
        if not c:
            continue
        for j, r in enumerate(F.tpow[k]):
            if r:
                out[j] = diagram.padd(out[j], diagram.pscale(c, r, p), p)
    return out


def _s3_coefficients(F: ExtField, E: ExtCurve, X1, X2, nv: int):
    """(A, B, C) with S_3(X1, X2, X) = A X^2 + B X + C, all F_q-valued polynomials."""
    a, b = _const(F, E.a, nv), _const(F, E.b, nv)
    diff = _eadd(F, X1, _escale(F, X2, -1))
    A = _emul(F, diff, diff)
    s, prod = _eadd(F, X1, X2), _emul(F, X1, X2)
    B = _escale(F, _eadd(F, _emul(F, s, _eadd(F, prod, a)), _escale(F, b, 2)), -2)
    pa = _eadd(F, prod, _escale(F, a, -1))
    C = _eadd(F, _emul(F, pa, pa), _escale(F, _emul(F, b, s), -4))
    return A, B, C


def _s3(F, E, X1, X2, X3, nv):
    A, B, C = _s3_coefficients(F, E, X1, X2, nv)
    return _eadd(F, _eadd(F, _emul(F, A, _emul(F, X3, X3)), _emul(F, B, X3)), C)


def descent_names(m: int, n: int, topology: str) -> list[str]:
    wires = 0 if topology == "monolithic" else diagram.build(topology, m).wires
    return ([f"x{i + 1}" for i in range(m)]
            + [f"u{k + 1}c{j}" for k in range(wires) for j in range(n)] + ["z"])


def descent_system(E: ExtCurve, xR: Elem, m: int, rng: random.Random,
                   topology: str = "chain") -> System:
    """The Weil-descended decomposition system for x(R) = xR under a presentation."""
    F = E.F
    dg = diagram.build(topology, m)
    names = descent_names(m, F.n, topology)
    nv = len(names)
    R = _const(F, xR, nv)

    def term(t):
        if t[0] == "x":
            return _var(F, t[1], nv)
        if t[0] == "u":
            return _wire(F, m + F.n * t[1], nv)
        return R

    if topology == "monolithic":
        if m == 2:
            semaev = [_s3(F, E, term(("x", 0)), term(("x", 1)), R, nv)]
        else:  # m == 3, one wire: Res_u(S_3(x1, x2, u), S_3(u, x3, xR)) over F_q
            A0, B0, C0 = _s3_coefficients(F, E, term(("x", 0)), term(("x", 1)), nv)
            A1, B1, C1 = _s3_coefficients(F, E, term(("x", 2)), R, nv)
            neg = -1
            t1 = _eadd(F, _emul(F, A0, C1), _escale(F, _emul(F, C0, A1), neg))
            t2 = _eadd(F, _emul(F, A0, B1), _escale(F, _emul(F, B0, A1), neg))
            t3 = _eadd(F, _emul(F, B0, C1), _escale(F, _emul(F, C0, B1), neg))
            semaev = [_eadd(F, _emul(F, t1, t1), _escale(F, _emul(F, t2, t3), neg))]
    else:
        semaev = [_s3(F, E, term(bx.a), term(bx.b), term(bx.c), nv) for bx in dg.boxes]
    polys = [coord for ep in semaev for coord in ep if coord]
    p = F.p
    form: Poly = {tuple(1 if v == nv - 1 else 0 for v in range(nv)): 1}
    for v in range(nv - 1):
        form[tuple(1 if w == v else 0 for w in range(nv))] = (-rng.randrange(1, p)) % p
    polys.append(form)
    return System(names, polys, p, m)


def descent_plan(topology: str, m: int, n: int) -> dict:
    dg = diagram.build(topology, m)
    contracted = topology == "monolithic"
    return {
        "topology": topology, "m": m, "n": n,
        "unknowns": m + (0 if contracted else n * dg.wires),
        "equations": n * (1 if contracted else len(dg.boxes)),
        "max_degree_per_x": 2 ** (m - 1) if contracted else 2,
    }


# -- decomposition ----------------------------------------------------------------

Relation = tuple[tuple[int, int], ...]  # sorted (x, sign) pairs; sign of the normalised lift


def signed_relation(E: ExtCurve, xs: list[int], R: ExtPoint) -> Relation | None:
    """The first sign pattern (fixed order) with sum s_i * lift(x_i) = R, canonicalised."""
    xs = sorted(xs)
    pts = [E.factor_base_point(x) for x in xs]
    if any(P is None for P in pts):
        return None
    for mask in range(1 << len(xs)):
        S: ExtPoint = None
        signs = []
        for i, P in enumerate(pts):
            s = -1 if mask >> i & 1 else 1
            signs.append(s)
            S = E.add(S, P if s > 0 else E.neg(P))
        if S == R:
            return tuple(zip(xs, signs))
    return None


def decompositions_bruteforce(E: ExtCurve, R: ExtPoint, m: int) -> list[Relation]:
    """Every decomposition by the group law alone (no summation polynomials); m in (2, 3)."""
    if m not in (2, 3):
        raise ValueError("brute force is implemented for m = 2, 3")
    F = E.F
    base = [x for x in range(F.p) if E.factor_base_point(x) is not None]
    found: set[tuple[int, ...]] = set()
    if m == 2:
        for x1 in base:
            P = E.factor_base_point(x1)
            for Q in (E.add(R, E.neg(P)), E.add(R, P)):
                if Q is not None and F.in_base_field(Q[0]):
                    found.add(tuple(sorted((x1, Q[0][0]))))
    else:
        for i, x1 in enumerate(base):
            P1 = E.factor_base_point(x1)
            for s1 in (P1, E.neg(P1)):
                R1 = E.add(R, E.neg(s1))
                for x2 in base[i:]:
                    P2 = E.factor_base_point(x2)
                    for s2 in (P2, E.neg(P2)):
                        Q = E.add(R1, E.neg(s2))
                        if Q is not None and F.in_base_field(Q[0]):
                            found.add(tuple(sorted((x1, x2, Q[0][0]))))
    rels = {signed_relation(E, list(xs), R) for xs in found}
    return sorted(r for r in rels if r is not None)


@dataclass
class DescentOutcome:
    status: str
    relations: list[Relation]
    seconds: float
    runs: int
    degree: int
    rational_solutions: int
    unlifted: int
    topology: str
    plan: dict = field(default_factory=dict)
    detail: str = ""


def decompose_descent(E: ExtCurve, R: ExtPoint, m: int, seed: int = 0,
                      topology: str = "chain", timeout: float | None = None,
                      retries: int = 8, threads: int = 1) -> DescentOutcome:
    """All decompositions of R over the F_p-abscissa factor base, via msolve.

    msolve 0.6.5's report that the separating form fails (status ``failed``)
    is not deterministic for small p: on one identical n = m = 3 system over
    F_{101^3} it was returned in 9 of 15 runs, at p = 211 in 4 of 15 for one
    presentation, and in none of 15 at p = 307, 503, 1009, 4099 and 32749.  Each
    failure is retried with a fresh form and charged in ``runs`` and
    ``seconds``; a final ``failed`` is censored, never read as no solution.
    """
    if R is None:
        raise ValueError("target is the point at infinity")
    F = E.F
    rng = random.Random(f"descent|{F.p}|{F.modulus}|{E.a}|{E.b}|{R}|{m}|{seed}")
    plan = descent_plan(topology, m, F.n)
    seconds, runs = 0.0, 0
    while runs < retries:
        runs += 1
        run = run_msolve(descent_system(E, R[0], m, rng, topology), timeout, threads)
        seconds += run.seconds
        if run.status != "failed":
            break
    if run.status not in ("ok", "no_solution"):
        return DescentOutcome(run.status, [], seconds, runs, run.degree, 0, 0, topology,
                              plan, run.detail)
    rels, unlifted = set(), 0
    for vals in run.solutions:
        rel = signed_relation(E, vals[:m], R)
        if rel is None:
            unlifted += 1
            continue
        rels.add(rel)
    return DescentOutcome(run.status, sorted(rels), seconds, runs, run.degree,
                          len(run.solutions), unlifted, topology, plan)

