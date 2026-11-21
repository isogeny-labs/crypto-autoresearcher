"""Shared helpers for WP1 (G31-004): Semaev summation-polynomial census.

Field/curve helpers only -- no summation polynomials here.  Provides:
  * F_p square root + quadratic-character helpers
  * F_{p^2} = F_p[w]/(w^2 - ns) arithmetic (ns = a fixed non-residue),
    so that every x in F_p has its curve "lifts" y with y^2 = x^3+ax+b
    represented inside F_{p^2}  (residue -> y in F_p, non-residue -> y in w*F_p)
  * Elliptic-curve arithmetic over K = F_{p^2} for points given as
    (x, y) with x, y in K (tuples); None denotes the point at infinity O.

All arithmetic is plain Python integers; deliberately simple and auditable.
"""
from __future__ import annotations


# ---------------------------------------------------------------- F_p basics
def sqrt_mod_p(a: int, p: int) -> int | None:
    """Square root of a mod p (p odd prime), or None if non-residue."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    # Tonelli-Shanks (small p here; keep dependency-free)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        bb = b * b % p
        m, c, t, r = i, bb, t * bb % p, r * b % p
    return r


def nonsquare(p: int) -> int:
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    return z


# ------------------------------------------------------------------ F_{p^2}
# element: tuple (u, v) meaning u + v*w with w^2 = ns (fixed nonsquare mod p).
class Fp2:
    __slots__ = ("p", "ns")

    def __init__(self, p: int):
        self.p = p
        self.ns = nonsquare(p)

    def from_int(self, a: int):
        return (a % self.p, 0)

    def eq(self, x, y):
        return x[0] == y[0] and x[1] == y[1]

    def add(self, x, y):
        p = self.p
        return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)

    def sub(self, x, y):
        p = self.p
        return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)

    def neg(self, x):
        p = self.p
        return ((-x[0]) % p, (-x[1]) % p)

    def mul(self, x, y):
        p, ns = self.p, self.ns
        return ((x[0] * y[0] + ns * x[1] * y[1]) % p,
                (x[0] * y[1] + x[1] * y[0]) % p)

    def inv(self, x):
        p, ns = self.p, self.ns
        assert (x[0], x[1]) != (0, 0), "inverse of zero"
        n = pow((x[0] * x[0] - ns * x[1] * x[1]) % p, -1, p)
        return (x[0] * n % p, (-x[1]) * n % p)

    def is_zero(self, x):
        return x[0] == 0 and x[1] == 0

    def in_base(self, x):
        return x[1] == 0


# ------------------------------------------------- curve over K = F_{p^2}
class CurveK:
    """y^2 = x^3 + a x + b over K = F_{p^2}.  Points: None (O) or (x, y)
    with x, y in K (tuples).  a, b are embedded into K from F_p."""

    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p
        self.K = Fp2(p)
        assert (4 * self.a ** 3 + 27 * self.b ** 2) % p != 0, "singular curve"

    # --- curve RHS and lifts over K -------------------------------------
    def f(self, x: int) -> int:
        """f(x) in F_p for x in F_p."""
        return (x * x * x + self.a * x + self.b) % self.p

    def lift_ys(self, x: int):
        """All y in K with y^2 = f(x) (length 1 if f(x)=0, else 2)."""
        fx = self.f(x)
        r = sqrt_mod_p(fx, self.p)
        if r is not None:
            return [(r, 0)] if r == 0 else [(r, 0), ((-r) % self.p, 0)]
        # fx non-residue: y = v*w with v^2 = fx/ns (ratio of non-residues)
        v = sqrt_mod_p(fx * pow(self.K.ns, -1, self.p), self.p)
        assert v is not None and v != 0
        return [(0, v), (0, (-v) % self.p)]

    def on_base_x(self, x: int) -> bool:
        """True iff some F_p-point of E has x-coordinate x."""
        return sqrt_mod_p(self.f(x), self.p) is not None

    # --- arithmetic over K (x, y general elements of K) ------------------
    def double(self, P):
        if P is None:
            return None
        K, a = self.K, self.a
        x, y = P
        assert not K.is_zero(y), "cannot double a 2-torsion point -> O"
        l = K.mul(K.inv(K.mul(K.from_int(2), y)),
                  K.add(K.mul(K.from_int(3), K.mul(x, x)), K.from_int(a)))
        x3 = K.sub(K.mul(l, l), K.mul(K.from_int(2), x))
        y3 = K.sub(K.mul(l, K.sub(x, x3)), y)
        return (x3, y3)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        K = self.K
        (x1, y1), (x2, y2) = P, Q
        if K.eq(x1, x2):
            if K.is_zero(K.add(y1, y2)):
                return None
            return self.double(P)
        l = K.mul(K.sub(y2, y1), K.inv(K.sub(x2, x1)))
        x3 = K.sub(K.sub(K.mul(l, l), x1), x2)
        y3 = K.sub(K.mul(l, K.sub(x1, x3)), y1)
        return (x3, y3)

    def neg(self, P):
        if P is None:
            return None
        return (P[0], self.K.neg(P[1]))
