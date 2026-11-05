#!/usr/bin/env python3
"""J3: Git-bound receipt consistency and hostile-receipt controls; no Lean build."""
import copy
import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = Path(sys.argv[1] if len(sys.argv) > 1 else '/var/tmp/autoresearcher-odd-torsion-review-20261103')
BINDING = 'docs/reports/2026-11-03-odd-torsion-review/input-bindings.json'
RECEIPT = ROOT/'raw/run-41494797344/scoped-odd-torsion-translation.json'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)
def blob(rev, path):
    return git('show', f'{rev}:{path}')
def sha(data):
    return hashlib.sha256(data).hexdigest()
def paths(rev, path):
    return git('ls-tree', '-r', '--name-only', rev, path).decode().splitlines()
bindings = json.loads(blob('b806841cef6ad73e80c5d49ca9a51845e5cf2eb6', BINDING))
receipt = json.loads(RECEIPT.read_bytes())
rev = receipt['provenance']['source_commit']
workspace = receipt['task']['workspace']
def workspace_map(revision):
    files = paths(revision, workspace)
    return {p[len(workspace)+1:]: sha(blob(revision,p)) for p in files
            if Path(p).suffix == '.lean' or Path(p).name in {'lakefile.toml','lean-toolchain','lake-manifest.json'}}
def verifier_map(revision):
    return {p:sha(blob(revision,p)) for p in paths(revision,'orchestration/formal')
            if Path(p).parent.as_posix() == 'orchestration/formal' and p.endswith('.py')}
checks = {'receipt_sha256': sha(RECEIPT.read_bytes()),
          'bound_receipt_matches': sha(RECEIPT.read_bytes()) == bindings['prior_named_receipt']['sha256'],
          'archived_revision': rev, 'input_revision': bindings['source_commit'],
          'theorem': receipt['task']['theorem_name'], 'source_bindings':{}, 'revision_maps':{}}
for name in ['source_note','target','theorem']:
    entry = bindings[name]
    checks['source_bindings'][name] = {r:sha(blob(r,entry['path'])) == entry['sha256']
                                      for r in [rev,bindings['source_commit'],'b806841cef6ad73e80c5d49ca9a51845e5cf2eb6']}
for r in [rev,bindings['source_commit'],'b806841cef6ad73e80c5d49ca9a51845e5cf2eb6']:
    wm,vm = workspace_map(r),verifier_map(r)
    checks['revision_maps'][r] = {
        'workspace_count':len(wm), 'workspace_exact':wm == receipt['provenance']['workspace_inputs'],
        'verifier_count':len(vm), 'verifier_exact':vm == receipt['provenance']['verifier_inputs'],
        'verifier_changed':sorted(k for k in set(vm)|set(receipt['provenance']['verifier_inputs'])
                                  if vm.get(k)!=receipt['provenance']['verifier_inputs'].get(k))}

# Read only the archived checker and the source files in the receipt. Execute its
# consistency function against an isolated snapshot; this does not execute Lean.
snapshot = ROOT/'raw/archived-input-snapshot'
snapshot.mkdir(exist_ok=True)
for p in [*paths(rev,workspace),*receipt['provenance']['verifier_inputs'],bindings['target']['path'],bindings['source_note']['path']]:
    q=snapshot/p; q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes(blob(rev,p))
checker_path=snapshot/'orchestration/formal/receipts.py'
module=types.ModuleType('j3_archived_receipts'); module.__file__=str(checker_path)
sys.modules[module.__name__]=module
exec(compile(checker_path.read_bytes(),str(checker_path),'exec'),module.__dict__)
Task=dataclasses.make_dataclass('Task',[(k,object) for k in receipt['task']])
task=Task(**receipt['task'])
def errors(data):
    return module.receipt_errors(data,repo=snapshot,spec=snapshot/bindings['target']['path'],task=task)
checks['archived_checker_baseline_errors']=errors(receipt)
mutants={}
def mutant(name,modify):
    m=copy.deepcopy(receipt);modify(m);mutants[name]=errors(m)
mutant('wrong_named_result',lambda x:x['verification'].update(theorem_name='Wrong.theorem'))
mutant('false_build',lambda x:x['verification'].update(build_passed=False))
mutant('false_audit',lambda x:x['verification'].update(axiom_audit_passed=False))
mutant('forbidden_construct',lambda x:x['verification'].update(forbidden_constructs=['sorry']))
mutant('empty_audit',lambda x:x.update(audit_log=''))
mutant('empty_build',lambda x:x.update(build_log=''))
mutant('stale_theorem',lambda x:x['provenance'].update(theorem_sha256='0'*64))
mutant('missing_workspace_input',lambda x:x['provenance']['workspace_inputs'].pop('AxiomAudit.lean'))
mutant('missing_verifier_input',lambda x:x['provenance']['verifier_inputs'].pop('orchestration/formal/lean_worker.py'))
mutant('fake_Lean_version',lambda x:x['provenance'].update(lean_version='Lean (version 0.0.0, fake)'))
mutant('contradictory_audit_error',lambda x:x.update(audit_log=x['audit_log']+'\nerror: fake audit failure\n'))
checks['mutation_controls']=mutants
checks['all_mutation_controls_rejected']=all(mutants.values())
checks['fabrication_boundary']='Consistent fabricated logs and hashes cannot be authenticated by receipt_errors; hosted provenance is separate; no independent kernel recheck performed.'
checks['manifest']=json.loads(blob(rev,workspace+'/lake-manifest.json'))
checks['lean_toolchain']=blob(rev,workspace+'/lean-toolchain').decode().strip()
xml=ROOT/'raw/lean-controls/lean-controls.xml'
if xml.exists():
    tree=ET.parse(xml); suites=list(tree.getroot().iter('testsuite'))
    checks['hosted_controls']=[s.attrib for s in suites]
    checks['hosted_live_control_names']=[c.attrib for c in tree.getroot().iter('testcase')
            if 'lean_live' in c.attrib.get('classname','')]
checks['local_build_executed']=False
checks['independent_kernel_recheck_executed']=False
assert checks['bound_receipt_matches']
assert all(all(v.values()) for v in checks['source_bindings'].values())
assert checks['revision_maps'][rev]['workspace_exact']
assert checks['revision_maps'][rev]['verifier_exact']
assert not checks['archived_checker_baseline_errors']
assert checks['all_mutation_controls_rejected']
(ROOT/'raw/checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
