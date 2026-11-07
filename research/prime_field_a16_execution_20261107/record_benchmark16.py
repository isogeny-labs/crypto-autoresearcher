"""Register the closed A16 interval after raw/report/official S3 publication."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from custody16 import ROOT, HERE, load, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run','report'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--resume-record', type=Path)
    parser.add_argument('--remote-receipt',type=Path,default=HERE/'validation/official-s3-final.json')
    args = parser.parse_args()
    run, report = args.run.resolve(), args.report.resolve()
    execution, host, metrics = [load(path) for path in (run/'execution.json',run/'host.json',run/'metrics.json')]
    if not load(report/'inspection.json')['passed']: raise ValueError('inspect every report page first')
    remote = load(args.remote_receipt)
    if remote['broker_returncode'] != 0 or remote['tool']['returncode'] != 0: raise ValueError('official remote verification required')
    generated = load(run/'raw/generated.json') if (run/'raw/generated.json').is_file() else dict(cells=[])
    curves = len(generated['cells'])
    targets = sum(len(load(run/'raw'/(cell['id']+'.targets.json'))['generation']['targets']) for cell in generated['cells'])
    def bench(*argv):
        return subprocess.check_output([sys.executable,'tools/benchrec.py',*map(str,argv)],cwd=ROOT,text=True).strip()
    record = (str(args.resume_record) if args.resume_record else
        bench('init','--slug','prime-field-target-effort','--problem',
        'kernel:prime-field-target-effort','--entry',str(run.relative_to(ROOT))).splitlines()[0])
    path = ROOT/record
    value = load(path)
    if value['status'] != 'open': raise ValueError('cannot resume a closed benchmark record')
    value.update(commit=execution['observed_git_head'],commit_dirty=host['git_dirty'])
    native_protocol=Path(execution['argv'][execution['argv'].index('--protocol')+1]);native_release=Path(execution['argv'][execution['argv'].index('--release')+1])
    release=load(native_release)
    if digest(native_release)!=execution['release_sha256']:raise ValueError('actual release identity differs')
    launcher='launch_continuation16.py' if 'infrastructure_continuation'in release else 'supervise16.py'
    value['commands'] = [dict(argv=['env',
        'PYTHONPATH=/workspace/crypto-autoresearcher/src:/workspace/crypto-autoresearcher',
        'OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1',sys.executable,'-B',str(HERE.relative_to(ROOT)/launcher),
        '--protocol',str(native_protocol.resolve().relative_to(ROOT)),'--release',str(native_release.resolve().relative_to(ROOT)),
        '--out',str(run.relative_to(ROOT)),'--owner',execution['owner']],cwd='.',exit=execution['returncode'],
        started_utc=execution['started_at'],wall_s=execution['diagnostic_wall_seconds'])]
    value['extensions'] = dict(benchmark_wrapper_executed=False,record_registered_after_raw_publication=True,
        native_receipt=str((run/'execution.json').relative_to(ROOT)),scientific_source_commit=execution['source_commit'],
        physical_attempts=1,pre_launch_checkpoint_heading_refusals=1,pre_launch_refusal_stage="release builder before any native attempt",pre_launch_refusal_generated_native_data=False,
        observed_curves=curves,observed_targets=targets,planned_systems=1260,planned_solver_calls=2520,
        planned_information_diagnostics=576,verified_systems=metrics['verified_systems'],
        verified_solver_calls=metrics['verified_solver_calls'],verified_information_diagnostics=metrics['verified_information_audits'],
        partial_work_unknown=metrics['partial_work_unknown'],absolute_deadline=execution['absolute_deadline'],
        effective_watchdog_seconds=execution['effective_watchdog_seconds'],numpy_runtime=host['numpy_runtime'],infrastructure_continuation=release.get('infrastructure_continuation'),release_sha256=execution['release_sha256'],
        wall_valid=False,S=None,matched_reference=None,
        scope='Finite fresh five-program construction/collection/native target/algebra panel with independent cold8/24target horizons, common actual batchpairs and separately paid duplicate48base construction. Partial/native joint controls, separate old-coordinate outside-cancellation diagnostics, physical and conditional cold vectors. Supplied logs not learned rank; reused target slots dependent; no calibrated complete-cost/runtime/whole-attack claim. Producer unverified.')
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    raw = sorted([*(run/'raw').glob('*.gz'),*run.glob('*.json.gz'),run/'execution.json',run/'stderr.txt',run/'metrics.json'])
    bench('add-raw',record,*[str(p.relative_to(ROOT)) for p in raw])
    physical = metrics['physical_counters']
    source_queries = sum(v.get('signed_point_queries',0) for key,v in physical.items() if key.endswith('.source_construction'))
    target_queries = sum(v.get('signed_point_queries',0) for v in physical.values())-source_queries
    values = [('verified_systems',metrics['verified_systems'],'count'),('verified_solver_calls',metrics['verified_solver_calls'],'count'),
        ('verified_information_diagnostics',metrics['verified_information_audits'],'count'),('curves',curves,'count'),
        ('public_targets',targets,'count'),('signed_source_queries',source_queries,'count'),
        ('signed_target_queries',target_queries,'count'),('max_rss_bytes',execution['max_rss_bytes'],'bytes')]
    for base in ('norm8','hybrid8','known32_8','known48_8','known48_24'):
        for method in ('partial_joint','sparse_joint'):
            for op in ('add','sub','mul','inv'):
                values.append((base+'_'+method+'_fr_'+op,metrics['observed_arm_counters'].get(base+'.'+method,{}).get('Fr.field_'+op,0),'fmul' if op=='mul' else 'count'))
    for engine in ('scalar','batch'):
        for op in ('add','sub','mul','inv'):
            values.append(('query_'+engine+'_fp_'+op,metrics['query_engine_totals'][engine].get('Fp.field_'+op,0),'fmul' if op=='mul' else 'count'))
    for name,count,unit in values:
        bench('metric',record,'--name',name,'--value',count,'--unit',unit,'--better','neutral','--n',1,
            '--note','Observed aggregate in one actual attempt; dependent matrices/query controls and separate diagnostics, no independent target draws or calibrated cost. [pcc:unverified]')
    status = 'measured' if metrics['panel_complete'] else 'censored' if execution['timeout'] else 'invalid'
    argv = ['close',record,'--status',status,'--report',str(report/'report.pdf')]
    for name in ['target-recovery.svg']:
        argv += ['--svg',str(report/name)]
    argv += ['--validation',str((run/'analysis.json').relative_to(ROOT)),'--summary',
        'Fresh matched norm8/hybrid8/known32_8/known48_8/known48_24 with independent full8/24horizon constructors, actual batchpairs, paired native algebra and separate old-coordinate outside-cancellation diagnostics. Exact target identities/old-coordinate information and included costs retained; supplied knowledge is not learned rank. Producer unverified; no calibrated/runtime/whole-attack claim. [pcc:unverified]']
    bench(*argv)
    print(json.dumps(dict(record=record,status=status,raw_files=len(raw))))


if __name__=='__main__': main()
