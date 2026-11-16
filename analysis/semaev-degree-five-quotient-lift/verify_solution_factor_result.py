#!/usr/bin/env python3
"""Independent replay of a positive factorization or negative kernel witness.

This implementation does not import the producer, SeedKernel, or their parsers.
It reopens the original map and equations and checks the saved result directly.
"""
import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import struct


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as file:
        for chunk in iter(lambda: file.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def read_points(path, k, count):
    lines = Path(path).read_text().splitlines()
    if len(lines) != count:
        raise ValueError('wrong number of ordered pairs')
    points = []
    for line in lines:
        parts = line.split()
        if len(parts) != 2 or any(not p or any(c not in '0123456789abcdef' for c in p)
                                  for p in parts):
            raise ValueError('malformed ordered pair')
        a, b = [int(p, 16) for p in parts]
        if a >= 1 << k or b >= 1 << k:
            raise ValueError('pair outside fixed polynomial basis')
        points.append(a | (b << k))
    if len(set(points)) != count:
        raise ValueError('duplicate ordered pair')
    return points


def verify_roots(path, points, variables, expected_generators):
    with Path(path).open('rb') as file:
        if file.read(8) != b'SLCGEN01':
            raise ValueError('invalid generator magic')
        head = file.read(16)
        if len(head) != 16:
            raise ValueError('truncated generator header')
        n, generators = struct.unpack('<QQ', head)
        if n != variables or generators != expected_generators:
            raise ValueError('generator dimensions differ')
        for _ in range(generators):
            raw = file.read(8)
            if len(raw) != 8:
                raise ValueError('truncated generator length')
            length, = struct.unpack('<Q', raw)
            if length > 1048576:
                raise ValueError('generator too long')
            raw = file.read(8 * length)
            if len(raw) != 8 * length:
                raise ValueError('truncated generator terms')
            terms = struct.unpack('<' + str(length) + 'Q', raw)
            if len(set(terms)) != length or any(m >= 1 << n for m in terms):
                raise ValueError('invalid generator terms')
            for point in points:
                value = 0
                for m in terms:
                    value ^= int(m & point == m)
                if value:
                    raise ValueError('listed point is not a root')
        if file.read(1):
            raise ValueError('trailing generator data')


def map_header(file, variables, degree, columns, codimension):
    head = file.read(32)
    if len(head) != 32 or struct.unpack('<4q', head) != (variables, degree, columns, codimension):
        raise ValueError('wrong quotient-map header')
    if columns != sum(comb(variables, j) for j in range(degree + 1)):
        raise ValueError('wrong monomial universe')
    raw = file.read(8 * columns)
    if len(raw) != 8 * columns:
        raise ValueError('truncated monomial array')
    masks = struct.unpack('<' + str(columns) + 'Q', raw)
    if len(set(masks)) != columns or any(m >= 1 << variables or m.bit_count() > degree
                                         for m in masks):
        raise ValueError('invalid monomial array')
    row_bytes = 8 * ((codimension + 63) // 64)
    if file.seek(0, 2) != 32 + 8 * columns + columns * row_bytes:
        raise ValueError('wrong quotient-map length')
    file.seek(32 + 8 * columns)
    return masks, row_bytes


def replay_map(path, points, result, variables, degree, columns, codimension):
    with Path(path).open('rb') as file:
        masks, row_bytes = map_header(file, variables, degree, columns, codimension)
        offset = file.tell()
        if result['factorization'] is True:
            reps = [None] * codimension
            for mask in masks:
                image = int.from_bytes(file.read(row_bytes), 'little')
                if image >= 1 << codimension:
                    raise ValueError('out-of-range quotient bit')
                if image and image & (image - 1) == 0:
                    q = image.bit_length() - 1
                    if reps[q] is None:
                        reps[q] = mask
            if any(m is None for m in reps):
                raise ValueError('missing quotient unit representative')
            weights = [sum(1 << q for q, mask in enumerate(reps) if mask & s == mask)
                       for s in points]
            file.seek(offset)
            for mask in masks:
                image = int.from_bytes(file.read(row_bytes), 'little')
                for s, w in zip(points, weights):
                    if ((image & w).bit_count() & 1) != int(mask & s == mask):
                        raise ValueError('positive factorization contradicted by map row')
            return 'factorization_verified'
        if result['factorization'] is not False:
            raise ValueError('missing Boolean factorization verdict')
        point = int(result['witness_point_hex'], 16)
        if point not in points:
            raise ValueError('witness point is not in verified root list')
        texts = result['kernel_witness_terms_hex']
        if not texts or len(texts) != len(set(texts)):
            raise ValueError('missing or duplicate kernel witness terms')
        lookup = {m: j for j, m in enumerate(masks)}
        image_sum = 0
        value = 0
        for text in texts:
            mask = int(text, 16)
            if mask not in lookup:
                raise ValueError('witness term outside D4 monomial universe')
            file.seek(offset + lookup[mask] * row_bytes)
            image_sum ^= int.from_bytes(file.read(row_bytes), 'little')
            value ^= int(mask & point == mask)
        if image_sum or value != 1:
            raise ValueError('kernel witness fails independent replay')
        return 'seed_nonvanishing_witness'


def main():
    p = argparse.ArgumentParser()
    for name in ('plan', 'result', 'pairs', 'count_stdout', 'generator', 'seed'):
        p.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text())
    result = json.loads(a.result.read_text())
    rec = plan['record']
    k = rec['k']
    if (rec['name'] != 'fresh-n51-poly-00' or rec['n'] != 51 or k != 26 or
            [int(v, 16) for v in rec['V_basis_hex']] != [1 << j for j in range(k)] or
            plan['expected_exact_solutions'] != 6):
        raise ValueError('wrong fixed named input')
    seed_sha = digest(a.seed)
    if (seed_sha != plan['hashes'][str(a.seed)] or
            digest(a.generator) != plan['hashes'][str(a.generator)] or
            digest(a.pairs) != result['pairs_sha256'] or
            digest(a.count_stdout) != result['count_sha256'] or
            a.count_stdout.read_text().strip() != '6'):
        raise ValueError('input hash or exact count mismatch')
    if (result['named_input'] != rec['name'] or
            result['seed_sha256'] != seed_sha or
            result['generator_sha256'] != plan['hashes'][str(a.generator)]):
        raise ValueError('producer result names different inputs')
    points = read_points(a.pairs, k, 6)
    verify_roots(a.generator, points, 52, 51)
    if result['checked_pairs'] != 6 or result['columns'] != 294204 or result['codimension'] != 45615:
        raise ValueError('result dimensions differ from original D4 map')
    verdict = replay_map(a.seed, points, result, 52, 4, 294204, 45615)
    print(json.dumps({'schema': 'semaev.solution-factor-independent-review/v1',
                      'verified': True, 'verdict': verdict,
                      'result_sha256': digest(a.result), 'seed_sha256': seed_sha},
                     sort_keys=True))


if __name__ == '__main__':
    main()
