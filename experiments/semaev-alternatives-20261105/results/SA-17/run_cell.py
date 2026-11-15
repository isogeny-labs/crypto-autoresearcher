"""Scan S=D1+D2 for one cell (q,n,s,t) in both twins; append JSON lines to results/cells.jsonl"""
import sys, json, time, random, sympy
sys.path.insert(0, '.')
from lat import *
q, n, s, t, ntf, ntz = map(int, sys.argv[1:7])
tag = sys.argv[7] if len(sys.argv) > 7 else 'main'
KF = {3: 12, 5: 9, 7: 7}[q]
seed = hash((q, n, s, t)) % 10**6
rng = random.Random(seed); random.seed(seed)
F = Field(q, n); p = int(sympy.nextprime(q**n))
M, ks, pred = shift_params(s, t)
out = open('results/cells.jsonl', 'a')
def scan(kind):
    S = 5; fails = 0; ntr = ntf if kind == 'ff' else ntz
    while S <= 2*n*0.6 and fails < 3:
        rs = []
        t0 = time.time()
        for _ in range(ntr):
            rs.append(ff_trial(F, S, s, t, rng, KF) if kind == 'ff' else z_trial(q, n, p, S, s, t, rng))
        rate = sum(r['success'] for r in rs)/ntr
        rec = dict(tag=tag, kind=kind, q=q, n=n, bits=round(n*math.log2(q), 1), s=s, t=t, dim=len(M), S=S, delta=S/(2*n),
                   trials=ntr, rate=rate, nvan_mean=sum(r['nvan'] for r in rs)/ntr, tred_mean=sum(r['tred'] for r in rs)/ntr,
                   wall=time.time()-t0, pred_asym=pred)
        if kind == 'ff':
            rec.update(d2_mean=sum(r['d2'] for r in rs)/ntr, tn=t*n)
        out.write(json.dumps(rec)+'\n'); out.flush()
        fails = fails+1 if rate < 0.5 else 0
        S += 1
for kind in ('ff', 'z'): scan(kind)
