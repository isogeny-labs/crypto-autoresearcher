"""Fail-closed bundle/evidence handling; fixtures do not assert Lean proofs.

Fresh proof execution remains the canonical verifier's responsibility. These
unit fixtures exercise provenance checks, failure propagation and mode labels.
The actual five unchanged CI receipts are checked separately by the CLI.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import verify_lfd_bundle as check
from orchestration.formal.targets import load_spec


def write_json(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / "repo"
    receipts = tmp_path / "receipts"
    specs = {}
    files = set()
    for name in check.TARGETS:
        original = check.ROOT / f"formal/targets/{name}.yaml"
        destination = root / f"formal/targets/{name}.yaml"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(original.read_bytes())
        specs[name] = load_spec(destination)
        files.add(destination)
        source = root / "formal" / specs[name]["theorem_file"]
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("-- test-only source; not a claimed proof\nimport CryptoResearch.Helper\n")
        files.add(source)
    helper = root / "formal/CryptoResearch/Helper.lean"
    helper.write_text("-- test-only imported source\n")
    files.add(helper)
    for name in ["lean-toolchain", "lake-manifest.json"]:
        path = root / "formal" / name
        path.write_text("test fixture\n")
        files.add(path)
    write_json(root / check.BUNDLE, {
        "schema": "degree-bound-proof-map/v2",
        "artifacts": {str(p.relative_to(root)): check.digest(p) for p in files},
    })
    metadata = {"schema": "lfd-ci-evidence/v1", "verification_commit": "b" * 40,
                "receipt_sha256": {}}
    for name, spec in specs.items():
        result = {key: spec[key] for key in ["theorem_name", "theorem_file"]}
        result.update(status="machine_verified", build_passed=True,
                      axiom_audit_passed=True, forbidden_constructs=[], blocking_reason=None)
        record = {
            "schema": "crypto.autoresearch.formal_verification.v1",
            "task": {key: spec[key] for key in ["task_id", "theorem_name", "theorem_file", "workspace"]},
            "verification": result, "infrastructure_failure": None,
            "provenance": {
                "source_commit": "b" * 40,
                "task_spec_sha256": check.digest(root / f"formal/targets/{name}.yaml"),
                "theorem_sha256": check.digest(root / "formal" / spec["theorem_file"]),
                "lean_toolchain_sha256": check.digest(root / "formal/lean-toolchain"),
                "lake_manifest_sha256": check.digest(root / "formal/lake-manifest.json"),
                "workspace_inputs": check.local_sources(root, spec["theorem_file"]),
            },
        }
        path = receipts / f"{name}.json"
        write_json(path, record)
        metadata["receipt_sha256"][path.name] = check.digest(path)
    write_json(receipts / "provenance.json", metadata)
    return root, receipts


def alter_receipt(receipts, change):
    path = receipts / (check.TARGETS[0] + ".json")
    record = json.loads(path.read_text())
    change(record)
    write_json(path, record)
    metadata = json.loads((receipts / "provenance.json").read_text())
    metadata["receipt_sha256"][path.name] = check.digest(path)
    write_json(receipts / "provenance.json", metadata)


def test_all_five_receipts_bind_current_sources(bundle):
    root, receipts = bundle
    assert check.check_integrity(root)["status"] == "passed"
    assert len(check.check_ci_receipts(root, receipts)) == 5


def test_integrity_does_not_claim_a_proof_run(bundle, monkeypatch, capsys):
    root, _ = bundle
    monkeypatch.setattr(check, "ROOT", root)
    monkeypatch.setattr(check, "run_lean", lambda *a: pytest.fail("unexpected proof execution"))
    assert check.main(["--integrity-only"]) == 0
    assert json.loads(capsys.readouterr().out)["proof_action"] == "not_run"


def test_changed_artifact_rejected(bundle):
    root, _ = bundle
    (root / "formal/CryptoResearch/Helper.lean").write_text("changed\n")
    with pytest.raises(check.BundleError, match="digest mismatch"):
        check.check_integrity(root)


def test_imported_source_drift_rejected_independently(bundle):
    root, receipts = bundle
    (root / "formal/CryptoResearch/Helper.lean").write_text("changed\n")
    with pytest.raises(check.BundleError, match="imported source mismatch"):
        check.check_ci_receipts(root, receipts)


@pytest.mark.parametrize("field,value", [
    ("build_passed", False), ("axiom_audit_passed", False),
    ("status", "formalization_blocked"), ("forbidden_constructs", ["sorry"]),
])
def test_failed_receipt_cannot_be_relabelled_by_metadata(bundle, field, value):
    root, receipts = bundle
    alter_receipt(receipts, lambda r: r["verification"].update({field: value}))
    with pytest.raises(check.BundleError, match="did not pass"):
        check.check_ci_receipts(root, receipts)


def test_nearby_theorem_is_not_the_requested_theorem(bundle):
    root, receipts = bundle
    alter_receipt(receipts, lambda r: r["task"].update(theorem_name="Other.nearbyLemma"))
    with pytest.raises(check.BundleError, match="different theorem_name"):
        check.check_ci_receipts(root, receipts)


def test_bundle_path_escape_rejected(bundle):
    root, _ = bundle
    path = root / check.BUNDLE
    record = json.loads(path.read_text())
    record["artifacts"]["../outside.txt"] = "a" * 64
    write_json(path, record)
    with pytest.raises(check.BundleError, match="path escapes"):
        check.check_integrity(root)


def test_canonical_verifier_is_used_for_each_target(bundle, tmp_path):
    root, _ = bundle
    calls = []
    code, outcomes = check.run_lean(root, tmp_path / "fresh", verifier=lambda args: calls.append(args) or 0)
    assert code == 0 and len(outcomes) == len(calls) == 5
    assert all(args[:3] == ["--repo-root", str(root), "verify"] for args in calls)
    assert {Path(args[args.index("--task-file") + 1]).stem for args in calls} == set(check.TARGETS)


def test_canonical_infrastructure_failure_stays_failure(bundle, tmp_path):
    root, _ = bundle
    code, outcomes = check.run_lean(root, tmp_path / "fresh", verifier=lambda args: 3)
    assert code == 3 and len(outcomes) == 1
    with pytest.raises(FileExistsError):
        check.run_lean(root, tmp_path / "fresh", verifier=lambda args: pytest.fail("overwrote receipts"))
