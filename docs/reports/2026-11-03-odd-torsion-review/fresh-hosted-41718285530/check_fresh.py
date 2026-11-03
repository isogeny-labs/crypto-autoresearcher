"""Recheck exact fresh named receipt against sealed odd-torsion J3 inputs."""
from pathlib import Path
import hashlib
import json

here = Path(__file__).parent
root = here.parent
old = root / 'reviews/TASK-20261103-a1d703/raw/run-41494797344/scoped-odd-torsion-translation.json'
new = here / 'scoped-odd-torsion-translation.json'
metadata = json.loads((here / 'github-metadata.json').read_text())
a = json.loads(old.read_text())
b = json.loads(new.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = {
 'new_receipt_sha': sha(new) == '5246d01c4a35fea1896f6b40a182deef1859171b4916abc5256d899aacedb45e',
 'old_receipt_sha': sha(old) == '63419f85fb756ca00a9772fb5c7454a605aed73f53b1fad2b355de3c7ba15403',
 'task_identity': b['task'] == a['task'],
 'named_theorem': b['verification']['theorem_name'] == 'ScopedObstructions.AdditiveModel.odd_translation_outside_kernel',
 'machine_status': b['verification']['status'] == 'machine_verified',
 'build': b['verification']['build_passed'] is True and bool(b['build_log']),
 'axiom_audit': b['verification']['axiom_audit_passed'] is True and 'zero-axiom audit passed: ScopedObstructions.AdditiveModel.odd_translation_outside_kernel' in b['audit_log'],
 'forbidden_empty': b['verification']['forbidden_constructs'] == [],
 'no_infrastructure_failure': b['infrastructure_failure'] is None,
 'target_sha': b['provenance']['task_spec_sha256'] == '1913803fed7b509e7755a51d9d56b8bd085fdc41964af4dc1d572aeac3bc9de7',
 'theorem_sha': b['provenance']['theorem_sha256'] == '68eb719cc0c34018475a73e00b22a623a8937f66f471be407dc4015c51020e8b',
 'workspace_map': b['provenance']['workspace_inputs'] == a['provenance']['workspace_inputs'] and len(b['provenance']['workspace_inputs']) == 6,
 'verifier_map': b['provenance']['verifier_inputs'] == a['provenance']['verifier_inputs'] and len(b['provenance']['verifier_inputs']) == 10,
 'toolchain_manifest_hashes': all(b['provenance'][k] == a['provenance'][k] for k in ('lean_toolchain_sha256','lake_manifest_sha256')),
 'pin_files_equal': (here/'dependency-pins-before.json').read_bytes() == (here/'dependency-pins-after.json').read_bytes(),
 'run_success': metadata['run']['id'] == 41718285530 and metadata['run']['status'] == 'completed' and metadata['run']['conclusion'] == 'success',
 'head_parent': metadata['run']['head_sha'] in metadata['checkout_commit']['parents'],
 'checkout_identity': b['provenance']['source_commit'] == metadata['checkout_commit']['sha'],
 'artifact_identity': metadata['artifact']['id'] == 13272842471 and metadata['artifact']['name'] == 'formal-verification-receipts' and metadata['artifact']['expired'] is False,
}
print(json.dumps({'checks': checks, 'passed': sum(checks.values()), 'total': len(checks)}, indent=2, sort_keys=True))
assert all(checks.values()), 'fresh hosted receipt check failed'
