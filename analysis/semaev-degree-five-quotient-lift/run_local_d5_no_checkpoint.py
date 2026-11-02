#!/usr/bin/env python3
"""Run one pinned local D5 lift without checkpoint publication or retries."""

import argparse
import fcntl
import hashlib
import json
from math import comb
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def available_bytes():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise ValueError("MemAvailable unavailable")


def checked_codimension(stdout, degree):
    match = re.search(r"VALID: 1 is not in W_" + str(degree)
                      + r"\(F\), and codim W_" + str(degree)
                      + r"\(F\) >= (\d+)", stdout)
    if not match:
        raise ValueError("independent checker did not accept degree " + str(degree))
    return int(match.group(1))


def run_stage(root, label, argv, cap, timeout, env):
    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    argv = [str(x) for x in argv]
    with (root / (label + ".stdout.txt")).open("xb") as stdout, \
         (root / (label + ".stderr.txt")).open("xb") as stderr:
        child = subprocess.Popen(argv, stdout=stdout, stderr=stderr, env=env,
                                 start_new_session=True, preexec_fn=limit)
        save(root / (label + ".started.json"),
             {"argv": argv, "pid": child.pid, "memory_bytes": cap,
              "started_unix": time.time()})
        expired = False
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            expired = True
            os.killpg(child.pid, signal.SIGTERM)
            try:
                code = child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
    result = {"returncode": code, "timed_out": expired,
              "stdout_sha256": sha(root / (label + ".stdout.txt")),
              "stderr_sha256": sha(root / (label + ".stderr.txt"))}
    save(root / (label + ".finished.json"), result)
    if code != 0 or expired:
        raise RuntimeError(label + " failed or timed out")
    return (root / (label + ".stdout.txt")).read_text()


def run(plan_path, protocol_path):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    if plan["schema"] != "semaev.local-d5-no-checkpoint-plan/v1":
        raise ValueError("wrong plan schema")
    if protocol["freeze"]["status"] != "frozen" or \
       protocol["links"]["plan_sha256"] != sha(plan_path):
        raise ValueError("plan is not frozen")
    if sha(__file__) != plan["runner_sha256"]:
        raise ValueError("runner source hash mismatch")
    for name, expected in plan["hashes"].items():
        if sha(name) != expected:
            raise ValueError("pinned input changed: " + name)
    record = plan["record"]
    nvars = 2 * len(record["V_basis_hex"])
    profile = json.loads(Path(plan["profile_path"]).read_text())
    if (nvars != profile["variables"] or profile["seed_degree"] != 4 or
        profile["seed_sha256"] != plan["seed_sha256"] or
        profile["native_envelopes"][str(plan["chunk_rows"])]["envelope_bytes"] > plan["memory_bytes"]):
        raise ValueError("profile or native memory cap mismatch")
    if plan["seed_bytes"] != 32 + 8 * sum(comb(nvars, d) for d in range(5)) \
       * (1 + (profile["seed_codimension"] + 63) // 64):
        raise ValueError("seed dimensions mismatch")
    if plan["seed_sha256"] != plan["hashes"][plan["seed_path"]]:
        raise ValueError("seed hash is not pinned")
    maximum_certificate = 32 + 8 * profile["next_degree_columns"] \
        * (1 + (profile["working_coordinates"] + 63) // 64)
    if maximum_certificate > plan["disk_capacity_bytes"]:
        raise ValueError("disk capacity below certificate ceiling")

    locks = []
    try:
        for name in plan["locks"]:
            handle = Path(name).open("r+")
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                handle.close()
                raise RuntimeError("frontier lock busy: " + name)
            locks.append(handle)
        available = available_bytes()
        if available < plan["memory_bytes"] + plan["reserve_bytes"]:
            raise RuntimeError("memory admission refused")
        root = Path(plan["output_root"])
        if root.exists():
            raise FileExistsError("output root already exists")
        free = shutil.disk_usage(root.parent).free
        if free < maximum_certificate + plan["disk_reserve_bytes"]:
            raise RuntimeError("filesystem disk admission refused")
        root.mkdir(mode=0o700)
        save(root / "admission.json",
             {"plan_sha256": sha(plan_path), "protocol_sha256": sha(protocol_path),
              "mem_available_bytes": available, "disk_free_bytes": free,
              "maximum_certificate_bytes": maximum_certificate,
              "checkpoint_policy": "none", "time_unix": time.time()})
        result = {"schema": "semaev.local-d5-no-checkpoint-result/v1",
                  "status": "started", "id": plan["id"], "exact_solutions": None,
                  "certified_codimension_lower_bound": None}
        bundle = Path(plan["bundle_path"])
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("SEMAEV_CHECKPOINT_")}
        env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                   LD_LIBRARY_PATH=str(bundle / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", ""))
        r = record
        check_args = [sys.executable, bundle / "cert_check.py", plan["seed_path"],
                      r["n"], r["modulus_hex"], r["a2"], r["a6_hex"], r["z_hex"],
                      *r["V_basis_hex"]]
        try:
            d4 = checked_codimension(run_stage(root, "check4", check_args,
                plan["memory_bytes"], plan["check_timeout_seconds"], env), 4)
            if d4 != profile["seed_codimension"]:
                raise ValueError("D4 codimension differs from frozen seed")
            count_args = [bundle / "bin/count_by_sum", r["n"], r["modulus_hex"],
                          r["z_hex"], r["a6_hex"], len(r["V_basis_hex"]),
                          *r["V_basis_hex"]]
            count = int(run_stage(root, "count", count_args, 1 << 30,
                                  plan["count_timeout_seconds"], env).strip())
            if count != plan["expected_exact_solutions"]:
                raise ValueError("fresh exact count differs from frozen value")
            result["exact_solutions"] = count
            cert = root / "degree5.bin"
            output = run_stage(root, "produce5",
                [bundle / "bin/quotient_lift_checkpoint", plan["seed_path"],
                 cert, plan["chunk_rows"], plan["memory_bytes"]],
                plan["memory_bytes"], plan["produce_timeout_seconds"], env)
            produced = json.loads(output.strip())
            if produced["status"] == "projection_kills_one":
                if cert.exists():
                    raise ValueError("unexpected certificate after killed constant")
                result["status"] = "projection_kills_one"
            elif produced["status"] == "candidate_certificate":
                if not cert.exists():
                    raise ValueError("producer declared missing certificate")
                d5 = checked_codimension(run_stage(root, "check5",
                    [sys.executable, bundle / "cert_check.py", cert, r["n"],
                     r["modulus_hex"], r["a2"], r["a6_hex"], r["z_hex"],
                     *r["V_basis_hex"]], plan["memory_bytes"],
                    plan["check_timeout_seconds"], env), 5)
                result.update(status="certificate_verified",
                              certified_codimension_lower_bound=d5,
                              certificate_sha256=sha(cert),
                              certificate_bytes=cert.stat().st_size)
                if d5 > count:
                    result["last_fall_degree_lower_bound"] = 6
            else:
                raise ValueError("unrecognized producer status")
        except Exception as error:
            result.update(status="failed", error=str(error))
        result["checkpoint_files"] = len(list(root.glob("checkpoint-*.bin")))
        save(root / "result.json", result)
        return 0 if result["status"] != "failed" else 1
    finally:
        for handle in reversed(locks):
            fcntl.flock(handle, fcntl.LOCK_UN)
            handle.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(run(args.plan, args.protocol))
