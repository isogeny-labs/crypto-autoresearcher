"""Apply only the user-authorized unsigned PCC fork reconciliation.

Both historical journals and every claim remain unchanged in their original
commits. The current-main journal is an exact prefix; native entries are new.
"""
from pathlib import Path
import base64,datetime as dt,gzip,hashlib,json,os,subprocess,sys,tempfile
R=Path('/tmp/ecd-git-repair-20261106/repository');O=Path('/tmp/ecd-reconcile-20261107');C=R/'research/pcc-fork-reconciliation-20261107'
sys.path.insert(0,str(R));from tools.pcc import pcc
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def write_json(path,document):
 with path.open('x') as f:json.dump(document,f,indent=2,sort_keys=True);f.write('\n')
s=json.loads((O/'input-snapshot.json').read_text());main=s['main_commit'];feature=s['feature_commit'];assert git('rev-parse','HEAD').decode().strip()==main;assert git('rev-parse','MERGE_HEAD').decode().strip()==feature
assert git('branch','--show-current').decode().strip()=='research/classical-ecdlp-continuation-20261107'
expected={'pcc/ledger.jsonl',*[f'docs/benchmarks/progress/{name}' for name in ('PROGRESS.md','progress.json','progress.pdf','progress.svg')]};assert set(git('diff','--name-only','--diff-filter=U').decode().splitlines())==expected
assert not C.exists()
proposal=Path('/tmp/ecd-git-repair-20261106/pcc-fork-proposal/PROPOSAL.md').read_bytes();assert sha(proposal)==s['proposal_sha256']=='27830a49ad644f20c71948ec456a19500450471f9f608ec0888602b42850da0e'
mainraw=git('show',main+':pcc/ledger.jsonl');oldraw=git('show',feature+':pcc/ledger.jsonl');reviewedraw=Path('/tmp/ecd-git-repair-20261106/pcc-fork-proposal/main-ledger.jsonl').read_bytes();assert mainraw.startswith(reviewedraw)
for name,raw in [('main',mainraw),('feature',oldraw)]:assert len(raw)==s['journals'][name]['bytes'] and sha(raw)==s['journals'][name]['sha256']
mainrows=pcc.read_ledger_text(mainraw.decode());oldrows=pcc.read_ledger_text(oldraw.decode());assert len(oldrows)==20 and all(e['type']=='claim' and 'sig' not in e for e in oldrows[1:])
for rows in (mainrows,oldrows):
 errors=[];pcc.check_chain(rows,errors);assert not errors,errors
krraw=git('show',main+':pcc/keyring.json');assert sha(krraw)==s['keyring_sha256'] and (R/'pcc/keyring.json').read_bytes()==krraw;kr=json.loads(krraw)
for claim in s['feature_claims']:
 raw=git('show',feature+':'+claim['path']);assert sha(raw)==claim['file_sha256'] and (R/claim['path']).read_bytes()==raw;assert pcc.claim_digest(json.loads(raw))==claim['claim_sha256']
auth={'schema':'administrative.owner-exception/v1','authorization_source':'User message in this conversation on 2026-11-07','authorization_text':'Yes authorized','authorized_question':'Do you authorize the prepared journal reconciliation, preserving both originals and re-registering the 19 unsigned claims?','proposal_sha256':sha(proposal),'recorded_at':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'One PCC fork reconciliation: current-main prefix,19 existing unsigned claim subjects as new registrations,one provenance note, both originals retained; old branch/PR2590 unchanged.','does_not_change':['claim content','existing event identities','signatures','keyring','verified standing','scientific results or hypothesis status','old experiment attempt/deadline limits']}
auth_bytes=(json.dumps(auth,indent=2,sort_keys=True)+'\n').encode();auth_sha=sha(auth_bytes)
candidate=O/'application-prepared-ledger.jsonl';assert not candidate.exists();candidate.write_bytes(mainraw);mapping=[]
for old in oldrows[1:]:
 new=pcc.append_entry(candidate,'claim',old['body']);assert new['body']==old['body'] and 'sig' not in new;mapping.append({'claim_id':old['body']['claim_id'],'claim_sha256':old['body']['claim_sha256'],'old_event_seq':old['seq'],'old_event_hash':old['hash'],'new_event_seq':new['seq'],'new_event_hash':new['hash']})
