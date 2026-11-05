#!/usr/bin/env python3
"""Check the frozen LFD bundle, replay CI evidence, or run canonical Lean checks.

A successful integrity-only check does NOT verify a mathematical proof.
CI evidence mode checks existing receipts against current source bytes; it does
not execute Lean. --run-lean delegates to the unchanged canonical verifier,
including its full-workspace build and axiom audits. No gate is replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BUNDLE = "analysis/rigorous-lfd-solving-20261105/proof-map.json"
TARGETS = (
    "boolean-normalization-repair-20261105",
    "boolean-lastfall-upper-20261105",
    "binary-semaev-repair-20261105",
    "binary-supported-affine-lastfall-20261105",
    "binary-raw-chain-lastfall-20261105",
)
DIGEST = re.compile(r"[0-9a-f]{64}")
LOCAL_IMPORT = re.compile(r"^(?:public |private )?import\s+(.+)$", re.M)


class BundleError(ValueError):
    pass


def inside(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name:
        raise BundleError(f"path escapes bundle: {name}")
    result = (root / name).resolve()
    if not result.is_relative_to(root.resolve()):
        raise BundleError(f"path escapes bundle: {name}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_integrity(root: Path) -> dict:
    record = json.loads(inside(root, BUNDLE).read_text())
    if record.get("schema") != "degree-bound-proof-map/v2":
        raise BundleError("unsupported proof-map schema")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise BundleError("proof map has no artifact bindings")
    required = {f"formal/targets/{name}.yaml" for name in TARGETS}
    if not required.issubset(artifacts):
        raise BundleError("proof map omits a required LFD target")
    for name, expected in artifacts.items():
        if not isinstance(expected, str) or DIGEST.fullmatch(expected) is None:
            raise BundleError(f"invalid digest: {name}")
        path = inside(root, name)
        if not path.is_file():
            raise BundleError(f"missing artifact: {name}; hydrate it with tools/artifacts first")
        if digest(path) != expected:
            raise BundleError(f"artifact digest mismatch: {name}")
    return {"status": "passed", "artifacts_checked": len(artifacts)}


def local_sources(root: Path, relative: str) -> dict[str, str]:
    """Hash the local Lean import closure; external packages use the pin checks."""
    seen: dict[str, str] = {}
    pending = [relative]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        path = inside(root, "formal/" + name)
        seen[name] = digest(path)
        for line in LOCAL_IMPORT.findall(path.read_text()):
            for module in line.split("--", 1)[0].split():
                if module.startswith("CryptoResearch."):
                    if re.fullmatch(r"[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+", module) is None:
                        raise BundleError("invalid local module name")
                    pending.append(module.replace(".", "/") + ".lean")
    return seen


def check_ci_receipts(root: Path, directory: Path) -> list[dict]:
    from orchestration.formal.targets import load_spec

    metadata = json.loads((directory / "provenance.json").read_text())
    if metadata.get("schema") != "lfd-ci-evidence/v1":
        raise BundleError("unsupported CI evidence metadata")
    merge_sha = metadata.get("verification_commit", "")
    if re.fullmatch(r"[0-9a-f]{40}", merge_sha) is None:
        raise BundleError("CI evidence must bind its actual verification commit")
    results = []
    for name in TARGETS:
        receipt_path = directory / (name + ".json")
        if digest(receipt_path) != metadata.get("receipt_sha256", {}).get(receipt_path.name):
            raise BundleError(f"CI receipt digest mismatch: {name}")
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("schema") != "crypto.autoresearch.formal_verification.v1":
            raise BundleError(f"wrong receipt schema: {name}")
        result = receipt.get("verification") or {}
        if (receipt.get("infrastructure_failure") is not None
                or result.get("status") != "machine_verified"
                or result.get("build_passed") is not True
                or result.get("axiom_audit_passed") is not True
                or result.get("forbidden_constructs") != []
                or result.get("blocking_reason") is not None):
            raise BundleError(f"CI verification did not pass: {name}")
        spec_path = inside(root, f"formal/targets/{name}.yaml")
        spec = load_spec(spec_path)
        task = receipt.get("task") or {}
        for key in ("task_id", "theorem_name", "theorem_file", "workspace"):
            if task.get(key) != spec.get(key):
                raise BundleError(f"CI receipt identifies a different {key}: {name}")
        for key in ("theorem_name", "theorem_file"):
            if result.get(key) != spec[key]:
                raise BundleError(f"CI result identifies a different {key}: {name}")
        provenance = receipt.get("provenance") or {}
        if provenance.get("source_commit") != merge_sha:
            raise BundleError(f"CI verification commit mismatch: {name}")
        files = {
            "task_spec_sha256": spec_path,
            "theorem_sha256": inside(root, "formal/" + spec["theorem_file"]),
            "lean_toolchain_sha256": root / "formal/lean-toolchain",
            "lake_manifest_sha256": root / "formal/lake-manifest.json",
        }
        for key, path in files.items():
            if provenance.get(key) != digest(path):
                raise BundleError(f"CI source/config mismatch ({key}): {name}")
        closure = local_sources(root, spec["theorem_file"])
        for path, expected in closure.items():
            if provenance.get("workspace_inputs", {}).get(path) != expected:
                raise BundleError(f"CI imported source mismatch: {path}")
        results.append({"target": name, "theorem": spec["theorem_name"],
                        "local_sources_bound": len(closure),
                        "status": "recorded_ci_evidence_matches"})
    return results


def run_lean(root: Path, directory: Path, verifier=None) -> tuple[int, list[dict]]:
    from orchestration.formal.cli import main as canonical_verify
    from orchestration.formal.lean_worker import verification_session

    # Caller must choose a fresh directory; individual receipts are write-once.
    directory.mkdir(parents=True, exist_ok=False)
    verifier = verifier or canonical_verify
    outcomes = []
    with verification_session():
        for name in TARGETS:
            code = verifier([
                "--repo-root", str(root), "verify",
                "--task-file", str(root / f"formal/targets/{name}.yaml"),
                "--artifact-out", str(directory / f"{name}.json"),
            ])
            outcomes.append({"target": name, "canonical_exit_code": code})
            if code:
                return code, outcomes
    return 0, outcomes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--integrity-only", action="store_true")
    mode.add_argument("--ci-receipts", type=Path, metavar="DIRECTORY")
    mode.add_argument("--run-lean", action="store_true")
    parser.add_argument("--artifact-dir", type=Path,
                        help="fresh receipt directory, required with --run-lean")
    parser.add_argument("--output", type=Path, help="new JSON summary file; never overwritten")
    args = parser.parse_args(argv)
    if args.run_lean and args.artifact_dir is None:
        parser.error("--run-lean requires --artifact-dir")
    if args.output and args.output.exists():
        parser.error("--output already exists; choose a new path")
    report = {"schema": "lfd-bundle-check/v1", "proof_action": "not_run",
              "scope": "frozen LFD bundle; no novelty, research promotion or runtime claim"}
    code = 0
    try:
        report["integrity"] = check_integrity(ROOT)
        if args.ci_receipts:
            report["ci_evidence"] = check_ci_receipts(ROOT, args.ci_receipts)
            report["proof_action"] = "checked_existing_ci_receipts; Lean not executed"
        elif args.run_lean:
            code, report["canonical_verifications"] = run_lean(ROOT, args.artifact_dir)
            report["proof_action"] = "canonical_verifier_passed" if code == 0 else "canonical_verifier_failed"
    except (BundleError, OSError, ValueError, KeyError) as exc:
        report["error"] = str(exc)
        code = 1
    report["exit_code"] = code
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
