"""Retire only frozen exact NEW review copies, after preparation and native claim."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sys,time
R=Path('/workspace/classical-ecdlp-validation-ready');F=Path('/workspace/classical-ecdlp-endpoint-reuse/fresh48-20261105-root');sys.path.insert(0,str(R))
from tools.research_dispatch import validate_queue,GitRepositoryVerifier
from tools.goal_lanes import claim_summary
ap=argparse.ArgumentParser();ap.add_argument('--owner',required=True);ap.add_argument('--epoch',type=int,required=True);a=ap.parse_args()
B='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/';qpath=R/(B+'dispatch_queue.json');q=json.loads(qpath.read_bytes());by=validate_queue(q,repository_verifier=GitRepositoryVerifier(R));claims=claim_summary(R,qpath)
assert by['TASK-20261105-ad13ba']['state']=='completed' and claims['TASK-20261105-ad13ba']['status']=='released' and claims['TASK-20261105-ad13ba']['release']['outcome']=='completed'
task=by['TASK-20261105-08d44b'];claim=claims[task['id']];assert claim['status']=='live' and claim['owner']==a.owner and claim['epoch']==a.epoch
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();free=lambda:os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
sp=F/'new-review-hydration-exact-selection.json';selection=json.loads(sp.read_bytes());policy=task['handoff']['local_retirement'];assert policy['selection_sha256']==sha(sp)
rows=selection['selected'];assert policy['exact_external_paths']==[r['absolute_path'] for r in rows] and len({r['absolute_path'] for r in rows})==len(rows)
assert selection['source_archive_commit']==by['TASK-20261105-ad13ba']['archive']['commit_sha'] and selection['deletions']==0 and selection['selection_before_08_claim'] is True
allowed={'TASK-20261105-85442c':Path('/workspace/classical-ecdlp-endpoint-reuse/independent-interstage-gap-20261105/TASK-20261105-85442c'),'TASK-20261105-fb2770':Path('/workspace/classical-ecdlp-endpoint-reuse/independent-interstage-gap-followup-20261105/TASK-20261105-fb2770')}
assert {r['task_id'] for r in selection['rounds']}==set(allowed)
for c in selection['rounds']:assert c['full_uncached_GET_verified'] and c['all_member_hashes_verified'] and c['all_current_physical_members_match'] and c['get_returncode']==0 and c['get_wait_returned']
for row in rows:
 p=Path(row['absolute_path']);S=allowed[row['capsule_task']];assert not p.is_symlink() and p.is_file();st=p.stat();assert st.st_size==row['bytes'] and st.st_dev==row['device'] and st.st_ino==row['inode'] and sha(p)==row['sha256']
 if row['capsule_member'] is not None:assert p==S/row['capsule_member'] and '/mirror/exercise/runs/' in '/'+row['capsule_member'] and st.st_size>1<<20
 else:
  rel=next(x for x in by[row['capsule_task']]['artifact_paths'] if x.endswith('/checks.json'));assert p in [R/rel,S/'proposed'/rel] and sha(Path(row['canonical_pointer']))==row['pointer_sha256']
journal=R/task['artifact_paths'][0];assert not journal.exists();journal.parent.mkdir(parents=True,exist_ok=True)
record={'schema':'classical.ecdlp.exact-new-review-hydration-retirement/v1','task_id':task['id'],'started_at':now(),'started_monotonic':time.monotonic(),'claim':claim,'phase':'all_exact_local_bytes_and_fresh_remote_capsules_verified_before_any_unlink','before_free_bytes':free(),'selection_literal_sha256':sha(sp),'selection':selection,'files':[],'scientific_runs':0,'new_nonces_or_cohorts':0,'remote_deletions':0,'preexisting_old_raw_removed':0,'source_utf8':Path(__file__).read_text()}
def save():journal.write_text(json.dumps(record,indent=2)+'\n')
save()
for row in rows:
 p=Path(row['absolute_path']);st=p.stat();assert st.st_dev==row['device'] and st.st_ino==row['inode'] and st.st_size==row['bytes'] and sha(p)==row['sha256'] and not p.is_symlink();p.unlink();record['files'].append({**row,'unlinked':True,'unlinked_at':now()});save()
assert all(not Path(r['absolute_path']).exists() for r in rows)
for row in rows:
 if row.get('canonical_pointer'):assert Path(row['canonical_pointer']).is_file() and sha(Path(row['canonical_pointer']))==row['pointer_sha256']
record.update(phase='completed',finished_at=now(),elapsed_seconds=time.monotonic()-record['started_monotonic'],after_free_bytes=free(),hydrated_logical_bytes_unlinked=sum(r['bytes'] for r in rows),unique_selected_inodes=len({(r['device'],r['inode']) for r in rows}),restoration='Use unchanged artifacts.py pull for exact canonical checks paths, then decode their lossless base64-gzip-tar capsule and restore only listed safe relative members to their recorded NEW root; preserve pointers and all remote bytes. Small helpers, source, receipts and witnesses remain local.',qualification='Only redundant NEW large output hydrations were retired. This records storage operations; no runtime or fit assurance.');save()
print(json.dumps({'journal':str(journal),'files_unlinked':len(rows),'before_free_bytes':record['before_free_bytes'],'after_free_bytes':record['after_free_bytes'],'old_raw_removed':0,'remote_deleted':0}))
