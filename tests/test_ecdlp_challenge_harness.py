"""Six-track ECDLP challenge adapter and optional real-native end-to-end control."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from harness import ecdlp_challenges
from harness import runner_ecdlp_v1 as challenge_runner

ROOT = Path(__file__).resolve().parents[1]


def native_binary() -> Path | None:
    candidates = []
    if os.environ.get("ECDLP_CHALLENGES_BIN"):
        candidates.append(Path(os.environ["ECDLP_CHALLENGES_BIN"]))
    candidates.extend((
        ROOT.parent / "crypto/target/debug/ecdlp-challenges",
        ROOT.parent / "crypto/target/release/ecdlp-challenges",
    ))
    return next((path.resolve() for path in candidates
                 if path.is_file() and os.access(path, os.X_OK)), None)


def test_receipt_shape_requires_all_tracks_and_fixed_claim_boundary():
    assert (ecdlp_challenges.sha256_file(ecdlp_challenges.DEFAULT_FIXTURE)
            == ecdlp_challenges.DEFAULT_FIXTURE_FILE_SHA256)
    receipt = {
        "schema": "crypto.ecdlp-challenge-receipt/v1",
        "status": "verified",
        "tracks": {name: {"status": "verified", "metrics": {}}
                   for name in ecdlp_challenges.TRACKS},
        "frontier": [{"track": name, "value": index}
                     for index, name in enumerate(ecdlp_challenges.TRACKS)],
        "claim_boundary": dict(ecdlp_challenges.CLAIM_BOUNDARY),
    }
    ecdlp_challenges.validate_receipt(receipt)

    missing = json.loads(json.dumps(receipt))
    missing["tracks"].pop("matrix_smash")
    with pytest.raises(ecdlp_challenges.ChallengeRefused, match="six tracks"):
        ecdlp_challenges.validate_receipt(missing)

    widened = json.loads(json.dumps(receipt))
    widened["claim_boundary"]["performance"] = "measured"
    with pytest.raises(ecdlp_challenges.ChallengeRefused, match="claim boundary"):
        ecdlp_challenges.validate_receipt(widened)


def test_explicit_missing_binary_is_refused(tmp_path, monkeypatch):
    monkeypatch.delenv("ECDLP_CHALLENGES_BIN", raising=False)
    monkeypatch.setattr(ecdlp_challenges.shutil, "which", lambda _: None)
    monkeypatch.setattr(ecdlp_challenges, "REPO", tmp_path / "isolated")
    with pytest.raises(ecdlp_challenges.ChallengeRefused, match="not executable"):
        ecdlp_challenges.resolve_binary(str(tmp_path / "absent"))


def test_versioned_replay_checks_digest_and_exact_receipt(tmp_path):
    receipt = {
        "schema": "crypto.ecdlp-challenge-receipt/v1",
        "status": "verified",
        "claim_boundary": dict(ecdlp_challenges.CLAIM_BOUNDARY),
    }
    verifier = tmp_path / "verifier"
    verifier.write_text("#!/usr/bin/env python3\nprint(" + repr(json.dumps(receipt)) + ")\n")
    verifier.chmod(0o755)
    cert = {
        "kind": "ecdlp_challenge_receipt",
        "native_verifier": {
            "path": str(verifier),
            "sha256": ecdlp_challenges.sha256_file(verifier),
        },
        "statement": {"fixture": {}, "submission": {}, "receipt": receipt},
    }
    verified, label = challenge_runner._verify(cert)
    assert verified is True
    assert label.startswith("native-replay:")

    altered = json.loads(json.dumps(cert))
    altered["statement"]["receipt"]["status"] = "rejected"
    verified, _ = challenge_runner._verify(altered)
    assert verified is False
    assert "native_receipt_mismatch" in altered["failing_checks"]

    altered = json.loads(json.dumps(cert))
    altered["native_verifier"]["sha256"] = "0" * 64
    verified, _ = challenge_runner._verify(altered)
    assert verified is False
    assert "native_verifier_digest_mismatch" in altered["failing_checks"]


@pytest.mark.skipif(native_binary() is None, reason="sibling native verifier is not built")
def test_real_native_receipt_replay_rejects_tampering():
    result = ecdlp_challenges.make_result(binary=str(native_binary()))
    certificate = dict(result.certificate)
    verified, label = challenge_runner._verify(certificate)
    assert verified is True
    assert label.startswith("native-replay:")
    assert result.metrics["frontier"] == {
        "relation_forge": 5,
        "factor_base_lab": 9,
        "matrix_smash": 5,
        "descent_tree": 2,
        "transfer_audit": 3,
        "orbit_relations": 9,
    }
    assert result.certificate["native_verifier"]["source"]["commit"]

    tampered = json.loads(json.dumps(result.certificate))
    tampered["statement"]["receipt"]["frontier"][0]["value"] += 1
    verified, _ = challenge_runner._verify(tampered)
    assert verified is False
    assert "native_receipt_mismatch" in tampered["failing_checks"]


@pytest.mark.skipif(native_binary() is None, reason="sibling native verifier is not built")
def test_existing_run_program_writes_verified_immutable_record(tmp_path):
    completed = subprocess.run(
        [sys.executable, "-m", "harness.run",
         "--experiment", ecdlp_challenges.EXP_ID,
         "--crypto-bin", str(native_binary()),
         "--out", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
    assert completed.returncode == 0, completed.stderr
    manifests = list((tmp_path / "runs").glob("*/manifest.yaml"))
    assert len(manifests) == 1
    manifest = yaml.safe_load(manifests[0].read_text(encoding="utf-8"))
    run = manifest["run"]
    assert run["status"] == "completed_valid"
    assert run["result"]["valid"] is True
    assert run["result"]["certificate"]["verified"] is True
    assert run["inputs"]["parameters"]["performance_measurement"] is False

    raw = json.loads((manifests[0].parent / "raw-result.json").read_text())
    assert raw["raw"]["receipt"]["status"] == "verified"
    assert raw["raw"]["claim_boundary"] == ecdlp_challenges.CLAIM_BOUNDARY
