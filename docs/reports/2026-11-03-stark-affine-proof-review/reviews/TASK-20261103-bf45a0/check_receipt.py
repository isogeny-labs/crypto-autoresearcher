#!/usr/bin/env python3
"""Read-only checks of a downloaded hosted STARK affine receipt."""
import hashlib
import json
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path('/var/tmp/autoresearcher-stark-proof-review-20261103')
SOURCE = '01df8d319edad2b28395167eed86581e6e54b302'
CHECKOUT = 'd3ce7758698c822e16feef174ecdac53c41e4568'
HEAD = '70cdc0c5a12b49b7a0ef1bb3590c6e8d99a4d311'
receipt_bytes = (HERE / 'hosted/stark-affine-probes.json').read_bytes()
receipt = json.loads(receipt_bytes)
bindings = json.loads((REPO / 'docs/reports/2026-11-03-stark-affine-proof-review/input-bindings.json').read_text())
before = json.loads((HERE / 'hosted/dependency-pins-before.json').read_text())
after = json.loads((HERE / 'hosted/dependency-pins-after.json').read_text())

def sha(b): return hashlib.sha256(b).hexdigest()
def git_bytes(commit, path):
    return subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=REPO,
                          check=True, stdout=subprocess.PIPE).stdout
def gh_json(path):
    return json.loads(subprocess.run(['gh', 'api', path], check=True,
                                     stdout=subprocess.PIPE).stdout)

out = {'checks': {}, 'detail': {}}
def check(name, value, detail=None):
    out['checks'][name] = bool(value)
    if detail is not None: out['detail'][name] = detail

run = gh_json('repos/aburan28/crypto-autoresearcher/actions/runs/41698891260')
artifact = gh_json('repos/aburan28/crypto-autoresearcher/actions/artifacts/13264657224')
check('github_run_success_exact_head', run['status'] == 'completed' and run['conclusion'] == 'success' and run['head_sha'] == HEAD,
      {'head_sha':run['head_sha'], 'status':run['status'], 'conclusion':run['conclusion']})
check('artifact_bound_to_run_and_head', artifact['workflow_run']['id'] == run['id'] and artifact['workflow_run']['head_sha'] == HEAD and artifact['name'] == 'formal-verification-receipts' and not artifact['expired'])
parents = subprocess.run(['git','show','-s','--format=%P',CHECKOUT],cwd=REPO,check=True,stdout=subprocess.PIPE,text=True).stdout.split()
check('checkout_is_pr_merge_of_head', HEAD in parents, {'checkout_parents':parents})
check('receipt_sha256', sha(receipt_bytes) == bindings['hosted_receipt_uncompressed_sha256'], sha(receipt_bytes))
for name in ['dependency-pins-before.json','dependency-pins-after.json']:
    check(name + '_sha256', sha((HERE/'hosted'/name).read_bytes()) == bindings['archived_sha256'][name])
check('receipt_identity', receipt['task']['theorem_name'] == 'CryptoResearch.Stark.AffineTransition.three_probe_extensionality' and receipt['verification']['theorem_name'] == receipt['task']['theorem_name'] and receipt['task']['task_id'] == receipt['verification']['task_id'])
check('receipt_status', receipt['verification']['status'] == 'machine_verified' and receipt['verification']['build_passed'] and receipt['verification']['axiom_audit_passed'] and not receipt['verification']['forbidden_constructs'] and receipt['infrastructure_failure'] is None)
check('receipt_checkout', receipt['provenance']['source_commit'] == CHECKOUT and before['github_checkout_sha'] == CHECKOUT and after['github_checkout_sha'] == CHECKOUT)

for label, entries, prefix in [('workspace',receipt['provenance']['workspace_inputs'],'formal/'),('verifier',receipt['provenance']['verifier_inputs'],'')]:
    mismatches=[]
    for path, expected in entries.items():
        if label == 'workspace' and path == 'CryptoResearch.lean':
            module_paths = [p for p in entries if p.startswith('CryptoResearch/') and p.endswith('.lean')]
            module_names = sorted(p.removesuffix('.lean').replace('/','.') for p in module_paths)
            generated = ('/-\nGENERATED FILE -- do not edit, and do not commit.\n\n'
                         'Rebuild with `python3 tools/rebuild_formal_root.py`.  It lists every module\n'
                         'under CryptoResearch/ so that `lake build` compiles them and AxiomAudit.lean can\n'
                         'see their theorems.\n-/\n\n' +
                         ''.join(f'import {m}\n' for m in module_names)).encode()
            actual=sha(generated)
        else:
            try: actual=sha(git_bytes(CHECKOUT,prefix+path))
            except subprocess.CalledProcessError: actual='MISSING'
        if actual != expected: mismatches.append({'path':path,'expected':expected,'actual':actual})
    check(label+'_input_map_at_checkout',not mismatches,{'count':len(entries),'mismatches':mismatches})

