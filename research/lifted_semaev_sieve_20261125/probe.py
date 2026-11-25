#!/usr/bin/env python3
"""Exact small-field census for the frozen lifted-S3 sieve protocol."""
import json
from collections import defaultdict

PRIMES = (97, 193)
BOUND = 8
ELLS = (2, 3, 5, 7, 11, 13)


def points(p):
    return [(x, y) for x in range(p) for y in range(p)
            if y * y % p == (x**3 + 7) % p]


def add(P, Q, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    z, w = Q
    if x == z and (y + w) % p == 0:
        return None
    lam = ((3 * x * x) * pow(2 * y, -1, p) if P == Q else
           (w - y) * pow(z - x, -1, p)) % p
    u = (lam * lam - x - z) % p
    return (u, (lam * (x - u) - y) % p)


def s3(x, y, z):
    return (x - y)**2 * z**2 - 2 * ((x + y) * x * y + 14) * z + (x * y)**2 - 28 * (x + y)


def main():
    results = []
    for p in PRIMES:
        pts = points(p)
        base = [P for P in pts if P[0] <= BOUND]
        by_x = defaultdict(list)
        for P in base:
            by_x[P[0]].append(P)
        xs = sorted(by_x)
        counts = {str(ell): dict(hits=0, valid=0, s3_hits=0) for ell in ELLS}
        total = valid = modular = targets_without = 0
        for R in pts:
            target_valid = 0
            for x in xs:
                for y in xs:
                    v = s3(x, y, R[0])
                    is_valid = any(add(P, Q, p) == R for P in by_x[x] for Q in by_x[y])
                    is_modular = (v % p == 0)
                    assert not is_valid or is_modular
                    total += 1
                    valid += is_valid
                    modular += is_modular
                    target_valid += is_valid
                    for ell in ELLS:
                        if v % ell == 0:
                            row = counts[str(ell)]
                            row['hits'] += 1
                            row['valid'] += is_valid
                            row['s3_hits'] += is_modular
            targets_without += (target_valid == 0)
        results.append(dict(p=p, A=0, B=7, group_order=len(pts)+1,
                            factor_base_points=len(base), factor_base_x=len(xs),
                            targets=len(pts), ordered_x_trials=total,
                            verified_relation_hits=valid, modular_s3_hits=modular,
                            targets_without_relation=targets_without, ell=counts))
    print(json.dumps(dict(protocol='lifted-s3-sieve-v1', results=results), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
