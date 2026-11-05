"""Finite-group development checks for P1/P2. Not a Lean or execution proof."""
from fractions import Fraction
from itertools import product


def sum_fibres(modulus, base, arity):
    if modulus <= 0 or arity < 1:
        raise ValueError('positive modulus and arity required')
    if len(base) != len(set(base)) or any(x < 0 or x >= modulus for x in base):
        raise ValueError('base must be distinct actual group elements')
    counts = [0] * modulus
    for points in product(base, repeat=arity):
        counts[sum(points) % modulus] += 1
    return counts


def collection_floor(modulus, base_size, arity, successes, per_query=1, setup=0):
    if min(modulus, arity, per_query) <= 0 or min(base_size, successes, setup) < 0:
        raise ValueError('invalid model parameters')
    if base_size > modulus:
        raise ValueError('base cannot exceed the group')
    if successes == 0:
        return Fraction(setup)
    if base_size == 0:
        raise ValueError('positive successes impossible from an empty base')
    return Fraction(setup) + Fraction(per_query*successes*modulus,
                                     min(modulus, base_size**arity))
