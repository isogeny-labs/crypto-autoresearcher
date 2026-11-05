#!/usr/bin/env python3
"""Independent, constant-space arithmetic for the blind J3 review."""

import json
from math import isqrt


P, A, B = 1048571, 3, 20
G = (2, 199837)
CLAIMED_N = 1047689


def is_prime(n):
    if n < 2:
        return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def count_points():
    # For prime P, chi(rhs) is 0, +1, or -1; each x gives 1+chi(rhs)
    # affine points. The point at infinity contributes one more.
    blocks = []
    character_sum = 0
    roots_zero = 0
    for lo in range(0, P, 65536):
        hi = min(P, lo + 65536)
        subtotal = 0
        zeros = 0
        for x in range(lo, hi):
            rhs = (x * x * x + A * x + B) % P
            if rhs == 0:
                chi = 0
                zeros += 1
            else:
                residue = pow(rhs, (P - 1) // 2, P)
                assert residue in (1, P - 1)
                chi = 1 if residue == 1 else -1
            subtotal += chi
        character_sum += subtotal
        roots_zero += zeros
        blocks.append({"x_from": lo, "x_to_exclusive": hi,
                       "character_sum": subtotal, "zero_rhs": zeros})
    return 1 + P + character_sum, character_sum, roots_zero, blocks


def add(u, v):
    # None represents the point at infinity.
    if u is None:
        return v
    if v is None:
        return u
    x1, y1 = u
    x2, y2 = v
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if u == v:
        slope = ((3 * x1 * x1 + A) * pow(2 * y1, -1, P)) % P
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, P)) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def mul(k, u):
    result = None
    while k:
        if k & 1:
            result = add(result, u)
        u = add(u, u)
        k >>= 1
    return result


def main():
    assert is_prime(P)
    discriminant_factor = (4 * A**3 + 27 * B**2) % P
    assert discriminant_factor != 0
    n, character_sum, zeros, blocks = count_points()
    assert n == CLAIMED_N
    assert is_prime(n)
    gx, gy = G
    g_rhs = (gx**3 + A * gx + B) % P
    g_y2 = gy**2 % P
    assert g_y2 == g_rhs
    assert mul(n, G) is None
    assert mul(1, G) == G
    m = isqrt(n - 1) + 1  # ceil(sqrt(n))
    assert m == 1024
    assert (m - 1)**2 < n <= m**2
    assert divmod(m * m - 1, m) == (m - 1, m - 1)
    assert divmod(m * m, m) == (m, 0)
    assert mul(m * m, G) == mul(m * m - n, G)
    first_missing_at_narrow_width = mul((m - 1)**2, G)
    assert first_missing_at_narrow_width is not None
    assert first_missing_at_narrow_width != mul(0, G)
    wrapped_boundary_point = mul(m*m, G)
    print(json.dumps({
        "p": P, "p_prime_by_trial_division": True,
        "discriminant_factor_mod_p": discriminant_factor,
        "group_order": n, "group_order_prime_by_trial_division": True,
        "character_sum": character_sum, "zero_rhs_total": zeros,
        "blocks": blocks,
        "G": G, "G_rhs_mod_p": g_rhs, "G_y_squared_mod_p": g_y2,
        "n_times_G_is_infinity": True,
        "m_for_all_canonical_exponents": m,
        "m_minus_one_squared": (m - 1)**2, "m_squared": m**2,
        "m_squared_minus_n": m**2 - n,
        "first_missing_point_at_width_1023": first_missing_at_narrow_width,
        "wrapped_point_at_k_1024_squared": wrapped_boundary_point,
        "boundary_covered_divmod": divmod(m*m - 1, m),
        "boundary_uncovered_divmod": divmod(m*m, m),
        "m_zero_has_no_valid_index_pair": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
