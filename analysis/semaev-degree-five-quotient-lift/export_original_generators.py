#!/usr/bin/env python3
"""Export original Semaev Boolean equations from the independent descent."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    parser.add_argument('--descent-source', type=Path, required=True)
    parser.add_argument('--descent-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sha(args.plan) != args.plan_sha256 or sha(args.descent_source) != args.descent_sha256:
        raise ValueError('plan or independent descent source SHA-256 mismatch')
    record = json.loads(args.plan.read_text())['record']
    spec = importlib.util.spec_from_file_location('independent_semaev_descent', args.descent_source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    nvars, polys = module.descend(
        record['n'], int(record['modulus_hex'], 16), record['a2'],
        int(record['a6_hex'], 16), int(record['z_hex'], 16),
        [int(v, 16) for v in record['V_basis_hex']])
    if nvars != 2 * record['k'] or len(polys) != record['n']:
        raise ValueError('unexpected original system dimensions')
    total = 0
    with args.out.open('xb') as out:
        out.write(b'SLCGEN01' + struct.pack('<QQ', nvars, len(polys)))
        for poly in polys:
            masks = sorted(poly)
            if len(masks) != len(set(masks)) or any(m >= 1 << nvars for m in masks):
                raise ValueError('invalid descended polynomial')
            out.write(struct.pack('<Q', len(masks)))
            for mask in masks:
                out.write(struct.pack('<Q', mask))
            total += len(masks)
    print(json.dumps({'schema': 'semaev.original-generators/v1',
                      'variables': nvars, 'generators': len(polys),
                      'terms': total, 'plan_sha256': args.plan_sha256,
                      'descent_source_sha256': args.descent_sha256,
                      'output_sha256': sha(args.out),
                      'output_bytes': args.out.stat().st_size}, sort_keys=True))


if __name__ == '__main__':
    main()
