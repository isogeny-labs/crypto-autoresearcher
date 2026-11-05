#!/usr/bin/env python3
"""Read-only, pinned J2 source/type checks; writes beside this script."""
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTO = Path('/var/tmp/autoresearcher-stark-proof-review-20261103')
CRYPTO = Path('/home/ec2-user/crypto')
INPUT = AUTO / 'docs/reports/2026-11-03-stark-affine-proof-review'
HEAD = '01df8d319edad2b28395167eed86581e6e54b302'
OLD = 'd4f1279102709518247f5a7d1926de354fe5929a'
RUST = '8ce2800fbe3d265027e2341ec193ad69b946a8bd'
MOD = 'formal/CryptoResearch/Stark/AffineTransition.lean'
RUST_PATH = 'src/zk/stark_v2.rs'
NAMES = ['recover_coefficients', 'coefficients_eq_of_probes',
         'three_probe_extensionality', 'multiplication_not_affine',
         'two_probes_insufficient', 'zero_ring_product_control',
         'multiplication_not_affine_on_four_probes']

def show(repo, rev, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{rev}:{path}'])

def sha(data):
    return hashlib.sha256(data).hexdigest()

def declaration(src, name):
    match = re.search(r'(?ms)^theorem ' + re.escape(name) + r'\b.*?(?=^/--|^set_option|\Z)', src)
    if not match:
        raise ValueError(f'missing declaration {name}')
    return match.group().rstrip()

binding = json.loads((INPUT / 'input-bindings.json').read_text())
current = show(AUTO, HEAD, MOD)
old = show(AUTO, OLD, MOD)
rust = show(CRYPTO, RUST, RUST_PATH)
current_text = current.decode()
old_text = old.decode()
checks = {
    'current_module_matches_binding': sha(current) == binding['tracked_sha256'][MOD],
    'rust_blob_matches_binding': subprocess.check_output(
        ['git', '-C', str(CRYPTO), 'rev-parse', f'{RUST}:{RUST_PATH}']).decode().strip()
        == binding['rust_source_blob'],
    'rust_sha256_matches_inputs_v2': sha(rust) ==
        json.loads(show(AUTO, HEAD, 'research/stark-affine-proof-20261029/inputs-v2.json'))['crypto_source']['sha256'],
    'seven_declarations_present': all(re.search(r'^theorem ' + n + r'\b', current_text, re.M) for n in NAMES),
    'old_six_declarations_byte_equal': all(
        declaration(current_text, n) == declaration(old_text, n) for n in NAMES[:6]),
    'new_seventh_absent_in_prior_sealed_scope': not re.search(
        r'^theorem multiplication_not_affine_on_four_probes\b', old_text, re.M),
}
for path, expected in binding['tracked_sha256'].items():
    checks['bound_file_' + path] = sha(show(AUTO, HEAD, path)) == expected

artifact_path = INPUT / 'hosted-artifact/stark-affine-probes.json.gz'
checks['artifact_compressed_sha256'] = sha(artifact_path.read_bytes()) == binding['archived_sha256']['stark-affine-probes.json.gz']
artifact = json.load(gzip.open(artifact_path, 'rt'))
log = artifact['build_log']
first = log.index('info: CryptoResearch/Stark/AffineTransition.lean:87:0:')
last = log.index("info: CryptoResearch/Stark/AffineTransition.lean:113:0:", first)
end = log.index('\n', last)
excerpt = log[first:end] + '\n'
(HERE / 'raw-type-and-control-prints.txt').write_text(excerpt)
checks['seven_elaborated_type_prints_present'] = all(
    excerpt.count('@' + n + '.{') == 1 for n in NAMES if n != 'zero_ring_product_control') and \
    excerpt.count('zero_ring_product_control : ∀') == 1
checks['seven_axiom_prints_present'] = all(
    excerpt.count("'CryptoResearch.Stark.AffineTransition." + n + "' depends on axioms:") == 1
    for n in NAMES)
checks['two_zero_ring_diagnostics_nontrivial'] = excerpt.count(
    'failed to synthesize instance of type class\n  Nontrivial.') == 2

seventh_start = excerpt.index('@multiplication_not_affine_on_four_probes.')
seventh_end = excerpt.index('info: CryptoResearch/Stark/AffineTransition.lean:99:3:', seventh_start)
seventh = excerpt[seventh_start:seventh_end]
checks['seventh_binders_commring_nontrivial_abc'] = bool(re.search(
    r'∀ \{R : Type u_2\} \[inst : CommRing\.\{u_2\} R\] \[Nontrivial\.\{u_2\} R\]\s+\(a b c : R\),\s+Not\s+\(And', seventh))
checks['seventh_four_equality_conjunction'] = seventh.count('(@Eq.{u_2 + 1} R') == 4 and seventh.count('(@evaluate.{u_2} R inst a b c') == 4

record = {
    'schema': 'stark_affine_j2_raw_checks/v1',
    'task_id': 'TASK-20261103-5c964f',
    'source_commit': HEAD,
    'prior_sealed_j2_scope_commit': OLD,
    'rust_commit': RUST,
    'hashes': {
        'current_module_sha256': sha(current),
        'old_module_sha256': sha(old),
        'rust_source_sha256': sha(rust),
        'hosted_artifact_gzip_sha256': sha(artifact_path.read_bytes()),
        'raw_type_and_control_prints_sha256': sha(excerpt.encode()),
    },
    'checks': checks,
    'all_checks_pass': all(checks.values()),
    'note': 'Receipt text is compared as a supplied input; this check does not authenticate its execution or independently run Lean.'
}
(HERE / 'raw-checks.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
print(json.dumps({'all_checks_pass': record['all_checks_pass'], 'failed': [k for k,v in checks.items() if not v], 'hashes': record['hashes']}, indent=2))
