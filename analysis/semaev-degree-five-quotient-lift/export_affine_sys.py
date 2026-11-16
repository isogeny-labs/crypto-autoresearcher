#!/usr/bin/env python3
"""Export an affine-sliced .sys from a saved original Boolean system.

The source .sys and affine witness are hash-bound. This path does not use
field descent or the native sliced-generator exporter.
"""
import argparse
import hashlib
import json
from pathlib import Path
import os


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_original(path):
    with path.open() as source:
        n, count = map(int, source.readline().split())
        rows = []
        for line in source:
            if not line.strip():
                continue
            words = line.split()
            count_terms = int(words[0])
            terms = [int(word, 16) for word in words[1:]]
            if len(terms) != count_terms or len(terms) != len(set(terms)):
                raise ValueError('invalid original generator')
            rows.append(set(terms))
    if len(rows) != count or any(m >= 1 << n for row in rows for m in row):
        raise ValueError('invalid original system dimensions')
    return n, rows


def restrict(poly, variable, retained_bit):
    bit = 1 << variable
    lower = bit - 1
    def remove(mask):
        return (mask & lower) | (mask >> (variable + 1) << variable)
    result = set()
    for mask in poly:
        if mask & bit:
            base = mask ^ bit
            images = (remove(base), remove(base | retained_bit))
        else:
            images = (remove(mask),)
        for image in images:
            if image in result:
                result.remove(image)
            else:
                result.add(image)
    return result


def export(original, witness, output, expected_original, expected_witness):
    if sha256(original) != expected_original or sha256(witness) != expected_witness:
        raise ValueError('input digest mismatch')
    if output.exists() or output.with_name(output.name + '.partial').exists():
        raise FileExistsError(output)
    n, polys = read_original(original)
    record = json.loads(witness.read_text())
    indices = record['generator_indices_zero_based']
    a, b = record['relation_variable_indices']
    if (record['variables'] != n or record['constant'] != 1 or
            not 0 <= a < b < n or len(indices) != len(set(indices)) or
            any(not 0 <= i < len(polys) for i in indices)):
        raise ValueError('invalid affine witness')
    relation = set()
    for i in indices:
        relation.symmetric_difference_update(polys[i])
    if relation != {0, 1 << a, 1 << b}:
        raise ValueError('witness relation disagrees with original system')
    sliced = [restrict(poly, b, 1 << a) for poly in polys]
    partial = output.with_name(output.name + '.partial')
    with partial.open('x') as target:
        target.write('%d %d\n' % (n - 1, len(sliced)))
        for poly in sliced:
            masks = sorted(poly)
            target.write('%d' % len(masks))
            for mask in masks:
                target.write(' %x' % mask)
            target.write('\n')
    os.link(partial, output)
    partial.unlink()
    return {'status': 'exported_affine_sys', 'variables': n - 1,
            'generators': len(sliced), 'terms': sum(map(len, sliced)),
            'input_sha256': expected_original, 'witness_sha256': expected_witness,
            'output_sha256': sha256(output), 'output_bytes': output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('witness', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expect-original-sha256', required=True)
    parser.add_argument('--expect-witness-sha256', required=True)
    args = parser.parse_args()
    try:
        result = export(args.original, args.witness, args.output,
                        args.expect_original_sha256, args.expect_witness_sha256)
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, 'INVALID: %s\n' % error)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
