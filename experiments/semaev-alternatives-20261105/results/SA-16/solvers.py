"""Oracle solvers. Each takes an instance dict (p,a,b,xr,B) -- never the planted x1,x2 -- and returns
a list of verified decompositions [(x1,x2)] (verification by group law is done by the caller via verify_decomp).
"""
import math
from fpylll import IntegerMatrix, LLL
from common import *


KMULT = 64


def _rows(M):
    return [[int(M[i, j]) for j in range(M.ncols)] for i in range(M.nrows)]


# ---------------------------------------------------------------- L3: 3-dim form lattice (lat.py style)
def solve_L3(inst):
    p, a, b, xr = inst['p'], inst['a'], inst['b'], inst['xr']
    M = IntegerMatrix(3, 3)
    M[0, 0] = p; M[1, 0] = (-xr) % p; M[1, 1] = 1; M[2, 0] = (-xr * xr) % p; M[2, 2] = 1
    LLL.reduction(M)
    sols = []
    for r in _rows(M):
        for k in range(1, KMULT + 1):   # LLL returns the primitive vector; target may be a small multiple
            sols += recover_from_form(k * r[0], k * r[1], k * r[2], a, b)
            if sols: return sols
    return sols


# ---------------------------------------------------------------- L2: c2=0 sublattice (diagonal-aware)
def solve_L2diag(inst):
    """Assumes x1=x2 (so c2=0).  2-dim lattice {(c0,c1): c0 + c1 xr = 0 mod p}, columns weighted (1,B)."""
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    W = B
    M = IntegerMatrix(2, 2)
    M[0, 0] = p; M[1, 0] = (-xr) % p; M[1, 1] = W
    LLL.reduction(M)
    sols = []
    for r in _rows(M):
        if r[1] % W: continue
        for k in range(1, KMULT + 1):
            sols += recover_from_form(k * r[0], k * (r[1] // W), 0, a, b)
            if sols: return sols
    return sols


# ---------------------------------------------------------------- univariate Coppersmith (diagonal x1=x2)
def solve_cop_uni(inst, m=4, t=4):
    """Howgrave-Graham for F(x)= x^4-2a x^2-8b x+a^2-4 xr (x^3+a x+b) mod p, monic deg 4, root x<=B."""
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    F = [(a * a - 4 * xr * b) % p, (-8 * b - 4 * xr * a) % p, (-2 * a) % p, (-4 * xr) % p, 1]  # low->high
    d = 4
    # powers of F
    pw = [[1]]
    for k in range(1, m + 1):
        prev = pw[-1]
        new = [0] * (len(prev) + d)
        for i, c in enumerate(prev):
            for j, f in enumerate(F):
                new[i + j] += c * f
        pw.append(new)
    n = d * m + t
    polys = []
    for u in range(m):
        for v in range(d):
            polys.append((u, v, m - u))
    for v in range(t):
        polys.append((m, v, 0))
    M = IntegerMatrix(n, n)
    for r, (u, v, e) in enumerate(polys):
        coeff = [c * p ** e for c in pw[u]]
        for i, c in enumerate(coeff):
            if i + v < n:
                M[r, i + v] = c * B ** (i + v)
    LLL.reduction(M)
    sols = []
    rows = _rows(M)
    for r in rows[:3]:
        coeffs = []
        ok = True
        for j, c in enumerate(r):
            if c % B ** j: ok = False; break
            coeffs.append(c // B ** j)
        if not ok: continue
        if all(c == 0 for c in coeffs): continue
        poly = pari('Pol(%s)' % str([int(c) for c in reversed(coeffs)]).replace(' ', ''))
        if poly.poldegree() < 1: continue
        for rt in pari.nfroots(None, poly):
            x = int(rt)
            if 1 <= x <= B:
                sols.append((x, x))
        if sols: break
    return sols


# ---------------------------------------------------------------- bivariate Coppersmith on S_3(x1,x2,xr) mod p
def _polymul(A, Bp, mod=None):
    out = {}
    for (i, j), c in A.items():
        for (k, l), d in Bp.items():
            out[(i + k, j + l)] = out.get((i + k, j + l), 0) + c * d
    return out


def build_biv_lattice(S, p, B, m, s):
    """Coron-style: monomials [0,2m+s]^2; each monomial (a,b) gets k=min(m,a//2,b//2), poly x1^(a-2k) x2^(b-2k) S^k p^(m-k)."""
    N = 2 * m + s
    pw = [{(0, 0): 1}]
    for k in range(1, m + 1):
        pw.append(_polymul(pw[-1], S))
    mons = [(i, j) for i in range(N + 1) for j in range(N + 1)]
    idx = {mm: r for r, mm in enumerate(mons)}
    n = len(mons)
    M = IntegerMatrix(n, n)
    for r, (i, j) in enumerate(mons):
        k = min(m, i // 2, j // 2)
        sh = (i - 2 * k, j - 2 * k)
        for (u, v), c in pw[k].items():
            col = idx[(u + sh[0], v + sh[1])]
            M[r, col] = (c * p ** (m - k)) * B ** (u + sh[0] + v + sh[1])
    return M, mons



def _extract_pairs(polys, B, maxpairs=40):
    """try resultants of pairs among the shortest reduced polynomials; return verified-candidate (x1,x2) list."""
    import itertools
    def tostr(d):
        return '+'.join('(%d)*x^%d*y^%d' % (c, i, j) for (i, j), c in d.items())
    sols = []
    pp = [pari(tostr(d)) for d in polys]
    n = 0
    for i, j in itertools.combinations(range(len(pp)), 2):
        if n >= maxpairs: break
        n += 1
        try:
            res = pari.polresultant(pp[i], pp[j], pari('y'))
            if res == 0: continue
            for rt in pari.nfroots(None, res):
                x1 = int(rt)
                if 1 <= x1 <= B:
                    g = pari.gcd(pari.subst(pp[i], 'x', x1), pari.subst(pp[j], 'x', x1))
                    if g.poldegree() >= 1:
                        for r2 in pari.nfroots(None, g):
                            x2 = int(r2)
                            if 1 <= x2 <= B: sols.append((x1, x2))
            if sols: return sols
        except Exception:
            continue
    return sols

def solve_cop_biv(inst, m=1, s=0, nvec=2, S=None, rad=False, extract=True):
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    S = S if S is not None else S3_bivariate(xr, a, b, p)
    M, mons = build_biv_lattice(S, p, B, m, s)
    LLL.reduction(M)
    rows = _rows(M)
    polys = []
    for r in rows[:nvec + 7]:
        d = {}
        ok = True
        for (i, j), c in zip(mons, r):
            if c == 0: continue
            if c % (B ** (i + j)): ok = False; break
            d[(i, j)] = c // B ** (i + j)
        if ok and d: polys.append(d)
    inst['_polys'] = polys  # exposed for the harness (vanishing check at planted root)
    if not extract:
        return []
    if len(polys) < 2: return []
    return _extract_pairs(polys, B)


def radical_poly(inst):
    """bilinear radical g = (x1-xr)(x2-xr) - (3xr^2+a) for the degenerate case f(xr)=0 (S_3 = g^2).
    Returned as dict mod p; the solver is told f(xr)=0 (that IS the degenerate family definition)."""
    p, a, xr = inst['p'], inst['a'], inst['xr']
    return {(1, 1): 1, (1, 0): (-xr) % p, (0, 1): (-xr) % p, (0, 0): (xr * xr - 3 * xr * xr - a) % p}


def solve_cop_biv_rad(inst, m=1, s=0, nvec=2):
    """Coppersmith on the radical bilinear form (degree 1 in each variable): rewrite lattice with N=m+s."""
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    g = radical_poly(inst)
    # leading monomial x1 x2 ; Coron-style with degree-1 box: k=min(m,a,b)
    N = m + s
    pw = [{(0, 0): 1}]
    for k in range(1, m + 1):
        pw.append(_polymul(pw[-1], g))
    mons = [(i, j) for i in range(N + 1) for j in range(N + 1)]
    idx = {mm: r for r, mm in enumerate(mons)}
    n = len(mons)
    M = IntegerMatrix(n, n)
    for r, (i, j) in enumerate(mons):
        k = min(m, i, j)
        sh = (i - k, j - k)
        for (u, v), c in pw[k].items():
            col = idx[(u + sh[0], v + sh[1])]
            M[r, col] = (c * p ** (m - k)) * B ** (u + sh[0] + v + sh[1])
    LLL.reduction(M)
    rows = _rows(M)
    polys = []
    for r in rows[:nvec + 7]:
        d = {}; ok = True
        for (i, j), c in zip(mons, r):
            if c == 0: continue
            if c % (B ** (i + j)): ok = False; break
            d[(i, j)] = c // B ** (i + j)
        if ok and d: polys.append(d)
    inst['_polys'] = polys
    if len(polys) < 2: return []
    return _extract_pairs(polys, B)


# ---------------------------------------------------------------- Vieta-plane CVP (Cornacchia/Gauss analogue), conic degenerate
def solve_vieta_cvp(inst):
    """Degenerate conic: S_3 = (e2 - xr e1 - (a+2xr^2))^2 when f(xr)=0.  Find small (e1,e2) with
    e2 = xr e1 + k mod p (2-dim CVP, Gauss/Babai), then x1,x2 = roots of z^2-e1 z+e2."""
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    k = (a + 2 * xr * xr) % p
    W = B
    M = IntegerMatrix(2, 2)
    M[0, 0] = W; M[0, 1] = xr % p      # e1 = 1
    M[1, 0] = 0; M[1, 1] = p
    LLL.reduction(M)
    t = (0, (-k) % p)
    # Babai rounding in the reduced basis, then local search +-3 around the rounded coefficients
    bas = _rows(M)
    # solve coefficients by real linear algebra (2x2) with exact fractions
    from fractions import Fraction
    (a11, a12), (a21, a22) = bas
    det = a11 * a22 - a12 * a21
    # t = c1*bas0 + c2*bas1  => c = t * inv(Bmat)
    c1 = Fraction(t[0] * a22 - t[1] * a21, det)
    c2 = Fraction(-t[0] * a12 + t[1] * a11, det)
    f1, f2 = round(c1), round(c2)
    sols = []
    for d1 in range(-3, 4):
        for d2 in range(-3, 4):
            n1, n2 = f1 + d1, f2 + d2
            vx = n1 * a11 + n2 * a21 - t[0]
            vy = n1 * a12 + n2 * a22 - t[1]
            if vx % W: continue
            e1 = vx // W
            e2 = vy
            if e1 <= 0 or e2 <= 0: continue
            if e1 > 2 * B or e2 > B * B: continue
            disc = e1 * e1 - 4 * e2
            r = isqrt_exact(disc)
            if r is None or (e1 + r) % 2: continue
            x1 = (e1 + r) // 2; x2 = (e1 - r) // 2
            if x2 >= 1:
                sols.append((x1, x2))
    return sols


# ---------------------------------------------------------------- baselines
def solve_enum(inst):
    """brute force over x1<=B using doubling (diagonal) or pairs?  For null/exponent check: scan x in [1,B],
    test whether [2]P_x has x-coordinate xr (cost ~B group doublings)."""
    p, a, b, xr, B = inst['p'], inst['a'], inst['b'], inst['xr'], inst['B']
    for x in range(1, B + 1):
        P = point(x, a, b, p)
        if P is None: continue
        D = add(P, P, a, p)
        if D is not None and D[0] == xr:
            return [(x, x)]
    return []


# ---------------------------------------------------------------- Smart attack on anomalous curve
def _padd(P, Q, mod):
    X1, Y1, Z1 = P; X2, Y2, Z2 = Q
    u = (Y2 * Z1 - Y1 * Z2) % mod; v = (X2 * Z1 - X1 * Z2) % mod
    w = (u * u * Z1 * Z2 - v ** 3 - 2 * v * v * X1 * Z2) % mod
    return (v * w % mod, (u * (v * v * X1 * Z2 - w) - v ** 3 * Y1 * Z2) % mod, v ** 3 * Z1 * Z2 % mod)


def _pdbl(P, a, mod):
    X, Y, Z = P
    w = (a * Z * Z + 3 * X * X) % mod
    s = Y * Z % mod
    B_ = X * Y * s % mod
    h = (w * w - 8 * B_) % mod
    return (2 * h * s % mod, (w * (4 * B_ - h) - 8 * Y * Y * s * s) % mod, 8 * s ** 3 % mod)


def _pmul(k, P, a, mod):
    R = P
    for bit in bin(k)[3:]:
        R = _pdbl(R, a, mod)
        if bit == '1':
            R = _padd(R, P, mod)
    return R


def smart_psi(P, a, b, p, r=12345):
    """psi(P) = (X/Y of [p]P~) / p mod p  (Smart's p-adic elliptic log, up to a common factor)."""
    mod = p * p
    x, y = P
    # NON-canonical lift of the curve: j=0 curves lift canonically for any b, so lift a as well
    a = (a + p * r) % mod
    b = (b + p * (r + 7)) % mod
    y2 = (y + ((f_of(x, a, b, mod) - y * y) // p) * pow(2 * y, -1, p) * p) % mod
    assert (y2 * y2 - f_of(x, a, b, mod)) % mod == 0
    X, Y, Z = _pmul(p, (x, y2, 1), a, mod)
    assert Z % p == 0 and Y % p != 0, 'not anomalous / bad lift'
    t = (-X * pow(Y, -1, mod)) % mod
    assert t % p == 0
    return (t // p) % p
