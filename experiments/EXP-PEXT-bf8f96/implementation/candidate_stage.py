"""Approved supervisor component for the three geometric-census stages.

This binds the fixed six-stage contract, builds one binary per census stage,
and places each cohort in its prescribed supervisor run. It emits candidate
artifacts only; the full experiment launcher must add the descent, controls,
analysis, run envelope and final checker before approval.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

from candidate_batch import expected_units
from candidate_binding import CandidateBinder
from candidate_build import build, verify_build
from candidate_census_check import check_batch
from candidate_census_driver import run_production
from candidate_unit_artifact import REQUIRED_SOURCES, checked_limits
from input_manifest import INPUTS, ROOT


STAGE_ORDER = ("regression", "orbits", "n3core", "n3ext", "n5", "analyze")
WATCHDOGS = {"regression": 7200, "orbits": 3600, "n3core": 21600,
             "n3ext": 28800, "n5": 21600, "analyze": 3600}
COHORTS = {"n3core": ("q5-n3", "q7-n3"), "n3ext": ("q11-n3",),
           "n5": ("q3-n5",)}
BASE = "experiments/EXP-PEXT-bf8f96/inputs/join-plans-20261103"
COMPONENT_SOURCES = REQUIRED_SOURCES | {
    "experiments/EXP-PEXT-bf8f96/implementation/candidate_stage.py"
}


def join_path(cohort):
    if cohort not in {c for values in COHORTS.values() for c in values}:
        raise ValueError("cohort absent from geometric stages")
    return ROOT / BASE / f"{cohort}.json"


def expected_artifacts(stage):
    """Exact declared relative paths for every candidate stage output."""
    if stage not in COHORTS:
        raise ValueError("not a geometric census stage")
    names = ["candidate-unit", "candidate-build.json", "build.stdout.log",
             "build.stderr.log", "candidate-stage.json", "candidate-stage-check.json"]
    for cohort in COHORTS[stage]:
        path = join_path(cohort)
        if path.is_symlink() or not path.is_file():
            raise ValueError("published join plan missing or symlinked")
        plan = json.loads(path.read_bytes())
        if plan.get("cohort") != cohort or plan.get("schema") != "pext.join-plan/v1":
            raise ValueError("published join plan identity mismatch")
        prefix = f"cohorts/{cohort}/"
        chunks = list(dict.fromkeys(row["chunk"] for row in expected_units(plan)))
        for name in chunks:
            names.extend((prefix + "chunks/" + name,
                          prefix + "chunks/" + name.replace(".tar", ".receipt.json")))
        names.extend((prefix + "units-index.json", prefix + "candidate-reviews.jsonl",
                      prefix + "candidate-check.json"))
    if len(names) != len(set(names)):
        raise ValueError("candidate artifact names collide")
    return names


def validate_shape(plan, stage):
    """Check frozen stage shape, resource caps and exact archive coverage."""
    if stage not in COHORTS:
        raise ValueError("not a geometric census stage")
    if plan["experiment_id"] != "EXP-PEXT-bf8f96":
        raise ValueError("wrong experiment in frozen plan")
    trials = plan["trials"]
    if (tuple(row["id"] for row in trials) != STAGE_ORDER
            or any(row.get("stage") != row["id"]
                   or row.get("watchdog_seconds") != WATCHDOGS[row["id"]]
                   for row in trials)
            or sum(WATCHDOGS.values()) != 86400):
        raise ValueError("frozen plan differs from six-stage budget")
    trial = next(row for row in trials if row["id"] == stage)
    driver_seconds = trial.get("candidate_driver_wall_seconds")
    checker_reserve = trial.get("candidate_checker_reserve_seconds")
    if (type(driver_seconds) is not int or type(checker_reserve) is not int
            or driver_seconds < 1 or checker_reserve < 1
            or driver_seconds + checker_reserve > WATCHDOGS[stage]):
        raise ValueError("candidate stage driver/checker budget missing or exceeds watchdog")
    if not COMPONENT_SOURCES <= set(plan["source_sha256"]):
        raise ValueError("candidate stage source closure absent from plan")
    if not set(expected_artifacts(stage)) <= set(trial["artifacts"]):
        raise ValueError("candidate stage artifacts absent from frozen plan")
    config = trial.get("candidate_config")
    if not isinstance(config, dict) or set(config) != set(COHORTS[stage]):
        raise ValueError("candidate stage cohort config missing")
    for cohort in COHORTS[stage]:
        row = config[cohort]
        if not isinstance(row, dict) or set(row) != {"caps", "memory_bytes", "cpu_seconds", "unit_wall_seconds"}:
            raise ValueError("candidate cohort cap shape")
        caps = row["caps"]
        checked_limits(caps, row["memory_bytes"], row["cpu_seconds"],
                       row["unit_wall_seconds"])
        published = json.loads(join_path(cohort).read_bytes())
        field = published["field"]
        if (caps["field_elements"] != field["prime"] ** field["degree"]
                or caps["structures"] != published["structures_per_T"]
                or row["memory_bytes"] > min(3*1024**3, int(trial["memory_mb"]*1024**2))
                or row["unit_wall_seconds"] > WATCHDOGS[stage]
                or row["cpu_seconds"] > WATCHDOGS[stage]):
            raise ValueError("candidate cohort caps differ from exact layout or stage budget")
    return trial


def _preflight(trial_plan, run_dir, stage):
    """Recheck plan, exact supervisor launch, claim, sources and input hashes."""
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import authorize, load_plan, read_json, run_root, sha256
    trial_plan, run_dir = Path(trial_plan), Path(run_dir)
    plan = load_plan(ROOT, trial_plan)
    trial = validate_shape(plan, stage)
    launch = read_json(run_dir / "launch.json")
    if (launch.get("trial_id") != stage or launch.get("run_id") != trial["run_id"]
            or launch.get("plan_sha256") != sha256(trial_plan)
            or run_root(ROOT, plan, trial) != run_dir.resolve()):
        raise ValueError("candidate stage does not match supervisor launch")
    authority = launch.get("authority")
    if not isinstance(authority, dict) or authorize(
            ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch")) != authority:
        raise ValueError("candidate stage lacks current supervisor authority")
    for cohort in COHORTS[stage]:
        for path in (join_path(cohort), ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json",
                     ROOT / INPUTS / f"{cohort}.json"):
            relative = path.relative_to(ROOT).as_posix()
            if path.is_symlink() or not path.is_file() or sha256(path) != plan.get("input_sha256", {}).get(relative):
                raise ValueError(f"candidate stage input hash mismatch: {relative}")
    return plan, trial, launch


def _launch_start(launch):
    started = datetime.fromisoformat(launch["started_at"].replace("Z", "+00:00"))
    if started.tzinfo is None:
        raise ValueError("supervisor launch clock has no timezone")
    return started


def _remaining(launch, cutoff_seconds):
    remaining = cutoff_seconds - (datetime.now(timezone.utc) - _launch_start(launch)).total_seconds()
    if remaining < 1:
        raise TimeoutError("candidate stage watchdog reached")
    return int(remaining)


def _write_once(path, record):
    with path.open("x") as stream:
        json.dump(record, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())


def run_stage(trial_plan, run_dir, stage):
    """Run candidate construction only in the exact approved supervisor trial."""
    plan, trial, launch = _preflight(trial_plan, run_dir, stage)
    run_dir = Path(run_dir)
    binary, build_receipt = build(run_dir, plan["source_sha256"])
    verify_build(run_dir, plan["source_sha256"])
    cohorts_dir = run_dir / "cohorts"
    cohorts_dir.mkdir()
    results = []
    for cohort in COHORTS[stage]:
        cohort_dir = cohorts_dir / cohort
        cohort_dir.mkdir()
        config = trial["candidate_config"][cohort]
        result = run_production(trial_plan, run_dir, cohort, join_path(cohort),
                                binary, build_receipt["binary_sha256"],
                                config["caps"], config["memory_bytes"],
                                config["cpu_seconds"], config["unit_wall_seconds"],
                                _remaining(launch, trial["candidate_driver_wall_seconds"]),
                                unit_dir=cohort_dir)
        results.append(result)
    record = {"schema": "pext.candidate-stage/v1", "status": "candidate_complete",
              "stage": stage, "run_id": trial["run_id"],
              "plan_sha256": launch["plan_sha256"],
              "binary_sha256": build_receipt["binary_sha256"],
              "build_receipt_sha256": hashlib.sha256((run_dir / "candidate-build.json").read_bytes()).hexdigest(),
              "cohorts": results}
    _write_once(run_dir / "candidate-stage.json", record)
    return record


def check_stage(trial_plan, run_dir, stage):
    """Replay the candidate component during the supervisor checker phase."""
    plan, trial, launch = _preflight(trial_plan, run_dir, stage)
    run_dir = Path(run_dir)
    _, build_receipt = verify_build(run_dir, plan["source_sha256"])
    stage_path = run_dir / "candidate-stage.json"
    if stage_path.is_symlink() or not stage_path.is_file():
        raise ValueError("candidate stage record missing")
    record = json.loads(stage_path.read_bytes())
    if (record.get("schema") != "pext.candidate-stage/v1"
            or record.get("status") != "candidate_complete"
            or record.get("stage") != stage
            or record.get("run_id") != trial["run_id"]
            or record.get("plan_sha256") != launch["plan_sha256"]
            or record.get("binary_sha256") != build_receipt["binary_sha256"]
            or record.get("build_receipt_sha256") != hashlib.sha256(
                (run_dir / "candidate-build.json").read_bytes()).hexdigest()
            or not isinstance(record.get("cohorts"), list)
            or len(record["cohorts"]) != len(COHORTS[stage])):
        raise ValueError("candidate stage record differs from supervisor/build")
    results = []
    cohorts_dir = run_dir / "cohorts"
    if (cohorts_dir.is_symlink() or not cohorts_dir.is_dir()
            or {path.name for path in cohorts_dir.iterdir()} != set(COHORTS[stage])):
        raise ValueError("candidate stage cohort directories differ from frozen stage")
    deadline = _launch_start(launch) + timedelta(seconds=WATCHDOGS[stage])
    _remaining(launch, WATCHDOGS[stage])
    for cohort, produced in zip(COHORTS[stage], record["cohorts"]):
        binder = CandidateBinder(cohort, plan_path=join_path(cohort))
        cohort_dir = run_dir / "cohorts" / cohort
        checked = check_batch(cohort_dir, cohort, binder,
                              build_receipt["binary_sha256"], deadline_utc=deadline,
                              expected_limits=trial["candidate_config"][cohort])
        if (produced.get("cohort") != cohort
                or produced.get("index_sha256") != checked["index_sha256"]
                or produced.get("unit_count") != checked["unit_count"]
                or produced.get("chunk_count") != checked["chunk_count"]):
            raise ValueError("candidate stage cohort differs from independent replay")
        results.append(checked)
    summary = {"schema": "pext.candidate-stage-check/v1", "valid": True,
               "stage": stage, "run_id": trial["run_id"],
               "binary_sha256": build_receipt["binary_sha256"],
               "candidate_stage_sha256": hashlib.sha256(stage_path.read_bytes()).hexdigest(),
               "cohorts": results}
    _write_once(run_dir / "candidate-stage-check.json", summary)
    return summary
