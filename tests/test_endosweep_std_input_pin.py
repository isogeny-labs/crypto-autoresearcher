"""The Endosweep loader must consume only the declared std-curves revision."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from research.endosweep_dk_exact_20261016 import build_dk_exact as builder


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def test_std_input_pin_rejects_changed_revision_bytes_and_file_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "std-curves"
    curve = root / "brainpool" / "curves.json"
    curve.parent.mkdir(parents=True)
    curve.write_text('{"curves": []}\n')
    _git(root, "init")
    _git(root, "-c", "user.name=Input Pin Test", "-c", "user.email=test@example.invalid",
         "add", "brainpool/curves.json")
    _git(root, "-c", "user.name=Input Pin Test", "-c", "user.email=test@example.invalid",
         "commit", "-m", "pinned curves")
    head = _git(root, "rev-parse", "HEAD")
    monkeypatch.setattr(builder, "STD_CURVES_COMMIT", head)

    assert builder.verify_std_curves_checkout(str(root)) == {
        "brainpool/curves.json": hashlib.sha256(curve.read_bytes()).hexdigest()
    }

    curve.write_text('{"curves": [{"name": "altered"}]}\n')
    with pytest.raises(ValueError, match="input differs"):
        builder.verify_std_curves_checkout(str(root))
    with pytest.raises(ValueError, match="input differs"):
        builder.load_curves(str(root), str(tmp_path / "ark"))
    _git(root, "checkout", "--", "brainpool/curves.json")

    extra = root / "extra" / "curves.json"
    extra.parent.mkdir()
    extra.write_text('{"curves": []}\n')
    with pytest.raises(ValueError, match="file set differs"):
        builder.verify_std_curves_checkout(str(root))
    extra.unlink()

    _git(root, "-c", "user.name=Input Pin Test", "-c", "user.email=test@example.invalid",
         "commit", "--allow-empty", "-m", "different revision")
    with pytest.raises(ValueError, match="checkout must be repository root"):
        builder.verify_std_curves_checkout(str(root))
