from pathlib import Path
import copy,json,zipfile
from orchestration.formal.targets import task_from_spec
from orchestration.formal import targets,receipts
repo=Path('/var/tmp/semaev-certificate-fidelity-round2-20261109')
spec=repo/'formal/targets/semaev-decomposition-certificate.yaml'
with zipfile.ZipFile('/var/tmp/semaev-forced-run-42446577502.zip') as z:
    original=json.loads(z.read('semaev-decomposition-certificate.json'))
task=task_from_spec(original['task'])
targets.load_spec=lambda _p: {'source':'research/THM_SEMAEV_FALL1.md'}
rev='e5569428e5e53145f123f3aeb36de00591ad72b6'
# The worktree is sparse; use the archived receipt's full workspace map solely
# to isolate receipt field/log controls. The pinned Git bytes are checked separately.
receipts.workspace_inputs=lambda _w: original['provenance']['workspace_inputs']
def check(receipt):
    return receipts.receipt_errors(receipt,repo=repo,spec=spec,task=task,verifier_revision=rev)
results={}
results['baseline']=check(original)
r=copy.deepcopy(original)
r['verification']['theorem_name']='CryptoResearch.Semaev.wrongName'
results['wrong_name_verification_only']=check(r)
r=copy.deepcopy(original)
r['provenance']['theorem_sha256']='0'*64
results['changed_theorem_hash']=check(r)
r=copy.deepcopy(original)
r['provenance']['declared_source_sha256']='0'*64
results['changed_claim_source_hash']=check(r)
r=copy.deepcopy(original)
r['audit_log']='target axiom audit passed: CryptoResearch.Semaev.decidable_validDecomposition\naxiom audit: 1 theorem(s), all standard axioms only\n'
r['build_log']='synthetic build success text'
results['synthetic_self_consistent_logs']=check(r)
print(json.dumps(results,indent=2))
