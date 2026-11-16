"""SA-17 (resumed), m=3 mechanism test: S4(x1,x2,x3,X) = sum_{l=0..4} c_l(x1,x2,x3) X^l, deg_x c_l = 12-l.
5-dim form lattice {(c_0..c_4): sum c_l X^l = 0 mod pi (or p)}, columns weighted to the bounds of c_l.
Heuristic/exact uniqueness threshold: delta < 1/sum_l(12-l) = 1/50 per variable. FF: weak Popov; Z: LLL.
Success = first reduced vector proportional to the planted (c_0..c_4). Writes results/form5.jsonl."""
import sys, json, math, random, sympy
sys.path.insert(0, '/home/user/semaev-runs/SA-17')
from lat3 import *            # ffcore, S4 table, plant3_ff
from fpylll import IntegerMatrix, LLL
import numpy as np
DL = {l: 12-l for l in range(5)}

def cl_ff(xs, q):
    pw = [[ppow_small(x, i, q) for i in range(5)] for x in xs]
    c = {l: np.zeros(0, dtype=np.int64) for l in range(5)}
    for (m, l, cf) in S4:
        mono = pmul(pmul(pw[0][m[0]], pw[1][m[1]], q), pw[2][m[2]], q)
        c[l] = padd(c[l], pscale(mono, cf, q), q)
    return [c[l] for l in range(5)]

def plant3_odd(F, Ds, rng):
    """as lat3.plant3_ff, but y = r^((Q+1)/4) (needs Q = q^n = 3 mod 4: q in {3,7}, n odd); pari.sqrt stalls at n>=96."""
    q, n = F.q, F.n; a, b = curve_ab(q); Q = q**n; assert Q % 4 == 3
    pts = []
    for D in Ds:
        while True:
            xc = np.array([rng.randrange(q) for _ in range(D)], dtype=np.int64); x = F.to_pari(xc); r = x**3+a*x+b
            if r == 0: continue
            y = r**((Q+1)//4)
            if y*y == r: pts.append((trim(xc), x, y)); break
    def add(P, Q_):
        (x1, y1), (x2, y2) = P, Q_
        lam = (y2-y1)/(x2-x1); x3 = lam*lam-x1-x2; return (x3, lam*(x1-x3)-y1)
    (_, x1, y1), (_, x2, y2), (_, x3, y3) = pts
    if x1 == x2 or x1 == x3 or x2 == x3: return None
    P12 = add((x1, y1), (x2, y2))
    if P12[0] == x3: return None
    xr, yr = add(P12, (x3, y3)); assert yr*yr == xr**3 + a*xr + b
    return dict(xs=[p[0] for p in pts], xR=trim(F.to_arr(xr)))

def ff_trial(F, S, rng):
    q, n = F.q, F.n
    Ds = [S//3 + (1 if i < S % 3 else 0) for i in range(3)]
    while True:
        pl = plant3_odd(F, Ds, rng)
        if pl: break
    e = max(Ds)-1
    c = cl_ff(pl['xs'], q)
    Xp = [np.array([1], dtype=np.int64)]
    for l in range(4): Xp.append(pmod(pmul(Xp[-1], pl['xR'], q), F.pi, q))
    tot = np.zeros(0, dtype=np.int64)
    for l in range(5): tot = padd(tot, pmod(pmul(c[l], Xp[l], q), F.pi, q), q)
    assert len(tot) == 0, 'S4 relation fails'
    L = n + 12*e + 4
    M = np.zeros((5, 5, L), dtype=np.int16)
    for l in range(1, 5):
        M[l-1, l, 0] = 1; nx = pscale(Xp[l], -1, q); M[l-1, 0, :len(nx)] = nx
    M[4, 0, :len(F.pi)] = F.pi
    w = [l*e for l in range(5)]
    M, degs = weak_popov(M, w, q)
    r = int(np.argmin(degs)); v = [trim(M[r, k].astype(np.int64)) for k in range(5)]
    lc = lambda vs: next(int(p[-1]) for p in vs if len(p))
    f = (lc(c)*pow(lc(v), -1, q)) % q
    return dict(success=all(np.array_equal(pscale(vi, f, q), ti) for vi, ti in zip(v, c)))

def z_trial(q, n, p, S, rng, A_=1, B_=1):
    Ds = [S//3 + (1 if i < S % 3 else 0) for i in range(3)]
    Bs = [q**D for D in Ds]; Mp = pari.Mod
    def rpoint(Bd):
        while True:
            x = rng.randrange(1, Bd+1); r = (x**3+A_*x+B_) % p
            if r and pari.issquare(Mp(r, p)): return x, int(pari.lift(pari.sqrt(Mp(r, p))))
    def add(P, Q):
        lam = (Q[1]-P[1])*pow(Q[0]-P[0], -1, p) % p; x3 = (lam*lam-P[0]-Q[0]) % p; return (x3, (lam*(P[0]-x3)-P[1]) % p)
    while True:
        pts = [rpoint(B) for B in Bs]; xs = [P[0] for P in pts]
        if len(set(xs)) < 3: continue
        P12 = add(pts[0], pts[1])
        if P12[0] == xs[2]: continue
        R = add(P12, pts[2]); break
    X = R[0]
    c = [0]*5
    for (m, l, cf) in S4: c[l] += cf*xs[0]**m[0]*xs[1]**m[1]*xs[2]**m[2]
    assert sum(c[l]*pow(X, l, p) for l in range(5)) % p == 0
    Bd = max(Bs); wt = [Bd**(12-DL[l]) for l in range(5)]   # = Bd^l
    rows = []
    for l in range(1, 5):
        r_ = [0]*5; r_[l] = wt[l]; r_[0] = (-pow(X, l, p)) % p; rows.append(r_)
    rows.append([p, 0, 0, 0, 0])
    Mx = IntegerMatrix.from_matrix(rows); LLL.reduction(Mx, delta=0.99)
    v = [Mx[0, l]//wt[l] for l in range(5)]
    ok = any(x != 0 for x in v) and all(v[i]*c[j] == v[j]*c[i] for i in range(5) for j in range(5))
    return dict(success=bool(ok))

if __name__ == '__main__':
    q, n, ntr = map(int, sys.argv[1:4])
    seed = q*104729+n; rng = random.Random(seed); random.seed(seed)
    F = Field(q, n); p = int(sympy.nextprime(q**n))
    out = open('/home/user/semaev-runs/SA-17/results/form5.jsonl', 'a')
    kinds = sys.argv[4].split(',') if len(sys.argv) > 4 else ['ff', 'z']
    S0 = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    for kind in kinds:
        S = S0; fails = 0   # S<6 gives D=1 (constants): too few planting points, loops
        while S <= n and fails < 3:
            rs = [ff_trial(F, S, rng) if kind == 'ff' else z_trial(q, n, p, S, rng) for _ in range(ntr)]
            rate = sum(r['success'] for r in rs)/ntr
            out.write(json.dumps(dict(kind=kind, q=q, n=n, S=S, delta=S/(3*n), trials=ntr, rate=rate))+'\n'); out.flush()
            fails = fails+1 if rate < 0.5 else 0
            S += 1
