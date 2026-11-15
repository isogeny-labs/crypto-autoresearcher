"""SA-19 family (a), systematic scan of even degree-2 coordinates phi_Q = 1/(x - x_Q) (poles at (Q)+(-Q)); the budget
depends only on the pole pair (affine changes of phi preserve the degree filtration).  Q ranges over points of exact
order k = 2..16 (and a generic point) on random curves y^2 = x^3 + a2 x^2 + a4 x + a6 over F_PR, found with PARI.
Writes results/coords3.json."""
import sys, json, random, time
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lib19 import *
from sympy import factorint as sympy_factorint
import cypari2
pari = cypari2.Pari()
p = PR; rng = random.Random(37); out = []
inv = lambda v: pow(v, -1, p)

def budget_of_pole(E, xQ, label, extra):
    phi = lambda x, y: None if x == xQ else inv(x - xQ)
    d, polys = minimal_summation_poly(E, phi, rng, p, dstart=2, dmaxmax=2)
    S = polys[0]; co = coeffs_in_last(S, 3); n, seq, w = budget(co, p)
    rec = dict(label=label, coef_degrees=[pdeg(c) for c in co], seq=seq, w=w, reach=1 / w, nterms=len(S), total_degree=pdeg(S)); rec.update(extra)
    out.append(rec); print(json.dumps(rec), flush=True)

found = {}
t0 = time.time()
tries = 0
while len(found) < 15 and tries < 400 and time.time() - t0 < 600:
    tries += 1
    a2, a4, a6 = rng.randrange(p), rng.randrange(p), rng.randrange(p)
    try:
        Ep = pari.ellinit([0, a2, 0, a4, a6], p)
    except Exception:
        continue
    if int(pari('(E)->E.disc')(Ep)) % p == 0: continue
    N = int(pari.ellcard(Ep))
    E = Curve(a4, a6, p, a2=a2)
    for k in range(2, 17):
        if k in found or N % k: continue
        # find a point of exact order k
        for _ in range(30):
            P = E.random_point(rng)
            Q = E.mul(N // k, P)
            if Q is None: continue
            ok = all(E.mul(k // q, Q) is not None for q in set(sympy_factorint(k)))
            if ok:
                found[k] = True
                budget_of_pole(E, Q[0], 'pole_order_%d' % k, dict(order=k, curve=[a2, a4, a6], N=N, Q=[Q[0], Q[1]]))
                break
    if 'generic' not in found:
        P = E.random_point(rng); found['generic'] = True
        budget_of_pole(E, P[0], 'pole_generic', dict(order='generic', curve=[a2, a4, a6], N=N))
json.dump(out, open('/home/user/semaev-runs/SA-19/results/coords3.json', 'w'), indent=1)
print('orders covered:', sorted(k for k in found if k != 'generic'), 'time', round(time.time() - t0, 1))
