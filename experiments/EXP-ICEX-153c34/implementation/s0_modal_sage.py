#!/usr/bin/env python3
"""Fail-closed Modal Sandbox transport for the ICEX S0 Sage verifiers.

The adapter is deliberately not a general remote command runner.  It accepts
one of four allowlisted Sage verifier scripts, validates a complete content
manifest, sends a small deterministic tar stream to a fresh Modal Sandbox, and
returns the verifier's exact stdout and stderr bytes in a hash-bound receipt.
No Modal function layer, persistent volume, repository checkout, or worker
network access is used.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import re
import sys
import tarfile
import time
from pathlib import Path

try:
    import modal
except ImportError:  # Pure validation and --self-test remain offline.
    modal = None


SCHEMA = "crypto.autoresearch.icex_s0_modal_request.v1"
RESPONSE_SCHEMA = "crypto.autoresearch.icex_s0_modal_response.v1"
APP_NAME = "icex-s0-sage-verifiers"
SAGE_IMAGE_DIGEST = "sha256:4562582e9da21605ce1507932effb548d44888ed9e35ec768616049e6776391d"
SAGE_IMAGE = "sagemath/sagemath@" + SAGE_IMAGE_DIGEST
RSS_BYTES = 8 * 1024**3
MAX_TIMEOUT_SECONDS = 7200
MAX_BUNDLE_BYTES = 16 * 1024 * 1024
ALLOWED_SCRIPT_SHA256 = {
    "panel_fixtures.py": "701e69f06f22d890a09473f2a7fac04f78d60d7021e346f28555a8fae377fab6",
    "panel_fixtures_verifier.py": "2cfbea9b5fbbf1501e27954e610e274cb72a214cc8657fb31dd7a903b02e459d",
    "ic_leads_fixtures_v2.py": "bde44afb3e14c34d97bf50c154456565d12f0b5a1d33d63b473f0f4124b1f3b2",
    "s0_sage_gates.py": "7a37e1353ed2a5458929c023ce84053eedd5630f094a80b8c21cfcb4a7a50fe6",
}
V4_SHA256 = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
SEMAEV_INVENTORY_SHA256 = "447d9bfff27f2b57b50e60fffde0c380ab697f4b2cbf006114bb7a50be10642e"
O5_GROUP_SHA256 = "8b33c1bd1e5faa92f6e7a65a62f48a0f3e49432b3a846be330ad7f56ae52c07b"
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")

# The outer shell consumes the deterministic tar from stdin, verifies every
# manifest hash silently, applies the address-space ceiling, and starts the
# verifier under nice=10.  The trusted inner shell emits one authenticated
# limits prefix which the adapter separates; the retained verifier stdout and
# stderr are otherwise the exact Sage process streams.
BUNDLE_WRAPPER = r"""
set -euo pipefail
umask 077
work=/tmp/icex-s0
rm -rf "$work"
mkdir -m 700 "$work"
tar -xf - -C "$work"
cd "$work"
sha256sum --check --strict --status SHA256SUMS
inner=$1
shift
script=$1
shift
ulimit -v 8388608
exec nice -n 10 bash -c "$inner" icex-sage "$script" "$@"
""".strip()

# This shell is already nice-adjusted and inherits the RLIMIT from the outer
# wrapper.  It emits and verifies the actual values before replacing itself
# with Sage; the adapter strips this prefix from the retained Sage stdout.
SAGE_WRAPPER = r"""
set -euo pipefail
actual_nice=$(awk '{print $19}' /proc/$$/stat)
soft_kib=$(ulimit -Sv)
hard_kib=$(ulimit -Hv)
printf 'ICEX_LIMITS_V1\t%s\t%s\t%s\n' "$actual_nice" "$soft_kib" "$hard_kib"
test "$actual_nice" -ge 10
test "$soft_kib" -eq 8388608
test "$hard_kib" -eq 8388608
exec sage -python "$@"
""".strip()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical_json(document) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_digest(request: dict) -> str:
    unsigned = dict(request)
    unsigned["request_sha256"] = ""
    return sha256_bytes(canonical_json(unsigned))


def decode_file(row: dict) -> bytes:
    if set(row) != {"name", "role", "sha256", "content_base64"}:
        raise ValueError("bundle file fields differ from the frozen adapter schema")
    name = row["name"]
    if not isinstance(name, str) or SAFE_NAME.fullmatch(name) is None:
        raise ValueError("unsafe bundle filename")
    if row["role"] not in ("script", "input"):
        raise ValueError("unknown bundle role")
    try:
        data = base64.b64decode(row["content_base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError("invalid base64 bundle content") from error
    if sha256_bytes(data) != row["sha256"]:
        raise ValueError("bundle content hash mismatch")
    return data


def validate_request(request: dict) -> list[tuple[dict, bytes]]:
    expected = {
        "schema", "request_sha256", "image", "image_digest", "script",
        "argv", "files", "timeout_seconds", "resources", "environment",
    }
    if not isinstance(request, dict) or set(request) != expected:
        raise ValueError("request fields differ from the frozen adapter schema")
    if request["schema"] != SCHEMA or request["request_sha256"] != request_digest(request):
        raise ValueError("request schema or hash mismatch")
    if request["image"] != SAGE_IMAGE or request["image_digest"] != SAGE_IMAGE_DIGEST:
        raise ValueError("unapproved Sage image")
    if request["script"] not in ALLOWED_SCRIPT_SHA256:
        raise ValueError("script is not an S0 Sage verifier")
    timeout = request["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not (1 <= timeout <= MAX_TIMEOUT_SECONDS):
        raise ValueError("invalid timeout")
    if request["resources"] != {
        "cpu": 1.0, "memory_mib": 8192, "max_containers": 1,
        "retries": 0, "nice": 10, "rlimit_as_bytes": RSS_BYTES,
        "network": "blocked", "single_use_container": True,
    }:
        raise ValueError("resource declaration mismatch")
    if request["environment"] != {
        "HOME": "/tmp", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "VECLIB_MAXIMUM_THREADS": "1",
    }:
        raise ValueError("environment declaration mismatch")
    argv = request["argv"]
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise ValueError("argv must be a string list")
    if any("\x00" in item or item.startswith("/") or ".." in Path(item).parts for item in argv):
        raise ValueError("unsafe argv token")
    files = request["files"]
    if not isinstance(files, list) or not (1 <= len(files) <= 6):
        raise ValueError("invalid file bundle cardinality")
    decoded = [(row, decode_file(row)) for row in files]
    if sum(len(data) for _, data in decoded) > MAX_BUNDLE_BYTES:
        raise ValueError("bundle exceeds the sixteen-MiB verifier bound")
    names = [row["name"] for row, _ in decoded]
    if len(names) != len(set(names)):
        raise ValueError("duplicate bundle filename")
    if any(name in {"SHA256SUMS", ".limits.json"} for name in names):
        raise ValueError("bundle uses a reserved control filename")
    scripts = [row["name"] for row, _ in decoded if row["role"] == "script"]
    if scripts != [request["script"]]:
        raise ValueError("bundle must contain exactly the selected script")
    by_name = {row["name"]: (row, data) for row, data in decoded}
    script_row, _ = by_name[request["script"]]
    if script_row["sha256"] != ALLOWED_SCRIPT_SHA256[request["script"]]:
        raise ValueError("Sage verifier script hash is not approved")
    input_names = {row["name"] for row, _ in decoded if row["role"] == "input"}
    for token in argv:
        if token.endswith((".json", ".yaml", ".py")) and token not in input_names:
            raise ValueError("argv references a file absent from the bundle")
    if request["script"] == "s0_sage_gates.py":
        expected_argv = ["--gate", "G0-2", "--v4", "ic_leads_fixtures_v2.json",
                         "--panel", "panel_fixtures.json",
                         "--inventory", "semaev_polys.json",
                         "--o5-group", "o5_group.py"]
        if argv != expected_argv or input_names != {
            "ic_leads_fixtures_v2.json", "panel_fixtures.json",
            "semaev_polys.json", "o5_group.py",
        }:
            raise ValueError("G0-2 invocation differs from the approved call shape")
        v4_row, _ = by_name["ic_leads_fixtures_v2.json"]
        if v4_row["sha256"] != V4_SHA256:
            raise ValueError("G0-2 v4 input hash mismatch")
        inventory_row, _ = by_name["semaev_polys.json"]
        if inventory_row["sha256"] != SEMAEV_INVENTORY_SHA256:
            raise ValueError("G0-2 polynomial inventory hash mismatch")
        o5_row, _ = by_name["o5_group.py"]
        if o5_row["sha256"] != O5_GROUP_SHA256:
            raise ValueError("G0-2 O5 group-arithmetic input hash mismatch")
    elif argv or input_names:
        raise ValueError("G0-1 verifier calls accept no arguments or input files")
    return decoded


def deterministic_tar(decoded: list[tuple[dict, bytes]]) -> bytes:
    stream = io.BytesIO()
    checksum_rows = []
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for row, data in decoded:
            info = tarfile.TarInfo(row["name"])
            info.size = len(data)
            info.mode = 0o500 if row["role"] == "script" else 0o400
            info.mtime = info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
            checksum_rows.append("%s  %s\n" % (row["sha256"], row["name"]))
        checksums = "".join(checksum_rows).encode("ascii")
        info = tarfile.TarInfo("SHA256SUMS")
        info.size = len(checksums)
        info.mode = 0o400
        info.mtime = info.uid = info.gid = 0
        info.uname = info.gname = ""
        archive.addfile(info, io.BytesIO(checksums))
    return stream.getvalue()


def read_process(process) -> tuple[bytes, bytes, int]:
    stdout = process.stdout.read()
    stderr = process.stderr.read()
    returncode = process.wait()
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        raise RuntimeError("Modal byte-stream contract was not honored")
    return stdout, stderr, returncode


def split_limit_prefix(transport_stdout: bytes) -> tuple[dict, bytes, str | None]:
    first, separator, remainder = transport_stdout.partition(b"\n")
    if not separator:
        return {}, transport_stdout, "resource-limit prefix is absent"
    fields = first.split(b"\t")
    if len(fields) != 4 or fields[0] != b"ICEX_LIMITS_V1":
        return {}, transport_stdout, "resource-limit prefix is malformed"
    try:
        limits = {
            "nice_actual": int(fields[1]),
            "rlimit_as_soft_kib": int(fields[2]),
            "rlimit_as_hard_kib": int(fields[3]),
        }
    except ValueError:
        return {}, transport_stdout, "resource-limit prefix is nonnumeric"
    return limits, remainder, None


def run_remote(request: dict) -> dict:
    decoded = validate_request(request)
    if modal is None:
        raise RuntimeError("Modal SDK is unavailable in the selected adapter Python")
    archive = deterministic_tar(decoded)
    environment = {**request["environment"], "TMPDIR": "/tmp"}
    adapter_started_at = now()
    adapter_started = time.monotonic()
    app = modal.App(APP_NAME)
    image = modal.Image.from_registry(SAGE_IMAGE)
    sandbox = None
    with app.run():
        sandbox = modal.Sandbox.create(
            "sleep", "infinity", app=app, image=image,
            env=environment, timeout=request["timeout_seconds"] + 120,
            cpu=(1.0, 1.0), memory=(8192, 8192), block_network=True,
            name="icex-s0-" + request["request_sha256"][:24],
            tags={"experiment": "EXP-ICEX-153c34",
                  "request_sha256": request["request_sha256"]},
        )
        image_object_id = getattr(image, "object_id", None)
        sandbox_id = getattr(sandbox, "object_id", None)
        termination_error = None
        try:
            process_started_at = now()
            process_started = time.monotonic()
            process = sandbox.exec(
                "bash", "-c", BUNDLE_WRAPPER, "icex-bundle", SAGE_WRAPPER,
                request["script"], *request["argv"],
                timeout=request["timeout_seconds"], text=False,
            )
            process.stdin.write(archive)
            process.stdin.drain()
            process.stdin.write_eof()
            transport_stdout, stderr, returncode = read_process(process)
            process_finished_at = now()
            process_elapsed = round(time.monotonic() - process_started, 6)
            limits, stdout, limits_error = split_limit_prefix(transport_stdout)
        finally:
            try:
                sandbox.terminate(wait=True)
            except BaseException as error:
                termination_error = "%s: %s" % (type(error).__name__, error)
    try:
        nice_actual = int(limits["nice_actual"])
        soft_bytes = int(limits["rlimit_as_soft_kib"]) * 1024
        hard_bytes = int(limits["rlimit_as_hard_kib"]) * 1024
        limits_verified = (nice_actual >= 10 and soft_bytes == RSS_BYTES
                           and hard_bytes == RSS_BYTES)
    except (KeyError, TypeError, ValueError):
        nice_actual = soft_bytes = hard_bytes = None
        limits_verified = False
    if not limits_verified and limits_error is None:
        limits_error = "remote resource-limit receipt disagrees with the contract"
    receipt_valid = (limits_verified and termination_error is None
                     and isinstance(image_object_id, str)
                     and image_object_id.startswith("im-")
                     and isinstance(sandbox_id, str) and sandbox_id.startswith("sb-"))
    return {
        "schema": RESPONSE_SCHEMA,
        "receipt_valid": receipt_valid,
        "request_sha256": request["request_sha256"],
        "image": SAGE_IMAGE,
        "image_digest": SAGE_IMAGE_DIGEST,
        "modal_image_object_id": image_object_id,
        "modal_sandbox_id": sandbox_id,
        "modal_sdk_version": getattr(modal, "__version__", None),
        "adapter_started_at": adapter_started_at,
        "adapter_finished_at": now(),
        "adapter_elapsed_seconds": round(time.monotonic() - adapter_started, 6),
        "adapter_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "resources": request["resources"],
        "input_manifest": [
            {"name": row["name"], "role": row["role"], "sha256": row["sha256"],
             "bytes": len(data)}
            for row, data in decoded
        ],
        "worker": {
            "execution": "fresh Modal Sandbox; terminated after one verifier",
            "provider_cpu_request_limit": [1.0, 1.0],
            "provider_memory_request_limit_mib": [8192, 8192],
            "sandbox_timeout_seconds": request["timeout_seconds"] + 120,
            "network": "blocked",
            "resource_limits_verified": limits_verified,
            "resource_limit_error": limits_error,
            "termination_error": termination_error,
            "nice_actual": nice_actual,
            "rlimit_as_soft_bytes": soft_bytes,
            "rlimit_as_hard_bytes": hard_bytes,
        },
        "process": {
            "command": ["nice", "-n", "10", "sage", "-python",
                        request["script"], *request["argv"]],
            "started_at": process_started_at,
            "finished_at": process_finished_at,
            "elapsed_seconds": process_elapsed,
            "returncode": returncode,
            "timeout": returncode == -1,
            "timeout_seconds": request["timeout_seconds"],
            "stdout_base64": base64.b64encode(stdout).decode("ascii"),
            "stdout_sha256": sha256_bytes(stdout),
            "transport_stdout_base64": base64.b64encode(transport_stdout).decode("ascii"),
            "transport_stdout_sha256": sha256_bytes(transport_stdout),
            "stderr_base64": base64.b64encode(stderr).decode("ascii"),
            "stderr_sha256": sha256_bytes(stderr),
            "peak_rss_bytes": None,
        },
    }


def emit(document: dict) -> None:
    sys.stdout.write(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n")


def self_test() -> None:
    script = Path(__file__).with_name("panel_fixtures.py").read_bytes()
    if sha256_bytes(script) != ALLOWED_SCRIPT_SHA256["panel_fixtures.py"]:
        raise AssertionError("allowlisted panel generator hash is stale")
    request = {
        "schema": SCHEMA,
        "request_sha256": "",
        "image": SAGE_IMAGE,
        "image_digest": SAGE_IMAGE_DIGEST,
        "script": "panel_fixtures.py",
        "argv": [],
        "files": [{
            "name": "panel_fixtures.py", "role": "script",
            "sha256": sha256_bytes(script),
            "content_base64": base64.b64encode(script).decode("ascii"),
        }],
        "timeout_seconds": 1,
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
    request["request_sha256"] = request_digest(request)
    decoded = validate_request(request)
    first = deterministic_tar(decoded)
    second = deterministic_tar(decoded)
    if first != second or b"panel_fixtures.py" not in first:
        raise AssertionError("deterministic bundle construction failed")
    limits, verifier_stdout, error = split_limit_prefix(
        b"ICEX_LIMITS_V1\t10\t8388608\t8388608\nexact verifier bytes\n")
    if error or limits["nice_actual"] != 10 or verifier_stdout != b"exact verifier bytes\n":
        raise AssertionError("resource-prefix separation failed")
    tampered = json.loads(json.dumps(request))
    tampered["timeout_seconds"] = 2
    try:
        validate_request(tampered)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered request was accepted")
    emit({"pass": True, "mode": "offline", "bundle_bytes": len(first),
          "bundle_sha256": sha256_bytes(first),
          "request_sha256": request["request_sha256"]})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        if args.request is not None:
            parser.error("--self-test and --request are mutually exclusive")
        self_test()
        return 0
    if args.request is None:
        parser.error("--request is required")
    try:
        request = json.loads(args.request.read_text())
        emit(run_remote(request))
        return 0
    except BaseException as error:
        emit({
            "schema": RESPONSE_SCHEMA,
            "adapter_error": type(error).__name__,
            "message": str(error),
            "request_path": str(args.request),
        })
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