tracked=[]
for path, expected in bindings['tracked_sha256'].items():
    try: actual=sha(git_bytes(SOURCE,path))
    except subprocess.CalledProcessError: actual='MISSING'
    if actual != expected: tracked.append({'path':path,'expected':expected,'actual':actual})
check('bound_tracked_sources_at_source_commit',not tracked,{'count':len(bindings['tracked_sha256']),'mismatches':tracked})
target='formal/CryptoResearch/Stark/AffineTransition.lean'
spec='formal/targets/stark-affine-probes.yaml'
for path, key in [(target,'theorem_sha256'),(spec,'task_spec_sha256')]:
    hashes={c:sha(git_bytes(c,path)) for c in [SOURCE,CHECKOUT,HEAD]}
    check(key+'_at_all_revisions',len(set(hashes.values()))==1 and hashes[SOURCE]==receipt['provenance'][key],hashes)

manifest=json.loads(git_bytes(CHECKOUT,'formal/lake-manifest.json'))
manifest_pins={p['name']:p['rev'] for p in manifest['packages']}
pin_rows=before['dependencies']
check('pre_post_pins_identical',before==after)
check('ten_pins_match_manifest_and_installed',len(pin_rows)==10 and set(manifest_pins)=={r['name'] for r in pin_rows} and all(r['expected_revision']==r['installed_revision']==manifest_pins[r['name']] and r['clean_sources'] for r in pin_rows),{'count':len(pin_rows),'names':[r['name'] for r in pin_rows]})
check('pin_manifest_hash',before['manifest_sha256']==after['manifest_sha256']==sha(git_bytes(CHECKOUT,'formal/lake-manifest.json')))
check('pin_checker_hash',before['checker_sha256']==after['checker_sha256']==sha(git_bytes(CHECKOUT,'tools/check_lean_dependency_pins.py')))

source=git_bytes(CHECKOUT,target).decode()
build=receipt['build_log']
audit=receipt['audit_log']
names=['recover_coefficients','coefficients_eq_of_probes','three_probe_extensionality','multiplication_not_affine','two_probes_insufficient','zero_ring_product_control','multiplication_not_affine_on_four_probes']
types={n:len(re.findall(r'info: CryptoResearch/Stark/AffineTransition\.lean:\d+:0: @?'+n+r'(?:\.\{[^\n]*)?\s*:',build)) for n in names}
axioms={n:re.findall(r"'CryptoResearch\.Stark\.AffineTransition\."+n+r"' depends on axioms: \[([^\]]+)\]",build) for n in names}
check('seven_elaborated_type_prints',all(v>=1 for v in types.values()),types)
check('seven_axiom_prints',all(v and all(a in ['propext','propext, Quot.sound.{u}'] for a in v) for v in axioms.values()),axioms)
check('two_zmod1_negative_controls',source.count('#check_failure')>=2 and len(re.findall(r'info: CryptoResearch/Stark/AffineTransition\.lean:(?:99|103):3: failed to synthesize instance of type class\s+Nontrivial\.\{0\} \(ZMod',build))>=2 and 'Build completed successfully' in build)
check('named_target_audit',receipt['verification']['theorem_name'] in audit and 'target axiom audit passed:' in audit and 'axiom audit: 1105 theorem(s), all standard axioms only' in audit)
check('explicit_no_binary_recheck',before['binary_or_independent_kernel_recheck'] is False and after['binary_or_independent_kernel_recheck'] is False)
out['all_consistency_checks_passed']=all(out['checks'].values())
(HERE/'raw_checks.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'all_consistency_checks_passed':out['all_consistency_checks_passed'],'failed':[k for k,v in out['checks'].items() if not v],'type_counts':types,'axioms':axioms},indent=2))
