"""SA-21 analysis: alpha fits with two-level bootstrap, ratios to rho, pricing band, phase breakdown, lattice-arm model extrapolation."""
import json, math, random, collections, statistics as st, sys
import numpy as np
R = '/home/user/semaev-runs/SA-21/'
cur = {(c['fam'], c['k'], c['idx']): c for c in json.load(open(R + 'curves.json'))}
def load(f):
    try: return [json.loads(l) for l in open(R + 'results/' + f)]
    except FileNotFoundError: return []
rho = load('rho.jsonl'); pair = load('pair.jsonl'); lat = [r for r in load('lat.jsonl') if 'skipped' not in r]
skipped = [r for r in load('lat.jsonl') if 'skipped' in r]
import os
if os.path.exists(R + 'results/lat_rerun_E32.jsonl'):
    for l in open(R + 'results/lat_rerun_E32.jsonl'):
        if not l.strip(): continue
        rr = json.loads(l); rr['calib_rate'] = [x for x in lat if x['arm'] == 'latE' and x['k'] == 32 and x['idx'] == 0][0]['calib_rate']; rr['calib_F'] = 18; rr['rerun'] = True
        lat = [x for x in lat if not (x['arm'] == 'latE' and x['k'] == 32 and x['idx'] == 0 and x['target'] == 0 and x.get('timeout'))] + ([rr] if rr['ok'] else [x for x in lat if False])
latW = [r for r in lat if r['arm'] == 'latW']; latE = [r for r in lat if r['arm'] == 'latE']
for rs in (rho, pair, latW, latE):
    for r in rs: r['lg'] = math.log2(cur[(r['fam'], r['k'], r['idx'])]['l'])
FM = 6
def unpriced(r):
    """unpriced native work in field-operation units: lattice arms price their oracle at wall time instead (see cost())."""
    if r['arm'] in ('latW', 'latE'): return 0
    u = r['fmul'] - FM * r['adds']
    if r['arm'] == 'pair': u += r['attempts'] + r.get('table_entries', 0)
    return u
BAND = ['pi0', 'pi0.1', 'pi1']          # prereg band: 0, 0.1, 1 GAE per unpriced field op; lattice reduction and linear algebra at wall/t_GAE
PRICINGS = BAND + ['wall']              # 'wall' = total wall time / t_GAE, everything (setup, allocation, lookups), reported separately
def cost(r, pr):
    if pr == 'sec': return r['wall']
    if pr == 'wall': return r['wall'] / r['t_gae']
    base = r['adds'] + r.get('t_la', 0) / r['t_gae']
    if r['arm'] in ('latW', 'latE'): base += max(0.0, r['oracle_s'] - r['t_ver']) / r['t_gae']
    return base + {'pi0': 0.0, 'pi0.1': 0.1, 'pi1': 1.0}[pr] * unpriced(r)
def strata(rs):
    d = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rs: d[r['k']][r['idx']].append(r)
    return d
def size_stat(d, k, pr, rng=None):
    curves = list(d[k].keys())
    if rng: curves = [rng.choice(curves) for _ in curves]
    vals = []
    for c in curves:
        ts = d[k][c]
        if rng: ts = [rng.choice(ts) for _ in ts]
        vals += [cost(t, pr) for t in ts]
    lg = st.mean(t['lg'] for c in d[k] for t in d[k][c])
    return lg, st.mean(vals)
def fit(d, ks, pr, rng=None):
    xs, ys = [], []
    for k in ks:
        lg, m = size_stat(d, k, pr, rng); xs.append(lg); ys.append(math.log2(m))
    A = np.vstack([xs, np.ones(len(xs))]).T; sl, ic = np.linalg.lstsq(A, np.array(ys), rcond=None)[0]; return sl
def alpha(d, ks, pr, nboot=1500, seed=1):
    a = fit(d, ks, pr); rng = random.Random(seed)
    bs = sorted(fit(d, ks, pr, rng) for _ in range(nboot)); return a, bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]
def ratio(d1, d0, k, pr, nboot=1500, seed=2):
    r = size_stat(d1, k, pr)[1] / size_stat(d0, k, pr)[1]; rng = random.Random(seed)
    bs = sorted(size_stat(d1, k, pr, rng)[1] / size_stat(d0, k, pr, rng)[1] for _ in range(nboot)); return r, bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]
