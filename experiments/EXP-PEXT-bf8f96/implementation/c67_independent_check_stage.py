"""Prospective independent C6/C7 replay after sealed run custody.

This is a future approved-run checker. Importing it takes no control sample;
the fixed software tests use placeholder payloads and mocked replay engines.
"""

import argparse
import json
from pathlib import Path
import sys

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from c6_coordinate_control import check_all_slots
from c7_seed_replay import replay as replay_c7
import c67_run_custody as custody


ROOT = custody.ROOT
PREFIX = custody.PREFIX
CHECK = "c67-independent-check.json"
SOURCES = tuple(PREFIX + "implementation/" + name for name in (
    "c67_independent_check_stage.py", "c67_run_custody.py",
    "c67_control_schedule.py", "c6_coordinate_control.py",
    "c7_seed_replay.py", "c7_matched_random.py",
    "candidate_batch.py", "candidate_binding.py", "candidate_build.py",
    "candidate_census_check.py", "candidate_census_driver.py",
    "candidate_stage.py", "candidate_unit_artifact.py",
    "check_all_degree_collision_certificate.py",
    "check_compact_class_inputs.py", "check_curve_class_certificate.py",
    "check_join_certificate.py", "check_rational_collision_certificate.py",
    "check_quotient_certificate.py", "check_structure_certificate.py",
    "generic_disjoint.py", "generic_interval_descent.py",
    "independent_candidate_unit.py", "independent_check.py",
    "independent_component_geometry.py", "independent_source_map_check.py",
    "independent_transversal.py", "input_manifest.py", "join_plan.py",
    "source_map_binding.py", "squareclass_relations.py",
    "target_transport.py", "type2_predicate.py", "type2_unit_scan.py",
))


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def checked_sources(source_hashes):
    """Require the replay source closure in the approved trial plan."""
    _need(isinstance(source_hashes, dict) and set(SOURCES) <= set(source_hashes),
          "C6/C7 independent replay source closure absent")
    observed = {}
    for relative in SOURCES:
        digest = custody.digest(custody._regular(ROOT / relative))
        _need(source_hashes[relative] == digest,
              f"C6/C7 independent replay source hash mismatch: {relative}")
        observed[relative] = digest
    return observed


def recompute(run_dir, admission):
    """Replay every sealed batch; no producer answer is trusted."""
    run_dir = Path(run_dir)
    custody_summary = custody.compare_results(run_dir, admission)
    _need(custody._regular(run_dir / custody.READBACK)
          == custody.canonical(custody_summary),
          "C6/C7 custody readback is absent or differs from retained results")
    binders = {}
    checked = []
    for record, sealed in zip(admission["records"], custody_summary["records"]):
        data = custody._regular(run_dir / record["path"])
        _need(custody.digest(data) == sealed["sha256"],
              "C6/C7 result changed between custody and independent replay")
        payload = json.loads(data)["payload"]
        cohort = record["cohort"]
        if cohort not in binders:
            binders[cohort] = CandidateBinder(cohort, plan_path=join_path(cohort))
        binder = binders[cohort]
        _need(binder.plan_sha256 == record["join_plan_sha256"],
              "C6/C7 published source plan differs from sealed batch")
        if record["control"] == "C6":
            selection = record["selection"]
            expected = check_all_slots(binder, selection["class_index"],
                                       selection["T_index"],
                                       selection["structure_ordinal"])
            _need(payload == expected,
                  "C6 retained control differs from independent source replay")
            result = {"control": "C6", "checked_slots": 16,
                      "invariant_equality": True}
        else:
            result = {"control": "C7", **replay_c7(binder.plan["field"], payload)}
            _need(result.get("valid") is True,
                  "C7 independent seed and geometry replay invalid")
        checked.append({"path": record["path"],
                        "retained_sha256": sealed["sha256"], **result})
    _need(len(checked) == len(admission["records"]),
          "C6/C7 independent replay coverage incomplete")
    return {"schema": "pext.c67-independent-check/v1",
            "status": ("checked_all_controls" if custody_summary["coverage_complete"]
                       else "checked_inconclusive_draw_cap_exhausted"),
            "experiment": custody.EXP,
            **{key: admission[key] for key in (
                "stage", "run_id", "plan_sha256", "schedule_sha256")},
            "admission_sha256": custody.digest(custody.canonical(admission)),
            "custody_readback_sha256": custody.digest(custody.canonical(custody_summary)),
            "coverage_complete": custody_summary["coverage_complete"],
            "records": checked}


def check(trial_plan, run_dir, stage):
    """Require an approved supervisor and write one independent check record."""
    run_dir, admission = custody._preflight(trial_plan, run_dir, stage)
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import load_plan
    plan = load_plan(ROOT, Path(trial_plan))
    trial = next(row for row in plan["trials"] if row["id"] == stage)
    _need(CHECK in trial.get("artifacts", []),
          "C6/C7 independent check absent from approved trial artifacts")
    observed = checked_sources(plan.get("source_sha256"))
    summary = recompute(run_dir, admission)
    summary["source_sha256"] = observed
    data = custody.canonical(summary)
    path = run_dir / CHECK
    if path.exists() or path.is_symlink():
        _need(custody._regular(path) == data,
              "C6/C7 independent check differs from retained replay")
    else:
        custody._write_once(path, data)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=tuple(custody.COHORTS), required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.trial_plan, args.run_dir, args.stage),
                     sort_keys=True))
