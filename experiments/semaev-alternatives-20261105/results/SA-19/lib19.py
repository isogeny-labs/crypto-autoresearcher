"""SA-19 library: degree budget of relation polynomials for the form lattice.

Conventions (SA-13 / SA-17): a relation F = sum_l c_l(x) M_l(R) (M_l functions of the target R, c_l polynomials in
the small unknowns x = (x_1..x_m)) has coefficient space W = span_k(c_l).  Budget w(W) = sum of the degree sequence
of W (basis invariant).  With r independent congruences mod p on the same vector (r = dim W cap (S_R), S_R the
Semaev polynomial of the target), the form lattice has index p^r and predicted reach delta < r / w.
All symbolic ranks are computed modulo PR = 2^31-1 at random specialisations (generic rank w.h.p.), with a second
prime check available.  Lattice experiments use exact integers and fpylll.
"""
import random, math, itertools
import numpy as np

PR = (1 << 31) - 1          # 2^31-1, prime, = 3 mod 4

# ---------------------------------------------------------------- polynomials as dicts {exp tuple: coeff mod p}
def padd(a, b, p):
    r = dict(a)
    for k, v in b.items():
        r[k] = (r.get(k, 0) + v) % p
    return {k: v for k, v in r.items() if v}

def pscale(a, c, p):
    return {k: (v * c) % p for k, v in a.items() if (v * c) % p}

def pmul(a, b, p):
    r = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = tuple(i + j for i, j in zip(ka, kb))
            r[k] = (r.get(k, 0) + va * vb) % p
    return {k: v for k, v in r.items() if v}

def ppow(a, e, p, nv):
    r = {(0,) * nv: 1}
    for _ in range(e):
        r = pmul(r, a, p)
    return r

def pdeg(a):
    return max((sum(k) for k in a), default=-1)

def peval(a, pt, p):
    s = 0
    for k, v in a.items():
        t = v
        for e, x in zip(k, pt):
            if e:
                t = t * pow(x, e, p) % p
        s = (s + t) % p
    return s

def coeffs_in_last(a, nv):
    """split polynomial in nv variables by powers of the last variable: list of polys in the first nv-1 variables."""
    d = max((k[-1] for k in a), default=-1)
    out = [dict() for _ in range(d + 1)]
    for k, v in a.items():
        out[k[-1]][k[:-1]] = v
    return out

# ---------------------------------------------------------------- Semaev S3 / S4 over F_p
def S3_poly(a, b, p, nv=3):
    """S3(x1,x2,X) as a dict in nv>=3 variables (x1,x2,X,...), remaining exponents 0."""
    z = (0,) * (nv - 3)
    x1 = {(1, 0, 0) + z: 1}; x2 = {(0, 1, 0) + z: 1}; X = {(0, 0, 1) + z: 1}
    one = {(0, 0, 0) + z: 1}
    ca = pscale(one, a % p, p); cb = pscale(one, b % p, p)
    e1 = padd(x1, x2, p); e2 = pmul(x1, x2, p)
    d = padd(x1, pscale(x2, -1, p), p)
    A = pmul(d, d, p)
    B = pscale(padd(pmul(e1, padd(e2, ca, p), p), pscale(cb, 2, p), p), -2, p)
    u = padd(e2, pscale(ca, -1, p), p)
    C = padd(pmul(u, u, p), pscale(pmul(e1, cb, p), -4, p), p)
    return padd(padd(pmul(A, pmul(X, X, p), p), pmul(B, X, p), p), C, p)

# ---------------------------------------------------------------- linear algebra mod p (python ints, small) and numpy (large)
def rref_mod(rows, p):
    """row-reduce list of lists mod p; returns (rref rows (nonzero), pivot columns)."""
    rows = [r[:] for r in rows]; piv = []; rk = 0
    ncols = len(rows[0]) if rows else 0
    for c in range(ncols):
        pr = None
        for i in range(rk, len(rows)):
            if rows[i][c] % p:
                pr = i; break
        if pr is None:
            continue
        rows[rk], rows[pr] = rows[pr], rows[rk]
        inv = pow(rows[rk][c], -1, p)
        rows[rk] = [x * inv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk])]
        piv.append(c); rk += 1
        if rk == len(rows):
            break
    return rows[:rk], piv

def rank_mod(rows, p):
    return len(rref_mod(rows, p)[0]) if rows else 0

