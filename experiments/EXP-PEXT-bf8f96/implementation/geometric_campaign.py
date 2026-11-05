"""Read-only exact geometric campaign reduction over all four frozen cohorts.

Each cohort is reduced from its sealed units and independent checker output.
This is a P1-P4 count table, not the final control-valid scientific decision.
"""

import hashlib
import json
from pathlib import Path
import sys

from candidate_binding import CandidateBinder
from candidate_build import verify_build
from candidate_stage import COHORTS, join_path, validate_shape
from geometric_reducer import reduce_cohort
from input_manifest import ROOT


EXPECTED = {"q5-n3": (5, 3), "q7-n3": (7, 3),
            "q11-n3": (11, 3), "q3-n5": (3, 5)}


def _record(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"checked campaign artifact missing: {path.name}")
    data = path.read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def aggregate_cohorts(curves, cohorts):
    """Reconcile independent cohort metrics with actual curve rows."""
    if set(cohorts) != set(EXPECTED):
        raise ValueError("geometric campaign cohort coverage incomplete")
    grouped = {name: [] for name in EXPECTED}
    for curve in curves:
        name = curve.get("cohort")
        if name not in grouped:
            raise ValueError("curve belongs to undeclared cohort")
        grouped[name].append(curve)
    for name, rows in grouped.items():
        metrics = cohorts[name]
        if ([row.get("class_index") for row in rows] != list(range(len(rows)))
                or len(rows) != metrics["classes"]
                or sum(row["T_count"] for row in rows) != metrics["T_blocks"]
                or sum(row["strict_geometric_minimum_drop"] for row in rows)
                   != metrics["curves_with_strict_geometric_minimum_drop"]
                or sum(row["branch_type_mismatch_count"] for row in rows)
                   != metrics["branch_type_mismatch_count"]
                or sum(row["geometric_spectrum_violation_count"] for row in rows)
                   != metrics["geometric_spectrum_violation_count"]):
            raise ValueError("geometric cohort totals differ from actual curve rows")
        if EXPECTED[name][1] == 3:
            for key in ("type2_signature_count", "hyperelliptic_predicate_true_count",
                        "hyperelliptic_predicate_false_count"):
                if sum(row[key] for row in rows) != metrics[key]:
                    raise ValueError("Type2 cohort total differs from actual curve rows")
        elif any("type2_signature_count" in row for row in rows):
            raise ValueError("noncubic curve has Type2 counts")
    counts = {key: sum(row[key] for row in cohorts.values()) for key in (
        "classes", "T_blocks", "structures", "exceptional", "generic",
        "branch_type_mismatch_count", "geometric_spectrum_violation_count",
        "curves_with_strict_geometric_minimum_drop")}
    return {"schema": "pext.geometric-campaign/v1",
            "status": "complete_checked_geometric_counts; controls_and_descent_pending",
            "cohorts": cohorts, "totals": counts,
            "p3_geometric_drop_by_cohort": {name: cohorts[name][
                "curves_with_strict_geometric_minimum_drop"] for name in EXPECTED},
            "type2_by_cubic_cohort": {name: {key: cohorts[name][key]
                for key in ("type2_signature_count",
                            "hyperelliptic_predicate_true_count",
                            "hyperelliptic_predicate_false_count")}
                for name in EXPECTED if EXPECTED[name][1] == 3}}


def reduce_campaign(trial_plan, stage_dirs):
    """Require exact candidate-stage checks, then reduce every planned curve/T."""
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import load_plan, run_root, sha256, trial_state
    trial_plan = Path(trial_plan)
    plan = load_plan(ROOT, trial_plan)
    if plan["experiment_id"] != "EXP-PEXT-bf8f96":
        raise ValueError("geometric campaign trial plan experiment mismatch")
    trials = {row["id"]: row for row in plan["trials"]}
    if not set(COHORTS) <= set(trials):
        raise ValueError("geometric campaign stages absent from frozen plan")
    plan_sha256 = sha256(trial_plan)
    if not isinstance(stage_dirs, dict) or set(stage_dirs) != set(COHORTS):
        raise ValueError("geometric campaign requires exactly three census stages")
    curves, cohorts = [], {}
    for stage, names in COHORTS.items():
        validate_shape(plan, stage)
        if trial_state(ROOT, plan, trials[stage], plan_sha256) != "output_validated":
            raise ValueError("candidate stage lacks validated supervisor receipt")
        stage_dir = Path(stage_dirs[stage])
        if (stage_dir.is_symlink() or not stage_dir.is_dir()
                or stage_dir.resolve() != run_root(ROOT, plan, trials[stage])):
            raise ValueError("candidate stage directory missing or symlinked")
        _, verified_build = verify_build(stage_dir, plan["source_sha256"])
        stage_record, stage_hash = _record(stage_dir / "candidate-stage.json")
        check, _ = _record(stage_dir / "candidate-stage-check.json")
        build, build_hash = _record(stage_dir / "candidate-build.json")
        if (stage_record.get("schema") != "pext.candidate-stage/v1"
                or stage_record.get("status") != "candidate_complete"
                or stage_record.get("stage") != stage
                or stage_record.get("run_id") != trials[stage]["run_id"]
                or stage_record.get("plan_sha256") != plan_sha256
                or stage_record.get("build_receipt_sha256") != build_hash
                or stage_record.get("binary_sha256") != build.get("binary_sha256")
                or build != verified_build
                or check.get("schema") != "pext.candidate-stage-check/v1"
                or check.get("valid") is not True
                or check.get("stage") != stage
                or check.get("run_id") != stage_record.get("run_id")
                or check.get("binary_sha256") != stage_record.get("binary_sha256")
                or check.get("candidate_stage_sha256") != stage_hash
                or not isinstance(stage_record.get("cohorts"), list)
                or not isinstance(check.get("cohorts"), list)
                or len(stage_record["cohorts"]) != len(names)
                or len(check["cohorts"]) != len(names)):
            raise ValueError("candidate stage and checker identity mismatch")
        for index, cohort in enumerate(names):
            binder = CandidateBinder(cohort, plan_path=join_path(cohort))
            if (binder.plan["field"]["prime"], binder.plan["field"]["degree"]) != EXPECTED[cohort]:
                raise ValueError("published cohort field differs from frozen campaign")
            cohort_dir = stage_dir / "cohorts" / cohort
            candidate_check, candidate_hash = _record(cohort_dir / "candidate-check.json")
            produced = stage_record["cohorts"][index]
            checked = check["cohorts"][index]
            if (produced.get("cohort") != cohort or checked != candidate_check
                    or produced.get("index_sha256") != checked.get("index_sha256")
                    or produced.get("unit_count") != checked.get("unit_count")
                    or produced.get("chunk_count") != checked.get("chunk_count")):
                raise ValueError("candidate cohort differs from checked stage")
            curve_rows, metrics = reduce_cohort(cohort_dir, binder,
                                                 stage_record["binary_sha256"])
            if (metrics["classes"] != len(binder.plan["classes"])
                    or metrics["T_blocks"] != sum(
                        len(row["targets"]) for row in binder.plan["classes"])
                    or metrics["independent_check_sha256"] != candidate_hash):
                raise ValueError("geometric reduction differs from published cohort")
            cohorts[cohort] = metrics
            curves.extend(curve_rows)
    return curves, aggregate_cohorts(curves, cohorts)
