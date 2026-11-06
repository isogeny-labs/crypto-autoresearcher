"""Reader's own numeric checks for prior findings CAN-2, CAN-3, CAN-5 (SHF-20261028-0f3f64),
from decoded raw stdout of run 39882571652 and the archived twin run 38862448935.
Usage: python3 -I prior_checks.py decoded_runs.json decoded_twin.json protocol_band.json"""
import json, random, sys
rows = json.load(open(sys.argv[1])); twin = json.load(open(sys.argv[2])); pb = json.load(open(sys.argv[3]))
m = pb['models']['protocol']
out = {}
# CAN-2: base construction and LA solve absent from the S unit
frob = []; base_src = set(); la = {}
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        continue
    s = [r for r in d['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]
    ph = s['op_counts']['phases']
    frob.append(sum(ph[q]['ec_frobenius'] for q in ph))
    base_src.add(s.get('base_source'))
    if d['arm'] in ('kS', 'kP'):
        la[d['arm']] = {k: v for k, v in ph['linear_algebra'].items() if v}
out['CAN2_ec_frobenius_total_all_IC_records'] = sum(frob)
out['CAN2_base_source_values'] = sorted(map(str, base_src))
out['CAN2_rank_process_LA_phase'] = la
S1 = m['arms']['S']['cost']['1'][0]; R1 = m['arms']['rT']['cost']['1'][0]
out['CAN2_S_gap_w1'] = S1 / R1
out['CAN2_S_gap_w1_with_rank_LA_added'] = (S1 + la['kS']['la_mulmods']) / R1
# rT ns per walk step in this run (online ms / walk steps, mean of per-point ratios)
steps = []
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        rec = d['records'][0]
        steps.append(rec['online_phase_ns']['walk_and_collision'] / rec['outcome']['walk_steps'])
ns = sum(steps) / len(steps)
out['CAN2_this_run_rT_ns_per_walk_step_mean'] = ns
X_ms = 427.524
for label, step in (('175.95ns', 175.95), ('this_run', ns)):
    gae = X_ms * 1e6 / step
    out['CAN2_X_as_GAE_' + label] = gae
    out['CAN2_S_gap_w0_if_X_all_group_adds_' + label] = (m['arms']['S']['cost']['0'][0] + gae) / m['arms']['rT']['cost']['0'][0]
# CAN-3: rank-stage share; rank-seed variability; MC dependence of reported bounds
rs = [x['decoded'] for x in rows if x['decoded']['arm'] == 'kS'][0]
s = [r for r in rs['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]
rank_unpr = sum(v for k, v in s['op_counts']['phases']['rank_stage'].items()
                if k not in ('ec_add', 'ec_double', 'ec_scalar_mul', 'la_row_eliminations', 'field_mul', 'field_sqr', 'field_inv', 'field_half_trace'))
out['CAN3_rank_stage_share_of_S_unpriced'] = rank_unpr / m['arms']['S']['mean_unpriced']
tw = {}
for x in twin:
    d = x['decoded']
    if d['arm'] in ('kS', 'kP'):
        ss = [r for r in d['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]
        tw[(d['arm'], d['panel'], x['file'])] = ss['rank_probes_total']
out['CAN3_archived_rank_probes'] = {'%s %s %s' % k: v for k, v in tw.items()}
ks = sorted(v for k, v in tw.items() if k[0] == 'kS')
out['CAN3_kS_second_seed_probe_excess'] = max(ks) / min(ks) - 1
# scale the S rank stage by that ratio -> gaps
for w in ('0.1', '1'):
    Sp = m['arms']['S']['mean_group'] + float(w) * (m['arms']['S']['mean_unpriced'] + rank_unpr * (max(ks) / min(ks) - 1))
    out['CAN3_S_gap_w%s_rank_scaled_to_seed2' % w] = Sp / m['arms']['rT']['cost'][w][0]
out['CAN3_S_over_P_w0'] = m['S_over_P']['0']
# MC dependence: rebuild per-point S and rT costs at w=0.1 from the protocol_band units
# (reconstructed from decoded rows the same way as protocol_band.py)
GROUP = ('ec_add', 'ec_double'); NP = ('ec_scalar_mul', 'la_row_eliminations', 'field_mul', 'field_sqr', 'field_inv', 'field_half_trace')
UP = ('setup', 'linear_algebra', 'between_linear_algebra_and_targets', 'targets')
ph = {}; rho = {}
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        c = d['records'][0]['outcome']['charges_setup_and_solve']
        rho[d['panel']] = (c['group_additions'], sum(c[k] for k in ('canonicalizations', 'partition_hashes', 'table_queries', 'table_inserts', 'failed_collisions')))
    else:
        ph[(d['arm'], d['panel'])] = [r for r in d['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]['op_counts']['phases']
pts = sorted(rho)
def unitS(p):
    u = dict(ph[('kS', 's000')]['rank_stage'])
    for q in UP:
        for k, v in ph[('cS', p)][q].items():
            u[k] += v
    return sum(u[k] for k in GROUP), sum(v for k, v in u.items() if k not in GROUP + NP)
SU = {p: unitS(p) for p in pts}
def ci(seed, draws, w):
    rng = random.Random(seed)
    vals = []
    for _ in range(draws):
        smp = [pts[rng.randrange(len(pts))] for _ in pts]
        a = sum(SU[p][0] + w * SU[p][1] for p in smp) / len(smp)
        b = sum(rho[p][0] + w * rho[p][1] for p in smp) / len(smp)
        vals.append(a / b)
    vals.sort()
    return [vals[int(0.025 * (draws - 1))], vals[int(0.975 * (draws - 1))]]
out['CAN3_S_w0.1_ci_seed20261023_10k'] = ci(20261023, 10000, 0.1)
out['CAN3_S_w0.1_ci_seed1_10k'] = ci(1, 10000, 0.1)
out['CAN3_S_w0.1_ci_seed987654321_40k'] = ci(987654321, 40000, 0.1)
# CAN-5: memory
mem = {}
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        rec = d['records'][0]
        mem.setdefault('rT', []).append((rec['peak_rss_bytes'], rec['outcome']['table_entries'], rec['outcome']['table_payload_lower_bound_bytes']))
    else:
        s2 = [r for r in d['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]
        mem.setdefault(d['arm'], []).append((s2['peak_rss_bytes'], s2.get('root_table_entries'), s2.get('root_table_bytes')))
out['CAN5_memory'] = {a: {'peak_rss_max': max(t[0] for t in v), 'peak_rss_min': min(t[0] for t in v),
                          'entries_mean': sum(t[1] for t in v) / len(v), 'bytes_field_mean': sum(t[2] for t in v) / len(v)}
                      for a, v in mem.items()}
print(json.dumps(out, indent=1))
