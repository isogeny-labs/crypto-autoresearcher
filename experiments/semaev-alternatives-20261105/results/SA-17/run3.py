import sys, json, time, random, sympy
sys.path.insert(0, '.')
from lat3 import *
import math
q, n = int(sys.argv[1]), int(sys.argv[2]); ntr = int(sys.argv[3])
KF = {3: 12, 5: 9, 7: 7}[q]
rng = random.Random(q*1000+n); random.seed(q*1000+n)
F = Field(q, n); p = int(sympy.nextprime(q**n))
out = open('results/cells_m3.jsonl', 'a')
for kind in ('ff', 'z'):
    S = 6; fails = 0
    while S <= 3*n*0.5 and fails < 3:
        rs = []; t0 = time.time()
        for _ in range(ntr):
            Ds = [S//3 + (1 if i < S % 3 else 0) for i in range(3)]
            try:
                rs.append(ff_trial3(F, Ds, 4, 1, rng, KF) if kind == 'ff' else z_trial3(q, n, p, Ds, 4, 1, rng))
            except RuntimeError as e:
                rs.append(dict(success=False, nvan=0, tred=0))
        rate = sum(r['success'] for r in rs)/ntr
        out.write(json.dumps(dict(kind=kind, q=q, n=n, bits=round(n*math.log2(q), 1), s=4, t=1, dim=125, m=3, S=S, delta=S/(3*n),
                                  trials=ntr, rate=rate, nvan_mean=sum(r['nvan'] for r in rs)/ntr, wall=time.time()-t0))+'\n'); out.flush()
        fails = fails+1 if rate < 0.5 else 0
        S += 1
