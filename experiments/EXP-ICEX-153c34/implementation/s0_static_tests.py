#!/usr/bin/env python3
"""Deterministic offline checks for the ICEX S0 implementation.

This file deliberately does not call a gate, Sage, Docker, Modal, C-7, or a
frozen scientific draw.  It checks local algebra helpers, event-log replay,
the fail-closed remote request contract, and static lifecycle/governance
properties before an immutable implementation is offered for re-audit.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
from pathlib import Path
from unittest import mock

import g1_s0 as g1
import o5_group
import s0_counter_checker as checker
import s0_counter_reference as counter_reference
import s0_driver as driver
import s0_gate_worker as gate_worker
import s0_modal_sage as modal_adapter
import s0_operation_spec as operation_spec


HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _events_for_components(components):
    events = []
    for component in components:
        for site, (operation, allowed) in sorted(operation_spec.SITE_SPEC.items()):
            if component in allowed:
                events.append({"sequence": len(events), "component": component,
                               "operation": operation, "count": 1, "site": site})
    return events


def _aggregates(events, components):
    raw, errors = operation_spec.aggregate(events)
    assert not errors
    aggregates = {component: dict(raw[component], units=checker.units(raw[component]))
                  for component in components}
    reported = {component: aggregates[component]["units"] for component in components}
    return aggregates, reported


def synthetic_documents():
    setup_events = _events_for_components(("P",))
    setup_raw, errors = operation_spec.aggregate(setup_events)
    assert not errors
    setup_receipt = dict(setup_raw["P"], units=checker.units(setup_raw["P"]))
    query_events = _events_for_components(checker.COMPONENTS)
    components, reported = _aggregates(query_events, checker.COMPONENTS)
    expected_queries, producer_queries = [], []
    for attempt in range(20):
        result = {
            "status": "ok", "member": bool(attempt % 2),
            "candidate_xs": [[attempt] * 5], "decompositions": [],
            "basis_size": attempt + 1, "f6_terms": attempt + 2,
        }
        expected_queries.append({
            "attempt": attempt, "scalar": attempt,
            "target": [attempt, attempt + 1], "result": result,
            "components": json.loads(json.dumps(components)),
        })
        producer_queries.append({
            "attempt": attempt, "scalar": attempt,
            "target": [attempt, attempt + 1], "result": dict(result),
            "events": json.loads(json.dumps(query_events)),
            "components": json.loads(json.dumps(components)),
            "reported_units": dict(reported),
        })
    expected = {
        "fixture": {"fixture_id": "offline-operation-contract"},
        "terms_sha256": "offline-operation-contract",
        "setup": {"fingerprint_sha256": "offline-setup", **setup_receipt},
        "queries_completed": 20, "queries": expected_queries,
    }
    producer = {
        "fixture": expected["fixture"], "terms_sha256": expected["terms_sha256"],
        "producer_source_sha256": checker.source_hashes(),
        "setup": {"fingerprint_sha256": "offline-setup",
                  "events": setup_events, **setup_receipt},
        "queries_completed": 20, "operation_log": producer_queries,
    }
    return producer, expected


def check_counter_replay():
    document, expected = synthetic_documents()
    assert checker.compare_documents(document, expected)["pass"] is True

    # Every registered setup and query site is subjected independently to an
    # omission and to a semantic tamper.  The expected trace is held fixed.
    tested_pairs = []
    for location, events in (("setup", document["setup"]["events"]),
                             ("query", document["operation_log"][0]["events"])):
        for index, event in enumerate(events):
            pair = (location, event["component"], event["site"])
            tested_pairs.append(pair)
            omitted = json.loads(json.dumps(document))
            target = (omitted["setup"]["events"] if location == "setup"
                      else omitted["operation_log"][0]["events"])
            target.pop(index)
            for sequence, row in enumerate(target):
                row["sequence"] = sequence
            assert checker.compare_documents(omitted, expected)["pass"] is False

            tampered = json.loads(json.dumps(document))
            target = (tampered["setup"]["events"] if location == "setup"
                      else tampered["operation_log"][0]["events"])
            target[index]["count"] += 1
            assert checker.compare_documents(tampered, expected)["pass"] is False

    aggregate_tamper = json.loads(json.dumps(document))
    aggregate_tamper["operation_log"][7]["components"]["G"]["mul"] += 1
    assert checker.compare_documents(aggregate_tamper, expected)["pass"] is False
    source_tamper = json.loads(json.dumps(document))
    source_tamper["producer_source_sha256"]["g1_s0.py"] = "0" * 64
    assert checker.compare_documents(source_tamper, expected)["pass"] is False
    result_tamper = json.loads(json.dumps(document))
    result_tamper["operation_log"][3]["result"]["basis_size"] += 1
    assert checker.compare_documents(result_tamper, expected)["pass"] is False
    return {"queries": 20, "tampered_aggregate_rejected": True,
            "tampered_source_binding_rejected": True,
            "tampered_arithmetic_result_rejected": True,
            "site_component_pairs_with_omission_and_tamper_tests": len(tested_pairs),
            "registered_sites": len(operation_spec.SITE_SPEC)}


def check_independent_counter_inputs():
    producer_fixture, _deck = gate_worker.smoke_fixture(7, 2)
    checker_fixture = counter_reference.smoke_fixture(7, 2)
    assert producer_fixture == checker_fixture
    for attempt in range(20):
        producer_scalar, producer_target = gate_worker.attempt_target(
            producer_fixture, attempt)
        checker_scalar, checker_target = counter_reference.target_for(
            checker_fixture, attempt)
        assert (producer_scalar, producer_target) == (checker_scalar, checker_target)
    return {"fixture_byte_equal": True, "targets_equal": 20,
            "independent_reference_imports_g1": False,
            "producer_functions_called": ["smoke_fixture", "attempt_target"],
            "gate_functions_called": []}


def check_proves_too_much_regression():
    reference_output, reference_receipt = counter_reference.reference_pseudo_basis(
        101, 2, 3, 7)
    normal = g1.Counters()
    normal_output = g1._d2_pseudo_basis(101, 2, 3, 7, normal)
    assert normal_output == reference_output
    assert normal.totals() == reference_receipt

    class MissingProducerCharge(g1.Counters):
        def charge(self, operation, count=1, site="unspecified"):
            if site == "d2_target.a_square":
                return
            return super().charge(operation, count, site)

    missing = MissingProducerCharge()
    missing_output = g1._d2_pseudo_basis(101, 2, 3, 7, missing)
    assert missing_output == reference_output
    assert missing.totals()["mul"] == reference_receipt["mul"] - 1
    assert checker.compare_receipt(
        missing.totals(), reference_receipt, "proves-too-much")

    # A coherent producer forgery deletes both a trace charge and its reported
    # total while leaving the arithmetic result unchanged.  Trace-vs-total
    # self-consistency still passes; the standalone semantic total rejects it.
    producer, expected = synthetic_documents()
    query = producer["operation_log"][0]
    index = next(index for index, event in enumerate(query["events"])
                 if event["component"] == "S" and event["operation"] == "mul")
    deleted = query["events"].pop(index)
    assert deleted["count"] == 1
    for sequence, event in enumerate(query["events"]):
        event["sequence"] = sequence
    query["components"]["S"]["mul"] -= 1
    query["components"]["S"]["units"] -= 1
    query["reported_units"]["S"] -= 1
    assert not checker.compare_trace_claim(
        query["events"], query["components"], checker.COMPONENTS,
        "coherent deletion")
    checked = checker.compare_documents(producer, expected)
    assert checked["pass"] is False
    assert query["result"] == expected["queries"][0]["result"]
    return {
        "actual_arithmetic_output_unchanged": True,
        "actual_deleted_charge_count": 1,
        "coherent_trace_and_total_forgery_rejected": True,
        "independent_reference_mul": reference_receipt["mul"],
    }


def check_reference_component_units():
    # Fixed unit inputs, not a smoke fixture or query draw, exercise every
    # independently implemented component without invoking G0-6.
    producer_setup_count = g1.Counters()
    producer_setup_count.set_component("P")
    producer_setup = g1.d2_setup(
        101, 2, 3, (1, 3), checker.TERMS, producer_setup_count)
    reference_setup_count = counter_reference.PrimitiveCount()
    reference_setup = counter_reference.build_setup(
        101, 2, 3, (1, 3), checker.TERMS, reference_setup_count)
    assert producer_setup_count.totals() == reference_setup_count.receipt()
    assert (gate_worker.setup_fingerprint(producer_setup)
            == counter_reference.setup_fingerprint(reference_setup))

    specialised_units = {}
    for label, target_x in (("finite", 7), ("zero_target", None)):
        producer_s_count = g1.Counters()
        reference_s_count = counter_reference.PrimitiveCount()
        if target_x is None:
            producer_polynomial = g1.d2_zero_target(
                producer_setup, producer_s_count)
            reference_polynomial = counter_reference.zero_target(
                reference_setup, reference_s_count)
        else:
            producer_polynomial = g1.d2_specialise(
                producer_setup, target_x, producer_s_count)
            reference_polynomial = counter_reference.specialise(
                reference_setup, target_x, reference_s_count)
        assert producer_polynomial.terms == reference_polynomial.terms
        assert producer_s_count.totals() == reference_s_count.receipt()
        specialised_units[label] = reference_s_count.units()

    polynomial_terms = (
        {(2, 0): 1, (0, 0): -1},
        {(0, 2): 1, (0, 0): -1},
        {(1, 0): 1, (0, 1): -1},
    )
    producer_g_count = g1.Counters()
    reference_g_count = counter_reference.PrimitiveCount()
    producer_basis = g1.buchberger(
        [g1.SparsePoly(2, terms) for terms in polynomial_terms],
        101, producer_g_count)
    reference_basis = counter_reference.buchberger(
        [counter_reference.RefSparse(2, terms) for terms in polynomial_terms],
        101, reference_g_count)
    assert ([poly.terms for poly in producer_basis]
            == [poly.terms for poly in reference_basis])
    assert producer_g_count.totals() == reference_g_count.receipt()

    producer_x_count = g1.Counters()
    reference_x_count = counter_reference.PrimitiveCount()
    producer_roots = g1.extract_lex_roots(
        [], [], (1, 2), 101, producer_x_count,
        indicator=g1.indicator_coefficients((1, 2), 101))
    reference_roots = counter_reference.extract_roots(
        [], [], (1, 2), 101,
        counter_reference.indicator((1, 2), 101), reference_x_count)
    assert producer_roots == reference_roots
    assert producer_x_count.totals() == reference_x_count.receipt()

    fixture = {"p": 101, "a": 2, "b": 3}
    points = {1: o5_group.canonical_point(101, 2, 3, 1)}
    candidates = [(1, 1, 1, 1, 1)]
    producer_v_count = g1.Counters()
    reference_v_count = counter_reference.PrimitiveCount()
    producer_decompositions = g1.signed_recovery(
        fixture, candidates, None, producer_v_count, points=points)
    reference_decompositions = counter_reference.recover(
        fixture, candidates, None, points, reference_v_count)
    assert producer_decompositions == reference_decompositions
    assert producer_v_count.totals() == reference_v_count.receipt()
    return {
        "fixed_unit_inputs_only": True,
        "p_setup_fingerprint_equal": True,
        "p_setup_units": reference_setup_count.units(),
        "s_polynomial_and_totals_equal": True,
        "s_units": specialised_units,
        "g_basis_and_totals_equal": True,
        "x_roots_and_totals_equal": True,
        "v_recovery_and_totals_equal": True,
    }


def check_counter_sites_and_legal_root_branch():
    setup_counter = g1.Counters(trace_operations=True)
    setup_counter.set_component("P")
    g1.indicator_coefficients((1, 2), 101, setup_counter)
    assert setup_counter.events
    assert all(event["component"] == "P" for event in setup_counter.events)
    assert all(not operation_spec.validate_event(event, event["sequence"])
               for event in setup_counter.events)

    counter = g1.Counters(trace_operations=True)
    counter.set_component("S")
    g1._d2_pseudo_basis(101, 2, 3, 7, counter)
    sites = {event["site"] for event in counter.events}
    required = {"d2_target.xR_square", "d2_target.a_xR",
                "d2_target.a_square", "d2_target.b_xR"}
    assert required <= sites
    assert all(not operation_spec.validate_event(event, event["sequence"])
               for event in counter.events)

    root_counter = g1.Counters(trace_operations=True)
    root_counter.set_component("X")
    roots = g1.extract_lex_roots([], [], (1, 2), 101, root_counter,
                                indicator=g1.indicator_coefficients((1, 2), 101))
    # The all-vanishing branch must retain every V candidate at every level;
    # symmetry reduction leaves the six 5-multisets over two values.
    assert len(roots) == 6
    assert all(event["component"] == "X" for event in root_counter.events)
    source = inspect.getsource(g1.g1_membership)
    assert 'setup["indicator_generators"]' in source
    assert 'setup["points"]' in source
    assert "itertools.product(V" not in inspect.getsource(g1)
    return {"target_setup_sites": sorted(required),
            "p_setup_trace_events_checked": len(setup_counter.events),
            "registered_operation_sites": len(operation_spec.SITE_SPEC),
            "legal_all_vanishing_multisets": len(roots)}


def check_operation_spec_source_binding():
    tree = ast.parse((HERE / "g1_s0.py").read_text())
    used = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr == "charge":
            for keyword in node.keywords:
                if (keyword.arg == "site" and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)):
                    used.add(keyword.value.value)
        if (isinstance(node.func, ast.Name) and node.func.id == "_counted_mul"
                and node.args and isinstance(node.args[-1], ast.Constant)):
            used.add(node.args[-1].value)
        if isinstance(node.func, ast.Name) and node.func.id == "_fp_pow":
            for keyword in node.keywords:
                if keyword.arg == "site_prefix" and isinstance(keyword.value, ast.Constant):
                    used.add(keyword.value.value + ".accumulate")
                    used.add(keyword.value.value + ".square")
    # Calls which accept the default _fp_pow prefix are deliberately explicit
    # here: the prefix is part of the independently reviewed site contract.
    used.update(("fp_pow.accumulate", "fp_pow.square"))
    assert used == set(operation_spec.SITE_SPEC), (
        sorted(used - set(operation_spec.SITE_SPEC)),
        sorted(set(operation_spec.SITE_SPEC) - used))
    return {"source_sites": len(used), "contract_sites": len(operation_spec.SITE_SPEC),
            "exact_set_equal": True}


def check_o5_group():
    # Explicit y=0 lift plus closure/identity/inverse/commutativity/associativity
    # on several small nonsingular curves.  Sage remains the retained,
    # independent cross-check executed by G0-2.
    assert o5_group.canonical_point(5, 1, 0, 0) == (0, 0)
    cases = 0
    for p, a, b in ((5, 1, 0), (7, 2, 3), (11, 1, 6)):
        points = [None]
        for x in range(p):
            point = o5_group.canonical_point(p, a, b, x)
            if point is not None:
                assert (point[1] ** 2 - (point[0] ** 3 + a * point[0] + b)) % p == 0
                points.extend((point, (point[0], (-point[1]) % p)))
        unique = []
        for point in points:
            if point not in unique:
                unique.append(point)
        for left in unique:
            assert o5_group.point_add(None, left, p, a) == left
            assert o5_group.point_add(left, None, p, a) == left
            if left is not None:
                inverse = (left[0], (-left[1]) % p)
                assert o5_group.point_add(left, inverse, p, a) is None
            for right in unique:
                assert (o5_group.point_add(left, right, p, a)
                        == o5_group.point_add(right, left, p, a))
                cases += 1
        sample = unique[:min(7, len(unique))]
        for left in sample:
            for middle in sample:
                for right in sample:
                    lhs = o5_group.point_add(
                        o5_group.point_add(left, middle, p, a), right, p, a)
                    rhs = o5_group.point_add(
                        left, o5_group.point_add(middle, right, p, a), p, a)
                    assert lhs == rhs
                    cases += 1
    return {"small_curve_group_cases": cases, "sage_crosscheck_retained": True}


def check_raw_c7_boundary():
    threshold = 20 * 1024 ** 3
    reading = {
        "loadavg_15m": 14.0, "load_limit": 14.0,
        "root_free_bytes": 5 * 1024 ** 3, "root_free_min_bytes": 5 * 1024 ** 3,
        "repository_volume_exists": True,
        "repository_free_bytes": threshold,
        "repository_free_min_bytes": threshold,
        "nice_actual": 10, "nice_required": 10,
    }
    assert driver.c7_ok(reading) is True
    reading["repository_free_bytes"] = threshold - 1
    assert driver.c7_ok(reading) is False
    assert driver.MANDATED_REPOSITORY_VOLUME == Path("/Volumes/SSD990")
    assert driver.MANDATED_TMPDIR == Path("/Volumes/SSD990/.tmp-agent")
    assert driver.PORTABILITY_AUTHORIZED is False
    assert driver.EXECUTION_CHECKPOINT == (
        driver.REPO / "ledger/goals/GOAL-ICEX-001/checkpoints/BATCH-454f85.yaml")
    assert sha256(driver.EXECUTION_CHECKPOINT) == driver.EXECUTION_CHECKPOINT_SHA256
    assert driver.CHECKPOINT_EXECUTION_ADMITTED is False
    return {"raw_bytes_exact_threshold_passes": True,
            "one_byte_below_fails": True,
            "portable_substitution_authorized": False,
            "checkpoint_execution_admitted": False}


def check_modal_contract():
    def row(path, name, role):
        data = Path(path).read_bytes()
        return {"name": name, "role": role, "sha256": hashlib.sha256(data).hexdigest(),
                "content_base64": __import__("base64").b64encode(data).decode("ascii")}

    # G0-1 is intentionally not run here, so its future panel JSON is replaced
    # by a harmless object solely to exercise the bounded transport schema.
    panel_bytes = b'{"offline_contract_only":true}\n'
    panel_row = {"name": "panel_fixtures.json", "role": "input",
                 "sha256": hashlib.sha256(panel_bytes).hexdigest(),
                 "content_base64": __import__("base64").b64encode(panel_bytes).decode("ascii")}
    request = {
        "schema": modal_adapter.SCHEMA, "request_sha256": "",
        "image": modal_adapter.SAGE_IMAGE,
        "image_digest": modal_adapter.SAGE_IMAGE_DIGEST,
        "script": "s0_sage_gates.py",
        "argv": ["--gate", "G0-2", "--v4", "ic_leads_fixtures_v2.json",
                 "--panel", "panel_fixtures.json",
                 "--inventory", "semaev_polys.json",
                 "--o5-group", "o5_group.py"],
        "files": [
            row(driver.SAGE_GATES, "s0_sage_gates.py", "script"),
            row(driver.V4_JSON, "ic_leads_fixtures_v2.json", "input"), panel_row,
            row(driver.SEMAEV_INVENTORY, "semaev_polys.json", "input"),
            row(driver.O5_GROUP, "o5_group.py", "input"),
        ],
        "timeout_seconds": 7200,
        "resources": {"cpu": 1.0, "memory_mib": 8192, "max_containers": 1,
                      "retries": 0, "nice": 10, "rlimit_as_bytes": 8 * 1024 ** 3,
                      "network": "blocked", "single_use_container": True},
        "environment": {"HOME": "/tmp", "OMP_NUM_THREADS": "1",
                        "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                        "NUMEXPR_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1",
                        "VECLIB_MAXIMUM_THREADS": "1"},
    }
    request["request_sha256"] = modal_adapter.request_digest(request)
    decoded = modal_adapter.validate_request(request)
    first = modal_adapter.deterministic_tar(decoded)
    second = modal_adapter.deterministic_tar(decoded)
    assert first == second
    assert request["image_digest"] == driver.SAGE_IMAGE_DIGEST
    assert len(request["files"]) == 5
    tampered = json.loads(json.dumps(request))
    tampered["argv"][-1] = "different.py"
    tampered["request_sha256"] = modal_adapter.request_digest(tampered)
    try:
        modal_adapter.validate_request(tampered)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered G0-2 call shape was accepted")
    return {"files": len(request["files"]), "bundle_bytes": len(first),
            "bundle_sha256": hashlib.sha256(first).hexdigest(),
            "tampered_call_shape_rejected": True}


def check_backend_aware_gate_parsing():
    modal = {
        "backend": "modal", "command": ["sage"],
        "started_at": "offline", "finished_at": "offline",
        "returncode": 0, "stdout_bytes": b'{"pass":true}',
        "stderr_bytes": b"", "timeout": False,
        "sandbox_termination_confirmed": True,
        "modal_sandbox_id": "sb-offline-regression",
        "worker": {"termination_error": None},
    }
    native = {
        "backend": "native", "command": ["python"],
        "started_at": "offline", "finished_at": "offline",
        "returncode": 0, "stdout": '{"pass":true}', "stderr": "",
        "timeout": False, "process_group_reaped": True,
        "lifecycle_error": None,
    }
    evidence = driver.EVIDENCE / "offline-never-written.json"
    with (mock.patch.object(driver, "write_json") as write_json,
          mock.patch.object(driver, "run_sage", return_value=modal) as run_sage):
        modal_record = driver.run_g02(Path("/offline-not-used"))
        native_record = driver.run_json_gate("G0-3", native, evidence)
        unconfirmed_modal = dict(modal, sandbox_termination_confirmed=False,
                                 process_group_reaped=True)
        unconfirmed_modal_record = driver.run_json_gate(
            "G0-2", unconfirmed_modal, evidence)
        unreaped_native = dict(native, process_group_reaped=False,
                               sandbox_termination_confirmed=True)
        unreaped_native_record = driver.run_json_gate(
            "G0-3", unreaped_native, evidence)
    assert write_json.call_count == 4
    assert run_sage.call_count == 1
    assert modal_record["pass"] is True
    assert modal_record["execution_backend"] == "modal"
    assert modal_record["sandbox_termination_confirmed"] is True
    assert "native_process_group_reaped" not in modal_record
    assert native_record["pass"] is True
    assert native_record["execution_backend"] == "native"
    assert native_record["native_process_group_reaped"] is True
    assert "sandbox_termination_confirmed" not in native_record
    assert unconfirmed_modal_record["blocked"] is True
    assert unconfirmed_modal_record["sandbox_termination_confirmed"] is False
    assert unreaped_native_record["blocked"] is True
    assert unreaped_native_record["native_process_group_reaped"] is False
    return {
        "confirmed_modal_without_native_reap_field_passes": True,
        "modal_termination_failure_rejected_despite_native_field": True,
        "confirmed_native_reaping_passes": True,
        "native_reaping_failure_rejected_despite_modal_field": True,
    }


def check_audited_source_manifest_binding():
    document = driver.yaml.safe_load(driver.IMPLEMENTATION_REPORT.read_text())
    checked = driver.implementation_manifest_preflight(document)
    assert checked["pass"] is True
    assert checked["source_paths_exact"] is True
    assert len(checked["files"]) == len(driver.AUDITED_SOURCE_FILES) == 12
    assert all(row["pass"] for row in checked["files"])

    tampered_hash = json.loads(json.dumps(document))
    source_row = next(row for row in tampered_hash["files"]
                      if row["path"] == driver.AUDITED_SOURCE_FILES[0])
    source_row["sha256"] = "0" * 64
    assert driver.implementation_manifest_preflight(tampered_hash)["pass"] is False

    missing_source = json.loads(json.dumps(document))
    missing_source["files"] = [
        row for row in missing_source["files"]
        if row["path"] != driver.AUDITED_SOURCE_FILES[-1]
    ]
    assert driver.implementation_manifest_preflight(missing_source)["pass"] is False

    wrong_commit = json.loads(json.dumps(document))
    wrong_commit["implementation_commit"] = "0" * 40
    assert driver.implementation_manifest_preflight(wrong_commit)["pass"] is False
    return {
        "audited_source_files": len(checked["files"]),
        "current_and_commit_hashes_equal_manifest": True,
        "tampered_hash_rejected": True,
        "missing_source_rejected": True,
        "unavailable_source_commit_rejected": True,
    }


def check_static_lifecycle_and_sage_bindings():
    native_source = inspect.getsource(driver.run_native)
    cleanup_source = inspect.getsource(driver._terminate_and_reap_process_group)
    assert "start_new_session=True" in native_source
    assert "_terminate_and_reap_process_group" in native_source
    assert "except BaseException" in native_source
    assert '"backend": "native"' in native_source
    assert "os.killpg" in cleanup_source
    assert "signal.SIGTERM" in cleanup_source
    assert "signal.SIGKILL" in cleanup_source
    assert "process.wait" in cleanup_source
    assert "group_gone" in cleanup_source
    driver_source = inspect.getsource(driver)
    assert "unconfirmed Modal sandbox termination" in driver_source
    assert "unconfirmed native process-group reaping" in driver_source
    main_source = inspect.getsource(driver.main)
    assert (main_source.index("implementation_manifest_preflight()")
            < main_source.index("machine_reading()"))
    assert "audited implementation source manifest mismatch" in main_source
    assert "pinned checkpoint explicitly says execution not admitted" in driver_source
    assert "dir=MANDATED_TMPDIR" in driver_source
    assert 'choices=("modal",)' in driver_source
    assert 'if SAGE_BACKEND != "modal"' in driver_source
    assert "non-Modal backend refused before launch" in driver_source
    sage_source = driver.SAGE_GATES.read_text()
    assert "f4_inventory_equal" in sage_source
    assert "f5_inventory_equal" in sage_source
    assert "o5_group_crosscheck" in sage_source
    assert 'parser.add_argument("--inventory", required=True)' in sage_source
    worker_source = driver.WORKER.read_text()
    assert "trace_operations=True" in worker_source
    assert "leading_degree_drop_control" in worker_source
    assert "zero_target_control" in worker_source
    assert '"actual_d2_specialise_checks": len(samples)' in worker_source
    assert '"independent_bareiss_checks": len(samples)' in worker_source
    checker_source = driver.COUNTER_CHECKER.read_text()
    assert "standalone s0_counter_reference.py" in checker_source
    assert "producer_counters_or_events_are_expected_inputs" in checker_source
    checker_imports = {
        alias.name
        for node in ast.walk(ast.parse(checker_source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "g1_s0" not in checker_imports
    assert "o5_group" not in checker_imports

    reference_source = (HERE / "s0_counter_reference.py").read_text()
    reference_imports = {
        alias.name
        for node in ast.walk(ast.parse(reference_source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not ({"g1_s0", "o5_group", "s0_operation_spec"} & reference_imports)
    assert "def expected_document" in reference_source
    assert "def membership" in reference_source
    return {"native_process_group_kill": True,
            "native_abnormal_path_reap_and_global_stop": True,
            "modal_global_stop": True,
            "non_modal_sage_refused": True,
            "standalone_counter_import_independence": True,
            "inventory_and_o5_sage_bindings": True,
            "d2_all_tuple_and_d6_controls_present": True}


def main():
    checks = {
        "counter_replay": check_counter_replay(),
        "counter_input_regeneration": check_independent_counter_inputs(),
        "proves_too_much_regression": check_proves_too_much_regression(),
        "reference_component_units": check_reference_component_units(),
        "counter_sites_and_roots": check_counter_sites_and_legal_root_branch(),
        "operation_spec_source_binding": check_operation_spec_source_binding(),
        "o5_group": check_o5_group(),
        "raw_c7_boundary": check_raw_c7_boundary(),
        "modal_contract": check_modal_contract(),
        "backend_aware_gate_parsing": check_backend_aware_gate_parsing(),
        "audited_source_manifest": check_audited_source_manifest_binding(),
        "static_bindings": check_static_lifecycle_and_sage_bindings(),
    }
    result = {
        "schema": "crypto.autoresearch.icex_s0_static_tests.v1",
        "mode": "offline_static_only",
        "gates_or_external_workers_invoked": False,
        "pass": True,
        "checks": checks,
        "source_sha256": {
            name: sha256(HERE / name) for name in (
                "g1_s0.py", "o5_group.py", "s0_counter_checker.py",
                "s0_counter_reference.py", "s0_driver.py", "s0_gate_worker.py",
                "s0_modal_sage.py", "s0_operation_spec.py", "s0_sage_gates.py")
        },
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
