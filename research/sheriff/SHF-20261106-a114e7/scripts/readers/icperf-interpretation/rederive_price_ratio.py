#!/usr/bin/env python3
"""ICR reader, SHF-20261106-a114e7: blind re-derivation for H-ICPERF-2f52d1 from the
hypothesis statement and parameters alone (no producer code, no raw-result.json read),
plus proves-too-much controls and an independent section-5a band.

Inputs (from ledger/hypotheses/H-ICPERF-2f52d1.yaml statement/test_boundary only):
  c_probe 370 ns, c_state 2100 ns, c_step 40 ns, BL constant 21/10, states 10,
  cells (r, A) in {(1000,2), (4000,2), (1000,4)}.
Model (statement + mechanism): precomputation time P = states * c_state, BL walk with
P/c_step precomputation steps answers in (21/10) * (r/A) / P_steps steps; IC answers in
(r/A)/states probes.
"""
from fractions import Fraction as F
import itertools, json, random, sys

C_PROBE, C_STATE, C_STEP = 370, 2100, 40
BL = F(21, 10)
STATES = 10
CELLS = [(1000, 2), (4000, 2), (1000, 4)]
out = {}


def price_ratio(cp, cs, cb, bl=BL):
    return F(cp) * F(cs) / (bl * F(cb) ** 2)


def cell(r, A, cp, cs, cb, states=STATES, bl=BL, pre_steps=None):
    m = F(r, A)
    if pre_steps is None:
        pre_steps = F(states) * F(cs) / F(cb)          # equal precomputation TIME
    probes = m / states
    bl_steps = bl * m / pre_steps
    ic = probes * cp
    blt = bl_steps * cb
    return dict(probes=probes, bl_steps=bl_steps, ic=ic, bl=blt, ratio=ic / blt)


