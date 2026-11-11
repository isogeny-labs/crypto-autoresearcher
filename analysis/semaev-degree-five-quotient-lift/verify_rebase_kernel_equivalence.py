#!/usr/bin/env python3
"""Independently check every row of a quotient-map change of basis.

The output map supplies unit-row representatives. Their input rows define a
candidate basis. This checker reduces input rows against that basis and
compares the resulting coordinates with every output row. It does not use the
producer's pivot arrays or replay its reverse-greedy selection algorithm.
"""

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import struct


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 << 20), b''):
            value.update(block)
    return value.hexdigest()


def mapped(path):
    stream = path.open('rb')
    return stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)


def check(source, target, source_sha, target_sha):
    if source == target:
        raise ValueError('source and target paths coincide')
    if digest(source) != source_sha or digest(target) != target_sha:
        raise ValueError('pinned file digest mismatch')
    left_file, left = mapped(source)
    right_file, right = mapped(target)
    try:
        if len(left) < 32 or len(left) != len(right):
            raise ValueError('invalid file lengths')
        n, degree, columns, codim = struct.unpack_from('<4q', left, 0)
        if (n, degree, columns, codim) != struct.unpack_from('<4q', right, 0):
            raise ValueError('different certificate dimensions')
        if not (0 < degree < n <= 62 and 0 < codim <= columns):
            raise ValueError('invalid header')
        width = 8 * ((codim + 63) // 64)
        start = 32 + 8 * columns
        if len(left) != start + columns * width:
            raise ValueError('invalid certificate layout')
        if left[32:start] != right[32:start]:
            raise ValueError('monomial order differs')

        def row(data, index):
            offset = start + index * width
            value = int.from_bytes(data[offset:offset + width], 'little')
            if value.bit_length() > codim:
                raise ValueError('out-of-range row bit')
            return value

        # Read the new map, not the producer's selection transcript. Every
        # codomain coordinate needs a literal unit representative.
        representatives = [None] * codim
        for index in range(columns):
            value = row(right, index)
            if value and value & (value - 1) == 0:
                coordinate = value.bit_length() - 1
                if representatives[coordinate] is None:
                    representatives[coordinate] = index
        if any(index is None for index in representatives):
            raise ValueError('output map lacks a complete unit-row basis')

        retained = []
        missing = []
        for coordinate, index in enumerate(representatives):
            if row(left, index) == 1 << coordinate:
                retained.append(coordinate)
            else:
                missing.append(coordinate)
        missing_mask = sum(1 << coordinate for coordinate in missing)
        if not missing:
            raise ValueError('no nontrivial basis change to check')

        # The old rows selected by the new unit representatives must form a
        # basis: retained old units span the complement, while the remaining
        # selected old rows must span all missing-coordinate projections.
        pivots = {}
        for coordinate in missing:
            old = row(left, representatives[coordinate])
            projected = old & missing_mask
            correction = old ^ (1 << coordinate)
            while projected:
                bit = projected.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = (projected, correction)
                    break
                basis_projected, basis_correction = pivots[bit]
                projected ^= basis_projected
                correction ^= basis_correction
            else:
                raise ValueError('selected old rows are dependent')
        if len(pivots) != len(missing):
            raise ValueError('missing-coordinate basis incomplete')

        # This is the unique invertible linear map that sends each selected
        # old representative to its corresponding new unit coordinate.
        for index in range(columns):
            old = row(left, index)
            projected = old & missing_mask
            transformed = old
            while projected:
                bit = projected.bit_length() - 1
                basis_projected, basis_correction = pivots[bit]
                projected ^= basis_projected
                transformed ^= basis_correction
            if transformed != row(right, index):
                raise ValueError(f'row {index} differs under unique basis map')
        return {'schema': 'semaev.rebase-full-row-check/v1',
                'source_sha256': source_sha, 'target_sha256': target_sha,
                'variables': n, 'degree': degree, 'columns_checked': columns,
                'codimension': codim, 'retained_units': len(retained),
                'changed_coordinates': len(missing),
                'selected_basis_rank': len(pivots),
                'all_rows_equal_under_invertible_map': True}
    finally:
        right.close()
        right_file.close()
        left.close()
        left_file.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--target-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.source, args.target, args.source_sha256,
                           args.target_sha256), sort_keys=True))


if __name__ == '__main__':
    main()
