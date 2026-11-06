"""Control (iii): anomalous curve (#E=p, CM by -3).  Smart's lift gives discrete logs in poly(log p); test whether this makes
the 2-decomposition oracle sub-B.  Oracle = (a) log-table scan (setup B Smart evaluations, query O(B)),
(b) pair-sum table (setup ~B^2, query O(1) lookup).  Output per-B setup / query CPU times and success."""
import sys, json, time, random
from common import *
from solvers import smart_psi
from anomalous import anomalous_curve

bits = int(sys.argv[1]); kmin, kmax = int(sys.argv[2]), int(sys.argv[3]); trials = int(sys.argv[4]); kpair = int(sys.argv[5]); out = sys.argv[6]
rng = random.Random(77)
p, a, b = anomalous_curve(bits, rng)
x = 1
while point(x, a, b, p) is None: x += 1
G = point(x, a, b, p)
psiG = smart_psi(G, a, b, p); iG = pow(psiG, -1, p)
def log(P): return smart_psi(P, a, b, p) * iG % p
# sanity: log of random multiple
k0 = rng.randrange(1, p); assert log(mul(k0, G, a, p)) == k0

rows = []
for k in range(kmin, kmax + 1):
    B = 2 ** k
    t0 = time.process_time()
    L = {}   # log -> x
    xs = []
    for xx in range(1, B + 1):
        P = point(xx, a, b, p)
        if P is None: continue
        l = log(P)
        L[l] = xx; L[(-l) % p] = xx; xs.append((xx, l))
    setup1 = time.process_time() - t0
    keys = list(L.keys())
    pair = None; setup2 = None
    if k <= kpair:
        t0 = time.process_time()
        pair = {}
        for i, l1 in enumerate(keys):
            for l2 in keys[i:]:
                pair[(l1 + l2) % p] = (L[l1], L[l2])
        setup2 = time.process_time() - t0
    q1 = []; q2 = []; qlog = []; s1 = s2 = 0
    for _ in range(trials):
        inst = plant_small_curve(p, B, a=a, b=b, rng=rng)
        xr = inst['xr']
        t0 = time.process_time()
        R = point(xr, a, b, p)
        lR = log(R)
        qlog.append(time.process_time() - t0)
        t0 = time.process_time()
        found = None
        for l1 in keys:
            if (lR - l1) % p in L:
                found = (L[l1], L[(lR - l1) % p]); break
        q1.append(time.process_time() - t0)
        s1 += found is not None and verify_decomp(found[0], found[1], xr, a, b, p, B)
        if pair is not None:
            t0 = time.process_time()
            lR = log(point(xr, a, b, p))
            f2 = pair.get(lR)
            q2.append(time.process_time() - t0)
            s2 += f2 is not None and verify_decomp(f2[0], f2[1], xr, a, b, p, B)
    rows.append(dict(bits=bits, k=k, B=B, nbase=len(xs), setup_scan=setup1, setup_pair=setup2, q_scan=q1, q_pair=q2, q_log=qlog, succ_scan=s1, succ_pair=s2, trials=trials))
    print(k, 'q_log %.5f' % (sum(qlog) / len(qlog)), 'setup_scan %.3f' % setup1, 'q_scan %.5f' % (sum(q1) / len(q1)), 'succ', s1, '| pair setup', setup2, 'q_pair', (sum(q2) / len(q2)) if q2 else None, 'succ', s2, flush=True)
    json.dump(rows, open(out, 'w'))
