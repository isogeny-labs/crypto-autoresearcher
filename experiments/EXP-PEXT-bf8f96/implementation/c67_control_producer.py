"""Prospective approved-run C6/C7 producer within an existing census trial.

This module does no work on import. The future six-stage launcher must call it
only after its ordinary supervisor has admitted the frozen trial plan.
"""

import argparse
import json
from pathlib import Path
import sys

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from c6_coordinate_control import check_all_slots
from c7_matched_random import sample_stratum
import c67_independent_check_stage as independent
import c67_run_custody as custody


ROOT = custody.ROOT
SOURCE = custody.PREFIX + "implementation/c67_control_producer.py"


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def _preflight(trial_plan, run_dir, stage):
    """Refuse an unapproved plan or unbound producer before reserving data."""
    run_dir, admission = custody._preflight(trial_plan, run_dir, stage)
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import load_plan
    plan = load_plan(ROOT, Path(trial_plan))
    hashes = plan.get("source_sha256", {})
    _need(hashes.get(SOURCE) == custody.digest(custody._regular(ROOT / SOURCE)),
          "C6/C7 producer source differs from approved plan")
    independent.checked_sources(hashes)
    trial = next(row for row in plan["trials"] if row["id"] == stage)
    _need(independent.CHECK in trial.get("artifacts", []),
          "C6/C7 independent check absent from approved trial")
    return run_dir, admission


def run_controls(trial_plan, run_dir, stage):
    """Generate the exact scheduled controls once, then seal and replay them."""
    _, admitted = _preflight(trial_plan, run_dir, stage)
    admission = custody.prepare(trial_plan, run_dir, stage)
    _need(admission == admitted, "C6/C7 admission changed between preflight and reservation")
    binders = {}
    written = []
    for record in admission["records"]:
        cohort = record["cohort"]
        if cohort not in binders:
            binders[cohort] = CandidateBinder(cohort, plan_path=join_path(cohort))
        binder = binders[cohort]
        _need(binder.plan_sha256 == record["join_plan_sha256"],
              "C6/C7 producer source plan differs from schedule")
        selection = record["selection"]
        if record["control"] == "C6":
            payload = check_all_slots(binder, selection["class_index"],
                                      selection["T_index"],
                                      selection["structure_ordinal"])
        else:
            payload = sample_stratum(binder.plan["field"], record["pattern"],
                                     selection["scalar_class"], count=16)
        written.append(custody.write_result(trial_plan, run_dir, stage,
                                            record["path"], payload))
    sealed = custody.readback(trial_plan, run_dir, stage)
    checked = independent.check(trial_plan, run_dir, stage)
    _need(checked["coverage_complete"] == sealed["coverage_complete"],
          "C6/C7 producer and independent coverage disagree")
    return {"schema": "pext.c67-control-producer/v1",
            "status": checked["status"], "stage": stage,
            "run_id": admission["run_id"],
            "plan_sha256": admission["plan_sha256"],
            "schedule_sha256": admission["schedule_sha256"],
            "written": written,
            "custody_readback_sha256": custody.digest(custody.canonical(sealed)),
            "independent_check_sha256": custody.digest(custody.canonical(checked)),
            "coverage_complete": checked["coverage_complete"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=tuple(custody.COHORTS), required=True)
    args = parser.parse_args()
    print(json.dumps(run_controls(args.trial_plan, args.run_dir, args.stage),
                     sort_keys=True))
