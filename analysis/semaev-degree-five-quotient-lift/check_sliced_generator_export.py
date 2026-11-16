#!/usr/bin/env python3
"""Check a sliced generator binary against a separately saved original .sys.

This verifier does not call the generator exporter or the field descent.
The affine relation witness must be checked separately against that descent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read_sys(path):
    with path.open() as source:
        n, count = map(int, source.readline().split())
        polys = []
        for line in source:
            words = line.split()
            if not words:
                continue
            length = int(words[0])
            masks = [int(word, 16) for word in words[1:]]
            if len(masks) != length or len(set(masks)) != length:
                raise ValueError('invalid original generator line')
            polys.append(set(masks))
    if len(polys) != count or any(m >= 1 << n for p in polys for m in p):
        raise ValueError('invalid original system dimensions')
    return n, polys


def read_binary(path):
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b'SLCGEN01':
        raise ValueError('invalid sliced generator header')
    n, count = struct.unpack_from('<QQ', data, 8)
    offset = 24
    polys = []
    for _ in range(count):
        if offset + 8 > len(data):
            raise ValueError('truncated generator length')
        length, = struct.unpack_from('<Q', data, offset)
        offset += 8
        if length > (len(data) - offset) // 8:
            raise ValueError('truncated generator terms')
        masks = struct.unpack_from('<' + str(length) + 'Q', data, offset)
        offset += length * 8
        if len(set(masks)) != length or tuple(sorted(masks)) != masks:
            raise ValueError('invalid generator terms')
        polys.append(set(masks))
    if offset != len(data) or any(m >= 1 << n for p in polys for m in p):
        raise ValueError('invalid sliced generator dimensions')
    return n, polys


def substitute(poly, variable, affine):
    bit = 1 << variable
    low = bit - 1
    def delete_bit(mask):
        return (mask & low) | ((mask >> (variable + 1)) << variable)
    result = set()
    for mask in poly:
        terms = (delete_bit(mask ^ bit | a) for a in affine) if mask & bit else (delete_bit(mask),)
        for term in terms:
            if term in result:
                result.remove(term)
            else:
                result.add(term)
    return result


def check(original, sliced, witness, expected_original, expected_sliced, expected_witness):
    for path, expected in ((original, expected_original), (sliced, expected_sliced),
                           (witness, expected_witness)):
        if sha256(path) != expected:
            raise ValueError('digest mismatch: ' + str(path))
    relation = json.loads(witness.read_text())
    indices = relation['generator_indices_zero_based']
    variables = relation['relation_variable_indices']
    if (relation['constant'] != 1 or len(variables) != 2 or
            not (0 <= variables[0] < variables[1]) or
            len(indices) != len(set(indices))):
        raise ValueError('unexpected affine witness shape')
    n, original_polys = read_sys(original)
    sliced_n, sliced_polys = read_binary(sliced)
    if (n != relation['variables'] or sliced_n != n - 1 or
            len(original_polys) != len(sliced_polys)):
        raise ValueError('system or witness dimensions disagree')
    affine = (0, 1 << variables[0])
    variable = variables[1]
    for index, (source, actual) in enumerate(zip(original_polys, sliced_polys)):
        if substitute(source, variable, affine) != actual:
            raise ValueError('sliced generator %d disagrees' % index)
    relation_poly = set()
    for index in indices:
        if not 0 <= index < len(original_polys):
            raise ValueError('witness generator index out of range')
        relation_poly.symmetric_difference_update(original_polys[index])
    if relation_poly != {0, 1 << variables[0], 1 << variable}:
        raise ValueError('witness relation disagrees with original system')
    return {'status': 'valid_sliced_generator_export', 'variables': sliced_n,
            'generators': len(sliced_polys), 'terms': sum(map(len, sliced_polys)),
            'original_sha256': expected_original, 'sliced_sha256': expected_sliced,
            'witness_sha256': expected_witness}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('sliced', type=Path)
    parser.add_argument('witness', type=Path)
    parser.add_argument('--expect-original-sha256', required=True)
    parser.add_argument('--expect-sliced-sha256', required=True)
    parser.add_argument('--expect-witness-sha256', required=True)
    args = parser.parse_args()
    try:
        result = check(args.original, args.sliced, args.witness,
                       args.expect_original_sha256, args.expect_sliced_sha256,
                       args.expect_witness_sha256)
    except (OSError, KeyError, TypeError, ValueError, struct.error) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