def bsgs_enumerate(m, s):
    # baby steps {0..s-1}; giant step subtracts s; lookups up to and incl. first hit
    counts = [t // s + 1 for t in range(m)]
    return max(counts), F(sum(counts), m)


# --- 1. blind re-derivation -------------------------------------------------------------
pr = price_ratio(C_PROBE, C_STATE, C_STEP)
cells = {f"({r},{A})": cell(r, A, C_PROBE, C_STATE, C_STEP) for r, A in CELLS}
out["blind"] = {
    "price_ratio": str(pr),
    "precomputation_steps": str(F(STATES * C_STATE, C_STEP)),
    "cells": {k: {kk: str(v) for kk, v in c.items()} for k, c in cells.items()},
    "ratios_agree": all(c["ratio"] == pr for c in cells.values()),
    "bsgs": {f"({r},{A})": dict(zip(("max", "mean"), map(str, bsgs_enumerate(r // A, STATES))))
             for r, A in CELLS},
}
# what threshold supports the hypothesis: exact equality to 925/4 (no margin derivable from
# the statement: it is an identity claim, so any tolerance would be post hoc)
out["blind"]["support_condition"] = "price_ratio == 925/4 and every cell ratio == 925/4 and probes == (r/A)/states"
out["blind"]["support_condition_met"] = (pr == F(925, 4) and out["blind"]["ratios_agree"]
                                        and [c["probes"] for c in cells.values()] == [50, 200, 25])


def decision_rule(cp, cs, cb, pre_steps=None, bl=BL):
    """Frozen success criterion of EXP-ICPERF-284bc4 (price 925/4, ratios agree, probes match
    BSGS max), applied to arbitrary inputs. Returns (supported, ratios_agree, price)."""
    p = price_ratio(cp, cs, cb, bl)
    cs_ = [cell(r, A, cp, cs, cb, pre_steps=pre_steps, bl=bl) for r, A in CELLS]
    agree = all(c["ratio"] == cs_[0]["ratio"] for c in cs_) and cs_[0]["ratio"] == p
    bsgs_ok = all(c["probes"] == bsgs_enumerate(r // A, STATES)[0] for c, (r, A) in zip(cs_, CELLS))
    return (p == F(925, 4) and agree and bsgs_ok), agree, p


# --- 2. proves-too-much controls --------------------------------------------------------
ptm = {}
# 2a null-price vector (every price 1 unit): conclusion "925/4 holds" is false here
s, agree, p = decision_rule(1, 1, 1)
ptm["null_price_1_1_1"] = {"supported": s, "ratios_agree": agree, "price_ratio": str(p)}
# 2b random price vectors: does the identity part pass under the null?
rng = random.Random(20261106)
n, n_agree, n_support = 5000, 0, 0
for _ in range(n):
    cp, cs, cb = rng.randint(1, 5000), rng.randint(1, 50000), rng.randint(1, 500)
    s, agree, _ = decision_rule(cp, cs, cb)
    n_agree += agree; n_support += s
ptm["random_prices"] = {"n": n, "ratios_agree_true": n_agree, "supported": n_support,
                        "seed": 20261106}
# 2c planted perturbations (independent of producer controls)
ptm["c_probe_371"] = dict(zip(("supported", "ratios_agree", "price"),
                              map(str, decision_rule(371, 2100, 40))))
ptm["pre_steps_10"] = dict(zip(("supported", "ratios_agree", "price"),
                               map(str, decision_rule(370, 2100, 40, pre_steps=F(10)))))
ptm["pre_steps_10_cell_ratios"] = [str(cell(r, A, 370, 2100, 40, pre_steps=F(10))["ratio"]) for r, A in CELLS]
# 2d world-invariance: the rule reads no host datum. Evaluate it under three counterfactual
# n=83 measured deficits; the output cannot change, so `supported` carries no n=83 content.
ptm["world_invariance_n83"] = {str(d): decision_rule(370, 2100, 40)[0] for d in (2, 235, 2000)}
# 2e unrounded BL constants: the statement's identity is false (ratio != 925/4); rule output?
for name, bl in (("bl_2.124", F(2124, 1000)), ("bl_2.3353", F(23353, 10000))):
    s, agree, p = decision_rule(370, 2100, 40, bl=bl)
    ptm[name] = {"supported": s, "ratios_agree": agree, "price_ratio": f"{float(p):.4f}",
                 "integral_cells": all(cell(r, A, 370, 2100, 40, bl=bl)["bl_steps"].denominator == 1
                                       for r, A in CELLS)}
out["proves_too_much"] = ptm

# --- 3. section-5a band for the IC-online / BL-online ratio (independent counter models) ---
# R = c_probe*c_state/(2.1*c_step^2) with each price in GAE = 1 group addition + k*w native.
band = {}
ws = (F(0), F(1, 10), F(1))
# model RT (red team): one native op per probe, per state, per step; independent weights
corners = [(wp, wsx, wb) for wp in ws for wsx in ws for wb in ws]
Rs = [(1 + wp) * (1 + wsx) / (BL * (1 + wb) ** 2) for wp, wsx, wb in corners]
band["RT_uniform"] = {str(w): str((1 + w) ** 2 / (BL * (1 + w) ** 2)) for w in ws}
band["RT_27_corners"] = {"min": f"{float(min(Rs)):.4f}", "max": f"{float(max(Rs)):.4f}",
                         "corners_BL_ahead": sum(R > 1 for R in Rs), "n": len(Rs)}
# model MULT (this reader): uniform w per native op (as section 5a prescribes: the same weight on
# every arm), but native-op multiplicities k_probe, k_state, k_step in {1,2} unknown
mult = []
for kp, ks, kb in itertools.product((1, 2), repeat=3):
    for w in ws:
        mult.append(((kp, ks, kb, str(w)), (1 + kp * w) * (1 + ks * w) / (BL * (1 + kb * w) ** 2)))
vals = [v for _, v in mult]
band["MULT_uniform_w"] = {"min": f"{float(min(vals)):.4f}", "max": f"{float(max(vals)):.4f}",
                          "BL_ahead_cases": [k for k, v in mult if v > 1], "n": len(mult)}
# IC mean probes instead of the worst case (parent idea defines probes/target as a mean)
mean_factor = [bsgs_enumerate(r // A, STATES)[1] / (F(r, A) / STATES) for r, A in CELLS]
band["mean_probe_factor"] = [f"{float(x):.4f}" for x in mean_factor]
band["RT_uniform_with_mean_probes"] = [f"{float(F(10, 21) * x):.4f}" for x in mean_factor]
band["record_ns_prices_R"] = str(pr)
band["record_prices_in_GAE_at_40ns"] = {"probe": str(F(370, 40)), "state": str(F(2100, 40))}
# memory axis (listed, not charged): IC table = states entries; BL table at equal precomputation
# time: P_steps = 525 => T ~ sqrt(P/1.2) per the parent's 'precomputation ~1.2 T^2' model
P = F(STATES * C_STATE, C_STEP)
band["memory_entries"] = {"IC_states": STATES, "BL_T_from_parent_model": f"{(float(P) / 1.2) ** 0.5:.2f}"}
out["s5a_band"] = band

json.dump(out, sys.stdout, indent=1, default=str)
print()
