#!/usr/bin/env python3
"""Bounded disclosed software controls; every attempt has a fresh evidence root."""
from pathlib import Path
import argparse,copy,io,json,os,subprocess,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent));import driver as d
exp=d.module(d.HERE/'export.py','unit_export');checker=d.module(d.HERE/'check.py','unit_check');adapter=d.module(d.HERE/'cohort_adapter.py','unit_adapter')
ARGS=None;EVENTS=[]
def cli(argv):
 before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now();r=subprocess.run(argv,capture_output=True,timeout=30);after=d.snapshot(ARGS.repo_root,ARGS.contracts_root)
 EVENTS.append({'kind':'actual_cli','argv':argv,'started_at':start,'finished_at':d.now(),'source_before':before,'source_after':after,'returncode':r.returncode,'stdout_utf8':r.stdout.decode(),'stderr_utf8':r.stderr.decode()});return r
class Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(ARGS.control_root);cls.root.mkdir(parents=True,exist_ok=False)
  cls.protocol=cls.root/'protocol.json';d.write(cls.protocol,exp.fixture_protocol(ARGS.contracts_root))
  cls.ctx=d.fixture_context(ARGS.repo_root,ARGS.contracts_root);cls.ctx['protocol_sha256']=d.read(cls.protocol)['freeze']['protocol_sha256']
  cls.input=cls.root/'input.json';d.write(cls.input,adapter.fixed_input(cls.ctx['protocol_sha256'],d.sha(d.canonical(cls.ctx['source_sha256']))))
  cls.out=cls.root/'execution';cls.result=d.run_fixture(ARGS.repo_root,ARGS.contracts_root,cls.input,cls.out,cls.protocol)
  cls.bundle,cls.findings=exp.make(cls.protocol,cls.out,ARGS.contracts_root,cls.root/'export')
 def valid(self):
  return checker.check(self.out,self.protocol,self.root/'export/export.json',ARGS.repo_root,ARGS.contracts_root,self.result['trusted_launch_sha256'])
 def test_01_actual_full_toy_route(self):
  self.assertEqual(self.result['status'],'complete');self.assertEqual(self.findings,[]);self.assertEqual(self.valid()['operational_status'],'complete')
  pr=[d.read(self.out/a/'process.json') for a in ('candidate','baseline')];self.assertEqual(len({r['pid'] for r in pr}),2)
  v=d.read(self.out/'baseline/result/verification.json');self.assertEqual(v['observed'],{'setups':16,'singles':16,'intents':20,'traces':20,'cells':24})
  rows=d.read(self.out/'baseline/result/bsgs.json')['rows'];self.assertEqual([r['answer']['scalar'] for r in rows],[7,7]);self.assertTrue(all(r['public_equation_verified'] for r in rows))
  EVENTS.append({'kind':'actual_fixed_coverage','pids':[r['pid'] for r in pr],'counts':v['observed'],'decoder_statuses':v['decoder_statuses'],'BSGS_scalars':[7,7],'scientific_runs':0})
 def test_01b_framed_toy_route_preserves_logical_outputs(self):
  import framing
  ctx=copy.deepcopy(self.ctx);ctx['framing_part_bytes']=65536
  case=self.root/'framed-route';case.mkdir();out=case/'execution'
  result=d.execute(ARGS.repo_root,ARGS.contracts_root,self.input,out,ctx,self.protocol)
  self.assertEqual(result['status'],'complete')
  bundle,findings=exp.make(self.protocol,out,ARGS.contracts_root,case/'export');self.assertEqual(findings,[])
  checked=checker.check(out,self.protocol,case/'export/export.json',ARGS.repo_root,ARGS.contracts_root,result['trusted_launch_sha256'])
  self.assertEqual(checked['operational_status'],'complete')
  logical=framing.open_logical(out/'candidate/result/raw')
  for name,path in logical.items():self.assertEqual(d.sha_file(path),d.sha_file(self.out/'candidate/result/raw'/name),name)
  EVENTS.append({'kind':'actual_framed_toy_route','status':result['status'],'logical_files_equal':len(logical),'physical_solver_rows':len(bundle['runs']),'scientific_draws':0})
 def test_02_unchanged_native_json_and_cli(self):
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','unit_native')
  for arm in ('candidate','baseline'):
   out=self.out/arm;body=d.read(out/'manifest.yaml')['run'];launch=d.read(out/'launch.json');plan=d.read(out/'native-plan.json');trial={'id':arm,'run_id':body['id'],'parameters':{'fixture_only':True}};old=(out/'manifest.yaml').read_bytes();before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now()
   r=native.complete_manifest(out,plan,'native-plan.json',d.sha_file(out/'native-plan.json'),trial,launch['authority'],launch['argv'],launch['check_argv'],launch['started_at'],body['timing']['finished_at'])
   self.assertEqual(r['action'],'unchanged');self.assertEqual((out/'manifest.yaml').read_bytes(),old)
   EVENTS.append({'kind':'native_complete_manifest','arm':arm,'started_at':start,'finished_at':d.now(),'source_before':before,'source_after':d.snapshot(ARGS.repo_root,ARGS.contracts_root),'result':r,'exact_manifest_bytes_preserved':True})
  for args in (['validate',str(self.protocol)],['check-export',str(self.root/'export/export.json'),'--protocol',str(self.protocol),'--verify-files']):
   r=cli([sys.executable,'-B',str(Path(ARGS.contracts_root)/'tools/experiment_protocol.py')]+args);self.assertEqual(r.returncode,0,r.stdout.decode()+r.stderr.decode())
 def test_03_same_path_isolated_metadata_mutations(self):
  mutations={
   'missing_arm':lambda p,b,r:r['processes'].pop(),
   'cloned_pid':lambda p,b,r:r['processes'][1].update(pid=r['processes'][0]['pid']),
   'row_reuse':lambda p,b,r:b['runs'][1].update(backend_ref=b['runs'][0]['backend_ref']),
   'instance':lambda p,b,r:b['runs'][1].update(instance_id='wrong'),
   'analysis':lambda p,b,r:b['analysis'].pop('script'),
   'physical_count':lambda p,b,r:b['runs'][0]['measurements']['counted'].update(physical_invocations=2),
   'false_completion':lambda p,b,r:b['runs'][0].update(status='infra_error'),
   'instrument_commit':lambda p,b,r:[a['instrument'].update(commit='0'*40) for a in p['arms']]}
  targets=[self.protocol,self.root/'export/export.json',self.out/'registry.json']
  for name,mutate in mutations.items():
   self.valid();p=d.read(targets[0]);b=d.read(targets[1]);reg=d.read(targets[2]);mutate(p,b,reg)
   if name in ('missing_arm','cloned_pid'):
    encoded=d.canonical(reg);b['host']['sha256']=d.sha(encoded)
    for item in b['files']+[f for row in b['runs'] for f in row['artifacts']]:
     if (self.root/'export'/item['path']).resolve()==targets[2].resolve():item.update(sha256=d.sha(encoded),bytes=len(encoded))
   if name=='false_completion':b['flow']=exp.ep_module(ARGS.contracts_root).compute_flow(b['runs']);b['runs'][0]['outcome_class']='not_completed'
   if name=='instrument_commit':
    p['freeze']['protocol_sha256']=exp.ep_module(ARGS.contracts_root).protocol_hash(p)
    b['protocol']['sha256']=p['freeze']['protocol_sha256'];b['source']['commit']='0'*40
    for a in b['arms']:a['commit']='0'*40
   case=self.root/'negative'/name;case.mkdir(parents=True);old=[t.read_bytes() for t in targets]
   for i,(target,obj) in enumerate(zip(targets,[p,b,reg])):
    (case/f'{i}.before').write_bytes(old[i]);bad=d.canonical(obj);(case/f'{i}.mutated').write_bytes(bad);target.write_bytes(bad)
   try:
    try:self.valid()
    except (ValueError,KeyError) as error:message=str(error)
    else:self.fail('accepted '+name)
   finally:
    for t,raw in zip(targets,old):t.write_bytes(raw)
   if name in ('missing_arm','cloned_pid'):self.assertIn('missing or cloned process',message)
   if name=='instrument_commit':self.assertTrue('input/source/protocol binding' in message or 'false instrument' in message)
   EVENTS.append({'kind':'isolated_negative','name':name,'baseline_passed_same_paths':True,'single_logical_mutation':True,'dependent_hashes_recomputed':name in ('missing_arm','cloned_pid','false_completion'),'refused':True,'refusal':message})
 def test_04_bytes_source_native_and_parser_refusals(self):
  for text in ('{"x":0,"x":1}','x: 1','{"x":NaN}','{"x":1e999}','{'):
   with self.assertRaises(ValueError):d.loads(text)
  for name,path,fn in [('member',self.out/'candidate/result/raw/traces.jsonl',lambda b:b+b'{}\n'),('partial',self.out/'candidate/result/raw/traces.jsonl',lambda b:b[:-1]),('seal',self.out/'candidate/seal.json',lambda b:d.canonical({**d.loads(b),'tree_sha256':'0'*64})),('source',self.out/'candidate/process.json',lambda b:d.canonical({**d.loads(b),'source_publication_commit':'0'*40}))]:
   self.valid();old=path.read_bytes();bad=fn(old);case=self.root/'negative'/name;case.mkdir(parents=True);(case/'before').write_bytes(old);(case/'mutated').write_bytes(bad);path.write_bytes(bad)
   try:
    with self.assertRaises((ValueError,KeyError)):self.valid()
   finally:path.write_bytes(old)
   EVENTS.append({'kind':'file_negative','name':name,'baseline_passed_same_paths':True,'refused':True})
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','unit_native_bad');out=self.out/'candidate';old=(out/'manifest.yaml').read_bytes();m=d.loads(old);launch=d.read(out/'launch.json');plan=d.read(out/'native-plan.json');trial={'id':'candidate','run_id':m['run']['id'],'parameters':{'fixture_only':True}}
  for name,fn in [('commit',lambda x:x['run']['code'].update(commit='0'*40)),('command',lambda x:x['run']['code'].update(command=['false'])),('boolean',lambda x:x['run'].update(attack_claimed=0)),('approval',lambda x:x['run'].update(approved_by='DEC-20000101-000000')),('task',lambda x:x['run'].update(task_id='TASK-20000101-000000')),('trial',lambda x:x['run'].update(trial_id='wrong')),('input_plan',lambda x:x['run']['inputs'].update(plan_sha256='0'*64)),('environment_source',lambda x:x['run']['environment']['source_sha256'].update({'tools/experiment_execution.py':'0'*64}))]:
   bad=copy.deepcopy(m);fn(bad);case=self.root/'negative'/('native_'+name);case.mkdir(parents=True);(case/'before').write_bytes(old);(case/'mutated').write_bytes(d.canonical(bad));(out/'manifest.yaml').write_bytes(d.canonical(bad));start=d.now()
   try:
    with self.assertRaises(native.EnvelopeRefused):native.complete_manifest(out,plan,'native-plan.json',d.sha_file(out/'native-plan.json'),trial,launch['authority'],launch['argv'],launch['check_argv'],launch['started_at'],m['run']['timing']['finished_at'])
   finally:(out/'manifest.yaml').write_bytes(old)
   EVENTS.append({'kind':'native_negative','name':name,'started_at':start,'finished_at':d.now(),'refused':True})
 def test_05_real_failed_children_truthful_incomplete(self):
  case=self.root/'failed-children';case.mkdir();out=case/'execution';r=d.execute(ARGS.repo_root,ARGS.contracts_root,self.input,out,self.ctx,self.protocol,{'candidate':'nonzero','baseline':'nonzero'})
  self.assertEqual(r['status'],'incomplete');b,f=exp.make(self.protocol,out,ARGS.contracts_root,case/'export');self.assertEqual(f,[]);self.assertEqual([r['status'] for r in b['runs']],['infra_error','infra_error']);self.assertEqual(checker.check(out,self.protocol,case/'export/export.json',ARGS.repo_root,ARGS.contracts_root,r['trusted_launch_sha256'])['operational_status'],'incomplete')
  procs=[d.read(out/a/'process.json') for a in ('candidate','baseline')];self.assertTrue(all(r['returncode']!=0 and r['termination_ack']['wait_returned'] for r in procs));EVENTS.append({'kind':'actual_failed_children','pids':[r['pid'] for r in procs],'returncodes':[r['returncode'] for r in procs],'partial_markers_retained':True,'no_zero_filled_completion':True})
 def test_06_real_watchdog_escalation_and_byte_guard(self):
  for name,fault,limits in [('timeout','hang',{'seconds':0.3,'terminate_grace_seconds':0.2}),('escalation','ignore-term',{'seconds':2,'terminate_grace_seconds':0.1}),('filecap',None,{'file_bytes':128}),('treecap',None,{'tree_bytes':128}),('logcap','flood',{'log_bytes':1024})]:
   ctx=copy.deepcopy(self.ctx);ctx['limits'].update(limits);case=self.root/name;case.mkdir()
   r=d.launch_arm('candidate',ARGS.repo_root,ARGS.contracts_root,self.input,case/'candidate',ctx,fault);self.assertFalse(r['operational_complete']);self.assertTrue(r['termination_ack']['wait_returned']);self.assertTrue((case/'candidate/stdout.log').is_file());self.assertTrue((case/'candidate/stderr.log').is_file())
   try:os.kill(r['pid'],0)
   except ProcessLookupError:pass
   else:self.fail('child remains alive')
   if name=='escalation':self.assertEqual([x['signal'] for x in r['signals']],['SIGTERM','SIGKILL'])
   if name=='filecap':self.assertNotEqual(r['returncode'],0)
   EVENTS.append({'kind':'actual_resource_control','name':name,'pid':r['pid'],'returncode':r['returncode'],'resource_stop':r['resource_stop'],'signals':r['signals'],'wait_returned':True,'all_partial_bytes_retained':True})
 def test_07_job_law_static_full_schedule_and_no_authority_bypass(self):
  plan=adapter.static_schedule(ARGS.repo_root);self.assertEqual(plan['jobs'],764928);self.assertEqual(plan['counts'],adapter.FULL);self.assertEqual(plan['scientific_draws'],0);self.assertEqual(len(plan['calibration_arms']),8);self.assertEqual(len(plan['job_kinds']),3);self.assertEqual({tuple(x) for x in plan['six_confirmation_cells']},{(x['radius'],x['erasure_cap']) for x in checker.records(self.out/'candidate/result/raw/decoder-cells.jsonl')});EVENTS.append({'kind':'actual_static_plan_only','result':plan})
  x=d.read(self.input);bad=copy.deepcopy(x['plan']);bad['jobs'][1]['id']=bad['jobs'][0]['id']
  with self.assertRaisesRegex(ValueError,'duplicate/unfrozen job'):adapter.expected_from_jobs(x['public'],bad)
  bad=copy.deepcopy(x);bad['public']['curves'][0]['model']['r']=31
  with self.assertRaises(ValueError):d.input_check(bad)
  fake=self.root/'no-native-context';fake.mkdir()
  with self.assertRaises((ValueError,OSError,KeyError,TypeError)):d.production_authority(ARGS.repo_root,fake,self.root/'missing-plan.json','fake',self.root/'missing-config.json')
  self.assertFalse((fake/'shared').exists())
 def test_08_lossless_no_duplicate_publication_stream(self):
  path=self.out/'candidate/result/raw/decoder-cells.jsonl';sink=io.BytesIO();r=d.stream_payload(path,sink,257);self.assertEqual(sink.getvalue(),path.read_bytes());self.assertEqual(r,{'sha256':d.sha_file(path),'bytes':path.stat().st_size,'local_duplicate_bytes':0});EVENTS.append({'kind':'actual_lossless_stream','source_sha256':r['sha256'],'bytes':r['bytes'],'chunk_bytes':257,'source_unchanged':True,'network_calls':0,'publication_or_deletion':False})

 def test_09_resealed_source_public_and_process_mutations(self):
  import base64
  files=[p for p in self.out.rglob('*') if p.is_file()]+[self.root/'export/export.json',self.input]
  originals={p:p.read_bytes() for p in files}
  def overwrite(p,obj):p.write_bytes(d.canonical(obj))
  def reseal():
   for arm in ('candidate','baseline'):
    root=self.out/arm;pr=d.read(root/'process.json');seal=d.read(root/'seal.json')
    completion=root/'result/raw/engine-completion.json'
    if completion.exists():
     comp=d.read(completion)
     for n,row in list(comp['files'].items()):
      q=completion.parent/n
      if not q.exists():comp['files'].pop(n);continue
      row.update(bytes=q.stat().st_size,sha256=d.sha_file(q))
     overwrite(completion,comp)
    for row in seal['files']:
     q=root/'result'/row['path'];row.update(bytes=q.stat().st_size,sha256=d.sha_file(q))
    seal['tree_sha256']=d.sha(d.canonical(seal['files']));seal['process_sha256']=d.sha_file(root/'process.json');overwrite(root/'seal.json',seal)
   reg=d.read(self.out/'registry.json')
   for row in reg['processes']:
    row['process_sha256']=d.sha_file(self.out/row['arm']/'process.json');row['pid']=d.read(self.out/row['arm']/'process.json')['pid']
   overwrite(self.out/'registry.json',reg)
   b=d.read(self.root/'export/export.json');b['host']['sha256']=d.sha_file(self.out/'registry.json');b['backend_record']['registry']=reg
   for row in b['runs']:
    pr=d.read(self.out/row['arm']/'process.json');row['worker']=str(pr['pid']);row['backend_ref']=row['arm']+'/'+str(pr['pid'])
   for row in b['files']+[q for row in b['runs'] for q in row['artifacts']]:
    p=(self.root/'export'/row['path']).resolve()
    if p.exists():row.update(bytes=p.stat().st_size,sha256=d.sha_file(p))
   b['files']=[r for r in b['files'] if (self.root/'export'/r['path']).exists()]
   for row in b['runs']:row['artifacts']=[r for r in row['artifacts'] if (self.root/'export'/r['path']).exists()]
   overwrite(self.root/'export/export.json',b)
  for name in ('omit-native','extra-source','alter-transitive','scalar-zero','scalar-nonzero','prepared-invalid','prepared-valid','pid-plausible','pid-large','argv-forgery','input-forgery','missing-job','missing-member'):
   self.valid();case=self.root/'negative'/name;case.mkdir(parents=True)
   for p,b in originals.items():(case/'before'/p.relative_to(self.root)).parent.mkdir(parents=True,exist_ok=True);(case/'before'/p.relative_to(self.root)).write_bytes(b)
   if name in ('omit-native','extra-source','alter-transitive'):
    for arm in ('candidate','baseline'):
     p=self.out/arm/'process.json';pr=d.read(p)
     for key in ('source_before','source_after'):
      captures=pr[key]['files']
      if name=='omit-native':captures.pop('tools/experiment_execution.py')
      elif name=='extra-source':captures['invented-extra.py']={'sha256':d.sha(b'extra'),'bytes':5,'base64':base64.b64encode(b'extra').decode()}
      else:
       row=captures['tools/fast_yaml.py'];raw=base64.b64decode(row['base64'])+b'\n# altered\n';row.update(bytes=len(raw),sha256=d.sha(raw),base64=base64.b64encode(raw).decode())
     overwrite(p,pr)
    x=d.read(self.input);x['provenance']['source_fingerprint']=d.sha(d.canonical(d.source_map(pr['source_before'])));overwrite(self.input,x)
   elif name.startswith('scalar'):
    p=self.out/'baseline/result/bsgs.json';obj=d.read(p);obj['rows'][0]['answer']['scalar']=0 if name.endswith('zero') and name!='scalar-nonzero' else 8;obj['rows'][0]['public_equation_verified']=True;overwrite(p,obj)
   elif name.startswith('prepared'):
    p=self.out/'candidate/result/raw/setups.jsonl';rows=list(checker.records(p));row=rows[0]
    if name=='prepared-invalid':row['prepared_base']=[0,0]
    else:
     pv=d.module(d.HERE/'public_verify.py','mutation_public');row['prepared_base']=list(pv.mul(2,pv.point(row['base'],row['model']),row['model']))
    p.write_bytes(b''.join(d.canonical(x) for x in rows))
   elif name=='missing-job':
    p=self.out/'candidate/result/raw/single-points.jsonl';rows=list(checker.records(p));p.write_bytes(b''.join(d.canonical(x) for x in rows[:-1]))
   elif name=='missing-member':
    p=self.out/'candidate/result/raw/single-points.jsonl';p.rename(case/'removed-original-single-points.jsonl')
    seal=d.read(self.out/'candidate/seal.json');seal['files']=[r for r in seal['files'] if r['path']!='raw/single-points.jsonl'];overwrite(self.out/'candidate/seal.json',seal)
   else:
    p=self.out/'candidate/process.json';pr=d.read(p)
    if name=='argv-forgery':
     pr['argv']=list(pr['argv']);pr['argv'][0]='/invented/plausible-python'
    elif name=='input-forgery':pr['input']['path']=str(self.input)+'.invented'
    else:pr.update(pid=2147483646 if name=='pid-large' else 42424,parent_pid=42423,start_ticks=12345)
    overwrite(p,pr)
    if name=='argv-forgery':
     root=self.out/'candidate';launch=d.read(root/'launch.json');launch['argv']=pr['argv'];overwrite(root/'launch.json',launch);(root/'command.txt').write_text(json.dumps(pr['argv'])+'\n');manifest=d.read(root/'manifest.yaml');manifest['run']['code']['command']=pr['argv'];overwrite(root/'manifest.yaml',manifest)
   reseal()
   try:
    with self.assertRaises(ValueError) as caught:self.valid()
    message=str(caught.exception)
    expected='exact source capture' if name in ('omit-native','extra-source') else 'source capture/publication' if name=='alter-transitive' else 'public scalar' if name.startswith('scalar') else 'public point' if name=='prepared-invalid' else 'public prepared base' if name=='prepared-valid' else 'missing/duplicate job' if name=='missing-job' else 'required members' if name=='missing-member' else 'trusted launch input/source' if name=='input-forgery' else 'trusted launch observation'
    self.assertIn(expected,message)
    EVENTS.append({'kind':'resealed_known_false','name':name,'same_path_positive_first':True,'refusal':message,'trusted_record_held_fixed':True})
   finally:
    for p in files:
     q=case/'mutated'/p.relative_to(self.root);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes()) if p.exists() else q.write_bytes(b'ABSENT: original bytes retained in before witness and removed-original file')
    for p,b in originals.items():p.write_bytes(b)
   self.valid()
 def test_10_actual_native_nested_lifecycle(self):
  import datetime,time,signal
  d.lifecycle.subreaper()
  sys.path.insert(0,str(Path(ARGS.contracts_root)/'tools'));native=d.module(Path(ARGS.contracts_root)/'tools/experiment_execution.py','unit_native_lifecycle')
  for mode in ('normal','watchdog','expiry','exception','term','kill','race'):
   for arm in ('candidate','baseline','generator'):
    case=self.root/'native-lifecycle'/mode/arm;case.mkdir(parents=True)
    marker=case/'observations.jsonl';lock=(case/'lock').open('wb')
    argv=[sys.executable,'-B',str(d.HERE/'test_contracts.py'),'--lifecycle-helper',mode,'--arm',arm,'--case',str(case),'--input',str(self.input),'--repo-root',str(ARGS.repo_root)]
    authority={'expires_at':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=2 if mode=='expiry' else 20)).isoformat()};trial={'memory_mb':2048,'watchdog_seconds':2 if mode=='watchdog' else 8}
    start=d.now();result=native.run_process(argv,Path(ARGS.repo_root),case,'native-',trial,authority,lock.fileno());lock.close()
    observations=list(checker.records(marker));self.assertEqual(len(observations),1,mode);record=observations[0];pid=record['os']['pid']
    adopted=None;deadline=time.monotonic()+4
    while time.monotonic()<deadline:
     try:
      waited,status=os.waitpid(pid,os.WNOHANG)
      if waited==pid:adopted={'pid':waited,'raw_wait_status':status,'waitpid_returned':True,'observer_pid':os.getpid(),'actually_adopted':True};break
     except ChildProcessError:
      if not Path('/proc',str(pid)).exists():break
     time.sleep(.01)
    live=Path('/proc',str(pid)).exists();self.assertFalse(live,repr((mode,arm,pid,d.observer.os_fact(pid) if live else None)))
    if mode in ('watchdog','expiry','exception','term','kill','race'):self.assertIsNotNone(adopted,'independent subreaper did not obtain wait acknowledgment')
    EVENTS.append({'kind':'actual_native_nested','mode':mode,'arm':arm,'argv':argv,'started_at':start,'finished_at':d.now(),'native_result':result,'independent_os_launch':record,'adopted_wait':adopted,'live_after':live,'scope':'actual unchanged native run_process; closure observed independently'})
 def test_11_parent_framing_and_honest_partial(self):
  import time
  ctx=copy.deepcopy(self.ctx);ctx['limits']['document_bytes']=128;case=self.root/'framing128';case.mkdir()
  with self.assertRaisesRegex(ValueError,'document byte limit'):d.launch_arm('candidate',ARGS.repo_root,ARGS.contracts_root,self.input,case/'candidate',ctx)
  self.assertTrue((case/'candidate/result/raw/engine-completion.json').is_file());self.assertTrue((case/'candidate/process.json').is_file());self.assertLessEqual((case/'candidate/process.json').stat().st_size,128)
  self.assertFalse((case/'candidate/seal.json').exists());self.assertFalse((case/'export/export.json').exists())
  EVENTS.append({'kind':'parent_document_cap','configured_bytes':128,'status':'operational_incomplete','typed_export_present':False,'all_available_partial_bytes_retained':True,'scientific_state':'UNKNOWN'})
 def test_12_fixed_generator_and_actual_import_guard(self):
  import time
  for name,fault,limits in [('positive',None,{}),('nonzero','nonzero',{}),('timeout','hang',{'seconds':2}),('escalation','ignore-term',{'seconds':2,'terminate_grace_seconds':.1})]:
   case=self.root/'fixed-generator'/name;case.mkdir(parents=True);ctx=copy.deepcopy(self.ctx);ctx['limits'].update(limits)
   pr=d.launch_arm('generator',ARGS.repo_root,ARGS.contracts_root,self.input,case/'generator',ctx,fault)
   self.assertEqual(pr['operational_complete'],fault is None);self.assertTrue(pr['termination_ack']['wait_returned']);self.assertFalse(Path('/proc',str(pr['pid'])).exists())
   if name=='positive':self.assertEqual(d.read(case/'generator/result/fixed-output.json')['public'],d.read(self.input)['public'])
   if name=='escalation':self.assertEqual([x['signal'] for x in pr['signals']],['SIGTERM','SIGKILL'])
   EVENTS.append({'kind':'fixed_generator','name':name,'process':pr,'scientific_draws':0})
  with self.assertRaisesRegex(ValueError,'undeclared actual repository import'):d.module(Path(ARGS.repo_root)/'harness/__init__.py','forbidden_actual_repo_import')
  EVENTS.append({'kind':'actual_import_guard','path':'harness/__init__.py','refused_before_execution':True})
