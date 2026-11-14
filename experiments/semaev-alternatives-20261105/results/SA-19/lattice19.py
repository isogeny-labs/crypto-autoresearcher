"""SA-19 planted recovery with the generalised form lattice.
Unknown vector v = T c(u) where c(u) are the u_R-coefficients of the relation (integer polynomials in the small
coordinates u1,u2) and T is the rational change of basis that puts span(c) in degree-echelon form (degree sequence);
r congruences mod p; columns weighted by B^{deg}; LLL; success = first reduced vector proportional to planted v.
Modes:
  coord  <name>  : single relation (r = 1) in a coordinate phi (weierstrass_x | edwards_y), S^phi interpolated mod p
                   and lifted to small integers (checked).
  multi  <shape> : Weierstrass x, monomial coefficient space W (box h | tot d), r = dim W cap (S_R) congruences.
usage: python3 lattice19.py <mode> <name> <bits> <ntrials> <delta_list comma> <seed>
appends json rows to results/lattice.jsonl"""
import sys, json, random, time, math
from fractions import Fraction
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *
import sympy
from fpylll import IntegerMatrix, LLL

def rand_prime(bits, rng):
    while True:
        p = sympy.nextprime(rng.getrandbits(bits) | (1 << (bits - 1)))
        if p % 4 == 3 and p.bit_length() == bits: return int(p)

# ------------------------------------------------------------ degree-echelon basis over Q
def echelon_T(polys):
    """polys: list of n integer polys (dicts).  Returns (T integer n x n, degs) with rows of T*C in degree-echelon
    form: row l of T*C has top degree degs[l], degs sorted ascending; T has integer entries (rows scaled)."""
    n = len(polys)
    mons = sorted({k for q in polys for k in q}, key=lambda m: (-sum(m), m))   # high degree first
    idx = {m: i for i, m in enumerate(mons)}
    C = [[Fraction(0)] * len(mons) for _ in range(n)]
    for l, q in enumerate(polys):
        for k, v in q.items(): C[l][idx[k]] = Fraction(v)
    T = [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    rk = 0
    for c in range(len(mons)):
        pr = next((i for i in range(rk, n) if C[i][c] != 0), None)
        if pr is None: continue
        C[rk], C[pr] = C[pr], C[rk]; T[rk], T[pr] = T[pr], T[rk]
        for i in range(n):
            if i != rk and C[i][c] != 0:
                f = C[i][c] / C[rk][c]
                C[i] = [a - f * b for a, b in zip(C[i], C[rk])]; T[i] = [a - f * b for a, b in zip(T[i], T[rk])]
        rk += 1
        if rk == n: break
    assert rk == n, 'coefficient polynomials dependent'
    degs = []
    Tint = []
    for i in range(n):
        top = next(sum(mons[c]) for c in range(len(mons)) if C[i][c] != 0)
        degs.append(top)
        den = 1
        for a in T[i]: den = den * a.denominator // math.gcd(den, a.denominator)
        row = [int(a * den) for a in T[i]]
        g = 0
        for a in row: g = math.gcd(g, a)
        Tint.append([a // g for a in row])
    order = sorted(range(n), key=lambda i: degs[i])
    return [Tint[i] for i in order], [degs[i] for i in order]

def mat_inv_mod(T, p):
    n = len(T)
    rows = [[x % p for x in T[i]] + [int(i == j) for j in range(n)] for i in range(n)]
    R, piv = rref_mod(rows, p); assert piv == list(range(n))
    return [r[n:] for r in R]

# ------------------------------------------------------------ lattice from r congruences
def form_lattice_recover(mu_rows, v_planted, degs, B, p):
    """mu_rows: r x n (mod p) congruences mu.v = 0; weights B^deg; returns success flag and the first vector."""
    n = len(degs); R, piv = rref_mod([[x % p for x in r] for r in mu_rows], p); r = len(R)
    free = [j for j in range(n) if j not in piv]
    dmax = max(degs); sc = [B ** (dmax - d) for d in degs]
    rows = []
    for j in free:
        v = [0] * n; v[j] = 1
        for i, c in enumerate(piv): v[c] = (-R[i][j]) % p
        rows.append([v[l] * sc[l] for l in range(n)])
    for c in piv:
        v = [0] * n; v[c] = p; rows.append([v[l] * sc[l] for l in range(n)])
    M = IntegerMatrix.from_matrix(rows); LLL.reduction(M, delta=0.99)
    best = None
    for i in range(M.nrows):
        v = [M[i, l] // sc[l] for l in range(n)]
        if any(v):
            best = v; break
    ok = best is not None and all(best[i] * v_planted[j] == best[j] * v_planted[i] for i in range(n) for j in range(n))
    return ok, best

# ------------------------------------------------------------ coordinate systems
class WeierstrassX:
    name = 'weierstrass_x'; a, b = 1, 1
    def setup(self, p, rng):
        self.p = p; self.E = Curve(self.a, self.b, p)
        S = S3_poly(self.a, self.b, p)
        self.S = {k: (v if v < p // 2 else v - p) for k, v in S.items()}      # exact small integers
        self.co = coeffs_in_last(self.S, 3)
    def plant(self, B, rng):
        E = self.E
        while True:
            P1, P2 = E.random_small(B, rng), E.random_small(B, rng)
            if P1[0] != P2[0]: break
        R = E.add(P1, P2)
        return P1[0], P2[0], R[0]

class EdwardsY:
    """Montgomery v^2 = u^3 + A u^2 + u (A small) <-> twisted Edwards a = A+2, d = A-2; y = (u-1)/(u+1)."""
    name = 'edwards_y'; A = 6      # a = 8, d = 4
    def setup(self, p, rng):
        self.p = p; self.E = Curve(1, 0, p, a2=self.A)
        # interpolate over F_PR (31-bit) with the same small A: the integer polynomial is independent of p
        q = PR; Eq = Curve(1, 0, q, a2=self.A)
        inv = lambda v: pow(v, -1, q)
        phi = lambda x, y: None if x == q - 1 else (x - 1) * inv(x + 1) % q
        d, polys = minimal_summation_poly(Eq, phi, rng, q, dstart=2, dmaxmax=2)
        assert d == 2 and len(polys) == 1
        S = polys[0]
        # normalise so that the y1^2 y2^2 y3^2 coefficient is a small integer: scale to make coefficient lift small
        # try scaling by k for small k so that all lifts are small
        def lift(v): return v if v < q // 2 else v - q
        best = None
        for k in range(1, 400):
            for sgn in (1, -1):
                Sk = {m: lift(v * k * sgn % q) for m, v in S.items()}
                mx = max(abs(v) for v in Sk.values())
                if best is None or mx < best[0]: best = (mx, Sk)
        assert best[0] < 2 ** 24, 'summation polynomial does not lift to small integers'
        self.S = best[1]; self.co = coeffs_in_last(self.S, 3)
        # verify over F_p at random planted points
        for _ in range(5):
            u1, u2, uR = self.plant(1 << 20, rng)
            assert peval({m: v % p for m, v in self.S.items()}, (u1, u2, uR), p) == 0
    def plant(self, B, rng):
        E, p = self.E, self.p
        pts = []
        while len(pts) < 2:
            y = rng.randrange(2, B + 2)          # y = 1 is the point at infinity
            u = (1 + y) * pow(1 - y, -1, p) % p
            P = E.lift_x(u)
            if P is None: continue
            if rng.random() < 0.5: P = E.neg(P)
            if pts and pts[0][1][0] == P[0]: continue
            pts.append((y, P))
        R = E.add(pts[0][1], pts[1][1])
        yR = (R[0] - 1) * pow(R[0] + 1, -1, p) % p
        return pts[0][0], pts[1][0], yR

def coord_trial(cs, B, p, rng):
    u1, u2, uR = cs.plant(B, rng)
    c = [peval_int(q, (u1, u2)) for q in cs.co]            # exact integers
    assert sum(c[l] * pow(uR, l, p) for l in range(len(c))) % p == 0
    T, degs = cs.T, cs.degs
    v = [sum(T[i][j] * c[j] for j in range(len(c))) for i in range(len(c))]
    mu = [pow(uR, l, p) for l in range(len(c))]               # mu . c = 0
    Tinv = cs.Tinv
    mu2 = [sum(mu[j] * Tinv[j][i] for j in range(len(c))) % p for i in range(len(c))]   # mu2 . v = mu . T^{-1} v = mu . c
    assert sum(mu2[i] * v[i] for i in range(len(v))) % p == 0
    ok, best = form_lattice_recover([mu2], v, degs, B, p)
    return ok

def peval_int(q, pt):
    s = 0
    for k, v in q.items():
        t = v
        for e, x in zip(k, pt): t *= x ** e
        s += t
    return s

# ------------------------------------------------------------ multi-congruence monomial W (Weierstrass)
class MultiW:
    def __init__(self, shape):
        kind, par = shape.split(':'); par = int(par) if '_' not in par else par
        self.sym = kind.startswith('sym')
        if kind == 'box': self.mons = [(i, j) for i in range(3 + par) for j in range(3 + par)]
        elif kind == 'tot': self.mons = monomials_upto(2, par)
        elif kind == 'sym': self.mons = [(i, j) for i in range(par + 1) for j in range(par // 2 + 1) if i + 2 * j <= par]   # e1^i e2^j
        elif kind == 'symbox': self.mons = [(i, j) for i in range(3 + par) for j in range(3 + par // 2 + (par % 2))]           # e1^i e2^j box
        elif kind == 'mult':   # W = x-side span of {x^alpha X^j S3 : |alpha| <= dx, j <= dX}, degree-echelon basis over Q
            self.mult = tuple(int(t) for t in str(par).split('_')) if '_' in str(par) else (par, par)
            self.mons = None
        else: raise ValueError
        self.name = 'multi_' + shape
    def setup(self, p, rng):
        self.p = p; self.E = Curve(1, 1, p); self.a, self.b = 1, 1
        if self.mons is None:
            dx, dX = self.mult
            S3i = S3_poly(self.a, self.b, p); S3i = {k: (v if v < p // 2 else v - p) for k, v in S3i.items()}
            polys = []
            for al in monomials_upto(2, dx):
                for j in range(dX + 1):
                    F = {(k[0] + al[0], k[1] + al[1], k[2] + j): v for k, v in S3i.items()}
                    polys += xside_span(F, 2, p)
            # independent integer basis of the span: rref over Q then echelon
            mons = sorted({k for q in polys for k in q}); idx = {m: i for i, m in enumerate(mons)}
            rows = [[q.get(m, 0) % p for m in mons] for q in polys]
            R, piv = rref_mod(rows, p)
            # pick independent originals: greedy
            basis = []; cur = []
            for q in polys:
                test = cur + [[q.get(m, 0) % p for m in mons]]
                if rank_mod(test, p) > len(cur): cur = test; basis.append(q)
            self.cpolys = basis
            self.T, self.degs = echelon_T(basis); self.Tinv = mat_inv_mod(self.T, p)
            self.W = [{k: v % p for k, v in q.items()} for q in basis]
            self.mons = list(range(len(basis)))
            return
        self.degs = [m[0] + 2 * m[1] for m in self.mons] if self.sym else [sum(m) for m in self.mons]
        if self.sym:   # expand e1^i e2^j in x1, x2 over F_p
            e1 = {(1, 0): 1, (0, 1): 1}; e2 = {(1, 1): 1}
            self.W = [pmul(ppow(e1, m[0], p, 2), ppow(e2, m[1], p, 2), p) for m in self.mons]
        else:
            self.W = [{m: 1} for m in self.mons]
    def trial(self, B, rng):
        E, p = self.E, self.p
        while True:
            P1, P2 = E.random_small(B, rng), E.random_small(B, rng)
            if P1[0] != P2[0]: break
        R = E.add(P1, P2); X = R[0]
        S3 = S3_poly(self.a, self.b, p)
        SR = {}
        for k, v in S3.items(): SR[k[:2]] = (SR.get(k[:2], 0) + v * pow(X, k[2], p)) % p
        W = self.W
        mus = kernel_vectors(W, SR, p)
        if hasattr(self, 'cpolys'):
            c = [peval_int(q, (P1[0], P2[0])) for q in self.cpolys]
            for mu in mus: assert sum(a * b for a, b in zip(mu, c)) % p == 0
            n = len(c); v = [sum(self.T[i][j] * c[j] for j in range(n)) for i in range(n)]
            mus = [[sum(mu[j] * self.Tinv[j][i] for j in range(n)) % p for i in range(n)] for mu in mus]
        elif self.sym:
            e1, e2 = P1[0] + P2[0], P1[0] * P2[0]
            v = [e1 ** m[0] * e2 ** m[1] for m in self.mons]
        else:
            v = [P1[0] ** m[0] * P2[0] ** m[1] for m in self.mons]
        for mu in mus: assert sum(a * b for a, b in zip(mu, v)) % p == 0
        ok, best = form_lattice_recover(mus, v, self.degs, B, p)
        return ok, len(mus)

if __name__ == '__main__':
    mode, name, bits, ntr = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    deltas = [float(x) for x in sys.argv[5].split(',')]; seed = int(sys.argv[6])
    rng = random.Random(seed); p = rand_prime(bits, rng)
    out = open('/home/user/semaev-runs/SA-19/results/lattice.jsonl', 'a')
    if mode == 'coord':
        cs = {'weierstrass_x': WeierstrassX, 'edwards_y': EdwardsY}[name]()
        cs.setup(p, rng)
        cs.T, cs.degs = echelon_T(cs.co); cs.Tinv = mat_inv_mod(cs.T, p)
        w = sum(cs.degs)
        print(name, 'bits', bits, 'degree sequence', cs.degs, 'budget', w, 'predicted reach', round(1 / w, 4), 'S terms', len(cs.S), flush=True)
        for d in deltas:
            B = int(round(2 ** (d * bits))); t = time.time()
            succ = sum(coord_trial(cs, B, p, rng) for _ in range(ntr))
            row = dict(mode=mode, name=name, bits=bits, p=str(p), delta=d, B_bits=round(math.log2(B), 2), trials=ntr, success=succ,
                       rate=succ / ntr, degs=cs.degs, w=w, r=1, secs=round(time.time() - t, 1))
            print(json.dumps(row), flush=True); out.write(json.dumps(row) + '\n'); out.flush()
    else:
        mw = MultiW(name); mw.setup(p, rng)
        for d in deltas:
            B = int(round(2 ** (d * bits))); t = time.time(); succ = 0; rs = set()
            for _ in range(ntr):
                ok, r = mw.trial(B, rng); succ += ok; rs.add(r)
            w = sum(mw.degs)
            row = dict(mode=mode, name=mw.name, bits=bits, p=str(p), delta=d, B_bits=round(math.log2(B), 2), trials=ntr, success=succ,
                       rate=succ / ntr, w=w, r=sorted(rs), dim=len(mw.mons), secs=round(time.time() - t, 1))
            print(json.dumps(row), flush=True); out.write(json.dumps(row) + '\n'); out.flush()
