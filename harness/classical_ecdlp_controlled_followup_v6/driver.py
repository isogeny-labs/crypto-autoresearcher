#!/usr/bin/env python3
"""Full-schedule local adapter. No sampling is reachable without native authority."""
from pathlib import Path
import argparse,base64,datetime,fcntl,hashlib,importlib.util,json,math,os,re,resource,signal,subprocess,sys,threading,time
import source_closure,lifecycle,observer
CUSTODY=None
HERE=Path(__file__).resolve().parent
PREFIX='harness/classical_ecdlp_controlled_followup_v6/'
DEPEND=PREFIX+'core/'
PINS={'cohort.py': 'cdc14ebe61b578da5c1db377fa81f89955c46113856f7ba09f4b21cebc130bb3', 'constructor.py': '31e58db07649df4e61ec2cbcaa1969789bc2c7f229c21f8555daaaaad8fdc451', 'curve.py': '6ce0b50fcc78287de7091c36383b5ccefb5dbe208ba3d1ab1c80b1ddbc326400', 'engine.py': 'cacdd0ce9a0bc7e88c88bb6e7979c0ec28ba56ca3c7c35dd3ded56d3fa7b40a3', 'host/reference.py': 'ee58b639fecbed063e74d6e825ca5a6d0e19dc79816c3713092defc8dcfa3ce2', 'host/verify.py': '244bcbd4ff7621d046165d9fa23402cd39db1e4cf17656f9841c38d2ddab4da3'}
CONTRACTS=source_closure.NATIVE
SOURCE_NAMES=source_closure.NAMES
DEFAULT_LIMITS={'seconds':120,'terminate_grace_seconds':2,'memory_bytes':2<<30,'file_bytes':16<<20,'tree_bytes':256<<20,'log_bytes':1<<20,'document_bytes':16<<20,'input_bytes':16<<20,'generation_bytes':512<<20,'reserve_bytes':128<<20}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
 with (p.open('rb') if hasattr(p,'open') else Path(p).open('rb')) as f:return hashlib.file_digest(f,'sha256').hexdigest()
def stream_payload(path,sink,chunk_bytes=1<<20):
 """Lossless bounded-memory local stream for a separately authorized publisher.

 No credentials/network/archive deletion here. The caller verifies remote full
 GET streams against this same original SHA/size before any spool retirement.
 """
 need(type(chunk_bytes) is int and 0<chunk_bytes<=8<<20,'bounded stream chunk')
 h=hashlib.sha256();total=0
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(chunk_bytes),b''):
   written=sink.write(block);need(written is None or written==len(block),'short publication sink write');h.update(block);total+=len(block)
 return {'sha256':h.hexdigest(),'bytes':total,'local_duplicate_bytes':0}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()+b'\n'
def pairs(items):
 d={}
 for k,v in items:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def loads(b):
 def finite(v):
  x=float(v);need(math.isfinite(x),'nonfinite');return x
 return json.loads(b,object_pairs_hook=pairs,parse_float=finite,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite')))
def read(p,cap=256<<20):
 p=Path(p);need(p.is_file() and not p.is_symlink() and p.stat().st_size<=cap,'bounded regular JSON');return loads(p.read_bytes())
def write(p,x,cap=16<<20):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 total=0
 with p.open('xb') as f:
  for text in json.JSONEncoder(sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).iterencode(x):
   b=text.encode();need(total+len(b)+1<=cap,'document byte limit');f.write(b);total+=len(b)
  f.write(b'\n')
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def safe(root,relative):
 need(type(relative) is str and not Path(relative).is_absolute() and '..' not in Path(relative).parts,'relative safe path')
 p=Path(root)/relative;need(p.resolve().is_relative_to(Path(root).resolve()) and not p.is_symlink(),'unsafe path');return p
def dependencies(repo):
 root=Path(repo)/DEPEND
 for name,h in PINS.items():need(sha_file(root/name)==h,'pinned dependency mismatch: '+name)
 return root
def snapshot(repo,contracts):
 paths,_=source_closure.reconstruct(repo,HERE)
 files={}
 for rel,p in sorted(paths.items()):
  b=p.read_bytes();files[rel]={'sha256':sha(b),'bytes':len(b),'base64':base64.b64encode(b).decode()}
 return {'captured_at':now(),'files':files}
def source_map(s):return {k:v['sha256'] for k,v in s['files'].items()}
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo)
def limits_check(limits):
 need(type(limits) is dict and set(limits)==set(DEFAULT_LIMITS),'exact frozen resource limits')
 for k,v in limits.items():need(type(v) in (int,float) and not isinstance(v,bool) and v>0 and math.isfinite(v),'positive finite limit: '+k)
 for k in set(limits)-{'seconds','terminate_grace_seconds'}:need(type(limits[k]) is int,'integer byte limit')
 need(limits['file_bytes']<=2<<30 and limits['memory_bytes']<=16<<30 and limits['document_bytes']<=64<<20 and limits['input_bytes']<=256<<20,'supported framing limit')
 return limits