def lifecycle_helper():
 import signal,time
 p=argparse.ArgumentParser();p.add_argument('--lifecycle-helper');p.add_argument('--arm');p.add_argument('--case');p.add_argument('--input');p.add_argument('--repo-root');a=p.parse_args();case=Path(a.case);mode=a.lifecycle_helper
 # All three paths use the same safe wrapper. Generator uses only fixed constants.
 target=d.HERE/('cohort_adapter.py' if a.arm=='generator' else a.arm+'.py')
 args=['--repo-root',a.repo_root,'--input',a.input,'--out',str(case/'child-result'),'--fixture-fault','hang']
 if a.arm=='baseline':args+=['--candidate',str(case/'unused-candidate')]
 if a.arm=='generator':args+=['--fixed-worker']
 argv=d.lifecycle.wrapper_argv(target,args,2<<30,16<<20)
 if mode=='race':
  argv[3]='probe';argv[4:4]=['--fixture-startup-delay','1.5']
 with (case/'child-stdout.log').open('xb') as stdout,(case/'child-stderr.log').open('xb') as stderr:
  proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)
  record=d.observer.capture(proc,argv,a.input,d.source_map(d.snapshot(a.repo_root,a.repo_root)));d.write(case/'observations.jsonl',record)
  if mode=='normal':proc.terminate();proc.wait();d.write(case/'parent-wait.json',{'pid':proc.pid,'wait_returned':True,'returncode':proc.returncode});return
  if mode=='race':raise RuntimeError('disclosed parent failure during wrapper install race')
  time.sleep(.15)
  if mode=='exception':raise RuntimeError('disclosed helper exception')
  if mode=='term':os.kill(os.getpid(),signal.SIGTERM)
  if mode=='kill':os.kill(os.getpid(),signal.SIGKILL)
  time.sleep(20)
if __name__=='__main__' and '--lifecycle-helper' in sys.argv:
 lifecycle_helper();raise SystemExit(0)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--contracts-root',required=True);p.add_argument('--control-root',required=True);ARGS=p.parse_args();before=d.snapshot(ARGS.repo_root,ARGS.contracts_root);start=d.now();r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));Path(ARGS.control_root).mkdir(parents=True,exist_ok=True);d.write(Path(ARGS.control_root)/'checks.json',{'schema':'controlled-followup-v6.unit-checks/v1','started_at':start,'finished_at':d.now(),'source_before':before,'source_after':d.snapshot(ARGS.repo_root,ARGS.contracts_root),'events':EVENTS,'returncode':0 if r.wasSuccessful() else 1,'scientific_runs':0,'actual_vms':0,'fresh_entropy_draws':0},64<<20);raise SystemExit(0 if r.wasSuccessful() else 1)
