#!/usr/bin/env python3
"""Small exact reference checker for the compact D5 quotient criterion.

This is deliberately limited to tiny instances. It supplies a correctness
oracle for a future bounded frontier checker; it is not the n47 verifier.
"""

from functools import lru_cache
from itertools import combinations

from check_quotient_closure_factorized import check_closure_factorized


def popcount(value):
    return bin(value).count('1')


def check_factorization(first, second):
    """Check ker(first) is contained in ker(second) over F2."""
    if len(first) != len(second):
        raise ValueError('factorization column count')
    pivots = {}
    for a, b in zip(first, second):
        while a:
            bit = a.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = (a, b)
                break
            a ^= pivots[bit][0]
            b ^= pivots[bit][1]
        else:
            if b:
                return False
    return True


class ProvisionalMap:
    def __init__(self, n, degree, masks, rows, codim):
        if n > 10 or degree < 1 or degree >= n or not 1 <= codim <= len(masks):
            raise ValueError('reference checker only accepts tiny instances')
        expected = tuple(sorted((sum(1 << i for i in part)
                                 for d in range(degree + 1)
                                 for part in combinations(range(n), d)),
                                key=lambda m: (-popcount(m), m)))
        if tuple(masks) != expected:
            raise ValueError('invalid seed monomial order or universe')
        if len(rows) != len(masks) or any(r < 0 or r >> codim for r in rows):
            raise ValueError('invalid seed rows')
        self.n, self.degree, self.codim = n, degree, codim
        self.masks, self.rows = tuple(masks), tuple(rows)
        self.beta = dict(zip(masks, rows))
        self.reps = {}
        for q in range(codim):
            candidates = [i for i, r in enumerate(rows) if r == 1 << q]
            if not candidates:
                raise ValueError('seed lacks unit representative')
            self.reps[q] = masks[max(candidates)]
        rep_index = {masks.index(m): q for q, m in self.reps.items()}
        for index, row in enumerate(rows):
            if index in rep_index:
                continue
            if any(masks.index(self.reps[q]) <= index
                   for q in range(codim) if row >> q & 1):
                raise ValueError('nontriangular seed')
        high = [sum(1 << i for i in part)
                for part in combinations(range(n), degree + 1)]
        # The native producer enumerates equal-degree masks in ascending
        # Gosper order, then rewrites from the last high column backwards.
        self.high = sorted(high)
        self.high_index = {m: i for i, m in enumerate(self.high)}
        reps = set(self.reps.values())
        self.standard = [m for m in self.high if all(
            (m ^ (1 << i)) in reps for i in range(n) if m >> i & 1)]
        self.standard_index = {m: i for i, m in enumerate(self.standard)}
        self.work = len(self.standard) + codim

    @lru_cache(maxsize=None)
    def phi(self, mask):
        if popcount(mask) <= self.degree:
            return self.beta[mask] << len(self.standard)
        if mask in self.standard_index:
            return 1 << self.standard_index[mask]
        options = [(mask ^ (1 << i), i) for i in range(self.n)
                   if mask >> i & 1 and (mask ^ (1 << i)) not in self.reps.values()]
        if not options:
            raise ValueError('missing high rewrite')
        divisor, variable = min(options)
        result = 0
        for q in range(self.codim):
            if self.beta[divisor] >> q & 1:
                target = self.reps[q] | (1 << variable)
                if (popcount(target) == self.degree + 1 and
                        self.high_index[target] <= self.high_index[mask]):
                    raise ValueError('cyclic high rewrite')
                result ^= self.phi(target)
        return result


def check_compact(provisional, h_rows, generators):
    """Return the rank and constant image after checking the three conditions."""
    if len(h_rows) != provisional.work:
        raise ValueError('compact matrix row count')
    if any(r < 0 for r in h_rows):
        raise ValueError('negative compact row')
    check_closure_factorized(provisional.n, provisional.degree,
                             provisional.masks, provisional.rows)

    def image(mask):
        vector = provisional.phi(mask)
        value = 0
        while vector:
            bit = (vector & -vector).bit_length() - 1
            value ^= h_rows[bit]
            vector &= vector - 1
        return value

    if not image(0):
        raise ValueError('constant killed')
    for generator in generators:
        if any(popcount(mask) > provisional.degree for mask in generator):
            raise ValueError('generator exceeds seed degree')
        if _xor(provisional.beta[mask] for mask in generator):
            raise ValueError('generator not killed by seed')
    for mask, beta in provisional.beta.items():
        for i in range(provisional.n):
            bit = 1 << i
            relation = image(mask | bit)
            for q in range(provisional.codim):
                if beta >> q & 1:
                    relation ^= image(provisional.reps[q] | bit)
            if relation:
                raise ValueError('initial relation not killed')
    low_rows = [image(provisional.reps[q]) for q in range(provisional.codim)]
    for i in range(provisional.n):
        products = [image(provisional.reps[q] | (1 << i))
                    for q in range(provisional.codim)]
        if not check_factorization(low_rows, products):
            raise ValueError('low-coordinate closure fails')
    pivots = {}
    for row in h_rows:
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return {'rank': len(pivots), 'constant_image': image(0)}


def _xor(values):
    value = 0
    for item in values:
        value ^= item
    return value
