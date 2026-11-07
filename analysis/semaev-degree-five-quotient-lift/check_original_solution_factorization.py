#!/usr/bin/env python3
"""Check named original solutions and their factorization through a D4 map.

This checker does not enumerate solutions. Its count-file premise must come
from a separately pinned exact counter run on the identical named input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from seed_kernel import SeedKernel

ORIGINAL_GENERATOR_SHA256 = '83042965fc5cdc78ffe76b79092b9daff1307161aba35476b031bb64caa9ac7b'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def require_hash(path, expected):
    actual = sha(path)
    if actual != expected:
        raise ValueError(f'digest mismatch: {path}')
    return actual


def read_pairs(path, k, expected):
    points = []
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 2 or any(not x or any(c not in '0123456789abcdef' for c in x)
                                    for x in fields):
            raise ValueError('invalid ordered-pair line')
        a, b = (int(x, 16) for x in fields)
        if a >= 1 << k or b >= 1 << k:
            raise ValueError('pair lies outside fixed polynomial basis')
        points.append(a | (b << k))
    if len(points) != expected or len(set(points)) != expected:
        raise ValueError('ordered-pair list does not contain distinct expected points')
    return points


def check_generators(path, points, nvars, expected_generators):
    with Path(path).open('rb') as stream:
        if stream.read(8) != b'SLCGEN01':
            raise ValueError('wrong independent-generator magic')
        head = stream.read(16)
        if len(head) != 16:
            raise ValueError('truncated generator header')
        variables, generators = struct.unpack('<QQ', head)
        if variables != nvars or generators != expected_generators:
            raise ValueError('wrong generator dimensions')
        terms = 0
        for _ in range(generators):
            raw = stream.read(8)
            if len(raw) != 8:
                raise ValueError('truncated generator length')
            count, = struct.unpack('<Q', raw)
            if count > 1 << 20:
                raise ValueError('unreasonable generator length')
            data = stream.read(8 * count)
            if len(data) != 8 * count:
                raise ValueError('truncated generator')
            masks = struct.unpack('<' + str(count) + 'Q', data)
            if len(set(masks)) != count or any(m >= 1 << nvars for m in masks):
                raise ValueError('invalid generator monomials')
            for point in points:
                if sum((m & point) == m for m in masks) & 1:
                    raise ValueError('listed point fails an independently exported generator')
            terms += count
        if stream.read(1):
            raise ValueError('trailing generator bytes')
    return terms


def check_factorization(seed_path, expected_sha, points, nvars):
    seed = SeedKernel(seed_path, expected_sha)
    try:
        if seed.variables != nvars or seed.degree != 4:
            raise ValueError('wrong D4 quotient dimensions')
        masks = [None] * len(seed.index)
        for mask, index in seed.index.items():
            masks[index] = mask
        reps = [None] * seed.codimension
        seed.stream.seek(seed.rows_offset)
        for mask in masks:
            row = seed.stream.read(seed.row_bytes)
            if len(row) != seed.row_bytes:
                raise ValueError('truncated D4 map')
            image = int.from_bytes(row, 'little')
            if image >= 1 << seed.codimension:
                raise ValueError('D4 map has out-of-range quotient bit')
            if image and image & (image - 1) == 0:
                q = image.bit_length() - 1
                if reps[q] is None:
                    reps[q] = mask
        if any(mask is None for mask in reps):
            raise ValueError('map lacks a complete unit-row basis')
        functionals = [sum(1 << q for q, mask in enumerate(reps)
                           if mask & point == mask) for point in points]
        seed.stream.seek(seed.rows_offset)
        for mask in masks:
            row = seed.stream.read(seed.row_bytes)
            if len(row) != seed.row_bytes:
                raise ValueError('truncated D4 map')
            image = int.from_bytes(row, 'little')
            for point, functional in zip(points, functionals):
                if ((image & functional).bit_count() & 1) != (mask & point == mask):
                    raise ValueError('solution evaluation does not factor through D4 map')
        return {'columns': len(masks), 'codimension': seed.codimension,
                'checked_pairs': len(points), 'factorization': True}
    finally:
        seed.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--generator', type=Path, required=True)
    p.add_argument('--generator-sha256', required=True)
    p.add_argument('--pairs', type=Path, required=True)
    p.add_argument('--pairs-sha256', required=True)
    p.add_argument('--count-stdout', type=Path, required=True)
    p.add_argument('--count-sha256', required=True)
    p.add_argument('--seed', type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text())
    rec = plan['record']
    k = rec['k']
    if (rec['n'] != 51 or rec['name'] != 'fresh-n51-poly-00' or
            rec['basis'] != 'poly' or
            [int(x, 16) for x in rec['V_basis_hex']] != [1 << j for j in range(k)] or
            plan['expected_exact_solutions'] != 6):
        raise ValueError('not the fixed original n51 polynomial-00 input')
    if a.generator_sha256 != ORIGINAL_GENERATOR_SHA256:
        raise ValueError('not the independently checked original generators')
    require_hash(a.generator, a.generator_sha256)
    require_hash(a.pairs, a.pairs_sha256)
    require_hash(a.count_stdout, a.count_sha256)
    if a.count_stdout.read_text().strip() != '6':
        raise ValueError('separate counter did not return six')
    points = read_pairs(a.pairs, k, 6)
    terms = check_generators(a.generator, points, 2 * k, 51)
    result = check_factorization(a.seed, plan['seed_sha256'], points, 2 * k)
    result.update(schema='semaev.original-solution-factorization/v1',
                  named_input=rec['name'], generator_terms=terms,
                  generator_sha256=a.generator_sha256, pairs_sha256=a.pairs_sha256,
                  count_sha256=a.count_sha256, seed_sha256=plan['seed_sha256'])
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