out = {}
dr = {'W': strata([r for r in rho if r['fam'] == 'W']), 'E': strata([r for r in rho if r['fam'] == 'E'])}
arms = {'pair': (strata(pair), 'W'), 'latW': (strata(latW), 'W'), 'latE': (strata(latE), 'E')}
allk = sorted(dr['W'].keys())
lines = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); lines.append(s)
P('# SA-21 analysis (auto-generated)'); P()
P('## rho alpha (all sizes k=20..40, and k>=28)')
rho_alpha = {}
for fam in 'WE':
    for pr in PRICINGS:
        for lab, ks in (('all', allk), ('k>=28', [k for k in allk if k >= 28])):
            a = alpha(dr[fam], ks, pr); rho_alpha[(fam, pr, lab)] = a
            P(f'rho {fam} {pr:6s} {lab:6s} alpha = {a[0]:.3f} [{a[1]:.3f}, {a[2]:.3f}]')
out['rho_alpha'] = {f'{k[0]}|{k[1]}|{k[2]}': v for k, v in rho_alpha.items()}
P(); P('## IC arms alpha (same size range as the arm; rho refit on the same sizes)')
arm_alpha = {}; verdict_rows = []
for name, (d, fam) in arms.items():
    ks = sorted(k for k in d if len(d[k]) >= 1)
    if len(ks) < 2: continue
    ranges = [('all', ks)]
    if name == 'pair': ranges.append(('k>=28', [k for k in ks if k >= 28]))
    for lab, kk in ranges:
        for pr in PRICINGS:
            a = alpha(d, kk, pr); ra = alpha(dr[fam], kk, pr)
            arm_alpha[(name, lab, pr)] = (a, ra)
            above = a[1] > ra[2]; below = a[2] < ra[1]
            P(f'{name:5s} {lab:6s} {pr:6s} sizes {kk[0]}..{kk[-1]} ({len(kk)} sizes, {math.log2(2**(kk[-1]-kk[0])):.0f} doublings): alpha = {a[0]:.3f} [{a[1]:.3f}, {a[2]:.3f}] ; rho on same sizes {ra[0]:.3f} [{ra[1]:.3f}, {ra[2]:.3f}] ; CI entirely above rho: {above}; entirely below: {below}')
out['arm_alpha'] = {f'{k[0]}|{k[1]}|{k[2]}': v for k, v in arm_alpha.items()}
P(); P('## Ratio arm/rho per size (mean cost ratio, bootstrap 95% CI), by pricing')
ratios = {}
for name, (d, fam) in arms.items():
    for k in sorted(d):
        row = []
        for pr in PRICINGS:
            r = ratio(d, dr[fam], k, pr); ratios[(name, k, pr)] = r
            row.append(f'{pr}: {r[0]:.3g} [{r[1]:.3g},{r[2]:.3g}]')
        n = sum(len(v) for v in d[k].values())
        P(f'{name:5s} k={k:2d} n={n:2d} ' + ' | '.join(row))
out['ratios'] = {f'{k[0]}|{k[1]}|{k[2]}': v for k, v in ratios.items()}
P(); P('## Mean absolute cost per size (wall seconds, adds)')
for name, (d, fam) in list(arms.items()) + [('rhoW', (dr['W'], 'W')), ('rhoE', (dr['E'], 'E'))]:
    for k in sorted(d):
        ts = [t for c in d[k].values() for t in c]
        P(f'{name:5s} k={k:2d} n={len(ts):2d} ok={sum(t["ok"] for t in ts)}/{len(ts)} wall={st.mean(t["wall"] for t in ts):.4g}s adds={st.mean(t["adds"] for t in ts):.4g} load0~{st.mean(t["load0"] for t in ts):.2f}')
# ---- verdict logic
P(); P('## Frozen-criteria evaluation')
def slower_everywhere(name):
    d, fam = arms[name]
    return all(ratios[(name, k, pr)][1] > 1 for k in d for pr in BAND if (name, k, pr) in ratios)