def nullspace_mod(rows, p):
    """right nullspace basis of the matrix (rows) mod p: vectors v with rows . v = 0."""
    if not rows:
        return []
    ncols = len(rows[0])
    R, piv = rref_mod(rows, p)
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = [0] * ncols; v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-R[i][f]) % p
        basis.append(v)
    return basis

def np_rref_mod(M, p):
    """numpy vectorised row reduction mod p (p < 2^31); returns (R, pivots) with R int64 array."""
    M = M.astype(np.int64) % p
    nr, nc = M.shape; piv = []; rk = 0
    for c in range(nc):
        if rk >= nr:
            break
        nz = np.nonzero(M[rk:, c])[0]
        if len(nz) == 0:
            continue
        i = rk + nz[0]
        if i != rk:
            M[[rk, i]] = M[[i, rk]]
        inv = pow(int(M[rk, c]), -1, p)
        M[rk] = (M[rk] * inv) % p
        col = M[:, c].copy(); col[rk] = 0
        nzr = np.nonzero(col)[0]
        if len(nzr):
            M[nzr] = (M[nzr] - np.outer(col[nzr], M[rk]) % p) % p
        piv.append(c); rk += 1
    return M[:rk], piv

def np_nullspace_mod(M, p):
    R, piv = np_rref_mod(M, p)
    nc = M.shape[1]
    free = [c for c in range(nc) if c not in set(piv)]
    out = []
    for f in free:
        v = np.zeros(nc, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-int(R[i, f])) % p
        out.append(v)
    return out

# ---------------------------------------------------------------- degree sequence / budget
def monomial_list(polys):
    mons = sorted({k for q in polys for k in q}, key=lambda m: (sum(m), m))
    return mons

def degree_sequence(polys, p=PR, weights=None):
    """degree sequence of span(polys) w.r.t. (weighted) total degree.  Returns (dim, sorted list of degrees)."""
    polys = [q for q in polys if q]
    if not polys:
        return 0, []
    mons = monomial_list(polys)
    wdeg = (lambda m: sum(m)) if weights is None else (lambda m: sum(e * w for e, w in zip(m, weights)))
    idx = {m: i for i, m in enumerate(mons)}
    rows = []
    for q in polys:
        r = [0] * len(mons)
        for k, v in q.items():
            r[idx[k]] = v % p
        rows.append(r)
    R, piv = rref_mod(rows, p); n = len(R)
    degs = sorted({wdeg(m) for m in mons})
    seq = []; prev = 0
    for d in degs:
        cols = [i for i, m in enumerate(mons) if wdeg(m) > d]
        if cols:
            rk = rank_mod([[r[i] for i in cols] for r in R], p)
        else:
            rk = 0
        cd = n - rk
        seq += [d] * (cd - prev); prev = cd
    return n, seq

def budget(polys, p=PR, weights=None):
    n, seq = degree_sequence(polys, p, weights)
    return n, seq, sum(seq)

def xside_span(F, nv_x, p=PR):
    """x-side coefficient polynomials of F (dict in nv_x + k variables): coefficients of each monomial in the
    trailing k variables (the target functions).  Returns list of polys in nv_x variables."""
    out = {}
    for k, v in F.items():
        kx, kr = k[:nv_x], k[nv_x:]
        out.setdefault(kr, {})[kx] = v
    return list(out.values())

def monomials_upto(nv, d):
    return [m for m in itertools.product(range(d + 1), repeat=nv) if sum(m) <= d]

def r_of_W(W, S_R, p=PR, nv=2):
    """r = dim { H in k[x]_{<= dmax-4} : H * S_R in span(W) }, S_R a polynomial in the x variables only (target
    specialised).  Returns r (and the list of (mu, -h) kernel vectors if wanted)."""
    dW = max(pdeg(q) for q in W); dS = pdeg(S_R)
    if dW < dS:
        return 0
    Hm = monomials_upto(nv, dW - dS)
    mults = [pmul({m: 1}, S_R, p) for m in Hm]
    mons = monomial_list(W + mults); idx = {m: i for i, m in enumerate(mons)}
    def vec(q):
        r = [0] * len(mons)
        for k, v in q.items():
            r[idx[k]] = v % p
        return r
    rows = [vec(q) for q in W] + [vec(q) for q in mults]
    rk = rank_mod(rows, p)
    dimW = rank_mod([vec(q) for q in W], p)
    return dimW + len(Hm) - rk

