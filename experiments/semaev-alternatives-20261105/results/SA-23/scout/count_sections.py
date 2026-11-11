#!/usr/bin/env python3
"""Scout for SA-23: count integral sections of the elliptic surface
    y^2 = x^3 + t^d + 1   over F_p(t),   6 | d,  chi = d/6,
i.e. X in F_p[t] with deg X <= 2 chi such that X^3 + t^d + 1 is a square in F_p[t].
Brute force over all X (p^(2chi+1) candidates), pure Python, for small p.
Then the height pairing <P,Q> = chi + P.O + Q.O - P.Q (all fibres irreducible when 6|d)
gives the Gram matrix; rank and determinant of the lattice they generate.
Usage: count_sections.py p d
"""
import sys, itertools, json, time
from fractions import Fraction

p = int(sys.argv[1]); d = int(sys.argv[2]); assert d % 6 == 0
chi = d // 6; degX = 2 * chi; degY = 3 * chi

def polmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % p
    return r

def poladd(a, b):
    n = max(len(a), len(b)); r = [0] * n
    for i, x in enumerate(a): r[i] = x
    for i, x in enumerate(b): r[i] = (r[i] + x) % p
    return r

def trim(a):
    while len(a) > 1 and a[-1] == 0: a = a[:-1]
    return a

sq = {}
for u in range(p): sq.setdefault(u * u % p, u)

def polsqrt(g, degh_unused=None):
    """h with h^2 = g (lists mod p). None if g is not a square."""
    g = trim(list(g))
    if g == [0]: return [0]
    dg = len(g) - 1
    if dg % 2: return None
    n = dg // 2
    if g[dg] not in sq: return None
    h = [0] * (n + 1)
    h[n] = sq[g[dg]]
    if h[n] == 0: return None
    inv = pow(2 * h[n], p - 2, p)
    for k in range(n - 1, -1, -1):
        s = 0
        for i in range(k + 1, n):
            j = n + k - i
            if k < j < n: s = (s + h[i] * h[j]) % p
        h[k] = ((g[n + k] - s) * inv) % p
    hh = polmul(h, h)
    hh = hh + [0] * (len(g) - len(hh))
    if any((hh[i] - g[i]) % p for i in range(len(g))): return None
    return h

def polsqrt_generic(g):
    return None  # leading coefficient zero never happens here: deg g = 3*degX = d exactly? no: X^3 + t^d + 1 has degree max(3 deg X, d) = d when deg X <= 2chi

t0 = time.time()
base = [1] + [0] * (d - 1) + [1]  # t^d + 1
sections = []
for coeffs in itertools.product(range(p), repeat=degX + 1):
    X = list(coeffs)
    X3 = polmul(polmul(X, X), X)
    g = poladd(X3, base)
    h = polsqrt(g)
    if h is None: continue
    # verify
    sections.append((X, h)); sections.append((X, [(-c) % p for c in h]))
S = len(sections)
print(json.dumps({"p": p, "d": d, "chi": chi, "num_integral_sections": S, "enum_seconds": round(time.time() - t0, 1)}))

# height pairing. P.Q = sum over t in P^1 of intersection multiplicity of the two sections.
# Affine part: common zeros of (X_P - X_Q, Y_P - Y_Q): multiplicity = min of valuations? For two
# curves meeting on a smooth surface, use ord_t gcd of (X_P - X_Q) and (Y_P - Y_Q) at each t over Fpbar:
# I(P,Q)_t = min(ord_t(X_P-X_Q), ord_t(Y_P-Y_Q)) is correct when the fibre is smooth at the point and
# the sections are transversal to the fibre (they are, being sections). Total = deg gcd(XP-XQ, YP-YQ).
# At infinity: use chart s=1/t, X' = s^(2chi) X, Y' = s^(3chi) Y; same recipe at s = 0.
def polsub(a, b): return trim(poladd(a, [(-c) % p for c in b]))

def polmod(a, b):
    a = trim(list(a)); b = trim(list(b))
    if len(b) == 1 and b[0] == 0: raise ZeroDivisionError
    inv = pow(b[-1], p - 2, p)
    while len(a) >= len(b) and not (len(a) == 1 and a[0] == 0):
        c = a[-1] * inv % p; sh = len(a) - len(b)
        for i in range(len(b)): a[sh + i] = (a[sh + i] - c * b[i]) % p
        a = trim(a)
    return a

def polgcd(a, b):
    a = trim(list(a)); b = trim(list(b))
    while not (len(b) == 1 and b[0] == 0):
        a, b = b, polmod(a, b)
    return a

def degree(a):
    a = trim(list(a)); return -1 if a == [0] else len(a) - 1

def inter(P, Q):
    XP, YP = P; XQ, YQ = Q
    dx = polsub(XP, XQ); dy = polsub(YP, YQ)
    if degree(dx) < 0 and degree(dy) < 0: return None  # same section
    aff = degree(polgcd(dx, dy)) if degree(dx) >= 0 and degree(dy) >= 0 else (degree(dx) if degree(dy) < 0 else degree(dy))
    # at infinity: ord_s of s^(2chi)(X_P - X_Q)(1/s) = 2chi - deg(dx) (if dx != 0), similarly 3chi - deg(dy)
    ox = (2 * chi - degree(dx)) if degree(dx) >= 0 else 10 ** 9
    oy = (3 * chi - degree(dy)) if degree(dy) >= 0 else 10 ** 9
    inf = min(ox, oy)
    return aff + inf

if S <= 400:
    # Gram matrix, rank, and determinant of the lattice spanned (via integer row reduction of Gram over Q)
    import sympy
    n = S
    G = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            if i == j: G[i][j] = chi  # <P,P> = 2chi + 2 P.O - 0 ... with P.O = 0: height = 2chi? see note
            else: G[i][j] = G[j][i] = chi - inter(sections[i], sections[j])
    # NOTE: <P,P> = 2chi + 2(P.O) - sum contr = 2chi for integral sections (all fibres irreducible).
    for i in range(n): G[i][i] = 2 * chi
    M = sympy.Matrix(G)
    r = M.rank()
    print(json.dumps({"gram_rank": r, "expected_rank_bound": 12 * chi - 4}))
    # lattice det: pick r independent sections greedily, compute det of their Gram, then reduce by index found via LLL-free approach: report Gram det of greedy basis only.
    idx = []
    for i in range(n):
        if sympy.Matrix([[G[a][b] for b in idx + [i]] for a in idx + [i]]).rank() == len(idx) + 1:
            idx.append(i)
        if len(idx) == r: break
    Gb = sympy.Matrix([[G[a][b] for b in idx] for a in idx])
    print(json.dumps({"greedy_basis_gram_det": str(Gb.det()), "min_height": 2 * chi}))
