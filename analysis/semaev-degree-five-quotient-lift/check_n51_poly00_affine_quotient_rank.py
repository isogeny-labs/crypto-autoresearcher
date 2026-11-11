#!/usr/bin/env python3
"""Check affine images in the retained n51 polynomial00 D3/D4 quotient maps."""

import argparse
import hashlib
import json
from pathlib import Path
import struct


EXPECTED = {
    3: (23479, 12509,
        '2b1b26fe59b2a5489dfd666b9753344943a14f19af41fe90835d1d80b1a7fd5c'),
    4: (294204, 45615,
        '90878ee8bc6bda02957f25728380a9e677cd13b0f46c9eed1828349da796f115'),
}


def check(path, expected_degree):
    expected_columns, expected_quotient, expected_sha256 = EXPECTED[expected_degree]
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    if digest.hexdigest() != expected_sha256:
        raise ValueError('quotient map digest mismatch')
    with path.open('rb') as source:
        header = source.read(32)
        if len(header) != 32:
            raise ValueError('truncated map')
        variables, degree, columns, quotient = struct.unpack('<4q', header)
        if (variables, degree, columns, quotient) != (
                52, expected_degree, expected_columns, expected_quotient):
            raise ValueError('unexpected map dimensions')
        mask_bytes = source.read(columns * 8)
        if len(mask_bytes) != columns * 8:
            raise ValueError('truncated monomial list')
        masks = struct.unpack('<%dQ' % columns, mask_bytes)
        width = 8 * ((quotient + 63) // 64)
        offset = 32 + columns * 8
        if path.stat().st_size != offset + columns * width or len(set(masks)) != columns:
            raise ValueError('invalid map body or duplicate monomial')
        affine_masks = [0] + [1 << i for i in range(52)]
        indices = {mask: i for i, mask in enumerate(masks)}
        if any(mask not in indices for mask in affine_masks):
            raise ValueError('affine monomial missing')
        pivots = {}
        relations = []
        for affine_index, mask in enumerate(affine_masks):
            index = indices[mask]
            source.seek(offset + index * width)
            row_bytes = source.read(width)
            if len(row_bytes) != width:
                raise ValueError('truncated affine image')
            row = int.from_bytes(row_bytes, 'little')
            witness = 1 << affine_index
            while row:
                bit = row.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = (row, witness)
                    break
                row ^= pivots[bit][0]
                witness ^= pivots[bit][1]
            if row == 0:
                relations.append(witness)
    if len(pivots) + len(relations) != 53:
        raise ValueError('affine elimination incomplete')
    expected_relation = (1 << 0) | (1 << 1) | (1 << 27)
    if relations != [expected_relation]:
        raise ValueError('unexpected affine kernel basis: %r' % relations)
    return {'status': 'unique_affine_quotient_relation', 'degree': degree,
            'affine_monomials': 53, 'affine_image_rank': len(pivots),
            'affine_kernel_dimension': len(relations),
            'relation_masks': ['0x0', '0x1', '0x4000000'],
            'map_sha256': expected_sha256}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('quotient_map', type=Path)
    parser.add_argument('--degree', type=int, choices=(3, 4), required=True)
    args = parser.parse_args()
    try:
        result = check(args.quotient_map, args.degree)
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
