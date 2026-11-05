# SA-07 resumed analysis: pools predecessor rows (5 s CPU cap, seeds 1-2, p ~ 2^28..2^40) and resume rows
# (20 s CPU cap, seeds 3-5, p ~ 2^28, 2^36). Exponent of SCIP node count in B, per (m, formulation):
#  (1) Tobit (right-censored normal regression of log2 nodes on log2 B; timeouts censored at nodes-at-cap),
#      bootstrap CI by resampling instances within each B level;
#  (2) OLS on solved instances only (biased low: survivors), same bootstrap;
#  (3) solved fraction per B. SCIP "infeasible"/spurious returns are checked against the exactly verified
#      planted solution and counted as numerical false negatives (excluded from (1),(2)).
import json, collections, math, random
import numpy as np
from scipy import optimize, stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sa07

rows = []
for f, ph in [('raw_m2.jsonl', 'pre'), ('raw_m3.jsonl', 'pre'), ('raw2_m2.jsonl', 'resume'), ('raw2_m3.jsonl', 'resume')]:
    for l in open(f):
        r = json.loads(l); r.setdefault('phase', ph); r.setdefault('cap', 5.0); rows.append(r)

def cls(r):
    s = str(r['status'])
    if s == 'skipped': return 'skipped'
    if s == 'timelimit': return 'timeout'
    if r['verified'] is True: return 'ok'
    if s.startswith('error'): return 'error'
    return 'false'

# exact check that every SCIP "false" case had a valid planted solution (recompute instance deterministically)
nfalse = 0; nfalse_ok = 0
for r in rows:
    if cls(r) == 'false':
        nfalse += 1
        rng = random.Random(1000 * r['seed'] + r['bits'] * 7 + r['B'])
        xs, xR = sa07.plant(r['p'], r['m'], r['B'], rng)
        if sa07.verify(r['p'], r['m'], xs, xR): nfalse_ok += 1

def tobit_fit(pts):
    # pts: (log2B, log2nodes, censored_bool)
    x = np.array([a for a, _, _ in pts]); y = np.array([b for _, b, _ in pts]); c = np.array([k for _, _, k in pts])
    if len(set(x)) < 2: return None
    A = np.vstack([np.ones_like(x), x]).T
    b0 = np.linalg.lstsq(A, y, rcond=None)[0]
    def nll(th):
        a, b, ls = th; s = math.exp(ls); mu = a + b * x
        ll = np.where(c, stats.norm.logsf(y, mu, s), stats.norm.logpdf(y, mu, s))
        return -ll.sum()
    res = optimize.minimize(nll, [b0[0], b0[1], 1.0], method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-4, fatol=1e-6))
    return res.x[1]

def ols_fit(pts):
    x = np.array([a for a, _, _ in pts]); y = np.array([b for _, b, _ in pts])
    if len(set(x)) < 2: return None
    return np.polyfit(x, y, 1)[0]

def boot(pts, fn, n, seed=0):
    rng = random.Random(seed)
    est = fn(pts)
    if est is None: return None
    byB = collections.defaultdict(list)
    for p in pts: byB[p[0]].append(p)
    out = []
    for _ in range(n):
        q = [rng.choice(v) for v in byB.values() for _ in v]
        e = fn(q)
        if e is not None: out.append(e)
    out.sort()
    return est, out[int(.025 * len(out))], out[int(.975 * len(out)) - 1], len(byB)

def box(m, B): return math.comb(B + m - 1, m)

fits = ["| m | formulation | estimator | exponent | 95% bootstrap CI | B levels | points (solved/censored) |", "|--|--|--|--|--|--|--|"]
summary = {}
for m in [2, 3]:
    for form in ['raw', 'lll', 'vieta']:
        rs = [r for r in rows if r['m'] == m and r['form'] == form and cls(r) in ('ok', 'timeout')]
        pts = [(math.log2(r['B']), math.log2(max(r['nodes'], 1)), cls(r) == 'timeout') for r in rs]
        ns = sum(1 for p in pts if not p[2]); nc = len(pts) - ns
        t = boot(pts, tobit_fit, 300)
        o = boot([p for p in pts if not p[2]], ols_fit, 1000)
        summary[(m, form)] = (t, o)
        for name, b, npts in [('Tobit (timeouts right-censored)', t, f'{ns}/{nc}'), ('OLS solved only', o, f'{ns}/0')]:
            if b: fits.append(f"| {m} | {form} | {name} | {b[0]:.2f} | [{b[1]:.2f}, {b[2]:.2f}] | {b[3]} | {npts} |")
            else: fits.append(f"| {m} | {form} | {name} | n/a | n/a | - | {npts} |")

