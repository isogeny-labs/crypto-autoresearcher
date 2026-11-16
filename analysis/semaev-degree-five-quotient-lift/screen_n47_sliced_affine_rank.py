#!/usr/bin/env python3
"""Exact quadratic-kernel and affine-rank screen of the checked n47 slice."""
import argparse
import hashlib
import json
from pathlib import Path

from check_n47_sliced_generators import read_export


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def screen(path, expected_sha256):
    if digest(path) != expected_sha256:
        raise ValueError('sliced-generator digest mismatch')
    variables, polys = read_export(path)
    quadratic_monomials = sorted({m for poly in polys for m in poly
                                  if bin(m).count('1') == 2})
    quadratic_column = {m: i for i, m in enumerate(quadratic_monomials)}
    pivots = {}
    dependencies = []
    for i, poly in enumerate(polys):
        value = sum(1 << quadratic_column[m] for m in poly
                    if bin(m).count('1') == 2)
        combination = 1 << i
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit][0]
                combination ^= pivots[bit][1]
            else:
                pivots[bit] = (value, combination)
                break
        else:
            dependencies.append(combination)
    affine_rows = []
    for combination in dependencies:
        poly = set()
        for i, source in enumerate(polys):
            if combination >> i & 1:
                poly.symmetric_difference_update(source)
        if any(bin(m).count('1') > 1 for m in poly):
            raise ValueError('quadratic dependency did not cancel')
        affine_rows.append(sum(1 if m == 0 else 1 << m.bit_length() for m in poly))
    result = {
        'schema': 'semaev.n47-sliced-affine-screen/v1',
        'generator_sha256': expected_sha256,
        'variables': variables,
        'generators': len(polys),
        'quadratic_monomials_present': len(quadratic_monomials),
        'quadratic_rank': len(pivots),
        'quadratic_dependency_masks': [hex(mask) for mask in dependencies],
        'affine_rank': rank(affine_rows),
        'affine_linear_rank': rank([row >> 1 for row in affine_rows]),
        'constant_in_generator_span': rank(affine_rows) > rank([row >> 1 for row in affine_rows]),
    }
    if result['variables'] != 47 or result['generators'] != 47:
        raise ValueError('wrong named slice')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generators', type=Path)
    parser.add_argument('--expect-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(screen(args.generators, args.expect_sha256), sort_keys=True))


if __name__ == '__main__':
    main()
