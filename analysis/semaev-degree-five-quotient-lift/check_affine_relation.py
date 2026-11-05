#!/usr/bin/env python3
"""Verify a short affine equation certificate from independent Semaev descent."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def verify(certificate_path):
    root = Path(__file__).resolve().parents[2]
    certificate = json.loads(certificate_path.read_text())
    if certificate.get('schema') != 'semaev.affine-equation-certificate/v1':
        raise ValueError('wrong certificate schema')
    plan = root / certificate['plan']
    if not plan.resolve().is_relative_to(root.resolve()):
        raise ValueError('plan path escapes repository')
    if sha256(plan) != certificate['plan_sha256']:
        raise ValueError('named plan digest mismatch')
    source_dir = root / 'analysis/semaev-m2-last-fall-degree/verify'
    source = source_dir / 'cert_check.py'
    if sha256(source) != certificate['descent_source_sha256']:
        raise ValueError('independent descent digest mismatch')
    sys.path.insert(0, str(source_dir))
    from cert_check import descend
    record = json.loads(plan.read_text())['record']
    k = len(record['V_basis_hex'])
    n, polys = descend(record['n'], int(record['modulus_hex'], 16),
                       record['a2'], int(record['a6_hex'], 16),
                       int(record['z_hex'], 16),
                       [int(v, 16) for v in record['V_basis_hex']])
    if n != 2 * k or len(polys) != record['n']:
        raise ValueError('unexpected descended system dimensions')
    coefficient = int(certificate['combination_mask_hex'], 16)
    if not 0 < coefficient < (1 << len(polys)):
        raise ValueError('invalid equation combination')
    actual = set()
    for i, poly in enumerate(polys):
        if coefficient >> i & 1:
            actual.symmetric_difference_update(poly)
    pairs = certificate['pair_indices']
    if (not isinstance(pairs, list) or not pairs or
            pairs != sorted(set(pairs)) or any(type(j) is not int or not 0 <= j < k for j in pairs)):
        raise ValueError('invalid pair indices')
    expected = {1 << j for j in pairs} | {1 << (k + j) for j in pairs}
    if actual != expected:
        raise ValueError('equation combination differs from claimed affine relation')
    variable = certificate['eliminate_variable']
    if type(variable) is not int or variable not in [k + j for j in pairs]:
        raise ValueError('eliminated variable is not in relation')
    quadratic = sorted({m for poly in polys for m in poly if bin(m).count('1') == 2})
    positions = {m: i for i, m in enumerate(quadratic)}
    pivots = {}
    for poly in polys:
        row = sum(1 << positions[m] for m in poly if m in positions)
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return {
        'schema': 'semaev.affine-equation-check/v1',
        'status': 'valid_affine_relation',
        'certificate_sha256': sha256(certificate_path),
        'verifier_source_sha256': sha256(Path(__file__)),
        'plan_sha256': certificate['plan_sha256'],
        'descent_source_sha256': certificate['descent_source_sha256'],
        'field_degree': record['n'],
        'boolean_variables': n,
        'quadratic_rank': len(pivots),
        'combination_mask_hex': certificate['combination_mask_hex'],
        'pair_indices': pairs,
        'eliminated_variable': variable,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.certificate)
    except (OSError, KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
