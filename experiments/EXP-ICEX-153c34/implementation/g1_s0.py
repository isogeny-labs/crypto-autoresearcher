"""S0-only G1 instrument for EXP-ICEX-153c34.

The module contains the non-grid algebraic path needed by the smoke
gates: exact Semaev f3/f5 evaluation, the D-2 monomial-basis pseudo-resultant
for target-specialised f6, and a deterministic sparse lex Buchberger solver
over the indicator ideal.  The charged protocol driver is deliberately absent:
this task is not admitted to create frozen runs.

All arithmetic in the G1 path is local Python arithmetic with explicit
operation counters.  The O5 oracle is kept in the S0 gate worker as an independent
verifier and is never called from ``g1_membership``.
"""

from __future__ import annotations

import itertools
import json
from functools import lru_cache
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Counters:
    mul: int = 0
    inv: int = 0
    probes: int = 0
    point_add: int = 0
    s_pairs: int = 0
    reductions: int = 0
    product_skips: int = 0
    trace_operations: bool = False
    component: str | None = None
    events: list = field(default_factory=list, repr=False)

    FIELDS = ("mul", "inv", "probes", "point_add", "s_pairs",
              "reductions", "product_skips")

    def set_component(self, component):
        if component not in ("S", "G", "X", "V", "P"):
            raise ValueError("unknown counter component")
        self.component = component

    def charge(self, operation, count=1, site="unspecified"):
        if operation not in self.FIELDS:
            raise ValueError("unknown counter operation")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError("counter charge must be a positive integer")
        setattr(self, operation, getattr(self, operation) + count)
        if self.trace_operations:
            if self.component not in ("P", "S", "G", "X", "V"):
                raise RuntimeError("operation charged outside P/S/G/X/V")
            self.events.append({
                "sequence": len(self.events), "component": self.component,
                "operation": operation, "count": count, "site": site,
            })

    def units(self):
        return self.mul + 10 * self.inv + self.probes + 13 * self.point_add

    def snapshot(self):
        return {key: getattr(self, key) for key in self.FIELDS}

    def totals(self):
        return self.snapshot() | {"units": self.units()}

    @staticmethod
    def delta(after, before):
        raw = {key: after.get(key, 0) - before.get(key, 0) for key in after}
        raw["units"] = raw["mul"] + 10 * raw["inv"] + raw["probes"] + 13 * raw["point_add"]
        return raw


class Field:
    def __init__(self, p, counters=None):
        self.p = int(p)
        self.c = counters or Counters()

    def add(self, a, b):
        return (a + b) % self.p

    def neg(self, a):
        return (-a) % self.p

    def sub(self, a, b):
        return (a - b) % self.p

    def mul(self, a, b):
        self.c.charge("mul", site="Field.mul")
        return (a * b) % self.p

    def inv(self, a):
        if a % self.p == 0:
            raise ZeroDivisionError("field inverse of zero")
        self.c.charge("inv", site="Field.inv")
        return pow(a, self.p - 2, self.p)


def poly_trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return [x for x in a]


def poly_add(F, a, b):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % F.p
    return poly_trim(out)


def poly_scale(F, a, k):
    k %= F.p
    if k == 1:
        return poly_trim(a)
    if k == F.p - 1:
        return poly_trim([(-x) % F.p for x in a])
    return poly_trim([F.mul(x, k) for x in a])


