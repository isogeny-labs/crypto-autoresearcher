#!/usr/bin/env python3
"""Independently check an affine-sliced Semaev Boolean quotient certificate.

The named equations are rebuilt by the dossier's independent descent, then
restricted using its trace identity. A checked map proves nonmembership for
the sliced system; Proposition 2.5b transfers it to the original system.
"""
import argparse
import hashlib
import json
from math import comb
import mmap
import operator
from pathlib import Path
from functools import reduce
import struct
import sys


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def remove_bit(mask, bit):
    return (mask & ((1 << bit) - 1)) | ((mask >> (bit + 1)) << bit)


def substitute(poly, variable, affine_terms):
    """Set one Boolean variable to an affine form; preserve XOR cancellations."""
    result = set()
    bit = 1 << variable
    for monomial in poly:
        if monomial & bit:
            base = monomial ^ bit
            images = (remove_bit(base | term, variable) for term in affine_terms)
        else:
            images = (remove_bit(monomial, variable),)
        for image in images:
            if image in result:
                result.remove(image)
            else:
                result.add(image)
    return result


def trace_slice(record, variable, combination_mask=None):
    source_dir = Path(__file__).resolve().parents[1] / 'semaev-m2-last-fall-degree/verify'
    sys.path.insert(0, str(source_dir))
    from cert_check import descend, mk_field
    n = record['n']
    modulus = int(record['modulus_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    z = int(record['z_hex'], 16)
    if z == 0:
        raise ValueError('Semaev target z must be nonzero')
    basis = [int(v, 16) for v in record['V_basis_hex']]
    variables, polys = descend(n, modulus, record['a2'], a6, z, basis)
    k = len(basis)
    if variables != 2 * k or not k <= variable < variables:
        raise ValueError('slice variable must be a b-coordinate')
    if combination_mask is not None:
        if not (0 < combination_mask < (1 << len(polys))):
            raise ValueError('affine combination mask is out of range')
        relation = set()
        for i, poly in enumerate(polys):
            if combination_mask >> i & 1:
                relation.symmetric_difference_update(poly)
        if any(m and (m & (m - 1)) for m in relation):
            raise ValueError('selected equation combination is not affine')
        if (1 << variable) not in relation:
            raise ValueError('selected affine equation does not eliminate variable')
        affine = sorted(relation - {1 << variable})
        return variables - 1, [substitute(p, variable, affine) for p in polys], affine
    j = variable - k
    mul, power, trace = mk_field(n, modulus)
    trace_bits = [trace(v) for v in basis]
    if trace_bits[j] != 1:
        raise ValueError('selected basis vector has zero trace')
    inverse_z2 = power(mul(z, z), (1 << n) - 2)
    alpha_trace = trace(mul(a6, inverse_z2))
    trace_consequence = set()
    for i, poly in enumerate(polys):
        if trace(mul(inverse_z2, 1 << i)):
            trace_consequence.symmetric_difference_update(poly)
    expected_trace = ({0} if alpha_trace else set())
    for l in range(k):
        if trace_bits[l]:
            expected_trace.symmetric_difference_update((1 << l, 1 << (k + l)))
    if trace_consequence != expected_trace:
        raise ValueError('independent descent does not yield pinned trace equation')
    affine = ([0] if alpha_trace else []) + [1 << l for l in range(k)
              if trace_bits[l]] + [1 << (k + l) for l in range(k)
                                    if l != j and trace_bits[l]]
    sliced = [substitute(p, variable, affine) for p in polys]
    return variables - 1, sliced, affine


def read_certificate(path):
    with path.open('rb') as stream:
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            if len(data) < 32:
                raise ValueError('truncated certificate')
            n, degree, columns, codim = struct.unpack_from('<4q', data)
            if not (1 <= n <= 62 and 1 <= degree <= n and
                    1 <= codim <= columns and
                    columns == sum(comb(n, e) for e in range(degree + 1))):
                raise ValueError('invalid certificate dimensions')
            mask_end = 32 + 8 * columns
            row_bytes = 8 * ((codim + 63) // 64)
            if len(data) != mask_end + columns * row_bytes:
                raise ValueError('invalid certificate file length')
            masks = struct.unpack_from('<' + str(columns) + 'Q', data, 32)
            if len(set(masks)) != columns or any(m >= (1 << n) or
                                                  bin(m).count('1') > degree for m in masks):
                raise ValueError('invalid monomial universe')
            rows = [int.from_bytes(data[mask_end + i * row_bytes:
                                       mask_end + (i + 1) * row_bytes], 'little')
                    for i in range(columns)]
            if any(r >> codim for r in rows):
                raise ValueError('row exceeds quotient width')
    return n, degree, codim, masks, rows


def check_map(n, degree, codim, masks, rows, polys):
    if len(masks) != len(rows) or len(set(masks)) != len(masks):
        raise ValueError('invalid row or monomial count')
    columns = {m: i for i, m in enumerate(masks)}
    if 0 not in columns:
        raise ValueError('missing constant monomial')
    pivots = {}
    for row in rows:
        if row and not (row & (row - 1)):
            pivots[row.bit_length() - 1] = row
    for row in rows:
        value = row
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
        if len(pivots) == codim:
            break
    if len(pivots) != codim:
        raise ValueError('C0: quotient map is not onto')
    for index, poly in enumerate(polys):
        try:
            image = reduce(operator.xor, (rows[columns[m]] for m in poly), 0)
        except KeyError as error:
            raise ValueError('generator exceeds certificate universe') from error
        if image:
            raise ValueError('C1: sliced generator %d has nonzero image' % index)
    if rows[columns[0]] == 0:
        raise ValueError('C3: constant has zero image')
    low = [i for i, m in enumerate(masks) if bin(m).count('1') < degree]
    low_rank = None
    for variable in range(n):
        bit = 1 << variable
        # Let A send each low-degree monomial to its quotient row, and B send
        # it to the row of its product with this variable. Closure is exactly
        # ker(A) <= ker(B). Eliminate paired (A,B) columns: a zero A-remainder
        # must have a zero B-remainder. This avoids materializing a basis of
        # the potentially enormous low-degree kernel.
        paired_pivots = {}
        for index in low:
            image = rows[index]
            product = rows[columns[masks[index] | bit]]
            while image:
                high = image.bit_length() - 1
                pivot = paired_pivots.get(high)
                if pivot is None:
                    paired_pivots[high] = (image, product)
                    break
                image ^= pivot[0]
                product ^= pivot[1]
            else:
                if product:
                    raise ValueError('C2: multiplication fails at variable %d' % variable)
        if low_rank is None:
            low_rank = len(paired_pivots)
        elif low_rank != len(paired_pivots):
            raise ValueError('C2: inconsistent low-degree rank')
    return {'status': 'valid_affine_slice_nonmembership', 'degree': degree,
            'variables': n, 'codimension_lower_bound': codim,
            'generators': len(polys), 'low_kernel_dimension': len(low) - low_rank}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--expect-plan-sha256', required=True)
    parser.add_argument('--expect-descent-source-sha256', required=True)
    parser.add_argument('--variable', type=int, required=True)
    parser.add_argument('--affine-combination-mask', type=lambda s: int(s, 0))
    parser.add_argument('--expect-certificate-sha256')
    args = parser.parse_args()
    try:
        if sha256(args.plan) != args.expect_plan_sha256:
            raise ValueError('plan digest mismatch')
        descent_source = (Path(__file__).resolve().parents[1] /
                          'semaev-m2-last-fall-degree/verify/cert_check.py')
        if sha256(descent_source) != args.expect_descent_source_sha256:
            raise ValueError('independent descent source digest mismatch')
        if args.expect_certificate_sha256 and sha256(args.certificate) != args.expect_certificate_sha256:
            raise ValueError('certificate digest mismatch')
        plan = json.loads(args.plan.read_text())
        n, polys, affine = trace_slice(plan['record'], args.variable,
                                        args.affine_combination_mask)
        cert_n, degree, codim, masks, rows = read_certificate(args.certificate)
        if cert_n != n:
            raise ValueError('certificate has wrong sliced variable count')
        result = check_map(n, degree, codim, masks, rows, polys)
        result['eliminated_variable'] = args.variable
        result['substitution_terms'] = affine
        result['affine_combination_mask'] = (hex(args.affine_combination_mask)
                                             if args.affine_combination_mask is not None else 'trace')
        result['plan_sha256'] = args.expect_plan_sha256
        result['descent_source_sha256'] = args.expect_descent_source_sha256
        result['certificate_sha256'] = sha256(args.certificate)
    except (OSError, KeyError, TypeError, ValueError, IndexError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
