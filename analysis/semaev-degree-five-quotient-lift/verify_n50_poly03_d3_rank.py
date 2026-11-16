#!/usr/bin/env python3
"""Independent exact W3 rank for the fixed n50 polynomial03 Semaev input.

Construct the binary quadratic equations directly from the closed S3
formula, then close their span under all allowed Boolean variable products.
This uses Python integers and no quotient-lift, certificate, or native
closure code. It does not count solutions.
"""

import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path


def multiply(a, b, n, modulus):
    product = 0
    while b:
        if b & 1:
            product ^= a
        a <<= 1
        b >>= 1
    for bit in range(product.bit_length() - 1, n - 1, -1):
        if product >> bit & 1:
            product ^= modulus << (bit - n)
    return product


def generators(record):
    if (record['name'] != 'fresh-n50-poly-03' or record['n'] != 50 or
            record['k'] != 25 or record['basis'] != 'poly' or
            record['V_basis_hex'] != [format(1 << i, 'x') for i in range(25)]):
        raise ValueError('not the fixed named input')
    n = record['n']
    modulus = int(record['modulus_hex'], 16)
    z = int(record['z_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    if modulus.bit_length() != n + 1 or z == 0:
        raise ValueError('invalid field parameters')
    basis = [1 << i for i in range(25)]
    square = lambda v: multiply(v, v, n, modulus)
    polys = [set() for _ in range(n)]

    def add_term(mask, coefficient):
        for bit in range(n):
            if coefficient >> bit & 1:
                polys[bit].add(mask)

    # S3(X,Y,z) = a6 + (zX)^2 + (zY)^2 + (XY)^2 + zXY.
    # Squaring is F2-linear. Thus there are only constant, linear, and
    # cross-variable quadratic coefficients to extract.
    add_term(0, a6)
    for i, value in enumerate(basis):
        coefficient = square(multiply(z, value, n, modulus))
        add_term(1 << i, coefficient)
        add_term(1 << (25 + i), coefficient)
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            product = multiply(x, y, n, modulus)
            coefficient = square(product) ^ multiply(z, product, n, modulus)
            add_term((1 << i) | (1 << (25 + j)), coefficient)
    return polys


def close_degree_three(polys, variables):
    order = [0]
    for degree in range(1, 4):
        for positions in combinations(range(variables), degree):
            order.append(sum(1 << i for i in positions))
    position = {mask: index for index, mask in enumerate(order)}
    low_limit = 1 + variables + variables * (variables - 1) // 2
    if len(order) != low_limit + variables * (variables - 1) * (variables - 2) // 6:
        raise AssertionError('wrong monomial universe')
    pivots = {}
    low_queue = []

    def insert(row):
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                if bit < low_limit:
                    low_queue.append(bit)
                return
            row ^= pivots[bit]

    def multiply_row(row, variable):
        bit = 1 << variable
        result = 0
        while row:
            term = row & -row
            index = term.bit_length() - 1
            row ^= term
            result ^= 1 << position[order[index] | bit]
        return result

    for poly in polys:
        row = 0
        for mask in poly:
            row ^= 1 << position[mask]
        insert(row)
        for variable in range(variables):
            insert(multiply_row(row, variable))

    processed = set()
    while low_queue:
        bit = low_queue.pop()
        if bit in processed:
            continue
        processed.add(bit)
        row = pivots[bit]
        for variable in range(variables):
            insert(multiply_row(row, variable))

    constant = 1 << position[0]
    while constant:
        bit = constant.bit_length() - 1
        if bit not in pivots:
            break
        constant ^= pivots[bit]
    return {'columns': len(order), 'rank': len(pivots),
            'quotient_dimension': len(order) - len(pivots),
            'low_pivot_count': len(processed),
            'contains_one': constant == 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    plan = json.loads(raw)
    polys = generators(plan['record'])
    result = close_degree_three(polys, 50)
    coefficients = b''.join(
        len(poly).to_bytes(4, 'little') +
        b''.join(mask.to_bytes(8, 'little') for mask in sorted(poly))
        for poly in polys)
    result.update(schema='semaev.independent-n50-poly03-w3/v1',
                  named_input='fresh-n50-poly-03',
                  plan_sha256=hashlib.sha256(raw).hexdigest(),
                  equations=len(polys),
                  equation_terms=sum(map(len, polys)),
                  equation_masks_sha256=hashlib.sha256(coefficients).hexdigest())
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
