"""SA-17 m=3: S_4 (three small unknowns) box lattice, same pipeline in F_q[t]/(pi) and F_p."""
import numpy as np, random, math, time, json, itertools
from ffcore import *
from lat import bivar_mul
from fpylll import IntegerMatrix, LLL
S4 = [(tuple(m[:3]), m[3], c) for m, c in json.load(open('/home/user/semaev-runs/SA-17/s4_a1_b1.json'))]
S4 = [(tuple(m[0]), m[1], c) for m, c in [(x[0][:3] if False else (x[0][:3], x[0][3]), x[1]) for x in json.load(open('/home/user/semaev-runs/SA-17/s4_a1_b1.json'))]]
# S4 : list of ((i,j,k), l, c) meaning c * x1^i x2^j x3^k * X^l

def plant3_ff(F, Ds, rng):
    q = F.q; a, b = curve_ab(q)
    pts = []
    for D in Ds:
        for _ in range(10000):
            xc = np.array([rng.randrange(q) for _ in range(D)], dtype=np.int64); x = F.to_pari(xc); r = x**3+a*x+b
            if r != 0 and pari.issquare(r):
                y = pari.sqrt(r); pts.append((trim(xc), x, y)); break
    def add(P, Q):
        (x1, y1), (x2, y2) = P, Q
        lam = (y2-y1)/(x2-x1); x3 = lam*lam-x1-x2; return (x3, lam*(x1-x3)-y1)
    (_, x1, y1), (_, x2, y2), (_, x3, y3) = pts
    if x1 == x2 or x1 == x3 or x2 == x3: return None
    P12 = add((x1, y1), (x2, y2))
    if P12[0] == x3: return None
    R = add(P12, (x3, y3)); xr, yr = R
    assert yr*yr == xr**3 + a*xr + b
    return dict(xs=[p[0] for p in pts], xR=trim(F.to_arr(xr)))

def f_coeffs_ff(xR, q, pi):
    Xp = [np.array([1], dtype=np.int64)]
    for l in range(4): Xp.append(pmod(pmul(Xp[-1], xR, q), pi, q))
    d = {}
    for (m, l, c) in S4:
        d[m] = padd(d.get(m, np.zeros(0, dtype=np.int64)), pscale(Xp[l], c, q), q)
    return d

