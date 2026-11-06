"""Source-bound dispatch of the six prospective experiment components.

This is the internal stage interface for a future run.py/check.py envelope.
It uses the supervisor's approved-plan loader; it cannot approve or launch a
trial by itself. Analyze currently returns component outputs only.
"""

import argparse
import json
from pathlib import Path
import sys

from candidate_stage import (COHORTS, STAGE_ORDER,
                             check_stage as check_candidate,
                             run_stage as run_candidate)
from geometric_analysis_stage import (check_component as check_geometric,
                                      run_component as run_geometric)
from historical_regression_stage import (check_stage as check_regression,
                                         run_stage as run_regression)
from input_manifest import ROOT
from orbit_spectrum_stage import (check_stage as check_orbits,
                                  run_stage as run_orbits)


SELF = "experiments/EXP-PEXT-bf8f96/implementation/stage_router.py"
STAGES = STAGE_ORDER


def validate_shape(plan, trial_id, run_id):
    """Reject a different campaign, stage order, run identity or budget."""
    if not isinstance(plan, dict) or plan.get("experiment_id") != "EXP-PEXT-bf8f96":
        raise ValueError("router experiment identity mismatch")
    trials = plan.get("trials")
    if (not isinstance(trials, list) or len(trials) != len(STAGES)
            or any(not isinstance(row, dict) for row in trials)
            or tuple(row.get("id") for row in trials) != STAGES
            or any(row.get("stage") != row["id"] for row in trials)):
        raise ValueError("router six-stage order mismatch")
    if trial_id not in STAGES:
        raise ValueError("router trial outside frozen six-stage contract")
    trial = trials[STAGES.index(trial_id)]
    if trial.get("run_id") != run_id:
        raise ValueError("router run ID differs from frozen plan")
    expected = (7200, 3600, 21600, 28800, 21600, 3600)
    if (tuple(row.get("watchdog_seconds") for row in trials) != expected
            or sum(expected) != 86400
            or any(type(row.get("memory_mb")) is not int
                   or not 1 <= row["memory_mb"] <= 4096 for row in trials)):
        raise ValueError("router finite watchdog or memory budget mismatch")
    return trial


def dispatch(mode, trial_plan, run_dir, trial_id, run_id):
    """Call one approved component; no fallback stage or additional run."""
    if mode not in ("run", "check"):
        raise ValueError("router mode must be run or check")
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import load_plan, sha256
    plan_path = Path(trial_plan)
    plan = load_plan(ROOT, plan_path)
    validate_shape(plan, trial_id, run_id)
    path = ROOT / SELF
    if (path.is_symlink() or not path.is_file()
            or plan.get("source_sha256", {}).get(SELF) != sha256(path)):
        raise ValueError("router source absent from approved plan")
    run_dir = Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ValueError("router run directory missing or symlinked")
    if trial_id == "regression":
        result = (run_regression if mode == "run" else check_regression)(
            plan_path, run_dir)
    elif trial_id == "orbits":
        result = (run_orbits if mode == "run" else check_orbits)(
            plan_path, run_dir)
    elif trial_id in COHORTS:
        result = (run_candidate if mode == "run" else check_candidate)(
            plan_path, run_dir, trial_id)
    else:
        result = (run_geometric if mode == "run" else check_geometric)(
            plan_path, run_dir)
    return {"schema": "pext.component-route/v1", "mode": mode,
            "trial_id": trial_id, "run_id": run_id,
            "scope": "component_only; final_analysis_and_controls_pending"
                     if trial_id == "analyze" else "bounded_stage_component",
            "result": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("run", "check"), required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    result = dispatch(args.mode, args.trial_plan, args.run_dir,
                      args.trial_id, args.run_id)
    print(json.dumps(result, sort_keys=True))
