"""SA-19 step 4: m = 3.  Budget of S_4^phi (4 variables, P1+P2+P3+P4 = O) for phi = Weierstrass x (expect 50) and
phi = twisted Edwards y (symmetric classes e_i congruent mod 2).  Also w/r for W = P_{<=d} (3 variables) against S_4.
Writes results/m3.json."""
import sys, json, random, time, itertools
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *
p = PR; rng = random.Random(31); out = {}

def summation4(E, phi, dmax, classes_fn, nsamp_extra=40):
    mons_all = [m for m in itertools.product(range(dmax + 1), repeat=4)]
    groups = {}
    for m in mons_all: groups.setdefault(classes_fn(m), []).append(m)
    nmax = max(len(g) for g in groups.values()); samples = []
    while len(samples) < nmax + nsamp_extra:
        P1, P2, P3 = (E.random_point(rng) for _ in range(3))
        P4 = E.neg(E.add(E.add(P1, P2), P3))
        if P4 is None: continue
        u = [phi(*P) for P in (P1, P2, P3, P4)]
        if any(v is None for v in u): continue
        samples.append(u)
    pw = [[[pow(u[i], e, p) for e in range(dmax + 1)] for i in range(4)] for u in samples]
    res = []
    for cls, mons in groups.items():
        M = np.zeros((len(samples), len(mons)), dtype=np.int64)
        for j, m in enumerate(mons):
            M[:, j] = [pw[s][0][m[0]] * pw[s][1][m[1]] % p * pw[s][2][m[2]] % p * pw[s][3][m[3]] % p for s in range(len(samples))]
        ns = np_nullspace_mod(M, p)
        if ns: res.append((cls, [{mons[j]: int(v[j]) for j in range(len(mons)) if v[j]} for v in ns]))
    return res

def analyse(label, E, phi, classes_fn, dmax):
    t = time.time(); res = summation4(E, phi, dmax, classes_fn)
    assert res, 'no relation'
    cls, polys = res[0]; S = polys[0]
    co = coeffs_in_last(S, 4)
    n, seq, w = budget(co, p)
    rec = dict(label=label, degree_per_var=dmax, nullity=len(polys), n_coeffs=len(co), coef_degrees=[pdeg(c) for c in co],
               n=n, seq=seq, w=w, reach=1 / w, total_degree=pdeg(S), nterms=len(S), secs=round(time.time() - t, 1))
    out[label] = rec; print(json.dumps(rec), flush=True)
    return S, co

# Weierstrass x (a=b small), degree 4 per variable
E = Curve(5, 11, p)
S4w, cow = analyse('weierstrass_x_m3', E, lambda x, y: x, lambda m: 0, 4)
# twisted Edwards y on Montgomery v^2 = u^3 + A u^2 + u
A = 6; EM = Curve(1, 0, p, a2=A); inv = lambda v: pow(v, -1, p)
phi = lambda x, y: None if x == p - 1 else (x - 1) * inv(x + 1) % p
S4e, coe = analyse('edwards_y_m3', EM, phi, lambda m: ((m[0] + m[1]) % 2, (m[0] + m[2]) % 2, (m[0] + m[3]) % 2), 4)

# multi-equation at m=3: W = P_{<=d} in 3 variables vs S_4 (Weierstrass), r = dim W cap (S_R), S_R degree 12
X0 = rng.randrange(p)
def spec(F, X0, nv_x):
    o = {}
    for k, v in F.items(): o[k[:nv_x]] = (o.get(k[:nv_x], 0) + v * pow(X0, k[nv_x], p)) % p
    return {k: v for k, v in o.items() if v}
SR = spec(S4w, X0, 3); print('deg S4_R', pdeg(SR))
rows = []
for d in range(12, 16):
    W = [{m: 1} for m in monomials_upto(3, d)]
    n, seq, w = budget(W, p); r = r_of_W(W, SR, p, nv=3)
    rows.append(dict(d=d, dim=n, w=w, r=r, ratio=w / r if r else None, reach=r / w if r else 0)); print(rows[-1], flush=True)
out['m3_tot'] = rows
# Edwards y at m = 3: same with S4e
SRe = spec(S4e, X0, 3)
rows = []
for d in range(pdeg(SRe), pdeg(SRe) + 3):
    W = [{m: 1} for m in monomials_upto(3, d)]
    n, seq, w = budget(W, p); r = r_of_W(W, SRe, p, nv=3)
    rows.append(dict(d=d, dim=n, w=w, r=r, ratio=w / r if r else None, reach=r / w if r else 0)); print('edwards', rows[-1], flush=True)
out['m3_tot_edwards'] = rows
json.dump(out, open('/home/user/semaev-runs/SA-19/results/m3.json', 'w'), indent=1)
