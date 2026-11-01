#!/usr/bin/env python3
"""Single-process S0 gate workers; JSON stdout, no repository writes."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

import g1_s0 as g1


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TERMS = REPO / "experiments/EXP-SDEG-85eefd/implementation/semaev_polys.json"
POWER_SCRIPT = REPO / "coordination/goals/GOAL-ICEX-001/batches/BATCH-454f85/tasks/TASK-20261001-768475/power_check.py"
POWER_OUTPUT = REPO / "coordination/goals/GOAL-ICEX-001/batches/BATCH-454f85/tasks/TASK-20261001-768475/power_check_output.json"
SMOKE = "smoke|EXP-ICEX-153c34/v1"
V4_L = {(16, 21): 3, (16, 22): 5, (16, 23): 6,
        (20, 21): 7, (20, 22): 11, (20, 23): 5}


class QueryTimeout(RuntimeError):
    pass


def _alarm(_signum, _frame):
    raise QueryTimeout("3600-second per-query watchdog")


def digest(*parts):
    label = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def next_prime(n):
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def legendre(value, p):
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def curve_order(p, a, b):
    return p + 1 + sum(legendre(x**3 + a * x + b, p) for x in range(p))


def point_add(P, Q, p, a):
    """Verifier-only affine group law, independent of the G1 implementation."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        numerator, denominator = (3 * x1 * x1 + a) % p, (2 * y1) % p
    else:
        numerator, denominator = (y2 - y1) % p, (x2 - x1) % p
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def verifier_sqrt(value, p):
    """Verifier-only deterministic Tonelli-Shanks square root."""
    value %= p
    if value == 0:
        return 0
    if pow(value, (p - 1) // 2, p) != 1:
        raise ValueError("not a square")
    if p % 4 == 3:
        return pow(value, (p + 1) // 4, p)
    odd, power = p - 1, 0
    while odd % 2 == 0:
        odd //= 2
        power += 1
    nonresidue = 2
    while pow(nonresidue, (p - 1) // 2, p) != p - 1:
        nonresidue += 1
    m = power
    c = pow(nonresidue, odd, p)
    t = pow(value, odd, p)
    root = pow(value, (odd + 1) // 2, p)
    while t != 1:
        index, square = 1, t * t % p
        while square != 1:
            square = square * square % p
            index += 1
        correction = pow(c, 1 << (m - index - 1), p)
        root = root * correction % p
        t = t * correction * correction % p
        c = correction * correction % p
        m = index
    return root


def point_mul(k, P, p, a):
    out = None
    addend = P
    while k:
        if k & 1:
            out = point_add(out, addend, p, a)
        addend = point_add(addend, addend, p, a)
        k >>= 1
    return out


def canonical_point(p, a, b, x):
    rhs = (x**3 + a * x + b) % p
    if rhs == 0 or legendre(rhs, p) != 1:
        return None
    y = verifier_sqrt(rhs, p)
    return x, min(y, p - y)


def smoke_fixture(bits, wanted_l):
    """First nonsingular smoke curve under the dedicated smoke namespace."""
    for counter in range(1_000_000):
        value = digest(SMOKE, "curve", bits, wanted_l, counter)
        p = next_prime(2 ** (bits - 1) + value % 2 ** (bits - 1))
        if p.bit_length() != bits:
            continue
        a, b = (value >> 64) % p, (value >> 128) % p
        if a == 0 or b == 0 or (4 * a**3 + 27 * b**2) % p == 0:
            continue
        deck = []
        bound = None
        base = None
        for x in range(p):
            point = canonical_point(p, a, b, x)
            if base is None and point is not None:
                base = point
            if point is not None and len(deck) < wanted_l:
                deck.append(point)
                if len(deck) == wanted_l:
                    bound = x + 1
                    break
        if len(deck) != wanted_l or base is None:
            continue
        fixture = {
            "fixture_id": "smoke-b%d-L%d" % (bits, wanted_l),
            "namespace": SMOKE, "bits": bits, "L": wanted_l, "B": bound,
            "counter": counter, "p": p, "a": a, "b": b,
            "target_scalar_modulus": p,
            "G": list(base), "V": [point[0] for point in deck],
        }
        return fixture, deck
    raise RuntimeError("smoke fixture search exhausted")


def uniform(label_parts, modulus):
    limit = (1 << 256) // modulus * modulus
    for counter in range(1_000_000):
        value = digest(*label_parts, counter)
        if value < limit:
            return value % modulus
    raise RuntimeError("uniform rejection exhausted")


def attempt_target(fixture, attempt):
    scalar = uniform((SMOKE, "attempt", fixture["bits"], fixture["L"], attempt),
                     fixture["target_scalar_modulus"])
    point = point_mul(scalar, tuple(fixture["G"]), fixture["p"], fixture["a"])
    return scalar, point


def exact_o5(fixture, deck):
    p, a = fixture["p"], fixture["a"]
    signed = []
    for point in deck:
        signed.extend((point, (point[0], (-point[1]) % p)))
    represented = set()
    for symbols in itertools.combinations_with_replacement(range(len(signed)), 5):
        total = None
        for symbol in symbols:
            total = point_add(total, signed[symbol], p, a)
        represented.add(total)
    return represented


def factor_base(fixture):
    bound = fixture.get("B_star")
    if bound is None:
        bound = 1
        while bound ** 5 < int(fixture["p"]):
            bound += 1
    points = []
    for x in range(int(bound)):
        point = canonical_point(int(fixture["p"]), int(fixture["a"]), int(fixture["b"]), x)
        if point is not None:
            points.append(point)
    return points


def all_gate_fixtures(panel_path):
    v4_path = REPO / "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json"
    v4 = json.loads(v4_path.read_text())["EXP-ICEX-aaccfc"]
    panel = json.loads(Path(panel_path).read_text())["panel"]
    rows = []
    for fixture in v4:
        item = dict(fixture)
        item["fixture_id"] = "v4-b%d-s%d" % (item["bits"], item["seed"])
        rows.append(item)
    for fixture in panel:
        item = dict(fixture)
        item["fixture_id"] = "panel-b%d-s%d" % (item["bits"], item["seed"])
        rows.append(item)
    return rows


def sample_indices(fixture_id, kind, sample, count, modulus, retry):
    return [uniform((SMOKE, "G0-3", fixture_id, kind, sample, retry, index), modulus)
            for index in range(count)]


def signed_sum(points, signs, fixture):
    total = None
    p, a = int(fixture["p"]), int(fixture["a"])
    for point, sign in zip(points, signs):
        selected = point if sign > 0 else (point[0], (-point[1]) % p)
        total = point_add(total, selected, p, a)
    return total


def gate_g03_samples(fixture, deck):
    signed, nonsums = [], []
    retries = {"signed_target_O": 0, "non_sum_collision": 0, "non_sum_target_O": 0}
    for sample in range(1000):
        retry = 0
        while True:
            indices = sample_indices(fixture["fixture_id"], "signed", sample, 5, len(deck), retry)
            sign_bits = sample_indices(fixture["fixture_id"], "signed-sign", sample, 5, 2, retry)
            signs = [1 if bit else -1 for bit in sign_bits]
            chosen = [deck[index] for index in indices]
            target = signed_sum(chosen, signs, fixture)
            if target is not None:
                signed.append((tuple(point[0] for point in chosen), target))
                break
            retries["signed_target_O"] += 1
            retry += 1
    for sample in range(1000):
        retry = 0
        while True:
            indices = sample_indices(fixture["fixture_id"], "nonsum", sample, 5, len(deck), retry)
            chosen = [deck[index] for index in indices]
            scalar = 1 + uniform((SMOKE, "G0-3", fixture["fixture_id"], "nonsum-target",
                                  sample, retry), int(fixture["N"]) - 1)
            target = point_mul(scalar, tuple(fixture["G"]), int(fixture["p"]), int(fixture["a"]))
            if target is None:
                retries["non_sum_target_O"] += 1
                retry += 1
                continue
            neg_target = (target[0], (-target[1]) % int(fixture["p"]))
            if any(signed_sum(chosen, signs, fixture) in (target, neg_target)
                   for signs in itertools.product((-1, 1), repeat=5)):
                retries["non_sum_collision"] += 1
                retry += 1
                continue
            nonsums.append((tuple(point[0] for point in chosen), target))
            break
    return signed, nonsums, retries


def f5_tensor(fixture):
    terms, _degrees = g1.load_s5_terms(str(TERMS))
    p, a, b = int(fixture["p"]), int(fixture["a"]), int(fixture["b"])
    tensor = np.zeros((9, 9, 9, 9, 9), dtype=np.int64)
    for term in terms:
        coefficient = term[7] * pow(a, term[0], p) * pow(b, term[1], p) % p
        e1, e2, e3, e4, ez = term[2:7]
        tensor[ez, e1, e2, e3, e4] = (tensor[ez, e1, e2, e3, e4] + coefficient) % p
    return tensor


def batch_f5_coefficients(tensor, tuples, p):
    count = len(tuples)
    coordinates = np.asarray(tuples, dtype=np.int64)
    x = coordinates[:, 3]
    result = np.zeros(tensor.shape[:-1] + (count,), dtype=np.int64)
    for degree in range(8, -1, -1):
        result = (result * x + tensor[..., degree, None]) % p
    for coordinate in (2, 1, 0):
        x = coordinates[:, coordinate]
        reduced = np.zeros(result.shape[:-2] + (count,), dtype=np.int64)
        for degree in range(8, -1, -1):
            reduced = (reduced * x + result[..., degree, :]) % p
        result = reduced
    return result.T


def numeric_resultant_bareiss(A, B, p):
    degree_a, degree_b = 8, 2
    size = degree_a + degree_b
    matrix = [[0] * size for _ in range(size)]
    for row in range(degree_b):
        for column, value in enumerate(A):
            matrix[row][row + column] = int(value) % p
    for row in range(degree_a):
        for column, value in enumerate(B):
            matrix[degree_b + row][row + column] = int(value) % p
    previous, sign = 1, 1
    for k in range(size - 1):
        pivot_row = next((row for row in range(k, size) if matrix[row][k] % p), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]
            sign = -sign
        pivot = matrix[k][k] % p
        for row in range(k + 1, size):
            for column in range(k + 1, size):
                value = (pivot * matrix[row][column]
                         - matrix[row][k] * matrix[k][column]) % p
                if k:
                    value = value * pow(previous, p - 2, p) % p
                matrix[row][column] = value
            matrix[row][k] = 0
        previous = pivot
    return sign * matrix[-1][-1] % p


def numeric_d2_resultant(coefficients, p, a, b, x5, xR):
    """Evaluate the frozen D-2 pseudo-remainder/pair-product formula."""
    constant, linear, leading = g1.s3_coeffs(p, a, b, x5, xR)
    if leading == 0:
        # The quotient formula has a removable singularity here; the full
        # formal-slot determinant is the exact specialisation of its polynomial.
        return numeric_resultant_bareiss(coefficients, [constant, linear, leading], p)
    u, v = [0, 1], [1, 0]
    for degree in range(2, 9):
        u.append((leading * v[-1] - linear * u[-1]) % p)
        v.append((-constant * u[-2]) % p)
    U, V = [], []
    for degree in range(9):
        if degree == 0:
            U.append(0)
            V.append(pow(leading, 7, p))
        else:
            scale = pow(leading, 8 - degree, p)
            U.append(u[degree] * scale % p)
            V.append(v[degree] * scale % p)
    alpha = sum(int(coefficients[i]) * U[i] for i in range(9)) % p
    beta = sum(int(coefficients[i]) * V[i] for i in range(9)) % p
    numerator = (constant * alpha * alpha - linear * alpha * beta
                 + leading * beta * beta) % p
    return numerator * pow(pow(leading, 7, p), p - 2, p) % p


def gate_g03(panel_path):
    evidence = []
    all_pass = True
    for fixture in all_gate_fixtures(panel_path):
        deck = factor_base(fixture)
        expected_l = int(fixture.get("L_star", V4_L.get((fixture["bits"], fixture["seed"]), -1)))
        if len(deck) != expected_l:
            evidence.append({"fixture_id": fixture["fixture_id"], "pass": False,
                             "reason": "factor-base cardinality mismatch",
                             "expected_L": expected_l, "observed_L": len(deck)})
            all_pass = False
            continue
        signed, nonsums, retries = gate_g03_samples(fixture, deck)
        samples = signed + nonsums
        tensor = f5_tensor(fixture)
        coefficients = batch_f5_coefficients(
            tensor, [sample[0][:4] for sample in samples], int(fixture["p"]))
        signed_failures, nonsum_failures, d2_crosscheck_failures = [], [], []
        for index, ((xs, target), f5_coeff) in enumerate(zip(samples, coefficients)):
            p, a, b = int(fixture["p"]), int(fixture["a"]), int(fixture["b"])
            value = numeric_d2_resultant(f5_coeff, p, a, b, xs[4], target[0])
            if index in (0, 1000):
                independent = numeric_resultant_bareiss(
                    f5_coeff, g1.s3_coeffs(p, a, b, xs[4], target[0]), p)
                if value != independent:
                    d2_crosscheck_failures.append({"sample": index, "d2": int(value),
                                                   "bareiss": int(independent)})
            if index < 1000 and value != 0:
                signed_failures.append({"sample": index, "value": int(value)})
            if index >= 1000 and value == 0:
                nonsum_failures.append({"sample": index - 1000, "value": 0})
        passed = not signed_failures and not nonsum_failures and not d2_crosscheck_failures
        all_pass &= passed
        evidence.append({"fixture_id": fixture["fixture_id"], "p": fixture["p"],
                         "L": len(deck), "signed_checks": 1000, "nonsum_checks": 1000,
                         "signed_failures": signed_failures, "nonsum_failures": nonsum_failures,
            "d2_bareiss_crosscheck_failures": d2_crosscheck_failures,
                         "rejections": retries, "pass": passed,
            "frozen_fixture_cost_fields_emitted": False})
    all_pass = all_pass and len(evidence) == 26
    return {"gate": "G0-3", "pass": all_pass, "blocked": False,
            "classification": "pass" if all_pass else "implementation_error",
            "fixtures_required": 26, "fixtures_checked": len(evidence),
            "samples_per_fixture": {"signed_5_sums": 1000, "non_sums": 1000},
            "sample_namespace": SMOKE, "fixtures": evidence}


def run_query(fixture, setup, target):
    prior = signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(3600)
    started = time.perf_counter()
    try:
        result = g1.g1_membership(fixture, fixture["V"], target, TERMS, setup=setup)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, prior)
    return result, time.perf_counter() - started


def gate_g04(bits, wanted_l):
    fixture, deck = smoke_fixture(bits, wanted_l)
    oracle_started = time.perf_counter()
    oracle = exact_o5(fixture, deck)
    oracle_seconds = time.perf_counter() - oracle_started
    setup_started = time.perf_counter()
    setup = g1.d2_setup(fixture["p"], fixture["a"], fixture["b"], fixture["V"], TERMS)
    setup_seconds = time.perf_counter() - setup_started
    attempts, timings = [], []
    for index in range(200):
        scalar, target = attempt_target(fixture, index)
        try:
            result, elapsed = run_query(fixture, setup, target)
        except QueryTimeout as error:
            return {
                "gate": "G0-4", "pass": False, "blocked": True,
                "classification": "resource_exhaustion", "fixture": fixture,
                "attempts_required": 200, "attempts_completed": len(attempts),
                "observation": str(error), "setup_seconds": setup_seconds,
                "oracle_seconds": oracle_seconds, "attempts": attempts,
                "frozen_fixture_cost_fields_emitted": False,
            }
        expected = target in oracle
        row = {"attempt": index, "scalar": scalar, "target": target,
               "g1_member": result.get("member"), "o5_member": expected,
               "agree": result.get("status") == "ok" and result.get("member") == expected,
               "seconds": elapsed}
        attempts.append(row)
        timings.append(elapsed)
        if not row["agree"]:
            return {
                "gate": "G0-4", "pass": False, "blocked": False,
                "classification": "implementation_error", "fixture": fixture,
                "attempts_required": 200, "attempts_completed": len(attempts),
                "observation": "first G1/O5 disagreement", "setup_seconds": setup_seconds,
                "oracle_seconds": oracle_seconds, "attempts": attempts,
                "frozen_fixture_cost_fields_emitted": False,
            }
    ordered = sorted(timings)
    median = (ordered[99] + ordered[100]) / 2
    return {
        "gate": "G0-4", "pass": True, "blocked": False, "classification": "pass",
        "fixture": fixture, "attempts_required": 200, "attempts_completed": 200,
        "all_agree": True, "median_query_seconds": median,
        "setup_seconds": setup_seconds, "oracle_seconds": oracle_seconds,
        "attempts": attempts, "frozen_fixture_cost_fields_emitted": False,
    }


def gate_g06():
    fixture, _deck = smoke_fixture(7, 2)
    setup = g1.d2_setup(fixture["p"], fixture["a"], fixture["b"], fixture["V"], TERMS)
    operation_log = []
    for index in range(20):
        _scalar, target = attempt_target(fixture, index)
        result, elapsed = run_query(fixture, setup, target)
        if result.get("status") != "ok":
            return {"gate": "G0-6", "pass": False, "blocked": True,
                    "classification": "infrastructure_error", "fixture": fixture,
                    "queries_completed": len(operation_log), "operation_log": operation_log,
                    "observation": result}
        operation_log.append({
            "attempt": index, "seconds": elapsed, "components": result["components"],
            "reported_units": {name: raw["units"] for name, raw in result["components"].items()},
        })
    return {"gate": "G0-6", "pass": None, "blocked": False,
            "classification": "pending_independent_checker", "fixture": fixture,
            "queries_completed": 20, "operation_log": operation_log}


def collect_rate_records(node, path=(), inherited_reps=None):
    records = []
    if isinstance(node, dict):
        reps = node.get("reps", inherited_reps)
        for key, value in node.items():
            child_path = path + (key,)
            if isinstance(value, (dict, list)):
                records.extend(collect_rate_records(value, child_path, reps))
            elif (isinstance(value, (int, float))
                  and ("rate" in key or key.startswith("false_favourable")) and reps):
                records.append((".".join(child_path), float(value), int(reps)))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            records.extend(collect_rate_records(value, path + (str(index),), inherited_reps))
    return records


def gate_g05():
    expected = json.loads(POWER_OUTPUT.read_text())
    process = subprocess.run([sys.executable, str(POWER_SCRIPT)], cwd=REPO,
                             capture_output=True, text=True, check=False,
                             env={**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                                  "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
    if process.returncode:
        return {"gate": "G0-5", "pass": False, "blocked": True,
                "classification": "infrastructure_error", "returncode": process.returncode,
                "stderr": process.stderr[-4000:]}
    observed = json.loads(process.stdout)
    expected_rates = {path: (value, reps) for path, value, reps in collect_rate_records(expected)}
    observed_rates = {path: (value, reps) for path, value, reps in collect_rate_records(observed)}
    comparisons = []
    for path in sorted(set(expected_rates) | set(observed_rates)):
        if path not in expected_rates or path not in observed_rates:
            comparisons.append({"path": path, "pass": False, "reason": "missing rate"})
            continue
        wanted, reps = expected_rates[path]
        got, got_reps = observed_rates[path]
        standard_error = math.sqrt(wanted * (1 - wanted) / reps)
        tolerance = 3 * standard_error
        comparisons.append({"path": path, "expected": wanted, "observed": got,
                            "reps": reps, "observed_reps": got_reps,
                            "mc_standard_error": standard_error, "tolerance_3se": tolerance,
                            "absolute_difference": abs(got - wanted),
                            "pass": got_reps == reps and abs(got - wanted) <= tolerance + 1e-15})
    return {"gate": "G0-5", "pass": bool(comparisons) and all(row["pass"] for row in comparisons),
            "blocked": False, "classification": "pass" if comparisons and all(row["pass"] for row in comparisons) else "implementation_error",
            "rates_compared": len(comparisons), "comparisons": comparisons,
            "expected_output_sha256": hashlib.sha256(POWER_OUTPUT.read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256(POWER_SCRIPT.read_bytes()).hexdigest(),
            "command": [sys.executable, str(POWER_SCRIPT)],
            "observed_reported_seconds": observed.get("seconds")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=("G0-3", "G0-4", "G0-5", "G0-6"), required=True)
    parser.add_argument("--bits", type=int)
    parser.add_argument("--L", type=int)
    parser.add_argument("--panel")
    args = parser.parse_args()
    if args.gate == "G0-3":
        if not args.panel:
            parser.error("G0-3 requires --panel")
        result = gate_g03(args.panel)
    elif args.gate == "G0-4":
        if args.bits is None or args.L is None:
            parser.error("G0-4 requires --bits and --L")
        result = gate_g04(args.bits, args.L)
    elif args.gate == "G0-5":
        result = gate_g05()
    else:
        result = gate_g06()
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    raise SystemExit(0 if result.get("pass") is not False else 2)


if __name__ == "__main__":
    main()