def ff_trial3(F, Ds, s, t, rng, kfield):
    q, n = F.q, F.n
    while True:
        pl = plant3_ff(F, Ds, rng)
        if pl: break
    xs = pl['xs']; e = [D-1 for D in Ds]
    co = f_coeffs_ff(pl['xR'], q, F.pi)
    # check S4(x1,x2,x3,xR)=0 mod pi independent of PARI
    pw = [[ppow_small(x, i, q) for i in range(5)] for x in xs]
    tot = np.zeros(0, dtype=np.int64)
    for m, cf in co.items():
        mono = pmul(pmul(pw[0][m[0]], pw[1][m[1]], q), pw[2][m[2]], q)
        tot = padd(tot, pmod(pmul(cf, mono, q), F.pi, q), q)
    assert len(tot) == 0, "S4 check failed"
    M = [m for m in itertools.product(range(s+1), repeat=3)]
    ks = [min(t, min(m)//4) for m in M]
    idx = {m: i for i, m in enumerate(M)}
    w = np.array([sum(e[i]*m[i] for i in range(3)) for m in M])
    L = t*n + int(w.max()) + 2
    one = {(0, 0, 0): np.array([1], dtype=np.int64)}
    fk = [one]
    for k in range(1, t+1):
        R_ = {}
        for m1, u in fk[-1].items():
            for m2, v in co.items():
                key = tuple(x+y for x, y in zip(m1, m2)); val = pmul(u, v, q)
                R_[key] = padd(R_[key], val, q) if key in R_ else val
        fk.append(R_)
    pik = [np.array([1], dtype=np.int64)]
    for k in range(1, t+1): pik.append(pmul(pik[-1], F.pi, q))
    A = np.zeros((len(M), len(M), L), dtype=np.int16)
    for r, m in enumerate(M):
        k = ks[r]; sm = tuple(x-4*k for x in m)
        for mm, poly in fk[k].items():
            pp = pmul(poly, pik[t-k], q); key = tuple(x+y for x, y in zip(sm, mm))
            A[r, idx[key], :len(pp)] = pp
    t0 = time.time(); A, degs = weak_popov(A, w, q); tred = time.time()-t0
    pwf = [[ppow_small(x, i, q) for i in range(s+1)] for x in xs]
    mono = {m: pmul(pmul(pwf[0][m[0]], pwf[1][m[1]], q), pwf[2][m[2]], q) for m in M}
    order = sorted(range(len(M)), key=lambda r: degs[r])
    van = []
    for r in order[:12]:
        tot = np.zeros(0, dtype=np.int64)
        for c, m in enumerate(M):
            cp = trim(A[r, c].astype(np.int64))
            if len(cp): tot = padd(tot, pmul(cp, mono[m], q), q)
        if len(tot) == 0: van.append(r)
    # Jacobian rank at the root, specialised t -> random element of GF(q^kfield)
    ok = False
    if len(van) >= 3:
        pol = pari.ffinit(q, kfield, 'u'); g = pari.ffgen(pol, 'g'); t0e = g**random.randrange(1, q**kfield-1)
        def ev(poly):
            v = g*0
            for ci in poly[::-1]: v = v*t0e + int(ci)
            return v
        rowsJ = []
        for r in van[:8]:
            grad = [g*0, g*0, g*0]
            for c, m in enumerate(M):
                cp = trim(A[r, c].astype(np.int64))
                if len(cp) == 0: continue
                cv = ev(cp)
                for v in range(3):
                    if m[v] == 0: continue
                    mm = list(m); mm[v] -= 1
                    dm = pmul(pmul(pwf[0][mm[0]], pwf[1][mm[1]], q), pwf[2][mm[2]], q)
                    grad[v] = grad[v] + (m[v] % q)*cv*ev(dm)
            rowsJ.append(grad)
        J = pari.matrix(len(rowsJ), 3, [x for row in rowsJ for x in row])
        ok = int(pari.matrank(J)) == 3
    srt = sorted(degs)
    return dict(success=bool(ok), nvan=len(van), d1=srt[0], d3=srt[2], tn=t*n, tred=tred, S=sum(Ds))

def z_trial3(q, n, p, Ds, s, t, rng, A_=1, B_=1):
    Bs = [q**D for D in Ds]
    Mp = pari.Mod
    def rpoint(Bd):
        while True:
            x = rng.randrange(1, Bd+1); r = (x**3+A_*x+B_) % p
            if r and pari.issquare(Mp(r, p)): return x, int(pari.lift(pari.sqrt(Mp(r, p))))
    while True:
        pts = [rpoint(B) for B in Bs]
        xs = [P[0] for P in pts]
        if len(set(xs)) < 3: continue
        def add(P, Q):
            lam = (Q[1]-P[1])*pow(Q[0]-P[0], -1, p) % p; x3 = (lam*lam-P[0]-Q[0]) % p; return (x3, (lam*(P[0]-x3)-P[1]) % p)
        P12 = add(pts[0], pts[1])
        if P12[0] == xs[2]: continue
        R = add(P12, pts[2]); break
    xr = R[0]; assert (R[1]**2-(xr**3+A_*xr+B_)) % p == 0
    co = {}
    for (m, l, c) in S4: co[m] = (co.get(m, 0) + c*pow(xr, l, p)) % p
    assert sum(c*xs[0]**m[0]*xs[1]**m[1]*xs[2]**m[2] for m, c in co.items()) % p == 0
    M = [m for m in itertools.product(range(s+1), repeat=3)]
    ks = [min(t, min(m)//4) for m in M]; idx = {m: i for i, m in enumerate(M)}
    fk = [{(0, 0, 0): 1}]
    for k in range(1, t+1):
        R_ = {}
        for m1, u in fk[-1].items():
            for m2, v in co.items():
                key = tuple(x+y for x, y in zip(m1, m2)); R_[key] = R_.get(key, 0)+u*v
        fk.append(R_)
    d = len(M); Mx = IntegerMatrix(d, d)
    sc = {m: Bs[0]**m[0]*Bs[1]**m[1]*Bs[2]**m[2] for m in M}
    for r, m in enumerate(M):
        k = ks[r]; sm = tuple(x-4*k for x in m)
        for mm, c in fk[k].items():
            key = tuple(x+y for x, y in zip(sm, mm))
            Mx[r, idx[key]] = c*p**(t-k)*sc[key]
    t0 = time.time(); LLL.reduction(Mx, delta=0.99); tred = time.time()-t0
    gl = []
    for r in range(d):
        g = {M[c]: int(Mx[r, c])//sc[M[c]] for c in range(d)}
        if sum(cf*xs[0]**m[0]*xs[1]**m[1]*xs[2]**m[2] for m, cf in g.items()) == 0: gl.append(g)
        if len(gl) >= 8: break
    ok = False
    if len(gl) >= 3:
        rowsJ = []
        for g in gl:
            grad = [0, 0, 0]
            for m, cf in g.items():
                for v in range(3):
                    if m[v] == 0: continue
                    mm = list(m); mm[v] -= 1
                    grad[v] += m[v]*cf*xs[0]**mm[0]*xs[1]**mm[1]*xs[2]**mm[2]
            rowsJ.append(grad)
        J = pari.matrix(len(rowsJ), 3, [x for row in rowsJ for x in row])
        ok = int(pari.matrank(J)) == 3
    return dict(success=bool(ok), nvan=len(gl), tred=tred, S=sum(Ds))
