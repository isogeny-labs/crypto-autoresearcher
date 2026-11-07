#!/usr/bin/env python3
"""Independently check a primal affine span witness against a pinned .sys file."""

import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            value.update(block)
    return value.hexdigest()


def check(system, witness):
    proof = json.loads(witness.read_text())
    if proof['schema'] != 'semaev.affine-span-witness/v1':
        raise ValueError('wrong witness schema')
    if digest(system) != proof['input_sys_sha256']:
        raise ValueError('input system digest mismatch')
    with system.open() as stream:
        n, generators = map(int, stream.readline().split())
        if (n, generators) != (proof['variables'], proof['generators']):
            raise ValueError('input system dimensions mismatch')
        equations = []
        for line in stream:
            words = line.split()
            if not words or len(words) != int(words[0]) + 1:
                raise ValueError('malformed equation')
            masks = [int(word, 16) for word in words[1:]]
            if len(set(masks)) != len(masks) or any(mask >= 1 << n for mask in masks):
                raise ValueError('malformed monomial masks')
            equations.append(set(masks))
        if len(equations) != generators:
            raise ValueError('generator count mismatch')
    indices = proof['generator_indices_zero_based']
    variables = proof['relation_variable_indices']
    if (indices != sorted(set(indices)) or not indices or
            any(i < 0 or i >= generators for i in indices) or
            variables != sorted(set(variables)) or not variables or
            any(i < 0 or i >= n for i in variables) or
            proof['constant'] not in (0, 1)):
        raise ValueError('invalid witness indices')
    lhs = set()
    for i in indices:
        lhs.symmetric_difference_update(equations[i])
    rhs = {1 << i for i in variables}
    if proof['constant']:
        rhs.add(0)
    if lhs != rhs:
        raise ValueError('XOR of generators does not equal affine relation')
    return {'accepted': True, 'input_sys_sha256': proof['input_sys_sha256'],
            'witness_sha256': digest(witness), 'generator_terms': len(indices),
            'affine_terms': len(rhs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('system', type=Path)
    parser.add_argument('witness', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.system, args.witness), sort_keys=True))


if __name__ == '__main__':
    main()
