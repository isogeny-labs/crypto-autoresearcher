#!/usr/bin/env python3
"""Compute the exact affine part of degree-three Boolean closure for named plans.

Rows use degree-then-index monomial order. A row with a degree-at-most-two
leading monomial is a genuine low-degree fall, so its variable products must be
inserted; processing these rows to exhaustion is precisely W_3's closure rule.
"""
import hashlib
import json
import sys
from collections import deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis/semaev-m2-last-fall-degree/verify'))
from cert_check import descend


def analyze(name):
    path = (ROOT / 'analysis/semaev-degree-five-quotient-lift' / name).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('plan path escapes repository')
    record = json.loads(path.read_text())['record']
    n, polys = descend(record['n'], int(record['modulus_hex'], 16),
                       record['a2'], int(record['a6_hex'], 16),
                       int(record['z_hex'], 16),
                       [int(v, 16) for v in record['V_basis_hex']])
    masks = [0] + [1 << i for i in range(n)]
    masks += [(1 << i) | (1 << j) for i, j in combinations(range(n), 2)]
    masks += [(1 << i) | (1 << j) | (1 << k)
              for i, j, k in combinations(range(n), 3)]
    pos = {m: j for j, m in enumerate(masks)}
    low_end = 1 + n + n * (n - 1) // 2
    pivots = {}
    todo = deque()
    seen = 0

    def insert(row):
        nonlocal seen
        while row:
            j = row.bit_length() - 1
            if j in pivots:
                row ^= pivots[j]
            else:
                pivots[j] = row
                seen += 1
                if j < low_end:
                    todo.append(row)
                break

    for p in polys:
        insert(sum(1 << pos[m] for m in p))
    while todo:
        row = todo.popleft()
        for variable in range(n):
            x = 1 << variable
            product = 0
            tmp = row
            while tmp:
                bit = tmp & -tmp
                tmp ^= bit
                product ^= 1 << pos[masks[bit.bit_length() - 1] | x]
            insert(product)
    affine = [row for j, row in pivots.items() if j <= n]
    out = []
    for row in affine:
        support = []
        while row:
            bit = row & -row
            row ^= bit
            support.append(masks[bit.bit_length() - 1])
        out.append(support)
    return {
        'schema': 'semaev.affine-w3-check/v1',
        'plan': str(path.relative_to(ROOT)),
        'plan_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'descent_source_sha256': hashlib.sha256(
            (ROOT / 'analysis/semaev-m2-last-fall-degree/verify/cert_check.py').read_bytes()
        ).hexdigest(),
        'variables': n,
        'w3_rank': seen,
        'low_degree_rank': sum(j < low_end for j in pivots),
        'affine_rank': len(affine),
        'affine_supports': out,
    }


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(json.dumps(analyze(name), sort_keys=True), flush=True)
