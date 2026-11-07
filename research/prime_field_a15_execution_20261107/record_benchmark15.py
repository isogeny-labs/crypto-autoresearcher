"""Register one existing A15 interval after raw/report/official S3 publication."""
import argparse,json,subprocess,sys
from pathlib import Path
from collections import Counter
from custody15 import HERE,ROOT,load


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('run','report'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-record',type=Path);a=p.parse_args();run,report=a.run.resolve(),a.report.resolve()
    e,h,m=[load(path) for path in (run/'execution.json',run/'host.json',run/'metrics.json')]
    if not load(report/'inspection.json')['passed']:raise ValueError('inspect every report page first')
    remote=load(HERE/'validation/official-s3-final.json')
    if remote['broker_returncode']!=0 or remote['tool']['returncode']!=0:raise ValueError('official remote verification required')
    def bench(*argv):return subprocess.check_output([sys.executable,'tools/benchrec.py',*map(str,argv)],cwd=ROOT,text=True).strip()
    record=str(a.resume_record) if a.resume_record else bench('init','--slug','prime-field-batched-pairs','--problem','kernel:prime-field-signed-pair-construction','--entry',str(run.relative_to(ROOT))).splitlines()[0]
    path=ROOT/record;v=load(path)
    if v['status']!='open':raise ValueError('closed records cannot be resumed')
    v.update(commit=e['observed_git_head'],commit_dirty=h['git_dirty'])
    v['commands']=[dict(argv=['env','PYTHONPATH=/workspace/crypto-autoresearcher/src:/workspace/crypto-autoresearcher','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1',sys.executable,'-B',str(HERE.relative_to(ROOT)/'supervise15.py'),'--protocol',str(HERE.relative_to(ROOT)/'protocol.json'),'--release',str(HERE.relative_to(ROOT)/'root-release.json'),'--out',str(run.relative_to(ROOT)),'--owner',e['owner']],cwd='.',exit=e['returncode'],started_utc=e['started_at'],wall_s=e['diagnostic_wall_seconds'])]
    v['extensions']=dict(benchmark_wrapper_executed=False,record_registered_after_raw_publication=True,scientific_source_commit=e['source_commit'],
        native_receipt=str((run/'execution.json').relative_to(ROOT)),physical_attempts=1,conditioned_input_reuse=True,new_target_solver_calls=0,
        independent_new_target_draws=0,planned_builds=32,planned_query_calls=17920,planned_endpoint_engine_calls=35840,
        verified_builds=m['verified_builds'],verified_query_calls=m['verified_query_calls'],partial_work_unknown=m['partial_work_unknown'],
        absolute_deadline=e['absolute_deadline'],numpy_runtime=h['numpy_runtime'],wall_valid=False,S=None,matched_reference=None,
        scope='Existing signed-sum denominator reuse/product-tree technique; actual cold scalar/batched pair constructors and complete retained query/native-row/miss/counter controls. Separate primitive vectors and explicit allocation traffic, no new targets/solvers or calibrated runtime/whole-attack claim. Producer unverified.')
    path.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    raw=sorted(run.rglob('*.gz'))
    bench('add-raw',record,*[str(path.relative_to(ROOT)) for path in raw])
    values=[('verified_builds',m['verified_builds'],'count'),('verified_query_calls',m['verified_query_calls'],'count'),('new_target_solver_calls',0,'count'),('max_rss_bytes',e['max_rss_bytes'],'bytes')]
    for method in ('scalar','batched'):
        counters=Counter()
        for row in m['rows']:
            if row['method']==method and row['build']:counters.update(row['build']['counters'])
        for op in ('add','sub','mul','inv'):values.append((method+'_construction_fp_'+op,counters.get('Fp.field_'+op,0),'fmul' if op=='mul' else 'count'))
        values.append((method+'_pair_array_bytes',counters.get('pair_array_allocated_bytes',0),'bytes'))
    existing={x['name'] for x in load(path)['metrics']}
    for name,value,unit in values:
        if name not in existing:bench('metric',record,'--name',name,'--value',value,'--unit',unit,'--better','neutral','--n',1,'--note','Observed aggregate in one bounded component attempt on retained inputs, no independent targets/solvers or calibrated complete cost. [pcc:unverified]')
    status='measured' if m['panel_complete'] else 'censored' if e['timeout'] else 'invalid'
    bench('close',record,'--status',status,'--report',str(report/'report.pdf'),'--svg',str(report/'construction-arithmetic.svg'),'--svg',str(report/'explicit-array-traffic.svg'),
        '--validation',str((run/'analysis.json').relative_to(ROOT)),'--summary','Cold signed-pair scalar/batch construction on all16 retained A14 geometries with exact ordered pair/native/query/miss and independent arithmetic/allocation schedule checks. Query controls executed, zero new target solvers or target draws. Producer unverified; no calibrated runtime or complete attack-cost claim. [pcc:unverified]')
    print(json.dumps(dict(record=record,status=status,raw_files=len(raw))))


if __name__=='__main__':main()
