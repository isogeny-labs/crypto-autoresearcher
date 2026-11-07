#!/usr/bin/env python3
"""Exact GF(2) rank screen for the n=47, k=23 polynomial factor space.

This is a small symbolic linear-algebra check, not a fall-degree experiment.
"""
import json

N = 47
MODULUS = (1 << 47) | (1 << 5) | 1


def square_mod(value):
    doubled = sum(1 << (2 * i) for i in range(N) if (value >> i) & 1)
    while doubled.bit_length() > N:
        doubled ^= MODULUS << (doubled.bit_length() - N - 1)
    return doubled


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def main():
    v = [1 << i for i in range(23)]
    p = [1 << i for i in range(45)]
    image = [square_mod(x) ^ x for x in p]
    quadratic_rank = rank(image)
    affine_linear_rank = rank(image + [square_mod(x) for x in v]) - quadratic_rank
    result = {
        "n": N,
        "k": 23,
        "modulus_hex": hex(MODULUS),
        "dim_product_space": rank(p),
        "quadratic_rank": quadratic_rank,
        "quadratic_null_combinations": N - quadratic_rank,
        "affine_linear_rank": affine_linear_rank,
    }
    assert result == {
        "n": 47, "k": 23, "modulus_hex": "0x800000000021",
        "dim_product_space": 45, "quadratic_rank": 44,
        "quadratic_null_combinations": 3, "affine_linear_rank": 1,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
