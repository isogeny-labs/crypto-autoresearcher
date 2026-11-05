#!/usr/bin/env python3
"""Export independently descended affine-sliced generators for a native map checker."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from check_trace_slice_certificate import trace_slice

MAGIC = b'SLCGEN01'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--expect-plan-sha256', required=True)
    parser.add_argument('--expect-descent-source-sha256', required=True)
    parser.add_argument('--variable', type=int, required=True)
    parser.add_argument('--affine-combination-mask', type=lambda s: int(s, 0))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sha(args.plan) != args.expect_plan_sha256:
        raise ValueError('plan SHA-256 mismatch')
    descent = Path(__file__).resolve().parents[1] / 'semaev-m2-last-fall-degree/verify/cert_check.py'
    if sha(descent) != args.expect_descent_source_sha256:
        raise ValueError('independent descent source SHA-256 mismatch')
    record = json.loads(args.plan.read_text())['record']
    nvars, polys, affine = trace_slice(record, args.variable, args.affine_combination_mask)
    if not (1 <= nvars <= 62 and 1 <= len(polys) <= 100000):
        raise ValueError('invalid generator dimensions')
    with args.out.open('xb') as out:
        out.write(MAGIC)
        out.write(struct.pack('<QQ', nvars, len(polys)))
        terms = 0
        for poly in polys:
            masks = sorted(poly)
            if any(m >= 1 << nvars for m in masks):
                raise ValueError('generator monomial exceeds sliced variables')
            out.write(struct.pack('<Q', len(masks)))
            for mask in masks:
                out.write(struct.pack('<Q', mask))
            terms += len(masks)
    print(json.dumps({'schema': 'semaev.sliced-generators/v1',
                      'variables': nvars, 'generators': len(polys), 'terms': terms,
                      'eliminated_variable': args.variable,
                      'affine_terms': affine,
                      'affine_combination_mask': (hex(args.affine_combination_mask)
                                                  if args.affine_combination_mask is not None else 'trace'),
                      'plan_sha256': args.expect_plan_sha256,
                      'descent_source_sha256': args.expect_descent_source_sha256,
                      'output_sha256': sha(args.out), 'output_bytes': args.out.stat().st_size},
                     sort_keys=True))


if __name__ == '__main__':
    main()
