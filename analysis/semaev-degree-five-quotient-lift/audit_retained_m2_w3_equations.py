#!/usr/bin/env python3
"""Compare direct S3 coefficients with independent Möbius descent for 16 inputs."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from verify_retained_m2_w3_item import generators


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--checker', type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    if plan['id'] != 'n50n51-bounded-d4-concurrent-001' or len(plan['items']) != 16:
        raise ValueError('not the fixed 16-item retained panel')
    spec = importlib.util.spec_from_file_location('independent_cert_checker', args.checker)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    rows = []
    seen = set()
    for item in plan['items']:
        record = item['record']
        if item['id'] in seen:
            raise ValueError('duplicate panel id')
        seen.add(item['id'])
        direct = generators(record)
        variables, interpolated = checker.descend(
            record['n'], int(record['modulus_hex'], 16), record['a2'],
            int(record['a6_hex'], 16), int(record['z_hex'], 16),
            [int(x, 16) for x in record['V_basis_hex']])
        if variables != 2 * record['k'] or len(direct) != record['n']:
            raise ValueError('wrong descended dimensions')
        if any(a != set(b) for a, b in zip(direct, interpolated)):
            raise ValueError('equation mask mismatch: ' + item['id'])
        encoded = b''.join(
            len(poly).to_bytes(4, 'little') +
            b''.join(mask.to_bytes(8, 'little') for mask in sorted(poly))
            for poly in direct)
        rows.append({'item_id': item['id'], 'named_input': record['name'],
                     'variables': variables, 'equations': len(direct),
                     'terms': sum(map(len, direct)),
                     'equation_masks_sha256': hashlib.sha256(encoded).hexdigest(),
                     'all_masks_match': True})
    print(json.dumps({'schema': 'semaev.retained-m2-w3-equation-audit/v1',
                      'plan_sha256': digest(args.plan),
                      'checker_sha256': digest(args.checker),
                      'items_checked': len(rows), 'rows': rows}, sort_keys=True))


if __name__ == '__main__':
    main()