# per-B table pooled over primes and phases
tab = ["| m | form | B | box size C(B+m-1,m) | n run | solved | solved at 1 node | timeout | SCIP false-infeasible | skipped | median nodes (solved) | median nodes at timeout | min nodes at timeout / box |",
       "|--|--|--|--|--|--|--|--|--|--|--|--|--|"]
for m in [2, 3]:
    for form in ['raw', 'lll', 'vieta']:
        byB = collections.defaultdict(list)
        for r in rows:
            if r['m'] == m and r['form'] == form: byB[r['B']].append(r)
        for B in sorted(byB):
            rs = byB[B]; c = collections.Counter(cls(r) for r in rs)
            ok = [r['nodes'] for r in rs if cls(r) == 'ok']; to = [r['nodes'] for r in rs if cls(r) == 'timeout']
            one = sum(1 for v in ok if v <= 1)
            mo = f"{np.median(ok):.0f}" if ok else '-'; mt = f"{np.median(to):.0f}" if to else '-'
            rt = f"{min(to)/box(m,B):.1f}" if to else '-'
            tab.append(f"| {m} | {form} | {B} | {box(m,B)} | {len(rs)-c['skipped']} | {c['ok']} | {one} | {c['timeout']} | {c['false']} | {c['skipped']} | {mo} | {mt} | {rt} |")

# resume-phase only (uniform 20 s cap) solved fractions
res_tab = ["| m | form | B | solved / run (20 s cap, seeds 3-5, p~2^28,2^36) |", "|--|--|--|--|"]
for m in [2, 3]:
    for form in ['raw', 'lll', 'vieta']:
        byB = collections.defaultdict(list)
        for r in rows:
            if r['m'] == m and r['form'] == form and r['phase'] == 'resume' and cls(r) != 'skipped': byB[r['B']].append(r)
        for B in sorted(byB):
            rs = byB[B]; res_tab.append(f"| {m} | {form} | {B} | {sum(cls(r)=='ok' for r in rs)}/{len(rs)} |")

tot = collections.Counter(cls(r) for r in rows)
hdr = (f"Rows: {len(rows)} ({dict(tot)}). SCIP false negatives (infeasible/spurious although planted solution exists): "
       f"{nfalse}, planted solution re-verified exactly in {nfalse_ok}/{nfalse}.\n")
open('fits_table.md', 'w').write('# SA-07 exponent fits (node count vs B), pooled over primes and both phases\n\n' + hdr + '\n' + '\n'.join(fits) + '\n')
open('results_table.md', 'w').write('# SA-07 per-B results, pooled over primes and both phases\n\n' + hdr + '\n' + '\n'.join(tab) + '\n\n## Resume phase only\n\n' + '\n'.join(res_tab) + '\n')

fig, axs = plt.subplots(2, 3, figsize=(13, 7.5), sharey='row')
for i, m in enumerate([2, 3]):
    for j, form in enumerate(['raw', 'lll', 'vieta']):
        ax = axs[i][j]
        rs = [r for r in rows if r['m'] == m and r['form'] == form]
        jit = lambda r: r['B'] * (1 + 0.06 * (r['seed'] - 3))
        ok = [r for r in rs if cls(r) == 'ok']; to = [r for r in rs if cls(r) == 'timeout']; fa = [r for r in rs if cls(r) == 'false']
        ax.scatter([jit(r) for r in ok], [max(r['nodes'], 1) for r in ok], s=16, c='C0', label='solved (verified)')
        ax.scatter([jit(r) for r in to], [max(r['nodes'], 1) for r in to], s=22, marker='^', c='C3', label='timeout (lower bound)')
        if fa: ax.scatter([jit(r) for r in fa], [max(r['nodes'], 1) for r in fa], s=22, marker='x', c='k', label='SCIP false infeasible')
        Bs = sorted(set(r['B'] for r in rs))
        ax.plot(Bs, [box(m, B) for B in Bs], 'k--', lw=1, label='box size C(B+m-1,m)')
        t, o = summary[(m, form)]
        ttl = f"m={m} {form}"
        if t: ttl += f"  Tobit {t[0]:.2f} [{t[1]:.2f},{t[2]:.2f}]"
        ax.set_title(ttl, fontsize=9)
        ax.set_xscale('log', base=2); ax.set_yscale('log'); ax.set_xlabel('B'); ax.set_ylabel('SCIP nodes')
        ax.legend(fontsize=6, loc='lower right')
plt.suptitle('SA-07: SCIP B&B nodes vs box bound B (toy scale; caps 5 s / 20 s CPU)', fontsize=10)
plt.tight_layout(); plt.savefig('fig_nodes.png', dpi=110)
print(hdr); print('\n'.join(fits)); print('\n'.join(tab)); print('\n'.join(res_tab))
