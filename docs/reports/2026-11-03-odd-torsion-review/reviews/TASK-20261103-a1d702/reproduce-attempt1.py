#!/usr/bin/env python3
"""J2 source/type fidelity checks; direct Lean elaboration, no Lake build or network."""
from pathlib import Path
import hashlib, json, subprocess, sys
repo = Path('/var/tmp/autoresearcher-odd-torsion-review-20261103')
out = Path(__file__).resolve().parent
rev = 'b806841cef6ad73e80c5d49ca9a51845e5cf2eb6'

def git_bytes(path, revision=rev):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=repo)

def digest(b):
    return hashlib.sha256(b).hexdigest()

bindings_path = 'docs/reports/2026-11-03-odd-torsion-review/input-bindings.json'
bindings = json.loads(git_bytes(bindings_path))
checks = []
for key in ['source_note', 'target', 'theorem']:
    item = bindings[key]
    frozen = git_bytes(item['path'])
    producer = git_bytes(item['path'], bindings['source_commit'])
    local = (repo / item['path']).read_bytes()
    checks.append({'check': key, 'path': item['path'], 'expected': item['sha256'],
                   'frozen_sha256': digest(frozen), 'producer_sha256': digest(producer),
                   'working_sha256': digest(local),
                   'passed': digest(frozen) == digest(producer) == digest(local) == item['sha256']})
receipt_path = 'docs/reports/2026-10-31-hosted-formal-receipts/receipts/scoped-odd-torsion-translation.json'
receipt_bytes = git_bytes(receipt_path)
receipt = json.loads(receipt_bytes)
checks.append({'check': 'prior_named_receipt_digest', 'path': receipt_path,
               'expected': bindings['prior_named_receipt']['sha256'],
               'actual': digest(receipt_bytes),
               'passed': digest(receipt_bytes) == bindings['prior_named_receipt']['sha256']})
(out / 'prior-named-receipt.json').write_bytes(receipt_bytes)
(out / 'prior-printed-type.txt').write_text(receipt['audit_log'])
for field, path in [('lean_toolchain_sha256', 'lean-toolchain'),
                    ('lake_manifest_sha256', 'lake-manifest.json')]:
    actual = digest(git_bytes('formal/scoped-obstructions/' + path))
    checks.append({'check': field, 'actual': actual, 'expected': receipt['provenance'][field],
                   'passed': actual == receipt['provenance'][field]})
source = git_bytes(bindings['theorem']['path'])
(out / 'Torsion.lean').write_bytes(source)
commands = '''
#print ScopedObstructions.AdditiveModel
#check ScopedObstructions.AdditiveModel.odd_translation
#check ScopedObstructions.AdditiveModel.odd_translation_outside_kernel
#print axioms ScopedObstructions.AdditiveModel.odd_translation
#print axioms ScopedObstructions.AdditiveModel.odd_translation_outside_kernel
#print axioms ScopedObstructions.positive_control
#print axioms ScopedObstructions.even_scalar_control
example : (∃ k : Nat, 3 = k + k + 1) ∧
    ScopedObstructions.xorModel.multiple 3 false = ScopedObstructions.xorModel.zero ∧
    ScopedObstructions.xorModel.add true true = ScopedObstructions.xorModel.zero ∧
    true ≠ ScopedObstructions.xorModel.zero := by
  exact ⟨⟨1, rfl⟩, rfl, rfl, by decide⟩
example : ScopedObstructions.xorModel.multiple 3
    (ScopedObstructions.xorModel.add false false) = ScopedObstructions.xorModel.zero := rfl
'''
(out / 'TypeAudit.lean').write_bytes(source + commands.encode())
commands_log = []
for name, args in [('lean-version', ['lean', '+leanprover/lean4:v4.22.0', '--version']),
                   ('exact-source', ['lean', '+leanprover/lean4:v4.22.0', 'Torsion.lean']),
                   ('type-audit', ['lean', '+leanprover/lean4:v4.22.0', 'TypeAudit.lean'])]:
    result = subprocess.run(args, cwd=out, capture_output=True, timeout=45)
    (out / (name + '.stdout.txt')).write_bytes(result.stdout)
    (out / (name + '.stderr.txt')).write_bytes(result.stderr)
    commands_log.append({'name': name, 'argv': args, 'cwd': str(out), 'exit_code': result.returncode,
                         'stdout_sha256': digest(result.stdout), 'stderr_sha256': digest(result.stderr)})
    checks.append({'check': name, 'passed': result.returncode == 0})
checks.append({'check': 'source_snapshot_identity', 'actual': digest((out / 'Torsion.lean').read_bytes()),
               'expected': bindings['theorem']['sha256'],
               'passed': digest((out / 'Torsion.lean').read_bytes()) == bindings['theorem']['sha256']})
checks.append({'check': 'source_unchanged_after_check',
               'passed': digest((repo / bindings['theorem']['path']).read_bytes()) == bindings['theorem']['sha256']})
(out / 'commands.json').write_text(json.dumps(commands_log, indent=2) + '\n')
(out / 'checks.json').write_text(json.dumps({'schema': 'j2-source-type-checks/v1',
    'frozen_revision': rev, 'source_commit': bindings['source_commit'],
    'checks': checks, 'all_passed': all(x['passed'] for x in checks)}, indent=2) + '\n')
print(json.dumps({'all_passed': all(x['passed'] for x in checks), 'checks': len(checks)}, indent=2))
sys.exit(0 if all(x['passed'] for x in checks) else 1)
