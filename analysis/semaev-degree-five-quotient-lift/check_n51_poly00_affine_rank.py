#!/usr/bin/env python3
"""Check a 50-by-50 quadratic minor and the unique affine generator relation."""

import argparse
import hashlib
import json
from pathlib import Path


SYSTEM_SHA256 = 'dd7a724b4161da605952808c373eeeb2a904fe7aae65699b932f19bf2585674b'


def rank(rows):
    pivots = {}
    for original in rows:
        row = original
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def check(system_path, witness_path, minor_path):
    if hashlib.sha256(system_path.read_bytes()).hexdigest() != SYSTEM_SHA256:
        raise ValueError('original system digest mismatch')
    lines = system_path.read_text().splitlines()
    if lines[0] != '52 51' or len(lines) != 52:
        raise ValueError('unexpected system dimensions')
    polys = []
    for line in lines[1:]:
        words = line.split()
        masks = [int(word, 16) for word in words[1:]]
        if len(masks) != int(words[0]) or masks != sorted(set(masks)):
            raise ValueError('invalid equation row')
        if any(mask >= 1 << 52 or bin(mask).count('1') > 2 for mask in masks):
            raise ValueError('unexpected equation degree or variable')
        polys.append(set(masks))
    witness = json.loads(witness_path.read_text())
    if witness['input_sys_sha256'] != SYSTEM_SHA256:
        raise ValueError('affine witness input mismatch')
    relation = set()
    for index in witness['generator_indices_zero_based']:
        relation.symmetric_difference_update(polys[index])
    if relation != {0, 1, 1 << 26}:
        raise ValueError('affine witness mismatch')
    minor = json.loads(minor_path.read_text())
    row_indices = minor['generator_indices_zero_based']
    columns = [int(value, 16) for value in minor['quadratic_masks_hex']]
    if (minor['input_sys_sha256'] != SYSTEM_SHA256 or
            len(row_indices) != 50 or len(set(row_indices)) != 50 or
            len(columns) != 50 or len(set(columns)) != 50 or
            any(not 0 <= index < 51 for index in row_indices) or
            any(bin(mask).count('1') != 2 or mask >= 1 << 52 for mask in columns)):
        raise ValueError('invalid minor specification')
    matrix = [sum(1 << j for j, mask in enumerate(columns) if mask in polys[i])
              for i in row_indices]
    if rank(matrix) != 50:
        raise ValueError('quadratic minor is singular')
    # Fifty independent quadratic rows plus the displayed affine dependency
    # force the full 51-row quadratic rank to be exactly fifty.
    return {'status': 'unique_affine_generator_relation',
            'quadratic_rank': 50, 'minor_order': 50,
            'affine_kernel_dimension': 1,
            'system_sha256': SYSTEM_SHA256}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('system', type=Path)
    parser.add_argument('witness', type=Path)
    parser.add_argument('minor', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.system, args.witness, args.minor)
    except (OSError, KeyError, IndexError, TypeError, ValueError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
