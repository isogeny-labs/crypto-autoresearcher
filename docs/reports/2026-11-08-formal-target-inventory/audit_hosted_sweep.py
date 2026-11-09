#!/usr/bin/env python3
"""Audit a downloaded hosted Lean receipt artifact against pinned Git objects."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--receipts", type=Path, required=True)
    ap.add_argument("--checkout", required=True)
    ap.add_argument("--current", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    inventory = json.loads(args.inventory.read_text())
    errors: list[str] = []
    cached: dict[tuple[str, str], bytes] = {}

    def blob(commit: str, path: str) -> bytes:
        key = (commit, path)
        if key not in cached:
            cached[key] = git(args.repo, "show", f"{commit}:{path}")
        return cached[key]

    files = {p.name: p for p in args.receipts.glob("*.json")}
    expected = {Path(row["spec"]).stem + ".json" for row in inventory["targets"]}
    if set(files) != expected | {"dependency-pins-before.json", "dependency-pins-after.json"}:
        errors.append("receipt file set differs from target inventory plus two pin receipts")

    workspaces: dict[str, dict] = {}
    verifier_inputs: dict | None = None
    states: dict[str, int] = {}
    semantic: dict[str, int] = {}
    for row in inventory["targets"]:
        name = Path(row["spec"]).stem + ".json"
        if name not in files:
            continue
        receipt = json.loads(files[name].read_text())
        task, proof, prov = (receipt[k] for k in ("task", "verification", "provenance"))
        workspace = task["workspace"].rstrip("/")
        checks = {
            "schema": receipt["schema"] == "crypto.autoresearch.formal_verification.v1",
            "checkout": prov["source_commit"] == args.checkout,
            "task": task["task_id"] == row["task_id"] == proof["task_id"],
            "claim": task["claim_id"] == row["claim_id"],
            "theorem": task["theorem_name"] == row["theorem_name"] == proof["theorem_name"],
            "file": workspace + "/" + task["theorem_file"] == row["theorem_file"]
            and task["theorem_file"] == proof["theorem_file"],
            "spec_hash": prov["task_spec_sha256"] == row["spec_sha256"]
            == sha(blob(args.checkout, row["spec"])),
            "source_hash": prov["declared_source_sha256"] == row["source_sha256"]
            == sha(blob(args.checkout, row["source"])) == sha(blob(args.current, row["source"])),
            "theorem_hash": prov["theorem_sha256"] == row["theorem_sha256"]
            == sha(blob(args.checkout, row["theorem_file"]))
            == sha(blob(args.current, row["theorem_file"])),
            "proof": proof["status"] == "machine_verified" and proof["build_passed"] is True
            and proof["axiom_audit_passed"] is True and proof["forbidden_constructs"] == [],
            "semantic": receipt["semantic_review"] == {"required": True, "status": "pending"},
        }
        for key, passed in checks.items():
            if not passed:
                errors.append(f"{name}: {key}")
        states[proof["status"]] = states.get(proof["status"], 0) + 1
        sem = receipt["semantic_review"]["status"]
        semantic[sem] = semantic.get(sem, 0) + 1
        current = {k: prov[k] for k in ("workspace_inputs", "lean_toolchain_sha256", "lake_manifest_sha256")}
        if workspace in workspaces and workspaces[workspace] != current:
            errors.append(f"{name}: inconsistent workspace input map")
        workspaces[workspace] = current
        if verifier_inputs is not None and verifier_inputs != prov["verifier_inputs"]:
            errors.append(f"{name}: inconsistent verifier input map")
        verifier_inputs = prov["verifier_inputs"]

    # The main workspace root module is generated deterministically. Its other
    # inputs, and all inputs in the nested workspace, are tracked Git blobs.
    module = ast.parse(blob(args.current, "orchestration/formal/workspace.py").decode())
    header = next(ast.literal_eval(node.value) for node in module.body
                  if isinstance(node, ast.Assign) and any(
                      isinstance(t, ast.Name) and t.id == "_HEADER" for t in node.targets))
    modules = sorted(p[len("formal/"):-5].replace("/", ".") for p in
                     git(args.repo, "ls-tree", "-r", "--name-only", args.current,
                         "formal/CryptoResearch").decode().splitlines() if p.endswith(".lean"))
    generated_root = (header.format(library="CryptoResearch") + "\n"
                      + "".join(f"import {m}\n" for m in modules)).encode()
    for workspace, record in workspaces.items():
        for path, digest in record["workspace_inputs"].items():
            content = (generated_root if workspace == "formal" and path == "CryptoResearch.lean"
                       else blob(args.current, workspace + "/" + path))
            if sha(content) != digest:
                errors.append(f"{workspace}/{path}: workspace input hash")
        for filename, key in (("lean-toolchain", "lean_toolchain_sha256"),
                              ("lake-manifest.json", "lake_manifest_sha256")):
            if sha(blob(args.current, workspace + "/" + filename)) != record[key]:
                errors.append(f"{workspace}/{filename}: pin hash")
    for path, digest in (verifier_inputs or {}).items():
        if sha(blob(args.current, path)) != digest:
            errors.append(f"{path}: verifier input hash")

    pins = {side: json.loads(files[f"dependency-pins-{side}.json"].read_text())
            for side in ("before", "after")}
    if pins["before"] != pins["after"]:
        errors.append("dependency pins changed between before and after")
    for side, record in pins.items():
        if not (record["passed"] is True and record["github_run_id"] == args.run_id
                and record["github_checkout_sha"] == args.checkout
                and all(dep["expected_revision"] == dep["installed_revision"]
                        and dep["clean_sources"] is True for dep in record["dependencies"])):
            errors.append(f"dependency pins {side}: status or identity")
        if record["manifest_sha256"] != workspaces["formal"]["lake_manifest_sha256"]:
            errors.append(f"dependency pins {side}: manifest hash")
    result = {
        "schema": "crypto.validation.hosted_formal_sweep_audit/v1",
        "run_id": args.run_id, "checkout": args.checkout, "current": args.current,
        "targets": len(expected), "receipt_files": len(files),
        "workspaces": {name: len(record["workspace_inputs"]) for name, record in sorted(workspaces.items())},
        "verifier_inputs": len(verifier_inputs or {}), "proof_statuses": states,
        "semantic_review_statuses": semantic, "errors": errors,
        "status": "pass" if not errors else "fail",
        "scope": "Receipt contents, Git input hashes, and hosted pin records; no independent Lean execution or claim-semantic review",
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "targets", "receipt_files", "workspaces", "proof_statuses", "semantic_review_statuses", "errors")}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
