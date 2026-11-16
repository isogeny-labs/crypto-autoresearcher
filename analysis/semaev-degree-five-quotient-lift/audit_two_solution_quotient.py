#!/usr/bin/env python3
"""Audit whether a retained two-coordinate D5 map is exactly point evaluation."""

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import struct


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def masks_in_native_order(n, degree):
    for d in range(degree, -1, -1):
        if d == 0:
            yield 0
            continue
        mask = (1 << d) - 1
        while mask < (1 << n):
            yield mask
            low = mask & -mask
            next_bit = mask + low
            mask = next_bit + (((next_bit ^ mask) // low) >> 2)


def input_generators(path, n):
    with path.open(encoding='ascii') as stream:
        header = stream.readline().split()
        if len(header) != 2 or int(header[0]) != n:
            raise ValueError('input system header differs from map')
        count = int(header[1])
        generators = []
        for line in stream:
            fields = line.split()
            if not fields:
                continue
            size = int(fields[0])
            terms = [int(term, 16) for term in fields[1:]]
            if len(terms) != size or any(term >= (1 << n) for term in terms):
                raise ValueError('invalid generator row')
            generators.append(terms)
        if len(generators) != count:
            raise ValueError('wrong number of generators')
    return generators


def field_product(a, b, modulus, degree):
    product = 0
    while b:
        if b & 1:
            product ^= a
        a <<= 1
        b >>= 1
    for bit in range(product.bit_length() - 1, degree - 1, -1):
        if (product >> bit) & 1:
            product ^= modulus << (bit - degree)
    return product


def check_named_field_equation(point, record, variables):
    degree = record['n']
    k = record['k']
    basis = [int(value, 16) for value in record['V_basis_hex']]
    modulus = int(record['modulus_hex'], 16)
    z = int(record['z_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    if (2 * k != variables or len(basis) != k or
            modulus.bit_length() != degree + 1 or
            any(value >= 1 << degree for value in basis + [z, a6])):
        raise ValueError('named field record disagrees with Boolean map')
    x = 0
    y = 0
    for i, value in enumerate(basis):
        if (point >> i) & 1:
            x ^= value
        if (point >> (k + i)) & 1:
            y ^= value
    multiply = lambda a, b: field_product(a, b, modulus, degree)
    xy = multiply(x, y)
    s = xy ^ multiply(x, z) ^ multiply(y, z)
    return multiply(s, s) ^ multiply(xy, z) ^ a6 == 0


def audit(map_path, system_path, instance_path):
    before = sha256(map_path)
    system_before = sha256(system_path)
    instance_before = sha256(instance_path)
    with map_path.open('rb') as stream, mmap.mmap(
            stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if len(data) < 32:
            raise ValueError('truncated map')
        n, degree, rows, q = struct.unpack_from('<4q', data, 0)
        if not (1 <= n <= 62 and degree == 5 and q == 2 and
                rows > n + 1 and len(data) == 32 + 16 * rows):
            raise ValueError('unexpected D5 map dimensions or length')
        row_start = 32 + 8 * rows
        def image(index):
            return struct.unpack_from('<Q', data, row_start + 8 * index)[0]
        one = image(rows - 1)
        variables = [image(rows - n - 1 + i) for i in range(n)]
        if not 0 < one < 4 or any(value >= 4 for value in variables):
            raise ValueError('invalid constant or variable image')
        separator = next((i for i, value in enumerate(variables)
                          if value not in (0, one)), None)
        if separator is None:
            raise ValueError('no variable separates the two coordinates')
        other = variables[separator]
        coefficients = {(a * one) ^ (b * other): (a, b)
                        for a in (0, 1) for b in (0, 1)}
        if len(coefficients) != 4:
            raise ValueError('constant and separator are dependent')
        first = sum(coefficients[value][0] << i
                    for i, value in enumerate(variables))
        second = sum((coefficients[value][0] ^ coefficients[value][1]) << i
                     for i, value in enumerate(variables))
        if first == second:
            raise ValueError('recovered assignments are equal')
        seen = 0
        for index, mask in enumerate(masks_in_native_order(n, degree)):
            if index >= rows:
                raise ValueError('extra expected monomial')
            actual_mask = struct.unpack_from('<Q', data, 32 + 8 * index)[0]
            if actual_mask != mask:
                raise ValueError(f'monomial order differs at row {index}')
            at_first = (mask & first) == mask
            at_second = (mask & second) == mask
            expected = (one if at_first else 0) ^ \
                       (other if at_first ^ at_second else 0)
            if image(index) != expected:
                raise ValueError(f'evaluation map differs at row {index}')
            seen += 1
        if seen != rows:
            raise ValueError('missing expected monomials')
    generators = input_generators(system_path, n)
    for index, terms in enumerate(generators):
        if any(sum((term & point) == term for term in terms) % 2
               for point in (first, second)):
            raise ValueError(f'recovered assignment fails generator {index}')
    records = json.loads(instance_path.read_text())
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError('expected one named field record')
    if not all(check_named_field_equation(point, records[0], n)
               for point in (first, second)):
        raise ValueError('recovered assignment fails named field equation')
    if (sha256(map_path) != before or sha256(system_path) != system_before or
            sha256(instance_path) != instance_before):
        raise ValueError('input changed during audit')
    return {'schema': 'semaev.two-solution-d5-evaluation-audit/v1',
            'map_path': str(map_path), 'map_sha256': before,
            'system_path': str(system_path), 'system_sha256': system_before,
            'instance_path': str(instance_path),
            'instance_sha256': instance_before,
            'variables': n, 'degree': degree, 'rows_checked': rows,
            'quotient_dimension': q, 'generator_rows_checked': len(generators),
            'constant_image': one, 'separator_variable': separator,
            'separator_image': other,
            'assignment_masks_hex': [hex(first), hex(second)],
            'all_map_rows_equal_two_point_evaluation': True,
            'both_assignments_satisfy_input_system': True,
            'both_assignments_satisfy_named_field_equation': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('map_path', type=Path)
    parser.add_argument('system_path', type=Path)
    parser.add_argument('instance_path', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.map_path, args.system_path,
                           args.instance_path), sort_keys=True))


if __name__ == '__main__':
    main()
