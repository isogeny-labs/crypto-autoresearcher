"""Independent Boolean truth tables and subset finite differences.

Source only: no module in this directory was imported during authoring.
There is no candidate import, substitution dictionary, binary search or sweep.
"""


def evaluate(polynomial, point, p, n):
    """Evaluate original monomials by explicit Boolean multiplication."""
    total = 0
    for mask, coefficient in polynomial:
        product = 1
        for index in range(n):
            if (mask // (2 ** index)) % 2:
                product *= point[index]
        total = (total + coefficient * product) % p
    return total


def expectation(case):
    p, n, assignment = case['p'], case['n'], case['assignment']
    originals = case['generators']
    tables, residuals, witness = [], [], None
    evaluations = 0
    for depth in range(n + 1):
        level_tables, level_residuals = [], []
        for index, polynomial in enumerate(originals):
            table = []
            for suffix in range(2 ** (n - depth)):
                point = [(assignment // (2 ** i)) % 2 for i in range(depth)]
                point += [(suffix // (2 ** i)) % 2 for i in range(n - depth)]
                table.append(evaluate(polynomial, point, p, n))
                evaluations += 1
            level_tables.append(table)
            if witness is None and table[0] != 0 and all(v == table[0] for v in table):
                witness = [depth, assignment % (2 ** depth), index, table[0]]
            coefficients = {}
            for subset in range(2 ** (n - depth)):
                coefficient = 0
                # Explicit finite difference over all U contained in S.
                for contained in range(2 ** (n - depth)):
                    if contained & ~subset == 0:
                        sign = (-1) ** (subset.bit_count() - contained.bit_count())
                        coefficient += sign * table[contained]
                coefficient %= p
                if coefficient:
                    coefficients[subset * (2 ** depth)] = coefficient
            level_residuals.append(coefficients)
        tables.append(level_tables)
        residuals.append(level_residuals)
    if witness is None:
        if any(table[0] != 0 for table in tables[n]):
            raise AssertionError('oracle full evaluation inconsistency')
    if 'expected' in case and witness != case['expected']:
        raise AssertionError('registered control disagrees with independent oracle')
    return {'witness': witness, 'tables': tables, 'residuals': residuals,
            'full_evaluations': evaluations}