def input_check(x):
 need(type(x) is dict and set(x)=={'schema','fixture_only','generation_status','public','plan','provenance'},'shared input fields')
 need(x['schema']=='controlled-followup-v6.public-input/v1' and type(x['fixture_only']) is bool,'shared input schema')
 need(x['generation_status'] in ('complete','incomplete'),'generation state')
 need(type(x['public']) is dict and set(x['public'])=={'curves','nonce'} and re.fullmatch('[0-9a-f]{64}',x['public']['nonce']) is not None,'public allowlist')
 need(type(x['plan']) is dict and set(x['plan'])=={'jobs','expected'},'plan fields')
 ids=set()
 for c in x['public']['curves']:
  need(set(c)=={'curve_id','model','base','targets'} and type(c['curve_id']) is str and c['curve_id'] not in ids and len(c['curve_id'])<=96,'curve identity');ids.add(c['curve_id'])
  need(set(c['model'])=={'p','a','b','r'} and all(type(v) is int for v in c['model'].values()),'public model')
  need(c['model']['r']<=29 if x['fixture_only'] else c['model']['r']<1<<16 and c['model']['p']<1<<17,'fixed order/field boundary')
  need(type(c['targets']) is list and all(set(t)=={'target_id','point'} and type(t['target_id']) is str and len(t['target_id'])<=96 for t in c['targets']),'public target allowlist')
  need(len({t['target_id'] for t in c['targets']})==len(c['targets']),'duplicate target')
 need(set(x['provenance'])=={'protocol_sha256','source_fingerprint','cohort_sha256'} and all(type(v) is str and re.fullmatch('[0-9a-f]{64}',v) for v in x['provenance'].values()),'provenance')
 need(x['provenance']['cohort_sha256']==sha(canonical(x['public'])),'public bytes binding')
 if x['fixture_only']:
  fixed=read(HERE/'fixtures.json')['fixed_input'];need(x['public']==fixed['public'] and x['plan']==fixed['plan'],'only frozen disclosed two-group fixture permitted')
 elif x['generation_status']=='complete':
  from study import SLOTS,STAGES,TIERS
  expected={f'{stage}-{bits}-{slot}':(stage,bits) for stage in STAGES for bits in TIERS for slot in range(SLOTS)}
  need(ids==set(expected),'exact96-domain slot membership')
  models=set()
  for c in x['public']['curves']:
   stage,bits=expected[c['curve_id']];m=c['model'];p=m['p'];a=m['a'];b=m['b']
   need(p>3 and p%4==3 and 0<=a<p and 0<=b<p and m['r']!=p and m['r'].bit_length()==bits,'declared production tier/model')
   denominator=(4*a**3+27*b*b)%p;need(denominator!=0,'production singular model')
   key=(p,1728*4*a**3*pow(denominator,-1,p)%p);need(key not in models,'repeated production p,j');models.add(key)
   need(len(c['targets'])==(64 if stage in STAGES[2:] else 0),'exact targets per production domain')
 return x
