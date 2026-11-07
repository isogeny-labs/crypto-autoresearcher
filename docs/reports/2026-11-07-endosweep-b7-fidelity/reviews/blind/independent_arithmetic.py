#!/usr/bin/env python3
"""Independent integer arithmetic copied solely from blind-input.md."""

import json
from math import gcd, isqrt, prod


def candidate(rows):
    factor_product = prod(base**exponent for base, exponent in rows)
    odd_product = prod(base for base, exponent in rows if exponent % 2)
    square_part = prod(base ** (exponent // 2) for base, exponent in rows)
    discriminant = -odd_product if odd_product % 4 == 3 else -4 * odd_product
    numerator = abs(discriminant) + discriminant % 2
    assert numerator % 4 == 0
    d = numerator // 4
    level = abs(discriminant).bit_length() - 1
    return {
        "factor_product": factor_product,
        "s": odd_product,
        "square_part": square_part,
        "square_decomposition_holds": factor_product == odd_product * square_part**2,
        "s_mod_4": odd_product % 4,
        "D": discriminant,
        "D_mod_2": discriminant % 2,
        "d": d,
        "L": level,
        "lower_power": 2**level,
        "upper_power": 2 ** (level + 1),
        "discriminant_boundary_holds": 2**level <= abs(discriminant) < 2 ** (level + 1),
        "d_lower_power": 2 ** (level - 2),
        "d_boundary_holds": d >= 2 ** (level - 2),
    }


q = 8948962207650232551656602815159153422162609644098354511344597187200057010413552439917934304191956942765446530386427345937963894309923928536070534607816947
t = 133911538952573548431982907995132016398065354869678696041884562716142492272779
h = 1
n = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169
rows = [
    (557, 1),
    (407446053312479106780211110971118243100813139950432927, 1),
    (78712267674886896645620535677555857297633185282989415704617570124138345917365678302464602380771873, 1),
]

N = 4 * q - t * t
result = candidate(rows)
result.update({
    "q_plus_1_minus_t": q + 1 - t,
    "order_identity_holds": q + 1 - t == h * n,
    "t_squared": t * t,
    "N": N,
    "N_positive": N > 0,
    "factor_product_equals_N": result["factor_product"] == N,
    "pairwise_gcds": [gcd(rows[i][0], rows[j][0]) for i in range(3) for j in range(i + 1, 3)],
    "557_prime_by_exhaustive_trial_division": all(557 % k for k in range(2, isqrt(557) + 1)),
    "other_factor_primality": "not tested or assumed",
    "d_equals_q_minus_t_square_adjustment": result["d"] == q - (t * t - 1) // 4,
    "D_above_lower_power": abs(result["D"]) - result["lower_power"],
    "upper_power_above_D": result["upper_power"] - abs(result["D"]),
    "d_above_lower_power": result["d"] - result["d_lower_power"],
})
assert result["order_identity_holds"]
assert result["factor_product_equals_N"]
assert result["discriminant_boundary_holds"]
assert result["d_boundary_holds"]

mutated_rows = [(558, 1), *rows[1:]]
mutated_product = prod(base**exponent for base, exponent in mutated_rows)
mutation = {
    "edit": "557 -> 558 (one digit)",
    "factor_product": mutated_product,
    "factor_product_equals_N": mutated_product == N,
    "factor_product_minus_N": mutated_product - N,
    "residual_equals_other_factor_product": mutated_product - N == rows[1][0] * rows[2][0],
}
assert not mutation["factor_product_equals_N"]
assert mutation["residual_equals_other_factor_product"]

counterexample = candidate([(9, 1), (7, 1)])
counterexample.update({
    "q": 16,
    "t": 1,
    "N": 4 * 16 - 1**2,
    "pairwise_gcd": gcd(9, 7),
    "s_divisible_by_3_squared": counterexample["s"] % 9 == 0,
    "actual_squarefree_part": 7,
    "actual_fundamental_discriminant": -7,
    "D_equals_nine_times_actual_discriminant": counterexample["D"] == 9 * (-7),
})
assert counterexample["factor_product"] == counterexample["N"] == 63
assert counterexample["discriminant_boundary_holds"]
assert counterexample["d_boundary_holds"]
assert counterexample["s_divisible_by_3_squared"]

print(json.dumps({"input_check": result, "one_digit_mutation": mutation,
                  "composite_factor_counterexample": counterexample}, indent=2))
