"""Blind re-derivation of the crypto:AGENTS.md section 5a band for the n=83 counted row.

Inputs: only decoded raw per-run stdout (decode_runs.py output). No producer analysis
script, band.md, counts.json, baselines.json or BASELINES.md is read here.

Model (reader's own literal reading of section 5a):
  cost(w) = priced_group_ops + w * sum(every unpriced operation counter)
  IC arms: priced = ec_add + ec_double (kind 'group'); ec_scalar_mul (group_composite)
    is not charged again because its adds/doubles are already in ec_add/ec_double
    (checked: LA phase has 600 scalar muls ~ 30.5k doubles + 15.2k adds);
    ec_add_trivial (group_trivial) not charged; every counter of kind native,
    native_grouping, field or endomorphism is charged w per count.
  rho (rT): priced = group_additions; unpriced = canonicalizations + partition_hashes
    + table_inserts + table_queries + failed_collisions (scalar_multiplications are
    composite; reported as a sensitivity).
  S = cost / sqrt(subgroup order).
Variants are reported for sensitivity. Usage:
  python3 -I blind_band.py decoded_runs.json out.json [--perturb ARM:PANEL:COUNTER:DELTA]
"""
import json, math, statistics as st, sys

src, out = sys.argv[1], sys.argv[2]
perturb = None
if len(sys.argv) > 4 and sys.argv[3] == '--perturb':
    a, p, c, dlt = sys.argv[4].split(':')
    perturb = (a, p, c, int(dlt))
W = [0.0, 0.1, 1.0]
rows = json.load(open(src))

def summary_rec(d):
    for rec in d['records']:
        oc = rec.get('op_counts')
        if isinstance(oc, dict) and 'end_to_end' in oc:
            return rec, oc
    raise SystemExit('no summary op_counts in ' + d['arm'] + d['panel'])

ic, rho = {}, {}
ell = None
for x in rows:
    d = x['decoded']
    if d['returncode'] != 0 or d['issues']:
        raise SystemExit('nonzero rc/issues in %s %s' % (d['arm'], d['panel']))
    if d['arm'] == 'rT':
        rec = d['records'][0]
        c = dict(rec['outcome']['charges_setup_and_solve'])
        if perturb and perturb[0] == 'rT' and perturb[1] == d['panel']:
            c[perturb[2]] += perturb[3]
        ell_here = int(rec['subgroup_order'])
        ell = ell or ell_here
        assert ell == ell_here
        rho[d['panel']] = {'c': c, 'prep': rec['preparation_charges'],
                           'scalar': rec['recovered_scalar'],
                           'replay_ok': rec['generic_scalar_replay_verified'],
                           'status': rec['status']}
    else:
        rec, oc = summary_rec(d)
        e2e = dict(oc['end_to_end'])
        if perturb and perturb[0] == d['arm'] and perturb[1] == d['panel']:
            e2e[perturb[2]] += perturb[3]
        tgt = d['records'][0]
        ic[(d['arm'], d['panel'])] = {'e2e': e2e, 'kinds': oc['kinds'], 'phases': oc['phases'],
                                      'scalar': tgt['recovered_scalar'],
                                      'targets_solved': rec.get('targets_solved'),
                                      'targets_failed': rec.get('targets_failed')}

sq = math.sqrt(ell)

def ic_cost(e, kinds, w, variant='lit'):
    priced = e['ec_add'] + e['ec_double']
    unpr = 0
    for k, v in e.items():
        kd = kinds[k]
        if kd == 'group':
            continue
        if kd in ('group_trivial', 'group_composite'):
            if variant in ('charge_trivial_composite_at_w', 'no_field_charge_tc'):
                unpr += v
            continue
        if variant == 'no_endomorphism' and kd == 'endomorphism':
            continue
        if variant == 'no_s3_composite' and k == 's3_root_solves':
            continue
        if variant in ('no_field', 'no_field_charge_tc') and kd == 'field':
            continue
        unpr += v
    return priced + w * unpr, priced, unpr

def rho_cost(c, w, variant='lit'):
    priced = c['group_additions']
    unpr = c['canonicalizations'] + c['partition_hashes'] + c['table_inserts'] + c['table_queries'] + c['failed_collisions']
    if variant == 'charge_scalar_mul_at_w':
        unpr += c['scalar_multiplications']
    return priced + w * unpr, priced, unpr

res = {'ell': ell, 'sqrt_ell': sq, 'n_rho_panels': len(rho), 'weights': W, 'cells': {}, 'variants': {}}
rho_panels = sorted(rho)

def rho_mean(w, variant='lit'):
    return st.mean(rho_cost(rho[p]['c'], w, variant)[0] for p in rho_panels)

def arm_mean(arm, w, variant='lit'):
    keys = sorted(k for k in ic if k[0] == arm)
    return st.mean(ic_cost(ic[k]['e2e'], ic[k]['kinds'], w, variant)[0] for k in keys), len(keys)

for variant_ic, variant_rho in [('lit', 'lit'), ('charge_trivial_composite_at_w', 'charge_scalar_mul_at_w'),
                                ('no_endomorphism', 'lit'), ('no_s3_composite', 'lit'),
                                ('no_field', 'lit'), ('no_field_charge_tc', 'charge_scalar_mul_at_w')]:
    tag = variant_ic + '|' + variant_rho
    cells = {}
    for w in W:
        rT = rho_mean(w, variant_rho)
        cells_w = {'rT_mean_cost': rT, 'rT_S': rT / sq}
        for arm in ('kS', 'kP', 'cS', 'cP'):
            m, nk = arm_mean(arm, w, variant_ic)
            cells_w[arm] = {'n_runs': nk, 'mean_cost': m, 'S': m / sq, 'ratio_to_rT_mean': m / rT}
        cells[str(w)] = cells_w
    res['variants'][tag] = cells