def production_authority(repo,out,plan_path,trial_id,config_path):
 """Read actual native supervisor facts; never an approved=true bypass."""
 out=Path(out);plan_path=Path(plan_path).resolve();config_path=Path(config_path).resolve()
 launch=read(out/'launch.json');env=read(out/'environment.json');plan=read(plan_path)
 trial=next(t for t in plan['trials'] if t['id']==trial_id)
 need(launch['run_id']==trial['run_id'] and launch['trial_id']==trial_id and launch['plan_sha256']==sha_file(plan_path),'native plan/trial identity')
 need(re.fullmatch('EXP-ECDLP-[0-9a-f]{6}',plan['experiment_id']) and re.fullmatch('RUN-ECDLP-[0-9a-f]{6}',trial['run_id']),'actual allocated production IDs')
 need(re.fullmatch('TASK-[0-9]{8}-[0-9a-f]{6}',plan['task_id']) and re.fullmatch('DEC-[0-9]{8}-[0-9a-f]{6}',plan['approved_by']),'native task/approval identity')
 need(launch['supervisor_pid']==os.getppid() and launch['supervisor_pid']!=os.getpid(),'actual native parent PID required')
 need(launch['argv']==sys.orig_argv,'native launched argv')
 need((out/'command.txt').read_text().strip()==json.dumps(launch['argv']),'native command file')
 head=git(repo,'rev-parse','HEAD').decode().strip()
 context=launch['authority']['commit'];need(context==env['commit'],'native launch context differs');git(repo,'merge-base','--is-ancestor',context,head)
 need(launch['authority']['owner'] and type(launch['authority']['epoch']) is int and datetime.datetime.fromisoformat(launch['authority']['expires_at'])>datetime.datetime.now(datetime.timezone.utc),'live native authority')
 # Use the unchanged native admission/claim/coverage guard. A fabricated
 # approved=true or matching parent PID never substitutes for a live admitted
 # executor task, committed plan/source/approval and exact archive coverage.
 sys.path.insert(0,str(Path(repo)/'tools'));native=module(Path(repo)/'tools/experiment_execution.py','v6_native_authority')
 rechecked=native.authorize(Path(repo).resolve(),plan_path,plan,launch['authority']['owner'],launch['authority']['epoch'])
 need(rechecked['owner']==launch['authority']['owner'] and rechecked['epoch']==launch['authority']['epoch'],'native authority recheck differs')
 config=read(config_path)
 from study import validate_profile
 validate_profile(read(HERE/'cohort-profile.json'))
 inventory=read(HERE/'preparation/exclusions.json')
 need(config['sampler']['excluded_p_j']==inventory['excluded_p_j'],'complete exposed-domain exclusions required')
 need(config['schema']=='controlled-followup-v6.production-config/v1' and config['fixture_only'] is False,'production config')
 binding=trial['parameters']['config'];need(safe(repo,binding['path']).resolve()==config_path and sha_file(config_path)==binding['sha256'],'frozen config binding')
 need(config['experiment_id']==plan['experiment_id'] and config['parent_run_id']==trial['run_id'] and config['task_id']==plan['task_id'] and config['approved_by']==plan['approved_by'],'config/native identity')
 publication=config['source_publication_commit'];need(re.fullmatch('[0-9a-f]{40}',publication) is not None,'actual source publication required')
 git(repo,'merge-base','--is-ancestor',publication,context)
 snap=snapshot(repo,repo);pins=source_map(snap);need(config['source_sha256']==pins,'source closure mismatch')
 for rel,h in pins.items():
  need(sha(git(repo,'show',publication+':'+rel))==h and env['source_sha256'].get(rel)==h,'source publication/native closure mismatch: '+rel)
 child=config['child_run_ids'];need(set(child)=={'candidate','baseline'} and len(set(child.values()))==2 and trial['run_id'] not in child.values() and all(re.fullmatch('RUN-ECDLP-[0-9a-f]{6}',v) for v in child.values()),'allocated distinct child IDs')
 limits=limits_check(config['limits']);need(limits['memory_bytes']<=trial['memory_mb']*(1<<20),'child memory exceeds native trial guard')
 protocol_path=safe(repo,config['protocol']['path']);protocol=read(protocol_path)
 ep=module(Path(repo)/'tools/experiment_protocol.py','v6_authority_protocol')
 need(sha_file(protocol_path)==config['protocol']['sha256'] and ep.protocol_hash(protocol)==config['protocol']['protocol_sha256']==protocol['freeze']['protocol_sha256'],'frozen protocol bytes/hash')
 need(protocol['protocol_id']==plan['experiment_id'] and {a['id'] for a in protocol['arms']}=={'candidate','baseline'} and all(a['instrument']['commit']==publication for a in protocol['arms']),'protocol instrument/arm identity')
 need(protocol['analysis_plan']['script']['sha256']==sha_file(HERE/'export.py'),'analysis binding')
 return {'fixture_only':False,'plan':plan,'trial':trial,'plan_path':os.path.relpath(plan_path,repo),'plan_sha256':sha_file(plan_path),'launch':launch,'environment':env,'context':context,'publication':publication,'child_run_ids':child,'limits':limits,'protocol_path':str(protocol_path),'protocol_sha256':config['protocol']['protocol_sha256'],'config_path':str(config_path),'config':config,'source_sha256':pins,'native_authority_recheck':rechecked}
