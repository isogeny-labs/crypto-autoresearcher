"""Supervised full-cohort candidate-unit loop with fixed chunk completion.

This is one stage component, not a standalone experiment launcher. Production
construction must pass through admitted_runner, which checks the frozen plan,
live supervisor claim, input/source hashes and binary identity. No directory
or completed unit is resumed or overwritten after an interrupted attempt.
"""

from pathlib import Path
import time

from candidate_batch import (MAX_UNITS, expected_units, seal_chunk,
                             seal_complete_index, verify_complete_index)
from candidate_unit_artifact import (CandidateUnitArtifacts, admitted_runner,
                                     checked_limits)


def run_batch(runner, run_dir, cohort, plan_sha256, caps, memory_bytes,
              cpu_seconds, unit_wall_seconds, stage_wall_seconds, *, use_worker=False):
    """Execute every fixed unit, then seal the complete exact-coverage index."""
    if not isinstance(runner, CandidateUnitArtifacts):
        raise ValueError("candidate artifact runner required")
    if runner.scope not in ("approved-cohort", "software-fixture"):
        raise ValueError("invalid runner scope")
    if runner.scope == "approved-cohort" and runner.binder.plan_path is None:
        raise ValueError("production runner lacks checked join plan")
    run_dir = Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir() or runner.parent != run_dir:
        raise ValueError("runner and run directory differ")
    if (type(stage_wall_seconds) is not int or not 0 < stage_wall_seconds <= 86400
            or type(unit_wall_seconds) is not int or unit_wall_seconds > stage_wall_seconds):
        raise ValueError("stage/unit wall ceilings invalid")
    checked_limits(caps, memory_bytes, cpu_seconds, unit_wall_seconds)
    binder = runner.binder
    if binder is None or binder.cohort != cohort:
        raise ValueError("runner cohort binding missing")
    if binder.plan_sha256 != plan_sha256:
        raise ValueError("run join plan hash mismatch")
    plan = binder.plan
    units = expected_units(plan)
    chunks_dir = run_dir / "chunks"
    chunks_dir.mkdir()  # an interrupted attempt is never reused
    started = time.monotonic()
    pending = []
    worker_mode = runner.scope == "approved-cohort" or use_worker
    if worker_mode:
        runner.start_worker(caps, memory_bytes, stage_wall_seconds,
                            stage_wall_seconds)
    try:
        for ordinal, row in enumerate(units):
            remaining = stage_wall_seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("stage wall ceiling reached before next unit")
            wall = min(unit_wall_seconds, max(1, int(remaining)))
            binding = binder.bind(row["class_index"], row["T_index"])
            if (binding["cohort"] != cohort or binding["join_plan_sha256"] != plan_sha256
                    or binding["class_index"] != row["class_index"]
                    or binding["T_index"] != row["T_index"]):
                raise ValueError("bound unit differs from fixed layout")
            if worker_mode:
                receipt = runner.run_worker(row["name"], binding["quotient_form"],
                    binding["field"], binding["structures_per_T"], caps,
                    memory_bytes, cpu_seconds, wall, binding)
            else:
                receipt = runner.run(row["name"], binding["quotient_form"],
                    binding["field"], binding["structures_per_T"], caps,
                    memory_bytes, cpu_seconds, wall, binding=None)
            if receipt["status"] != "candidate_emitted":
                raise ValueError(f"candidate unit failed: {row['name']}: {receipt['status']}")
            pending.append(run_dir / row["name"])
            if len(pending) == MAX_UNITS or ordinal == len(units)-1:
                seal_chunk(pending, chunks_dir / row["chunk"])
                pending = []
        if worker_mode:
            remaining = stage_wall_seconds - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("stage wall ceiling reached before worker exit")
            runner.finish_worker(remaining)
    except BaseException as error:
        if worker_mode:
            runner.abort_worker(str(error))
        raise
    finally:
        runner.stop_worker()
    index = seal_complete_index(run_dir, cohort, plan, plan_sha256,
                                runner.binary_sha256)
    verified = verify_complete_index(run_dir, cohort, plan, plan_sha256,
                                     runner.binary_sha256)
    if verified["unit_count"] != index["unit_count"]:
        raise ValueError("index readback differs from sealed complete cohort")
    return verified


def run_production(trial_plan, run_dir, cohort, join_plan, binary,
                   binary_sha256, caps, memory_bytes, cpu_seconds,
                   unit_wall_seconds, stage_wall_seconds, *, unit_dir=None):
    """Enter only through the live supervisor's approved trial run directory."""
    runner = admitted_runner(trial_plan, run_dir, cohort, join_plan,
                             binary, binary_sha256, unit_dir=unit_dir)
    return run_batch(runner, runner.parent, cohort, runner.binder.plan_sha256,
                     caps, memory_bytes, cpu_seconds, unit_wall_seconds,
                     stage_wall_seconds)
