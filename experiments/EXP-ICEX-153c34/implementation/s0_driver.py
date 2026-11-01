#!/usr/bin/env python3
"""Fail-closed S0 gate orchestrator for EXP-ICEX-153c34."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import errno
import hashlib
import json
import os
import platform
import resource
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXP = "EXP-ICEX-153c34"
TASK = "TASK-20261001-4862b6"
OWNER = "executor-codex"
EPOCH = 1
SMOKE_NAMESPACE = "smoke|EXP-ICEX-153c34/v1"
EVIDENCE = HERE / "s0_evidence"
PANEL_JSON = HERE / "panel_fixtures.json"
V4_JSON = REPO / "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json"
V4_GENERATOR = REPO / "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.py"
PANEL_GENERATOR = HERE / "panel_fixtures.py"
PANEL_VERIFIER = HERE / "panel_fixtures_verifier.py"
SAGE_GATES = HERE / "s0_sage_gates.py"
MODAL_SAGE = HERE / "s0_modal_sage.py"
WORKER = HERE / "s0_gate_worker.py"
COUNTER_CHECKER = HERE / "s0_counter_checker.py"
IMPLEMENTATION_REPORT = HERE / "implementation_report.yaml"
SEMAEV_INVENTORY = REPO / "experiments/EXP-SDEG-85eefd/implementation/semaev_polys.json"
O5_GROUP = HERE / "o5_group.py"
SAGE_IMAGE_DIGEST = "sha256:4562582e9da21605ce1507932effb548d44888ed9e35ec768616049e6776391d"
SAGE_IMAGE = "sagemath/sagemath@" + SAGE_IMAGE_DIGEST
RSS_BYTES = 8 * 1024 ** 3
SAGE_BACKEND = "modal"
MODAL_PYTHON = None
MANDATED_REPOSITORY_VOLUME = Path("/Volumes/SSD990")
MANDATED_TMPDIR = MANDATED_REPOSITORY_VOLUME / ".tmp-agent"
EXECUTION_CHECKPOINT = REPO / "ledger/goals/GOAL-ICEX-001/checkpoints/BATCH-454f85.yaml"
EXECUTION_CHECKPOINT_SHA256 = "063874821efef1b5f25eedd6292c2d228e0646613e949fb86c4a9379cad92026"
# No committed Coordinator amendment authorising a substitute path has been
# located.  This is an execution-authority condition, not a portability guess.
PORTABILITY_AUTHORIZED = False
# The pinned checkpoint says ``evidence_id: null`` and ``execution not
# admitted``.  Only a committed Coordinator admission/amendment may change
# this frozen launch condition.
CHECKPOINT_EXECUTION_ADMITTED = False

AUDITED_SOURCE_FILES = (
    "experiments/EXP-ICEX-153c34/implementation/g1_s0.py",
    "experiments/EXP-ICEX-153c34/implementation/o5_group.py",
    "experiments/EXP-ICEX-153c34/implementation/panel_fixtures.py",
    "experiments/EXP-ICEX-153c34/implementation/panel_fixtures_verifier.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_counter_checker.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_counter_reference.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_driver.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_gate_worker.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_modal_sage.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_operation_spec.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_sage_gates.py",
    "experiments/EXP-ICEX-153c34/implementation/s0_static_tests.py",
)

GATES = {
    "G0-1": "v4 fixtures reproduce and panel_fixtures.py byte-reproduces independently",
    "G0-2": "f4 and f5 agree between Bareiss and subset-DP determinant reconstruction",
    "G0-3": "specialised f6 has 1,000 signed-sum and 1,000 non-sum checks per fixture",
    "G0-4": "G1 agrees with O5 on 200 smoke attempts per size, including L=8",
    "G0-5": "frozen power analysis reproduces committed rates within 3 MC standard errors",
    "G0-6": "standalone reference matches P_setup, arithmetic outputs, and S,G,X,V totals on 20 smoke queries",
}

PINNED = {
    "experiments/EXP-ICEX-153c34/specification.yaml": "f3342c52ea66c6272a8b3a61ea82265de0b865dd82339e4800c33a956daa598e",
    "ledger/decisions/DEC-20261001-36e4fa.yaml": "d0a1cd813d23015793bf6e64e8c6ef55c2e8d1223c9942b7379c67d835f509f7",
    "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json": "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45",
    "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.py": "bde44afb3e14c34d97bf50c154456565d12f0b5a1d33d63b473f0f4124b1f3b2",
    "experiments/EXP-ICEX-fa2b37/specification.yaml": "85735fc99b106af8b47f3e04bacb7c04e6decc615c2e7823640e160492a4ba49",
    "coordination/goals/GOAL-ICEX-001/batches/BATCH-454f85/tasks/TASK-20261001-768475/power_check.py": "daafecd5393b446133e80562e540a2957288467b38d8988ada8b9dddc7c973af",
    "coordination/goals/GOAL-ICEX-001/batches/BATCH-454f85/tasks/TASK-20261001-768475/power_check_output.json": "4566443ab0f3495292e3b9b31694458d36c631433a166cf184f0ea5095576135",
    "experiments/EXP-SDEG-85eefd/implementation/semaev_polys.json": "447d9bfff27f2b57b50e60fffde0c380ab697f4b2cbf006114bb7a50be10642e",
    "ledger/goals/GOAL-ICEX-001/checkpoints/BATCH-454f85.yaml": EXECUTION_CHECKPOINT_SHA256,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def machine_reading():
    system = Path("/")
    repo_volume = MANDATED_REPOSITORY_VOLUME
    try:
        nice_value = os.getpriority(os.PRIO_PROCESS, 0)
    except (AttributeError, OSError):
        nice_value = None
    rss_soft, rss_hard = resource.getrlimit(resource.RLIMIT_AS)
    root_free_bytes = shutil.disk_usage(system).free
    repository_volume_exists = repo_volume.is_dir()
    repository_free_bytes = (shutil.disk_usage(repo_volume).free
                             if repository_volume_exists else None)
    return {
        "read_at": now(), "host": platform.node(), "platform": platform.platform(),
        "python": sys.version, "loadavg_15m": float(os.getloadavg()[2]),
        "load_limit": 14.0,
        "root_free_bytes": root_free_bytes,
        "root_free_min_bytes": 5 * 1024 ** 3,
        "root_free_gib_display": round(root_free_bytes / 1024 ** 3, 6),
        "repository_volume": str(repo_volume),
        "repository_volume_exists": repository_volume_exists,
        "repository_free_bytes": repository_free_bytes,
        "repository_free_min_bytes": 20 * 1024 ** 3,
        "repository_free_gib_display": (round(repository_free_bytes / 1024 ** 3, 6)
                                         if repository_free_bytes is not None else None),
        "tmpdir_required": str(MANDATED_TMPDIR),
        "portability_substitution_authorized": PORTABILITY_AUTHORIZED,
        "rss_limit_gib": 8.0,
        "rlimit_as_soft_bytes": rss_soft, "rlimit_as_hard_bytes": rss_hard,
        "workers": 1, "nice_required": 10, "nice_actual": nice_value,
    }


def c7_ok(reading):
    nice_actual = reading["nice_actual"]
    nice_ok = (isinstance(nice_actual, int) and not isinstance(nice_actual, bool)
               and nice_actual >= reading["nice_required"])
    return (reading["loadavg_15m"] <= reading["load_limit"]
            and reading["root_free_bytes"] >= reading["root_free_min_bytes"]
            and reading["repository_volume_exists"]
            and reading["repository_free_bytes"] is not None
            and reading["repository_free_bytes"] >= reading["repository_free_min_bytes"]
            and nice_ok)


def git_state():
    def run(*args):
        process = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
        return process.stdout.strip() if process.returncode == 0 else None
    return {"commit": run("rev-parse", "HEAD"),
            "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "status_porcelain": (run("status", "--porcelain") or "").splitlines()}


def input_preflight():
    rows = []
    for relative, expected in PINNED.items():
        path = REPO / relative
        observed = sha256(path) if path.is_file() else None
        rows.append({"path": relative, "expected_sha256": expected,
                     "observed_sha256": observed, "pass": observed == expected})
    return rows


def implementation_manifest_preflight(document=None):
    """Bind launch to the exact audited Python-source manifest and commit."""
    errors = []
    if document is None:
        try:
            document = yaml.safe_load(IMPLEMENTATION_REPORT.read_text())
        except (OSError, yaml.YAMLError) as error:
            return {"pass": False, "errors": [
                "implementation report could not be read: %s" % error], "files": []}
    if not isinstance(document, dict):
        return {"pass": False, "errors": [
            "implementation report is not an object"], "files": []}

    source_commit = document.get("implementation_commit")
    source_tree = document.get("implementation_tree")
    if (not isinstance(source_commit, str) or len(source_commit) != 40
            or any(character not in "0123456789abcdef" for character in source_commit)):
        errors.append("implementation_commit is not a full lowercase Git object id")
    if (not isinstance(source_tree, str) or len(source_tree) != 40
            or any(character not in "0123456789abcdef" for character in source_tree)):
        errors.append("implementation_tree is not a full lowercase Git object id")

    file_rows = document.get("files")
    if not isinstance(file_rows, list):
        file_rows = []
        errors.append("implementation report files is not a list")
    by_path = {}
    for index, row in enumerate(file_rows):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            errors.append("implementation report file row %d is malformed" % index)
            continue
        path = row["path"]
        if path in by_path:
            errors.append("implementation report repeats path %s" % path)
        by_path[path] = row

    expected_paths = set(AUDITED_SOURCE_FILES)
    declared_source_paths = {
        path for path in by_path
        if path.startswith("experiments/EXP-ICEX-153c34/implementation/")
        and path.endswith(".py")
    }
    actual_source_paths = {
        str(path.relative_to(REPO)) for path in HERE.glob("*.py") if path.is_file()
    }
    if declared_source_paths != expected_paths:
        errors.append("report Python-source path set differs from frozen audited set")
    if actual_source_paths != expected_paths:
        errors.append("worktree Python-source path set differs from frozen audited set")

    def git(arguments, text=False):
        return subprocess.run(
            ["git", "-C", str(REPO), *arguments], capture_output=True,
            text=text, check=False)

    current_head = git(["rev-parse", "HEAD"], text=True)
    current_head_id = current_head.stdout.strip() if current_head.returncode == 0 else None
    commit_exists = False
    if isinstance(source_commit, str) and len(source_commit) == 40:
        commit_check = git(["cat-file", "-e", source_commit + "^{commit}"])
        commit_exists = commit_check.returncode == 0
        if not commit_exists:
            errors.append("implementation_commit is not available as a commit")
        elif current_head_id is None or git(
                ["merge-base", "--is-ancestor", source_commit, current_head_id]).returncode != 0:
            errors.append("implementation_commit is not an ancestor of current HEAD")
        tree = git(["rev-parse", source_commit + "^{tree}"], text=True)
        if tree.returncode != 0 or tree.stdout.strip() != source_tree:
            errors.append("implementation_tree disagrees with implementation_commit")

    rows = []
    for relative in AUDITED_SOURCE_FILES:
        row_errors = []
        declared = by_path.get(relative)
        declared_hash = declared.get("sha256") if isinstance(declared, dict) else None
        if (not isinstance(declared_hash, str) or len(declared_hash) != 64
                or any(character not in "0123456789abcdef" for character in declared_hash)):
            row_errors.append("missing or malformed declared SHA-256")
        path = REPO / relative
        current_hash = sha256(path) if path.is_file() else None
        if current_hash != declared_hash:
            row_errors.append("current file differs from declared SHA-256")
        committed_hash = None
        if commit_exists:
            committed = git(["show", source_commit + ":" + relative])
            if committed.returncode != 0:
                row_errors.append("file is absent from implementation_commit")
            else:
                committed_hash = hashlib.sha256(committed.stdout).hexdigest()
                if committed_hash != declared_hash:
                    row_errors.append("implementation_commit file differs from declared SHA-256")
        rows.append({
            "path": relative, "declared_sha256": declared_hash,
            "current_sha256": current_hash, "commit_sha256": committed_hash,
            "pass": not row_errors, "errors": row_errors,
        })
        errors.extend("%s: %s" % (relative, error) for error in row_errors)
    return {
        "pass": not errors, "implementation_commit": source_commit,
        "implementation_tree": source_tree, "current_head": current_head_id,
        "source_paths_exact": (declared_source_paths == expected_paths
                               and actual_source_paths == expected_paths),
        "files": rows, "errors": errors,
    }


def child_environment(tmpdir):
    return {**os.environ, "TMPDIR": str(tmpdir), "PYTHONDONTWRITEBYTECODE": "1",
            "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"}


def child_limits():
    try:
        current = os.getpriority(os.PRIO_PROCESS, 0)
        if current < 10:
            os.nice(10 - current)
    except (AttributeError, OSError):
        pass
    resource.setrlimit(resource.RLIMIT_AS, (RSS_BYTES, RSS_BYTES))


def _process_group_exists(process_group):
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    except OSError as error:
        if error.errno == errno.ESRCH:
            return False
        return True
    return True


def _wait_process_group_gone(process_group, timeout):
    deadline = time.monotonic() + timeout
    while _process_group_exists(process_group):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)
    return True


def _stream_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def _terminate_and_reap_process_group(process, stdout="", stderr=""):
    """TERM/KILL a native process group and prove leader and group are gone."""
    errors = []
    process_group = process.pid
    captured_stdout, captured_stderr = _stream_text(stdout), _stream_text(stderr)

    def capture(timeout):
        nonlocal captured_stdout, captured_stderr
        try:
            new_stdout, new_stderr = process.communicate(timeout=timeout)
            captured_stdout = _stream_text(new_stdout)
            captured_stderr = _stream_text(new_stderr)
            return True
        except subprocess.TimeoutExpired as error:
            if error.stdout is not None:
                captured_stdout = _stream_text(error.stdout)
            if error.stderr is not None:
                captured_stderr = _stream_text(error.stderr)
            return False
        except BaseException as error:  # cleanup must continue after decoder/pipe failures
            errors.append("communicate %s: %s" % (type(error).__name__, error))
            return False

    if _process_group_exists(process_group):
        try:
            os.killpg(process_group, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except OSError as error:
            if error.errno != errno.ESRCH:
                errors.append("SIGTERM %s: %s" % (type(error).__name__, error))
    capture(5)

    if process.poll() is None or _process_group_exists(process_group):
        try:
            os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError as error:
            if error.errno != errno.ESRCH:
                errors.append("SIGKILL %s: %s" % (type(error).__name__, error))
        capture(5)

    if process.poll() is None:
        try:
            process.wait(timeout=5)
        except BaseException as error:
            errors.append("wait %s: %s" % (type(error).__name__, error))
    group_gone = _wait_process_group_gone(process_group, 5)
    leader_reaped = process.poll() is not None
    if not leader_reaped:
        errors.append("direct child was not reaped")
    if not group_gone:
        errors.append("process group still exists after SIGKILL")
    return {
        "stdout": captured_stdout, "stderr": captured_stderr,
        "process_group_reaped": leader_reaped and group_gone,
        "termination_error": "; ".join(errors) if errors else None,
    }


def run_native(arguments, tmpdir, timeout):
    command = [sys.executable, *map(str, arguments)]
    started = now()
    process = None
    try:
        process = subprocess.Popen(
            command, cwd=REPO, env=child_environment(tmpdir),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=child_limits, start_new_session=True)
        stdout, stderr = process.communicate(timeout=timeout)
        # A normally reaped leader must not leave descendants in its private
        # session.  Clean them up and classify the launch as abnormal if it did.
        if _process_group_exists(process.pid):
            cleanup = _terminate_and_reap_process_group(process, stdout, stderr)
            return {"backend": "native", "command": command,
                    "started_at": started, "finished_at": now(),
                    "returncode": process.returncode,
                    "stdout": cleanup["stdout"], "stderr": cleanup["stderr"],
                    "timeout": False,
                    "process_group_reaped": cleanup["process_group_reaped"],
                    "termination_error": cleanup["termination_error"],
                    "lifecycle_error": "native leader exited with live descendants",
                    "launch_error": None}
        return {"backend": "native", "command": command,
                "started_at": started, "finished_at": now(),
                "returncode": process.returncode, "stdout": stdout,
                "stderr": stderr, "timeout": False, "process_group_reaped": True,
                "termination_error": None, "lifecycle_error": None,
                "launch_error": None}
    except subprocess.TimeoutExpired as error:
        cleanup = _terminate_and_reap_process_group(
            process, error.stdout or "", error.stderr or "")
        return {"backend": "native", "command": command,
                "started_at": started, "finished_at": now(),
                "returncode": process.returncode,
                "stdout": cleanup["stdout"], "stderr": cleanup["stderr"],
                "timeout": True, "timeout_seconds": timeout,
                "process_group_reaped": cleanup["process_group_reaped"],
                "termination_error": cleanup["termination_error"],
                "lifecycle_error": None, "launch_error": None}
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as error:
        cleanup = ({"stdout": "", "stderr": "",
                    "process_group_reaped": True, "termination_error": None}
                   if process is None else _terminate_and_reap_process_group(process))
        return {"backend": "native", "command": command,
                "started_at": started, "finished_at": now(),
                "returncode": process.returncode if process is not None else None,
                "stdout": cleanup["stdout"],
                "stderr": cleanup["stderr"] + ("\n" if cleanup["stderr"] else "") + str(error),
                "timeout": False,
                "process_group_reaped": cleanup["process_group_reaped"],
                "termination_error": cleanup["termination_error"],
                "lifecycle_error": None,
                "launch_error": "%s: %s" % (type(error).__name__, error)}
    except BaseException:
        if process is not None:
            _terminate_and_reap_process_group(process)
        raise


def modal_request(script, arguments, timeout):
    files = []
    used_names = set()

    def add_file(path, role):
        data = path.read_bytes()
        base = path.name
        name = base
        suffix = 1
        while name in used_names:
            name = "%d-%s" % (suffix, base)
            suffix += 1
        used_names.add(name)
        files.append({"name": name, "role": role, "sha256": hashlib.sha256(data).hexdigest(),
                      "content_base64": base64.b64encode(data).decode("ascii")})
        return name

    script_name = add_file(Path(script), "script")
    remote_arguments = []
    for argument in arguments:
        if isinstance(argument, Path):
            remote_arguments.append(add_file(argument, "input"))
        else:
            remote_arguments.append(str(argument))
    request = {
        "schema": "crypto.autoresearch.icex_s0_modal_request.v1",
        "request_sha256": "",
        "image": SAGE_IMAGE,
        "image_digest": SAGE_IMAGE_DIGEST,
        "script": script_name,
        "argv": remote_arguments,
        "files": files,
        "timeout_seconds": timeout,
        "resources": {
            "cpu": 1.0, "memory_mib": 8192, "max_containers": 1,
            "retries": 0, "nice": 10, "rlimit_as_bytes": RSS_BYTES,
            "network": "blocked", "single_use_container": True,
        },
        "environment": {
            "HOME": "/tmp", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "VECLIB_MAXIMUM_THREADS": "1",
        },
    }
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
    request["request_sha256"] = hashlib.sha256(canonical).hexdigest()
    return request


def run_modal_sage(script, arguments, tmpdir, timeout):
    request = modal_request(script, arguments, timeout)
    request_path = tmpdir / ("modal-" + request["request_sha256"] + ".json")
    write_json(request_path, request)
    python = MODAL_PYTHON or sys.executable
    command = [python, str(MODAL_SAGE), "--request", str(request_path)]
    python_path = Path(python).resolve()
    python_sha256 = sha256(python_path) if python_path.is_file() else None
    started = now()
    try:
        launcher = subprocess.run(command, cwd=REPO, env=child_environment(tmpdir),
                                  capture_output=True, timeout=timeout + 180,
                                  preexec_fn=child_limits)
    except (OSError, subprocess.TimeoutExpired) as error:
        if isinstance(error, subprocess.TimeoutExpired):
            stdout, stderr = error.stdout or b"", error.stderr or b""
            stdout = stdout.encode() if isinstance(stdout, str) else stdout
            stderr = stderr.encode() if isinstance(stderr, str) else stderr
        else:
            stdout, stderr = b"", str(error).encode()
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": None, "stdout_bytes": b"", "stderr_bytes": stderr,
                "timeout": isinstance(error, subprocess.TimeoutExpired), "timeout_seconds": timeout,
                "backend": "modal", "image": SAGE_IMAGE,
                "request_sha256": request["request_sha256"],
                "adapter_stdout_base64": base64.b64encode(stdout).decode("ascii"),
                "adapter_stderr_base64": base64.b64encode(stderr).decode("ascii"),
                "sandbox_termination_confirmed": False,
                "termination_error": "outer adapter failure; sandbox termination unconfirmed"}
    adapter_stdout = launcher.stdout
    adapter_stderr = launcher.stderr
    try:
        response = json.loads(adapter_stdout.decode("utf-8"))
        process = response["process"]
        stdout = base64.b64decode(process["stdout_base64"], validate=True)
        stderr = base64.b64decode(process["stderr_base64"], validate=True)
        transport_stdout = base64.b64decode(process["transport_stdout_base64"], validate=True)
        manifest_expected = [{"name": row["name"], "role": row["role"],
                              "sha256": row["sha256"],
                              "bytes": len(base64.b64decode(row["content_base64"]))}
                             for row in request["files"]]
        expected_command = ["nice", "-n", "10", "sage", "-python",
                            request["script"], *request["argv"]]
        nice_actual = response["worker"]["nice_actual"]
        expected_prefix = ("ICEX_LIMITS_V1\t%d\t%d\t%d\n"
                           % (nice_actual, RSS_BYTES // 1024,
                              RSS_BYTES // 1024)).encode()
        returncode = process["returncode"]
        timed_out = process["timeout"]
        peak_rss = process["peak_rss_bytes"]
        valid = (
            launcher.returncode == 0
            and response["schema"] == "crypto.autoresearch.icex_s0_modal_response.v1"
            and response["receipt_valid"] is True
            and response["request_sha256"] == request["request_sha256"]
            and response["image"] == SAGE_IMAGE
            and response["image_digest"] == SAGE_IMAGE_DIGEST
            and isinstance(response["modal_image_object_id"], str)
            and response["modal_image_object_id"].startswith("im-")
            and isinstance(response["modal_sandbox_id"], str)
            and response["modal_sandbox_id"].startswith("sb-")
            and response["modal_sdk_version"] == "1.6.0"
            and response["adapter_sha256"] == sha256(MODAL_SAGE)
            and response["resources"] == request["resources"]
            and response["input_manifest"] == manifest_expected
            and response["worker"]["execution"] == "fresh Modal Sandbox; terminated after one verifier"
            and response["worker"]["provider_cpu_request_limit"] == [1.0, 1.0]
            and response["worker"]["provider_memory_request_limit_mib"] == [8192, 8192]
            and response["worker"]["sandbox_timeout_seconds"] == timeout + 120
            and response["worker"]["network"] == "blocked"
            and response["worker"]["resource_limits_verified"] is True
            and response["worker"]["resource_limit_error"] is None
            and response["worker"]["termination_error"] is None
            and isinstance(nice_actual, int) and not isinstance(nice_actual, bool)
            and nice_actual >= 10
            and response["worker"]["rlimit_as_soft_bytes"] == RSS_BYTES
            and response["worker"]["rlimit_as_hard_bytes"] == RSS_BYTES
            and process["command"] == expected_command
            and process["timeout_seconds"] == timeout
            and isinstance(process["started_at"], str) and bool(process["started_at"])
            and isinstance(process["finished_at"], str) and bool(process["finished_at"])
            and isinstance(returncode, int) and not isinstance(returncode, bool)
            and isinstance(timed_out, bool)
            and timed_out == (returncode == -1)
            and isinstance(process["elapsed_seconds"], (int, float))
            and process["elapsed_seconds"] >= 0
            and (peak_rss is None or (isinstance(peak_rss, int)
                                      and not isinstance(peak_rss, bool) and peak_rss >= 0))
            and hashlib.sha256(stdout).hexdigest() == process["stdout_sha256"]
            and hashlib.sha256(stderr).hexdigest() == process["stderr_sha256"]
            and hashlib.sha256(transport_stdout).hexdigest() == process["transport_stdout_sha256"]
            and transport_stdout == expected_prefix + stdout
        )
        if not valid:
            raise ValueError("remote receipt validation failed")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as error:
        combined = (b"Modal Sage adapter failed closed: " + str(error).encode() + b"\n"
                    + adapter_stderr + adapter_stdout)
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": None, "stdout_bytes": b"", "stderr_bytes": combined,
                "timeout": False, "backend": "modal", "image": SAGE_IMAGE,
                "request_sha256": request["request_sha256"],
                "adapter_returncode": launcher.returncode,
                "adapter_stdout_base64": base64.b64encode(adapter_stdout).decode("ascii"),
                "adapter_stderr_base64": base64.b64encode(adapter_stderr).decode("ascii"),
                "sandbox_termination_confirmed": False,
                "termination_error": "invalid adapter receipt; sandbox termination unconfirmed"}
    return {
        "command": process["command"], "launcher_command": command,
        "started_at": process["started_at"], "finished_at": process["finished_at"],
        "returncode": process["returncode"], "stdout_bytes": stdout, "stderr_bytes": stderr,
        "timeout": process["timeout"], "timeout_seconds": process["timeout_seconds"],
        "elapsed_seconds": process["elapsed_seconds"], "peak_rss_bytes": process["peak_rss_bytes"],
        "backend": "modal", "image": response["image"],
        "image_digest": response["image_digest"], "resources": response["resources"],
        "input_manifest": response["input_manifest"],
        "request_sha256": response["request_sha256"],
        "modal_sandbox_id": response.get("modal_sandbox_id"),
        "modal_image_object_id": response.get("modal_image_object_id"),
        "modal_sdk_version": response.get("modal_sdk_version"),
        "adapter_started_at": response.get("adapter_started_at"),
        "adapter_finished_at": response.get("adapter_finished_at"),
        "adapter_elapsed_seconds": response.get("adapter_elapsed_seconds"),
        "worker": response.get("worker"),
        "adapter_sha256": response["adapter_sha256"],
        "modal_python": str(python_path), "modal_python_sha256": python_sha256,
        "adapter_returncode": launcher.returncode,
        "adapter_stdout_sha256": hashlib.sha256(adapter_stdout).hexdigest(),
        "adapter_stderr_base64": base64.b64encode(adapter_stderr).decode("ascii"),
        "sandbox_termination_confirmed": True,
        "termination_error": None,
    }


def run_sage(script, arguments, tmpdir, timeout):
    if SAGE_BACKEND != "modal":
        return {"command": [], "started_at": now(), "finished_at": now(),
                "returncode": None, "stdout_bytes": b"",
                "stderr_bytes": b"frozen S0 driver requires the pinned Modal backend",
                "timeout": False, "backend": SAGE_BACKEND,
                "sandbox_termination_confirmed": False,
                "termination_error": "non-Modal backend refused before launch"}
    return run_modal_sage(script, arguments, tmpdir, timeout)


def public_receipt(process):
    stdout = process.get("stdout", "")
    stderr = process.get("stderr", "")
    if "stdout_bytes" in process:
        stdout_bytes = process["stdout_bytes"]
        stderr_bytes = process["stderr_bytes"]
    else:
        stdout_bytes = stdout if isinstance(stdout, bytes) else stdout.encode()
        stderr_bytes = stderr if isinstance(stderr, bytes) else stderr.encode()
    return {key: value for key, value in process.items()
            if key not in ("stdout", "stderr", "stdout_bytes", "stderr_bytes")} | {
        "stdout_sha256": hashlib.sha256(stdout_bytes).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr_bytes).hexdigest(),
        "stdout_base64": base64.b64encode(stdout_bytes).decode("ascii"),
        "stderr_base64": base64.b64encode(stderr_bytes).decode("ascii"),
        "stderr": stderr_bytes.decode("utf-8", "replace"),
    }


def modal_termination_confirmed(process):
    """Fail closed unless a Modal receipt proves that its sandbox terminated."""
    if process.get("backend") != "modal":
        return False
    return (process.get("sandbox_termination_confirmed") is True
            and isinstance(process.get("modal_sandbox_id"), str)
            and process["modal_sandbox_id"].startswith("sb-")
            and isinstance(process.get("worker"), dict)
            and process["worker"].get("termination_error") is None)


def unstarted_process(observation):
    return {"command": [], "started_at": None, "finished_at": None,
            "returncode": None, "stdout_bytes": b"", "stderr_bytes": b"",
            "timeout": False, "backend": SAGE_BACKEND,
            "not_started": True, "observation": observation,
            "sandbox_termination_confirmed": False}


def write_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")


def gate_record(gate_id, passed=False, failed=False, blocked=False,
                classification="implementation_error", observation="", evidence=()):
    return {"id": gate_id, "description": GATES[gate_id], "pass": bool(passed),
            "fail": bool(failed), "blocked": bool(blocked), "classification": classification,
            "evidence_paths": [str(Path(path).relative_to(REPO)) for path in evidence],
            "observation": observation}


def bind_native_reaping(record, *processes):
    record["native_process_group_reaped"] = all(
        process.get("process_group_reaped") is True for process in processes)
    return record


def process_lifecycle_status(process):
    """Return backend-specific termination proof without cross-applying fields."""
    backend = process.get("backend")
    if backend == "modal":
        confirmed = modal_termination_confirmed(process)
        return {"backend": backend, "confirmed": confirmed,
                "proof": "sandbox_termination_confirmed",
                "error": None if confirmed else
                "Modal sandbox termination was not confirmed"}
    if backend == "native":
        confirmed = process.get("process_group_reaped") is True
        return {"backend": backend, "confirmed": confirmed,
                "proof": "process_group_reaped",
                "error": None if confirmed else
                "native process group reaping was not confirmed"}
    return {"backend": backend, "confirmed": False, "proof": None,
            "error": "gate process receipt has an unknown backend"}


def bind_gate_lifecycle(record, process):
    lifecycle = process_lifecycle_status(process)
    record["execution_backend"] = lifecycle["backend"]
    if lifecycle["backend"] == "modal":
        record["sandbox_termination_confirmed"] = lifecycle["confirmed"]
    elif lifecycle["backend"] == "native":
        record["native_process_group_reaped"] = lifecycle["confirmed"]
    return record


def parse_process_json(process, binary=False):
    if binary:
        return json.loads(process["stdout_bytes"].decode("utf-8"))
    return json.loads(process["stdout"])


def run_g01(tmpdir):
    calls = (("generator", PANEL_GENERATOR),
             ("independent_verifier", PANEL_VERIFIER),
             ("v4_reproducer", V4_GENERATOR))
    processes = {}
    sequence_attestations = []
    prior_name = None
    for name, script in calls:
        if prior_name is not None:
            confirmed = modal_termination_confirmed(processes[prior_name])
            sequence_attestations.append({
                "before": name, "prior_call": prior_name,
                "prior_sandbox_termination_confirmed": confirmed,
                "no_prior_live_sandbox_attested": confirmed,
            })
            if not confirmed:
                processes[name] = unstarted_process(
                    "not started after unconfirmed prior Modal sandbox termination")
                prior_name = name
                continue
        processes[name] = run_sage(script, [], tmpdir, 7200)
        prior_name = name
    generator = processes["generator"]
    verifier = processes["independent_verifier"]
    v4 = processes["v4_reproducer"]
    panel_match = (generator["returncode"] == 0 and verifier["returncode"] == 0
                   and generator["stdout_bytes"] == verifier["stdout_bytes"])
    v4_match = (v4["returncode"] == 0 and v4["stdout_bytes"] == V4_JSON.read_bytes())
    if panel_match:
        try:
            panel_document = json.loads(generator["stdout_bytes"])
            expected_cells = {(bits, seed) for bits in (16, 18, 20, 22, 24)
                              for seed in (1, 2, 3, 4)}
            observed_cells = {(row["bits"], row["seed"])
                              for row in panel_document.get("panel", [])}
            panel_shape_ok = (len(panel_document.get("panel", [])) == 20
                              and observed_cells == expected_cells)
            if panel_shape_ok:
                PANEL_JSON.write_bytes(generator["stdout_bytes"])
        except (json.JSONDecodeError, KeyError, TypeError):
            panel_document = None
            panel_shape_ok = False
    else:
        panel_document = None
        panel_shape_ok = False
    passed = panel_match and panel_shape_ok and v4_match
    evidence_path = EVIDENCE / "g0-1-reproduction.json"
    evidence = {"schema": "crypto.autoresearch.icex_s0_gate_evidence.v1", "gate": "G0-1",
        "pass": passed, "panel_byte_equal": panel_match, "panel_shape_ok": panel_shape_ok,
        "v4_byte_equal": v4_match,
        "panel_sha256": (hashlib.sha256(generator["stdout_bytes"]).hexdigest()
                           if generator["returncode"] == 0 else None),
        "v4_expected_sha256": sha256(V4_JSON),
        "panel_entries": len(panel_document.get("panel", [])) if panel_document else None,
        "panel_shape_ok": panel_shape_ok,
        "max_workers": 1,
        "sequence_attestations": sequence_attestations,
        "all_sandbox_terminations_confirmed": all(
            modal_termination_confirmed(process) for process in processes.values()
            if not process.get("not_started")),
        "processes": {name: public_receipt(process)
                      for name, process in processes.items()}}
    write_json(evidence_path, evidence)
    if passed:
        record = gate_record("G0-1", passed=True, classification="pass",
                           observation="v4 and 20-panel fixture byte streams reproduced exactly",
                           evidence=(evidence_path, PANEL_JSON))
        record["sandbox_termination_confirmed"] = evidence["all_sandbox_terminations_confirmed"]
        return record
    blocked = any(item["timeout"] or item["returncode"] != 0 for item in (generator, verifier, v4))
    record = gate_record("G0-1", failed=not blocked, blocked=blocked,
                       classification="infrastructure_error" if blocked else "implementation_error",
                       observation="fixture byte reproduction did not complete or disagreed",
                       evidence=(evidence_path,))
    record["sandbox_termination_confirmed"] = evidence["all_sandbox_terminations_confirmed"]
    return record


def run_json_gate(gate_id, process, evidence_path):
    result = None
    try:
        result = parse_process_json(process, binary="stdout_bytes" in process)
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    write_json(evidence_path, {"schema": "crypto.autoresearch.icex_s0_gate_evidence.v1",
                               "gate": gate_id, "process": public_receipt(process),
                               "result": result})
    lifecycle = process_lifecycle_status(process)
    if not lifecycle["confirmed"]:
        return bind_gate_lifecycle(
            gate_record(gate_id, blocked=True, classification="infrastructure_error",
                        observation=lifecycle["error"], evidence=(evidence_path,)),
            process)
    if lifecycle["backend"] == "native" and process.get("lifecycle_error"):
        return bind_gate_lifecycle(
            gate_record(gate_id, blocked=True, classification="infrastructure_error",
                        observation=process["lifecycle_error"],
                        evidence=(evidence_path,)), process)
    if process["timeout"]:
        return bind_gate_lifecycle(
            gate_record(gate_id, blocked=True, classification="resource_exhaustion",
                        observation="gate process watchdog expired", evidence=(evidence_path,)),
            process)
    if result is None:
        return bind_gate_lifecycle(
            gate_record(gate_id, blocked=True, classification="infrastructure_error",
                        observation="gate emitted no parseable JSON receipt",
                        evidence=(evidence_path,)), process)
    if result.get("pass") is True and process["returncode"] == 0:
        return bind_gate_lifecycle(
            gate_record(gate_id, passed=True, classification="pass",
                        observation="frozen gate condition passed", evidence=(evidence_path,)),
            process)
    return bind_gate_lifecycle(
        gate_record(gate_id, failed=not result.get("blocked", False),
                    blocked=result.get("blocked", False),
                    classification=result.get("classification", "implementation_error"),
                    observation=result.get("observation", "frozen gate condition did not pass"),
                    evidence=(evidence_path,)), process)


def run_g02(tmpdir):
    process = run_sage(SAGE_GATES, ["--gate", "G0-2", "--v4", V4_JSON,
                                    "--panel", PANEL_JSON,
                                    "--inventory", SEMAEV_INVENTORY,
                                    "--o5-group", O5_GROUP], tmpdir, 7200)
    record = run_json_gate("G0-2", process, EVIDENCE / "g0-2-determinants.json")
    record["sandbox_termination_confirmed"] = modal_termination_confirmed(process)
    return record


def run_g03(tmpdir):
    process = run_native([WORKER, "--gate", "G0-3", "--panel", PANEL_JSON], tmpdir, 7200)
    return run_json_gate("G0-3", process, EVIDENCE / "g0-3-f6-identity.json")


def run_g05(tmpdir):
    process = run_native([WORKER, "--gate", "G0-5"], tmpdir, 7200)
    return run_json_gate("G0-5", process, EVIDENCE / "g0-5-power-reproduction.json")


def run_g06(tmpdir):
    producer = run_native([WORKER, "--gate", "G0-6"], tmpdir, 7200)
    producer_path = EVIDENCE / "g0-6-operation-log.json"
    try:
        result = parse_process_json(producer)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        result = None
    if result is not None:
        result["producer_process"] = public_receipt(producer)
    write_json(producer_path, result or {"parse_error": True, "process": public_receipt(producer)})
    if producer.get("process_group_reaped") is not True:
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation="producer process group reaping was not confirmed",
                        evidence=(producer_path,)), producer)
    if producer.get("lifecycle_error"):
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation=producer["lifecycle_error"], evidence=(producer_path,)),
            producer)
    if producer["timeout"]:
        return bind_native_reaping(
            gate_record("G0-6", blocked=True,
                        classification="resource_exhaustion",
                        observation="20-query producer watchdog expired",
                        evidence=(producer_path,)), producer)
    if producer.get("launch_error") or producer.get("returncode") != 0:
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation="operation-log producer failed to execute cleanly",
                        evidence=(producer_path,)), producer)
    if (not isinstance(result, dict) or result.get("queries_completed") != 20
            or not isinstance(result.get("operation_log"), list)
            or len(result["operation_log"]) != 20):
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation="producer receipt was malformed or incomplete",
                        evidence=(producer_path,)), producer)
    checker = run_native([COUNTER_CHECKER, producer_path], tmpdir, 7200)
    checker_path = EVIDENCE / "g0-6-independent-check.json"
    try:
        checked = parse_process_json(checker)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        checked = None
    write_json(checker_path, {"process": public_receipt(checker), "result": checked})
    if checker.get("process_group_reaped") is not True:
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation="counter-checker process group reaping was not confirmed",
                        evidence=(producer_path, checker_path)), producer, checker)
    if checker.get("lifecycle_error"):
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation=checker["lifecycle_error"],
                        evidence=(producer_path, checker_path)), producer, checker)
    if checker["timeout"]:
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="resource_exhaustion",
                        observation="independent counter checker watchdog expired",
                        evidence=(producer_path, checker_path)), producer, checker)
    if checker.get("launch_error") or checker.get("returncode") != 0 or not isinstance(checked, dict):
        return bind_native_reaping(
            gate_record("G0-6", blocked=True, classification="infrastructure_error",
                        observation="counter checker failed or emitted a malformed receipt",
                        evidence=(producer_path, checker_path)), producer, checker)
    if checked.get("pass") is True:
        return bind_native_reaping(
            gate_record("G0-6", passed=True, classification="pass",
                        observation=("standalone arithmetic reference matched setup state, "
                                     "20 query outputs, and every primitive total"),
                        evidence=(producer_path, checker_path)), producer, checker)
    return bind_native_reaping(
        gate_record("G0-6", failed=True, classification="implementation_error",
                    observation="independent semantic counter reference disagreed",
                    evidence=(producer_path, checker_path)), producer, checker)


def run_g04(tmpdir):
    sizes = [(20, 8), (16, 5), (18, 6), (22, 10), (24, 13)]
    results, processes, native_reaped = [], [], []
    for bits, size in sizes:
        reading = machine_reading()
        if not c7_ok(reading):
            results.append({"bits": bits, "L": size, "pass": False, "blocked": True,
                            "classification": "infrastructure_error",
                            "observation": "C-7 failed before smoke size", "machine": reading})
            break
        process = run_native([WORKER, "--gate", "G0-4", "--bits", str(bits), "--L", str(size)],
                             tmpdir, 48 * 3600)
        processes.append(public_receipt(process))
        native_reaped.append(process.get("process_group_reaped") is True)
        if process.get("process_group_reaped") is not True:
            results.append({"bits": bits, "L": size, "pass": False, "blocked": True,
                            "classification": "infrastructure_error",
                            "observation": "native process group reaping was not confirmed"})
            break
        if process.get("lifecycle_error"):
            results.append({"bits": bits, "L": size, "pass": False, "blocked": True,
                            "classification": "infrastructure_error",
                            "observation": process["lifecycle_error"]})
            break
        try:
            result = parse_process_json(process)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
            result = {"bits": bits, "L": size, "pass": False, "blocked": True,
                      "classification": "resource_exhaustion" if process["timeout"] else "infrastructure_error",
                      "observation": "size process emitted no parseable result"}
        results.append(result)
        if result.get("blocked") or result.get("pass") is False:
            break
    by_bits = sorted(results, key=lambda row: row.get("fixture", {}).get("bits", row.get("bits", 0)))
    passed = len(results) == 5 and all(row.get("pass") is True for row in results)
    hard_failure = any(row.get("pass") is False and not row.get("blocked") for row in results)
    blocked = not hard_failure and (any(row.get("blocked") for row in results) or len(results) < 5)
    evidence_path = EVIDENCE / "g0-4-smoke-agreement.json"
    write_json(evidence_path, {"schema": "crypto.autoresearch.icex_s0_gate_evidence.v1",
        "gate": "G0-4", "pass": passed, "blocked": blocked,
        "sizes_required": [{"bits": b, "L": l, "attempts": 200} for b, l in sorted(sizes)],
        "sizes": by_bits, "processes": processes,
        "larger_sizes_after_terminal_blocker_started": len(results) == 5})
    timing_by_key = {}
    for row in results:
        fixture = row.get("fixture", {})
        key = (fixture.get("bits", row.get("bits")), fixture.get("L", row.get("L")))
        timing_by_key[key] = row
    timing_table = []
    for bits, size in sizes:
        row = timing_by_key.get((bits, size))
        timing_table.append({
            "bits": bits, "L": size, "attempts_required": 200,
            "attempts_completed": row.get("attempts_completed") if row else None,
            "median_query_seconds": row.get("median_query_seconds") if row else None,
            "setup_seconds": row.get("setup_seconds") if row else None,
            "oracle_seconds": row.get("oracle_seconds") if row else None,
            "pass": row.get("pass") if row else None,
            "blocked": row.get("blocked") if row else True,
            "classification": (row.get("classification") if row
                               else "not_started_after_terminal_condition"),
        })
    if passed:
        record = gate_record("G0-4", passed=True, classification="pass",
                           observation="all 1,000 smoke decisions agreed with O5",
                           evidence=(evidence_path,))
        record["per_size_timing"] = timing_table
        record["native_process_group_reaped"] = all(native_reaped)
        return record
    blocking_class = next((row.get("classification") for row in results if row.get("blocked")),
                          "resource_exhaustion")
    record = gate_record("G0-4", blocked=blocked, failed=not blocked,
                       classification=blocking_class if blocked else "implementation_error",
                       observation="G1/O5 smoke panel did not complete; see per-size receipt",
                       evidence=(evidence_path,))
    record["per_size_timing"] = timing_table
    record["native_process_group_reaped"] = all(native_reaped)
    return record


def pending_gate(gate_id, observation, classification="infrastructure_error"):
    return gate_record(gate_id, blocked=True, classification=classification, observation=observation)


def write_reports(started, readings, gates, command, preflight, protocol_deviations,
                  implementation_manifest):
    all_pass = all(gate["pass"] for gate in gates)
    any_started = any(gate["evidence_paths"] for gate in gates)
    status = "passed" if all_pass else ("completed_with_failures" if any_started else "not_started")
    report = {
        "schema": "crypto.autoresearch.exp_s0_gates.v1", "task_id": TASK,
        "experiment_id": EXP, "goal_id": "GOAL-ICEX-001", "owner": OWNER,
        "epoch": EPOCH, "smoke_namespace": SMOKE_NAMESPACE,
        "sage_backend": SAGE_BACKEND,
        "sage_image": SAGE_IMAGE,
        "execution_scope": "S0 gates G0-1..G0-6 only; no frozen/protocol run",
        "started_at": started, "finished_at": now(), "command": command,
        "git": git_state(), "input_preflight": preflight,
        "implementation_source_manifest_preflight": implementation_manifest,
        "machine_protection_readings": readings,
        "machine_protection_passed_at_launch": bool(readings and c7_ok(readings[0])),
        "execution_authority": {
            "frozen_tmpdir": str(MANDATED_TMPDIR),
            "frozen_repository_volume": str(MANDATED_REPOSITORY_VOLUME),
            "portable_substitution_authorized": PORTABILITY_AUTHORIZED,
            "checkpoint": str(EXECUTION_CHECKPOINT.relative_to(REPO)),
            "checkpoint_sha256": EXECUTION_CHECKPOINT_SHA256,
            "checkpoint_execution_admitted": CHECKPOINT_EXECUTION_ADMITTED,
            "blockers": [blocker for blocker in (
                (None if CHECKPOINT_EXECUTION_ADMITTED else
                 "committed checkpoint says execution not admitted"),
                (None if MANDATED_REPOSITORY_VOLUME.is_dir() else
                 "Coordinator portability mapping/amendment required before launch"),
            ) if blocker is not None],
        },
        "runner_status": status, "gates": gates,
        "protocol_deviations": protocol_deviations,
        "forbidden_actions_not_taken": ["no frozen scientific query draw",
            "no charged protocol run", "no frozen-fixture cost field in G0-4",
            "no evaluation/CRT or direct Cartesian V^5 membership substitute",
            "no experiments/EXP-ICEX-153c34/runs/RUN-* directory",
            "no specification, fixture, hypothesis or ledger edit"],
        "observation_only": True,
    }
    gates_path = HERE / "s0_gates_report.yaml"
    gates_path.write_text(yaml.safe_dump(report, sort_keys=False))
    note = ["# EXP-ICEX-153c34 implementation note", "",
        "Task `TASK-20261001-4862b6` is limited to the frozen S0 gates. The G1 path uses",
        "the D-2 monomial-basis pseudo-resultant, deterministic lex Buchberger, recursive",
        "gcd/specialisation root extraction, and independent signed point recovery. It uses",
        "no direct Cartesian/grid membership substitute and never consults O5 inside G1.",
        "The mandated all-vanishing root branch retains every V candidate and is charged in X.",
        "D-4 witness certification and D-5 B0 hit-order selection remain explicitly unimplemented",
        "in this S0-only package and cannot be used for a protocol run.",
        "", "Gate outcomes:", ""]
    for gate in gates:
        label = "PASS" if gate["pass"] else ("BLOCKED" if gate["blocked"] else "FAIL")
        note.append("* `%s`: **%s** — %s" % (gate["id"], label, gate["observation"]))
    note += ["", "No scientific interpretation is made. Failures and resource stops are",
             "implementation/infrastructure observations, not evidence about the hypothesis.", ""]
    (HERE / "implementation.md").write_text("\n".join(note))
    files = []
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.name != "implementation_report.yaml" and "__pycache__" not in path.parts:
            files.append({"path": str(path.relative_to(REPO)), "sha256": sha256(path)})
    implementation_commit = git_state()["commit"]
    tree_process = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", implementation_commit + "^{tree}"],
        capture_output=True, text=True, check=False)
    implementation_tree = (tree_process.stdout.strip()
                           if tree_process.returncode == 0 else None)
    impl = {
        "schema": "crypto.autoresearch.implementation_report.v1", "task_id": TASK,
        "experiment_id": EXP, "implementation_commit": implementation_commit,
        "implementation_tree": implementation_tree,
        "commit_binding": ("implementation_commit identifies the immutable source commit; "
                           "this report is stored in a later evidence commit and does not "
                           "claim a self-referential hash"),
        "owner": OWNER, "epoch": EPOCH,
        "write_scope": ["experiments/EXP-ICEX-153c34/implementation/"],
        "files": files,
        "commands": [command], "results": {"runner_status": status,
            "implementation_source_manifest_passed_before_gates":
                implementation_manifest.get("pass") is True,
            "s0_gates_report": str(gates_path.relative_to(REPO)),
            "gates_passed": [gate["id"] for gate in gates if gate["pass"]],
            "gates_failed": [gate["id"] for gate in gates if gate["fail"]],
            "gates_blocked": [gate["id"] for gate in gates if gate["blocked"]]},
        "infrastructure_impediment": None if all_pass else "see per-gate terminal classifications",
        "protocol_complete": all_pass, "requires_rerun": not all_pass,
        "scientific_interpretation": "none; executor observations only",
    }
    (HERE / "implementation_report.yaml").write_text(yaml.safe_dump(impl, sort_keys=False))


def main(argv=None):
    global SAGE_BACKEND, MODAL_PYTHON
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-gates", action="store_true", required=True)
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--epoch", type=int, default=EPOCH)
    parser.add_argument("--launch-command", default=None)
    parser.add_argument("--sage-backend", choices=("modal",),
                        default=os.environ.get("ICEX_S0_SAGE_BACKEND", "modal"))
    parser.add_argument("--modal-python", default=os.environ.get("ICEX_S0_MODAL_PYTHON"))
    args = parser.parse_args(argv)
    if args.owner != OWNER or args.epoch != EPOCH:
        raise SystemExit("refused: owner/epoch must be executor-codex/1")
    SAGE_BACKEND = args.sage_backend
    MODAL_PYTHON = args.modal_python
    if SAGE_BACKEND == "modal" and MODAL_PYTHON is not None:
        candidate = Path(MODAL_PYTHON)
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise SystemExit("refused: --modal-python is not an executable file")
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    bounded_hard = RSS_BYTES if current_hard == resource.RLIM_INFINITY else min(current_hard, RSS_BYTES)
    resource.setrlimit(resource.RLIMIT_AS, (min(RSS_BYTES, bounded_hard), bounded_hard))
    command = args.launch_command or " ".join([sys.executable, *sys.argv])
    started = now()
    implementation_manifest = implementation_manifest_preflight()
    if implementation_manifest.get("pass") is not True:
        print(json.dumps({
            "refused": "audited implementation source manifest mismatch",
            "preflight": implementation_manifest,
        }, sort_keys=True), file=sys.stderr)
        return 8
    readings = [machine_reading()]
    preflight = input_preflight()
    deviations = [{"kind": "development_probe", "classification": "procedure_deviation",
                   "observation": "Before the frozen runner, one non-protocol L=3 development query was started without the required nice/C-7 wrapper and manually terminated after 34 seconds; it emitted no result and is not gate evidence."}]
    deviations.append({
        "kind": "execution_authority",
        "classification": "hard_blocker",
        "observation": ("The frozen card literally requires TMPDIR=/Volumes/SSD990/.tmp-agent "
                        "and C-7 on /Volumes/SSD990. No committed Coordinator amendment "
                        "authorises /workspace or any task-local substitute; none is used."),
        "required_resolution": "committed Coordinator portability mapping/amendment",
    })
    deviations.append({
        "kind": "checkpoint_authority",
        "classification": "hard_blocker",
        "observation": ("The pinned BATCH-454f85 checkpoint has evidence_id null and "
                        "states that execution is not admitted."),
        "checkpoint": str(EXECUTION_CHECKPOINT.relative_to(REPO)),
        "checkpoint_sha256": EXECUTION_CHECKPOINT_SHA256,
        "required_resolution": "committed Coordinator execution admission/amendment",
    })
    if not CHECKPOINT_EXECUTION_ADMITTED:
        gates = [pending_gate(
            gate_id,
            "not started: pinned checkpoint explicitly says execution not admitted",
            "execution_authority") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations,
                      implementation_manifest)
        return 7
    if not MANDATED_REPOSITORY_VOLUME.is_dir():
        gates = [pending_gate(
            gate_id,
            "not started: frozen /Volumes/SSD990 authority cannot be substituted; Coordinator amendment required",
            "execution_authority") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations,
                      implementation_manifest)
        return 6
    if not c7_ok(readings[0]):
        gates = [pending_gate(gate_id, "not started because C-7 failed at launch") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations,
                      implementation_manifest)
        return 3
    if not all(row["pass"] for row in preflight):
        gates = [pending_gate(gate_id, "not started because a frozen input hash mismatched",
                              "specification_error") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations,
                      implementation_manifest)
        return 4
    if git_state()["status_porcelain"]:
        gates = [pending_gate(gate_id,
                              "not started because the immutable implementation worktree was dirty",
                              "execution_precondition") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations,
                      implementation_manifest)
        return 5
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="icex-s0-", dir=MANDATED_TMPDIR) as temporary:
        tmpdir = Path(temporary)
        outcomes = {"G0-1": run_g01(tmpdir)}
        readings.append(machine_reading())
        global_stop = None
        if outcomes["G0-1"].get("sandbox_termination_confirmed") is False:
            global_stop = "unconfirmed Modal sandbox termination in G0-1"
        if global_stop:
            outcomes["G0-2"] = pending_gate("G0-2", global_stop, "infrastructure_error")
            outcomes["G0-3"] = pending_gate("G0-3", global_stop, "infrastructure_error")
        elif outcomes["G0-1"]["pass"] and c7_ok(readings[-1]):
            outcomes["G0-2"] = run_g02(tmpdir)
            readings.append(machine_reading())
            if outcomes["G0-2"].get("sandbox_termination_confirmed") is False:
                global_stop = "unconfirmed Modal sandbox termination in G0-2"
                outcomes["G0-3"] = pending_gate("G0-3", global_stop, "infrastructure_error")
            else:
                outcomes["G0-3"] = (run_g03(tmpdir) if c7_ok(readings[-1])
                                     else pending_gate("G0-3", "C-7 failed between stages"))
        else:
            outcomes["G0-2"] = pending_gate("G0-2", "G0-1 dependency did not pass")
            outcomes["G0-3"] = pending_gate("G0-3", "G0-1 dependency did not pass")
        if outcomes["G0-3"].get("native_process_group_reaped") is False:
            global_stop = "unconfirmed native process-group reaping in G0-3"
        if global_stop:
            for gate_id in ("G0-5", "G0-6", "G0-4"):
                outcomes[gate_id] = pending_gate(gate_id, global_stop, "infrastructure_error")
        else:
            readings.append(machine_reading())
            outcomes["G0-5"] = (run_g05(tmpdir) if c7_ok(readings[-1])
                                  else pending_gate("G0-5", "C-7 failed between stages"))
            if outcomes["G0-5"].get("native_process_group_reaped") is False:
                global_stop = "unconfirmed native process-group reaping in G0-5"
            if global_stop:
                outcomes["G0-6"] = pending_gate("G0-6", global_stop, "infrastructure_error")
                outcomes["G0-4"] = pending_gate("G0-4", global_stop, "infrastructure_error")
            else:
                readings.append(machine_reading())
                outcomes["G0-6"] = (run_g06(tmpdir) if c7_ok(readings[-1])
                                      else pending_gate("G0-6", "C-7 failed between stages"))
                if outcomes["G0-6"].get("native_process_group_reaped") is False:
                    global_stop = "unconfirmed native process-group reaping in G0-6"
                if global_stop:
                    outcomes["G0-4"] = pending_gate(
                        "G0-4", global_stop, "infrastructure_error")
                else:
                    readings.append(machine_reading())
                    outcomes["G0-4"] = (run_g04(tmpdir) if c7_ok(readings[-1])
                                          else pending_gate(
                                              "G0-4", "C-7 failed between stages"))
        gates = [outcomes[gate_id] for gate_id in GATES]
    write_reports(started, readings, gates, command, preflight, deviations,
                  implementation_manifest)
    return 0 if all(gate["pass"] for gate in gates) else 2


if __name__ == "__main__":
    raise SystemExit(main())