def fixture_context(repo,contracts):
 context=git(contracts,'rev-parse','HEAD').decode().strip()
 return {'fixture_only':True,'context':context,'publication':None,'child_run_ids':{'candidate':'RUN-FIXTURE-29dff8-candidate','baseline':'RUN-FIXTURE-29dff8-baseline'},'limits':dict(DEFAULT_LIMITS),'source_sha256':source_map(snapshot(repo,contracts))}
def directory_bytes(root):
 total=0
 for p in Path(root).rglob('*'):
  need(not p.is_symlink(),'output symlink')
  if p.is_file():total+=p.stat().st_size
 return total
def launch_arm(arm,repo,contracts,input_path,out,ctx,fixture_fault=None):
 need(threading.current_thread() is threading.main_thread(),'launch requires persistent main parent thread')
 need(arm in ('candidate','baseline','generator'),'physical arm or generation stage')
 limits=limits_check(ctx['limits']);x=input_check(read(input_path,limits['input_bytes']))
 need(x['fixture_only']==ctx['fixture_only'],'fixture/native mismatch')
 need(x['provenance']['source_fingerprint']==sha(canonical(ctx['source_sha256'])) and x['provenance']['protocol_sha256']==ctx['protocol_sha256'],'source/protocol input binding')
 need(fixture_fault is None or ctx['fixture_only'] is True,'fault hooks unit-only')
 before=snapshot(repo,contracts);need(source_map(before)==ctx['source_sha256'],'source changed before launch')
 out=Path(out);out.mkdir(parents=True,exist_ok=False)
 write(out/'source-before.json',before,16<<20)
 script=HERE/('cohort_adapter.py' if arm=='generator' else arm+'.py')
 argv=[sys.executable,'-B',str(script),'--repo-root',str(repo),'--input',str(input_path),'--out',str(out/'result')]
 if arm=='generator':argv+=['--fixed-worker' if ctx['fixture_only'] else '--production-worker','--context',str(ctx.get('generation_context_path','unused-fixed-context'))]
 if arm=='baseline':argv+=['--candidate',str(out.parent/'candidate')]
 if arm=='candidate' and ctx.get('framing_part_bytes') is not None:
  need(ctx['fixture_only'],'framing override is fixed-fixture-only');argv+=['--part-bytes',str(ctx['framing_part_bytes'])]
 if fixture_fault:argv+=['--fixture-fault',fixture_fault]
 task_tmp=out/'tmp';task_tmp.mkdir();task_cache=out/'cache';task_cache.mkdir()
 env={'PATH':os.defpath,'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C.UTF-8','TMPDIR':str(task_tmp.resolve()),'XDG_CACHE_HOME':str(task_cache.resolve())}
 target_argv=argv
 argv=lifecycle.wrapper_argv(script,target_argv[3:],limits['memory_bytes'],limits['file_bytes'])
 barrier_r=barrier_w=None
 if CUSTODY is not None:
  barrier_r,barrier_w=os.pipe();argv[4:4]=['--release-fd',str(barrier_r),'--ready-file',str(out/'barrier-ready.json')]
 start=now();clock=time.monotonic();proc=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL,env=env,start_new_session=True,close_fds=True,pass_fds=() if barrier_r is None else (barrier_r,))
 if barrier_r is not None:os.close(barrier_r)
 try:
  observation=observer.capture(proc,argv,input_path,ctx['source_sha256']) if CUSTODY is None else CUSTODY.observe(arm,proc,argv,input_path,out/'barrier-ready.json')
  if barrier_w is not None:os.write(barrier_w,b'R');os.close(barrier_w);barrier_w=None
  if CUSTODY is not None and CUSTODY.driver_fault:
   need(ctx['fixture_only'],'parent faults only fixedtoy');mode=CUSTODY.driver_fault
   if mode=='exception':raise RuntimeError('disclosed source-pinned driver exception')
   os.kill(os.getpid(),signal.SIGTERM if mode=='term' else signal.SIGKILL)
 except BaseException as error:
  if barrier_w is not None:os.close(barrier_w)
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.wait();stdout,stderr=proc.communicate();(out/'stdout.log').write_bytes(stdout);(out/'stderr.log').write_bytes(stderr);write(out/'barrier-failure.json',{'error':str(error),'pid':proc.pid,'wait_returned':True,'returncode':proc.returncode});raise
 trusted_path=out.parent/'trusted-launch.jsonl'
 with trusted_path.open('ab') as target:target.write(canonical({'arm':arm,**observation}));target.flush();os.fsync(target.fileno())
 pipe_capacity={name:fcntl.fcntl(stream.fileno(),fcntl.F_GETPIPE_SZ) for name,stream in [('stdout',proc.stdout),('stderr',proc.stderr)]}
 abort=threading.Event();done=threading.Event();log_failure=[];log_sizes={}
 def drain(stream,name):
  total=0
  with (out/(name+'.log')).open('xb') as target:
   while True:
    chunk=stream.read(65536)
    if not chunk:break
    target.write(chunk);target.flush();total+=len(chunk)
    if total>limits['log_bytes'] and not done.is_set():
     log_failure.append(name+'_byte_limit');abort.set();done.wait()
  log_sizes[name]=total
 threads=[threading.Thread(target=drain,args=(proc.stdout,'stdout')),threading.Thread(target=drain,args=(proc.stderr,'stderr'))]
 for t in threads:t.start()
 reason=None;signals=[]
 while proc.poll() is None:
  if CUSTODY is not None and CUSTODY.proc.poll() is not None:reason='observer_service_died'
  elif abort.is_set():reason=log_failure[0]
  elif time.monotonic()-clock>=limits['seconds']:reason='watchdog'
  elif directory_bytes(out)>limits['tree_bytes']:reason='tree_byte_limit'
  elif __import__('shutil').disk_usage(out).free<limits['reserve_bytes']:reason='free_byte_reserve'
  if reason:
   signals.append({'signal':'SIGTERM','sent_at':now()});os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=limits['terminate_grace_seconds'])
   except subprocess.TimeoutExpired:
    signals.append({'signal':'SIGKILL','sent_at':now()});os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  time.sleep(0.01)
 proc.wait();done.set()
 for t in threads:t.join()
 if reason is None and directory_bytes(out)>limits['tree_bytes']:reason='tree_byte_limit_after_exit'
 finish=now();after=snapshot(repo,contracts);write(out/'source-after.json',after,16<<20);need(source_map(before)==source_map(after),'source changed during child')
 complete=proc.returncode==0 and reason is None
 pr={'schema':'controlled-followup-v6.physical-process/v1','arm':arm,'run_id':ctx['child_run_ids'].get(arm,'generation-stage'),'pid':proc.pid,'parent_pid':os.getpid(),'start_ticks':observation['os']['start_ticks'],'argv':argv,'started_at':start,'finished_at':finish,'returncode':proc.returncode,'operational_complete':complete,'resource_stop':reason,'signals':signals,'termination_ack':{'wait_returned':True,'returncode':proc.returncode},'input':{'path':str(Path(input_path).resolve()),'sha256':sha_file(input_path)},'source_before':before,'source_after':after,'source_publication_commit':ctx['publication'],'launch_context_commit':ctx['context'],'interpreter':{'path':sys.executable,'sha256':sha_file(Path(sys.executable).resolve())},'fixture_only':ctx['fixture_only'],'limits':limits,'actual_vms':0,'wall_valid':False,'performance_qualified':False,'stdout':{'bytes':(out/'stdout.log').stat().st_size,'sha256':sha_file(out/'stdout.log')},'stderr':{'bytes':(out/'stderr.log').stat().st_size,'sha256':sha_file(out/'stderr.log')}}
 pr['native_parent']=None if ctx['fixture_only'] else {'experiment_id':ctx['plan']['experiment_id'],'run_id':ctx['trial']['run_id'],'trial_id':ctx['trial']['id'],'task_id':ctx['plan']['task_id'],'approved_by':ctx['plan']['approved_by'],'source_publication_commit':ctx['publication'],'launch_context_commit':ctx['context'],'plan_path':ctx['plan_path'],'plan_sha256':ctx['plan_sha256'],'config_path':ctx['config_path'],'config_sha256':sha_file(ctx['config_path']),'launch':ctx['launch'],'environment':ctx['environment']}
 pr['log_pipe_capacity_bytes']=pipe_capacity
 pr['child_environment_overrides']=env
 pr['actual_repository_import_policy']='exec audit exact reconstructed closure'
 pr['process_provenance_trust']='Caller independently pins trusted-launch.jsonl outside child custody; self seals alone do not authenticate process history'
 write(out/'process.json',pr,limits['document_bytes'])
 if CUSTODY is not None:CUSTODY.closed(arm,out/'process.json')
 members=[]
 for p in sorted((out/'result').rglob('*')):
  need(not p.is_symlink(),'result symlink')
  if p.is_file():members.append({'path':p.relative_to(out/'result').as_posix(),'bytes':p.stat().st_size,'sha256':sha_file(p)})
 need(len(members)<=4096,'bounded framed result member count')
 write(out/'seal.json',{'schema':'controlled-followup-v6.local-seal/v1','process_sha256':sha_file(out/'process.json'),'files':members,'tree_sha256':sha(canonical(members)),'wait_returned':True,'returncode':proc.returncode,'scope':'Actual local process group wait and closed output bytes; no remote/UID/isolation assertion.'})
 if arm=='generator':return pr
 native_plan={'experiment_id':'EXP-FIXTURE-29dff8' if ctx['fixture_only'] else ctx['plan']['experiment_id'],'task_id':'TASK-20261030-29dff8' if ctx['fixture_only'] else ctx['plan']['task_id'],'approved_by':None if ctx['fixture_only'] else ctx['plan']['approved_by']}
 native_trial={'id':arm,'run_id':pr['run_id'],'parameters':{'fixture_only':ctx['fixture_only']}}
 write(out/'native-plan.json',native_plan)
 envrec={'python':sys.version,'platform':sys.platform,'commit':ctx['context'],'source_sha256':source_map(before),'runtime_lock':None,'runtime_lock_sha256':None}
 write(out/'environment.json',envrec);checker=[sys.executable,str(HERE/'check.py')]
 launch={'argv':argv,'check_argv':checker,'started_at':start,'trial_id':arm,'run_id':pr['run_id'],'authority':{'commit':ctx['context']},'plan_sha256':sha_file(out/'native-plan.json'),'task_id':native_plan['task_id']}
 write(out/'launch.json',launch);(out/'command.txt').write_text(json.dumps(argv)+'\n')
 write(out/'raw-result.json',{'attack_claimed':False,'status':'completed' if complete else 'failed','physical_process_sha256':sha_file(out/'process.json'),'wall_valid':False})
 body={'id':pr['run_id'],'experiment_id':native_plan['experiment_id'],'task_id':native_plan['task_id'],'trial_id':arm,'approved_by':native_plan['approved_by'],'status':'completed' if complete else 'failed','attack_claimed':False,'code':{'commit':ctx['context'],'command':argv,'check_command':checker,'command_file':'command.txt','instrument_source_publication_commit':ctx['publication']},'environment':{'file':'environment.json',**envrec},'inputs':{'trial_plan':'native-plan.json','plan_sha256':sha_file(out/'native-plan.json'),'trial_id':arm,'parameters':native_trial['parameters']},'timing':{'started_at':start,'finished_at':finish},'result':{'raw_result':'raw-result.json','certificate':{'kind':'none','verified':None}},'metrics':{'physical_invocations':1,'wall_valid':False}}
 write(out/'manifest.yaml',{'run':body})
 return pr
