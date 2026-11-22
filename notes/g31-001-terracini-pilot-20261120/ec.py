"""Core arithmetic + secant/embedding machinery for the G31-001 pilot.

Self-contained (reads nothing from the read-only repo). Pure python ints;
sympy only for sqrt_mod / nextprime / isprime / factorint.

Conventions
-----------
E: y^2 = x^3 + a x + b over F_p, p > 3. Identity O = None.
Group law as usual; on the plane cubic, P+Q+R = O  <=>  P,Q,R collinear.

Embeddings by complete linear systems  L(d*O) = {f : div f + d*O >= 0}:
  d=3: (1, x, y)            P^2   (plane cubic)
  d=4: (1, x, y, x^2)       P^3
  d=5: (1, x, y, x^2, xy)   P^4
  d=6: (1, x, y, x^2, xy, y^2) P^5
Pole orders at O: ord_O(1)=0, ord_O(x)=-2, ord_O(y)=-3 (wt x=2, wt y=3).
phi_d(O) = e_{d} = the coordinate of the function of pole order exactly d.

Key dictionary fact used by the tests (genus 1, deg D > 2g-2):
  effective A ~ B  <=>  sum(A) = sum(B) in the group.
  The d+1 points of a hyperplane section of phi_d(E) sum to O.
  Hence hyperplanes through P_1..P_m (m = d-1, scheme sense with tangents
  for repeated points) cut out residual divisor R ~ d*O - sum P_i of degree 1,
  i.e. the single point -sum P_i. Therefore
      phi(-P_1-...-P_m) in span(P_1..P_m with multiplicities)   [exact],
  and containment for a curve point Q outside {P_i} forces Q = -sum P_i.
  For d > m+1 the residual has degree >= 2 and is base-point-free, so a
  curve point is NEVER in the span (dictionary fails).
"""
from __future__ import annotations

import sympy
from sympy.ntheory.residue_ntheory import sqrt_mod

Point = tuple[int, int] | None


class EC:
    def __init__(self, p: int, a: int, b: int):
        a %= p
        b %= p
        assert p > 3
        assert (4 * a * a * a + 27 * b * b) % p != 0, "singular"
        self.p, self.a, self.b = p, a, b

    def on(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, P: Point) -> Point:
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P: Point, Q: Point) -> Point:
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
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1 % p, -1, p) % p
        else:
            lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, k: int, P: Point) -> Point:
        if P is None:
            return None
        if k < 0:
            return self.mul(-k, self.neg(P))
        R: Point = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def order_naive(self) -> int:
        p = self.p
        tot = 1
        e = (p - 1) // 2
        for x in range(p):
            rhs = (x * x * x + self.a * x + self.b) % p
            if rhs == 0:
                tot += 1
            elif pow(rhs, e, p) == 1:
                tot += 2
        return tot

    def order_hasse(self) -> int:
        """Fast exact order for toy sizes: test Hasse candidates on 2 points."""
        import math
        p = self.p
        h = 2 * math.isqrt(p) + 1
        R = None
        for x in range(1, p):
            R = self.lift_x(x)
            if R:
                break
        for t in range(-h, h + 1):
            n = p + 1 - t
            if n > 0 and self.mul(n, R) is None:
                R2 = self.lift_x(p - 1) or R
                if self.mul(n, R2) is None:
                    # double-check with a third random-ish point
                    R3 = self.lift_x(p // 2) or R
                    if self.mul(n, R3) is None:
                        return n
        raise RuntimeError("order_hasse failed")

    def lift_x(self, x: int) -> Point:
        p = self.p
        rhs = (x * x * x + self.a * x + self.b) % p
        if rhs == 0:
            return (x % p, 0)
        if pow(rhs, (p - 1) // 2, p) != 1:
            return None
        y = sqrt_mod(rhs, p)
        return None if y is None else (x % p, int(y))

    def points_x_window(self, N: int) -> list[Point]:
        """All affine points with 0 <= x < N (both signs of y)."""
        out: list[Point] = []
        for x in range(N):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0:
                out.append((x, 0))
            elif pow(rhs, (self.p - 1) // 2, self.p) == 1:
                y = int(sqrt_mod(rhs, self.p))
                out.append((x, y))
                if y != 0:
                    out.append((x, (-y) % self.p))
        return out


# ---------------------------------------------------------------- embeddings
def phi(E: EC, d: int, P: Point) -> list[int]:
    """phi_d(P) in F_p^d.  Coordinates ordered by pole order 0,2,3,4,5,6."""
    if P is None:
        v = [0] * d
        v[d - 1] = 1
        return v
    x, y = P
    p = E.p
    mono = {
        3: [(0, 0), (1, 0), (0, 1)],
        4: [(0, 0), (1, 0), (0, 1), (2, 0)],
        5: [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1)],
        6: [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)],
    }[d]
    return [pow(x, i, p) * pow(y, j, p) % p for (i, j) in mono]


MONOMIALS = {
    3: [(0, 0), (1, 0), (0, 1)],
    4: [(0, 0), (1, 0), (0, 1), (2, 0)],
    5: [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1)],
    6: [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)],
}