note=pcc.append_entry(candidate,'note',{'operation':'owner_authorized_unsigned_fork_reregistration','authorization_path':'research/pcc-fork-reconciliation-20261107/owner-authorization.json','authorization_sha256':auth_sha,'proposal_sha256':sha(proposal),'main_commit':main,'main_journal_sha256':sha(mainraw),'feature_commit':feature,'feature_journal_sha256':sha(oldraw),'feature_journal_path':'research/pcc-fork-reconciliation-20261107/feature-ledger.jsonl','registrations':mapping,'scope':'Existing claim subjects registered as new unsigned events; original fork journal remains a separate immutable chain, not a prefix. No signature or verification standing is imported.'})
newraw=candidate.read_bytes();newrows=pcc.read_ledger(candidate);errors=[];pcc.check_chain(newrows,errors);pcc.check_prefix(mainrows,newrows,errors);assert not errors,errors;assert newraw.startswith(mainraw);assert len(newrows)==len(mainrows)+20
old_prefix_errors=[];pcc.check_prefix(oldrows,newrows,old_prefix_errors);assert old_prefix_errors
standings=[]
for claim in s['feature_claims']:
 c=json.loads((R/claim['path']).read_bytes());before=pcc.standing(c,mainrows,kr);after=pcc.standing(c,newrows,kr);assert before==after==claim['standing_on_main_before_import'];standings.append({'claim_id':claim['claim_id'],'before':before['standing'],'after':after['standing'],'unchanged':True})
assert [e for e in newrows if 'sig' in e]==[e for e in mainrows if 'sig' in e]
C.mkdir(parents=True);(C/'feature-ledger.jsonl').write_bytes(oldraw);custody=[]
for name,raw in [('feature',oldraw),('main',mainraw),('reviewed-main',reviewedraw)]:
 file=C/(name+'-ledger.jsonl'+('' if name=='feature' else '.gz'));wire=raw if name=='feature' else gzip.compress(raw,mtime=0);assert len(wire)<65536;file.write_bytes(wire);assert (wire if name=='feature' else gzip.decompress(wire))==raw;custody.append({'name':name,'path':file.relative_to(R).as_posix(),'stored_bytes':len(wire),'stored_sha256':sha(wire),'encoding':'identity' if name=='feature' else 'gzip','content_bytes':len(raw),'content_sha256':sha(raw)})
(C/'owner-authorization.json').write_bytes(auth_bytes);(C/'application-script.py').write_bytes(Path(__file__).read_bytes())
fd,tmp=tempfile.mkstemp(prefix='.authorized-fork-',dir=R/'pcc')
with os.fdopen(fd,'wb') as f:f.write(newraw)
os.replace(tmp,R/'pcc/ledger.jsonl');assert (R/'pcc/ledger.jsonl').read_bytes()==newraw
receipt={'schema':'pcc.authorized-fork-reconciliation/v1','applied_at':dt.datetime.now(dt.timezone.utc).isoformat(),'canonical_application_performed':True,'main_commit':main,'feature_commit':feature,'new_branch':git('branch','--show-current').decode().strip(),'owner_authorization_sha256':auth_sha,'approved_proposal_sha256':sha(proposal),'originals':s['journals'],'custody':custody,'canonical_result':{'entries':len(newrows),'bytes':len(newraw),'sha256':sha(newraw),'main_prefix_bytes':len(mainraw),'main_prefix_exact':True,'new_unsigned_registrations':len(mapping),'new_notes':1,'note_hash':note['hash']},'registrations':mapping,'claim_files':s['feature_claims'],'standing_inventory':standings,'keyring_sha256':sha(krraw),'signed_entries_unchanged':True,'old_feature_prefix_preserved':False,'old_feature_prefix_check_errors':old_prefix_errors,'old_feature_history_preservation':'Original commits remain reachable through the old feature merge parent; original journal snapshot byte-identical.','scientific_status_or_verified_standing_promoted':False,'checks_completed':['Both original chains valid','Current-main and reviewed-main bytes exact prefixes','19 claim record bytes and canonical subject digests unchanged','19 native unsigned registrations with exact original bodies','One native provenance note','Candidate chain and main prefix valid','Both original custody snapshots losslessly verified','Keyring and every signed entry unchanged','All19 native standings unchanged'],'pending_checks':['Native ledger verify --base on actual main','Regenerate four derived benchmark progress files','Merged-tree ledger/hygiene/artifact/required checks','Publish two-parent continuation without changing original branch/PR']}
write_json(C/'reconciliation.json',receipt);write_json(O/'application-result.json',receipt);print(json.dumps({'custody_directory':str(C),'canonical_entries':len(newrows),'registered_claims':len(mapping),'main_prefix_exact':True,'standings_unchanged':True,'canonical_sha256':sha(newraw),'custody_stored_bytes':sum(x['stored_bytes'] for x in custody)}))