def execute(repo,contracts,input_path,out,ctx,protocol_path,faults=None):
 dependencies(repo);source_closure.install(repo,HERE);input_check(read(input_path));out=Path(out);out.mkdir(parents=True,exist_ok=False)
 records=[launch_arm(a,repo,contracts,input_path,out/a,ctx,(faults or {}).get(a)) for a in ('candidate','baseline')]
 need(len({r['pid'] for r in records})==2,'distinct actual processes')
 write(out/'registry.json',{'schema':'controlled-followup-v6.physical-registry/v1','instance_id':'shared-public-bundle','processes':[{'arm':r['arm'],'pid':r['pid'],'run_id':r['run_id'],'process_sha256':sha_file(out/r['arm']/'process.json')} for r in records],'input_sha256':sha_file(input_path),'physical_invocations':2,'analytical_reference_is_arm':False,'fixture_only':ctx['fixture_only']})
 return {'status':'complete' if all(r['operational_complete'] for r in records) else 'incomplete','trusted_launch_sha256':sha_file(out/'trusted-launch.jsonl'),'physical_invocations':2,'wall_valid':False,'scientific_validity':'not_assessed'}
def run_fixture(repo,contracts,input_path,out,protocol_path,limits=None,faults=None):
 x=input_check(read(input_path));need(x['fixture_only'],'fixture only')
 ctx=fixture_context(repo,contracts)
 ctx['protocol_sha256']=read(protocol_path)['freeze']['protocol_sha256']
 if limits:ctx['limits']=limits_check(limits)
 return execute(repo,contracts,input_path,out,ctx,protocol_path,faults)
