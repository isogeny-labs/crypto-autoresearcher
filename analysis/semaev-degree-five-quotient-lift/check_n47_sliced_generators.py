#!/usr/bin/env python3
"""Check the n47 sliced-generator export against the retained original .sys.

The export and its independent-descent producer are not imported here. The
original .sys is independently tied to the named instance by the affine
witness checker before this checker applies its own Boolean substitution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from check_n47_affine_witness import check as check_witness


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def remove_bit(mask, bit):
    return (mask & ((1 << bit) - 1)) | ((mask >> (bit + 1)) << bit)


def read_system(path):
    with path.open() as stream:
        variables, count = map(int, stream.readline().split())
        polys = []
        for line in stream:
            words = line.split()
            if len(words) != int(words[0]) + 1:
                raise ValueError('malformed original generator')
            masks = [int(word, 16) for word in words[1:]]
            if len(masks) != len(set(masks)):
                raise ValueError('duplicate original monomial')
            polys.append(set(masks))
    if len(polys) != count:
        raise ValueError('original generator count mismatch')
    return variables, polys


def read_export(path):
    with path.open('rb') as stream:
        if stream.read(8) != b'SLCGEN01':
            raise ValueError('wrong export magic')
        header = stream.read(16)
        if len(header) != 16:
            raise ValueError('truncated export header')
        variables, count = struct.unpack('<QQ', header)
        if not (1 <= variables <= 62 and 1 <= count <= 100000):
            raise ValueError('invalid export dimensions')
        polys = []
        for _ in range(count):
            size_bytes = stream.read(8)
            if len(size_bytes) != 8:
                raise ValueError('truncated export generator')
            size, = struct.unpack('<Q', size_bytes)
            if size > 1000000:
                raise ValueError('export generator is too large')
            payload = stream.read(8 * size)
            if len(payload) != 8 * size:
                raise ValueError('truncated export monomials')
            masks = struct.unpack('<' + str(size) + 'Q', payload)
            if tuple(sorted(set(masks))) != masks or any(m >= 1 << variables for m in masks):
                raise ValueError('invalid export monomials')
            polys.append(set(masks))
        if stream.read(1):
            raise ValueError('trailing export bytes')
    return variables, polys


def slice_poly(poly, variable, affine):
    bit = 1 << variable
    result = set()
    for monomial in poly:
        terms = (affine if monomial & bit else (0,))
        for term in terms:
            image = remove_bit((monomial & ~bit) | term, variable)
            if image in result:
                result.remove(image)
            else:
                result.add(image)
    return result


def check(system, witness, plan, descent_source, export, expected_export_sha256):
    witness_result = check_witness(system, witness, plan, descent_source)
    proof = json.loads(witness.read_text())
    variable = 47
    combination = sum(1 << i for i in proof['generator_indices_zero_based'])
    if combination != 0x25d881e86ebe or variable not in proof['relation_variable_indices']:
        raise ValueError('wrong named affine relation')
    affine = [1 << i for i in proof['relation_variable_indices'] if i != variable]
    if proof['constant']:
        affine.append(0)
    old_n, original = read_system(system)
    new_n, sliced = read_export(export)
    if old_n != 48 or new_n != 47 or len(original) != len(sliced):
        raise ValueError('named system or export dimensions mismatch')
    for i, (source, actual) in enumerate(zip(original, sliced)):
        if slice_poly(source, variable, affine) != actual:
            raise ValueError('sliced generator %d differs from original .sys' % i)
    if digest(export) != expected_export_sha256:
        raise ValueError('export digest mismatch')
    return {'accepted': True, 'variables': new_n, 'generators': len(sliced),
            'terms': sum(map(len, sliced)), 'affine_combination_mask': hex(combination),
            'input_sys_sha256': witness_result['input_sys_sha256'],
            'descent_source_sha256': witness_result['descent_source_sha256'],
            'export_sha256': expected_export_sha256,
            'independent_descent_matched': witness_result['independent_descent_matched']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('system', type=Path)
    parser.add_argument('witness', type=Path)
    parser.add_argument('plan', type=Path)
    parser.add_argument('descent_source', type=Path)
    parser.add_argument('export', type=Path)
    parser.add_argument('--expect-export-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.system, args.witness, args.plan, args.descent_source,
                           args.export, args.expect_export_sha256), sort_keys=True))


if __name__ == '__main__':
    main()
