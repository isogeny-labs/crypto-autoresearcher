"""SA-17: Coppersmith box-shift lattice for S3 mod pi (function field) and mod p (integers), same shift sets."""
import numpy as np, random, math, time, json, sys
from ffcore import *
from fpylll import IntegerMatrix, LLL

def shift_params(s, t):
    """box M=[0,s]^2, leading-monomial shifts k=min(t, min(a,b)//2). returns monomials list, k list, predicted delta_asym, dim."""
    M = [(a, b) for a in range(s+1) for b in range(s+1)]
    ks = [min(t, min(a, b)//2) for a, b in M]
    pred = sum(ks)/sum(a+b for a, b in M)
    return M, ks, pred

def bivar_mul(P, Q, mulf, addf):
    R = {}
    for (i, j), u in P.items():
        for (k, l), v in Q.items():
            key = (i+k, j+l); w = mulf(u, v)
            R[key] = addf(R[key], w) if key in R else w
    return R

# ------------------------------------------------------------------ function field
def ff_trial(F, S, s, t, rng, kfield):
    q, n = F.q, F.n; a, b = curve_ab(q)
    D1, D2 = (S+1)//2, S//2
    pl = plant_ff(F, D1, D2, rng)
    assert check_S3(F, pl)
    e1, e2 = D1-1, D2-1                       # sup-degree bounds of x1,x2
    co = S3_coeffs_poly(pl['xR'], a, b, q, F.pi)
    M, ks, pred = shift_params(s, t)
    mulf = lambda u, v: pmul(u, v, q); addf = lambda u, v: padd(u, v, q)
    fk = [{(0, 0): np.array([1], dtype=np.int64)}]
    for k in range(1, t+1): fk.append(bivar_mul(fk[-1], co, mulf, addf))
    pik = [np.array([1], dtype=np.int64)]
    for k in range(1, t+1): pik.append(pmul(pik[-1], F.pi, q))
    w = np.array([e1*a_ + e2*b_ for a_, b_ in M])
    L = t*n + int(w.max()) + 2
    idx = {m: i for i, m in enumerate(M)}
    A = np.zeros((len(M), len(M), L), dtype=np.int16)
    for r, (a_, b_) in enumerate(M):
        k = ks[r]; sa, sb = a_-2*k, b_-2*k
        for (i, j), poly in fk[k].items():
            pp = pmul(poly, pik[t-k], q)
            A[r, idx[(sa+i, sb+j)], :len(pp)] = pp
    t0 = time.time()
    A, degs = weak_popov(A, w, q)
    tred = time.time()-t0
    # exact evaluation at the planted root
    x1, x2 = pl['x1'], pl['x2']
    p1 = [ppow_small(x1, i, q) for i in range(s+1)]; p2 = [ppow_small(x2, i, q) for i in range(s+1)]
    mono = [pmul(p1[a_], p2[b_], q) for a_, b_ in M]
    van = []
    for r in range(len(M)):
        tot = np.zeros(0, dtype=np.int64)
        for c in range(len(M)):
            cp = trim(A[r, c].astype(np.int64))
            if len(cp): tot = padd(tot, pmul(cp, mono[c], q), q)
        if len(tot) == 0: van.append(r)
    ok = zero_dim_ff(A, van, M, q, kfield, s)
    srt = sorted(degs)
    return dict(success=bool(ok), nvan=len(van), d1=srt[0], d2=srt[1], tn=t*n, ntheory=sum(d < t*n for d in degs),
                avg=sum(degs)/len(degs), tred=tred, S=S)

_fcache = {}
def coprime_pair_ff(rows, q, kf, s):
    if len(rows) < 2: return False
    if (q, kf) not in _fcache:
        pol = pari.ffinit(q, kf, 'u'); _fcache[(q, kf)] = pari.ffgen(pol, 'g')
    g = _fcache[(q, kf)]
    t0 = g**random.randrange(1, q**kf-1) ; c = g**random.randrange(1, q**kf-1)
    def spec(row):
        # value of each monomial coeff at t0, then polynomial in y=x2 after x1=c
        cache = {}
        coefs = [g*0 for _ in range(s+1)]
        for (a_, b_), poly in row.items():
            if len(poly) == 0: continue
            v = g*0
            for ci in poly[::-1]: v = v*t0 + int(ci)
            coefs[b_] = coefs[b_] + v*c**a_
        return pari.Pol(pari.Vecrev(coefs), 'y')
    P = [spec(r) for r in rows]
    for i in range(len(P)):
        for j in range(i+1, len(P)):
            if P[i] != 0 and P[j] != 0 and pari.poldegree(pari.gcd(P[i], P[j])) == 0: return True
    return False

# ------------------------------------------------------------------ integers
def z_trial(q, n, p, S, s, t, rng, A_=1, B_=1):
    D1, D2 = (S+1)//2, S//2
    B1, B2 = q**D1, q**D2
    Mp = pari.Mod
    def rpoint(Bd):
        for _ in range(20000):
            x = rng.randrange(1, Bd+1); r = (x**3 + A_*x + B_) % p
            if r and pari.issquare(Mp(r, p)): return x, int(pari.lift(pari.sqrt(Mp(r, p))))
        raise RuntimeError('unplantable')
    for _ in range(200):
        x1, y1 = rpoint(B1); x2, y2 = rpoint(B2)
        if x1 != x2: break
    else: raise RuntimeError('unplantable')
    lam = (y2-y1)*pow(x2-x1, -1, p) % p; xr = (lam*lam-x1-x2) % p; yr = (lam*(x1-xr)-y1) % p
    assert (yr*yr - (xr**3 + A_*xr + B_)) % p == 0
    X = xr
    co = {(2,0): X*X % p, (0,2): X*X % p, (1,1): (-2*X*X-2*A_) % p, (2,1): -2*X % p, (1,2): -2*X % p,
          (1,0): (-2*A_*X-4*B_) % p, (0,1): (-2*A_*X-4*B_) % p, (0,0): (-4*B_*X+A_*A_) % p, (2,2): 1}
    assert sum(c*x1**i*x2**j for (i, j), c in co.items()) % p == 0     # S3(x1,x2,xR)=0 mod p
    M, ks, pred = shift_params(s, t)
    mulf = lambda u, v: u*v; addf = lambda u, v: u+v
    fk = [{(0, 0): 1}]
    for k in range(1, t+1): fk.append(bivar_mul(fk[-1], co, mulf, addf))
    idx = {m: i for i, m in enumerate(M)}
    d = len(M); Mx = IntegerMatrix(d, d)
    for r, (a_, b_) in enumerate(M):
        k = ks[r]; sa, sb = a_-2*k, b_-2*k
        for (i, j), c in fk[k].items():
            cc = idx[(sa+i, sb+j)]
            Mx[r, cc] = c * p**(t-k) * B1**(sa+i) * B2**(sb+j)
    t0 = time.time(); LLL.reduction(Mx, delta=0.99); tred = time.time()-t0
    rows = []
    for r in range(d):
        g = {}; ok = True
        for c, (a_, b_) in enumerate(M):
            v = int(Mx[r, c]); sc = B1**a_ * B2**b_
            assert v % sc == 0; g[(a_, b_)] = v//sc
        val = sum(cf*x1**a_*x2**b_ for (a_, b_), cf in g.items())
        if val == 0: rows.append((0, g))
    nvan = len(rows)
    ok = zero_dim_z(rows, s) if nvan >= 2 else False
    return dict(success=bool(ok), nvan=nvan, tred=tred, S=S, x1=x1, x2=x2, rows=rows)

def coprime_pair_z(rows, s):
    r = 2**61-1; c = random.randrange(2, r)
    def spec(g):
        coefs = [0]*(s+1)
        for (a_, b_), v in g.items(): coefs[b_] = (coefs[b_] + v*pow(c, a_, r)) % r
        return pari.Pol(pari.Vecrev([pari.Mod(v, r) for v in coefs]), 'y')
    P = [spec(g) for _, g in rows]
    for i in range(len(P)):
        for j in range(i+1, len(P)):
            if P[i] != 0 and P[j] != 0 and pari.poldegree(pari.gcd(P[i], P[j])) == 0: return True
    return False


import galois
_gcache = {}
def zero_dim_ff(A, van, M, q, kf, s):
    """Success criterion: the planted root is an isolated common zero of the lattice polynomials that vanish at it,
    i.e. their gcd (as bivariate polynomials over F_q[t]) is 1.  Tested by specialising t->t0, x1->c at random points of GF(q^kf):
    gcd of the specialised univariate polynomials in x2 is constant (w.h.p. iff the bivariate gcd has no x2-positive-degree factor)."""
    if len(van) < 2: return False
    if (q, kf) not in _gcache: _gcache[(q, kf)] = galois.GF(q**kf)
    GF = _gcache[(q, kf)]
    L = A.shape[2]
    t0 = GF.Random(low=1); c = GF.Random(low=1)
    pws = []; x = GF(1)
    for l in range(L): pws.append(int(x)); x = x*t0
    pw = GF(np.array(pws))
    Av = GF(A[van].astype(np.int64))
    vals = np.sum(Av*pw, axis=-1)                       # (nv, C)
    cp = [GF(1)]
    for a_ in range(s): cp.append(cp[-1]*c)
    cps = GF(np.array([int(v) for v in cp]))
    g = None
    for i in range(len(van)):
        coefs = [GF(0)]*(s+1)
        for ci, (a_, b_) in enumerate(M):
            coefs[b_] = coefs[b_] + vals[i, ci]*cps[a_]
        P = galois.Poly(GF(np.array([int(v) for v in coefs[::-1]])), field=GF)
        if P.degree < 0: continue
        g = P if g is None else galois.gcd(g, P)
        if g.degree == 0: return True
    return False

def zero_dim_z(rows, s):
    r = 2**61-1; c = random.randrange(2, r)
    g = None
    for _, gg in rows:
        coefs = [0]*(s+1)
        for (a_, b_), v in gg.items(): coefs[b_] = (coefs[b_] + v*pow(c, a_, r)) % r
        P = pari.Pol(pari.Vecrev([pari.Mod(v, r) for v in coefs]), 'y')
        if P == 0: continue
        g = P if g is None else pari.gcd(g, P)
        if pari.poldegree(g) == 0: return True
    return False
