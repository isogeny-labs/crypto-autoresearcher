"""Register closed A12 interval and observed prefix counts, never execute again."""
import argparse,json,subprocess,sys
from pathlib import Path
from common import ROOT,HERE,load,digest
from streaming import lines

def main():
 p=argparse.ArgumentParser()
 for name in ('run','report'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();run=a.run.resolve();report=a.report.resolve();e=load(run/'execution.json');host=load(run/'host.json');data=load(run/'analysis.json')
 if not load(report/'inspection.json')['passed']:raise ValueError('inspect report first')
 custody=load(HERE/'validation/official-s3-final.json')
 if custody['broker_returncode']!=0 or custody['tool']['returncode']!=0:raise ValueError('official remote storage verification must precede registration')
 def bench(*args):return subprocess.check_output([sys.executable,'tools/benchrec.py',*map(str,args)],cwd=ROOT,text=True).strip()
 curves=sum(v['kind']=='curve_selected' for v in lines(run/'raw/generation.events.jsonl'));targets=sum(v['kind']=='target_candidate' and v.get('reason')=='selected' for field in load(HERE/'inputs.json')['fields'] for i in range(2) for v in lines(run/'raw'/('p'+str(field['p'])+'-i'+str(i)+'.events.jsonl')))
 record=bench('init','--slug','prime-field-batched-target-holdout','--problem','kernel:prime-field-batched-target-holdout','--entry',str(run.relative_to(ROOT))).splitlines()[0];path=ROOT/record;value=load(path)
 value.update(commit=e['observed_git_head'],commit_dirty=host['git_dirty']);value['commands']=[dict(argv=[sys.executable,'-B',str(HERE.relative_to(ROOT)/'supervise.py'),'--protocol',str(HERE.relative_to(ROOT)/'protocol.json'),'--release',str(HERE.relative_to(ROOT)/'root-release.json'),'--owner',e['owner'],'--out',str(run.relative_to(ROOT))],cwd='.',exit=e['returncode'],started_utc=e['started_at'],wall_s=e['diagnostic_wall_seconds'])]
 value['extensions']=dict(benchmark_wrapper_executed=False,record_registered_after_raw_publication=True,native_receipt=str((run/'execution.json').relative_to(ROOT)),scientific_source_commit=e['source_commit'],physical_attempts=1,observed_curves=curves,observed_targets=targets,planned_systems=1152,planned_solver_calls=2304,verified_systems=data['verified_systems'],verified_solver_calls=data['verified_solver_calls'],partial_work_unknown=data['partial_work_unknown'],absolute_deadline=e['absolute_deadline'],effective_watchdog_seconds=e['effective_watchdog_seconds'],numpy_runtime=host['numpy_runtime'],wall_valid=False,S=None,matched_reference=None,scope='Finite larger-field fixed-base32 query-engine/target/solver component study; producer measurements unverified. Both query engines charged physically, one equal matrix stream. Cold references and physical totals distinct. Unexpanded internals/calibration/signed replay absent; no weighted/runtime/whole-attack gain.')
 path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');raw=sorted([*(run/'raw').glob('*.gz'),*run.glob('*.json.gz')]) or [run/'execution.json',run/'stdout.txt',run/'stderr.txt'];bench('add-raw',record,*[str(p.relative_to(ROOT)) for p in raw]);value=load(path)
 for item in value['raw']:
  if not (ROOT/item['path']).is_file() or digest(ROOT/item['path'])!=item['sha256']:raise ValueError('raw custody')
  item['uploaded']=True  # Only invoke after official remote verification receipt.
 path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
 metrics=[('verified_systems',data['verified_systems'],'count'),('verified_solver_calls',data['verified_solver_calls'],'count'),('observed_curves',curves,'count'),('observed_public_targets',targets,'count'),('source_queries',data['physical_counters']['source'].get('source_queries',0),'count'),('target_queries',sum(v['queries'] for v in data['query_summary']),'count'),('max_rss_bytes',e['max_rss_bytes'],'bytes')]
 for arm in ('sparse_joint','sparse_cancel'):
  for key in ('add','sub','mul','inv'):metrics.append((arm+'_fr_'+key,data['observed_arm_counters'][arm].get('Fr.field_'+key,0),'fmul' if key=='mul' else 'count'))
 for engine in ('scalar','batch'):
  for key in ('add','sub','mul','inv'):metrics.append(('query_'+engine+'_fp_'+key,data['query_engine_totals'][engine].get('Fp.field_'+key,0),'fmul' if key=='mul' else 'count'))
 for name,count,unit in metrics:bench('metric',record,'--name',name,'--value',count,'--unit',unit,'--better','neutral','--n',1,'--note','Observed aggregate in one physical attempt; dependent systems/engine controls, no sample independence or calibrated cost. Partial unknown work stays explicit.')
 status='measured' if data['panel_complete'] else 'censored' if e['timeout'] else 'invalid';bench('close',record,'--status',status,'--report',str(report/'report.pdf'),'--svg',str(report/'target-recovery.svg'),'--svg',str(report/'query-engine-costs.svg'),'--validation',str((run/'analysis.json').relative_to(ROOT)),'--summary','Fixed-base32 fresh18/19bit target panel with actually executed scalar/batch query controls and one matrix stream. All recorded outcomes/failures, counter vectors and cold references retained; producer standing unverified, no weighted/runtime/whole-attack claim.')
 print(json.dumps(dict(record=record,status=status,raw_files=len(raw))))
if __name__=='__main__':main()
