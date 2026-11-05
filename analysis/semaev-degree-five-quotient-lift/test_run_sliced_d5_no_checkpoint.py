#!/usr/bin/env python3
"""Small end-to-end control for the sliced, checkpoint-free D5 runner."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
RUNNER = ROOT / "run_sliced_d5_no_checkpoint.py"
CHECKER = ROOT / "check_trace_slice_certificate.py"
PROJECTOR = ROOT / "slice_trace_certificate.py"
PROFILE = ROOT / "capacity_profile.py"
DESCENT = ROOT.parent / "semaev-m2-last-fall-degree/verify/cert_check.py"
BUNDLE = Path("/home/ec2-user/fall-degree-runtime-20261029/blocked-checkpoint-worker-cloud-001/bundle")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True) + "\n")


def tracked_bytes(relative):
    path = REPO / relative
    if path.exists():
        return path.read_bytes()
    return subprocess.check_output(["git", "show", "HEAD:" + relative], cwd=REPO)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    fixture = "analysis/semaev-degree-five-quotient-lift/validation/panel-worker-v2-20261029/odd-a2-0"
    with tempfile.TemporaryDirectory(prefix="lfd-sliced-d5-control-") as temporary:
        root = Path(temporary)
        original = root / "original.bin"
        original.write_bytes(tracked_bytes(fixture + "/result/certificate.bin"))
        record = json.loads(tracked_bytes(fixture + "/instance.json"))[0]
        sliced = root / "sliced.bin"
        module("slice_project", PROJECTOR).project(original, sliced, 3, digest(original))
        seed_sha = digest(sliced)
        original_plan = root / "original-plan.json"
        save(original_plan, {"record": record})
        check_argv = [sys.executable, str(CHECKER), str(sliced), "--plan", str(original_plan),
                      "--expect-plan-sha256", digest(original_plan),
                      "--expect-descent-source-sha256", digest(DESCENT),
                      "--variable", "3", "--expect-certificate-sha256", seed_sha]
        check = subprocess.run(check_argv, capture_output=True, text=True, timeout=120)
        assert check.returncode == 0, check.stderr
        check_stdout = root / "check.stdout.txt"
        check_stdout.write_text(check.stdout)
        check_receipt = root / "check.result.json"
        save(check_receipt, {"status": "exit", "exit_code": 0,
                             "stdout_sha256": digest(check_stdout)})

        capacity = module("capacity_profile", PROFILE).profile(sliced, seed_sha)
        stride = ((capacity["working_coordinates"] + 63) // 64 + 2) * 8
        seedstride = ((capacity["seed_codimension"] + 63) // 64 + 2) * 8
        chunk = 31
        columns = capacity["next_degree_columns"]
        old = capacity["seed_columns"]
        nq = capacity["seed_codimension"]
        work = capacity["working_coordinates"]
        payload = ((columns + 4096) * stride + old * seedstride
                   + (3 * work + 4 * chunk + nq) * stride
                   + (nq + chunk) * seedstride + columns * 40)
        capacity["native_envelopes"] = {str(chunk): {
            "envelope_bytes": payload * 135 // 100 + (64 << 20)}}
        profile = root / "profile.json"
        save(profile, capacity)
        locks = [root / "lock1", root / "lock2"]
        for lock in locks:
            lock.touch()
        output = root / "run"
        plan = {
            "schema": "semaev.sliced-d5-no-checkpoint-plan/v1",
            "id": "sliced-control-odd-a2-0", "record": record,
            "seed_path": str(sliced), "seed_sha256": seed_sha,
            "seed_bytes": sliced.stat().st_size,
            "slice_variable": 3, "affine_combination_mask": None,
            "original_plan_sha256": digest(original_plan),
            "descent_source_sha256": digest(DESCENT),
            "seed_check_result_path": str(check_receipt),
            "seed_check_stdout_path": str(check_stdout),
            "profile_path": str(profile), "bundle_path": str(BUNDLE),
            "runner_sha256": digest(RUNNER),
            "hashes": {str(path): digest(path) for path in (
                sliced, check_receipt, check_stdout, profile,
                BUNDLE / "bin/quotient_lift_checkpoint", BUNDLE / "bin/count_by_sum")},
            "memory_bytes": 1 << 30, "reserve_bytes": 0,
            "disk_capacity_bytes": 1 << 30, "disk_reserve_bytes": 1 << 20,
            "chunk_rows": chunk, "expected_exact_solutions": 1,
            "count_timeout_seconds": 120, "produce_timeout_seconds": 120,
            "latest_deadline_utc": (datetime.datetime.now(datetime.timezone.utc)
                                    + datetime.timedelta(minutes=5)).isoformat(),
            "locks": [str(path) for path in locks], "output_root": str(output),
        }
        plan_path = root / "plan.json"
        save(plan_path, plan)
        protocol = root / "protocol.json"
        save(protocol, {"freeze": {"status": "frozen"},
                        "links": {"plan_sha256": digest(plan_path)}})
        env = dict(os.environ, SEMAEV_CHECKPOINT_DIR=str(root / "forbidden-checkpoints"))
        run = subprocess.run([sys.executable, str(RUNNER), "--plan", str(plan_path),
                              "--protocol", str(protocol)], env=env,
                             capture_output=True, text=True, timeout=180)
        assert run.returncode == 0, (run.stdout, run.stderr)
        result = json.loads((output / "result.json").read_text())
        assert result["status"] in ("candidate_unchecked", "projection_kills_one"), result
        assert result["exact_solutions"] == 1 and result["last_fall_degree_lower_bound"] is None
        assert result["checkpoint_files"] == 0
        assert not (root / "forbidden-checkpoints").exists()
        bad_output = root / "bad-output"
        plan["output_root"] = str(bad_output)
        plan["hashes"][str(sliced)] = "0" * 64
        bad_plan = root / "bad-plan.json"
        save(bad_plan, plan)
        bad_protocol = root / "bad-protocol.json"
        save(bad_protocol, {"freeze": {"status": "frozen"},
                            "links": {"plan_sha256": digest(bad_plan)}})
        bad = subprocess.run([sys.executable, str(RUNNER), "--plan", str(bad_plan),
                              "--protocol", str(bad_protocol)],
                             capture_output=True, text=True, timeout=30)
        assert bad.returncode != 0 and not bad_output.exists(), (bad.stdout, bad.stderr)
        print(json.dumps({"status": "passed", "fixture": record["name"],
                          "runner_status": result["status"],
                          "exact_solutions": result["exact_solutions"],
                          "checkpoint_files": result["checkpoint_files"],
                          "bad_hash_refused": True}))


if __name__ == "__main__":
    main()
