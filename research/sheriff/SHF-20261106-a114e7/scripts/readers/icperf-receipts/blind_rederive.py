#!/usr/bin/env python3
"""Blind re-derivation for sheriff case SHF-20261106-a114e7, joint ICV (icperf-receipts).

Written from the STATEMENT text of the two frozen specifications only:
  experiments/EXP-ICPERF-284bc4/specification.yaml  /experiment/online_time_model, /bsgs_probe_count, /controls
  experiments/EXP-ICPERF-283a70/specification.yaml  /experiment/sampler, /controls, DESC-1, DESC-2
No producer code (run.py, check.py, analysis.md, reports, review/*) was read before this file was written.

Proves-too-much controls are built in: inputs whose conclusion is known false
(perturbed prices, wrong samplers, off-by-one median, wrong shift directions)
must NOT reproduce the preregistered integers.
"""
from fractions import Fraction as F
import json
import sys

# ---------------------------------------------------------------- EXP-ICPERF-284bc4
def icperf_284(c_probe=370, c_state=2100, c_step=40, bl_num=21, bl_den=10, states=10,
               precomp=None, cells=((1000, 2), (4000, 2), (1000, 4))):
    if precomp is None:
        precomp = F(states * c_state, c_step)
    precomp = F(precomp)
    price = F(c_probe * c_state * bl_den, bl_num * c_step ** 2)
    out = {"precomputation_steps": str(precomp), "price_ratio": [price.numerator, price.denominator], "cells": []}
    for r, A in cells:
        probes = F(r, A * states)
        bl_steps = F(bl_num * r, 1) / (bl_den * A * precomp)
        bl_ns = bl_steps * c_step
        ic_ns = probes * c_probe
        ratio = ic_ns / bl_ns
        out["cells"].append({
            "r": r, "A": A,
            "probes": str(probes), "bl_steps": str(bl_steps),
            "ic_online_ns": str(ic_ns), "bl_online_ns": str(bl_ns),
            "online_ratio": [ratio.numerator, ratio.denominator],
            "all_integer": all(x.denominator == 1 for x in (probes, bl_steps, ic_ns, bl_ns)),
            "bsgs_enumerated": bsgs_enum(r // A if r % A == 0 else None, states),
        })
    out["ratios_agree"] = all(tuple(c["online_ratio"]) == (price.numerator, price.denominator) for c in out["cells"])
    return out


def bsgs_enum(m, states):
    """Max over targets t in Z/m of table lookups up to and including the first hit.
    Baby steps {0..states-1}; each giant step subtracts `states` (mod m)."""
    if m is None:
        return None
    table = set(range(states))
    worst = 0
    for t in range(m):
        x, k = t, 0
        while True:
            k += 1
            if x % m in table:
                break
            x = (x - states) % m
            if k > m + 1:  # no hit ever: report as None (cannot happen when states >= 1)
                return None
        worst = max(worst, k)
    return worst


# ---------------------------------------------------------------- EXP-ICPERF-283a70
M32 = 0xFFFFFFFF


def xorshift_step(x, a, b, c):
    x ^= (x << a) & M32
    x ^= (x >> b)
    x ^= (x << c) & M32
    return x & M32


def geometric_sample(seed=20261017, p_den=50, n=64, shifts=(13, 17, 5), support_min=1):
    x = seed
    draws = []
    for _ in range(n):
        tests = 0
        while True:
            x = xorshift_step(x, *shifts)
            tests += 1
            if x % p_den == 0:
                break
            if tests > 10 ** 7:
                raise RuntimeError("no success in 1e7 tests")
        draws.append(tests - (1 - support_min))  # support_min 0 -> failures before success
    s = sorted(draws)
    med32, med33 = s[31], s[32]
    ssum = sum(draws)
    ssq = sum(d * d for d in draws)
    cv_num = n * ssq - ssum * ssum
    cv_den = ssum * ssum
    cv_sq = F(cv_num, cv_den)
    mr = F(med32 * n, ssum)
    return {
        "draws": draws,
        "sample_sum": ssum, "sum_squares": ssq,
        "median": med32, "median_split": med32 != med33,
        "cv_sq_num": cv_num, "cv_sq_den": cv_den,
        "cv_in_band": F(81, 100) <= cv_sq <= F(121, 100),
        "median_ratio_num": med32 * n, "median_ratio_den": ssum,
        "median_ratio_reduced": [mr.numerator, mr.denominator],
        "median_ratio_in_band": F(3, 5) <= mr <= F(4, 5),
        "exact_match": (ssum, ssq, med32) == (2943, 289567, 28),
    }


def main():
    res = {}
    res["284bc4_primary"] = icperf_284()
    res["284bc4_NEG1_c_probe_371"] = icperf_284(c_probe=371)
    res["284bc4_NEG2_precomp_10"] = icperf_284(precomp=10)
    # proves-too-much controls (conclusion known false: must NOT give 925/4 everywhere)
    res["284bc4_PTM_c_state_2101"] = icperf_284(c_state=2101)
    res["284bc4_PTM_bl_21_over_11"] = icperf_284(bl_den=11)
    res["284bc4_PTM_c_step_41"] = icperf_284(c_step=41)
    res["284bc4_PTM_states_11"] = icperf_284(states=11)

    g = {}
    g["primary"] = geometric_sample()
    g["CTL1_wrong_triple_1_2_14"] = geometric_sample(shifts=(1, 2, 14))
    g["CTL2_support_zero"] = geometric_sample(support_min=0)
    # proves-too-much controls
    g["PTM_seed_plus_1"] = geometric_sample(seed=20261018)
    g["PTM_triple_13_17_5_reversed_5_17_13"] = geometric_sample(shifts=(5, 17, 13))
    g["PTM_p_den_49"] = geometric_sample(p_den=49)
    g["PTM_n_63"] = geometric_sample(n=63) if False else None  # n change shifts median index; not meaningful, skipped
    g = {k: v for k, v in g.items() if v is not None}
    for k, v in g.items():
        v["draws_head"] = v["draws"][:8]
    res["283a70"] = {k: {kk: vv for kk, vv in v.items()} for k, v in g.items()}
    json.dump(res, sys.stdout, indent=1, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
