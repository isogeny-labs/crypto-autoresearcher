"""Register the already closed A13 interval after raw/report/S3 publication."""
import argparse, json, subprocess, sys
from pathlib import Path
from custody import ROOT, HERE, load, digest
from streams import lines


def main():
    parser = argparse.ArgumentParser()
    for name in ('run', 'report'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    run, report = args.run.resolve(), args.report.resolve()
    execution, host, metrics = [load(path) for path in (run/'execution.json', run/'host.json', run/'metrics.json')]
    if not load(report/'inspection.json')['passed']:
        raise ValueError('inspect every report page first')
    remote = load(HERE/'validation/official-s3-final.json')
    if remote['broker_returncode'] != 0 or remote['tool']['returncode'] != 0:
        raise ValueError('official remote artifact verification required first')
    curves = len(load(run/'raw/generated.json')['cells'])
    targets = sum(v['kind'] == 'target_candidate' and v.get('reason') == 'selected'
        for field in load(HERE/'inputs.json')['fields'] for i in (0, 1)
        for v in lines(run/'raw'/('p'+str(field['p'])+'-i'+str(i)+'.events.jsonl')))
    def bench(*argv):
        return subprocess.check_output([sys.executable, 'tools/benchrec.py', *map(str, argv)], cwd=ROOT, text=True).strip()
    record = bench('init', '--slug', 'prime-field-paid-known-base-control', '--problem',
        'kernel:prime-field-paid-known-base-control', '--entry', str(run.relative_to(ROOT))).splitlines()[0]
    path = ROOT/record
    value = load(path)
    value.update(commit=execution['observed_git_head'], commit_dirty=host['git_dirty'])
    value['commands'] = [dict(argv=['env',
        'PYTHONPATH=/workspace/crypto-autoresearcher/research/prime_field_a12_execution_20261106:/workspace/crypto-autoresearcher/src:/workspace/crypto-autoresearcher',
        sys.executable, '-B', str(HERE.relative_to(ROOT)/'supervise.py'),
        '--protocol', str(HERE.relative_to(ROOT)/'protocol.json'), '--release', str(HERE.relative_to(ROOT)/'root-release.json'),
        '--owner', execution['owner'], '--out', str(run.relative_to(ROOT))], cwd='.', exit=execution['returncode'],
        started_utc=execution['started_at'], wall_s=execution['diagnostic_wall_seconds'])]
    value['extensions'] = dict(benchmark_wrapper_executed=False, record_registered_after_raw_publication=True,
        native_receipt=str((run/'execution.json').relative_to(ROOT)), scientific_source_commit=execution['source_commit'],
        physical_attempts=1, pre_admission_import_failures=1, pre_admission_failure_generated_native_data=False,
        observed_curves=curves, observed_targets=targets, planned_systems=624, planned_solver_calls=1248,
        verified_systems=metrics['verified_systems'], verified_solver_calls=metrics['verified_solver_calls'],
        partial_work_unknown=metrics['partial_work_unknown'], absolute_deadline=execution['absolute_deadline'],
        effective_watchdog_seconds=execution['effective_watchdog_seconds'], numpy_runtime=host['numpy_runtime'],
        wall_valid=False, S=None, matched_reference=None,
        scope='Finite two-base construction/collection/target/algebra component census; actual joint and base-aware controls, physical and conditional cold vectors. Known logs supplied, no learned rank/cross-base Delta or calibrated runtime/whole-attack claim. Producer unverified.')
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    raw = sorted([*(run/'raw').glob('*.gz'), *run.glob('*.json.gz')])
    bench('add-raw', record, *[str(v.relative_to(ROOT)) for v in raw])
    value = load(path)
    for item in value['raw']:
        if not (ROOT/item['path']).is_file() or digest(ROOT/item['path']) != item['sha256']:
            raise ValueError('raw custody hash')
        item['uploaded'] = True
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    values = [('verified_systems', metrics['verified_systems'], 'count'),
        ('verified_solver_calls', metrics['verified_solver_calls'], 'count'),
        ('observed_curves', curves, 'count'), ('observed_public_targets', targets, 'count'),
        ('source_queries', metrics['physical_counters']['norm_collection'].get('source_queries', 0), 'count'),
        ('target_queries', sum(v.get('target_queries', 0) for v in metrics['physical_counters'].values()), 'count'),
        ('max_rss_bytes', execution['max_rss_bytes'], 'bytes')]
    for arm in ('norm_joint', 'norm_cancel', 'known_direct', 'known_joint'):
        for op in ('add', 'sub', 'mul', 'inv'):
            values.append((arm+'_fr_'+op, metrics['observed_arm_counters'][arm].get('Fr.field_'+op, 0), 'fmul' if op == 'mul' else 'count'))
    for engine in ('scalar', 'batch'):
        for op in ('add', 'sub', 'mul', 'inv'):
            values.append(('query_'+engine+'_fp_'+op, metrics['query_engine_totals'][engine].get('Fp.field_'+op, 0), 'fmul' if op == 'mul' else 'count'))
    for name, count, unit in values:
        bench('metric', record, '--name', name, '--value', count, '--unit', unit, '--better', 'neutral',
              '--n', 1, '--note', 'Observed aggregate in one actual scientific attempt; dependent matrices/control views, no calibrated cost or independent target samples. [pcc:unverified]')
    status = 'measured' if metrics['panel_complete'] else 'censored' if execution['timeout'] else 'invalid'
    bench('close', record, '--status', status, '--report', str(report/'report.pdf'),
        '--svg', str(report/'target-recovery.svg'), '--svg', str(report/'cold-components.svg'),
        '--validation', str((run/'analysis.json').relative_to(ROOT)),
        '--summary', 'Paid hash-labelled known-log base versus unchanged norm collector on matched fresh curves/public targets. All actual algebra/query controls and conditional cold references retained; supplied knowledge is not learned rank. Producer unverified, no calibrated/runtime/whole-attack claim. [pcc:unverified]')
    print(json.dumps(dict(record=record, status=status, raw_files=len(raw))))


if __name__ == '__main__':
    main()
