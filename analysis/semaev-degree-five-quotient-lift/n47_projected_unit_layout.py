#!/usr/bin/env python3
"""Read-only selective-rebase unit-layout preflight on a pinned original map.

Rows containing the eliminated variable are skipped, exactly as in
slice_trace_certificate.py. This computes no projected output or closure.
"""

import argparse
import hashlib
import json
from math import comb
import mmap
from pathlib import Path
import struct


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def profile(path, expected_sha256, variable):
    if sha256(path) != expected_sha256:
        raise ValueError('source map digest mismatch')
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        n, degree, columns, q = struct.unpack_from('<4q', data)
        if (n, degree, columns, q) != (48, 4, 213053, 61196):
            raise ValueError('unexpected source map dimensions')
        if not 0 <= variable < n:
            raise ValueError('invalid eliminated variable')
        masks = struct.unpack_from('<' + str(columns) + 'Q', data, 32)
        if (len(set(masks)) != columns or
                list(masks) != sorted(masks, key=lambda m: (-bin(m).count('1'), m))):
            raise ValueError('invalid source monomial order')
        width = 8 * ((q + 63) // 64)
        row_start = 32 + columns * 8
        if len(data) != row_start + columns * width:
            raise ValueError('invalid source map length')
        retained = [i for i, mask in enumerate(masks) if not mask & (1 << variable)]
        expected_columns = sum(comb(n - 1, j) for j in range(degree + 1))
        if len(retained) != expected_columns:
            raise ValueError('wrong projected monomial count')

        original_representatives = [None] * q
        for i in range(columns):
            start = row_start + i * width
            value = int.from_bytes(data[start:start + width], 'little')
            if value and value & (value - 1) == 0:
                original_representatives[value.bit_length() - 1] = i
        if any(i is None for i in original_representatives):
            raise ValueError('original map lacks unit representatives')

        seen = 0
        safe = 0
        literal = 0
        safe_representatives = [None] * q
        for i in reversed(retained):
            start = row_start + i * width
            value = int.from_bytes(data[start:start + width], 'little')
            if value >> q:
                raise ValueError('row exceeds declared quotient width')
            if value and value & (value - 1) == 0:
                literal |= value
                if not seen & value:
                    safe |= value
                    safe_representatives[value.bit_length() - 1] = i
            seen |= value
        original_retained = [j for j, i in enumerate(original_representatives)
                             if not masks[i] & (1 << variable)]
        retained_original_safe = all(safe_representatives[j] == original_representatives[j]
                                     for j in original_retained)
    missing = q - bin(safe).count('1')
    return {'schema': 'semaev.projected-unit-layout/v1',
            'source_sha256': expected_sha256, 'eliminated_variable': variable,
            'projected_variables': n - 1, 'projected_columns': expected_columns,
            'projected_bytes': 32 + expected_columns * (8 + width),
            'codimension_claimed': q,
            'literal_unit_coordinates': bin(literal).count('1'),
            'reverse_safe_unit_coordinates': q - missing,
            'original_unit_representatives_retained': len(original_retained),
            'retained_original_representatives_are_safe': retained_original_safe,
            'coordinates_requiring_projected_elimination': missing,
            'projected_bitset_payload_bytes': expected_columns * 8 * ((missing + 63) // 64),
            'scope': 'Read-only layout of an existing D4 map. Does not establish projected rank, checker acceptance, actual rebased border, or D5 nonmembership.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--variable', type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(profile(args.source, args.sha256, args.variable), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
