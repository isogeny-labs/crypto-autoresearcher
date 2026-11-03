"""Write-once, capped candidate-unit artifacts for a supervisor-owned run.

Production construction rechecks the live dispatcher claim. The fixture
constructor is for explicitly labelled software checks only. This helper is
not a trial-plan launcher or an experiment approval mechanism.
"""

import gzip
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from candidate_binding import CandidateBinder
from input_manifest import INPUTS, ROOT


CAP_NAMES = ("field_elements", "structures", "image_entries", "rational_candidates",
             "nonrational_maps", "total_candidates")
MAX_MEMORY_BYTES = 4 * 1024**3
MAX_CPU_SECONDS = 24 * 3600
MAX_WALL_SECONDS = 86400
_ADMISSION_TOKEN = object()
IMPLEMENTATION = "experiments/EXP-PEXT-bf8f96/implementation/"
REQUIRED_SOURCES = {
    IMPLEMENTATION + name for name in (
        "candidate_unit.rs", "candidate_unit_artifact.py", "candidate_binding.py",
        "quotient_core.rs", "symbolic_extension.rs", "branch_factorization.rs",
        "branch_roots.rs", "root_collision.rs", "join_plan.py", "input_manifest.py",
        "check_quotient_certificate.py", "check_compact_class_inputs.py")
} | {"experiments/EXP-PEXT-212d5c/implementation/cover_census_n7.rs"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_once(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":"), allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def checked_limits(caps, memory_bytes, cpu_seconds, wall_seconds):
    if (set(caps) != set(CAP_NAMES) or any(type(caps[key]) is not int or caps[key] < 1
                                         for key in CAP_NAMES)):
        raise ValueError("six positive integer candidate caps required")
    if (type(memory_bytes) is not int or not 0 < memory_bytes <= MAX_MEMORY_BYTES
            or type(cpu_seconds) is not int or not 0 < cpu_seconds <= MAX_CPU_SECONDS
            or type(wall_seconds) is not int or not 0 < wall_seconds <= MAX_WALL_SECONDS):
        raise ValueError("positive bounded memory, CPU and wall limits required")
    return [str(caps[key]) for key in CAP_NAMES]


def admitted_runner(trial_plan, run_dir, cohort, join_plan, binary, binary_sha256):
    """Construct a production runner only inside the exact live supervisor run."""
    sys.path.insert(0, str(ROOT / "tools"))
    from experiment_execution import (authorize, load_plan, read_json, run_root,
                                      sha256 as supervisor_sha256)
    trial_plan, run_dir, binary = Path(trial_plan), Path(run_dir), Path(binary)
    plan = load_plan(ROOT, trial_plan)
    launch = read_json(run_dir / "launch.json")
    authority = launch.get("authority")
    if not isinstance(authority, dict):
        raise ValueError("missing supervisor authority")
    trial = next((row for row in plan["trials"] if row["id"] == launch.get("trial_id")), None)
    if (trial is None or run_root(ROOT, plan, trial) != run_dir.resolve()
            or launch.get("run_id") != trial["run_id"]
            or launch.get("plan_sha256") != supervisor_sha256(trial_plan)):
        raise ValueError("supervisor launch does not bind this run")
    fresh = authorize(ROOT, trial_plan, plan, authority.get("owner"), authority.get("epoch"))
    if fresh != authority:
        raise ValueError("supervisor authority changed")
    if not REQUIRED_SOURCES <= set(plan["source_sha256"]):
        raise ValueError("candidate source closure absent from frozen plan")
    input_hashes = plan.get("input_sha256", {})
    expected_inputs = (join_plan, ROOT / "experiments/EXP-PEXT-bf8f96/inputs/manifest.json",
                       ROOT / INPUTS / f"{cohort}.json")
    for path in expected_inputs:
        path = Path(path)
        try:
            relative = path.resolve().relative_to(ROOT).as_posix()
        except ValueError as error:
            raise ValueError("candidate input outside checkout") from error
        if path.is_symlink() or not path.is_file() or input_hashes.get(relative) != file_sha256(path):
            raise ValueError(f"candidate input absent or hash mismatch: {relative}")
    if (not binary.is_file() or binary.is_symlink() or file_sha256(binary) != binary_sha256):
        raise ValueError("candidate binary digest mismatch")
    return CandidateUnitArtifacts(binary, binary_sha256, CandidateBinder(cohort, plan_path=join_plan),
                                  "approved-cohort", run_dir, _ADMISSION_TOKEN)


class CandidateUnitArtifacts:
    def __init__(self, binary, binary_sha256, binder, scope, parent, admission_token=None):
        self.binary = Path(binary)
        self.binary_sha256 = binary_sha256
        self.binder = binder
        self.scope = scope
        self.parent = Path(parent)
        if self.binary.is_symlink() or not self.binary.is_file() or file_sha256(self.binary) != binary_sha256:
            raise ValueError("candidate binary digest mismatch")
        if scope not in ("software-fixture", "approved-cohort"):
            raise ValueError("invalid candidate artifact scope")
        if scope == "approved-cohort" and admission_token is not _ADMISSION_TOKEN:
            raise ValueError("production runner requires live supervisor admission")

    def run(self, name, form, field, structures, caps, memory_bytes, cpu_seconds,
            wall_seconds, binding=None):
        extra = checked_limits(caps, memory_bytes, cpu_seconds, wall_seconds)
        if (type(name) is not str or not name or "/" in name or name in (".", "..")
                or not self.parent.is_dir()):
            raise ValueError("invalid unit artifact directory")
        if (self.scope == "approved-cohort") != (binding is not None):
            raise ValueError("production binding/scope mismatch")
        if binding is not None and (self.binder is None or binding != self.binder.bind(
                binding["class_index"], binding["T_index"])):
            raise ValueError("candidate binding was not derived from checked cohort")
        if binding is not None and (binding["quotient_form"] != form
                                    or binding["field"] != field
                                    or binding["structures_per_T"] != structures):
            raise ValueError("candidate binding mismatch")
        if type(form) is not list or len(form) != 5:
            raise ValueError("five quotient coefficients required")
        directory = self.parent / name
        directory.mkdir()  # exclusive: a failed or interrupted unit is never overwritten
        args = [str(self.binary), str(field["prime"]), str(field["degree"]),
                ",".join(map(str, form)), *extra]
        metadata = {"schema": "pext.candidate-unit-input/v1", "scope": self.scope,
                    "binary_sha256": self.binary_sha256, "argv": args,
                    "field": field, "form": form, "structures": structures,
                    "caps": caps, "memory_bytes": memory_bytes,
                    "cpu_seconds": cpu_seconds, "wall_seconds": wall_seconds,
                    "binding": binding}
        write_once(directory / "input.json", metadata)
        partial = directory / "unit.json.partial"
        stderr_path = directory / "stderr.log"
        started = time.monotonic()
        status, returncode = "launch_error", None
        try:
            def limits():
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            with partial.open("xb") as stdout, stderr_path.open("xb") as stderr:
                process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=stdout,
                                           stderr=stderr, start_new_session=True,
                                           preexec_fn=limits)
                try:
                    returncode = process.wait(timeout=wall_seconds)
                    status = "exited" if returncode == 0 else "child_failed"
                except subprocess.TimeoutExpired:
                    status = "wall_timeout"
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
        except (OSError, subprocess.SubprocessError) as error:
            status = "launch_error"
            with (directory / "launch-error.txt").open("x") as stream:
                stream.write(str(error) + "\n")
        elapsed = time.monotonic() - started
        partial_sha = file_sha256(partial) if partial.is_file() else None
        stderr_sha = file_sha256(stderr_path) if stderr_path.is_file() else None
        if status == "exited":
            try:
                unit = json.loads(partial.read_bytes())
                if (unit.get("schema") != "pext.checked-candidate-unit/v1"
                        or unit.get("field") != field or unit.get("form") != form
                        or unit.get("structure_order") != "left-pgl2-fq/v1"
                        or unit.get("structures") != structures
                        or unit.get("exceptional", -1) + unit.get("generic", -1) != structures):
                    raise ValueError("candidate output identity or coverage mismatch")
                compressed = gzip.compress(partial.read_bytes(), mtime=0)
                with (directory / "unit.json.gz").open("xb") as stream:
                    stream.write(compressed)
                    stream.flush()
                    os.fsync(stream.fileno())
                partial.unlink()
                receipt = {"schema": "pext.candidate-unit-artifact/v1", "status": "candidate_emitted",
                           "scope": self.scope, "input_sha256": file_sha256(directory / "input.json"),
                           "raw_sha256": partial_sha, "compressed_sha256": sha256(compressed),
                           "stderr_sha256": stderr_sha, "returncode": returncode,
                           "wall_seconds": elapsed}
                write_once(directory / "receipt.json", receipt)
                return receipt
            except (ValueError, KeyError, TypeError, OSError) as error:
                status = "invalid_output"
                with (directory / "validation-error.txt").open("x") as stream:
                    stream.write(str(error) + "\n")
        failure = {"schema": "pext.candidate-unit-artifact/v1", "status": status,
                   "scope": self.scope, "input_sha256": file_sha256(directory / "input.json"),
                   "partial_sha256": partial_sha, "stderr_sha256": stderr_sha,
                   "returncode": returncode, "wall_seconds": elapsed}
        write_once(directory / "failure.json", failure)
        return failure


def software_fixture_runner(binary, parent):
    """Use only with the fixed F27 software fixture; never a cohort receipt."""
    return CandidateUnitArtifacts(binary, file_sha256(Path(binary)), None,
                                  "software-fixture", parent)
