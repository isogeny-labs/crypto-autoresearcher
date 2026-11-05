"""Prospective, supervised replay of every pinned historical C0 fixture row.

The stage executes only under an approved six-trial supervisor launch. A
source-only comparison helper is exposed for tests; importing this module
never compiles or runs a cohort.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys

from input_manifest import ROOT
from legacy_n3_alignment import INPUTS, compare_certificate
from legacy_class_bijection import verify_file


EXP = "EXP-PEXT-bf8f96"
OLD = ROOT / "experiments/EXP-PEXT-212d5c/implementation"
SOURCE = "experiments/EXP-PEXT-212d5c/implementation/cover_census_n7.rs"
SELF = "experiments/EXP-PEXT-bf8f96/implementation/historical_regression_stage.py"
ARMS = (
    ("R-n3-q3", 3, 3, "pilot-n3-q3-cosets.jsonl",
     "5003d258d9146d6650ac70d77ea373b4e4979713abbbebd82e1007c6394573ff"),
    ("R-n3-q5", 5, 3, "R1-n3-q5.jsonl",
     "8f1cad66e3625505b200822178a01baf98cc91c499080fef77f2f844b609babb"),
    ("R-n3-q7", 7, 3, "R1-n3-q7.jsonl",
     "9710fcd3eb89a8ec1464541c29424ac02c7de5b15cc08b614a05f1d2886e1d08"),
    ("R-n5-q3", 3, 5, "D-n5-q3-cosets.jsonl",
     "8f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa"),
)
SUMMARY = "historical-regression.json"
CHECK = "historical-regression-check.json"
BUILD = "historical-build.json"
BINARY = "historical-cover-census"
WATCHDOG = 7200
MAX_MEMORY_MB = 4096
DEPENDENT_SOURCES = {
    SOURCE, SELF,
    "experiments/EXP-PEXT-bf8f96/implementation/legacy_n3_alignment.py",
    "experiments/EXP-PEXT-bf8f96/implementation/legacy_class_bijection.py",
    "experiments/EXP-PEXT-bf8f96/implementation/check_compact_class_inputs.py",
    "experiments/EXP-PEXT-bf8f96/implementation/check_curve_class_certificate.py",
    "experiments/EXP-PEXT-bf8f96/implementation/check_quotient_certificate.py",
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fixture_path(arm):
    return OLD / "fixtures" / arm[3]


def expected_artifacts():
    names = [BINARY, "historical-build.stdout.log", "historical-build.stderr.log",
             BUILD, SUMMARY, CHECK]
    for name, _, _, _, _ in ARMS:
        names.extend((name + ".jsonl", name + ".stderr.log"))
    return names


def compare_rows(output, fixture):
    """All rows in order; only field.setup_s and totals.wall_s may vary."""
    output_rows = Path(output).read_bytes().splitlines()
    fixture_rows = Path(fixture).read_bytes().splitlines()
    if len(output_rows) != len(fixture_rows):
        return {"identical": False, "rows_output": len(output_rows),
                "rows_fixture": len(fixture_rows), "first_difference_line": min(
                    len(output_rows), len(fixture_rows))}
    for index, (got, wanted) in enumerate(zip(output_rows, fixture_rows)):
        try:
            output_record, fixture_record = json.loads(got), json.loads(wanted)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"identical": False, "rows_output": len(output_rows),
                    "rows_fixture": len(fixture_rows), "first_difference_line": index}
        if not isinstance(output_record, dict) or not isinstance(fixture_record, dict):
            raise ValueError("historical fixture row is not an object")
        rec = fixture_record.get("rec")
        if rec == "field":
            timing = output_record.get("setup_s")
            if type(timing) not in (int, float) or not math.isfinite(timing) or timing < 0:
                return {"identical": False, "rows_output": len(output_rows),
                        "rows_fixture": len(fixture_rows), "first_difference_line": index}
            output_record.pop("setup_s", None)
            fixture_record.pop("setup_s", None)
            equal = output_record == fixture_record
        elif rec == "totals":
            timing = output_record.get("wall_s")
            if type(timing) not in (int, float) or not math.isfinite(timing) or timing < 0:
                return {"identical": False, "rows_output": len(output_rows),
                        "rows_fixture": len(fixture_rows), "first_difference_line": index}
            output_record.pop("wall_s", None)
            fixture_record.pop("wall_s", None)
            equal = output_record == fixture_record
        else:
            equal = got == wanted
        if not equal:
            return {"identical": False, "rows_output": len(output_rows),
                    "rows_fixture": len(fixture_rows), "first_difference_line": index}
    return {"identical": True, "rows_output": len(output_rows),
            "rows_fixture": len(fixture_rows), "first_difference_line": None}


def _write_once(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _preflight(trial_plan, run_dir):
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import authorize, load_plan, read_json, run_root, sha256 as file_sha
    trial_plan, run_dir = Path(trial_plan), Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise ValueError("historical regression run directory missing or symlinked")
    plan = load_plan(ROOT, trial_plan)
    trials = plan.get("trials", [])
    if (plan.get("experiment_id") != EXP
            or tuple(row.get("id") for row in trials) !=
               ("regression", "orbits", "n3core", "n3ext", "n5", "analyze")):
        raise ValueError("historical regression differs from frozen six-stage contract")
    trial = trials[0]
    if (trial.get("stage") != "regression"
            or trial.get("watchdog_seconds") != WATCHDOG
            or type(trial.get("memory_mb")) is not int
            or not 1 <= trial["memory_mb"] <= MAX_MEMORY_MB
            or not set(expected_artifacts()) <= set(trial.get("artifacts", []))
            or not DEPENDENT_SOURCES <= set(plan.get("source_sha256", {}))
            or run_root(ROOT, plan, trial) != run_dir.resolve()):
        raise ValueError("historical regression absent from frozen stage")
    input_paths = [fixture_path(arm) for arm in ARMS]
    input_paths += [INPUTS / "legacy-n3-alignment.json",
                    INPUTS / "legacy-q3-n5-bijection.json",
                    INPUTS / "q3-n5.json", INPUTS / "q3-n5-field.json",
                    INPUTS / "q5-n3.json", INPUTS / "q7-n3.json"]
    for path in input_paths:
        relative = path.relative_to(ROOT).as_posix()
        if (path.is_symlink() or not path.is_file()
                or plan.get("input_sha256", {}).get(relative) != file_sha(path)):
            raise ValueError(f"historical regression input hash mismatch: {relative}")
    for relative in DEPENDENT_SOURCES:
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or plan["source_sha256"][relative] != file_sha(path):
            raise ValueError(f"historical regression source hash mismatch: {relative}")
    compare_certificate(INPUTS / "legacy-n3-alignment.json")
    mapping = json.loads((INPUTS / "legacy-q3-n5-bijection.json").read_bytes())
    check = verify_file(mapping, INPUTS / "q3-n5.json", INPUTS / "q3-n5-field.json",
                        fixture_path(ARMS[-1]))
    if check.get("valid") is not True or check.get("matched_classes") != 488:
        raise ValueError("historical q3/n5 identity alignment invalid")
    launch = read_json(run_dir / "launch.json")
    if (launch.get("trial_id") != "regression"
            or launch.get("run_id") != trial["run_id"]
            or launch.get("plan_sha256") != file_sha(trial_plan)):
        raise ValueError("historical regression supervisor launch mismatch")
    authority = launch.get("authority")
    if not isinstance(authority, dict) or authorize(
            ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch")) != authority:
        raise ValueError("historical regression lacks current supervisor authority")
    return plan, trial, launch


def _remaining(launch):
    started = datetime.fromisoformat(launch["started_at"].replace("Z", "+00:00"))
    if started.tzinfo is None:
        raise ValueError("supervisor launch has no timezone")
    remaining = WATCHDOG - (datetime.now(timezone.utc) - started).total_seconds()
    if remaining < 1:
        raise TimeoutError("historical regression watchdog reached")
    return max(1, int(remaining))


def _limit_memory(memory_mb):
    limit = memory_mb * 1024 * 1024
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    if current_soft != resource.RLIM_INFINITY:
        limit = min(limit, current_soft)
    resource.setrlimit(resource.RLIMIT_AS, (limit, current_hard))


def _run(command, stdout_path, stderr_path, launch, memory_mb):
    with Path(stdout_path).open("xb") as stdout, Path(stderr_path).open("xb") as stderr:
        try:
            result = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr,
                                    timeout=_remaining(launch), check=False,
                                    preexec_fn=lambda: _limit_memory(memory_mb))
        finally:
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
    if result.returncode != 0:
        raise ValueError(f"historical command exited {result.returncode}; logs retained")


def _build(run_dir, plan, trial, launch):
    compiler = shutil.which("rustc")
    if compiler is None:
        raise ValueError("rustc unavailable")
    binary = run_dir / BINARY
    partial = run_dir / (BINARY + ".partial")
    build = run_dir / BUILD
    if any(path.exists() or path.is_symlink() for path in (binary, partial, build)):
        raise FileExistsError("historical build attempt already exists")
    command = [compiler, "--edition=2021", "-O", str(ROOT / SOURCE), "-o", str(partial)]
    _run(command, run_dir / "historical-build.stdout.log",
         run_dir / "historical-build.stderr.log", launch, trial["memory_mb"])
    if partial.is_symlink() or not partial.is_file():
        raise ValueError("historical compiler produced no binary")
    os.replace(partial, binary)
    record = {"schema": "pext.historical-build/v1", "source_sha256": plan["source_sha256"][SOURCE],
              "invoked_compiler": compiler,
              "compiler": str(Path(compiler).resolve()),
              "compiler_sha256": sha256(Path(compiler).resolve()),
              "compiler_version": subprocess.check_output([compiler, "--version"], text=True).strip(),
              "command": command, "binary_sha256": sha256(binary),
              "stdout_sha256": sha256(run_dir / "historical-build.stdout.log"),
              "stderr_sha256": sha256(run_dir / "historical-build.stderr.log")}
    _write_once(build, record)
    return binary, record


def _verify_build(run_dir, plan):
    path = run_dir / BUILD
    if path.is_symlink() or not path.is_file():
        raise ValueError("historical build receipt missing")
    record = json.loads(path.read_bytes())
    compiler = record.get("compiler")
    invoked = record.get("invoked_compiler")
    expected_command = [invoked, "--edition=2021", "-O", str(ROOT / SOURCE),
                        "-o", str(run_dir / (BINARY + ".partial"))]
    if (record.get("schema") != "pext.historical-build/v1"
            or record.get("source_sha256") != plan["source_sha256"][SOURCE]
            or not isinstance(invoked, str) or not Path(invoked).is_file()
            or not isinstance(compiler, str) or not Path(compiler).is_file()
            or str(Path(invoked).resolve()) != compiler
            or record.get("compiler_sha256") != sha256(compiler)
            or record.get("compiler_version") != subprocess.check_output(
                [invoked, "--version"], text=True).strip()
            or record.get("command") != expected_command
            or record.get("binary_sha256") != sha256(run_dir / BINARY)
            or record.get("stdout_sha256") != sha256(run_dir / "historical-build.stdout.log")
            or record.get("stderr_sha256") != sha256(run_dir / "historical-build.stderr.log")):
        raise ValueError("historical build receipt differs from binary or source")
    return record


def _arm_result(run_dir, arm):
    name, q, n, _, fixture_hash = arm
    fixture = fixture_path(arm)
    if sha256(fixture) != fixture_hash:
        raise ValueError("pinned historical fixture hash mismatch")
    output = run_dir / (name + ".jsonl")
    stderr = run_dir / (name + ".stderr.log")
    if output.is_symlink() or not output.is_file() or stderr.is_symlink() or not stderr.is_file():
        raise ValueError("historical arm output missing or symlinked")
    comparison = compare_rows(output, fixture)
    return {"name": name, "q": q, "n": n,
            "fixture_sha256": fixture_hash, "output_sha256": sha256(output),
            "stderr_sha256": sha256(stderr),
            **comparison}


def run_stage(trial_plan, run_dir):
    plan, trial, launch = _preflight(trial_plan, run_dir)
    run_dir = Path(run_dir)
    binary, build = _build(run_dir, plan, trial, launch)
    results = []
    for arm in ARMS:
        name, q, n, _, _ = arm
        command = [str(binary), str(q), str(n), "exhaustive", "cosets", "4"]
        try:
            _run(command, run_dir / (name + ".jsonl"),
                 run_dir / (name + ".stderr.log"), launch, trial["memory_mb"])
            result = _arm_result(run_dir, arm)
            results.append(result)
            if not result["identical"]:
                break
        except (TimeoutError, subprocess.TimeoutExpired, ValueError) as error:
            results.append({"name": name, "identical": False,
                            "failure": f"{type(error).__name__}: {error}"})
            break
    summary = {"schema": "pext.historical-regression/v1",
               "experiment": EXP, "run_id": trial["run_id"],
               "plan_sha256": launch["plan_sha256"],
               "binary_sha256": build["binary_sha256"],
               "status": "all_fixture_rows_match" if len(results) == len(ARMS)
                         and all(row["identical"] for row in results) else "failed_or_incomplete",
               "checks": results}
    _write_once(run_dir / SUMMARY, summary)
    if summary["status"] != "all_fixture_rows_match":
        raise ValueError("historical fixture replay failed or incomplete; evidence retained")
    return summary


def check_stage(trial_plan, run_dir):
    plan, trial, launch = _preflight(trial_plan, run_dir)
    run_dir = Path(run_dir)
    build = _verify_build(run_dir, plan)
    path = run_dir / SUMMARY
    if path.is_symlink() or not path.is_file():
        raise ValueError("historical regression summary missing or symlinked")
    summary = json.loads(path.read_bytes())
    expected = {"schema": "pext.historical-regression/v1", "experiment": EXP,
                "run_id": trial["run_id"], "plan_sha256": launch["plan_sha256"],
                "binary_sha256": build["binary_sha256"],
                "status": "all_fixture_rows_match",
                "checks": [_arm_result(run_dir, arm) for arm in ARMS]}
    if summary != expected or any(not row["identical"] for row in expected["checks"]):
        raise ValueError("historical regression summary differs from complete fixture replay")
    result = {"schema": "pext.historical-regression-check/v1", "valid": True,
              "summary_sha256": sha256(path), "binary_sha256": build["binary_sha256"],
              "fixture_rows": sum(row["rows_fixture"] for row in expected["checks"])}
    _write_once(run_dir / CHECK, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("run", "check"), required=True)
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    value = (run_stage if args.mode == "run" else check_stage)(
        args.trial_plan, args.run_dir)
    print(json.dumps(value, sort_keys=True))
