"""After final archive: fresh full remote capsule verification and exact selection; no unlink."""
from pathlib import Path
import base64,datetime,gzip,hashlib,io,json,os,subprocess,sys,tarfile,time
R=Path('/workspace/classical-ecdlp-validation-ready');F=Path('/workspace/classical-ecdlp-endpoint-reuse/fresh48-20261105-root');sys.path.insert(0,str(R))
from tools.research_dispatch import validate_queue,GitRepositoryVerifier
from tools.goal_lanes import claim_summary
B='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/'
qpath=R/(B+'dispatch_queue.json');q=json.loads(qpath.read_bytes());by=validate_queue(q,repository_verifier=GitRepositoryVerifier(R));claims=claim_summary(R,qpath)
assert by['TASK-20261105-ad13ba']['state']=='completed' and claims['TASK-20261105-ad13ba']['status']=='released'
assert claims['TASK-20261105-ad13ba']['release']['outcome']=='completed'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
out=F/'new-review-hydration-exact-selection.json';assert not out.exists();rounds=[];selected=[]
roots={'TASK-20261105-85442c':Path('/workspace/classical-ecdlp-endpoint-reuse/independent-interstage-gap-20261105/TASK-20261105-85442c'),'TASK-20261105-fb2770':Path('/workspace/classical-ecdlp-endpoint-reuse/independent-interstage-gap-followup-20261105/TASK-20261105-fb2770')}
for task,S in roots.items():
 rel=next(p for p in by[task]['artifact_paths'] if p.endswith('/checks.json'));p=R/rel;v=json.loads(Path(str(p)+'.blob.json').read_bytes());manifest=json.loads((p.parent/'.artifacts.json').read_bytes())
 assert v['encoding']=='identity' and v['sha256']==v['content_sha256'] and v['size']==v['content_size'] and manifest['files'][p.name]=={'sha256':v['sha256'],'bytes':v['size']}
 assert p.stat().st_size==v['size'] and sha(p)==v['sha256'] and v['uri'].startswith('s3://setec-astronomy-artifacts/store/')
 argv=['/workspace/classical-ecdlp-endpoint-reuse/runtime-20261028/bin/aws','--region','us-east-2','--cli-connect-timeout','10','--cli-read-timeout','30','s3','cp',v['uri'],'-','--only-show-errors','--no-progress']
 started=now();c=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=180)
 err=c.stderr.decode(errors='replace')
 for k in ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN']:
  if os.environ.get(k):err=err.replace(os.environ[k],'[REDACTED_CREDENTIAL]')
 ep=F/(task+'-fresh-capsule-GET.stderr.txt');ep.write_text(err)
 assert c.returncode==0 and len(c.stdout)==v['size'] and hashlib.sha256(c.stdout).hexdigest()==v['sha256']
 d=json.loads(c.stdout);caps=d['capsule'];z=base64.b64decode(caps['data_base64'],validate=True);assert len(z)==caps['gzip_bytes'] and hashlib.sha256(z).hexdigest()==caps['gzip_sha256']
 members={x['path']:x for x in caps['members']};assert len(members)==len(caps['members'])==caps['member_count'];seen=[];checked=[]
 class Reader:
  def __init__(self):self.raw=gzip.GzipFile(fileobj=io.BytesIO(z));self.h=hashlib.sha256();self.count=0
  def read(self,n=-1):
   b=self.raw.read(n);self.h.update(b);self.count+=len(b);return b
 reader=Reader()
 with tarfile.open(fileobj=reader,mode='r|') as tf:
  for m in tf:
   assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.name in members and m.name not in seen
   row=members[m.name];assert m.size==row['bytes'];stream=tf.extractfile(m);h=hashlib.sha256();n=0
   for chunk in iter(lambda:stream.read(1<<20),b''):h.update(chunk);n+=len(chunk)
   assert n==row['bytes'] and h.hexdigest()==row['sha256'];physical=Path(row['physical_path']);assert physical==S/m.name and not physical.is_symlink() and physical.is_file() and physical.stat().st_size==n and sha(physical)==row['sha256']
   checked.append({'path':m.name,'bytes':n,'sha256':h.hexdigest(),'current_physical_match':True});seen.append(m.name)
 while reader.read(1<<20):pass
 assert set(seen)==set(members) and reader.count==caps['tar_bytes'] and reader.h.hexdigest()==caps['tar_sha256']
 # Selection occurs only after this entire remote capsule has passed all checks.
 for row in members.values():
  if '/mirror/exercise/runs/' in '/'+row['path'] and row['bytes']>1<<20:
   physical=Path(row['physical_path']);st=physical.stat();selected.append({'absolute_path':str(physical),'bytes':st.st_size,'sha256':row['sha256'],'device':st.st_dev,'inode':st.st_ino,'capsule_task':task,'capsule_member':row['path'],'kind':'large NEW native output hydration'})
 for physical in [p,S/'proposed'/rel]:
  assert physical.is_file() and not physical.is_symlink() and physical.stat().st_size==v['size'] and sha(physical)==v['sha256'];st=physical.stat();selected.append({'absolute_path':str(physical),'bytes':st.st_size,'sha256':v['sha256'],'device':st.st_dev,'inode':st.st_ino,'capsule_task':task,'capsule_member':None,'kind':'large checks payload hardlink; outer payload itself remote verified','canonical_pointer':str(Path(str(p)+'.blob.json')),'pointer_sha256':sha(Path(str(p)+'.blob.json'))})
 rounds.append({'task_id':task,'checks_path':rel,'outer_bytes':v['size'],'outer_sha256':v['sha256'],'uri':v['uri'],'get_argv':argv,'get_started_at':started,'get_finished_at':now(),'get_returncode':c.returncode,'get_wait_returned':True,'full_uncached_GET_verified':True,'readback_disk_spool_bytes':0,'gzip_sha256':caps['gzip_sha256'],'tar_sha256':caps['tar_sha256'],'all_member_hashes_verified':True,'all_current_physical_members_match':True,'members':checked})
assert len({x['absolute_path'] for x in selected})==len(selected)
record={'schema':'classical.ecdlp.new-review-hydration-selection/v1','recorded_at':now(),'source_archive_task':'TASK-20261105-ad13ba','source_archive_commit':by['TASK-20261105-ad13ba']['archive']['commit_sha'],'source_archive_parent':by['TASK-20261105-ad13ba']['archive']['parent_sha'],'rounds':rounds,'selected':selected,'selection_before_08_claim':True,'deletions':0,'preexisting_old_raw_selected':0,'remote_deletions':0,'source_utf8':Path(__file__).read_text(),'qualification':'Preparation only; exact frozen task scope and live native08 claim still required before any unlink. No fit claim.'}
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'selection':str(out),'files':len(selected),'unique_selected_inodes':len({(x['device'],x['inode']) for x in selected}),'logical_bytes':sum(x['bytes'] for x in selected),'all_remote_and_member_hashes_verified':True,'deletions':0}))