def taylor_xy(E: EC, P: Point, K: int) -> tuple[list[int], list[int]]:
    """Exact Taylor series x(t), y(t) mod t^K at P, t a uniformizer.
    y != 0: t = x - x(P);  y == 0: t = y (then x = x0 + O(t^2)).
    Series solved from the curve equation order by order (no closed forms)."""
    p = E.p
    x0, y0 = P
    X = [0] * K
    Y = [0] * K
    if y0 % p != 0:
        X[0] = x0
        if K > 1:
            X[1] = 1  # t = x - x0  =>  x = x0 + t exactly
        # RHS(t) = x^3 + a x + b, a polynomial of degree <= 3 in t
        S = ([(x0 * x0 * x0 + E.a * x0 + E.b) % p,
              (3 * x0 * x0 + E.a) % p, 3 * x0 % p, 1] + [0] * K)[:K]
        # Y = sqrt(S): 2 y0 yk = S[k] - sum_{i+j=k, i,j>0} y_i y_j
        Y[0] = y0
        inv2y0 = pow(2 * y0 % p, -1, p)
        for k in range(1, K):
            acc = S[k]
            for i in range(1, k):
                acc = (acc - Y[i] * Y[k - i]) % p
            Y[k] = acc * inv2y0 % p
    else:
        # t = y; y = t exactly (y0 = 0); x = x0 + sum_{k>=1} x_k t^k, x1 = 0
        X[0] = x0
        fx = (3 * x0 * x0 + E.a) % p  # != 0 since curve smooth and y0 = 0
        for k in range(1, K):
            # X = Xlow + x_k t^k ; coeff of t^k in X^3+aX+b is fx*x_k + known
            Lo = X[:]
            Lo[k] = 0
            C = _series_cubic(E, Lo, K)
            known = (C[k] - (1 if k == 2 else 0)) % p
            X[k] = (-known) * pow(fx, -1, p) % p
        Y = [0] * K
        if K > 1:
            Y[1] = 1
    return X[:K], Y[:K]


def _series_cubic(E: EC, X: list[int], K: int) -> list[int]:
    p = E.p
    X2 = [0] * K
    for i in range(K):
        if X[i]:
            for j in range(K - i):
                if X[j]:
                    X2[i + j] = (X2[i + j] + X[i] * X[j]) % p
    X3 = [0] * K
    for i in range(K):
        if X[i]:
            for j in range(K - i):
                if X2[j]:
                    X3[i + j] = (X3[i + j] + X[i] * X2[j]) % p
    return [(X3[k] + E.a * X[k] + (E.b if k == 0 else 0)) % p for k in range(K)]


def derivs(E: EC, d: int, P: Point, kmax: int) -> list[list[int]]:
    """Local Taylor columns [phi, phi', phi'', ... up to order kmax] at P,
    w.r.t. a uniformizer (x if y != 0, else y).  Multiplicity k of P in a
    decomposition means the containing hyperplane must contain the scheme at
    P, i.e. span{phi(P), phi'(P), ..., phi^(k-1)(P)}; column k holds the
    degree-k Taylor coefficients (a valid projective direction column: what
    matters for containment tests is the span of columns 0..k-1)."""
    p = E.p
    if P is None:
        raise ValueError("O not supported in Taylor columns")
    K = kmax + 1
    X, Y = taylor_xy(E, P, K)
    # series per monomial
    ser: dict[tuple[int, int], list[int]] = {}
    for (i, j) in MONOMIALS[d]:
        s = [1] + [0] * (K - 1)
        for _ in range(i):
            s = _mulmod(s, X, p, K)
        for _ in range(j):
            s = _mulmod(s, Y, p, K)
        ser[(i, j)] = s
    return [[ser[m][k] for m in MONOMIALS[d]] for k in range(K)]


def _mulmod(A: list[int], B: list[int], p: int, K: int) -> list[int]:
    C = [0] * K
    for i in range(K):
        if A[i]:
            for j in range(K - i):
                if B[j]:
                    C[i + j] = (C[i + j] + A[i] * B[j]) % p
    return C


def rank_p(p: int, cols: list[list[int]], extra: list[list[int]] | None = None) -> int:
    mat = [list(c) for c in cols]
    if extra is not None:
        mat.append(list(extra))
    nr = len(mat[0])
    r = 0
    for c in range(nr):
        piv = next((i for i in range(r, len(mat)) if mat[i][c] % p), None)
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        inv = pow(mat[r][c], -1, p)
        mat[r] = [v * inv % p for v in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] % p:
                f = mat[i][c]
                mat[i] = [(a - f * b) % p for a, b in zip(mat[i], mat[r])]
        r += 1
        if r == len(mat):
            break
    return r
