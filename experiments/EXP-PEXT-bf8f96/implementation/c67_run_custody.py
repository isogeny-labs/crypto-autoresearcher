"""Prospective C6/C7 run custody; never constructs or replays control data.

The future launcher calls ``prepare`` inside an existing approved census trial,
then places wrapped control batches in c67-results. ``readback`` seals byte and
coverage custody only. Arithmetic and deterministic-seed validation remain the
responsibility of the independent control checkers.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
EXP = "EXP-PEXT-bf8f96"
PREFIX = f"experiments/{EXP}/"
SELF = PREFIX + "implementation/c67_run_custody.py"
SCHEDULE = PREFIX + "inputs/c67-control-schedule-prospective.json"
ADMISSION = "c67-custody.json"
READBACK = "c67-custody-readback.json"
STAGES = ("regression", "orbits", "n3core", "n3ext", "n5", "analyze")
WATCHDOGS = (7200, 3600, 21600, 28800, 21600, 3600)
MAX_CONTROL_BYTES = 8 * 1024 * 1024
COHORTS = {"n3core": ("q5-n3", "q7-n3"), "n3ext": ("q11-n3",),
           "n5": ("q3-n5",)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode() + b"\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def _regular(path):
    path = Path(path)
    _need(not path.is_symlink() and path.is_file(),
          f"C6/C7 missing or symlinked file: {path.name}")
    _need(path.stat().st_size <= MAX_CONTROL_BYTES,
          f"C6/C7 retained file exceeds byte cap: {path.name}")
    return path.read_bytes()


def _write_once(path, data):
    # Exclusive creation preserves an interrupted attempt and blocks reruns.
    _need(len(data) <= MAX_CONTROL_BYTES,
          "C6/C7 output exceeds byte cap")
    with Path(path).open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def expected_records(schedule, stage):
    """Enumerate published batch identities, without drawing a control."""
    _need(stage in COHORTS, "C6/C7 requires an existing census stage")
    _need(schedule.get("schema") == "pext.c67-prospective-control-schedule/v1"
          and schedule.get("experiment") == EXP and schedule.get("seed") == 20261102,
          "C6/C7 published schedule identity mismatch")
    rows = schedule.get("cohorts")
    all_cohorts = tuple(c for cohorts in COHORTS.values() for c in cohorts)
    _need(isinstance(rows, list)
          and tuple(row.get("cohort") for row in rows) == all_cohorts,
          "C6/C7 schedule cohort order or coverage mismatch")
    expected = []
    units = 0
    for row in rows:
        strata = row.get("strata")
        _need(isinstance(strata, list) and bool(strata), "C6/C7 empty strata")
        patterns = []
        for index, stratum in enumerate(strata):
            pattern = stratum["pattern"]
            _need(isinstance(pattern, list) and all(type(n) is int and n > 0 for n in pattern)
                  and sum(pattern) == 4 and pattern not in patterns,
                  "C6/C7 duplicate or invalid pattern")
            patterns.append(pattern)
            c6, c7 = stratum["C6"], stratum["C7"]
            _need(c6["seed"] == 20261102 and c6["slots"] == 16
                  and c6["structure_ordinal"] == 0
                  and [c["scalar_class"] for c in c7] == [0, 1]
                  and all(c["seed"] == 20261102 and c["samples"] == 16
                          and c["draw_cap"] == 4096
                          and c["coefficient_block_cap"] == 4096 for c in c7),
                  "C6/C7 frozen seed, count or draw caps changed")
            units += 1
            if row["cohort"] not in COHORTS[stage]:
                continue
            shared = {"cohort": row["cohort"], "pattern": pattern,
                      "join_plan_sha256": row["join_plan_sha256"],
                      "field_sha256": row["field_sha256"], "seed": 20261102}
            expected.append({**shared, "control": "C6", "selection": c6,
                             "path": f"c67-results/{row['cohort']}-s{index}-c6.json"})
            for control in c7:
                expected.append({**shared, "control": "C7", "selection": control,
                                 "path": f"c67-results/{row['cohort']}-s{index}-c7-{control['scalar_class']}.json"})
    _need((schedule.get("C6_selected_units"), schedule.get("C6_coordinate_slots"),
           schedule.get("C7_strata"), schedule.get("C7_requested_forms"))
          == (units, 16 * units, 2 * units, 32 * units),
          "C6/C7 schedule totals mismatch")
    return expected


def expected_artifacts(schedule, stage):
    return [ADMISSION, READBACK] + [row["path"] for row in expected_records(schedule, stage)]


def _preflight(trial_plan, run_dir, stage):
    """Use the ordinary approved-plan and current supervisor-claim gates."""
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import authorize, load_plan, read_json, run_root, sha256
    trial_plan, run_dir = Path(trial_plan), Path(run_dir)
    plan = load_plan(ROOT, trial_plan)
    trials = plan.get("trials", [])
    _need(plan.get("experiment_id") == EXP and stage in COHORTS
          and tuple(t.get("id") for t in trials) == STAGES
          and tuple(t.get("stage") for t in trials) == STAGES
          and tuple(t.get("watchdog_seconds") for t in trials) == WATCHDOGS
          and all(type(t.get("memory_mb")) is int and 1 <= t["memory_mb"] <= 4096
                  for t in trials), "C6/C7 frozen six-run budget mismatch")
    trial = trials[STAGES.index(stage)]
    _need(not run_dir.is_symlink() and run_dir.is_dir(), "C6/C7 run directory invalid")
    launch = read_json(run_dir / "launch.json")
    _need(launch.get("trial_id") == stage and launch.get("run_id") == trial["run_id"]
          and launch.get("plan_sha256") == sha256(trial_plan)
          and run_root(ROOT, plan, trial) == run_dir.resolve(),
          "C6/C7 supervisor launch identity mismatch")
    authority = launch.get("authority")
    _need(isinstance(authority, dict) and authorize(
        ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch")) == authority,
        "C6/C7 current supervisor authority missing")
    _need(digest(_regular(ROOT / SELF)) == plan.get("source_sha256", {}).get(SELF),
          "C6/C7 custody source not bound by approved plan")
    data = _regular(ROOT / SCHEDULE)
    _need(digest(data) == plan.get("input_sha256", {}).get(SCHEDULE),
          "C6/C7 schedule not bound by approved plan")
    schedule = json.loads(data)
    records = expected_records(schedule, stage)
    for cohort in COHORTS[stage]:
        row = next(row for row in schedule["cohorts"] if row["cohort"] == cohort)
        relative = PREFIX + f"inputs/join-plans-20261103/{cohort}.json"
        _need(digest(_regular(ROOT / relative)) == row["join_plan_sha256"]
              == plan.get("input_sha256", {}).get(relative),
              "C6/C7 source join plan not bound by approved plan")
    _need(set(expected_artifacts(schedule, stage)) <= set(trial.get("artifacts", [])),
          "C6/C7 artifacts absent from approved trial coverage")
    admission = {"schema": "pext.c67-run-custody/v1", "experiment": EXP,
                 "status": "prospective_custody_only; control_execution_pending",
                 "stage": stage, "run_id": trial["run_id"],
                 "plan_sha256": launch["plan_sha256"],
                 "schedule_sha256": digest(data), "records": records}
    return run_dir, admission


def prepare(trial_plan, run_dir, stage):
    """Reserve one prospective attempt before any control output exists."""
    run_dir, admission = _preflight(trial_plan, run_dir, stage)
    _need(not (run_dir / "c67-results").exists()
          and not (run_dir / "c67-results").is_symlink(),
          "C6/C7 results existed before prospective custody")
    _need(not (run_dir / READBACK).exists() and not (run_dir / READBACK).is_symlink(),
          "C6/C7 prior readback exists")
    _write_once(run_dir / ADMISSION, canonical(admission))
    # A crash after the admission remains an attempted run; never recreate it.
    (run_dir / "c67-results").mkdir()
    return admission


def _payload_coverage(payload, record):
    """Check batch identities/counts only; no seed or arithmetic replay."""
    selection = record["selection"]
    if record["control"] == "C6":
        _need(payload.get("schema") == "pext.c6-coordinate-control-batch/v1"
              and payload.get("cohort") == record["cohort"]
              and payload.get("join_plan_sha256") == record["join_plan_sha256"]
              and all(payload.get(key) == selection[key] for key in (
                  "class_index", "T_index", "structure_ordinal", "seed"))
              and payload.get("draw_cap") == 4096 and payload.get("slot_count") == 16,
              "C6 batch identity or frozen count mismatch")
        rows = payload.get("rows")
        _need(isinstance(rows, list) and [row.get("slot") for row in rows] == list(range(16))
              and all(all(row.get(key) == payload[key] for key in (
                  "cohort", "class_index", "T_index", "structure_ordinal", "join_plan_sha256", "seed"))
                      and row.get("binding_sha256") == selection["binding_sha256"]
                      for row in rows), "C6 exact slot coverage mismatch")
        _need(all(row.get("schema") == "pext.c6-coordinate-control/v1"
                  and isinstance(row.get("transport_matrix"), list)
                  and len(row["transport_matrix"]) == 4
                  and all(type(value) is int for value in row["transport_matrix"])
                  and isinstance(row.get("base_invariants"), dict)
                  and isinstance(row.get("common_transport_invariants"), dict)
                  for row in rows), "C6 retained result payload missing")
        return {"requested": 16, "retained": 16, "coverage": "all_slots_retained"}
    _need(payload.get("schema") == "pext.c7-matched-random/v1"
          and payload.get("field_sha256") == record["field_sha256"]
          and payload.get("pattern") == record["pattern"]
          and payload.get("scalar_class") == selection["scalar_class"]
          and payload.get("seed") == selection["seed"]
          and payload.get("requested") == 16 and payload.get("draw_cap") == 4096,
          "C7 batch identity or frozen count mismatch")
    selected, attempted = payload.get("selected"), payload.get("attempted")
    _need(isinstance(selected, list) and len(selected) <= 16
          and type(attempted) is int and len(selected) <= attempted <= 4096,
          "C7 retained or attempted count mismatch")
    draws = [row.get("draw") for row in selected]
    _need(all(type(draw) is int and 0 <= draw < attempted for draw in draws)
          and draws == sorted(set(draws)), "C7 draw coverage duplicated or unordered")
    _need(all(isinstance(row.get("form"), list) and len(row["form"]) == 5
              and all(type(value) is int for value in row["form"])
              and isinstance(row.get("check"), dict)
              and row["check"].get("pattern") == record["pattern"]
              and row["check"].get("scalar_class") == selection["scalar_class"]
              for row in selected)
          and len({tuple(row["form"]) for row in selected}) == len(selected),
          "C7 retained form payload missing or duplicated")
    complete = len(selected) == 16
    _need(payload.get("status") == ("control_complete" if complete else "inconclusive_draw_cap_exhausted")
          and (complete or attempted == 4096), "C7 incomplete attempt not retained at draw cap")
    return {"requested": 16, "retained": len(selected),
            "coverage": "all_forms_retained" if complete else "inconclusive_draw_cap_exhausted"}


def compare_results(run_dir, admission):
    """Read the exact expected set and report coverage including failed strata."""
    run_dir = Path(run_dir)
    admission_data = canonical(admission)
    _need(_regular(run_dir / ADMISSION) == admission_data,
          "C6/C7 custody differs from approved prospective admission")
    directory = run_dir / "c67-results"
    _need(not directory.is_symlink() and directory.is_dir(), "C6/C7 result directory invalid")
    records = admission["records"]
    _need({path.name for path in directory.iterdir()} == {Path(row["path"]).name for row in records},
          "C6/C7 result file coverage differs from prospective schedule")
    checked = []
    for record in records:
        data = _regular(run_dir / record["path"])
        wrapped = json.loads(data)
        _need(wrapped.get("schema") == "pext.c67-run-result/v1"
              and all(wrapped.get(key) == admission[key] for key in (
                  "experiment", "stage", "run_id", "plan_sha256", "schedule_sha256"))
              and wrapped.get("admission_sha256") == digest(admission_data)
              and wrapped.get("record") == record, "C6/C7 result custody binding mismatch")
        coverage = _payload_coverage(wrapped.get("payload", {}), record)
        checked.append({"path": record["path"], "sha256": digest(data),
                        "bytes": len(data), **coverage})
    return {"schema": "pext.c67-custody-readback/v1", "experiment": EXP,
            "status": "custody_readback_only; arithmetic_and_seed_validation_pending",
            **{key: admission[key] for key in ("stage", "run_id", "plan_sha256", "schedule_sha256")},
            "admission_sha256": digest(admission_data), "records": checked,
            "coverage_complete": all(row["requested"] == row["retained"] for row in checked)}


def write_result(trial_plan, run_dir, stage, relative_path, payload):
    """Exclusively wrap one declared result after prospective admission.

    The supplied payload is retained, never generated or arithmetically checked.
    The future producer remains responsible for all control computation.
    """
    run_dir, admission = _preflight(trial_plan, run_dir, stage)
    admission_data = canonical(admission)
    _need(_regular(run_dir / ADMISSION) == admission_data,
          "C6/C7 custody differs from approved prospective admission")
    record = next((row for row in admission["records"] if row["path"] == relative_path), None)
    _need(record is not None, "C6/C7 result path outside prospective schedule")
    directory = run_dir / "c67-results"
    _need(not directory.is_symlink() and directory.is_dir(), "C6/C7 result directory invalid")
    _need({path.name for path in directory.iterdir()} <= {
        Path(row["path"]).name for row in admission["records"]},
        "C6/C7 undeclared result already present")
    _need(not (run_dir / READBACK).exists() and not (run_dir / READBACK).is_symlink(),
          "C6/C7 result write after sealed readback")
    _payload_coverage(payload, record)
    envelope = {"schema": "pext.c67-run-result/v1",
                **{key: admission[key] for key in (
                    "experiment", "stage", "run_id", "plan_sha256", "schedule_sha256")},
                "admission_sha256": digest(admission_data), "record": record,
                "payload": payload}
    data = canonical(envelope)
    _write_once(run_dir / relative_path, data)
    return {"path": relative_path, "sha256": digest(data), "bytes": len(data)}


def readback(trial_plan, run_dir, stage):
    """Write once, or compare an existing readback; never overwrite evidence."""
    run_dir, admission = _preflight(trial_plan, run_dir, stage)
    result = compare_results(run_dir, admission)
    data, path = canonical(result), run_dir / READBACK
    if path.exists() or path.is_symlink():
        _need(_regular(path) == data, "C6/C7 retained result bytes differ from sealed readback")
    else:
        _write_once(path, data)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "readback"))
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=tuple(COHORTS), required=True)
    args = parser.parse_args()
    print(json.dumps((prepare if args.action == "prepare" else readback)(
        args.trial_plan, args.run_dir, args.stage), sort_keys=True))
