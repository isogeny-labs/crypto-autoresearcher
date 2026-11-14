"""SA-17 (resumed): mechanism test. The S3 relation is linear in the 3-vector (A,B,C) = coefficients of X^2, X, 1:
S3 = A X^2 + B X + C with A=(x1-x2)^2, B=-2((x1+x2)(x1x2+a)+2b), C=(x1x2-a)^2-4b(x1+x2).
3-dim form lattice {(al,be,ga): al X^2 + be X + ga = 0 mod pi (or p)}, columns weighted to the bounds of (A,B,C).
FF: weak Popov (exact); Z: LLL.  Success = reduced first vector is +-planted (A,B,C) (up to F_q^* scalar in FF).
Same planting and same S scan as run_cell.py; writes results/form3.jsonl."""
import sys, json, math, random, time, sympy
sys.path.insert(0, '/home/user/semaev-runs/SA-17')
from ffcore import *
from fpylll import IntegerMatrix, LLL
import numpy as np

def ABC_poly(x1, x2, a, b, q):
    one = np.array([1], dtype=np.int64)
    d = padd(x1, pscale(x2, -1, q), q); A = pmul(d, d, q)
    s_ = padd(x1, x2, q); pr = pmul(x1, x2, q)
    B = pscale(padd(pmul(s_, padd(pr, trim(np.array([a % q])), q), q), trim(np.array([(2*b) % q])), q), -2, q)
    u = padd(pr, trim(np.array([(-a) % q])), q)
    C = padd(pmul(u, u, q), pscale(s_, -4*b, q), q)
    return A, B, C

def ff_trial(F, S, rng):
    q, n = F.q, F.n; a, b = curve_ab(q)
    D1, D2 = (S+1)//2, S//2
    pl = plant_ff(F, D1, D2, rng); assert check_S3(F, pl)
    e = D1-1
    A, B, C = ABC_poly(pl['x1'], pl['x2'], a, b, q)
    X = pl['xR']; X2 = pmod(pmul(X, X, q), F.pi, q)
    # check relation
    tot = padd(padd(pmod(pmul(A, X2, q), F.pi, q), pmod(pmul(B, X, q), F.pi, q), q), pmod(C, F.pi, q), q)
    assert len(tot) == 0
    L = n + 4*e + 4
    M = np.zeros((3, 3, L), dtype=np.int16)
    M[0, 0, 0] = 1; nx2 = pscale(X2, -1, q); M[0, 2, :len(nx2)] = nx2
    M[1, 1, 0] = 1; nx = pscale(X, -1, q); M[1, 2, :len(nx)] = nx
    M[2, 2, :len(F.pi)] = F.pi
    w = [2*e, e, 0]
    M, degs = weak_popov(M, w, q)
    r = int(np.argmin(degs))
    v = [trim(M[r, c].astype(np.int64)) for c in range(3)]
    # planted up to scalar: compare normalised
    tgt = [A, B, C]
    lc = lambda vs: next(int(p[-1]) for p in vs if len(p))
    f = (lc(tgt)*pow(lc(v), -1, q)) % q
    ok = all(np.array_equal(pscale(vi, f, q), ti) for vi, ti in zip(v, tgt))
    second = sorted(degs)[1]
    return dict(success=bool(ok), d1=min(degs), d2=second, e=e)

def z_trial(q, n, p, S, rng, A_=1, B_=1):
    D1, D2 = (S+1)//2, S//2
    B1, B2 = q**D1, q**D2
    Mp = pari.Mod
    def rpoint(Bd):
        for _ in range(20000):
            x = rng.randrange(1, Bd+1); r = (x**3 + A_*x + B_) % p
            if r and pari.issquare(Mp(r, p)): return x, int(pari.lift(pari.sqrt(Mp(r, p))))
        raise RuntimeError
    while True:
        x1, y1 = rpoint(B1); x2, y2 = rpoint(B2)
        if x1 != x2: break
    lam = (y2-y1)*pow(x2-x1, -1, p) % p; X = (lam*lam-x1-x2) % p
    A = (x1-x2)**2; Bc = -2*((x1+x2)*(x1*x2+A_)+2*B_); C = (x1*x2-A_)**2-4*B_*(x1+x2)
    assert (A*X*X + Bc*X + C) % p == 0
    Bd = max(B1, B2)
    wA, wB = Bd**2, Bd          # scale so that all three columns have size ~ Bd^4
    Mx = IntegerMatrix.from_matrix([[wA, 0, (-X*X % p)], [0, wB, (-X) % p], [0, 0, p]])
    LLL.reduction(Mx, delta=0.99)
    v = [Mx[0, 0]//wA, Mx[0, 1]//wB, Mx[0, 2]]
    # planted up to a rational scalar (planted (A,B,C) may be non-primitive, e.g. B is always even)
    tg = [A, Bc, C]
    ok = any(x != 0 for x in v) and all(v[i]*tg[j] == v[j]*tg[i] for i in range(3) for j in range(3))
    return dict(success=bool(ok))

if __name__ == '__main__':
    q, n, ntr = map(int, sys.argv[1:4])
    seed = q*7919+n; rng = random.Random(seed); random.seed(seed)
    F = Field(q, n); p = int(sympy.nextprime(q**n))
    out = open('/home/user/semaev-runs/SA-17/results/form3.jsonl', 'a')
    for kind in ('ff', 'z'):
        S = 4; fails = 0
        while S <= n and fails < 3:
            rs = [ff_trial(F, S, rng) if kind == 'ff' else z_trial(q, n, p, S, rng) for _ in range(ntr)]
            rate = sum(r['success'] for r in rs)/ntr
            out.write(json.dumps(dict(kind=kind, q=q, n=n, S=S, delta=S/(2*n), trials=ntr, rate=rate))+'\n'); out.flush()
            fails = fails+1 if rate < 0.5 else 0
            S += 1
