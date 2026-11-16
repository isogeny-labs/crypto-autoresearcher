#!/usr/bin/env python3
"""Deterministic degree-five evaluation-map control for the native checker."""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import struct

N, D, Q = 8, 5, 73
ROOT = Path(__file__).resolve().parent


def masks_through(degree):
    return [sum(1 << j for j in choice)
            for size in range(degree + 1)
            for choice in combinations(range(N), size)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    points = sorted(masks_through(3), key=lambda m: (bin(m).count('1'), m))[:Q]
    assert len(points) == Q and len(set(points)) == Q
    masks = sorted(masks_through(D), key=lambda m: (-bin(m).count('1'), m))
    assert len(masks) == 219
    cert = ROOT / 'd5-checker-fixture.bin'
    gens = ROOT / 'd5-checker-fixture-generators.bin'
    with cert.open('wb') as out:
        out.write(struct.pack('<4q', N, D, len(masks), Q))
        out.write(struct.pack('<' + str(len(masks)) + 'Q', *masks))
        for mask in masks:
            value = sum(1 << j for j, point in enumerate(points)
                        if mask & point == mask)
            out.write(value.to_bytes(16, 'little'))
    # x0*x1*x2*x3 vanishes on every selected point (weight at most three).
    with gens.open('wb') as out:
        out.write(b'SLCGEN01')
        out.write(struct.pack('<QQQQ', N, 1, 1, 15))
    print(json.dumps({'certificate_sha256': sha(cert),
                      'certificate_bytes': cert.stat().st_size,
                      'generators_sha256': sha(gens),
                      'generators_bytes': gens.stat().st_size,
                      'expected': {'degree': D, 'variables': N,
                                   'codimension_lower_bound': Q,
                                   'generators': 1,
                                   'low_kernel_dimension': 90}}, sort_keys=True))


if __name__ == '__main__':
    main()