def production(repo,out,plan_path,trial_id,config_path):
 global CUSTODY
 ctx=production_authority(repo,out,plan_path,trial_id,config_path)
 CUSTODY=observer.Service(repo,out,plan_path,trial_id,config_path)
 adapter=module(HERE/'cohort_adapter.py','v6_cohort_adapter')
 input_path=adapter.generate(repo,ctx,Path(out)/'shared')
 result=execute(repo,repo,input_path,Path(out)/'execution',ctx,ctx['protocol_path'])
 CUSTODY.finish();CUSTODY=None
 exp=module(HERE/'export.py','v6_export_production');exp.make(ctx['protocol_path'],Path(out)/'execution',repo,Path(out)/'typed-export')
 write(Path(out)/'raw-result.json',{'attack_claimed':False,'status':'completed' if result['status']=='complete' else 'failed','execution':result,'export':'typed-export/export.json','wall_valid':False})
 launch=ctx['launch'];trial=ctx['trial'];plan=ctx['plan'];body={'id':trial['run_id'],'experiment_id':plan['experiment_id'],'task_id':plan['task_id'],'trial_id':trial['id'],'approved_by':plan['approved_by'],'status':'completed' if result['status']=='complete' else 'failed','attack_claimed':False,'code':{'commit':ctx['context'],'command':launch['argv'],'check_command':launch['check_argv'],'command_file':'command.txt'},'environment':{'file':'environment.json',**ctx['environment']},'inputs':{'trial_plan':ctx['plan_path'],'plan_sha256':ctx['plan_sha256'],'trial_id':trial['id'],**{k:trial[k] for k in ('parameters','seed','curve_id') if k in trial}},'timing':{'started_at':launch['started_at'],'finished_at':now()},'result':{'raw_result':'raw-result.json','certificate':{'kind':'none','verified':None}},'metrics':{'physical_invocations':2,'wall_valid':False}}
 if 'hypothesis_id' in plan:body['hypothesis_id']=plan['hypothesis_id']
 write(Path(out)/'manifest.yaml',{'run':body})
 return result
