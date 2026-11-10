#!/usr/bin/env python3
"""Blind re-derivation of the EXP-XEDN-0c0182 primary metrics (P1-P3), from definitions only.

Audit AUD-20261106T051427Z-6b4683, reader screen of RBS-XEDN-a7cd25. Written by the auditor
without reading experiments/EXP-XEDN-0c0182/implementation/run.py or check.py, any producer
report, or the earlier audit-review.yaml. Stdlib only. It is a verification under the audit
directory, never a trial or a run record.

Definitions used (and nothing else):
  * specification.yaml (sha256 pinned below): curve y^2 = x(x^2 + A x + B), A=-1, B=16; primes
    31, 43, 59, 83, 353; frozen primes 31, 43, 59, 83; historical p=353 points (9,63),(17,183);
    t_max 64; metric names, P1-P3 tests, C1-C3 checks.
  * F1 (P1): an odd-order point has x a nonzero square, so a violation is an odd-order affine
    point with chi(x) != +1.  f1_violations_total = violations summed over all five primes.
  * Sign eligibility of a point for sign s: chi(s*x) = +1 ("character" reading). A second,
    "t-representative" reading (some 1 <= t <= t_max with s*t^2 == x mod p) is also computed;
    the specification does not say which one the point-level fields use, so both are reported.
  * odd_order_minus_eligible_at_3mod4 = odd-order affine points with minus-sign eligibility,
    summed over primes p == 3 mod 4.
  * faithful = both target points of odd order (IDEA-20261016-633cb1 claim text, cited as the
    source of F1/F2 by the specification). An arm (sP, sQ) of a pair is eligible when P is
    eligible for sP and Q for sQ under the t-representative reading (the frozen targets carry
    t_representatives). faithful_nonplus_eligible_arms_at_3mod4 = eligible arms other than
    (+1,+1) of faithful pairs at p == 3 mod 4.
  * Legendre table (P3): D_minus_63 = (-63/p) (-63 is the discriminant of x^2 - x + 16),
    minus_16 = (-16/p).
Arithmetic: points by exhaustive enumeration of (x, y); point order by repeated affine
addition until the identity.

Usage: python3 -I blind_rederive.py <repo_root> <out.json>
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
EXP = ROOT / "experiments/EXP-XEDN-0c0182"
SPEC_SHA = "c708b93631abc6b4ffcf27295c457796f979be6393de455e4476c00184c0f6e8"
TARGETS = ROOT / "analysis/xedni-cheon/20261007-certificates/targets.json"
TARGETS_SHA = "55cfa8826a8c3eedcb599a5a6a0871e74ea49f68a41c806b7284230b627b5452"
RUNS = {"RUN-XEDN-132272": "2a630d12b28c7a83ae7a9045364e882f784614e54dfc69954d948d4741738389",
        "RUN-XEDN-f4d646": "a328120c6366bd96570a961b00615acb483f9d50335efedb3a303d463cfeb221"}

A, B = -1, 16
PRIMES = [31, 43, 59, 83, 353]
FROZEN = [31, 43, 59, 83]
HIST_P, HIST_POINTS = 353, [(9, 63), (17, 183)]
T_MAX = 64
P3_TABLE = {31: (-1, -1), 43: (1, -1), 59: (-1, -1), 83: (-1, -1), 353: (-1, 1)}  # (D-63, -16)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chi(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def rhs(x, p):
    return (x * x * x + A * x * x + B * x) % p


def add(P, Q, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        lam = (3 * x1 * x1 + 2 * A * x1 + B) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - A - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def order(P, p):
    k, R = 1, P
    while R is not None:
        R = add(R, P, p)
        k += 1
    return k


def t_reps(s, x, p):
    return [t for t in range(1, T_MAX + 1) if (s * t * t - x) % p == 0]


def census(p):
    pts = [(x, y) for x in range(p) for y in range(p) if (y * y - rhs(x, p)) % p == 0]
    N = len(pts) + 1
    two = 1
    while N % (2 * two) == 0:
        two *= 2
    odd = [P for P in pts if order(P, p) % 2 == 1]
    even = [P for P in pts if order(P, p) % 2 == 0]
    return {
        "p": p, "p_mod_4": p % 4, "affine_points": len(pts), "group_order": N,
        "two_part": two, "odd_part": N // two, "odd_order_affine_points": len(odd),
        "f1_violations": sum(1 for (x, _) in odd if chi(x, p) != 1),
        "f1_violation_points": sorted([x, y] for (x, y) in odd if chi(x, p) != 1),
        "even_order_points_with_nonresidue_x": sum(1 for (x, _) in even if chi(x, p) == -1),
        "odd_order_points_with_plus_sign_eligible": sum(1 for (x, _) in odd if chi(x, p) == 1),
        "odd_order_points_with_minus_sign_eligible": sum(1 for (x, _) in odd if chi(-x, p) == 1),
        "alt_t_rep_plus_eligible": sum(1 for (x, _) in odd if t_reps(1, x, p)),
        "alt_t_rep_minus_eligible": sum(1 for (x, _) in odd if t_reps(-1, x, p)),
        "legendre": {"D_minus_63": chi(-63, p), "minus_16": chi(-16, p), "minus_1": chi(-1, p)},
    }


def main():
    assert sha(EXP / "specification.yaml") == SPEC_SHA, "specification digest moved"
    assert sha(TARGETS) == TARGETS_SHA, "targets digest moved"
    per = {p: census(p) for p in PRIMES}
    targets = json.loads(TARGETS.read_text())
    pairs = []
    for pair in targets["pairs"]:
        p = pair["p"]
        P, Q = tuple(pair["P"]), tuple(pair["Q"])
        po, qo = order(P, p) % 2 == 1, order(Q, p) % 2 == 1
        arms = []
        for arm in pair["arms"]:
            sP, sQ = arm["signs"]
            arms.append({"signs": [sP, sQ],
                         "eligible": bool(t_reps(sP, P[0], p)) and bool(t_reps(sQ, Q[0], p))})
        pairs.append({"id": pair["id"], "p": p, "P_odd_order": po, "Q_odd_order": qo,
                      "faithful": po and qo, "arms": arms})
    faithful = [x for x in pairs if x["faithful"]]
    mine = {
        "f1_violations_total": sum(per[p]["f1_violations"] for p in PRIMES),
        "odd_order_minus_eligible_at_3mod4": sum(
            per[p]["odd_order_points_with_minus_sign_eligible"] for p in PRIMES if p % 4 == 3),
        "alt_t_rep_odd_order_minus_eligible_at_3mod4": sum(
            per[p]["alt_t_rep_minus_eligible"] for p in PRIMES if p % 4 == 3),
        "faithful_pairs": len(faithful),
        "faithful_pair_ids": [x["id"] for x in faithful],
        "faithful_nonplus_eligible_arms_at_3mod4": sum(
            1 for x in faithful if x["p"] % 4 == 3 for a in x["arms"]
            if a["eligible"] and a["signs"] != [1, 1]),
        "p353_odd_order_points_with_minus_sign_eligible":
            per[353]["odd_order_points_with_minus_sign_eligible"],
        "p353_alt_t_rep_minus_eligible": per[353]["alt_t_rep_minus_eligible"],
        "p353_odd_order_affine_points": per[353]["odd_order_affine_points"],
        "legendre": {str(p): per[p]["legendre"] for p in PRIMES},
        "historical_control": {
            "on_curve": [all((y * y - rhs(x, HIST_P)) % HIST_P == 0 for (x, y) in HIST_POINTS)],
            "x_residue": [chi(x, HIST_P) for (x, _) in HIST_POINTS],
            "minus_x_residue": [chi(-x, HIST_P) for (x, _) in HIST_POINTS],
            "odd_order": [order(Pt, HIST_P) % 2 == 1 for Pt in HIST_POINTS]},
    }
    preds = {
        "P1": mine["f1_violations_total"] == 0,
        "P2": (mine["odd_order_minus_eligible_at_3mod4"] == 0
               and mine["faithful_nonplus_eligible_arms_at_3mod4"] == 0
               and mine["p353_odd_order_points_with_minus_sign_eligible"]
               == mine["p353_odd_order_affine_points"]),
        "P2_faithful_clause_vacuous": mine["faithful_pairs"] == 0,
        "P3": all((per[p]["legendre"]["D_minus_63"], per[p]["legendre"]["minus_16"]) == P3_TABLE[p]
                  for p in PRIMES),
        "C1": (mine["historical_control"]["on_curve"] == [True]
               and mine["historical_control"]["x_residue"] == [1, 1]
               and mine["historical_control"]["minus_x_residue"] == [1, 1]),
        "C2": any(x["id"] == "p31-pair00" and not x["faithful"]
                  and any(a["signs"] == [1, -1] and a["eligible"] for a in x["arms"]) for x in pairs),
        "C3": any(per[p]["even_order_points_with_nonresidue_x"] > 0 for p in PRIMES),
    }
    comparison = {}
    for run, digest in RUNS.items():
        path = EXP / "runs" / run / "raw-result.json"
        assert sha(path) == digest, f"{run} raw-result digest moved"
        raw = json.loads(path.read_text())
        diffs = []
        for key in ("f1_violations_total", "odd_order_minus_eligible_at_3mod4", "faithful_pairs",
                    "faithful_pair_ids", "faithful_nonplus_eligible_arms_at_3mod4"):
            if raw[key] != mine[key]:
                diffs.append({"field": key, "raw": raw[key], "blind": mine[key]})
        raw_per = {e["p"]: e for e in raw["per_prime"]}
        for p in PRIMES:
            for key in ("affine_points", "group_order", "two_part", "odd_part",
                        "odd_order_affine_points", "f1_violations", "f1_violation_points",
                        "even_order_points_with_nonresidue_x",
                        "odd_order_points_with_plus_sign_eligible",
                        "odd_order_points_with_minus_sign_eligible", "legendre", "p_mod_4"):
                if raw_per[p][key] != per[p][key]:
                    diffs.append({"field": f"per_prime[p={p}].{key}", "raw": raw_per[p][key],
                                  "blind": per[p][key]})
        hc = raw["historical_control"]
        for key, value in mine["historical_control"].items():
            if hc.get(key) != value:
                diffs.append({"field": f"historical_control.{key}", "raw": hc.get(key), "blind": value})
        raw_pairs = {x["id"]: x for x in raw["pairs"]}
        for x in pairs:
            r = raw_pairs[x["id"]]
            for key in ("P_odd_order", "Q_odd_order", "faithful"):
                if r[key] != x[key]:
                    diffs.append({"field": f"pairs[{x['id']}].{key}", "raw": r[key], "blind": x[key]})
            for a in x["arms"]:
                ra = next(b for b in r["arms"] if b["signs"] == a["signs"])
                if ra["eligible"] != a["eligible"]:
                    diffs.append({"field": f"pairs[{x['id']}].arms{a['signs']}.eligible",
                                  "raw": ra["eligible"], "blind": a["eligible"]})
        comparison[run] = {"raw_result_sha256": digest, "differences": diffs,
                           "fields_compared": "top-level P1/P2 counts and faithful ids; per_prime "
                           "census and legendre fields at all five primes; historical_control; "
                           "per-pair odd-order/faithful flags and 128 arm eligibilities"}
    out = {"blind": mine, "per_prime": {str(p): per[p] for p in PRIMES},
           "predictions_on_blind_values": preds, "comparison_with_raw_results": comparison}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"blind_primary": {k: mine[k] for k in (
        "f1_violations_total", "odd_order_minus_eligible_at_3mod4",
        "faithful_nonplus_eligible_arms_at_3mod4", "faithful_pairs",
        "p353_odd_order_points_with_minus_sign_eligible", "p353_odd_order_affine_points",
        "alt_t_rep_odd_order_minus_eligible_at_3mod4", "p353_alt_t_rep_minus_eligible")},
        "legendre": mine["legendre"], "predictions": preds,
        "differences": {r: len(c["differences"]) for r, c in comparison.items()}}, indent=1))


if __name__ == "__main__":
    main()
