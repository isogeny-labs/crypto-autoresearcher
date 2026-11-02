#!/usr/bin/env python3
"""Compare frozen formal targets on one Git revision with hosted receipts.

This checks named source/target byte identity and receipt status. It does not
run Lean, authenticate downloaded receipts, or review theorem semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

import yaml


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_path(root: str, suffix: str) -> str:
    path = pathlib.PurePosixPath(root) / suffix
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe theorem path: {path}")
    return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, help="full Git commit SHA")
    parser.add_argument("--receipts", action="append", required=True,
                        metavar="RUN_ID:DIR", help="downloaded receipt artifact directory")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    revision = git("rev-parse", "--verify", args.revision + "^{commit}").decode().strip()
    if len(revision) != 40 or revision != args.revision:
        raise ValueError("--revision must be one full commit SHA")

    receipt_index: dict[str, list[tuple[str, pathlib.Path, dict]]] = {}
    run_pins = []
    for item in args.receipts:
        run_id, sep, directory = item.partition(":")
        if not sep or not run_id.isdecimal():
            raise ValueError("--receipts must have RUN_ID:DIR form")
        root = pathlib.Path(directory)
        before = (root / "dependency-pins-before.json").read_bytes()
        after = (root / "dependency-pins-after.json").read_bytes()
        if before != after:
            raise ValueError(f"dependency pins changed during run {run_id}")
        run_pins.append({"run_id": int(run_id), "before_sha256": sha256(before),
                         "after_sha256": sha256(after), "before_equals_after": before == after})
        for receipt_path in sorted(root.glob("*.json")):
            if receipt_path.name.startswith("dependency-pins-"):
                continue
            body = json.loads(receipt_path.read_bytes())
            if body.get("schema") != "crypto.autoresearch.formal_verification.v1":
                raise ValueError(f"unexpected receipt schema: {receipt_path}")
            claim_id = body["task"]["claim_id"]
            receipt_index.setdefault(claim_id, []).append((run_id, receipt_path, body))

    tree = git("ls-tree", "-r", "-z", revision, "formal/targets")
    target_paths = []
    for record in tree.split(b"\0"):
        if record:
            _, path = record.split(b"\t", 1)
            path_text = path.decode()
            if path_text.endswith(".yaml"):
                target_paths.append(path_text)

    rows = []
    seen_claims = set()
    for target_path in sorted(target_paths):
        target_bytes = git("show", f"{revision}:{target_path}")
        target = yaml.safe_load(target_bytes)
        claim_id = target["claim_id"]
        if claim_id in seen_claims:
            raise ValueError(f"duplicate claim id: {claim_id}")
        seen_claims.add(claim_id)
        theorem_path = checked_path(target["workspace"], target["theorem_file"])
        try:
            theorem_bytes = git("show", f"{revision}:{theorem_path}")
        except subprocess.CalledProcessError:
            theorem_bytes = None
        target_hash = sha256(target_bytes)
        theorem_hash = sha256(theorem_bytes) if theorem_bytes is not None else None
        matches = []
        for run_id, receipt_path, receipt in receipt_index.get(claim_id, []):
            task = receipt["task"]
            verification = receipt["verification"]
            provenance = receipt["provenance"]
            if (verification["status"] == "machine_verified"
                and verification["build_passed"] is True
                and verification["axiom_audit_passed"] is True
                and not verification["forbidden_constructs"]
                and not receipt["infrastructure_failure"]
                and bool(receipt["audit_log"])
                and task["task_id"] == target["task_id"]
                and verification["task_id"] == target["task_id"]
                and task["workspace"] == target["workspace"]
                and task["theorem_name"] == target["theorem_name"]
                and task["theorem_file"] == target["theorem_file"]
                and verification["theorem_name"] == target["theorem_name"]
                and verification["theorem_file"] == target["theorem_file"]
                and provenance["task_spec_sha256"] == target_hash
                and provenance["theorem_sha256"] == theorem_hash
                and provenance["workspace_inputs"].get(target["theorem_file"]) == theorem_hash):
                matches.append({"run_id": int(run_id), "file": receipt_path.name,
                                "sha256": sha256(receipt_path.read_bytes()),
                                "source_commit": provenance["source_commit"]})
        rows.append({"claim_id": claim_id, "target_path": target_path,
                     "theorem_name": target["theorem_name"],
                     "theorem_path": theorem_path,
                     "target_sha256": target_hash,
                     "theorem_sha256": theorem_hash,
                     "source_present": theorem_bytes is not None,
                     "matching_receipts": matches})

    missing = [row["claim_id"] for row in rows if not row["matching_receipts"]]
    output = {"schema": "formal-target-matching-receipts/v1",
              "revision": revision,
              "target_count": len(rows),
              "named_source_count": sum(row["source_present"] for row in rows),
              "matching_receipt_count": len(rows) - len(missing),
              "unmatched_claim_ids": missing,
              "run_pins": run_pins,
              "evidence_boundary": "Byte-matched named machine receipts only; no fresh Lean build, receipt authentication, semantic review, implementation bridge, or performance validation is inferred.",
              "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: output[key] for key in
                      ("revision", "target_count", "named_source_count",
                       "matching_receipt_count", "unmatched_claim_ids")}, sort_keys=True))
    if args.require_complete and missing:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        sys.exit(2)
