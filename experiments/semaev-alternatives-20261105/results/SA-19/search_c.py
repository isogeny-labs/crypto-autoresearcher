"""SA-19 family (c): multi-equation form lattices at modulus p.  For a coefficient space W (fixed polynomials in
x1,x2), r(W) = dim W cap (S_R) congruences, effective budget w(W)/r(W), predicted reach r/w.
Families: P_{<=d}, boxes [0,2+h]^2, x-side spans of multiplier sets {x^alpha X^j} S3 (Coppersmith k=1 shapes),
random sparse multipliers, exhaustive small monomial sets, and a hill climb over monomial sets.
Writes results/search_c.json."""
import sys, json, random, time, itertools
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *

p = PR; rng = random.Random(1907); a, b = 5, 11
MODE = sys.argv[1] if len(sys.argv) > 1 else 'w'
if MODE == 'w':
    S3 = S3_poly(a, b, p)
else:   # twisted Edwards y on Montgomery v^2 = u^3 + 6u^2 + u: interpolated summation polynomial (degree 2 per variable)
    EM = Curve(1, 0, p, a2=6); inv = lambda v: pow(v, -1, p)
    d_, polys_ = minimal_summation_poly(EM, lambda x, y: None if x == p - 1 else (x - 1) * inv(x + 1) % p, rng, p, dstart=2, dmaxmax=2)
    S3 = polys_[0]; print('Edwards S3 terms', len(S3), 'coefficient degree sequence', budget(coeffs_in_last(S3, 3), p))
OUT = '/home/user/semaev-runs/SA-19/results/search_c%s.json' % ('' if MODE == 'w' else '_ed')
X0 = rng.randrange(p)
def spec(F, X0, nv_x=2):
    out = {}
    for k, v in F.items(): out[k[:nv_x]] = (out.get(k[:nv_x], 0) + v * pow(X0, k[nv_x], p)) % p
    return {k: v for k, v in out.items() if v}
SR = spec(S3, X0); SR2 = spec(S3, rng.randrange(p))
res = {}
def record(fam, key, W, extra=None):
    n, seq, w = budget(W, p); r = r_of_W(W, SR, p); r2 = r_of_W(W, SR2, p)
    rec = dict(family=fam, key=str(key), dim=n, w=w, r=r, r_check=r2, ratio=(w / r if r else None), reach=(r / w if r else 0))
    if extra: rec.update(extra)
    res.setdefault(fam, []).append(rec)
    return rec

t0 = time.time()
# 1. total-degree spaces and boxes
for d in range(4, 13): record('tot', d, [{m: 1} for m in monomials_upto(2, d)])
for h in range(0, 6): record('box', h, [{(i, j): 1} for i in range(3 + h) for j in range(3 + h)])
# rectangles [0,2+h1] x [0,2+h2]
for h1 in range(0, 5):
    for h2 in range(h1, 6): record('rect', (h1, h2), [{(i, j): 1} for i in range(3 + h1) for j in range(3 + h2)])
print('tot/box done', time.time() - t0, flush=True)

# 2. x-side spans of multiplier sets {x^alpha X^j : |alpha| <= dx, j <= dX} S3  (Coppersmith k=1 shapes)
def xside_of_mults(mults):
    polys = [pmul(H, S3, p) for H in mults]
    W = []
    for F in polys: W += xside_span(F, 2, p)
    return W
for dx in range(0, 4):
    for dX in range(0, 4):
        mults = [{(al[0], al[1], j): 1} for al in monomials_upto(2, dx) for j in range(dX + 1)]
        record('mult_tot', (dx, dX), xside_of_mults(mults))
for bx in range(0, 3):
    for dX in range(0, 3):
        mults = [{(i, j, l): 1} for i in range(bx + 1) for j in range(bx + 1) for l in range(dX + 1)]
        record('mult_box', (bx, dX), xside_of_mults(mults))
print('mult done', time.time() - t0, flush=True)

# 3. random sparse multiplier sets (coefficients in {-1,0,1} or random) : k multipliers each with t terms
best_rand = None
for trial in range(600):
    k = rng.randrange(1, 4); t = rng.randrange(1, 4); dx = rng.randrange(0, 3); dX = rng.randrange(0, 3)
    mults = []
    for _ in range(k):
        H = {}
        for _ in range(t):
            al = rng.choice(monomials_upto(2, dx)); j = rng.randrange(dX + 1)
            H[(al[0], al[1], j)] = rng.choice([1, p - 1]) if rng.random() < 0.7 else rng.randrange(1, p)
        if H: mults.append(H)
    rec = record('rand_mult', trial, xside_of_mults(mults), dict(k=k, t=t, dx=dx, dX=dX))
    if rec['r'] and (best_rand is None or rec['ratio'] < best_rand['ratio']): best_rand = rec
print('random multipliers: best ratio', best_rand, time.time() - t0, flush=True)

# 4. exhaustive monomial sets: the 9 box monomials (needed for r >= 1 at degree <= 4) plus up to 5 extra monomials of degree 5
box9 = [(i, j) for i in range(3) for j in range(3)]
extra5 = [m for m in monomials_upto(2, 5) if m not in box9]
best_ex = None; cnt = 0
for k in range(0, 6):
    for add in itertools.combinations(extra5, k):
        sub = box9 + list(add); W = [{m: 1} for m in sub]
        r = r_of_W(W, SR, p); cnt += 1
        if r:
            w = sum(sum(m) for m in sub)
            if best_ex is None or w / r < best_ex[0]: best_ex = (w / r, sub, r, w)
res['exhaustive_box9_plus_deg5'] = dict(count=cnt, best_ratio=best_ex[0], best_set=[list(m) for m in best_ex[1]], r=best_ex[2], w=best_ex[3])
print('exhaustive box9 + deg-5 subsets:', res['exhaustive_box9_plus_deg5'], time.time() - t0, flush=True)

# 5. hill climb over monomial sets within degree <= 8, objective w/r (r >= 1), 12 restarts
mons8 = monomials_upto(2, 8)
def ratio_of(sub):
    W = [{m: 1} for m in sub]; r = r_of_W(W, SR, p)
    return (sum(sum(m) for m in sub) / r if r else 1e9), r
hc = []
for restart in range(12):
    cur = set(rng.sample(mons8, rng.randrange(6, 20))) | {(2, 2), (0, 0), (1, 1), (2, 0), (0, 2), (1, 0), (0, 1), (2, 1), (1, 2)}
    cur_val, cur_r = ratio_of(cur); improved = True; steps = 0
    while improved and steps < 200:
        improved = False; steps += 1
        cands = [cur ^ {m} for m in mons8]
        rng.shuffle(cands)
        for c in cands:
            if len(c) < 3: continue
            v, r = ratio_of(c)
            if v < cur_val - 1e-9:
                cur, cur_val, cur_r = c, v, r; improved = True; break
    hc.append(dict(restart=restart, ratio=cur_val, r=cur_r, size=len(cur), degs=sorted(sum(m) for m in cur)))
    print('hill climb', restart, round(cur_val, 3), 'r', cur_r, 'size', len(cur), time.time() - t0, flush=True)
res['hill_climb'] = hc
json.dump(res, open(OUT, 'w'), indent=1)
print('min ratio per family:')
for fam, rows in res.items():
    if isinstance(rows, list) and rows and 'ratio' in rows[0]:
        ok = [r for r in rows if r['r']]
        m = min(ok, key=lambda r: r['ratio']) if ok else None
        print(fam, m)
