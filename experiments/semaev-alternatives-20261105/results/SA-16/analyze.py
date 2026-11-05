"""Analyse raw sweeps: reach, exponent fits (bootstrap CI), control-vs-null comparison, figure + tables."""
import json, glob, math, random, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = random.Random(2026)
rows = []
for f in sorted(glob.glob('raw/*_*.json')):
    if 'smart' in f: continue
    rows += json.load(open(f))
# cell: (fam,bits,solver) -> list over k
cells = {}
for r in rows:
    cells.setdefault((r['fam'], r['bits'], r['solver']), []).append(r)
for key, v in list(cells.items()):
    m = {}
    for r in v:
        if r['k'] in m:
            q = m[r['k']]; q['succ'] += r['succ']; q['trials'] += r['trials']; q['vanish'] += r['vanish']; q['times'] = q['times'] + r['times']
        else:
            m[r['k']] = dict(r)
    cells[key] = [m[k] for k in sorted(m)]

THR = 0.5


def wilson(s, n, z=1.96):
    ph = s / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def fit_exponent(pts, nboot=2000):
    """pts: list of (k, times list, succ, trials).  cost = mean(times)/(succ/trials).  slope of log2(cost) vs k.
    Bootstrap: resample times per cell, success ~ Binomial(trials, observed rate) (min 1 success enforced to stay on region)."""
    ks = np.array([p[0] for p in pts], float)

    def slope(ys):
        return np.polyfit(ks, ys, 1)[0]
    ys = [math.log2(max(np.mean(p[1]), 1e-9) / (p[2] / p[3])) for p in pts]
    est = slope(ys)
    bs = []
    for _ in range(nboot):
        yb = []
        for k, t, s, n in pts:
            tt = [rng.choice(t) for _ in t]
            ss = max(1, sum(rng.random() < s / n for _ in range(n)))
            yb.append(math.log2(max(np.mean(tt), 1e-9) / (ss / n)))
        bs.append(slope(yb))
    bs.sort()
    return est, bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]


summary = []
for (fam, bits, sol), v in sorted(cells.items()):
    good = [r for r in v if r['succ'] / r['trials'] >= THR]
    reach_k = max([r['k'] for r in good], default=None)
    # contiguous region from smallest k where all succ>=THR
    region = []
    for r in v:
        if r['succ'] / r['trials'] >= THR: region.append(r)
        else:
            if region: break
    pts = [(r['k'], r['times'], r['succ'], r['trials']) for r in good]
    if len(pts) >= 5:
        est, lo, hi = fit_exponent(pts)
    else:
        est = lo = hi = None
    summary.append(dict(fam=fam, bits=bits, solver=sol, reach_k=reach_k, reach_delta=(reach_k / bits if reach_k else None),
                        npts=len(pts), slope=est, lo=lo, hi=hi,
                        rates={r['k']: r['succ'] / r['trials'] for r in v}, vanish={r['k']: r['vanish'] / r['trials'] for r in v}))

json.dump(summary, open('summary.json', 'w'), indent=1)

# null-vs-control table
NULL = {'C2': 'G', 'C3': 'G', 'C1': 'Gp'}
lines = []
lines.append('| family | bits | solver | reach 2^k (succ>=50%) | delta=k/bits | pts | exponent of cost vs B [95% CI] | null family reach k | gain over null (doublings) |')
lines.append('|---|---|---|---|---|---|---|---|---|')
S = {(s['fam'], s['bits'], s['solver']): s for s in summary}
for s in summary:
    if s['fam'] == 'ENUM':
        pass
    nullk = None
    nf = NULL.get(s['fam'])
    if nf and (nf, s['bits'], s['solver']) in S:
        nullk = S[(nf, s['bits'], s['solver'])]['reach_k']
    elif nf and s['solver'] in ('biv_rad_m1s0',):
        nullk = None
    gain = (s['reach_k'] - nullk) if (s['reach_k'] is not None and nullk is not None) else ('n/a' if nullk is None else ('-' ))
    ex = '%.2f [%.2f, %.2f]' % (s['slope'], s['lo'], s['hi']) if s['slope'] is not None else 'undefined (<5 pts with succ>=50%)'
    lines.append('| %s | %d | %s | %s | %s | %d | %s | %s | %s |' % (
        s['fam'], s['bits'], s['solver'], s['reach_k'], ('%.3f' % s['reach_delta']) if s['reach_delta'] else '-', s['npts'], ex,
        nullk if nullk is not None else '-', gain))
