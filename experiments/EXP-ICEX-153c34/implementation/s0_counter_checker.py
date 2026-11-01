#!/usr/bin/env python3
"""Independent G0-6 replay from frozen inputs and an operation-site contract.

The producer's events and aggregate counters are treated only as claims.  This
checker independently regenerates the smoke fixture and targets, rebuilds the
setup, reruns G1, validates every replay event against ``s0_operation_spec``,
and then compares the producer trace byte-for-byte with that expected trace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import g1_s0 as g1
import o5_group
import s0_operation_spec as operation_spec


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TERMS = REPO / "experiments/EXP-SDEG-85eefd/implementation/semaev_polys.json"
TERMS_SHA256 = "447d9bfff27f2b57b50e60fffde0c380ab697f4b2cbf006114bb7a50be10642e"
SMOKE = "smoke|EXP-ICEX-153c34/v1"
COMPONENTS = ("S", "G", "X", "V")
RAW_FIELDS = operation_spec.RAW_FIELDS
WEIGHTS = operation_spec.WEIGHTS


def units(raw):
    return operation_spec.units(raw)


def empty_raw():
    return operation_spec.empty_raw()


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


def smoke_fixture(bits=7, wanted_l=2):
    for counter in range(1_000_000):
        value = digest(SMOKE, "curve", bits, wanted_l, counter)
        p = next_prime(2 ** (bits - 1) + value % 2 ** (bits - 1))
        if p.bit_length() != bits:
            continue
        a, b = (value >> 64) % p, (value >> 128) % p
        if a == 0 or b == 0 or (4 * a**3 + 27 * b**2) % p == 0:
            continue
        deck, base, bound = [], None, None
        for x in range(p):
            point = o5_group.canonical_point(p, a, b, x)
            if base is None and point is not None:
                base = point
            if point is not None and len(deck) < wanted_l:
                deck.append(point)
                if len(deck) == wanted_l:
                    bound = x + 1
                    break
        if len(deck) == wanted_l and base is not None:
            return {
                "fixture_id": "smoke-b%d-L%d" % (bits, wanted_l),
                "namespace": SMOKE, "bits": bits, "L": wanted_l, "B": bound,
                "counter": counter, "p": p, "a": a, "b": b,
                "target_scalar_modulus": p,
                "G": list(base), "V": [point[0] for point in deck],
            }
    raise RuntimeError("independent smoke fixture search exhausted")


def uniform(label_parts, modulus):
    limit = (1 << 256) // modulus * modulus
    for counter in range(1_000_000):
        value = digest(*label_parts, counter)
        if value < limit:
            return value % modulus
    raise RuntimeError("independent uniform rejection exhausted")


def point_mul(k, point, p, a):
    out, addend = None, point
    while k:
        if k & 1:
            out = o5_group.point_add(out, addend, p, a)
        addend = o5_group.point_add(addend, addend, p, a)
        k >>= 1
    return out


def attempt_target(fixture, attempt):
    scalar = uniform((SMOKE, "attempt", fixture["bits"], fixture["L"], attempt),
                     fixture["target_scalar_modulus"])
    target = point_mul(scalar, tuple(fixture["G"]), fixture["p"], fixture["a"])
    return scalar, target


def counter_record(counter):
    raw = counter.snapshot()
    return {"events": counter.events, "raw": raw, "units": counter.units()}


def expected_document():
    if hashlib.sha256(TERMS.read_bytes()).hexdigest() != TERMS_SHA256:
        raise RuntimeError("pinned Semaev inventory hash mismatch")
    fixture = smoke_fixture()
    setup_counter = g1.Counters(trace_operations=True)
    setup_counter.set_component("P")
    setup = g1.d2_setup(fixture["p"], fixture["a"], fixture["b"], fixture["V"],
                        TERMS, counters=setup_counter)
    queries = []
    for attempt in range(20):
        scalar, target = attempt_target(fixture, attempt)
        result = g1.g1_membership(
            fixture, fixture["V"], target, TERMS, setup=setup,
            trace_operations=True)
        queries.append({
            "attempt": attempt, "scalar": scalar,
            "target": None if target is None else list(target),
            "events": result["operation_events"],
            "components": result["components"],
            "reported_units": {
                name: result["components"][name]["units"] for name in COMPONENTS
            },
        })
    return {
        "fixture": fixture,
        "terms_sha256": TERMS_SHA256,
        "g1_sha256": hashlib.sha256(Path(g1.__file__).read_bytes()).hexdigest(),
        "operation_spec_sha256": hashlib.sha256(
            Path(operation_spec.__file__).read_bytes()).hexdigest(),
        "setup": counter_record(setup_counter),
        "queries_completed": 20,
        "operation_log": queries,
    }


def compare_aggregate(claim, expected_raw, expected_units, label):
    errors = []
    if not isinstance(claim, dict):
        return [label + " aggregate is absent"]
    for field in RAW_FIELDS:
        if claim.get(field) != expected_raw[field]:
            errors.append(label + " %s disagrees with independent replay" % field)
    if claim.get("units") != expected_units:
        errors.append(label + " units disagree with independent replay")
    return errors


def compare_trace(claim, expected, label):
    errors = []
    if not isinstance(claim, list):
        return [label + " event trace is not a list"]
    _claim_raw, claim_contract_errors = operation_spec.aggregate(claim)
    _expected_raw, expected_contract_errors = operation_spec.aggregate(expected)
    errors.extend(label + " claimed " + error for error in claim_contract_errors)
    errors.extend(label + " replay " + error for error in expected_contract_errors)
    if claim != expected:
        mismatch = next((index for index, pair in enumerate(zip(claim, expected))
                         if pair[0] != pair[1]), min(len(claim), len(expected)))
        errors.append("%s trace disagrees with independent replay at event %d"
                      % (label, mismatch))
    return errors


def compare_documents(producer, expected):
    errors = []
    if not isinstance(producer, dict):
        return {"schema": "crypto.autoresearch.icex_s0_counter_check.v3",
                "gate": "G0-6", "pass": False,
                "errors": ["producer document is not an object"], "queries": []}
    if producer.get("fixture") != expected["fixture"]:
        errors.append("producer fixture disagrees with independent regeneration")
    if producer.get("terms_sha256") != expected["terms_sha256"]:
        errors.append("producer Semaev inventory hash disagrees with pinned input")
    if producer.get("g1_sha256") != expected["g1_sha256"]:
        errors.append("producer G1 source hash disagrees with independent replay")
    if producer.get("operation_spec_sha256") != expected["operation_spec_sha256"]:
        errors.append("producer operation-site contract hash disagrees with independent replay")
    if producer.get("queries_completed") != 20:
        errors.append("producer queries_completed is not exactly 20")

    setup_errors = []
    claimed_setup = producer.get("setup")
    expected_setup = expected["setup"]
    if not isinstance(claimed_setup, dict):
        claimed_setup = {}
        setup_errors.append("setup receipt is absent")
    setup_errors.extend(compare_trace(
        claimed_setup.get("events"), expected_setup["events"], "P setup"))
    setup_claim_raw = claimed_setup.get("raw")
    if isinstance(setup_claim_raw, dict):
        setup_claim_raw = dict(setup_claim_raw,
                               units=claimed_setup.get("units"))
    setup_errors.extend(compare_aggregate(
        setup_claim_raw, expected_setup["raw"], expected_setup["units"], "P setup"))
    if claimed_setup.get("units") != expected_setup["units"]:
        setup_errors.append("P setup reported units disagree with independent replay")

    operation_log = producer.get("operation_log")
    if not isinstance(operation_log, list):
        operation_log = []
        errors.append("operation_log is not a list")
    if len(operation_log) != 20:
        errors.append("operation_log does not contain exactly 20 queries")

    rows = []
    for index in range(20):
        query_errors = []
        claim = operation_log[index] if index < len(operation_log) else {}
        wanted = expected["operation_log"][index]
        if not isinstance(claim, dict):
            claim = {}
            query_errors.append("query row is not an object")
        for field in ("attempt", "scalar", "target"):
            if claim.get(field) != wanted[field]:
                query_errors.append(field + " disagrees with independent regeneration")
        query_errors.extend(compare_trace(
            claim.get("events"), wanted["events"], "query %d" % index))
        expected_raw, expected_contract_errors = operation_spec.aggregate(wanted["events"])
        query_errors.extend("independent replay " + error
                            for error in expected_contract_errors)
        producer_components = claim.get("components")
        producer_reported = claim.get("reported_units")
        if not isinstance(producer_components, dict):
            producer_components = {}
            query_errors.append("components is not an object")
        if not isinstance(producer_reported, dict):
            producer_reported = {}
            query_errors.append("reported_units is not an object")
        components = {}
        for component in COMPONENTS:
            raw = expected_raw[component]
            calculated = units(raw)
            component_errors = compare_aggregate(
                producer_components.get(component), raw, calculated, component)
            if producer_reported.get(component) != calculated:
                component_errors.append(
                    component + " reported_units disagrees with independent replay")
            query_errors.extend(component_errors)
            components[component] = {
                "independent_replay_raw": raw,
                "independent_replay_units": calculated,
                "pass": not component_errors,
                "errors": component_errors,
            }
        rows.append({"attempt": index, "expected_events": len(wanted["events"]),
                     "components": components, "pass": not query_errors,
                     "errors": query_errors})

    passed = (not errors and not setup_errors and len(rows) == 20
              and all(row["pass"] for row in rows))
    return {
        "schema": "crypto.autoresearch.icex_s0_counter_check.v3",
        "gate": "G0-6", "queries_required": 20, "queries_checked": len(rows),
        "formula": "units = mul + 10*inv + probes + 13*point_add",
        "producer_counters_or_events_are_expected_inputs": False,
        "expected_trace_source": (
            "independent regeneration of the frozen smoke fixture, targets, setup, "
            "and deterministic G1 replay plus s0_operation_spec.py"),
        "setup": {"pass": not setup_errors, "errors": setup_errors,
                  "expected_events": len(expected_setup["events"]),
                  "expected_units": expected_setup["units"]},
        "pass": passed, "errors": errors, "queries": rows,
    }


def check_document(producer, expected=None):
    return compare_documents(producer, expected if expected is not None else expected_document())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation_log_json")
    args = parser.parse_args()
    try:
        with open(args.operation_log_json, "r") as handle:
            producer = json.load(handle)
        result = check_document(producer)
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as error:
        print("counter checker input/replay failure: %s" % error, file=sys.stderr)
        raise SystemExit(3)
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    # Semantic disagreement is encoded in the receipt.  A nonzero process
    # status is reserved for checker infrastructure failure.
    raise SystemExit(0)


if __name__ == "__main__":
    main()
