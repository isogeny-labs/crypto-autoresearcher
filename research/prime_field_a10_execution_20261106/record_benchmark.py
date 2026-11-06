"""Register the observed closed native interval after raw publication; no re-execution."""
import argparse,json,subprocess,sys
from pathlib import Path
from common import ROOT,HERE,load,write_once,digest

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();run=a.run.resolve();report=a.report.resolve();e=load(run/'execution.json');host=load(run/'host.json');analysis=load(run/'analysis.json')
 if not load(report/'inspection.json')['passed']:raise ValueError('inspect report first')
 def bench(*args):return subprocess.check_output([sys.executable,'tools/benchrec.py',*map(str,args)],cwd=ROOT,text=True).strip()
 record=bench('init','--slug','prime-field-ap-source-holdout','--problem','kernel:prime-field-ap-source-holdout','--entry',str(run.relative_to(ROOT))).splitlines()[0];path=ROOT/record;data=load(path)
 data.update(commit=e['observed_git_head'],commit_dirty=host['git_dirty'])
 data['commands']=[dict(argv=[sys.executable,'-B',str(HERE.relative_to(ROOT)/'supervise.py'),'--protocol',str(HERE.relative_to(ROOT)/'protocol.json'),'--release',str(HERE.relative_to(ROOT)/'root-release.json'),'--owner',e['owner'],'--out',str(run.relative_to(ROOT))],cwd='.',exit=e['returncode'],started_utc=e['started_at'],wall_s=e['diagnostic_wall_seconds'])]
 data['extensions']=dict(benchmark_wrapper_executed=False,record_registered_after_raw_publication=True,native_receipt=str((run/'execution.json').relative_to(ROOT)),scientific_source_commit=e['source_commit'],physical_attempts=1,fresh_curves=4,fresh_public_targets=32,scope_cases=432,solver_calls=864,absolute_deadline=e['absolute_deadline'],effective_watchdog_seconds=e['effective_watchdog_seconds'],wall_valid=False,S=None,matched_reference=None,scope='Fresh finite AP/hash source and kernel-free solver component comparison. Constructor/collection/Fr/lifting/check vectors separate. Primitivecoverage incomplete forlegacygeneration/checker/OS; no weighted/runtime/endtoend gain claimed. Command clock is retained inner supervised interval, no benchrec wrapper executed.')
 path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 raw=sorted((run/'raw').glob('*.gz'));bench('add-raw',record,*[str(p.relative_to(ROOT)) for p in raw])
 data=load(path)
 for item in data['raw']:
  if not (ROOT/item['path']).is_file() or digest(ROOT/item['path'])!=item['sha256']:raise ValueError('raw custody')
  # Official artifacts verify --remote must already have passed on these exact bytes.
  item['uploaded']=True
 path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 metrics=[('solver_calls_verified',analysis['solver_calls_verified'],'count',864),('scope_cases',432,'count',432),('fresh_curves',4,'count',4),('fresh_targets',32,'count',32),('source_queries',analysis['collection_counters']['source_queries'],'count',1),('target_queries',analysis['collection_counters']['target_queries'],'count',1),('constructor_group_add_calls',analysis['collection_counters']['constructor_group_add_calls'],'count',24),('max_rss_bytes',e['max_rss_bytes'],'bytes',1)]
 for arm in ('sparse_joint','sparse_cancel'):
  for key in ('add','sub','mul','inv'):metrics.append((arm+'_fr_'+key,analysis['arm_totals'][arm].get('Fr.field_'+key,0),'fmul' if key=='mul' else 'count',432))
 for name,value,unit,n in metrics:bench('metric',record,'--name',name,'--value',value,'--unit',unit,'--better','neutral','--n',n,'--note','Exact finite measured component/coverage count; dependent scopes, separate fields and shared work; no calibrated cost/runtime/endtoend claim.')
 status='measured' if analysis['panel_complete'] else 'censored' if e['timeout'] else 'invalid'
 bench('close',record,'--status',status,'--report',str(report/'report.pdf'),'--svg',str(report/'target-recovery.svg'),'--svg',str(report/'constructor-calls.svg'),'--validation',str((run/'analysis.json').relative_to(ROOT)),'--summary','Fresh4curve/32target AP-versus-optimizedhash source panel;432systems/864symmetric kernel-free calls checked, allcostvectors andadverse outcomes retained. No fullkernel production, no weighted/runtime/endtoend improvementclaim.')
 print(json.dumps(dict(record=record,status=status,raw_files=len(raw))))
if __name__=='__main__':main()
