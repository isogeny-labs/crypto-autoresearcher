#!/usr/bin/env python3
"""Independent semantic counter checker for ICEX gate G0-6.

The expected arithmetic and primitive totals come exclusively from
``s0_counter_reference``.  That module imports neither the G1 producer nor
the producer's operation-site registry and implements its own counted
arithmetic path.  Producer events are retained only as an auxiliary claim:
``s0_operation_spec`` validates their vocabulary and this checker verifies
that they aggregate to the producer's reported totals.  They never define an
expected value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import s0_counter_reference as reference
import s0_operation_spec as operation_spec


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TERMS = REPO / "experiments/EXP-SDEG-85eefd/implementation/semaev_polys.json"
TERMS_SHA256 = "447d9bfff27f2b57b50e60fffde0c380ab697f4b2cbf006114bb7a50be10642e"
COMPONENTS = reference.COMPONENTS
RAW_FIELDS = reference.FIELDS


def units(raw):
    return raw["mul"] + 10 * raw["inv"] + raw["probes"] + 13 * raw["point_add"]


def source_hashes():
    return {
        "g1_s0.py": hashlib.sha256((HERE / "g1_s0.py").read_bytes()).hexdigest(),
        "s0_operation_spec.py": hashlib.sha256(
            (HERE / "s0_operation_spec.py").read_bytes()).hexdigest(),
    }


def expected_document():
    return reference.expected_document(TERMS, TERMS_SHA256)


def compare_receipt(claim, expected, label):
    errors = []
    if not isinstance(claim, dict):
        return [label + " primitive receipt is absent"]
    for field in RAW_FIELDS:
        value = claim.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(label + " %s is not a nonnegative integer" % field)
        elif value != expected[field]:
            errors.append(label + " %s disagrees with independent reference" % field)
    raw = {field: claim.get(field) for field in RAW_FIELDS}
    if all(isinstance(value, int) and not isinstance(value, bool) and value >= 0
           for value in raw.values()):
        if claim.get("units") != units(raw):
            errors.append(label + " units are inconsistent with producer raw totals")
    if claim.get("units") != expected["units"]:
        errors.append(label + " units disagree with independent reference")
    return errors


def compare_trace_claim(events, receipts, components, label):
    """Validate producer events only against its own primitive receipts."""
    if not isinstance(events, list):
        return [label + " producer event trace is not a list"]
    aggregate, contract_errors = operation_spec.aggregate(events)
    errors = [label + " producer trace " + error for error in contract_errors]
    for component in components:
        receipt = receipts.get(component) if isinstance(receipts, dict) else None
        if not isinstance(receipt, dict):
            errors.append(label + " has no %s receipt for trace comparison" % component)
            continue
        for field in RAW_FIELDS:
            if aggregate[component][field] != receipt.get(field):
                errors.append(
                    "%s producer %s trace does not aggregate to reported %s"
                    % (label, component, field))
    return errors


def _canonical_hash(document):
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def compare_documents(producer, expected):
    errors = []
    if not isinstance(producer, dict):
        return {
            "schema": "crypto.autoresearch.icex_s0_counter_check.v4",
            "gate": "G0-6", "pass": False,
            "errors": ["producer document is not an object"], "queries": [],
        }

    if producer.get("fixture") != expected["fixture"]:
        errors.append("producer fixture disagrees with independent regeneration")
    if producer.get("terms_sha256") != expected["terms_sha256"]:
        errors.append("producer Semaev inventory hash disagrees with pinned input")
    if producer.get("producer_source_sha256") != source_hashes():
        errors.append("producer source hashes disagree with files checked by this process")
    if producer.get("queries_completed") != 20:
        errors.append("producer queries_completed is not exactly 20")

    setup_errors = []
    claimed_setup = producer.get("setup")
    expected_setup = expected["setup"]
    if not isinstance(claimed_setup, dict):
        claimed_setup = {}
        setup_errors.append("setup receipt is absent")
    if claimed_setup.get("fingerprint_sha256") != expected_setup["fingerprint_sha256"]:
        setup_errors.append("P setup arithmetic fingerprint disagrees with independent setup")
    setup_errors.extend(compare_receipt(claimed_setup, expected_setup, "P setup"))
    setup_errors.extend(compare_trace_claim(
        claimed_setup.get("events"), {"P": claimed_setup}, ("P",), "P setup"))

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
        wanted = expected["queries"][index]
        if not isinstance(claim, dict):
            claim = {}
            query_errors.append("query row is not an object")
        for field in ("attempt", "scalar", "target"):
            if claim.get(field) != wanted[field]:
                query_errors.append(field + " disagrees with independent regeneration")
        if claim.get("result") != wanted["result"]:
            query_errors.append("arithmetic result disagrees with independent reference")

        producer_components = claim.get("components")
        if not isinstance(producer_components, dict):
            producer_components = {}
            query_errors.append("components is not an object")
        producer_reported = claim.get("reported_units")
        if not isinstance(producer_reported, dict):
            producer_reported = {}
            query_errors.append("reported_units is not an object")

        query_errors.extend(compare_trace_claim(
            claim.get("events"), producer_components, COMPONENTS,
            "query %d" % index))
        component_rows = {}
        for component in COMPONENTS:
            expected_receipt = wanted["components"][component]
            component_errors = compare_receipt(
                producer_components.get(component), expected_receipt,
                "query %d %s" % (index, component))
            if producer_reported.get(component) != expected_receipt["units"]:
                component_errors.append(
                    "query %d %s reported_units disagrees with independent reference"
                    % (index, component))
            query_errors.extend(component_errors)
            component_rows[component] = {
                "independent_reference": expected_receipt,
                "pass": not component_errors,
                "errors": component_errors,
            }
        rows.append({
            "attempt": index,
            "independent_result_sha256": _canonical_hash(wanted["result"]),
            "components": component_rows,
            "pass": not query_errors,
            "errors": query_errors,
        })

    passed = (not errors and not setup_errors and len(rows) == 20
              and all(row["pass"] for row in rows))
    return {
        "schema": "crypto.autoresearch.icex_s0_counter_check.v4",
        "gate": "G0-6", "queries_required": 20,
        "queries_checked": len(rows),
        "formula": "units = mul + 10*inv + probes + 13*point_add",
        "producer_counters_or_events_are_expected_inputs": False,
        "semantic_reference": (
            "standalone s0_counter_reference.py implementation of setup, "
            "D-2, Buchberger, root extraction, and signed recovery"),
        "semantic_reference_sha256": hashlib.sha256(
            Path(reference.__file__).read_bytes()).hexdigest(),
        "producer_trace_role": (
            "auxiliary site-contract and producer-receipt consistency only; "
            "never an expected-total oracle"),
        "setup": {
            "pass": not setup_errors,
            "errors": setup_errors,
            "independent_fingerprint_sha256": expected_setup["fingerprint_sha256"],
            "independent_reference": {
                field: expected_setup[field] for field in (*RAW_FIELDS, "units")
            },
        },
        "pass": passed, "errors": errors, "queries": rows,
    }


def check_document(producer, expected=None):
    return compare_documents(
        producer, expected if expected is not None else expected_document())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation_log_json")
    args = parser.parse_args()
    try:
        with open(args.operation_log_json, "r") as handle:
            producer = json.load(handle)
        result = check_document(producer)
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as error:
        print("counter checker input/reference failure: %s" % error, file=sys.stderr)
        raise SystemExit(3)
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    # Semantic disagreement is encoded in the receipt.  A nonzero status is
    # reserved for checker infrastructure failure.
    raise SystemExit(0)


if __name__ == "__main__":
    main()
