#!/usr/bin/env python3
"""Root-only exact native-run publication using unchanged store APIs.
Streams uncached full GET without a local readback copy. Retains hydrated bytes and writes supported identity pointers and authoritative
modern manifests only after every uncached full GET matches. No remote deletes.
"""
import argparse,datetime,hashlib,importlib.util,json,sys,tempfile,os,subprocess,threading,time
from dataclasses import replace
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--directory',action='append',default=[]);p.add_argument('--file',action='append',default=[]);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--publish',action='store_true');p.add_argument('--trial-plan',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--expected-receipt-sha256',required=True);a=p.parse_args();root=a.repo.resolve()
path=root/'tools/artifacts/artifacts.py';spec=importlib.util.spec_from_file_location('_unchanged_store',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
cfg=replace(m.Config.load(root),read_url=None);assert cfg.remote.rstrip('/')=='s3://setec-astronomy-artifacts/store' and not cfg.endpoint
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
# This is publication after execution, not an execution route or acceptance gate.
# Scope comes from one exact immutable native plan/receipt, not arbitrary /runs/.
plan_path=a.trial_plan if a.trial_plan.is_absolute() else root/a.trial_plan
assert plan_path.resolve().is_relative_to(root) and plan_path.is_file() and not plan_path.is_symlink()
plan_bytes=plan_path.read_bytes();plan=json.loads(plan_bytes)
assert plan['schema']=='crypto.autoresearch.trial_plan.v1'
trials=[t for t in plan['trials'] if t['run_id']==a.run_id];assert len(trials)==1
trial=trials[0];run_rel='experiments/'+plan['experiment_id']+'/runs/'+a.run_id
run_base=root/run_rel;assert run_base.is_dir() and run_base.resolve().is_relative_to(root)
assert a.directory==[run_rel] and not a.file, 'Exactly the selected native run tree only'
for parent in [run_base,*run_base.parents]:
 if parent==root:break
 assert not parent.is_symlink()
native_receipt=run_base/'execution-receipt.json';native_bytes=native_receipt.read_bytes()
assert hashlib.sha256(native_bytes).hexdigest()==a.expected_receipt_sha256
native=json.loads(native_bytes)
assert native['schema']=='crypto.autoresearch.trial_receipt.v1'
assert native['plan_sha256']==hashlib.sha256(plan_bytes).hexdigest()
assert native['run_id']==a.run_id and native['trial_id']==trial['id']
assert native.get('finished_at') and native.get('status')
# Native stored files and entry paths remain present and are never remapped.
# Publication metadata records source/native mapping; native receipt stays exact.
for entry in native.get('artifact_storage',{}).values():
 stored=run_base/entry['path'];assert stored.is_file() and not stored.is_symlink()
 if not stored.name.endswith('.blob.json'):assert sha(stored)==entry['sha256']
publication_scope={'plan_path':plan_path.relative_to(root).as_posix(),'plan_sha256':hashlib.sha256(plan_bytes).hexdigest(),'experiment_id':plan['experiment_id'],'task_id':plan['task_id'],'trial_id':trial['id'],'run_id':a.run_id,'native_receipt_sha256':a.expected_receipt_sha256,'native_status':native['status'],'native_artifact_storage':native.get('artifact_storage',{}),'qualification':'Publication and exact identity checks only; status retained literally, no acceptance or scientific interpretation.'}

items=[]
assert a.directory or a.file
candidates=[]
for directory in a.directory:
 base=root/directory;assert base.is_dir() and base.resolve().is_relative_to(root)
 assert directory==run_rel and 'derived-supervisor-views' not in directory
 assert directory==run_rel
 candidates.extend(sorted(base.rglob('*')))
for name in a.file:
 f=root/name;assert f.is_file() and f.resolve().is_relative_to(root) and not f.is_symlink()
 assert Path(name).is_relative_to(Path(run_rel)) and 'derived-supervisor-views' not in name
 candidates.append(f)
for f in dict.fromkeys(candidates):
  assert not f.is_symlink()
  if not f.is_file() or f.name.endswith('.blob.json'):continue
  rel=f.relative_to(root).as_posix()
  if not m.belongs_in_store(rel,f.stat().st_size,cfg.policy):continue
  assert not Path(str(f)+'.gz').exists() and not Path(str(f)+'.gz.blob.json').exists()
  digest=sha(f);size=f.stat().st_size
  pointer={'schema':'crypto.autoresearch.blob_pointer.v1','encoding':'identity','sha256':digest,'size':size,'content_sha256':digest,'content_size':size,'uri':cfg.remote.rstrip('/')+'/'+m.object_key(digest)}
  ptr=Path(str(f)+'.blob.json');assert not ptr.exists() or json.loads(ptr.read_text())==pointer
  items.append({'path':rel,'bytes':size,'sha256':digest,'pointer':pointer})
assert len(items)==len({x['path'] for x in items})
r={'schema':'classical.ecdlp.assigned-file-publication/v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifact_tool_sha256':sha(path),'artifacts':items,'remote_prefix':cfg.remote,'remote_deletions':False,'hydrated_bytes_retained':True,'all_full_s3_gets_verified':False,'publication_requested':a.publish}
if not a.publish:print(json.dumps(r,indent=2));raise SystemExit()
assert not a.receipt.exists();remote=m.Remote(cfg);verified=[]
# Full remote GET is streamed directly into SHA/byte verification; no local spool.
for i,x in enumerate(items):
 f=root/x['path'];sent=remote.put(x['sha256'],f,x['bytes'])
 aws=os.environ.get('ARTIFACTS_AWS','aws')
 argv=[aws,'--region','us-east-2','--cli-connect-timeout','10','--cli-read-timeout','30','s3','cp',x['pointer']['uri'],'-','--only-show-errors','--no-progress']
 observed_start=datetime.datetime.now(datetime.timezone.utc).isoformat();h=hashlib.sha256();count=0;error_parts=[];error_bytes=[0];error_guard=[];deadline=time.monotonic()+180
 proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 def drain_errors():
  while True:
   b=proc.stderr.read(65536)
   if not b:break
   error_parts.append(b);error_bytes[0]+=len(b)
   if error_bytes[0]>1<<20:
    error_guard.append('stderr_1MiB_guard');proc.kill()
 reader=threading.Thread(target=drain_errors);reader.start()
 try:
  while True:
   b=proc.stdout.read(65536)
   if not b:break
   h.update(b);count+=len(b)
   if count>x['bytes'] or time.monotonic()>deadline:
    proc.kill();raise ValueError('Remote GET exceeded exact byte/deadline boundary')
  rc=proc.wait(timeout=30)
 finally:
  if proc.poll() is None:proc.kill();proc.wait()
  reader.join(timeout=5)
  assert not reader.is_alive()
  stderr=b''.join(error_parts).decode(errors='replace')
  for key in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN'):
   if os.environ.get(key):stderr=stderr.replace(os.environ[key],'[REDACTED_CREDENTIAL]')
  errpath=a.receipt.parent/(a.receipt.stem+'.get-'+str(i)+'.stderr.txt');errpath.parent.mkdir(parents=True,exist_ok=True)
  with errpath.open('x') as out:out.write(stderr)
 assert rc==0 and not error_guard and count==x['bytes'] and h.hexdigest()==x['sha256']
 assert f.stat().st_size==x['bytes'] and sha(f)==x['sha256']
 verified.append({'path':x['path'],'bytes':count,'sha256':h.hexdigest(),'put_sent_bytes':sent,'full_s3_get_verified':True,'readback_method':'uncached aws s3 cp object to stdout; entire body streamed through SHA256/byte verification','local_readback_spool_bytes':0,'get_argv':argv,'get_returncode':rc,'get_started_at':observed_start,'get_finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stderr_file':str(errpath)})
by={}
for x in items:
 f=root/x['path'];ptr=Path(str(f)+'.blob.json')
 if not ptr.exists():
  with ptr.open('x') as out:out.write(json.dumps(x['pointer'],indent=2)+'\n')
 entries=by.setdefault(f.parent,m.read_manifest(f.parent));entries[f.name]={'sha256':x['sha256'],'bytes':x['bytes']}
for d,entries in by.items():m.write_manifest(d,entries);m.write_gitignore(d,list(entries))
r.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_full_s3_gets_verified=True,readbacks=verified,storage_metadata=[{'path':(d/n).relative_to(root).as_posix(),'sha256':sha(d/n)} for d in by for n in ['.artifacts.json','.gitignore']])
assert native_receipt.read_bytes()==native_bytes and plan_path.read_bytes()==plan_bytes
r['native_run_scope']=publication_scope
a.receipt.parent.mkdir(parents=True,exist_ok=True)
with a.receipt.open('x') as out:out.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'receipt':str(a.receipt),'verified_artifacts':len(verified),'all_full_s3_gets_verified':True}))
