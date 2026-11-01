#!/usr/bin/env python3
"""Fail-closed S0 gate orchestrator for EXP-ICEX-153c34."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
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
SAGE_IMAGE_DIGEST = "sha256:4562582e9da21605ce1507932effb548d44888ed9e35ec768616049e6776391d"
SAGE_IMAGE = "sagemath/sagemath@" + SAGE_IMAGE_DIGEST
RSS_BYTES = 8 * 1024 ** 3
SAGE_BACKEND = "auto"
MODAL_PYTHON = None

GATES = {
    "G0-1": "v4 fixtures reproduce and panel_fixtures.py byte-reproduces independently",
    "G0-2": "f4 and f5 agree between Bareiss and subset-DP determinant reconstruction",
    "G0-3": "specialised f6 has 1,000 signed-sum and 1,000 non-sum checks per fixture",
    "G0-4": "G1 agrees with O5 on 200 smoke attempts per size, including L=8",
    "G0-5": "frozen power analysis reproduces committed rates within 3 MC standard errors",
    "G0-6": "independent checker exactly recomputes S,G,X,V units on 20 smoke queries",
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
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def free_gib(path: Path):
    return shutil.disk_usage(path).free / (1024 ** 3)


def machine_reading():
    system = Path("/")
    repo_volume = REPO
    try:
        nice_value = os.getpriority(os.PRIO_PROCESS, 0)
    except (AttributeError, OSError):
        nice_value = None
    rss_soft, rss_hard = resource.getrlimit(resource.RLIMIT_AS)
    return {
        "read_at": now(), "host": platform.node(), "platform": platform.platform(),
        "python": sys.version, "loadavg_15m": float(os.getloadavg()[2]),
        "load_limit": 14.0, "root_free_gib": round(free_gib(system), 6),
        "root_free_min_gib": 5.0, "repository_volume": str(repo_volume),
        "repository_free_gib": round(free_gib(repo_volume), 6),
        "repository_free_min_gib": 20.0, "rss_limit_gib": 8.0,
        "rlimit_as_soft_bytes": rss_soft, "rlimit_as_hard_bytes": rss_hard,
        "workers": 1, "nice_required": 10, "nice_actual": nice_value,
    }


def c7_ok(reading):
    nice_ok = reading["nice_actual"] is None or reading["nice_actual"] >= reading["nice_required"]
    return (reading["loadavg_15m"] <= reading["load_limit"]
            and reading["root_free_gib"] >= reading["root_free_min_gib"]
            and reading["repository_free_gib"] >= reading["repository_free_min_gib"]
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


def run_native(arguments, tmpdir, timeout):
    command = [sys.executable, *map(str, arguments)]
    started = now()
    try:
        process = subprocess.run(command, cwd=REPO, env=child_environment(tmpdir),
                                 capture_output=True, text=True, timeout=timeout,
                                 preexec_fn=child_limits)
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": process.returncode, "stdout": process.stdout,
                "stderr": process.stderr, "timeout": False}
    except subprocess.TimeoutExpired as error:
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": None, "stdout": error.stdout or "", "stderr": error.stderr or "",
                "timeout": True, "timeout_seconds": timeout}


def docker_base():
    return ["docker", "--host=unix:///var/run/docker.sock"]


def sage_command(script, *arguments):
    native = shutil.which("sage")
    if SAGE_BACKEND in ("auto", "native") and native:
        return [native, "-python", str(script), *map(str, arguments)], "native"
    if SAGE_BACKEND == "native":
        raise RuntimeError("explicit native Sage backend requested but sage is unavailable")
    if SAGE_BACKEND not in ("auto", "docker"):
        raise RuntimeError("sage_command called for unsupported backend %s" % SAGE_BACKEND)
    if shutil.which("docker") is None:
        raise RuntimeError("Docker Sage backend requested but docker is unavailable")
    relative_script = script.relative_to(REPO)
    mapped_arguments = []
    for argument in arguments:
        value = str(argument)
        candidate = Path(value)
        if candidate.is_absolute() or (not value.startswith("-") and (REPO / candidate).exists()):
            try:
                value = "/repo/" + str(candidate.resolve().relative_to(REPO))
            except (ValueError, OSError):
                pass
        mapped_arguments.append(value)
    command = docker_base() + ["run", "--rm", "--network=none", "--memory=8g",
        "--memory-swap=8g", "--cpus=1", "--pids-limit=512", "--read-only",
        "--user", "%d:%d" % (os.getuid(), os.getgid()),
        "--tmpfs", "/tmp:rw,size=2g", "-e", "OMP_NUM_THREADS=1",
        "-e", "OPENBLAS_NUM_THREADS=1", "-e", "MKL_NUM_THREADS=1", "-e", "HOME=/tmp",
        "-v", str(REPO) + ":/repo:ro", SAGE_IMAGE,
        "nice", "-n", "10", "sage", "-python", "/repo/" + str(relative_script),
        *mapped_arguments]
    return command, "docker"


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
                "adapter_stderr_base64": base64.b64encode(stderr).decode("ascii")}
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
                "adapter_stderr_base64": base64.b64encode(adapter_stderr).decode("ascii")}
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
    }


def run_sage(script, arguments, tmpdir, timeout):
    if SAGE_BACKEND == "modal":
        return run_modal_sage(script, arguments, tmpdir, timeout)
    try:
        command, backend = sage_command(script, *arguments)
    except RuntimeError as error:
        return {"command": [], "started_at": now(), "finished_at": now(),
                "returncode": None, "stdout_bytes": b"", "stderr_bytes": str(error).encode(),
                "timeout": False, "backend": SAGE_BACKEND}
    env = child_environment(tmpdir)
    if backend == "docker":
        for name in ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
            env.pop(name, None)
    started = now()
    try:
        process = subprocess.run(command, cwd=REPO, env=env, capture_output=True, timeout=timeout)
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": process.returncode, "stdout_bytes": process.stdout,
                "stderr_bytes": process.stderr, "timeout": False, "backend": backend,
                "image": SAGE_IMAGE if backend == "docker" else None}
    except subprocess.TimeoutExpired as error:
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": None, "stdout_bytes": error.stdout or b"",
                "stderr_bytes": error.stderr or b"", "timeout": True,
                "timeout_seconds": timeout, "backend": backend,
                "image": SAGE_IMAGE if backend == "docker" else None}
    except OSError as error:
        return {"command": command, "started_at": started, "finished_at": now(),
                "returncode": None, "stdout_bytes": b"", "stderr_bytes": str(error).encode(),
                "timeout": False, "backend": backend,
                "image": SAGE_IMAGE if backend == "docker" else None}


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


def write_json(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")


def gate_record(gate_id, passed=False, failed=False, blocked=False,
                classification="implementation_error", observation="", evidence=()):
    return {"id": gate_id, "description": GATES[gate_id], "pass": bool(passed),
            "fail": bool(failed), "blocked": bool(blocked), "classification": classification,
            "evidence_paths": [str(Path(path).relative_to(REPO)) for path in evidence],
            "observation": observation}


def parse_process_json(process, binary=False):
    if binary:
        return json.loads(process["stdout_bytes"].decode("utf-8"))
    return json.loads(process["stdout"])


def run_g01(tmpdir):
    generator = run_sage(PANEL_GENERATOR, [], tmpdir, 7200)
    verifier = run_sage(PANEL_VERIFIER, [], tmpdir, 7200)
    v4 = run_sage(V4_GENERATOR, [], tmpdir, 7200)
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
        "processes": {"generator": public_receipt(generator),
                      "independent_verifier": public_receipt(verifier),
                      "v4_reproducer": public_receipt(v4)}}
    write_json(evidence_path, evidence)
    if passed:
        return gate_record("G0-1", passed=True, classification="pass",
                           observation="v4 and 20-panel fixture byte streams reproduced exactly",
                           evidence=(evidence_path, PANEL_JSON))
    blocked = any(item["timeout"] or item["returncode"] != 0 for item in (generator, verifier, v4))
    return gate_record("G0-1", failed=not blocked, blocked=blocked,
                       classification="infrastructure_error" if blocked else "implementation_error",
                       observation="fixture byte reproduction did not complete or disagreed",
                       evidence=(evidence_path,))


def run_json_gate(gate_id, process, evidence_path):
    result = None
    try:
        result = parse_process_json(process, binary="stdout_bytes" in process)
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    write_json(evidence_path, {"schema": "crypto.autoresearch.icex_s0_gate_evidence.v1",
                               "gate": gate_id, "process": public_receipt(process),
                               "result": result})
    if process["timeout"]:
        return gate_record(gate_id, blocked=True, classification="resource_exhaustion",
                           observation="gate process watchdog expired", evidence=(evidence_path,))
    if result is None:
        return gate_record(gate_id, blocked=True, classification="infrastructure_error",
                           observation="gate emitted no parseable JSON receipt", evidence=(evidence_path,))
    if result.get("pass") is True and process["returncode"] == 0:
        return gate_record(gate_id, passed=True, classification="pass",
                           observation="frozen gate condition passed", evidence=(evidence_path,))
    return gate_record(gate_id, failed=not result.get("blocked", False),
                       blocked=result.get("blocked", False),
                       classification=result.get("classification", "implementation_error"),
                       observation=result.get("observation", "frozen gate condition did not pass"),
                       evidence=(evidence_path,))


def run_g02(tmpdir):
    process = run_sage(SAGE_GATES, ["--gate", "G0-2", "--v4", V4_JSON,
                                    "--panel", PANEL_JSON], tmpdir, 7200)
    return run_json_gate("G0-2", process, EVIDENCE / "g0-2-determinants.json")


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
    except json.JSONDecodeError:
        result = None
    if result is not None:
        result["producer_process"] = public_receipt(producer)
    write_json(producer_path, result or {"parse_error": True, "process": public_receipt(producer)})
    if producer["timeout"] or result is None or result.get("queries_completed") != 20:
        return gate_record("G0-6", blocked=True,
                           classification="resource_exhaustion" if producer["timeout"] else "infrastructure_error",
                           observation="20-query operation log was not completed", evidence=(producer_path,))
    checker = run_native([COUNTER_CHECKER, producer_path], tmpdir, 600)
    checker_path = EVIDENCE / "g0-6-independent-check.json"
    try:
        checked = parse_process_json(checker)
    except json.JSONDecodeError:
        checked = None
    write_json(checker_path, {"process": public_receipt(checker), "result": checked})
    if checked and checked.get("pass") and checker["returncode"] == 0:
        return gate_record("G0-6", passed=True, classification="pass",
                           observation="independent checker reproduced all four unit totals on 20 queries",
                           evidence=(producer_path, checker_path))
    return gate_record("G0-6", failed=True, classification="implementation_error",
                       observation="independent counter recomputation disagreed",
                       evidence=(producer_path, checker_path))


def run_g04(tmpdir):
    sizes = [(20, 8), (16, 5), (18, 6), (22, 10), (24, 13)]
    results, processes = [], []
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
        try:
            result = parse_process_json(process)
        except json.JSONDecodeError:
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
    if passed:
        return gate_record("G0-4", passed=True, classification="pass",
                           observation="all 1,000 smoke decisions agreed with O5",
                           evidence=(evidence_path,))
    blocking_class = next((row.get("classification") for row in results if row.get("blocked")),
                          "resource_exhaustion")
    return gate_record("G0-4", blocked=blocked, failed=not blocked,
                       classification=blocking_class if blocked else "implementation_error",
                       observation="G1/O5 smoke panel did not complete; see per-size receipt",
                       evidence=(evidence_path,))


def pending_gate(gate_id, observation, classification="infrastructure_error"):
    return gate_record(gate_id, blocked=True, classification=classification, observation=observation)


def write_reports(started, readings, gates, command, preflight, protocol_deviations):
    all_pass = all(gate["pass"] for gate in gates)
    any_started = any(gate["evidence_paths"] for gate in gates)
    status = "passed" if all_pass else ("completed_with_failures" if any_started else "not_started")
    report = {
        "schema": "crypto.autoresearch.exp_s0_gates.v1", "task_id": TASK,
        "experiment_id": EXP, "goal_id": "GOAL-ICEX-001", "owner": OWNER,
        "epoch": EPOCH, "smoke_namespace": SMOKE_NAMESPACE,
        "sage_backend": SAGE_BACKEND,
        "sage_image": SAGE_IMAGE if SAGE_BACKEND in ("docker", "modal") else None,
        "execution_scope": "S0 gates G0-1..G0-6 only; no frozen/protocol run",
        "started_at": started, "finished_at": now(), "command": command,
        "git": git_state(), "input_preflight": preflight,
        "machine_protection_readings": readings,
        "machine_protection_passed_at_launch": bool(readings and c7_ok(readings[0])),
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
    impl = {
        "schema": "crypto.autoresearch.implementation_report.v1", "task_id": TASK,
        "experiment_id": EXP, "implementation_commit": git_state()["commit"],
        "owner": OWNER, "epoch": EPOCH,
        "write_scope": ["experiments/EXP-ICEX-153c34/implementation/"],
        "files": files + [{"path": str((HERE / "implementation_report.yaml").relative_to(REPO)),
                            "sha256": "self; final content is bound by the Coordinator snapshot receipt"}],
        "commands": [command], "results": {"runner_status": status,
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
    parser.add_argument("--sage-backend", choices=("auto", "native", "docker", "modal"),
                        default=os.environ.get("ICEX_S0_SAGE_BACKEND", "auto"))
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
    readings = [machine_reading()]
    preflight = input_preflight()
    deviations = [{"kind": "development_probe", "classification": "procedure_deviation",
                   "observation": "Before the frozen runner, one non-protocol L=3 development query was started without the required nice/C-7 wrapper and manually terminated after 34 seconds; it emitted no result and is not gate evidence."}]
    deviations.append({"kind": "infrastructure_portability", "classification": "declared_deviation",
                       "observation": "The macOS-only /Volumes/SSD990/.tmp-agent path is absent on this cloud host; gate subprocesses use an auto-removed TMPDIR inside the task write scope on the same repository volume guarded by C-7."})
    if not c7_ok(readings[0]):
        gates = [pending_gate(gate_id, "not started because C-7 failed at launch") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations)
        return 3
    if not all(row["pass"] for row in preflight):
        gates = [pending_gate(gate_id, "not started because a frozen input hash mismatched",
                              "specification_error") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations)
        return 4
    if git_state()["status_porcelain"]:
        gates = [pending_gate(gate_id,
                              "not started because the immutable implementation worktree was dirty",
                              "execution_precondition") for gate_id in GATES]
        write_reports(started, readings, gates, command, preflight, deviations)
        return 5
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="s0-tmp-", dir=HERE) as temporary:
        tmpdir = Path(temporary)
        outcomes = {"G0-1": run_g01(tmpdir)}
        readings.append(machine_reading())
        if outcomes["G0-1"]["pass"] and c7_ok(readings[-1]):
            outcomes["G0-2"] = run_g02(tmpdir)
            readings.append(machine_reading())
            outcomes["G0-3"] = run_g03(tmpdir) if c7_ok(readings[-1]) else pending_gate("G0-3", "C-7 failed between stages")
        else:
            outcomes["G0-2"] = pending_gate("G0-2", "G0-1 dependency did not pass")
            outcomes["G0-3"] = pending_gate("G0-3", "G0-1 dependency did not pass")
        readings.append(machine_reading())
        outcomes["G0-5"] = run_g05(tmpdir) if c7_ok(readings[-1]) else pending_gate("G0-5", "C-7 failed between stages")
        readings.append(machine_reading())
        outcomes["G0-6"] = run_g06(tmpdir) if c7_ok(readings[-1]) else pending_gate("G0-6", "C-7 failed between stages")
        readings.append(machine_reading())
        outcomes["G0-4"] = run_g04(tmpdir) if c7_ok(readings[-1]) else pending_gate("G0-4", "C-7 failed between stages")
        gates = [outcomes[gate_id] for gate_id in GATES]
    write_reports(started, readings, gates, command, preflight, deviations)
    return 0 if all(gate["pass"] for gate in gates) else 2


if __name__ == "__main__":
    raise SystemExit(main())
