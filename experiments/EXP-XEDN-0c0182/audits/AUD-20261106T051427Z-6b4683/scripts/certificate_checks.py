#!/usr/bin/env python3
"""Point-level certificate checks and determinism (C4) on both units of RBS-XEDN-a7cd25.

Audit AUD-20261106T051427Z-6b4683. This census claims no discrete-log, relation or
decomposition certificate (the superseding manifest_v2.yaml records certificate.kind none);
its checkable claims are point facts: on-curve, odd/even order, t-representatives, group
order, and the exact H1 prediction. Neither unit was replayed by the deterministic audit
(replay population empty), so both are checked here as unreplayed units.

Arithmetic shares no code with the producer (run.py and check.py were never read) or with
blind_rederive.py: group order by the character sum N = p + 1 + sum_x chi(f(x)); odd order
by [odd part of N]P = O with Jacobian-coordinate double-and-add; exact H1 predictions with
fractions.Fraction from the formula in specification.yaml preregistered_prediction.formula.

Accepted cells (P5, secondary) need the progression base w0, z0, which the specification does
not define. ONE reading was fixed before comparing: w0 = y_P, z0 = y_Q as least non-negative
residues, w = w0 + p*j, z = z0 + p*k, j, k in [-8, 8], accepted iff n != 0 and
s_P*w^2 == s_Q*z^2 mod |n|, n = s_P*s^2 - s_Q*t^2 over the frozen (s, t) representatives.
No other reading is tried; a mismatch is reported as "not reproduced under this reading".

Usage: python3 -I certificate_checks.py <repo_root> <out.json>
"""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
EXP = ROOT / "experiments/EXP-XEDN-0c0182"
TARGETS = ROOT / "analysis/xedni-cheon/20261007-certificates/targets.json"
TARGETS_SHA = "55cfa8826a8c3eedcb599a5a6a0871e74ea49f68a41c806b7284230b627b5452"
RUNS = {"RUN-XEDN-132272": "2a630d12b28c7a83ae7a9045364e882f784614e54dfc69954d948d4741738389",
        "RUN-XEDN-f4d646": "a328120c6366bd96570a961b00615acb483f9d50335efedb3a303d463cfeb221"}
