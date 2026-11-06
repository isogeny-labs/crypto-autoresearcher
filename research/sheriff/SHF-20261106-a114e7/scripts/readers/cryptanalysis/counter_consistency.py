"""Internal consistency of op_counts against the producer's independent (non-counter) fields in the
same raw record. Usage: python3 -I counter_consistency.py decoded_runs.json"""
import json, sys
rows = json.load(open(sys.argv[1]))
res = {'checked_runs': 0, 'fail': []}
for x in rows:
    d = x['decoded']
    if d['arm'] == 'rT':
        continue
    t = d['records'][0]
    s = [r for r in d['records'] if r.get('kind') == 'compact_orbit_dlp_summary'][0]
    ph = s['op_counts']['phases']
    checks = {
        'target probes == targets.root_index_probes': t['probes'] == ph['targets']['root_index_probes'],
        'target root_calls == targets.s3_root_solves': t['root_calls'] == ph['targets']['s3_root_solves'],
        'target flat op_counts == phases.targets': all(t['op_counts'][k] == ph['targets'][k] for k in ph['targets']),
        'rank_probes_total == rank_stage.root_index_probes': s['rank_probes_total'] == ph['rank_stage']['root_index_probes'],
        'rank_root_calls_total == rank_stage.s3_root_solves': s['rank_root_calls_total'] == ph['rank_stage']['s3_root_solves'],
        'verified_columns == LA ec_scalar_mul': s['factor_log_table']['verified_columns'] == ph['linear_algebra']['ec_scalar_mul'],
        # observed pattern (reader's expectation, not a producer statement): folded index (S) inserts
        # logical_states + 600 (orbit columns); unfolded index (P) inserts 2 x logical_states
        'setup root_index_inserts matches fold pattern': ph['setup']['root_index_inserts'] == (
            s['index_digest']['logical_states'] + s['orbit_columns'] if s.get('state_fold') else 2 * s['index_digest']['logical_states']),
        'rank_relations == rank_stage.relation_lifts': s['rank_relations'] == ph['rank_stage']['relation_lifts'],
    }
    res['checked_runs'] += 1
    for k, v in checks.items():
        if not v:
            res['fail'].append((d['arm'], d['panel'], k))
print(json.dumps(res))
