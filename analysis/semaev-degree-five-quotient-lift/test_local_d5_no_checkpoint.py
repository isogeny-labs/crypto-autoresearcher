#!/usr/bin/env python3
"""End-to-end small retained-seed control for the checkpoint-free local runner."""

import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).with_name("run_local_d5_no_checkpoint.py")
BUNDLE = Path("/home/ec2-user/fall-degree-runtime-20261029/blocked-checkpoint-worker-cloud-001/bundle")
EXPECTED_CERT = "7cf2d46d96fe00dfddd1277935c7f0b6577c7ab9cbdc774151c81f56fee82d73"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def main():
    request = json.loads((BUNDLE / "request-0.json").read_text())
    with tempfile.TemporaryDirectory(prefix="lfd-no-checkpoint-control-") as temporary:
        root = Path(temporary)
        seed = root / "seed.bin"
        seed.write_bytes(gzip.decompress((BUNDLE / "seed-0.gz").read_bytes()))
        assert digest(seed) == request["seed_sha256"]
        profile = root / "profile.json"
        write(profile, {"variables": 6, "seed_degree": 4,
                        "seed_sha256": digest(seed), "seed_codimension": 3,
                        "working_coordinates": 3, "next_degree_columns": 63,
                        "native_envelopes": {"31": {"envelope_bytes": 67785505}}})
        locks = [root / "lock1", root / "lock2"]
        for lock in locks:
            lock.touch()
        output = root / "run"
        plan = {
            "schema": "semaev.local-d5-no-checkpoint-plan/v1",
            "id": "no-checkpoint-fixture-0",
            "record": request["record"],
            "seed_path": str(seed), "seed_sha256": digest(seed),
            "seed_bytes": seed.stat().st_size,
            "profile_path": str(profile), "bundle_path": str(BUNDLE),
            "runner_sha256": digest(SCRIPT),
            "hashes": {str(path): digest(path) for path in (
                seed, profile, BUNDLE / "bin/quotient_lift_checkpoint",
                BUNDLE / "bin/count_by_sum", BUNDLE / "cert_check.py")},
            "memory_bytes": 1 << 30, "reserve_bytes": 0,
            "disk_capacity_bytes": 1 << 30, "disk_reserve_bytes": 1 << 20,
            "chunk_rows": 31, "expected_exact_solutions": 3,
            "check_timeout_seconds": 120, "count_timeout_seconds": 120,
            "produce_timeout_seconds": 120, "locks": [str(x) for x in locks],
            "output_root": str(output),
        }
        plan_path = root / "plan.json"
        write(plan_path, plan)
        protocol_path = root / "protocol.json"
        write(protocol_path, {"freeze": {"status": "frozen"},
                              "links": {"plan_sha256": digest(plan_path)}})
        env = dict(os.environ, SEMAEV_CHECKPOINT_DIR=str(root / "forbidden-checkpoints"))
        result = subprocess.run([sys.executable, str(SCRIPT), "--plan", str(plan_path),
                                 "--protocol", str(protocol_path)], env=env,
                                capture_output=True, text=True, timeout=180)
        assert result.returncode == 0, (result.stdout, result.stderr)
        actual = json.loads((output / "result.json").read_text())
        assert actual["status"] == "certificate_verified", actual
        assert actual["certified_codimension_lower_bound"] == 3, actual
        assert actual["exact_solutions"] == 3, actual
        assert actual["certificate_sha256"] == EXPECTED_CERT, actual
        assert actual["checkpoint_files"] == 0, actual
        assert not (root / "forbidden-checkpoints").exists()
        refused = root / "refused"
        plan["output_root"] = str(refused)
        plan["hashes"][str(seed)] = "0" * 64
        write(root / "bad-plan.json", plan)
        write(root / "bad-protocol.json", {"freeze": {"status": "frozen"},
                                          "links": {"plan_sha256": digest(root / "bad-plan.json")}})
        bad = subprocess.run([sys.executable, str(SCRIPT), "--plan", str(root / "bad-plan.json"),
                              "--protocol", str(root / "bad-protocol.json")],
                             capture_output=True, text=True, timeout=30)
        assert bad.returncode != 0 and not refused.exists(), (bad.stdout, bad.stderr)
        print(json.dumps({"status": "passed", "fixture_certificate_sha256": EXPECTED_CERT,
                          "accepted_codimension": 3, "exact_solutions": 3,
                          "checkpoint_files": 0, "bad_hash_refused": True}))


if __name__ == "__main__":
    main()