def native_fixture(repo,out,plan_path,trial_id,config_path):
 global CUSTODY
 out=Path(out);cfg=read(config_path);need(cfg['fixture_only'] is True,'native fixedtoy only');launch=read(out/'launch.json');plan=read(plan_path);trial=next(t for t in plan['trials'] if t['id']==trial_id)
 need(launch['supervisor_pid']==os.getppid() and launch['argv']==sys.orig_argv,'native fixedtoy direct parent/argv')
 observer.native_binding(repo,out,plan_path,trial_id,config_path,os.getpid())
 ctx=fixture_context(repo,repo);ctx['protocol_sha256']=cfg['protocol']['protocol_sha256'];ctx['limits'].update(cfg.get('limits',{}));input_check(read(cfg['input']))
 CUSTODY=observer.Service(repo,out,plan_path,trial_id,config_path,cfg.get('observer_fault'))
 try:
  if cfg.get('fixed_generator'):launch_arm('generator',repo,repo,cfg['input'],out/'shared/generator',ctx,cfg.get('faults',{}).get('generator'))
  result=execute(repo,repo,cfg['input'],out/'execution',ctx,cfg['protocol']['path'],cfg.get('faults'))
  CUSTODY.finish();CUSTODY=None
 finally:
  if CUSTODY is not None:CUSTODY.abort();CUSTODY=None
 exp=module(HERE/'export.py','v6_export_native_fixture');exp.make(cfg['protocol']['path'],out/'execution',repo,out/'typed-export')
 write(out/'raw-result.json',{'attack_claimed':False,'status':'completed' if result['status']=='complete' else 'failed','execution':result,'fixture_only':True})
 environment=read(out/'environment.json');body={'id':trial['run_id'],'experiment_id':plan['experiment_id'],'task_id':plan['task_id'],'trial_id':trial_id,'approved_by':plan['approved_by'],'status':'completed' if result['status']=='complete' else 'failed','attack_claimed':False,'code':{'commit':environment['commit'],'command':launch['argv'],'check_command':launch['check_argv'],'command_file':'command.txt'},'environment':{'file':'environment.json',**environment},'inputs':{'trial_plan':str(Path(plan_path).relative_to(Path(cfg['native_root']))),'plan_sha256':sha_file(plan_path),'trial_id':trial_id,'parameters':trial['parameters']},'timing':{'started_at':launch['started_at'],'finished_at':now()},'result':{'raw_result':'raw-result.json','certificate':{'kind':'none','verified':None}},'metrics':{'physical_invocations':2,'wall_valid':False,'fixture_only':True}}
 write(out/'manifest.yaml',{'run':body});return result
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['production','fixture','native-fixture']);p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root');p.add_argument('--out',required=True);p.add_argument('--input');p.add_argument('--protocol');p.add_argument('--trial-plan');p.add_argument('--trial-id');p.add_argument('--config');a=p.parse_args()
 if a.action=='fixture':r=run_fixture(a.repo_root,a.contracts_root or a.repo_root,a.input,a.out,a.protocol)
 elif a.action=='native-fixture':r=native_fixture(a.repo_root,a.out,a.trial_plan,a.trial_id,a.config)
 else:
  try:r=production(a.repo_root,a.out,a.trial_plan,a.trial_id,a.config)
  finally:
   if CUSTODY is not None:CUSTODY.abort()
 print(json.dumps(r));return 0 if r['status']=='complete' else 1
if __name__=='__main__':raise SystemExit(main())
