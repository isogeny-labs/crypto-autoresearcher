"""Thresholds of the 3-dim form lattice (form3.jsonl) and comparison with the box-lattice thresholds (v2)."""
import json, collections, numpy as np, sys
sys.path.insert(0, '/home/user/semaev-runs/SA-17')
rows = [json.loads(l) for l in open('results/form3.jsonl')]
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
    # theory (FF, exact): planted is unique minimum iff 9e < n roughly; e = D1-1, D1=ceil(S/2)
    out.append(dict(q=q, n=n, d_ff=None if a is None else a/(2*n), d_z=None if b is None else b/(2*n),
                    loss=None if (a is None or b is None) else (a-b)/(2*n)))
print('form lattice: q n | delta_FF delta_Z loss')
for r in out: print(r['q'], r['n'], '|', *(None if r[k] is None else round(r[k], 4) for k in ('d_ff', 'd_z', 'loss')))
box = {(r['q'], r['n'], r['s'], r['t']): r for r in json.load(open('results/v2_thresholds.json'))}
print('\nbox (v2) minus form, same (q,n):')
cmp_ = []
for r in out:
    for st in [(2, 1), (4, 2)]:
        b = box.get((r['q'], r['n'])+st)
        if b and r['d_ff'] is not None and r['d_z'] is not None:
            cmp_.append(dict(q=r['q'], n=r['n'], st=st, ff_box=b['d_ff'], ff_form=r['d_ff'], z_box=b['d_z'], z_form=r['d_z']))
            print(r['q'], r['n'], st, 'FF box %.4f form %.4f | Z box %.4f form %.4f' % (b['d_ff'], r['d_ff'], b['d_z'], r['d_z']))
rng = np.random.default_rng(1); ext = {}
for key in ('d_ff', 'd_z', 'loss'):
    v = [r for r in out if r[key] is not None]
    x = np.array([1/r['n'] for r in v]); y = np.array([r[key] for r in v]); A = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(A, y, rcond=None); bs = []
    for _ in range(1000):
        ix = rng.integers(0, len(y), len(y)); cc, *_ = np.linalg.lstsq(A[ix], y[ix], rcond=None); bs.append(cc)
    bs = np.array(bs)
    ext[key] = dict(d_inf=float(c[0]), slope=float(c[1]), ci_inf=[float(np.percentile(bs[:, 0], 2.5)), float(np.percentile(bs[:, 0], 97.5))],
                    ci_slope=[float(np.percentile(bs[:, 1], 2.5)), float(np.percentile(bs[:, 1], 97.5))], npts=len(y))
    print('%-5s d_inf %.4f CI [%.4f, %.4f]  slope %.3f CI [%.3f, %.3f]  (%d cells)' % (key, c[0], *ext[key]['ci_inf'], c[1], *ext[key]['ci_slope'], len(y)))
json.dump(dict(thresholds=out, compare_box=cmp_, extrapolation=ext), open('results/form3_thresholds.json', 'w'), indent=1)
