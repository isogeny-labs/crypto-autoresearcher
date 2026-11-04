"""Adapt the sealed J1 attestation shape to the existing independence checker.

The original remains unchanged. The assertion below is derived from its
explicit blind_compliance fields; this script does not supply reviewer evidence.
"""
from pathlib import Path
import hashlib
import yaml

root = Path(__file__).parent
source = root / 'reviews/TASK-20261103-a1d701/review_attestation.yaml'
target = source.with_name('review_attestation_checker_wrapper.yaml')
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '5a10850e5c1932eff96410b37cadd77be80855a26caa40dbb7f41f392693f961'
a = yaml.safe_load(raw)
b = a['blind_compliance']
assert b['statement_only_derivation'] is True
assert all(b[x] is False for x in (
    'read_producer_source_note', 'read_producer_proof', 'read_lean_code',
    'read_machine_receipts', 'read_plan_attack_details',
    'read_sibling_review_outputs'))
a['sources_read'] = [s['path'] for s in a['sources_read']]
a['blind_from_respected'] = True
target.write_text(yaml.safe_dump({'review_attestation': a}, sort_keys=False))
print(target, hashlib.sha256(target.read_bytes()).hexdigest())
