#!/usr/bin/env python3
"""Exact Boolean W3 screen for a fixed affine restriction of SLCGEN01 inputs.

This only rules out a degree-five nonmembership candidate when 1 is in W3.
Nonmembership at W3 does not imply nonmembership at W5.
"""

import argparse
from collections import deque
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import struct

MAGIC = b'SLCGEN01'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_generators(data):
    if len(data) < 24 or data[:8] != MAGIC:
        raise ValueError('invalid generator header')
    n, count = struct.unpack_from('<QQ', data, 8)
    if not (1 <= n <= 62 and 1 <= count <= 100000):
        raise ValueError('invalid generator dimensions')
    offset = 24
    polys = []
    for _ in range(count):
        if offset + 8 > len(data):
            raise ValueError('truncated generator length')
        terms, = struct.unpack_from('<Q', data, offset)
        offset += 8
        if terms > (len(data) - offset) // 8:
            raise ValueError('truncated generator terms')
        masks = struct.unpack_from('<' + str(terms) + 'Q', data, offset)
        offset += 8 * terms
        if len(set(masks)) != terms or any(m >= 1 << n or bin(m).count('1') > 2
                                           for m in masks):
            raise ValueError('invalid quadratic generator')
        polys.append(set(masks))
    if offset != len(data):
        raise ValueError('trailing generator bytes')
    return n, polys


def restrict(polys, n, fixed):
    if len(fixed) >= n or any(not 0 <= i < n or b not in (0, 1)
                              for i, b in fixed.items()):
        raise ValueError('invalid restriction')
    zero_mask = sum(1 << i for i, b in fixed.items() if b == 0)
    fixed_mask = sum(1 << i for i in fixed)
    retained = [i for i in range(n) if i not in fixed]
    image = [1 << j for j in retained]
    result = []
    for poly in polys:
        out = set()
        for monomial in poly:
            if monomial & zero_mask:
                continue
            kept = monomial & ~fixed_mask
            mapped = sum(1 << j for j, old in enumerate(retained)
                         if kept & image[j])
            if mapped in out:
                out.remove(mapped)
            else:
                out.add(mapped)
        result.append(out)
    return len(retained), result


class Echelon:
    def __init__(self, low_columns):
        self.rows = {}
        self.low_columns = low_columns
        self.low_queue = deque()

    def add(self, row):
        while row:
            pivot = row.bit_length() - 1
            old = self.rows.get(pivot)
            if old is None:
                self.rows[pivot] = row
                if pivot < self.low_columns:
                    self.low_queue.append(row)
                return
            row ^= old

    def contains(self, row):
        while row:
            pivot = row.bit_length() - 1
            old = self.rows.get(pivot)
            if old is None:
                return False
            row ^= old
        return True


def screen_w3(n, polys, max_columns):
    columns = sum(comb(n, d) for d in range(4))
    if columns > max_columns:
        raise ValueError('W3 column cap exceeded')
    masks = [sum(1 << i for i in choice)
             for d in range(4) for choice in combinations(range(n), d)]
    index = {mask: j for j, mask in enumerate(masks)}
    low_columns = sum(comb(n, d) for d in range(3))
    multiply = [[index[mask | (1 << i)] for mask in masks[:low_columns]]
                for i in range(n)]
    closure = Echelon(low_columns)
    for poly in polys:
        closure.add(sum(1 << index[mask] for mask in poly))
    generator_rank = len(closure.rows)
    processed_low = 0
    while closure.low_queue:
        row = closure.low_queue.popleft()
        processed_low += 1
        for variable in range(n):
            product = 0
            while row:
                bit = row & -row
                j = bit.bit_length() - 1
                if j >= low_columns:
                    raise ValueError('invalid low-degree closure row')
                product ^= 1 << multiply[variable][j]
                row ^= bit
            closure.add(product)
    return {'variables': n, 'columns': columns, 'generator_rank': generator_rank,
            'w3_rank': len(closure.rows),
            'w3_low_rank': sum(j < low_columns for j in closure.rows),
            'processed_low_rows': processed_low,
            'one_in_w3': closure.contains(1 << index[0])}


def parse_fix(value):
    parts = value.split('=')
    if len(parts) != 2:
        raise argparse.ArgumentTypeError('use INDEX=0 or INDEX=1')
    try:
        index, bit = map(int, parts)
    except ValueError as error:
        raise argparse.ArgumentTypeError('use decimal INDEX=0 or INDEX=1') from error
    if bit not in (0, 1) or index < 0:
        raise argparse.ArgumentTypeError('invalid fixed coordinate')
    return index, bit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--expect-sha256', required=True)
    parser.add_argument('--fix', type=parse_fix, action='append', required=True)
    parser.add_argument('--max-columns', type=int, default=20000)
    args = parser.parse_args()
    data = args.input.read_bytes()
    if sha256(data) != args.expect_sha256:
        parser.error('input SHA-256 mismatch')
    fixed = dict(args.fix)
    if len(fixed) != len(args.fix):
        parser.error('duplicate fixed coordinate')
    n, polys = read_generators(data)
    try:
        restricted_n, restricted = restrict(polys, n, fixed)
        result = screen_w3(restricted_n, restricted, args.max_columns)
    except ValueError as error:
        parser.error(str(error))
    result.update({'schema': 'semaev.affine-restriction-d3-screen/v1',
                   'input_sha256': args.expect_sha256,
                   'fixed': [{'variable': i, 'value': b}
                             for i, b in sorted(fixed.items())],
                   'original_variables': n, 'generators': len(polys),
                   'interpretation': ('rules_out_d5_nonmembership_for_this_restriction'
                                      if result['one_in_w3']
                                      else 'd5_nonmembership_unknown')})
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
