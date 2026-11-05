"""Construct explicit bounded-degree repairs using b_i^2-b_i.

Ordinary polynomials use exponent tuples, not masks. The return value
certifies raw - multilinear(raw) = sum_i cofactor_i*(b_i^2-b_i).
No evaluation-only equality is accepted as polynomial equality.
"""


def normalize(raw, prime, variables):
    normal, cofactors = {}, [{} for _ in range(variables)]
    for exponents, coefficient in raw.items():
        if len(exponents) != variables or any(type(e) is not int or e < 0 for e in exponents):
            raise ValueError('bad exponent tuple')
        if type(coefficient) is not int:
            raise ValueError('bad coefficient')
        coefficient %= prime
        exponents = list(exponents)
        for i in range(variables):
            while exponents[i] >= 2:
                cofactor = exponents.copy()
                cofactor[i] -= 2
                key = tuple(cofactor)
                cofactors[i][key] = (cofactors[i].get(key, 0) + coefficient) % prime
                exponents[i] -= 1
        key = tuple(exponents)
        normal[key] = (normal.get(key, 0) + coefficient) % prime
    return ({m: c for m, c in normal.items() if c},
            [{m: c for m, c in q.items() if c} for q in cofactors])


def check_repair(raw, normal, cofactors, prime, variables, cap):
    """Independently expand the identity and verify every ordinary degree."""
    def validate(poly):
        if not isinstance(poly, dict):
            raise ValueError('bad polynomial')
        for e, c in poly.items():
            if (len(e) != variables or any(type(x) is not int or x < 0 for x in e)
                    or type(c) is not int or not 0 < c < prime or sum(e) > cap):
                raise ValueError('invalid ordinary polynomial or degree')
    validate(raw)
    validate(normal)
    if len(cofactors) != variables or any(any(x > 1 for x in e) for e in normal):
        raise ValueError('invalid normal form or cofactors')
    residual = dict(raw)
    def add(e, c):
        residual[e] = (residual.get(e, 0) + c) % prime
        if not residual[e]:
            del residual[e]
    for e, c in normal.items():
        add(e, -c)
    for i, q in enumerate(cofactors):
        validate(q)
        for e, c in q.items():
            if sum(e) + 2 > cap:
                raise ValueError('field-equation product exceeds degree cap')
            square, linear = list(e), list(e)
            square[i] += 2
            linear[i] += 1
            add(tuple(square), -c)
            add(tuple(linear), c)
    if residual:
        raise ValueError('ordinary polynomial repair identity failed')
    return True
