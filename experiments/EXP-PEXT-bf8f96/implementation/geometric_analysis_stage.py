"""Prospective write-once geometric analysis component for the analyze trial.

The full analysis/export/checker remains separate. This component retains
complete checked P1-P4 rows and refuses partial or unadmitted census stages.
"""

import hashlib
import argparse
import json
import os
from pathlib import Path
import sys

from candidate_stage import COMPONENT_SOURCES as CANDIDATE_SOURCES, STAGE_ORDER
from geometric_campaign import reduce_campaign
from input_manifest import ROOT


ROWS = "geometric-curves.jsonl"
SUMMARY = "geometric-analysis.json"
COMPONENT_SOURCES = CANDIDATE_SOURCES | {
    "experiments/EXP-PEXT-bf8f96/implementation/geometric_reducer.py",
    "experiments/EXP-PEXT-bf8f96/implementation/geometric_campaign.py",
    "experiments/EXP-PEXT-bf8f96/implementation/geometric_analysis_stage.py",
}


def canonical_line(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def artifact_bytes(curves, campaign, plan_sha256, source_runs):
    if campaign.get("schema") != "pext.geometric-campaign/v1":
        raise ValueError("checked geometric campaign required")
    rows = b"".join(canonical_line(row) for row in curves)
    summary = {"schema": "pext.geometric-analysis-component/v1",
               "status": "checked_geometric_counts; controls_and_descent_pending",
               "experiment": "EXP-PEXT-bf8f96", "plan_sha256": plan_sha256,
               "source_runs": source_runs, "curve_rows_sha256": hashlib.sha256(rows).hexdigest(),
               "campaign": campaign}
    return rows, canonical_line(summary)


def _preflight(trial_plan, run_dir):
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import authorize, load_plan, read_json, run_root, sha256
    trial_plan, run_dir = Path(trial_plan), Path(run_dir)
    plan = load_plan(ROOT, trial_plan)
    if (plan.get("experiment_id") != "EXP-PEXT-bf8f96"
            or tuple(row["id"] for row in plan["trials"]) != STAGE_ORDER):
        raise ValueError("analyze component trial plan differs from six-stage contract")
    trial = plan["trials"][-1]
    if (trial.get("stage") != "analyze"
            or not {ROWS, SUMMARY} <= set(trial.get("artifacts", []))
            or not {"n3core", "n3ext", "n5"} <= set(trial.get("depends_on", []))
            or trial.get("watchdog_seconds") != 3600
            or not COMPONENT_SOURCES <= set(plan["source_sha256"])
            or run_root(ROOT, plan, trial) != run_dir.resolve()):
        raise ValueError("analyze component absent from frozen stage")
    launch = read_json(run_dir / "launch.json")
    if (launch.get("trial_id") != "analyze"
            or launch.get("run_id") != trial["run_id"]
            or launch.get("plan_sha256") != sha256(trial_plan)):
        raise ValueError("analyze component supervisor launch mismatch")
    authority = launch.get("authority")
    if not isinstance(authority, dict) or authorize(
            ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch")) != authority:
        raise ValueError("analyze component lacks current supervisor authority")
    stage_dirs = {row["id"]: run_root(ROOT, plan, row) for row in plan["trials"]
                  if row["id"] in ("n3core", "n3ext", "n5")}
    source_runs = {row["id"]: row["run_id"] for row in plan["trials"]
                   if row["id"] in stage_dirs}
    return plan, stage_dirs, source_runs, launch["plan_sha256"]


def write_component(run_dir, curves, campaign, plan_sha256, source_runs):
    """Persist two exact outputs once; keep an interrupted attempt visible."""
    run_dir = Path(run_dir)
    rows_path, summary_path = run_dir / ROWS, run_dir / SUMMARY
    partial = run_dir / (ROWS + ".partial")
    if any(path.exists() or path.is_symlink() for path in
           (rows_path, summary_path, partial)):
        raise FileExistsError("geometric analysis attempt already exists")
    rows, summary = artifact_bytes(curves, campaign, plan_sha256, source_runs)
    with partial.open("xb") as stream:
        stream.write(rows); stream.flush(); os.fsync(stream.fileno())
    os.replace(partial, rows_path)
    with summary_path.open("xb") as stream:
        stream.write(summary); stream.flush(); os.fsync(stream.fileno())
    return json.loads(summary)


def run_component(trial_plan, run_dir):
    _, stage_dirs, source_runs, plan_sha256 = _preflight(trial_plan, run_dir)
    curves, campaign = reduce_campaign(trial_plan, stage_dirs)
    return write_component(run_dir, curves, campaign, plan_sha256, source_runs)


def compare_artifacts(run_dir, curves, campaign, plan_sha256, source_runs):
    expected_rows, expected_summary = artifact_bytes(
        curves, campaign, plan_sha256, source_runs)
    run_dir = Path(run_dir)
    for name, expected in ((ROWS, expected_rows), (SUMMARY, expected_summary)):
        path = run_dir / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
            raise ValueError(f"geometric analysis output differs from checked campaign: {name}")
    return {"schema": "pext.geometric-analysis-check/v1", "valid": True,
            "curve_rows_sha256": hashlib.sha256(expected_rows).hexdigest(),
            "summary_sha256": hashlib.sha256(expected_summary).hexdigest()}


def check_component(trial_plan, run_dir):
    """Recompute the checked campaign and compare every retained output byte."""
    _, stage_dirs, source_runs, plan_sha256 = _preflight(trial_plan, run_dir)
    curves, campaign = reduce_campaign(trial_plan, stage_dirs)
    return compare_artifacts(run_dir, curves, campaign, plan_sha256, source_runs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("run", "check"), required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    result = (run_component if args.mode == "run" else check_component)(
        args.trial_plan, args.run_dir)
    print(json.dumps(result, sort_keys=True))
