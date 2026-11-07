import json, math, collections, numpy as np, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = [json.loads(l) for l in open('results/cells.jsonl')]
cells = collections.defaultdict(dict)
for r in rows: cells[(r['kind'], r['q'], r['n'], r['s'], r['t'])][r['S']] = r['rate']
def threshold(rates):
    """continuous S where success rate crosses 0.5, taken at the LAST S with rate>=0.5 (robust to isolated dips)"""
    Ss = sorted(rates); last = None
    for i, S in enumerate(Ss):
        if rates[S] >= 0.5: last = i
    if last is None: return Ss[0]-1.0
    if last == len(Ss)-1: return None
    r0, r1 = rates[Ss[last]], rates[Ss[last+1]]
    return Ss[last] + (r0-0.5)/(r0-r1)
out = []
keys = sorted({(q, n, s, t) for (k, q, n, s, t) in cells})
for (q, n, s, t) in keys:
    ff = cells.get(('ff', q, n, s, t)); z = cells.get(('z', q, n, s, t))
    if not ff or not z: continue
    a, b = threshold(ff), threshold(z)
    if a is None or b is None: continue
    dim = (s+1)**2; ks = [min(t, min(x, y)//2) for x in range(s+1) for y in range(s+1)]
    wsum = sum(x+y for x in range(s+1) for y in range(s+1))
    bits = n*math.log2(q)
    out.append(dict(q=q, n=n, s=s, t=t, dim=dim, bits=bits, wsum=wsum, asym=sum(ks)/wsum,
                    d_ff=a/(2*n), d_z=b/(2*n), loss=(a-b)/(2*n)))
json.dump(out, open('results/thresholds.json', 'w'), indent=1)
print('q n s t dim bits | delta_FF delta_Z loss')
for r in out: print(r['q'], r['n'], r['s'], r['t'], r['dim'], round(r['bits']), '|', round(r['d_ff'], 4), round(r['d_z'], 4), round(r['loss'], 4))
# ---- summary by (s,t)
print('\nmean by lattice:')
by = collections.defaultdict(list)
for r in out: by[(r['s'], r['t'])].append(r)
for k, v in sorted(by.items()):
    print(k, 'dim', v[0]['dim'], 'asym', round(v[0]['asym'], 4), 'FF', round(np.mean([x['d_ff'] for x in v]), 4), 'Z', round(np.mean([x['d_z'] for x in v]), 4),
          'loss', round(np.mean([x['loss'] for x in v]), 4), 'sd', round(np.std([x['loss'] for x in v]), 4))
# ---- carry-loss law candidates
rng = np.random.default_rng(0)
def feats(r, which):
    f = {'const': [1.0], 'ball': [1.0/r['n']], 'ball+lll': [1.0/r['n'], r['dim']/(r['wsum']*r['bits'])],
         'lll': [r['dim']/(r['wsum']*r['bits'])], 'const+lll': [1.0, r['dim']/(r['wsum']*r['bits'])]}[which]
    return f
res = {}
for which in ['const', 'ball', 'lll', 'ball+lll', 'const+lll']:
    X = np.array([feats(r, which) for r in out]); y = np.array([r['loss'] for r in out])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None); err = y - X@coef
    # leave-one-lattice-out
    e = []
    for k in by:
        tr = [i for i, r in enumerate(out) if (r['s'], r['t']) != k]; te = [i for i, r in enumerate(out) if (r['s'], r['t']) == k]
        c, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None); e += list(y[te]-X[te]@c)
    e = np.array(e)
    # bootstrap CI of coefficients
    bs = []
    for _ in range(500):
        ix = rng.integers(0, len(y), len(y)); c, *_ = np.linalg.lstsq(X[ix], y[ix], rcond=None); bs.append(c)
    bs = np.array(bs)
    res[which] = dict(coef=list(map(float, coef)), ci=[[float(np.percentile(bs[:, k], 2.5)), float(np.percentile(bs[:, k], 97.5))] for k in range(X.shape[1])],
                      rms_in=float(np.sqrt((err**2).mean())), max_in=float(np.abs(err).max()), loo_max=float(np.abs(e).max()),
                      loo_within_001=float((np.abs(e) <= 0.01).mean()), in_within_001=float((np.abs(err) <= 0.01).mean()))
    print('%-10s coef %s CI %s | in-sample rms %.4f max %.4f within0.01 %.2f | LOLO max %.4f within0.01 %.2f' % (which, np.round(coef, 4), np.round(res[which]['ci'], 4).tolist(), res[which]['rms_in'], res[which]['max_in'], res[which]['in_within_001'], res[which]['loo_max'], res[which]['loo_within_001']))
json.dump(res, open('results/law.json', 'w'), indent=1)
coef = np.array(res['ball+lll']['coef'])
# ---- large-n extrapolation per lattice: delta(n) = d_inf + c/n
print('\nextrapolation delta(n)=d_inf+c/n (pooled over q):')
ext = {}
for k, v in sorted(by.items()):
    row = {}
    for key in ('d_ff', 'd_z'):
        x = np.array([1/r['n'] for r in v]); y = np.array([r[key] for r in v]); A = np.vstack([np.ones_like(x), x]).T
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        bs = []
        for _ in range(500):
            ix = rng.integers(0, len(y), len(y)); cc, *_ = np.linalg.lstsq(A[ix], y[ix], rcond=None); bs.append(cc[0])
        row[key] = (float(c[0]), float(c[1]), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
    ext[str(k)] = row
    print(k, 'dim', v[0]['dim'], 'FF d_inf %.4f [%.4f,%.4f] slope %.2f | Z d_inf %.4f [%.4f,%.4f] slope %.2f' % (row['d_ff'][0], row['d_ff'][2], row['d_ff'][3], row['d_ff'][1], row['d_z'][0], row['d_z'][2], row['d_z'][3], row['d_z'][1]))
json.dump(ext, open('results/extrapolation.json', 'w'), indent=1)
# ---- figure
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
cols = {(2,1):'C0',(3,1):'C1',(4,2):'C2',(5,2):'C3',(6,3):'C4',(8,4):'C5'}
for k, v in sorted(by.items()):
    for r in v:
        ax[0].scatter(r['n'], r['d_ff'], marker='o', color=cols.get(k, 'k'), s=14)
        ax[0].scatter(r['n'], r['d_z'], marker='x', color=cols.get(k, 'k'), s=18)
    ax[0].plot([], [], color=cols.get(k, 'k'), label='s=%d,t=%d dim %d' % (k[0], k[1], v[0]['dim']))
ax[0].axhline(1/6, ls='--', c='gray'); ax[0].text(24, 1/6+0.003, 'asymptotic 1/6', fontsize=8)
ax[0].set_xlabel('n (degree of pi; p = q^n)'); ax[0].set_ylabel('threshold delta'); ax[0].set_title('o: function field, x: integer LLL'); ax[0].legend(fontsize=7)
sc = ax[1].scatter([1/r['n'] for r in out], [r['loss'] for r in out], c=[r['dim'] for r in out], s=14); plt.colorbar(sc, ax=ax[1], label='lattice dim')
xs = np.linspace(0.01, 0.045, 20); ax[1].plot(xs, xs, 'k--', lw=0.8, label='loss = 1/n'); ax[1].legend(fontsize=7)
ax[1].set_xlabel('1/n'); ax[1].set_ylabel('delta_FF - delta_Z'); ax[1].set_title('FF-minus-integer threshold gap')
plt.tight_layout(); plt.savefig('fig_threshold.png', dpi=130)
