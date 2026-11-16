"""m=3 (S4) 5-dim form lattice thresholds, delta = S/(3n); theory 1/50."""
import json, collections, numpy as np
rows = [json.loads(l) for l in open('results/form5.jsonl')]
cells = collections.defaultdict(dict)
for r in rows: cells[(r['kind'], r['q'], r['n'])][r['S']] = r['rate']
def threshold(rates):
    Ss = sorted(rates); last = None
    for i, S in enumerate(Ss):
        if rates[S] >= 0.5: last = i
    if last is None or last == len(Ss)-1: return None
    r0, r1 = rates[Ss[last]], rates[Ss[last+1]]
    return Ss[last] + (r0-0.5)/(r0-r1)
out = []
for (q, n) in sorted({(q, n) for (_, q, n) in cells}):
    a = threshold(cells.get(('ff', q, n), {})); b = threshold(cells.get(('z', q, n), {}))
    out.append(dict(q=q, n=n, d_ff=None if a is None else a/(3*n), d_z=None if b is None else b/(3*n),
                    loss=None if a is None or b is None else (a-b)/(3*n)))
print('m=3 form lattice (theory 1/50 = 0.02): q n | delta_FF delta_Z loss  (n*delta_FF-n/50)')
for r in out: print(r['q'], r['n'], '|', *(None if r[k] is None else round(r[k], 4) for k in ('d_ff', 'd_z', 'loss')), '' if r['d_ff'] is None else round(r['n']*(r['d_ff']-0.02), 2))
rng = np.random.default_rng(2); ext = {}
for key in ('d_ff', 'd_z', 'loss'):
    v = [r for r in out if r[key] is not None]
    x = np.array([1/r['n'] for r in v]); y = np.array([r[key] for r in v]); A = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None); bs = []
    for _ in range(1000):
        ix = rng.integers(0, len(y), len(y))
        if len(set(ix)) < 2: continue
        cc, *_ = np.linalg.lstsq(A[ix], y[ix], rcond=None); bs.append(cc)
    bs = np.array(bs)
    ext[key] = dict(d_inf=float(c[0]), slope=float(c[1]), ci_inf=[float(np.percentile(bs[:, 0], 2.5)), float(np.percentile(bs[:, 0], 97.5))], npts=len(y))
    print('%-5s d_inf %.4f CI [%.4f, %.4f] slope %.3f (%d cells)' % (key, c[0], *ext[key]['ci_inf'], c[1], len(y)))
json.dump(dict(thresholds=out, extrapolation=ext), open('results/form5_thresholds.json', 'w'), indent=1)
