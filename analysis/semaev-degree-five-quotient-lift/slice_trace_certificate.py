#!/usr/bin/env python3
"""Project a Boolean quotient certificate onto all but one variable.

The producer copies rows; it does not certify the source or the result. Check
the result against independently descended, trace-sliced equations.
"""
import argparse
import hashlib
from math import comb
import os
from pathlib import Path
import struct


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def remove_bit(mask, bit):
    return (mask & ((1 << bit) - 1)) | ((mask >> (bit + 1)) << bit)


def project(source, destination, variable, expected_sha256):
    if digest(source) != expected_sha256:
        raise ValueError('source certificate digest mismatch')
    with source.open('rb') as stream:
        header = stream.read(32)
        if len(header) != 32:
            raise ValueError('truncated source header')
        n, degree, columns, codim = struct.unpack('<4q', header)
        if not (2 <= n <= 62 and 0 <= degree <= n - 1 and
                0 <= variable < n and 1 <= codim <= columns and
                columns == sum(comb(n, e) for e in range(degree + 1))):
            raise ValueError('invalid source dimensions')
        masks_blob = stream.read(8 * columns)
        if len(masks_blob) != 8 * columns:
            raise ValueError('truncated source monomials')
        masks = struct.unpack('<' + str(columns) + 'Q', masks_blob)
        if len(set(masks)) != columns or any(m >= (1 << n) or
                                               bin(m).count('1') > degree for m in masks):
            raise ValueError('invalid source monomial universe')
        retained = [(i, remove_bit(m, variable)) for i, m in enumerate(masks)
                    if not (m >> variable) & 1]
        want = sum(comb(n - 1, e) for e in range(degree + 1))
        if len(retained) != want or len({m for _, m in retained}) != want:
            raise ValueError('invalid projected monomial universe')
        row_bytes = 8 * ((codim + 63) // 64)
        if source.stat().st_size != 32 + 8 * columns + columns * row_bytes:
            raise ValueError('invalid source file length')
        if destination.exists():
            raise FileExistsError(destination)
        partial = destination.with_name(destination.name + '.partial')
        with partial.open('xb') as output:
            output.write(struct.pack('<4q', n - 1, degree, want, codim))
            output.write(struct.pack('<' + str(want) + 'Q', *(m for _, m in retained)))
            selected = {index for index, _ in retained}
            for index in range(columns):
                row = stream.read(row_bytes)
                if len(row) != row_bytes:
                    raise ValueError('truncated source row')
                if index in selected:
                    output.write(row)
        os.link(partial, destination)
        partial.unlink()
    return {'variables': n - 1, 'degree': degree, 'columns': want,
            'codimension': codim, 'source_sha256': expected_sha256,
            'certificate_sha256': digest(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--variable', type=int, required=True)
    parser.add_argument('--expect-source-sha256', required=True)
    args = parser.parse_args()
    print(project(args.source, args.destination, args.variable,
                  args.expect_source_sha256))


if __name__ == '__main__':
    main()
