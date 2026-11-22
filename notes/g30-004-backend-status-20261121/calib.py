from sage.all import *
import json

def semireg_dreg(n, m, d=2):
    R = PowerSeriesRing(QQ, 't', default_prec=80)
    t = R.gen()
    s = (1 - t**d)**m / (1 - t)**n
    for k in range(1, 80):
        if s[k] <= 0:
            return k
    return None

def random_system(n, m, d, p, seed):
    set_random_seed(seed)
    R = PolynomialRing(GF(p), n, 'x')
    return [R.random_element(degree=d) for _ in range(m)]

def measure(polys, R):
    I = R.ideal(polys)
    t0 = walltime()
    G = I.groebner_basis()
    dt = walltime(t0)
    degs = [g.degree() for g in G if g != 0]
    return dict(maxdeg=int(max(degs)) if degs else 0, gbsize=int(len(G)),
                secs=round(float(dt), 3), dim=int(I.dimension()))

out = []
for n in (4, 5, 6):
    for extra in (1, 2, 3):
        m = n + extra
        polys = random_system(n, m, 2, 65521, seed=1000 + 10*n + extra)
        R = polys[0].parent()
        r = measure(polys, R)
        r.update(n=n, m=m, d=2, pred=semireg_dreg(n, m, 2))
        out.append(r)
        print(json.dumps(r, default=float), flush=True)
json.dump(out, open('/Volumes/SSD990/llm/tmp/opencode/g30-004/calib.json', 'w'),
          indent=1, default=float)