open('results_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

# figure: success rate vs k for each family (bits=128), main solvers
fams = [('G', 'generic G (a=0,b=7)'), ('Gp', 'generic Gp (large a,b)'), ('C1', 'control (i) degenerate conic'),
        ('C2', 'control (ii) R=[2]P1'), ('C3', 'control (iii) anomalous curve')]
fig, axs = plt.subplots(1, 5, figsize=(22, 4.2), sharey=True)
for ax, (fam, title) in zip(axs, fams):
    for (f, bits, sol), v in sorted(cells.items()):
        if f != fam or bits != 128: continue
        ax.plot([r['k'] for r in v], [r['succ'] / r['trials'] for r in v], marker='o', ms=3, label=sol)
    ax.axvline(128 / 12, color='gray', ls=':', lw=1)
    ax.set_title(title, fontsize=10); ax.set_xlabel('log2 B  (p = 128 bits)')
    ax.legend(fontsize=6)
axs[0].set_ylabel('recovery rate (20 trials)')
plt.tight_layout(); plt.savefig('fig_reach.png', dpi=130)


# ---------------- control (iii): Smart + table oracle
import os
if os.path.exists('raw/smart_128.json'):
    sm = json.load(open('raw/smart_128.json'))
    out = ['| quantity | exponent vs B [95% CI] | note |', '|---|---|---|']
    ks = np.array([r['k'] for r in sm], float)

    def sl(ys): return np.polyfit(ks, ys, 1)[0]
    def boot(series):  # series: list over k of list of samples (or scalars)
        ys = [math.log2(max(np.mean(s), 1e-9)) for s in series]
        est = sl(ys); bs = []
        for _ in range(1500):
            bs.append(sl([math.log2(max(np.mean([rng.choice(s) for _ in s]), 1e-9)) for s in series]))
        bs.sort(); return est, bs[int(.025 * 1500)], bs[int(.975 * 1500)]
    e = boot([r['q_log'] for r in sm]); out.append('| query time, Smart log of R only | %.2f [%.2f, %.2f] | poly(log p), independent of B |' % e)
    e = boot([r['q_scan'] for r in sm]); out.append('| query time, scan of log table (after log of R) | %.2f [%.2f, %.2f] | O(B) scan, early exit at first match |' % e)
    e = boot([[r['setup_scan']] for r in sm]); out.append('| setup time (B Smart evaluations) | %.2f [%.2f, %.2f] | single run per B |' % e)
    pr = [r for r in sm if r['q_pair']]
    if len(pr) >= 3:
        ks = np.array([r['k'] for r in pr], float)
        e = boot([r['q_pair'] for r in pr]); out.append('| query time, pair-sum table | %.2f [%.2f, %.2f] | O(1) lookup + 1 Smart log (k<=%d) |' % (e + (pr[-1]['k'],)))
        e = boot([[r['setup_pair']] for r in pr]); out.append('| setup time, pair-sum table | %.2f [%.2f, %.2f] | ~B^2 entries |' % e)
    out.append('')
    out.append('success (scan): ' + ', '.join('2^%d:%d/%d' % (r['k'], r['succ_scan'], r['trials']) for r in sm))
    out.append('success (pair): ' + ', '.join('2^%d:%d/%d' % (r['k'], r['succ_pair'], r['trials']) for r in sm if r['q_pair']))
    open('results_smart.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
