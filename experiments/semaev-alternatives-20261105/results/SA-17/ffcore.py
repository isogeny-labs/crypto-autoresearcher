"""SA-17 core: F_q[t] polynomial helpers, planting in F_q[t]/(pi), weak-Popov (Mulders-Storjohann) reduction."""
import numpy as np, random
import cypari2
pari = cypari2.Pari(); pari.allocatemem(300*10**6)

# ---------- polynomial arithmetic over F_q, numpy int64 arrays low->high ----------
def trim(a):
    nz = np.nonzero(a)[0]
    return a[:nz[-1]+1] if len(nz) else a[:0]
def pmul(a, b, q):
    if len(a)==0 or len(b)==0: return np.zeros(0, dtype=np.int64)
    return np.convolve(a, b) % q
def padd(a, b, q):
    n = max(len(a), len(b)); r = np.zeros(n, dtype=np.int64)
    r[:len(a)] += a; r[:len(b)] += b
    return trim(r % q)
def pscale(a, c, q): return trim((a*c) % q)
def pmod(a, m, q):
    """a mod m, m monic."""
    a = a.copy() % q; dm = len(m)-1
    for i in range(len(a)-1, dm-1, -1):
        c = a[i]
        if c: a[i-dm:i+1] = (a[i-dm:i+1] - c*m) % q
    return trim(a[:dm])
def ppow_small(a, k, q):
    r = np.array([1], dtype=np.int64)
    for _ in range(k): r = pmul(r, a, q)
    return r

_vecrev = pari('(z)->Vecrev(z.pol)')
# ---------- field F_{q^n} = F_q[t]/(pi) via PARI ----------
class Field:
    def __init__(self, q, n):
        self.q, self.n = q, n
        pol = pari.ffinit(q, n, 't')
        self.pi = np.array([int(pari.lift(c)) for c in pari.Vecrev(pol)], dtype=np.int64)  # monic, low->high
        self.a = pari.ffgen(pol, 'a')
    def to_pari(self, c):  # coefficient array -> FFELT
        r = self.a*0
        for i, ci in enumerate(c):
            if ci: r = r + int(ci)*self.a**i
        return r
    def to_arr(self, x):
        v = _vecrev(x)
        out = np.zeros(self.n, dtype=np.int64)
        for i, ci in enumerate(v): out[i] = int(ci)
        return out

def curve_ab(q): return 1, 1   # y^2 = x^3 + x + 1 ; nonsingular for q=3,5,7 (checked in selftest)

def S3_coeffs_poly(x_R, a, b, q, pi):
    """monomial coefficients (as polys mod pi) of S3(x1,x2,x_R); dict (i,j)->array. Matches report formula."""
    X = x_R; X2 = pmod(pmul(X, X, q), pi, q)
    one = np.array([1], dtype=np.int64)
    def c(v): return trim(np.array([v % q], dtype=np.int64))
    d = {}
    d[(2,0)] = X2; d[(0,2)] = X2
    d[(1,1)] = padd(pscale(X2, -2, q), c(-2*a), q)
    d[(2,1)] = pscale(X, -2, q); d[(1,2)] = pscale(X, -2, q)
    d[(1,0)] = padd(pscale(X, -2*a, q), c(-4*b), q); d[(0,1)] = d[(1,0)]
    d[(0,0)] = padd(pscale(X, -4*b, q), c(a*a), q)
    d[(2,2)] = one
    return d

def plant_ff(F, D1, D2, rng):
    """Plant R = P1+P2 with deg x1 < D1, deg x2 < D2. Returns dict with x1,x2,xR arrays and checks."""
    q, n = F.q, F.n; a, b = curve_ab(q)
    def rand_point(D):
        for _ in range(10000):
            xc = np.array([rng.randrange(q) for _ in range(D)], dtype=np.int64)
            x = F.to_pari(xc)
            r = x**3 + a*x + b
            if r != 0 and pari.issquare(r):
                y = pari.sqrt(r)
                assert y*y == r
                return xc, x, y
        raise RuntimeError
    for _ in range(200):
        xc1, x1, y1 = rand_point(D1); xc2, x2, y2 = rand_point(D2)
        if x1 != x2: break
    else: raise RuntimeError('unplantable')
    lam = (y2-y1)/(x2-x1); xr = lam*lam - x1 - x2; yr = lam*(x1-xr) - y1
    assert yr*yr == xr**3 + a*xr + b           # R on curve
    # P1-P2 : other root of S3
    lam2 = (-y2-y1)/(x2-x1); xm = lam2*lam2 - x1 - x2
    return dict(x1=trim(xc1), x2=trim(xc2), xR=trim(F.to_arr(xr)), xM=trim(F.to_arr(xm)))

def check_S3(F, pl):
    """independent check: S3(x1,x2,xR)=0 and S3(x1,x2,xM)=0 mod pi using only numpy poly arithmetic."""
    q, pi = F.q, F.pi; a, b = curve_ab(q)
    for key in ('xR', 'xM'):
        co = S3_coeffs_poly(pl[key], a, b, q, pi)
        tot = np.zeros(0, dtype=np.int64)
        for (i, j), cf in co.items():
            m = pmul(ppow_small(pl['x1'], i, q), ppow_small(pl['x2'], j, q), q)
            tot = padd(tot, pmod(pmul(cf, m, q), pi, q), q)
        if len(tot): return False
    return True

# ---------- weak Popov form (Mulders-Storjohann) with column weights ----------
def weak_popov(A, w, q, maxsteps=10**8):
    """A: int array (R,C,L), coefficients mod q (low->high) of a full-rank polynomial matrix; rows = basis.
    w: column weights. Reduces in place until the pivots (rightmost column of max weighted degree) are distinct.
    Returns (A, degs): weighted row degrees (successive minima of the lattice)."""
    R, C, L = A.shape
    inv = [0]+[pow(i, -1, q) for i in range(1, q)]
    w = np.asarray(w)
    def info(r):
        nz = A[r] != 0
        has = nz.any(axis=1)
        top = L-1-np.argmax(nz[:, ::-1], axis=1)
        wd = np.where(has, top+w, -10**9)
        d = int(wd.max()); c = C-1-int(np.argmax((wd == d)[::-1]))
        return c, d, int(top[c]), int(A[r, c, top[c]])
    owner = {}; deg = [0]*R; queue = list(range(R)); steps = 0
    while queue:
        i = queue.pop()
        while True:
            c, d, ti, li = info(i); deg[i] = d
            j = owner.get(c)
            if j is None:
                owner[c] = i; break
            steps += 1
            assert steps < maxsteps
            cj, dj, tj, lj = info(j)
            if d >= dj:                       # reduce i by j
                sh = ti-tj; f = (li*inv[lj]) % q
                A[i, :, sh:] = (A[i, :, sh:] - f*A[j, :, :L-sh]) % q
            else:                             # reduce j by i; i takes the slot, j re-queued
                sh = tj-ti; f = (lj*inv[li]) % q
                A[j, :, sh:] = (A[j, :, sh:] - f*A[i, :, :L-sh]) % q
                owner[c] = i; queue.append(j); break
    degs = []; pv = set()
    for r in range(R):
        c, d, _, _ = info(r); degs.append(d); pv.add(c)
    assert len(pv) == R, "not weak Popov"
    return A, degs