def kernel_vectors(W, S_R, p, nv=2):
    """integer-mod-p kernel: vectors mu in (Z/p)^n with sum mu_l W_l in (S_R); returns list of mu (length n)."""
    dW = max(pdeg(q) for q in W); dS = pdeg(S_R)
    Hm = monomials_upto(nv, dW - dS) if dW >= dS else []
    mults = [pmul({m: 1}, S_R, p) for m in Hm]
    mons = monomial_list(W + mults); idx = {m: i for i, m in enumerate(mons)}
    def vec(q):
        r = [0] * len(mons)
        for k, v in q.items():
            r[idx[k]] = v % p
        return r
    cols = [vec(q) for q in W] + [vec(q) for q in mults]       # matrix with columns = polys; we need left kernel
    # transpose: rows = monomials, columns = polys; nullspace gives (mu, -h)
    M = [[cols[j][i] for j in range(len(cols))] for i in range(len(mons))]
    ns = nullspace_mod(M, p)
    return [v[:len(W)] for v in ns if any(v[:len(W)])]

# ---------------------------------------------------------------- elliptic curves over F_p (short Weierstrass) in python
def sqrt_mod(a, p):
    a %= p
    if a == 0:
        return 0
    if p % 4 == 3:
        r = pow(a, (p + 1) // 4, p)
        return r if r * r % p == a else None
    # Tonelli-Shanks
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

class Curve:
    """y^2 = x^3 + a2 x^2 + a4 x + a6 over F_p (a2 = 0 gives short Weierstrass)."""
    def __init__(self, a, b, p, a2=0):
        self.a, self.b, self.p, self.a2 = a % p, b % p, p, a2 % p
    def f(self, x):
        p = self.p
        return (pow(x, 3, p) + self.a2 * x * x + self.a * x + self.b) % p
    def lift_x(self, x):
        y = sqrt_mod(self.f(x), self.p)
        return None if y is None else (x % self.p, y)
    def on(self, P):
        return P is None or (P[1] * P[1] - self.f(P[0])) % self.p == 0
    def add(self, P, Q):
        p = self.p
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0:
                return None
            lam = (3 * P[0] * P[0] + 2 * self.a2 * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x3 = (lam * lam - self.a2 - P[0] - Q[0]) % p
        return (x3, (lam * (P[0] - x3) - P[1]) % p)
    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)
    def mul(self, k, P):
        R = None
        while k:
            if k & 1: R = self.add(R, P)
            P = self.add(P, P); k >>= 1
        return R
    def random_point(self, rng):
        while True:
            P = self.lift_x(rng.randrange(self.p))
            if P:
                return P if rng.random() < 0.5 else self.neg(P)
    def random_small(self, B, rng):
        while True:
            P = self.lift_x(rng.randrange(1, B + 1))
            if P:
                return P if rng.random() < 0.5 else self.neg(P)

# ---------------------------------------------------------------- summation polynomial of an arbitrary coordinate by interpolation
def summation_poly(E, phi, dmax, rng, p=PR, nsamp_extra=40, symmetric=True):
    """minimal polynomial S^phi(u1,u2,u3) with u_i = phi(P_i), P1+P2+P3 = O, degree <= dmax in each variable.
    phi: function (x,y) -> value mod p or None (pole).  Returns dict poly in 3 variables or None if no relation."""
    mons = [m for m in itertools.product(range(dmax + 1), repeat=3)]
    samples = []
    while len(samples) < len(mons) + nsamp_extra:
        P1, P2 = E.random_point(rng), E.random_point(rng)
        P3 = E.neg(E.add(P1, P2))
        if P3 is None or P1[0] == P2[0]:
            continue
        u = [phi(*P) for P in (P1, P2, P3)]
        if any(v is None for v in u):
            continue
        samples.append(u)
    M = np.zeros((len(samples), len(mons)), dtype=np.int64)
    pw = [[[pow(u[i], e, p) for e in range(dmax + 1)] for i in range(3)] for u in samples]
    for j, m in enumerate(mons):
        M[:, j] = [pw[s][0][m[0]] * pw[s][1][m[1]] % p * pw[s][2][m[2]] % p for s in range(len(samples))]
    ns = np_nullspace_mod(M, p)
    if not ns:
        return None
    polys = [{mons[j]: int(v[j]) for j in range(len(mons)) if v[j]} for v in ns]
    return polys

def minimal_summation_poly(E, phi, rng, p=PR, dstart=1, dmaxmax=9):
    for d in range(dstart, dmaxmax + 1):
        polys = summation_poly(E, phi, d, rng, p)
        if polys:
            return d, polys
    return None, None
