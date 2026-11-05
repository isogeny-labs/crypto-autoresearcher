#!/usr/bin/env python3
"""Audit archived n47 random00 D4 rank evidence and its dimension bridge."""

import hashlib
import json
from math import comb
from pathlib import Path
import re
import struct
import sys


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent.parent
PLAN = STUDY / "rank-check/n47-rand00-plan-002.json"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def audit(seed=None):
    manifest = json.loads((HERE / "evidence-manifest.json").read_text())
    assert manifest["schema"] == "semaev.independent-d4-rank-archive/v1"
    assert sha(PLAN) == manifest["plan_sha256"]
    plan = json.loads(PLAN.read_text())
    for prefix in ("request", "runner", "verifier"):
        assert sha(Path(plan[prefix + "_path"])) == plan[prefix + "_sha256"], prefix
    for name, meta in manifest["files"].items():
        path = HERE / "evidence" / name
        assert path.stat().st_size == meta["bytes"] and sha(path) == meta["sha256"], name
    result = json.loads((HERE / "evidence/result.json").read_text())
    admission = json.loads((HERE / "evidence/admission.json").read_text())
    started = json.loads((HERE / "evidence/started.json").read_text())
    assert result["plan_sha256"] == admission["plan_sha256"] == sha(PLAN)
    assert result["returncode"] == 0 and not result["timed_out"]
    assert result["status"] == "rank_match"
    for name in ("stdout", "stderr"):
        assert sha(HERE / "evidence" / (name + ".txt")) == result[name + "_sha256"]
    assert sha(HERE / "evidence/check4.stdout.txt") == plan["accepted_checker_stdout_sha256"]
    check = (HERE / "evidence/check4.stdout.txt").read_text()
    assert "VALID: 1 is not in W_4(F), and codim W_4(F) >= 61196" in check
    assert started["argv"][2] == plan["verifier_path"]
    record = plan["record"]
    assert started["argv"][3:] == [str(record["n"]), record["modulus_hex"], *(str(record[k]) for k in ("a2",)), record["a6_hex"], record["z_hex"], "4", *record["V_basis_hex"]]
    assert started["memory_bytes"] == plan["memory_bytes"]
    assert admission["seed_sha256"] == plan["seed_sha256"]
    assert result["target_rank"] == plan["target_rank"]
    nvars = 2 * len(plan["record"]["V_basis_hex"])
    columns = sum(comb(nvars, d) for d in range(5))
    observed = result["observed"]
    assert (nvars, columns) == (48, 213053)
    assert observed == {"columns": columns, "contains_one": False,
                        "dims": [0, 1, 141, 6909, 151857], "rank": 151857}
    assert columns - plan["accepted_codimension"] == observed["rank"]
    stdout = (HERE / "evidence/stdout.txt").read_text()
    match = re.search(r"^W4 dims \[0, 1, 141, 6909, 151857\] contains_one 0 "
                      r"rank 151857 cols 213053 \[([0-9.]+)s\]$", stdout, re.M)
    assert match
    if seed is not None:
        seed = Path(seed)
        assert sha(seed) == plan["seed_sha256"] and seed.stat().st_size == plan["seed_bytes"]
        with seed.open("rb") as stream:
            assert struct.unpack("<4q", stream.read(32)) == (48, 4, 213053, 61196)
    return {"schema": "semaev.independent-d4-rank-audit/v1",
            "id": plan["id"], "status": "rank_equality_checked",
            "ambient_dimension": columns, "w4_rank": observed["rank"],
            "u4_kernel_dimension": columns - plan["accepted_codimension"],
            "u4_codimension": plan["accepted_codimension"],
            "contains_one": observed["contains_one"],
            "seed_bytes_rechecked": seed is not None,
            "replay_seconds_reported": float(match.group(1)),
            "scope": "Archived transcript, source-bound plan and dimension argument; this audit does not rerun the 12535-second independent closure."}


if __name__ == "__main__":
    result = audit(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2, sort_keys=True))
