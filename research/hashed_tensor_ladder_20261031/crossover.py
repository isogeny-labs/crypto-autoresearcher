#!/usr/bin/env python3
"""Closed-form necessary condition for counting-based hashed-factor-base index calculus to beat rho.

Model, every hidden constant set to 1: a relation oracle counts a Boolean network with N variables in time
2^(N / sqrt(log2 N)); m slots; about 2^(ell/m) relations are needed, so the per-attempt exponent must stay
below (1/2 - 1/m) * ell to beat rho = 2^(ell/2). Full ell-bit coordinate unknowns give N >= m * ell. Then

    m*ell / sqrt(log2(m*ell)) < (1/2 - 1/m) * ell     <=>     sqrt(log2(m*ell)) > 2 m^2 / (m - 2),

which depends only on L = log2(m*ell). The bound 2m^2/(m-2) is minimised at m = 4 (value 16), so
log2(4*ell) > 256 and ell > 2^254. This is a necessary condition for this algorithm family at unit constants,
not a proof that no other mechanism works.
"""
import math


def sqrt_threshold(m):
    """Minimum sqrt(log2(m*ell)) needed to beat rho; only defined for m >= 3."""
    if m < 3:
        raise ValueError("m = 2 has a per-attempt budget below one operation")
    return 2.0 * m * m / (m - 2)


def min_log2_ell(m):
    """log2 of the smallest ell at which the unit-constant bound can beat rho with N = m*ell."""
    return sqrt_threshold(m) ** 2 - math.log2(m)


def beats_rho_unit_constants(log2_ell, m):
    """True iff the necessary condition holds for ell = 2**log2_ell (log domain: ell may be astronomically large)."""
    return math.sqrt(log2_ell + math.log2(m)) > sqrt_threshold(m)


def best_m(candidates=range(3, 65)):
    return min(candidates, key=sqrt_threshold)


if __name__ == "__main__":
    print(" m   sqrt-threshold   min log2(ell)")
    for m in range(3, 13):
        print(f"{m:2d}   {sqrt_threshold(m):12.3f}   {min_log2_ell(m):12.1f}")
    m = best_m()
    print(f"best m = {m}: ell > 2^{min_log2_ell(m):.0f}")