for name in arms:
    d, fam = arms[name]
    if not d: continue
    kk = sorted(d)
    ab = [arm_alpha[(name, 'all', pr)] for pr in BAND if (name, 'all', pr) in arm_alpha]
    allabove = all(a[0][1] > a[1][2] for a in ab); anybelow = any(a[0][2] < a[1][1] for a in ab)
    two_largest = kk[-2:]
    beat2 = all(ratios[(name, k, pr)][2] < 1 for k in two_largest for pr in BAND)
    P(f'{name}: alpha CI above rho under every pricing: {allabove}; alpha CI below rho under any pricing: {anybelow}; cheaper than rho (CI<1) at two largest sizes {two_largest} under every pricing: {beat2}; slower than rho (CI>1) at every measured size under every pricing: {slower_everywhere(name)}')
    verdict_rows.append((name, allabove, anybelow, beat2, slower_everywhere(name)))
out['verdict_rows'] = verdict_rows
# ---- phase breakdown
P(); P('## Phase breakdown (mean over solves, seconds and % of wall) at the largest size of each IC arm')
for name, (d, fam) in arms.items():
    if not d: continue
    k = max(d); ts = [t for c in d[k].values() for t in c]
    W = st.mean(t['wall'] for t in ts)
    ph = {'setup(FB, table, pool, chains)': st.mean(t['t_setup'] for t in ts), 'collection (walk stepping, GAE)': st.mean(t['t_coll'] for t in ts),
          'oracle (lookup or lattice, incl. y_R batch inv + verify adds)': st.mean(t['oracle_s'] for t in ts), 'linear algebra (elimination)': st.mean(t['t_la'] for t in ts), 'verification/descent ([k]G = Q check, in oracle if hit)': st.mean(t['t_ver'] for t in ts)}
    P(f'{name} k={k} (n={len(ts)}): wall {W:.4g}s; attempts {st.mean(t["attempts"] for t in ts):.4g}; hits {st.mean(t["hits"] for t in ts):.1f}; F {st.mean(t["F"] for t in ts):.1f}; table entries {st.mean(t.get("table_entries", 0) for t in ts):.3g}')
    for a, b in ph.items(): P(f'    {a}: {b:.4g}s ({100 * b / W:.1f}%)')
    P(f'    oracle calls {st.mean(t.get("oracle_calls", 0) for t in ts):.4g}, oracle seconds per call {st.mean(t["oracle_s"] for t in ts) / max(1, st.mean(t["attempts"] for t in ts)) * 1e9:.1f} ns per attempt (all included)')
# rho breakdown at 40
for fam in 'WE':
    k = max(dr[fam]); ts = [t for c in dr[fam][k].values() for t in c]
    P(f'rho {fam} k={k}: wall {st.mean(t["wall"] for t in ts):.4g}s steps {st.mean(t["steps"] for t in ts):.4g} setup {st.mean(t["t_setup"] for t in ts):.3g}s walk {st.mean(t["t_coll"] for t in ts):.3g}s')
# ---- lattice model extrapolation
P(); P('## Lattice-arm cost model extrapolated to the prereg sizes (MODEL, not measured)')
cal = load('calib.jsonl'); calk = collections.defaultdict(list)
for r in cal:
    if r['B'] > 0: calk[(r['fam'], r['k'])].append(r)
model = {}
for name, fam in (('latW', 'W'), ('latE', 'E')):
    d = arms[name][0]
    if not d: continue
    ts = [t for k in d for c in d[k].values() for t in c]
    # eta: hits per attempt = eta * F^2 * rate / l   (F = number of FB entries, rate = calibrated recovery)
    num = sum(t['hits'] for t in ts); den = sum(t['attempts'] * (t['F'] ** 2) * t['calib_rate'] / cur[(t['fam'], t['k'], t['idx'])]['l'] for t in ts)
    eta = num / den; rhoR = st.mean(t['hits'] / max(1, t['nv']) for t in ts)
    kmax = max(d); tt = [t for c in d[kmax].values() for t in c]; per_att = st.mean(t['wall'] / t['attempts'] for t in tt)
    P(f'{name}: fitted eta={eta:.3f} (hits per attempt = eta F^2 rate / l), hits per vertex {rhoR:.2f}, wall per attempt at k={kmax}: {per_att * 1e9:.0f} ns')
    for k in (20, 24, 28, 32, 36, 40):
        if (fam, k) not in calk: continue
        F = st.mean(r['F'] for r in calk[(fam, k)]); rate = st.mean(r['rate'] for r in calk[(fam, k)]); Bm = st.mean(r['B'] for r in calk[(fam, k)])
        l = st.mean(cur[(fam, k, i)]['l'] for i in range(3)); nv = F if fam == 'W' else F / 2
        h = eta * F ** 2 * rate / l; att = rhoR * nv / h; wallm = att * per_att
        rk = [t for c in dr[fam][k].values() for t in c]; rw = st.mean(t['wall'] for t in rk); ra = st.mean(t['adds'] for t in rk)
        model[(name, k)] = dict(F=F, B=Bm, rate=rate, attempts=att, wall=wallm, ratio_wall=wallm / rw, ratio_adds=att / ra)
        P(f'  k={k}: B*~{Bm:.0f} F~{F:.0f} rec~{rate:.2f} -> attempts {att:.3g}, wall {wallm:.3g}s ; rho wall {rw:.3g}s adds {ra:.3g} ; ratio wall {wallm / rw:.3g}, ratio adds-only {att / ra:.3g}')