def poly_mul(F, a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            F.c.charge("mul", site="poly_mul")
            out[i + j] = (out[i + j] + x * y) % F.p
    return poly_trim(out)


def poly_eval(F, a, x):
    out = 0
    for c in reversed(a):
        F.c.charge("mul", site="poly_eval")
        out = (out * x + c) % F.p
    return out


def poly_divmod(F, a, b):
    a = poly_trim(a)
    b = poly_trim(b)
    if not b:
        raise ZeroDivisionError("polynomial division by zero")
    if len(a) < len(b):
        return [], a
    q = [0] * (len(a) - len(b) + 1)
    r = a[:]
    ilc = 1 if b[-1] == 1 else F.inv(b[-1])
    while r and len(r) >= len(b):
        d = len(r) - len(b)
        k = r[-1] if ilc == 1 else F.mul(r[-1], ilc)
        q[d] = k
        for i, v in enumerate(b):
            r[i + d] = (r[i + d] - F.mul(k, v)) % F.p
        r = poly_trim(r)
    return poly_trim(q), r


def poly_gcd(F, a, b):
    """Monic gcd over F_p, with every division charged through ``F``."""
    a, b = poly_trim(a), poly_trim(b)
    while b:
        _, r = poly_divmod(F, a, b)
        a, b = b, r
    if not a:
        return []
    return poly_scale(F, a, F.inv(a[-1]))


def resultant_dp(F, A, B):
    """Division-free determinant of the full Sylvester matrix.

    A and B are low-to-high coefficient lists.  The subset DP is the
    independent reconstruction used for the S0 determinant check; it uses no
    divisions and retains formal zero slots.
    """
    da, db = len(A) - 1, len(B) - 1
    if da < 0 or db < 0:
        return 0
    n = da + db
    M = [[0 for _ in range(n)] for _ in range(n)]
    # db shifted rows of A followed by da shifted rows of B.
    for r in range(db):
        for j, v in enumerate(A):
            if r + j < n:
                M[r][r + j] = v % F.p
    for r in range(da):
        for j, v in enumerate(B):
            if r + j < n:
                M[db + r][r + j] = v % F.p
    dp = {0: 1}
    for r in range(n):
        nxt = {}
        for mask, value in dp.items():
            for col in range(n):
                if mask & (1 << col) or M[r][col] == 0:
                    continue
                # Number of unused columns before col gives the Laplace sign.
                inversions = (mask >> (col + 1)).bit_count()
                sign = -1 if inversions & 1 else 1
                term = F.mul(value, M[r][col])
                key = mask | (1 << col)
                nxt[key] = (nxt.get(key, 0) + sign * term) % F.p
        dp = nxt
    return dp.get((1 << n) - 1, 0) % F.p


def s3_coeffs(p, a, b, u, v):
    # f3(u,v,z) = A z^2 + B z + C.
    A = (u - v) ** 2 % p
    B = (-2 * ((u + v) * (u * v + a) + 2 * b)) % p
    C = ((u * v - a) ** 2 - 4 * b * (u + v)) % p
    return [C, B, A]


@lru_cache(maxsize=None)
def load_s5_terms(path):
    doc = json.loads(Path(path).read_text())
    return doc["S5"], doc["degrees"]["S5"]


def s5_eval(p, a, b, xs, terms_path):
    """Evaluate f5 from the committed S5 coefficient inventory."""
    terms, _ = load_s5_terms(terms_path)
    out = 0
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        c = term[7]
        v = c * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip(xs, exps):
            v = v * pow(x, e, p) % p
        out = (out + v) % p
    return out


def f6_specialised(p, a, b, xs, xR, terms_path):
    """Compute f6(x1..x5,xR) by the approved target-specialised resultant.

    The inner f5 is treated as a polynomial in z=x5 and the f3 factor as a
    quadratic in z.  This evaluates the full formal degree slots and does not
    form a target-independent symbolic f6.
    """
    x1, x2, x3, x4, x5 = xs
    terms, degrees = load_s5_terms(terms_path)
    A = [0] * (degrees[-1] + 1)
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        c = term[7]
        v = c * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip((x1, x2, x3, x4), exps[:4]):
            v = v * pow(x, e, p) % p
        A[exps[4]] = (A[exps[4]] + v * 1) % p
    B = s3_coeffs(p, a, b, x5, xR)
    F = Field(p)
    return resultant_dp(F, A, B)


def f6_specialised_bareiss(p, a, b, xs, xR, terms_path):
    """Independent division-based 10x10 determinant for G0-2/G0-3."""
    terms, degrees = load_s5_terms(terms_path)
    A = [0] * (degrees[-1] + 1)
    for term in terms:
        ea, eb = term[0], term[1]
        exps = term[2:7]
        v = term[7] * pow(a, ea, p) * pow(b, eb, p) % p
        for x, e in zip(xs[:4], exps[:4]):
            v = v * pow(x, e, p) % p
        A[exps[4]] = (A[exps[4]] + v) % p
    B = s3_coeffs(p, a, b, xs[4], xR)
    n = (len(A) - 1) + (len(B) - 1)
    M = [[0 for _ in range(n)] for _ in range(n)]
    da, db = len(A) - 1, len(B) - 1
    for r in range(db):
        for j, v in enumerate(A):
            M[r][r + j] = v % p
    for r in range(da):
        for j, v in enumerate(B):
            M[db + r][r + j] = v % p
    prev = 1
    sign = 1
    for k in range(n - 1):
        pivot = next((r for r in range(k, n) if M[r][k] % p), None)
        if pivot is None:
            return 0
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            sign = -sign
        pk = M[k][k] % p
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = (pk * M[i][j] - M[i][k] * M[k][j]) % p
                if k:
                    num = (num * pow(prev, p - 2, p)) % p
                M[i][j] = num
            M[i][k] = 0
        prev = pk
    return sign * M[-1][-1] % p


def _xpoly_sub(a, b, p):
    n = max(len(a), len(b))
    return poly_trim([((a[i] if i < len(a) else 0)
                       - (b[i] if i < len(b) else 0)) % p for i in range(n)])


def _xpoly_pow(F, base, exponent):
    out = [1]
    cur = list(base)
    while exponent:
        if exponent & 1:
            out = poly_mul(F, out, cur)
        exponent >>= 1
        if exponent:
            cur = poly_mul(F, cur, cur)
    return out


def _counted_mul(left, right, p, counters, site):
    """One explicit F_p multiplication used outside the Field wrapper."""
    if counters:
        counters.charge("mul", site=site)
    return left * right % p


def _d2_pseudo_basis(p, a, b, xR, counters=None):
    """Coefficients of A^7*z^i mod (A*z^2+B*z+C), i=0..8."""
    F = Field(p, counters)
    xR2 = _counted_mul(xR, xR, p, counters, "d2_target.xR_square")
    axR = _counted_mul(a, xR, p, counters, "d2_target.a_xR")
    aa = _counted_mul(a, a, p, counters, "d2_target.a_square")
    bxR = _counted_mul(b, xR, p, counters, "d2_target.b_xR")
    # Multiplication by the public small constants 2 and 4 is implemented as
    # additions and therefore belongs to telemetry_uncharged (D-2/D-3).
    twice_b = (b + b) % p
    twice_xR = (xR + xR) % p
    twice_axR = (axR + axR) % p
    four_b = (twice_b + twice_b) % p
    four_bxR = (bxR + bxR + bxR + bxR) % p
    A = [xR2, -twice_xR % p, 1]
    B = [-(axR + twice_b + axR + twice_b) % p,
         -(a + xR2 + a + xR2) % p, -twice_xR % p]
    C = [(aa - four_bxR) % p,
         (-twice_axR - four_b) % p, xR2]
    up = [[0], [1]]
    vp = [[1], [0]]
    for degree in range(2, 9):
        up.append(_xpoly_sub(poly_mul(F, A, vp[-1]), poly_mul(F, B, up[-1]), p))
        vp.append(poly_scale(F, poly_mul(F, C, up[-2]), -1 % p))
    U, V = [], []
    A_powers = {power: _xpoly_pow(F, A, power) for power in range(8)}
    for degree in range(9):
        if degree == 0:
            U.append([])
            V.append(A_powers[7])
        else:
            scale = A_powers[8 - degree]
            U.append(poly_mul(F, up[degree], scale))
            V.append(poly_mul(F, vp[degree], scale))
    return A, B, C, U, V, A_powers[7]


def _d2_pair_weights(p, a, b, xR, counters=None):
    """Quadratic coefficient polynomials for Res_z(f5,f3) after exact division."""
    F = Field(p, counters)
    A, B, C, U, V, divisor = _d2_pseudo_basis(p, a, b, xR, counters)
    weights = {}
    for i in range(9):
        for j in range(i, 9):
            if i == j:
                numerator = _xpoly_sub(
                    poly_add(F, poly_mul(F, C, poly_mul(F, U[i], U[i])),
                             poly_mul(F, A, poly_mul(F, V[i], V[i]))),
                    poly_mul(F, B, poly_mul(F, U[i], V[i])), p)
            else:
                cuu = poly_scale(F, poly_mul(F, C, poly_mul(F, U[i], U[j])), 2)
                avv = poly_scale(F, poly_mul(F, A, poly_mul(F, V[i], V[j])), 2)
                cross = poly_add(F, poly_mul(F, U[i], V[j]),
                                 poly_mul(F, U[j], V[i]))
                numerator = _xpoly_sub(poly_add(F, cuu, avv),
                                       poly_mul(F, B, cross), p)
            quotient, remainder = poly_divmod(F, numerator, divisor)
            if remainder:
                raise ArithmeticError("D-2 pseudo-resultant coefficient is not exactly divisible")
            weights[i, j] = quotient
    return weights


def indicator_coefficients(V, p, counters=None):
    """Return the monic product g_V(X)=prod_v(X-v), low coefficient first."""
    indicator = [1]
    for value in sorted(V):
        nxt = [0] * (len(indicator) + 1)
        for degree, coeff in enumerate(indicator):
            nxt[degree] = (nxt[degree] - coeff * value) % p
            if counters:
                counters.charge("mul", site="setup.indicator_product")
            nxt[degree + 1] = (nxt[degree + 1] + coeff) % p
        indicator = nxt
    return indicator


def indicator_from_coefficients(coefficients, var, nvars):
    terms = {}
    for degree, coeff in enumerate(coefficients):
        if coeff:
            exponent = [0] * nvars
            exponent[var] = degree
            terms[tuple(exponent)] = coeff
    return SparsePoly(nvars, terms)


def d2_setup(p, a, b, V, terms_path, counters=None):
    """Build and optionally charge the fixed per-fixture P_setup artifacts."""
    terms, degrees = load_s5_terms(str(terms_path))
    coeffs = [SparsePoly(4, {}) for _ in range(degrees[-1] + 1)]
    for term in terms:
        ea, eb = term[0], term[1]
        exps = tuple(term[2:7])
        a_power = _fp_pow(a, ea, p, counters, site_prefix="setup.f5.pow_a")
        b_power = _fp_pow(b, eb, p, counters, site_prefix="setup.f5.pow_b")
        coeff = _counted_mul(term[7] % p, a_power, p, counters,
                             "setup.f5.coefficient_a")
        coeff = _counted_mul(coeff, b_power, p, counters,
                             "setup.f5.coefficient_b")
        e = exps[:4]
        coeffs[exps[4]].terms[e] = (coeffs[exps[4]].terms.get(e, 0) + coeff) % p
    coeffs = [reduce_indicator_poly(poly, V, p, counters) for poly in coeffs]
    pairs = {}
    for i in range(9):
        for j in range(i, 9):
            product = coeffs[i].mul(coeffs[j], p, counters)
            pairs[i, j] = reduce_indicator_poly(product, V, p, counters)
    ordered_v = tuple(sorted(V))
    indicator = indicator_coefficients(ordered_v, p, counters)
    points = {}
    for x in ordered_v:
        x_square = _counted_mul(x, x, p, counters, "setup.lift.x_square")
        x_cube = _counted_mul(x_square, x, p, counters, "setup.lift.x_cube")
        a_x = _counted_mul(a, x, p, counters, "setup.lift.a_x")
        y = _legendre_sqrt((x_cube + a_x + b) % p, p, counters)
        points[x] = (x, min(y, p - y))
    return {
        "p": int(p), "a": int(a), "b": int(b), "V": ordered_v,
        "coeffs": coeffs, "pair_products": pairs,
        # g_V, its five monomial-basis generators, and factor-base lifts are
        # P_setup artifacts.  Rebuilding any of them inside a query would be
        # an uncharged operation in S/G/V and is therefore forbidden.
        "indicator": indicator,
        "indicator_generators": tuple(
            indicator_from_coefficients(indicator, var, 5) for var in range(5)
        ),
        "points": points,
    }


def d2_specialise(setup, xR, counters=None):
    """Form the D-2 target-specialised f6 normal form in monomial R5."""
    p, a, b, V = setup["p"], setup["a"], setup["b"], setup["V"]
    weights = _d2_pair_weights(p, a, b, int(xR), counters)
    indicator = setup["indicator"]
    remainders = {}
    out = {}
    for key, pair_poly in setup["pair_products"].items():
        weight = weights[key]
        for degree, value in enumerate(weight):
            if not value:
                continue
            if degree not in remainders:
                monomial = [0] * (degree + 1)
                monomial[degree] = 1
                remainders[degree] = _one_var_remainder(p, monomial, indicator, counters)
            for x5_degree, reduced_coeff in enumerate(remainders[degree]):
                if not reduced_coeff:
                    continue
                scalar = value * reduced_coeff % p
                if counters:
                    counters.charge("mul", site="d2_specialise.scalar")
                for exp4, coeff4 in pair_poly.terms.items():
                    exp = tuple(exp4) + (x5_degree,)
                    out[exp] = (out.get(exp, 0) + scalar * coeff4) % p
                    if counters:
                        counters.charge("mul", site="d2_specialise.pair_product")
    return SparsePoly(5, out).clean(p)


def d2_zero_target(setup, counters=None):
    """D-6 target-O branch: reduced f5(x1,...,x5)."""
    p, V = setup["p"], setup["V"]
    indicator = setup["indicator"]
    out = {}
    for degree, coeff_poly in enumerate(setup["coeffs"]):
        monomial = [0] * (degree + 1)
        monomial[degree] = 1
        remainder = _one_var_remainder(p, monomial, indicator, counters)
        for reduced_degree, scalar in enumerate(remainder):
            if not scalar:
                continue
            for exp4, coeff in coeff_poly.terms.items():
                exp = tuple(exp4) + (reduced_degree,)
                out[exp] = (out.get(exp, 0) + scalar * coeff) % p
                if counters:
                    counters.charge("mul", site="d2_zero_target.coefficient")
    return SparsePoly(5, out).clean(p)


def _one_var_remainder(p, coeff, degree_poly, counters=None):
    """Remainder of a low-degree monomial polynomial modulo a monic g_V."""
    a = list(coeff)
    while len(a) >= len(degree_poly):
        k = a[-1] % p
        d = len(a) - len(degree_poly)
        if k:
            for i, v in enumerate(degree_poly):
                a[i + d] = (a[i + d] - k * v) % p
                if counters:
                    counters.charge("mul", site="one_var_remainder")
        a.pop()
    return poly_trim(a)


def reduce_indicator_poly(poly, V, p, counters=None):
    """Reduce each coordinate modulo g_V in the monomial basis."""
    g = [1]
    for v in sorted(V):
        nxt = [0] * (len(g) + 1)
        for i, c in enumerate(g):
            nxt[i] = (nxt[i] - c * v) % p
            if counters:
                counters.charge("mul", site="setup.indicator_product")
            nxt[i + 1] = (nxt[i + 1] + c) % p
        g = nxt
    cache = {}
    out = SparsePoly(poly.nvars, {})
    for exp, coeff in poly.terms.items():
        pieces = {tuple([0] * poly.nvars): coeff % p}
        for var, power in enumerate(exp):
            key = (var, power)
            if key not in cache:
                c = [0] * (power + 1)
                c[power] = 1
                cache[key] = _one_var_remainder(p, c, g, counters)
            nxt = {}
            for base, bc in pieces.items():
                for d, dc in enumerate(cache[key]):
                    e = list(base)
                    e[var] = d
                    e = tuple(e)
                    nxt[e] = (nxt.get(e, 0) + bc * dc) % p
                    if counters:
                        counters.charge("mul", site="setup.indicator_reduce")
            pieces = nxt
        out = out.add(SparsePoly(poly.nvars, pieces), p)
    return out.clean(p)


def _fp_pow(value, exponent, p, counters=None, site_prefix="fp_pow"):
    result = 1
    base = value % p
    while exponent:
        if exponent & 1:
            result = result * base % p
            if counters:
                counters.charge("mul", site=site_prefix + ".accumulate")
        exponent >>= 1
        if exponent:
            base = base * base % p
            if counters:
                counters.charge("mul", site=site_prefix + ".square")
    return result


def sparse_eval(poly, xs, p, counters=None):
    total = 0
    for exp, coeff in poly.terms.items():
        value = coeff
        for x, e in zip(xs, exp):
            power = _fp_pow(x, e, p, counters)
            value = value * power % p
            if counters:
                counters.charge("mul", site="sparse_eval")
        total = (total + value) % p
    return total


@dataclass
class SparsePoly:
    nvars: int
    terms: dict = field(default_factory=dict)

    def clean(self, p):
        self.terms = {e: c % p for e, c in self.terms.items() if c % p}
        return self

    def copy(self):
        return SparsePoly(self.nvars, dict(self.terms))

    def add(self, other, p, scale=1, counters=None):
        out = dict(self.terms)
        reduced_scale = scale % p
        for e, c in other.terms.items():
            if reduced_scale == 1:
                scaled = c
            elif reduced_scale == p - 1:
                scaled = -c
            else:
                scaled = reduced_scale * c
                if counters:
                    counters.charge("mul", site="SparsePoly.add.scale")
            out[e] = (out.get(e, 0) + scaled) % p
        return SparsePoly(self.nvars, out).clean(p)

    def mul(self, other, p, counters=None):
        out = {}
        for ea, ca in self.terms.items():
            for eb, cb in other.terms.items():
                if counters:
                    counters.charge("mul", site="SparsePoly.mul")
                e = tuple(x + y for x, y in zip(ea, eb))
                out[e] = (out.get(e, 0) + ca * cb) % p
        return SparsePoly(self.nvars, out).clean(p)

    def lead(self):
        return max(self.terms) if self.terms else None

    def monic(self, p, counters=None):
        if not self.terms:
            return self.copy()
        lc = self.terms[self.lead()]
        if lc == 1:
            return self.copy()
        if counters:
            counters.charge("inv", site="SparsePoly.monic.inverse")
            counters.charge("mul", len(self.terms), site="SparsePoly.monic.scale")
        ilc = pow(lc, p - 2, p)
        return SparsePoly(self.nvars, {e: c * ilc % p for e, c in self.terms.items()})


def poly_monomial(nvars, exponent, coeff):
    return SparsePoly(nvars, {tuple(exponent): coeff})


def normal_form(f, basis, p, counters=None):
    f = f.copy().clean(p)
    rem = SparsePoly(f.nvars, {})
    while f.terms:
        lt = f.lead()
        reduced = False
        for g in basis:
            lg = g.lead()
            if lg and all(a >= b for a, b in zip(lt, lg)):
                shift = tuple(a - b for a, b in zip(lt, lg))
                divisor = g.terms[lg]
                if divisor == 1:
                    coeff = f.terms[lt]
                else:
                    if counters:
                        counters.charge("inv", site="normal_form.inverse")
                        counters.charge("mul", site="normal_form.leading_scale")
                    coeff = f.terms[lt] * pow(divisor, p - 2, p) % p
                shifted = SparsePoly(f.nvars, {tuple(a + b for a, b in zip(e, shift)): c
                                                for e, c in g.terms.items()})
                f = f.add(shifted, p, scale=-coeff, counters=counters)
                reduced = True
                if counters:
                    counters.charge("reductions", site="normal_form.reduction")
                break
        if not reduced:
            rem.terms[lt] = f.terms.pop(lt)
    return rem.clean(p)


def s_polynomial(f, g, p, counters=None):
    lf, lg = f.lead(), g.lead()
    lcm = tuple(max(a, b) for a, b in zip(lf, lg))
    sf = tuple(a - b for a, b in zip(lcm, lf))
    sg = tuple(a - b for a, b in zip(lcm, lg))
    cf = f.terms[lf]
    cg = g.terms[lg]
    icf = 1 if cf == 1 else pow(cf, p - 2, p)
    icg = 1 if cg == 1 else pow(cg, p - 2, p)
    if counters:
        if cf != 1:
            counters.charge("inv", site="s_polynomial.f_inverse")
            counters.charge("mul", len(f.terms), site="s_polynomial.f_scale")
        if cg != 1:
            counters.charge("inv", site="s_polynomial.g_inverse")
            counters.charge("mul", len(g.terms), site="s_polynomial.g_scale")
    af = SparsePoly(f.nvars, {
        tuple(a + b for a, b in zip(e, sf)): (c if icf == 1 else c * icf % p)
        for e, c in f.terms.items()
    })
    ag = SparsePoly(g.nvars, {
        tuple(a + b for a, b in zip(e, sg)): (c if icg == 1 else c * icg % p)
        for e, c in g.terms.items()
    })
    return af.add(ag, p, scale=-1, counters=counters)


def _poly_key(poly):
    """Frozen canonical ordering: leading monomial, then coefficient bytes."""
    serial = tuple(sorted(poly.terms.items(), reverse=True))
    return poly.lead(), serial


def _pair_key(pair, basis):
    i, j = pair
    li, lj = basis[i].lead(), basis[j].lead()
    lcm = tuple(max(a, b) for a, b in zip(li, lj))
    return sum(lcm), lcm, i, j


def _product_criterion(f, g):
    return all(min(a, b) == 0 for a, b in zip(f.lead(), g.lead()))


def _interreduce(basis, p, counters=None):
    """Return the canonical reduced lex basis.

    This is deliberately separate from basis construction: the frozen backend
    requires a completed, interreduced lex basis before root extraction.
    """
    work = sorted((g.monic(p, counters) for g in basis if g.terms), key=_poly_key, reverse=True)
    changed = True
    while changed:
        changed = False
        kept = []
        for i, g in enumerate(work):
            lg = g.lead()
            redundant = any(
                j != i
                and all(a >= b for a, b in zip(lg, h.lead()))
                and (lg != h.lead() or j < i)
                for j, h in enumerate(work)
            )
            if redundant:
                changed = True
            else:
                kept.append(g)
        work = kept
        reduced = []
        for i, g in enumerate(work):
            others = work[:i] + work[i + 1:]
            r = normal_form(g, others, p, counters).monic(p, counters)
            if not r.terms:
                changed = True
                continue
            if r.terms != g.terms:
                changed = True
            reduced.append(r)
        work = sorted(reduced, key=_poly_key, reverse=True)
    return work


def buchberger(generators, p, counters=None):
    """Frozen deterministic lex Buchberger with only the product criterion."""
    basis = sorted((g.monic(p, counters) for g in generators if g.terms),
                   key=_poly_key, reverse=True)
    pairs = [(i, j) for i in range(len(basis)) for j in range(i)]
    while pairs:
        pairs.sort(key=lambda pair: _pair_key(pair, basis))
        i, j = pairs.pop(0)
        if _product_criterion(basis[i], basis[j]):
            if counters:
                counters.charge("product_skips", site="buchberger.product_criterion")
            continue
        if counters:
            counters.charge("s_pairs", site="buchberger.s_pair")
        s = s_polynomial(basis[i], basis[j], p, counters)
        ordered_divisors = sorted(basis, key=_poly_key, reverse=True)
        r = normal_form(s, ordered_divisors, p, counters)
        if r.terms:
            r = r.monic(p, counters)
            k = len(basis)
            basis.append(r)
            pairs.extend((k, old) for old in range(k))
    return _interreduce(basis, p, counters)


def indicator_poly(V, var, nvars, p):
    # Product (x_var-v), expanded exactly over F_p.
    return indicator_from_coefficients(indicator_coefficients(V, p), var, nvars)


def _specialise_to_univariate(poly, current, trailing, p, counters=None):
    """Specialise fixed trailing variables and collect a current-var poly.

    ``None`` means the specialised polynomial still involves an earlier
    variable and therefore is not part of this triangular extraction step.
    """
    specialised = {}
    for exp, value in poly.terms.items():
        c = value
        for var, fixed in trailing.items():
            c = c * _fp_pow(fixed, exp[var], p, counters) % p
            if counters:
                counters.charge("mul", site="root_specialisation")
        remaining = tuple(exp[var] for var in range(current + 1))
        specialised[remaining] = (specialised.get(remaining, 0) + c) % p
    specialised = {exp: value for exp, value in specialised.items() if value}
    if any(any(exp[var] for var in range(current)) for exp in specialised):
        return None
    coeff = {}
    for exp, value in specialised.items():
        degree = exp[current]
        coeff[degree] = (coeff.get(degree, 0) + value) % p
    if not coeff:
        return []
    out = [0] * (max(coeff) + 1)
    for degree, value in coeff.items():
        out[degree] = value
    return poly_trim(out)


def extract_lex_roots(basis, generators, V, p, counters=None, indicator=None):
    """Frozen recursive gcd/specialisation extraction from x5 down to x1."""
    roots = sorted(set(int(v) % p for v in V))
    indicator = list(indicator if indicator is not None
                     else indicator_coefficients(roots, p))
    F = Field(p, counters)
    assignments = []

    def visit(current, trailing):
        common = list(indicator)
        found = False
        for poly in basis:
            univariate = _specialise_to_univariate(poly, current, trailing, p, counters)
            if univariate is None or not univariate:
                continue
            found = True
            if len(univariate) == 1:
                return
            common = poly_gcd(F, common, univariate)
            if len(common) <= 1:
                return
        if not found:
            common = list(indicator)
        candidates = [value for value in roots if poly_eval(F, common, value) == 0]
        for value in candidates:
            extended = dict(trailing)
            extended[current] = value
            if current:
                visit(current - 1, extended)
            else:
                xs = tuple(extended[i] for i in range(5))
                if all(sparse_eval(g, xs, p, counters) == 0 for g in generators):
                    assignments.append(xs)

    visit(4, {})
    # The ideal and f6 are symmetric; retain each x-multiset once.
    return sorted(set(tuple(sorted(xs)) for xs in assignments))


def _legendre_sqrt(value, p, counters=None):
    """Deterministic Tonelli-Shanks; factor-base setup, not query work."""
    value %= p
    if value == 0:
        return 0
    if _fp_pow(value, (p - 1) // 2, p, counters,
               site_prefix="setup.sqrt.legendre") != 1:
        raise ValueError("x does not lift to the curve")
    if p % 4 == 3:
        return _fp_pow(value, (p + 1) // 4, p, counters,
                       site_prefix="setup.sqrt.direct")
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while _fp_pow(z, (p - 1) // 2, p, counters,
                  site_prefix="setup.sqrt.nonresidue") != p - 1:
        z += 1
    m = s
    c = _fp_pow(z, q, p, counters, site_prefix="setup.sqrt.c")
    t = _fp_pow(value, q, p, counters, site_prefix="setup.sqrt.t")
    r = _fp_pow(value, (q + 1) // 2, p, counters,
                site_prefix="setup.sqrt.root")
    while t != 1:
        i = 1
        u = _counted_mul(t, t, p, counters, "setup.sqrt.t_square")
        while u != 1:
            u = _counted_mul(u, u, p, counters, "setup.sqrt.square_loop")
            i += 1
        correction = _fp_pow(c, 1 << (m - i - 1), p, counters,
                             site_prefix="setup.sqrt.correction")
        r = _counted_mul(r, correction, p, counters,
                         "setup.sqrt.root_correction")
        correction_square = _counted_mul(
            correction, correction, p, counters, "setup.sqrt.correction_square")
        t = _counted_mul(t, correction_square, p, counters,
                         "setup.sqrt.t_correction_square")
        c, m = correction_square, i
    return r


def _point_add(P, Q, p, a, counters=None):
    if P is None:
        return Q
    if Q is None:
        return P
    if counters:
        counters.charge("point_add", site="signed_recovery.point_add")
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        num, den = (3 * x1 * x1 + a) % p, (2 * y1) % p
    else:
        num, den = (y2 - y1) % p, (x2 - x1) % p
    slope = num * pow(den, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def signed_recovery(fx, candidate_xs, R, counters=None, all_decompositions=True,
                    points=None):
    """Verify algebraic roots by exact signed curve sums."""
    p, a, b = int(fx["p"]), int(fx["a"]), int(fx["b"])
    target = None if R is None else (int(R[0]), int(R[1]))
    neg_target = None if target is None else (target[0], (-target[1]) % p)
    if points is None:
        points = {}
        for x in sorted({x for xs in candidate_xs for x in xs}):
            y = _legendre_sqrt((x ** 3 + a * x + b) % p, p)
            points[x] = (x, min(y, p - y))
    decompositions = []
    for xs in candidate_xs:
        for signs in itertools.product((-1, 1), repeat=5):
            total = None
            for x, sign in zip(xs, signs):
                P = points[x]
                if sign < 0:
                    P = (P[0], (-P[1]) % p)
                total = _point_add(total, P, p, a, counters)
            if total == target or (target is not None and total == neg_target):
                decompositions.append({"xs": list(xs), "signs": list(signs),
                                       "target_sign": 1 if total == target else -1})
                if not all_decompositions:
                    return decompositions
    return decompositions


def g1_membership(fx, V, R, terms_path, setup=None, trace_operations=False):
    """Return an S0 smoke decision using the frozen lex-Buchberger path.

    The root extraction is deliberately performed from the resulting lex
    basis.  It does not construct an O5 sum table and does not receive any
    scalar labels or oracle result.
    """
    p = int(fx["p"])
    xR = None if R is None else int(R[0])
    setup = setup or d2_setup(p, int(fx["a"]), int(fx["b"]), V, terms_path)
    counters = Counters(trace_operations=trace_operations)
    marks = {"start": counters.snapshot()}
    counters.set_component("S")
    f6 = d2_zero_target(setup, counters) if xR is None else d2_specialise(setup, xR, counters)
    marks["S"] = counters.snapshot()
    generators = [f6, *setup["indicator_generators"]]
    counters.set_component("G")
    basis = buchberger(generators, p, counters)
    marks["G"] = counters.snapshot()
    # V is visited only through the per-variable root evaluations prescribed
    # by the frozen recursive gcd extractor.  An all-vanishing branch legally
    # expands through every V candidate (and is charged in X); this is not a
    # direct Cartesian/grid membership substitute.
    counters.set_component("X")
    candidate_xs = extract_lex_roots(
        basis, generators, V, p, counters, indicator=setup["indicator"]
    )
    marks["X"] = counters.snapshot()
    counters.set_component("V")
    decompositions = signed_recovery(
        fx, candidate_xs, R, counters, points=setup["points"]
    )
    marks["V"] = counters.snapshot()
    components = {
        "S": Counters.delta(marks["S"], marks["start"]),
        "G": Counters.delta(marks["G"], marks["S"]),
        "X": Counters.delta(marks["X"], marks["G"]),
        "V": Counters.delta(marks["V"], marks["X"]),
    }
    return {
        "status": "ok", "member": bool(decompositions),
        "candidate_xs": [list(x) for x in candidate_xs],
        "decompositions": decompositions,
        "basis_size": len(basis), "counters": counters.totals(),
        "components": components,
        "operation_events": counters.events if trace_operations else [],
        "f6_terms": len(f6.terms),
    }
