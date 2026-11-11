#!/usr/bin/env python3
"""Independent exact W3 rank for the fixed n51 polynomial00 Semaev input."""

import argparse
import hashlib
import json
from pathlib import Path

from verify_n50_poly03_d3_rank import close_degree_three, multiply


def generators(record):
    if (record['name'] != 'fresh-n51-poly-00' or record['n'] != 51 or
            record['k'] != 26 or record['basis'] != 'poly' or
            record['V_basis_hex'] != [format(1 << i, 'x') for i in range(26)]):
        raise ValueError('not the fixed named input')
    n = 51
    modulus = int(record['modulus_hex'], 16)
    z = int(record['z_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    if modulus.bit_length() != n + 1 or z == 0:
        raise ValueError('invalid field parameters')
    basis = [1 << i for i in range(26)]
    square = lambda v: multiply(v, v, n, modulus)
    polys = [set() for _ in range(n)]

    def add_term(mask, coefficient):
        for bit in range(n):
            if coefficient >> bit & 1:
                polys[bit].add(mask)

    # Independent direct expansion of S3 at the named polynomial basis:
    # a6 + (zX)^2 + (zY)^2 + (XY)^2 + zXY.
    add_term(0, a6)
    for i, value in enumerate(basis):
        coefficient = square(multiply(z, value, n, modulus))
        add_term(1 << i, coefficient)
        add_term(1 << (26 + i), coefficient)
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            product = multiply(x, y, n, modulus)
            add_term((1 << i) | (1 << (26 + j)),
                     square(product) ^ multiply(z, product, n, modulus))
    return polys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    plan = json.loads(raw)
    polys = generators(plan['record'])
    result = close_degree_three(polys, 52)
    coefficients = b''.join(
        len(poly).to_bytes(4, 'little') +
        b''.join(mask.to_bytes(8, 'little') for mask in sorted(poly))
        for poly in polys)
    result.update(schema='semaev.independent-n51-poly00-w3/v1',
                  named_input='fresh-n51-poly-00',
                  plan_sha256=hashlib.sha256(raw).hexdigest(),
                  equations=len(polys),
                  equation_terms=sum(map(len, polys)),
                  equation_masks_sha256=hashlib.sha256(coefficients).hexdigest())
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
