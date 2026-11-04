#!/usr/bin/env python3
"""One bounded, source-pinned independent W4 rank replay; no automatic retry."""

import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import struct
import subprocess
import sys
import time


FINAL = re.compile(r"^W4 dims (\[[0-9, ]+\]) contains_one ([01]) rank (\d+) cols (\d+) ")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def parse_final(stdout, expected_columns):
    lines = [FINAL.match(line) for line in stdout.splitlines()]
    records = [m for m in lines if m]
    if len(records) != 1:
        raise ValueError("expected exactly one completed W4 rank line")
    match = records[0]
    dims = json.loads(match.group(1))
    one, rank, columns = map(int, match.groups()[1:])
    if columns != expected_columns or dims[-1] != rank:
        raise ValueError("independent closure dimensions disagree with plan")
    return {"dims": dims, "contains_one": bool(one), "rank": rank, "columns": columns}


def available_bytes():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise ValueError("MemAvailable unavailable")


def run(plan_path, protocol_path):
    plan = json.loads(plan_path.read_text())
    if plan["schema"] != "semaev.independent-d4-rank-plan/v1":
        raise ValueError("wrong rank plan schema")
    plan_sha = digest(plan_path)
    protocol = json.loads(protocol_path.read_text())
    if (protocol["freeze"]["status"] != "frozen" or
            plan_sha not in protocol["links"]["request_sha256s"]):
        raise ValueError("plan is not bound to a frozen protocol")
    request_path = Path(plan["request_path"])
    source = Path(plan["verifier_path"])
    seed = Path(plan["seed_path"])
    accepted_check = Path(plan["accepted_checker_stdout_path"])
    if digest(Path(__file__)) != plan["runner_sha256"]:
        raise ValueError("runner source hash mismatch")
    for path, expected in ((request_path, plan["request_sha256"]),
                           (source, plan["verifier_sha256"])):
        if expected != digest(path):
            raise ValueError("source or plan hash mismatch: " + str(path))
    request = json.loads(request_path.read_text())
    rec = request["record"]
    if rec != plan["record"] or request["seed_sha256"] != plan["seed_sha256"]:
        raise ValueError("instance or seed identity mismatch")
    nvars = 2 * len(rec["V_basis_hex"])
    columns = sum(math.comb(nvars, i) for i in range(5))
    if (columns != plan["expected_columns"] or
            columns - request["seed_codimension"] != plan["target_rank"]):
        raise ValueError("target rank arithmetic mismatch")

    locks = []
    try:
        for name in plan["locks"]:
            stream = open(name, "r+")
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError("campaign lock busy: " + name)
            locks.append(stream)
        if Path(plan["output_root"]).exists():
            raise FileExistsError("rank attempt already has an output root")
        required = plan["memory_bytes"] + plan["reserve_bytes"]
        samples = []
        deadline = time.monotonic() + plan["admission_wait_seconds"]
        while True:
            free = available_bytes()
            samples.append({"mem_available_bytes": free, "unix_time": time.time()})
            if free >= required:
                break
            if time.monotonic() >= deadline:
                raise RuntimeError("memory admission refused")
            time.sleep(min(plan["admission_poll_seconds"], max(0, deadline-time.monotonic())))

        if digest(seed) != plan["seed_sha256"] or seed.stat().st_size != plan["seed_bytes"]:
            raise ValueError("local D4 seed differs from accepted input")
        if digest(accepted_check) != plan["accepted_checker_stdout_sha256"]:
            raise ValueError("accepted checker transcript differs from plan")
        if (f"VALID: 1 is not in W_4(F), and codim W_4(F) >= {request['seed_codimension']}"
                not in accepted_check.read_text()):
            raise ValueError("accepted checker transcript lacks required D4 conclusion")
        with seed.open("rb") as stream:
            header = struct.unpack("<4q", stream.read(32))
        if header != (nvars, 4, columns, request["seed_codimension"]):
            raise ValueError("D4 certificate header differs from plan")
        if digest(source) != plan["verifier_sha256"] or digest(request_path) != plan["request_sha256"]:
            raise ValueError("input changed during admission")

        out = Path(plan["output_root"])
        out.mkdir(parents=True, exist_ok=False)
        save(out / "admission.json", {"plan_sha256": plan_sha,
                                      "samples": samples, "required_bytes": required,
                                      "seed_sha256": plan["seed_sha256"]})
        argv = [sys.executable, "-u", str(source), str(rec["n"]), rec["modulus_hex"],
                str(rec["a2"]), rec["a6_hex"], rec["z_hex"], "4", *rec["V_basis_hex"]]
        env = {key: value for key, value in os.environ.items()
               if key not in ("FIX", "NOCLOSURE", "COUNT_SHARD")}
        env.update(NOCOUNT="1", PYTHONUNBUFFERED="1", PYTHONHASHSEED="0")
        def cap():
            resource.setrlimit(resource.RLIMIT_AS, (plan["memory_bytes"], plan["memory_bytes"]))
        with (out / "stdout.txt").open("xb") as stdout, (out / "stderr.txt").open("xb") as stderr:
            child = subprocess.Popen(argv, stdout=stdout, stderr=stderr, env=env,
                                     start_new_session=True, preexec_fn=cap)
            save(out / "started.json", {"argv": argv, "pid": child.pid,
                                        "started_unix": time.time(), "memory_bytes": plan["memory_bytes"]})
            timed_out = False
            try:
                code = child.wait(timeout=plan["timeout_seconds"])
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    code = child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
        output = (out / "stdout.txt").read_text()
        result = {"schema": "semaev.independent-d4-rank-result/v1",
                  "plan_sha256": plan_sha, "returncode": code,
                  "timed_out": timed_out, "stdout_sha256": digest(out / "stdout.txt"),
                  "stderr_sha256": digest(out / "stderr.txt"),
                  "target_rank": plan["target_rank"], "status": "incomplete"}
        if code == 0 and not timed_out:
            observed = parse_final(output, columns)
            result["observed"] = observed
            result["status"] = ("rank_match" if observed["rank"] == plan["target_rank"]
                                and not observed["contains_one"] else "rank_mismatch")
        save(out / "result.json", result)
        return 0 if result["status"] == "rank_match" else 1
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--protocol", required=True, type=Path)
    args = parser.parse_args()
    sys.exit(run(args.plan, args.protocol))
