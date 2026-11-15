import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
box = json.load(open('results/v2_thresholds.json'))
f3 = json.load(open('results/form3_thresholds.json'))['thresholds']; f5 = json.load(open('results/form5_thresholds.json'))['thresholds']
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
cols = {(2, 1): 'C0', (4, 2): 'C2', (6, 3): 'C4'}
for st, c in cols.items():
    v = [r for r in box if (r['s'], r['t']) == st]
    ax[0].scatter([r['n'] for r in v], [r['d_ff'] for r in v], color=c, marker='o', s=16, label='box s=%d,t=%d FF' % st)
    ax[0].scatter([r['n'] for r in v], [r['d_z'] for r in v], color=c, marker='x', s=20, label='box s=%d,t=%d Z' % st)
v = [r for r in f3 if r['n'] <= 64]
ax[0].scatter([r['n'] for r in v], [r['d_ff'] for r in v], facecolors='none', edgecolors='k', s=30, label='3-dim form lattice FF')
for y, t in [(1/2, 'existence 1/m = 1/2 (prereg FF prediction)'), (1/6, 'Jochemsz-May / bivariate wall 1/6'), (1/9, 'form-lattice uniqueness 1/9')]:
    ax[0].axhline(y, ls='--', c='gray', lw=0.8); ax[0].text(23, y+0.006, t, fontsize=7)
ax[0].set_ylim(0, 0.55); ax[0].set_xlabel('n (deg pi; p = nextprime(q^n))'); ax[0].set_ylabel('success threshold delta (per-variable)')
ax[0].set_title('m=2: FF (o) vs integer LLL (x), q=3,5,7'); ax[0].legend(fontsize=6, loc='center right')
for data, th, m, mk in [(f3, 1/9, 2, 'o'), (f5, 1/50, 3, 's')]:
    for key, c in [('d_ff', 'C3'), ('d_z', 'C0')]:
        v = [r for r in data if r[key] is not None]
        ax[1].scatter([1/r['n'] for r in v], [r[key]/th for r in v], color=c, marker=mk, s=18,
                      label='m=%d %s' % (m, 'F_q[t]/(pi) weak Popov' if key == 'd_ff' else 'F_p LLL'))
ax[1].axhline(1, c='k', lw=0.8); ax[1].set_xlabel('1/n'); ax[1].set_ylabel('threshold / theory (1/9 for m=2, 1/50 for m=3)')
ax[1].set_title('form lattices: both twins -> same limit (carry loss -> 0)'); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fig_mechanism.png', dpi=130)
