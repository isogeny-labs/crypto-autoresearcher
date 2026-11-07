#!/usr/bin/env python3
"""Read-only affine-relation and border-incidence screen of an existing D4 map.

This does not project/rebase the map or compute a D5 closure. Border counts
after projection are only optimistic screens until an actual rebase is profiled.
"""

import argparse
import hashlib
import itertools
import json
import math
import mmap
from pathlib import Path
import struct


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def envelope(border, codimension, variables, columns, next_columns, chunk=4096):
    work = codimension + border
    stride = ((work + 63) // 64 + 2) * 8
    seedstride = ((codimension + 63) // 64 + 2) * 8
    payload = ((next_columns + chunk) * stride + columns * seedstride
               + (3 * work + 4 * chunk + codimension) * stride
               + (codimension + chunk) * seedstride + next_columns * 40
               + variables * codimension * 8 + variables * chunk * 8
               + (codimension + chunk) * stride + chunk * seedstride)
    return payload * 135 // 100 + 64 * 2**20


def screen(path, expected):
    if sha256(path) != expected:
        raise ValueError('D4 map SHA-256 mismatch')
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        n, degree, columns, q = struct.unpack_from('<4q', data)
        if (n, degree, columns, q) != (48, 4, 213053, 61196):
            raise ValueError('unexpected D4 map dimensions')
        masks = struct.unpack_from('<' + str(columns) + 'Q', data, 32)
        if len(set(masks)) != columns:
            raise ValueError('duplicate monomial')
        index = {mask: i for i, mask in enumerate(masks)}
        width = 8 * ((q + 63) // 64)
        offset = 32 + 8 * columns
        if len(data) != offset + columns * width:
            raise ValueError('invalid map length')

        def row(mask):
            i = index[mask]
            return int.from_bytes(data[offset + i * width:offset + (i + 1) * width], 'little')

        pivots = {}
        relations = []
        for j, mask in enumerate([0] + [1 << i for i in range(n)]):
            value = row(mask)
            combo = 1 << j
            while value:
                bit = value.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = value, combo
                    break
                pivot, expression = pivots[bit]
                value ^= pivot
                combo ^= expression
            if not value:
                relations.append({'constant': bool(combo & 1),
                                  'variables': [i for i in range(n) if combo >> (i + 1) & 1]})

        representatives = [None] * q
        for mask in masks:
            value = row(mask)
            if value and value & (value - 1) == 0:
                representatives[value.bit_length() - 1] = mask
        if any(mask is None for mask in representatives):
            raise ValueError('map lacks unit representatives')
        free = set(representatives)
        border = 0
        incidence = [0] * n
        for combo in itertools.combinations(range(n), degree + 1):
            mask = sum(1 << i for i in combo)
            if all(mask ^ (1 << i) in free for i in combo):
                border += 1
                for i in combo:
                    incidence[i] += 1

    sliced_columns = sum(math.comb(n - 1, j) for j in range(degree + 1))
    sliced_next = sum(math.comb(n - 1, j) for j in range(degree + 2))
    cap = 64 * 2**30
    low, high = 0, border
    while low < high:
        middle = (low + high + 1) // 2
        if envelope(middle, q, n - 1, sliced_columns, sliced_next) <= cap:
            low = middle
        else:
            high = middle - 1
    eligible = sorted({i for relation in relations for i in relation['variables']})
    return {'schema': 'semaev.n47-slice-capacity-screen/v1', 'seed_sha256': expected,
            'affine_rank': len(pivots), 'affine_relations': relations, 'codimension': q,
            'source_border': border, 'sliced_d4_columns': sliced_columns,
            'sliced_d5_columns': sliced_next, 'maximum_border_under_64_gib': low,
            'sliced_envelope_if_border_unchanged_bytes': envelope(border, q, n - 1, sliced_columns, sliced_next),
            'eligible': [{'variable': i,
                          'representatives_containing': sum(bool(mask >> i & 1) for mask in representatives),
                          'source_border_containing': incidence[i],
                          'optimistic_border_without_containing': border - incidence[i],
                          'optimistic_envelope_bytes': envelope(border - incidence[i], q, n - 1, sliced_columns, sliced_next)}
                         for i in eligible],
            'scope': 'Existing D4 map only. Optimistic projected borders are not actual rebased borders or D5 evidence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('seed', type=Path)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(screen(args.seed, args.sha256), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