out['model'] = {f'{k[0]}|{k[1]}': v for k, v in model.items()}
open(R + 'results/analysis.md', 'w').write('\n'.join(lines) + '\n')
json.dump(out, open(R + 'results/summary.json', 'w'), indent=1, default=str)
# ---- figure
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for name, (d, fam) in list(arms.items()) + [('rho W', (dr['W'], 'W')), ('rho E', (dr['E'], 'E'))]:
    ks = sorted(d); xs = [size_stat(d, k, 'wall')[0] for k in ks]
    ax[0].plot(xs, [size_stat(d, k, 'sec')[1] for k in ks], 'o-', label=name)
    ax[1].plot(xs, [size_stat(d, k, 'pi0')[1] for k in ks], 'o-', label=name)
ax[0].set_yscale('log'); ax[1].set_yscale('log'); ax[0].set_title('mean wall seconds (single thread)'); ax[1].set_title('mean group additions (pricing pi=0)')
for a in ax: a.set_xlabel('log2 group order'); a.legend(); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(R + 'fig_sa21.png', dpi=120)

# ---- Coppersmith (SA-20 t=2 Edwards lattice) arm: MODEL from measured per-call LLL time and measured reach
cop = [json.loads(l) for l in open(R + 'cop/results/cop.jsonl') if '"lll_calls"' in l] if True else []
P(); P('## IC-coppersmith-E (t=2, dim 13): measured per-call cost and reach (32-bit prime), then MODEL')
if cop:
    last = cop[-1]; tcall = last['lll_s'] / last['lll_calls']
    for r in cop:
        P(f"  delta={r['delta']}: planted recovery {r['succ']}/{r['n']}")
    P(f"  LLL-only wall per call (fpylll, dim 13): {tcall * 1e3:.3f} ms  (lower bound: excludes lattice build and root recovery)")
    d = arms['latE'][0]; tsE = [t for k in d for c in d[k].values() for t in c]
    num = sum(t['hits'] for t in tsE); den = sum(t['attempts'] * (t['F'] ** 2) * t['calib_rate'] / cur[(t['fam'], t['k'], t['idx'])]['l'] for t in tsE)
    eta = num / den; rhoR = st.mean(t['hits'] / max(1, t['nv']) for t in tsE)
    per_att_form = st.mean(t['wall'] / t['attempts'] for t in [t for c in d[max(d)].values() for t in c])
    for k in (20, 24, 28, 32, 36, 40):
        l = st.mean(cur[('E', k, i)]['l'] for i in range(3)); p_ = l * 4
        dl = 0.165 if k <= 32 else 0.150    # 50% crossing: measured at 32 bits (about 0.165), SA-20 at 64 bits (0.15); optimistic choice
        B = p_ ** dl; F = max(2.0, B); nv = F / 2
        h = eta * F ** 2 * 0.5 / l; att = rhoR * nv / h
        rk = [t for c in dr['E'][k].values() for t in c]; rw = st.mean(t['wall'] for t in rk)
        P(f'  k={k}: B_cop~{B:.0f}, F~{F:.0f} -> attempts {att:.3g}, wall >= {att * tcall:.3g}s (vs rho {rw:.3g}s: ratio >= {att * tcall / rw:.3g}); same-F form lattice would be {att * per_att_form:.3g}s')
open(R + 'results/analysis.md', 'w').write('\n'.join(lines) + '\n')
