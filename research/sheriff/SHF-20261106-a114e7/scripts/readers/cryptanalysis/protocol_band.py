"""Reader's own implementation of the frozen PROTOCOL.md band definition
(cryptanalysis:experiments/koblitz-n83-opcounts-20261023/PROTOCOL.md lines 71-100),
built from the decoded raw per-run stdout only (decode_runs.py output). It does not
import or execute the producer's band.py, analyze_v2.py or opcounts.py.

Unit per point p:
  S_p  = kS.phases.rank_stage + cS_p.phases.{setup, linear_algebra,
         between_linear_algebra_and_targets, targets}
  P_p  = same with kP / cP
  rT_p = charges_setup_and_solve
cost(w, b) = group + b * bounded + w * unpriced; b in {0, 104} (rho scalar muls).
Also: sanity that e2e == sum of non-diagnostic phases for every IC run; crossover
weights; a paired bootstrap re-implemented from the protocol text (resample the 20
points with replacement, ratio of means, 2.5/97.5 order statistics); and the
literal 'every counter charged' variant for sensitivity.

Usage: python3 -I protocol_band.py decoded_runs.json out.json [--perturb ARM:PANEL:PHASE:COUNTER:DELTA]
"""
import json, math, random, sys

src, out = sys.argv[1], sys.argv[2]
perturb = None
if len(sys.argv) > 4 and sys.argv[3] == '--perturb':
    a, p, ph, c, dlt = sys.argv[4].split(':')
    perturb = (a, p, ph, c, int(dlt))
W = (0.0, 0.1, 1.0)
GROUP = ('ec_add', 'ec_double')
FIELD = ('field_mul', 'field_sqr', 'field_inv', 'field_half_trace')
NOT_PRICED = ('ec_scalar_mul', 'la_row_eliminations') + FIELD
FROB = ('frobenius_x', 'fold_rotations', 'ec_frobenius')
RHO_UNPR = ('canonicalizations', 'partition_hashes', 'table_queries', 'table_inserts', 'failed_collisions')
UNIT_PHASES = ('setup', 'linear_algebra', 'between_linear_algebra_and_targets', 'targets')

rows = json.load(open(src))
ic, rho, ell = {}, {}, None
e2e_check = []
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        rec = d['records'][0]
        c = dict(rec['outcome']['charges_setup_and_solve'])
        if perturb and perturb[0] == 'rT' and perturb[1] == d['panel']:
            c[perturb[3]] += perturb[4]
        rho[d['panel']] = c
        ell = int(rec['subgroup_order'])
        continue
    oc = [r['op_counts'] for r in d['records'] if isinstance(r.get('op_counts'), dict) and 'phases' in r['op_counts']][0]
    ph = {k: dict(v) for k, v in oc['phases'].items()}
    if perturb and perturb[0] == d['arm'] and perturb[1] == d['panel']:
        ph[perturb[2]][perturb[3]] += perturb[4]
    tot = {k: sum(ph[q][k] for q in ph if q != 'after_targets_index_digest') for k in oc['end_to_end']}
    e2e_check.append((d['arm'], d['panel'], tot == oc['end_to_end']))
    ic[(d['arm'], d['panel'])] = {'ph': ph, 'kinds': oc['kinds']}

points = sorted(rho)

def unit(rank_arm, cold_arm, p):
    u = dict(ic[(rank_arm, 's000')]['ph']['rank_stage'])
    for q in UNIT_PHASES:
        for k, v in ic[(cold_arm, p)]['ph'][q].items():
            u[k] += v
    return u

def split_ic(u, model='protocol', frob_group=False):
    g = sum(u[k] for k in GROUP) + (sum(u[k] for k in FROB) if frob_group else 0)
    if model == 'protocol':
        skip = set(GROUP) | set(NOT_PRICED) | (set(FROB) if frob_group else set())
    else:  # literal: every counter except group and composite scalar mul
        skip = set(GROUP) | {'ec_scalar_mul'} | (set(FROB) if frob_group else set())
    return g, sum(v for k, v in u.items() if k not in skip), 0

def split_rho(c):
    return c['group_additions'], sum(c[k] for k in RHO_UNPR), c['scalar_multiplications']

def cost(parts, w, b):
    return parts[0] + b * parts[2] + w * parts[1]

def mean(v):
    return sum(v) / len(v)