C4_EXCLUDED = {"run_id", "trial_id", "seed", "supplementary_manifest_proposal", "elapsed_seconds"}
A2, A4 = -1, 16
T_MAX, SHIFT = 64, range(-8, 9)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legendre(a, p):
    a %= p
    return 0 if a == 0 else (1 if pow(a, (p - 1) // 2, p) == 1 else -1)


def f(x, p):
    return (x ** 3 + A2 * x ** 2 + A4 * x) % p


def group_order(p):
    return p + 1 + sum(legendre(f(x, p), p) for x in range(p))


# Jacobian coordinates (X:Y:Z), affine x = X/Z^2, y = Y/Z^3; the identity has Z = 0.
def jdouble(P, p):
    X, Y, Z = P
    if Z == 0 or Y % p == 0:
        return (1, 1, 0)
    YY, ZZ = Y * Y % p, Z * Z % p
    S = 4 * X * YY % p
    M = (3 * X * X + 2 * A2 * X * ZZ + A4 * ZZ * ZZ) % p
    X3 = (M * M - 2 * S - A2 * 4 * YY * ZZ) % p
    # x3 = lam^2 - a2 - 2x with lam = M/(2YZ): scale by (2YZ)^2 = 4 YY ZZ
    Z3 = 2 * Y * Z % p
    Y3 = (M * (S - X3) - 8 * YY * YY) % p
    # y3 = lam(x - x3) - y; X3 already carries the a2 term, so S - X3 is consistent
    return (X3, Y3, Z3)


def jadd(P, Q, p):
    if P[2] == 0:
        return Q
    if Q[2] == 0:
        return P
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1, Z2Z2 = Z1 * Z1 % p, Z2 * Z2 % p
    U1, U2 = X1 * Z2Z2 % p, X2 * Z1Z1 % p
    S1, S2 = Y1 * Z2 * Z2Z2 % p, Y2 * Z1 * Z1Z1 % p
    if U1 == U2:
        return jdouble(P, p) if S1 == S2 else (1, 1, 0)
    H, R = (U2 - U1) % p, (S2 - S1) % p
    HH = H * H % p
    HHH = H * HH % p
    Z3 = H * Z1 * Z2 % p
    ZZ3 = Z3 * Z3 % p
    X3 = (R * R - HHH - 2 * U1 * HH - A2 * ZZ3) % p
    Y3 = (R * (U1 * HH - X3) - S1 * HHH) % p
    return (X3, Y3, Z3)


def jmul(k, pt, p):
    R, Q = (1, 1, 0), (pt[0] % p, pt[1] % p, 1)
    while k:
        if k & 1:
            R = jadd(R, Q, p)
        Q = jdouble(Q, p)
        k >>= 1
    return R


def odd_part(n):
    while n % 2 == 0:
        n //= 2
    return n


def on_curve(pt, p):
    return (pt[1] ** 2 - f(pt[0], p)) % p == 0


def is_odd_order(pt, p):
    return jmul(odd_part(group_order(p)), pt, p)[2] == 0


def self_test():
    # Cross-check the Jacobian law against brute-force affine addition at a small prime.
    p = 43
    pts = [(x, y) for x in range(p) for y in range(p) if on_curve((x, y), p)]
    N = group_order(p)
    assert N == len(pts) + 1
    for pt in pts:
        assert jmul(N, pt, p)[2] == 0, "Lagrange fails: group law wrong"
    return {"p": p, "points": len(pts), "lagrange_holds_for_all": True}


def reps(s, x, p):
    return [t for t in range(1, T_MAX + 1) if (s * t * t - x) % p == 0]


def h1_term(sP, sQ, s, t):
    n = abs(sP * s * s - sQ * t * t)
    hits = 0
    squares = {}
    for z in range(n):
        squares.setdefault(sQ * z * z % n, 0)
        squares[sQ * z * z % n] += 1
    for w in range(n):
        hits += squares.get(sP * w * w % n, 0)
    return Fraction(289 * hits, n * n)


def main():
    out = {"self_test": self_test(), "units": {}}
    assert sha(TARGETS) == TARGETS_SHA
    targets = json.loads(TARGETS.read_text())
    target_checks = []
    h1_exact = {}
    accepted_r1 = {}
    for pair in targets["pairs"]:
        p, P, Q = pair["p"], pair["P"], pair["Q"]
        row = {"id": pair["id"], "on_curve": [on_curve(P, p), on_curve(Q, p)],
               "odd_order": [is_odd_order(P, p), is_odd_order(Q, p)],
               "distinct_x": P[0] != Q[0], "t_rep_mismatch": []}
        for arm in pair["arms"]:
            sP, sQ = arm["signs"]
            mine = [reps(sP, P[0], p)[:4], reps(sQ, Q[0], p)[:4]]
            if mine != arm["t_representatives"]:
                row["t_rep_mismatch"].append({"signs": arm["signs"], "frozen": arm["t_representatives"],
                                              "recomputed": mine})
            key = (pair["id"], sP, sQ)
            if mine[0] and mine[1]:
                total, acc, zero = Fraction(0), 0, 0
                for s in mine[0]:
                    for t in mine[1]:
                        n = sP * s * s - sQ * t * t
                        if n == 0:
                            zero += 1
                            continue
                        total += h1_term(sP, sQ, s, t)
                        m = abs(n)
                        for j in SHIFT:
                            w = P[1] + p * j
                            for k in SHIFT:
                                z = Q[1] + p * k
                                if (sP * w * w - sQ * z * z) % m == 0:
                                    acc += 1
                h1_exact[key] = total
                accepted_r1[key] = (acc, zero)
        target_checks.append(row)
    out["targets"] = {"pairs": len(target_checks),
                      "all_on_curve": all(all(r["on_curve"]) for r in target_checks),
                      "all_distinct_x": all(r["distinct_x"] for r in target_checks),
                      "t_representative_mismatches": [r for r in target_checks if r["t_rep_mismatch"]],
                      "pairs_with_both_odd_order": [r["id"] for r in target_checks if all(r["odd_order"])]}
    raws = {}
    for run, digest in RUNS.items():
        path = EXP / "runs" / run / "raw-result.json"
        assert sha(path) == digest
        raw = raws[run] = json.loads(path.read_text())
        u = {"raw_result_sha256": digest, "issues": []}
        for e in raw["per_prime"]:
            if e["group_order"] != group_order(e["p"]):
                u["issues"].append(f"group_order p={e['p']}: raw {e['group_order']} vs {group_order(e['p'])}")
            for pt in e["f1_violation_points"]:
                u["issues"].append(f"claimed F1 violation point {pt} at p={e['p']}")
        hc = raw["historical_control"]
        hp = hc["p"]
        hist = [{"point": pt, "on_curve": on_curve(pt, hp), "odd_order": is_odd_order(pt, hp),
                 "chi_x": legendre(pt[0], hp), "chi_minus_x": legendre(-pt[0], hp)} for pt in hc["points"]]
        u["historical_control"] = hist
        if [h["odd_order"] for h in hist] != hc["odd_order"]:
            u["issues"].append("historical odd_order flags disagree")
        rows = {r["id"]: r for r in target_checks}
        flag_mismatch = h1_mismatch = 0
        acc_match = acc_mismatch = 0
        acc_examples = []
        for pr in raw["pairs"]:
            r = rows[pr["id"]]
            if [pr["P_odd_order"], pr["Q_odd_order"]] != r["odd_order"]:
                flag_mismatch += 1
            for a in pr["arms"]:
                key = (pr["id"], a["signs"][0], a["signs"][1])
                if key not in h1_exact:
                    continue
                if Fraction(a["h1_predicted_exact"]) != h1_exact[key]:
                    h1_mismatch += 1
                acc, zero = accepted_r1[key]
                if (a["accepted"], a["rejected_zero_discriminant"]) == (acc, zero):
                    acc_match += 1
                else:
                    acc_mismatch += 1
                    if len(acc_examples) < 3:
                        acc_examples.append({"arm": list(key), "raw": a["accepted"], "reading_R1": acc})
        u["pair_order_flag_mismatches"] = flag_mismatch
        u["eligible_arms_checked"] = len(h1_exact)
        u["h1_predicted_exact_mismatches"] = h1_mismatch
        u["accepted_cells_reading_R1"] = {"match": acc_match, "mismatch": acc_mismatch,
                                          "examples": acc_examples}
        sup = raw["supplementary_manifest_proposal"]
        bad = []
        count = 0
        for ps, plist in sup["pairs_by_prime"].items():
            p = int(ps)
            for P, Q in plist:
                count += 1
                if not (on_curve(P, p) and on_curve(Q, p) and is_odd_order(P, p) and is_odd_order(Q, p)
                        and P[0] != Q[0]):
                    bad.append([p, P, Q])
        u["supplementary_proposal"] = {"pairs": count, "seed": sup.get("seed"),
                                       "not_on_curve_odd_order_distinct_x": bad}
        out["units"][run] = u
    a, b = raws["RUN-XEDN-132272"], raws["RUN-XEDN-f4d646"]
    keys = (set(a) | set(b)) - C4_EXCLUDED
    out["c4_determinism"] = {"fields_compared": sorted(keys),
                             "differing_fields": sorted(k for k in keys if a.get(k) != b.get(k))}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"self_test": out["self_test"],
                      "targets": {k: v for k, v in out["targets"].items()},
                      "units": {r: {k: v for k, v in u.items() if k != "historical_control"}
                                for r, u in out["units"].items()},
                      "historical": out["units"]["RUN-XEDN-132272"]["historical_control"],
                      "c4_differing_fields": out["c4_determinism"]["differing_fields"]}, indent=1))


if __name__ == "__main__":
    main()