res['cells'] = res['variants']['lit|lit']

# per-arm components (lit)
comp = {}
for arm in ('kS', 'kP', 'cS', 'cP'):
    keys = sorted(k for k in ic if k[0] == arm)
    pr = [ic_cost(ic[k]['e2e'], ic[k]['kinds'], 0)[1] for k in keys]
    up = [ic_cost(ic[k]['e2e'], ic[k]['kinds'], 0)[2] for k in keys]
    comp[arm] = {'priced_mean': st.mean(pr), 'unpriced_mean': st.mean(up), 'priced_set': sorted(set(pr)),
                 'unpriced_min': min(up), 'unpriced_max': max(up), 'n': len(keys),
                 'unpriced_by_counter': {c: st.mean(ic[k]['e2e'][c] for k in keys)
                                         for c in ic[keys[0]]['e2e'] if ic[keys[0]]['kinds'][c] not in ('group',)}}
rp = [rho_cost(rho[p]['c'], 0)[1] for p in rho_panels]
ru = [rho_cost(rho[p]['c'], 0)[2] for p in rho_panels]
comp['rT'] = {'priced_mean': st.mean(rp), 'unpriced_mean': st.mean(ru), 'priced_median': st.median(rp),
              'n': len(rp), 'unpriced_by_counter': {c: st.mean(rho[p]['c'][c] for p in rho_panels)
                                                     for c in rho[rho_panels[0]]['c']}}
res['components'] = comp

# crossover weights w* where IC mean cost == rT mean cost: P_ic + w U_ic = P_r + w U_r
cross = {}
for arm in ('kS', 'kP', 'cS', 'cP'):
    Pi, Ui = comp[arm]['priced_mean'], comp[arm]['unpriced_mean']
    Pr, Ur = comp['rT']['priced_mean'], comp['rT']['unpriced_mean']
    cross[arm] = (Pr - Pi) / (Ui - Ur) if Ui != Ur else None
res['crossover_w_vs_rT_mean'] = cross
cross_nf = {}
for arm in ('kS', 'kP', 'cS', 'cP'):
    keys = sorted(k for k in ic if k[0] == arm)
    Pi = st.mean(ic_cost(ic[k]['e2e'], ic[k]['kinds'], 0, 'no_field')[1] for k in keys)
    Ui = st.mean(ic_cost(ic[k]['e2e'], ic[k]['kinds'], 0, 'no_field')[2] for k in keys)
    Pr, Ur = comp['rT']['priced_mean'], comp['rT']['unpriced_mean']
    cross_nf[arm] = (Pr - Pi) / (Ui - Ur)
res['crossover_w_vs_rT_mean_no_field'] = cross_nf

# paired per panel (cold arms share panels with rT); answers equal?
paired = {}
for arm in ('cS', 'cP'):
    rat = {str(w): [] for w in W}
    same = 0
    for p in rho_panels:
        if (arm, p) not in ic:
            continue
        same += int(str(ic[(arm, p)]['scalar']) == str(rho[p]['scalar']))
        for w in W:
            rat[str(w)].append(ic_cost(ic[(arm, p)]['e2e'], ic[(arm, p)]['kinds'], w)[0] / rho_cost(rho[p]['c'], w)[0])
    paired[arm] = {'answers_equal_to_rT': same,
                   'paired_ratio_median': {w: st.median(v) for w, v in rat.items()},
                   'paired_ratio_min': {w: min(v) for w, v in rat.items()},
                   'paired_ratio_max': {w: max(v) for w, v in rat.items()},
                   'IC_cheaper_panels': {w: sum(1 for t in v if t < 1) for w, v in rat.items()}}
for arm in ('kS', 'kP'):
    p = 's000'
    paired[arm] = {'answer_equal_to_rT_s000': str(ic[(arm, p)]['scalar']) == str(rho[p]['scalar']),
                   'ratio_vs_rT_s000': {str(w): ic_cost(ic[(arm, p)]['e2e'], ic[(arm, p)]['kinds'], w)[0] / rho_cost(rho[p]['c'], w)[0] for w in W}}
res['paired'] = paired
res['rho_status'] = sorted(set(rho[p]['status'] for p in rho_panels))
res['rho_replay_ok_all'] = all(rho[p]['replay_ok'] for p in rho_panels)
res['ic_targets_failed'] = sorted(set(str(v['targets_failed']) for v in ic.values()))
res['perturb'] = perturb
json.dump(res, open(out, 'w'), indent=1, sort_keys=True)

def f(x):
    return '%.6g' % x
print('ell', ell, 'sqrt', f(sq))
for w in W:
    c = res['cells'][str(w)]
    print('w=%s rT mean cost %s S_rT %s | ' % (w, f(c['rT_mean_cost']), f(c['rT_S'])) +
          ' '.join('%s: S=%s ratio=%s' % (a, f(c[a]['S']), f(c[a]['ratio_to_rT_mean'])) for a in ('kS', 'kP', 'cS', 'cP')))
print('crossover', {k: f(v) for k, v in cross.items()})
print('crossover_no_field', {k: f(v) for k, v in cross_nf.items()})
for tag in ('no_field|lit', 'no_field_charge_tc|charge_scalar_mul_at_w'):
    for w in W:
        c = res['variants'][tag][str(w)]
        print(tag, 'w=%s' % w, 'rT S %.10g cost %.10g |' % (c['rT_S'], c['rT_mean_cost']),
              ' '.join('%s: S=%.10g ratio=%.10g' % (a, c[a]['S'], c[a]['ratio_to_rT_mean']) for a in ('kS', 'kP', 'cS', 'cP')))