res = {'ell': ell, 'points': points, 'e2e_equals_phase_sum_all': all(t[2] for t in e2e_check), 'models': {}}
BENDS = (0.0, 104.0)
for model, frob in (('protocol', False), ('protocol', True), ('literal', False)):
    tag = model + ('+frob_as_group' if frob else '')
    parts = {'S': {p: split_ic(unit('kS', 'cS', p), model, frob) for p in points},
             'P': {p: split_ic(unit('kP', 'cP', p), model, frob) for p in points},
             'rT': {p: split_rho(rho[p]) for p in points},
             # cold arms alone (cached factor logs, rank stage NOT included): diagnostic only
             'cS_only': {p: split_ic({k: sum(ic[('cS', p)]['ph'][q][k] for q in UNIT_PHASES) for k in ic[('cS', p)]['ph']['setup']}, model, frob) for p in points},
             'cP_only': {p: split_ic({k: sum(ic[('cP', p)]['ph'][q][k] for q in UNIT_PHASES) for k in ic[('cP', p)]['ph']['setup']}, model, frob) for p in points}}
    def ac(arm, w, b, sample=None):
        ch = points if sample is None else [points[i] for i in sample]
        return mean([cost(parts[arm][p], w, b) for p in ch])
    m = {'arms': {}, 'gap': {}, 'crossover_w': {}}
    for arm in parts:
        m['arms'][arm] = {'mean_group': mean([parts[arm][p][0] for p in points]),
                          'mean_unpriced': mean([parts[arm][p][1] for p in points]),
                          'mean_bounded': mean([parts[arm][p][2] for p in points]),
                          'cost': {'%g' % w: [ac(arm, w, b) for b in BENDS] for w in W}}
    # bootstrap re-implemented from protocol text: 10,000 draws; the seed is the one band.py states
    rng = random.Random(20261023)
    res_s = [[rng.randrange(len(points)) for _ in points] for _ in range(10000)]
    for arm in ('S', 'P', 'cS_only', 'cP_only'):
        m['gap'][arm] = {}
        for w in W:
            cells = []
            for b in BENDS:
                vals = sorted(ac(arm, w, b, s) / ac('rT', w, b, s) for s in res_s)
                cells.append({'b': b, 'ratio': ac(arm, w, b) / ac('rT', w, b),
                              'ci95': [vals[int(0.025 * 9999)], vals[int(0.975 * 9999)]]})
            m['gap'][arm]['%g' % w] = cells
        for b in BENDS:
            Pi, Ui = m['arms'][arm]['mean_group'], m['arms'][arm]['mean_unpriced']
            Pr, Ur, Br = m['arms']['rT']['mean_group'], m['arms']['rT']['mean_unpriced'], m['arms']['rT']['mean_bounded']
            m['crossover_w'].setdefault(arm, {})['b=%g' % b] = (Pr + b * Br - Pi) / (Ui - Ur)
    # S vs P
    m['S_over_P'] = {'%g' % w: ac('S', w, 0) / ac('P', w, 0) for w in W}
    res['models'][tag] = m
res['sqrt_ell'] = math.sqrt(ell)
res['perturb'] = perturb
json.dump(res, open(out, 'w'), indent=1, sort_keys=True)
print('e2e == phase sum for every IC run:', res['e2e_equals_phase_sum_all'])
for tag, m in res['models'].items():
    print('==', tag)
    for arm, a in m['arms'].items():
        print('  %-8s mean_group %.10g mean_unpriced %.10g mean_bounded %.4g | cost w0 %s w0.1 %s w1 %s' % (
            arm, a['mean_group'], a['mean_unpriced'], a['mean_bounded'],
            ['%.10g' % c for c in a['cost']['0']], ['%.10g' % c for c in a['cost']['0.1']], ['%.10g' % c for c in a['cost']['1']]))
    for arm, g in m['gap'].items():
        print('  gap %-8s ' % arm + ' | '.join('w=%s: ' % w + ' / '.join('%.6g [%.6g, %.6g]' % (c['ratio'], c['ci95'][0], c['ci95'][1]) for c in g[w]) for w in g))
    print('  crossover_w', {k: {b: '%.6g' % v for b, v in d.items()} for k, d in m['crossover_w'].items()})
    print('  S/P', {k: '%.6g' % v for k, v in m['S_over_P'].items()})
