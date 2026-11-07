#!/usr/bin/env python3
"""Independently check a sliced Semaev quotient map with mapped rows.

This is a complete alternative to the frozen D4 checker, intended for a
future D5 certificate. It derives the named equations using the independent
descent and checks Proposition 1.5(i-ii), surjectivity, and pi(1) != 0.
The original D4 checker and its frozen source hash are left untouched.
"""

import argparse
from functools import reduce
import json
from math import comb
import mmap
import operator
from pathlib import Path
import struct

from check_quotient_closure_factorized import check_closure_factorized
from check_trace_slice_certificate import sha256, trace_slice


class MappedCertificate:
    """Read-only certificate whose row payload stays in a file mapping."""

    def __init__(self, path):
        with open(path, 'rb') as stream:
            self.data = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            if len(self.data) < 32:
                raise ValueError('truncated certificate')
            self.n, self.degree, self.columns, self.codim = struct.unpack_from(
                '<4q', self.data, 0)
            if not (1 <= self.n <= 62 and 2 <= self.degree <= self.n and
                    1 <= self.codim <= self.columns and
                    self.columns == sum(comb(self.n, d)
                                        for d in range(self.degree + 1))):
                raise ValueError('invalid certificate dimensions')
            self.row_bytes = 8 * ((self.codim + 63) // 64)
            self.row_start = 32 + 8 * self.columns
            if len(self.data) != self.row_start + self.columns * self.row_bytes:
                raise ValueError('invalid certificate file length')
            self.masks = struct.unpack_from('<%dQ' % self.columns, self.data, 32)
            if (len(set(self.masks)) != self.columns or
                    any(m >= (1 << self.n) or bin(m).count('1') > self.degree
                        for m in self.masks)):
                raise ValueError('invalid monomial universe')
            self.rows = self.Rows(self)
        except BaseException:
            self.data.close()
            raise

    class Rows:
        def __init__(self, certificate):
            self.certificate = certificate

        def __len__(self):
            return self.certificate.columns

        def __getitem__(self, index):
            c = self.certificate
            if not 0 <= index < c.columns:
                raise IndexError(index)
            start = c.row_start + index * c.row_bytes
            return int.from_bytes(c.data[start:start + c.row_bytes], 'little')

    def close(self):
        self.data.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def check_map_factorized(certificate, polys):
    n, degree, codim = (certificate.n, certificate.degree,
                        certificate.codim)
    masks, rows = certificate.masks, certificate.rows
    columns = {m: i for i, m in enumerate(masks)}
    # Exact cardinality, distinctness, and the degree/range checks in the
    # reader prove that this is the entire Boolean monomial universe.
    pivots = {}
    for row in rows:
        if row >> codim:
            raise ValueError('C0: row exceeds quotient width')
        value = row
        if len(pivots) == codim:
            continue
        while value:
            high = value.bit_length() - 1
            if high in pivots:
                value ^= pivots[high]
            else:
                pivots[high] = value
                break
    if len(pivots) != codim:
        raise ValueError('C0: quotient map is not onto')
    for index, poly in enumerate(polys):
        try:
            image = reduce(operator.xor, (rows[columns[m]] for m in poly), 0)
        except KeyError as error:
            raise ValueError('C1: generator exceeds certificate universe') from error
        if image:
            raise ValueError('C1: generator %d has nonzero image' % index)
    if rows[columns[0]] == 0:
        raise ValueError('C3: constant has zero image')
    kernel_dimension = check_closure_factorized(n, degree, masks, rows,
                                                 columns=columns)
    return {'status': 'valid_affine_slice_nonmembership', 'degree': degree,
            'variables': n, 'codimension_lower_bound': codim,
            'generators': len(polys),
            'low_kernel_dimension': kernel_dimension,
            'checker_method': 'mapped_rows_factorized_closure'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--expect-plan-sha256', required=True)
    parser.add_argument('--expect-descent-source-sha256', required=True)
    parser.add_argument('--expect-slice-source-sha256', required=True)
    parser.add_argument('--variable', type=int, required=True)
    parser.add_argument('--affine-combination-mask', type=lambda s: int(s, 0))
    parser.add_argument('--expect-certificate-sha256', required=True)
    args = parser.parse_args()
    try:
        if sha256(args.plan) != args.expect_plan_sha256:
            raise ValueError('plan digest mismatch')
        source_dir = Path(__file__).resolve().parent
        descent_source = (source_dir.parent /
                          'semaev-m2-last-fall-degree/verify/cert_check.py')
        slice_source = source_dir / 'check_trace_slice_certificate.py'
        if sha256(descent_source) != args.expect_descent_source_sha256:
            raise ValueError('independent descent source digest mismatch')
        if sha256(slice_source) != args.expect_slice_source_sha256:
            raise ValueError('slice source digest mismatch')
        if sha256(args.certificate) != args.expect_certificate_sha256:
            raise ValueError('certificate digest mismatch')
        plan = json.loads(args.plan.read_text())
        n, polys, affine = trace_slice(plan['record'], args.variable,
                                        args.affine_combination_mask)
        with MappedCertificate(args.certificate) as certificate:
            if certificate.n != n:
                raise ValueError('certificate has wrong sliced variable count')
            result = check_map_factorized(certificate, polys)
        result['eliminated_variable'] = args.variable
        result['substitution_terms'] = affine
        result['affine_combination_mask'] = (hex(args.affine_combination_mask)
                                             if args.affine_combination_mask is not None
                                             else 'trace')
        result['plan_sha256'] = args.expect_plan_sha256
        result['descent_source_sha256'] = args.expect_descent_source_sha256
        result['slice_source_sha256'] = args.expect_slice_source_sha256
        result['certificate_sha256'] = args.expect_certificate_sha256
    except (OSError, KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
