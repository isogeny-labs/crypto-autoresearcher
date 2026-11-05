"""Adapter for the native six-track ECDLP index-calculus challenge verifier."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from .runner import RunResult

EXP_ID = "EXP-ECDLP-CHALLENGES-001"
EXP_AREA = "ECDLPCH"
REPO = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = REPO / "harness/fixtures/ecdlp_challenges_v1.json"
DEFAULT_FIXTURE_FILE_SHA256 = "0399b42507f2c0c410bf801935ece4c00d5d7a16dc9b7276cfebf77f0115eb65"
TRACKS = (
    "relation_forge",
    "factor_base_lab",
    "matrix_smash",
    "descent_tree",
    "transfer_audit",
    "orbit_relations",
)
CLAIM_BOUNDARY = {
    "performance": "not_measured",
    "security": "not_established",
    "transfer_advantage": "unknown",
}


class ChallengeRefused(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_identity(binary: Path) -> dict:
    """Best-effort source identity for a binary built in a Git checkout."""
    for parent in binary.parents:
        if not (parent / ".git").exists() or not (parent / "Cargo.toml").is_file():
            continue
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=parent, capture_output=True,
            text=True, check=False).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=parent, capture_output=True, text=True, check=False).stdout
        return {
            "repository": str(parent),
            "commit": commit or None,
            "dirty": bool(status.strip()),
        }
    return {"repository": None, "commit": None, "dirty": None}


def resolve_binary(explicit: str | None = None) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise ChallengeRefused(
            f"explicit native ecdlp-challenges verifier is not executable: {candidate}")

    candidates: list[Path] = []
    if os.environ.get("ECDLP_CHALLENGES_BIN"):
        candidates.append(Path(os.environ["ECDLP_CHALLENGES_BIN"]))
    sibling = REPO.parent / "crypto" / "target"
    candidates.extend((
        sibling / "release/ecdlp-challenges",
        sibling / "debug/ecdlp-challenges",
    ))
    discovered = shutil.which("ecdlp-challenges")
    if discovered:
        candidates.append(Path(discovered))
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved.is_file() and os.access(resolved, os.X_OK):
            return resolved
    rendered = ", ".join(str(candidate) for candidate in candidates) or "none"
    raise ChallengeRefused(
        "native ecdlp-challenges verifier not found; pass --crypto-bin or set "
        f"ECDLP_CHALLENGES_BIN (checked: {rendered})")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ChallengeRefused(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ChallengeRefused(f"JSON root in {path} is not an object")
    return value


def _native(binary: Path, arguments: list[str]) -> tuple[dict, str, str]:
    completed = subprocess.run(
        [str(binary), *arguments], capture_output=True, text=True,
        timeout=30, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no diagnostic"
        raise ChallengeRefused(
            f"native verifier command {' '.join(arguments[:1])} failed "
            f"with exit {completed.returncode}: {detail}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ChallengeRefused("native verifier stdout is not one JSON object") from error
    if not isinstance(value, dict):
        raise ChallengeRefused("native verifier stdout root is not an object")
    return value, completed.stdout, completed.stderr


def validate_receipt(receipt: dict) -> None:
    if receipt.get("schema") != "crypto.ecdlp-challenge-receipt/v1":
        raise ChallengeRefused("native receipt has an unsupported schema")
    if receipt.get("status") != "verified":
        raise ChallengeRefused("native receipt is not verified")
    tracks = receipt.get("tracks")
    if not isinstance(tracks, dict) or set(tracks) != set(TRACKS):
        raise ChallengeRefused("native receipt does not contain exactly the six tracks")
    if any(not isinstance(tracks[name], dict)
           or tracks[name].get("status") != "verified" for name in TRACKS):
        raise ChallengeRefused("one or more native track receipts are not verified")
    frontier = receipt.get("frontier")
    if (not isinstance(frontier, list) or len(frontier) != len(TRACKS)
            or {entry.get("track") for entry in frontier
                if isinstance(entry, dict)} != set(TRACKS)):
        raise ChallengeRefused("native receipt frontier does not cover exactly six tracks")
    if receipt.get("claim_boundary") != CLAIM_BOUNDARY:
        raise ChallengeRefused("native receipt widened the fixed claim boundary")


def make_result(*, binary: str | None = None, fixture: str | None = None,
                submission: str | None = None) -> RunResult:
    native = resolve_binary(binary)
    fixture_path = Path(fixture).resolve() if fixture else DEFAULT_FIXTURE
    if not fixture and sha256_file(fixture_path) != DEFAULT_FIXTURE_FILE_SHA256:
        raise ChallengeRefused("committed default challenge fixture digest has drifted")
    fixture_value = read_json(fixture_path)
    logs: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ecdlp-challenge-") as tmp:
        if submission:
            submission_path = Path(submission).resolve()
            submission_value = read_json(submission_path)
        else:
            submission_path = Path(tmp) / "baseline.json"
            generated, stdout, stderr = _native(
                native, ["baseline", "--fixture", str(fixture_path)])
            submission_value = generated
            submission_path.write_text(
                json.dumps(generated, separators=(",", ":")), encoding="utf-8")
            logs.extend((stdout, stderr))
        receipt, stdout, stderr = _native(
            native, ["verify", "--fixture", str(fixture_path),
                     "--submission", str(submission_path)])
        logs.extend((stdout, stderr))
    validate_receipt(receipt)
    if receipt.get("suite_id") != fixture_value.get("suite_id"):
        raise ChallengeRefused("receipt suite_id differs from the fixture")
    frontier = {entry["track"]: entry["value"] for entry in receipt["frontier"]}
    binary_digest = sha256_file(native)
    native_source = source_identity(native)
    return RunResult(
        run_suffix=f"fixture-{receipt['submission_sha256'][:12]}",
        curve_id=str(receipt["suite_id"]),
        seed=0,
        parameters={
            "fixture_sha256": receipt["fixture_sha256"],
            "submission_sha256": receipt["submission_sha256"],
            "tracks": list(TRACKS),
            "performance_measurement": False,
        },
        metrics={"frontier": frontier, "track_metrics": {
            name: receipt["tracks"][name]["metrics"] for name in TRACKS}},
        certificate={
            "kind": "ecdlp_challenge_receipt",
            "native_verifier": {
                "path": str(native),
                "sha256": binary_digest,
                "source": native_source,
            },
            "statement": {
                "fixture": fixture_value,
                "submission": submission_value,
                "receipt": receipt,
            },
        },
        valid=True,
        stdout="".join(logs),
        raw={
            "receipt": receipt,
            "native_verifier_sha256": binary_digest,
            "native_verifier_source": native_source,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )
