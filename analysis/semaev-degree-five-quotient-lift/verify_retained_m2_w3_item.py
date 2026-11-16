#!/usr/bin/env python3
"""Independent exact W3 rank for one fixed n50/n51 retained m2 panel item.

The equations come from the closed S3 formula and the named basis. The
Boolean closure uses Python integer rows. This is a source-only candidate for
a future bounded 16-item panel; it does not launch a panel by itself.
"""

import argparse
import hashlib
import json
from pathlib import Path

from verify_n50_poly03_d3_rank import close_degree_three, multiply


def generators(record):
    n, k = record['n'], record['k']
    if (n, k) not in ((50, 25), (51, 26)) or record['name'] not in {
            'fresh-n50-poly-03', 'fresh-n50-rand-00', 'fresh-n50-rand-01',
            'fresh-n50-rand-02', 'fresh-n50-rand-03', 'fresh-n50-rand-04',
            'fresh-n51-poly-00', 'fresh-n51-poly-01', 'fresh-n51-poly-02',
            'fresh-n51-poly-03', 'fresh-n51-poly-04', 'fresh-n51-rand-00',
            'fresh-n51-rand-01', 'fresh-n51-rand-02', 'fresh-n51-rand-03',
            'fresh-n51-rand-04'}:
        raise ValueError('record outside retained panel')
    basis = [int(x, 16) for x in record['V_basis_hex']]
    modulus = int(record['modulus_hex'], 16)
    z = int(record['z_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    if (len(basis) != k or len(set(basis)) != k or
            any(v == 0 or v >= 1 << n for v in basis) or
            modulus.bit_length() != n + 1 or z == 0 or z >= 1 << n):
        raise ValueError('invalid named field or basis')
    if record['basis'] not in ('poly', 'rand'):
        raise ValueError('unknown basis type')
    pivots = {}
    for value in basis:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
        else:
            raise ValueError('dependent basis')
    square = lambda v: multiply(v, v, n, modulus)
    polys = [set() for _ in range(n)]

    def add_term(mask, coefficient):
        for bit in range(n):
            if coefficient >> bit & 1:
                polys[bit].add(mask)

    add_term(0, a6)
    for i, value in enumerate(basis):
        coefficient = square(multiply(z, value, n, modulus))
        add_term(1 << i, coefficient)
        add_term(1 << (k + i), coefficient)
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            product = multiply(x, y, n, modulus)
            add_term((1 << i) | (1 << (k + j)),
                     square(product) ^ multiply(z, product, n, modulus))
    return polys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--item-id', required=True)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    plan = json.loads(raw)
    if plan['id'] != 'n50n51-bounded-d4-concurrent-001':
        raise ValueError('wrong panel plan')
    matches = [item for item in plan['items'] if item['id'] == args.item_id]
    if len(matches) != 1:
        raise ValueError('item id is not unique in frozen panel')
    item = matches[0]
    polys = generators(item['record'])
    result = close_degree_three(polys, 2 * item['record']['k'])
    coefficients = b''.join(
        len(poly).to_bytes(4, 'little') +
        b''.join(mask.to_bytes(8, 'little') for mask in sorted(poly))
        for poly in polys)
    result.update(schema='semaev.retained-m2-w3-item/v1',
                  item_id=item['id'], named_input=item['record']['name'],
                  plan_sha256=hashlib.sha256(raw).hexdigest(),
                  seed_sha256=item['seed_sha256'],
                  expected_seed_codimension=item['seed_codimension'],
                  quotient_matches_seed=(result['quotient_dimension'] ==
                                         item['seed_codimension']),
                  equations=len(polys),
                  equation_terms=sum(map(len, polys)),
                  equation_masks_sha256=hashlib.sha256(coefficients).hexdigest())
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
