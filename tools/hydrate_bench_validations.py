#!/usr/bin/env python3
"""Restore benchmark validation JSON from committed lossless gzip receipts.

Only files explicitly named by benchmark records are considered. Archives use
the normal artifact transport; both encoded and decoded bytes are checked.
This prepares the checkout for benchrec without changing sealed records.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def repo_path(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError(f"unsafe repository path: {name!r}")
    path = root / name
    path.resolve().relative_to(root.resolve())
    return path


def digest(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size


def receipt(root: Path, logical: Path) -> dict | None:
    path = logical.parent / "derived-encodings" / (logical.stem + ".json")
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        return None
    value = json.loads(path.read_text())
    archive = value.get("archive_path")
    if value.get("original_path") != logical.name or not isinstance(archive, str) or Path(archive).name != archive or not archive.endswith(".gz"):
        raise ValueError(f"invalid encoding paths: {path}")
    if not isinstance(value.get("encoding"), str) or not value["encoding"].startswith("gzip"):
        raise ValueError(f"unsupported encoding: {path}")
    for prefix in ("original", "archive"):
        if not re.fullmatch(r"[0-9a-f]{64}", str(value.get(prefix + "_sha256", ""))):
            raise ValueError(f"invalid digest: {path}")
        size = value.get(prefix + "_bytes")
        if type(size) is not int or size < 0:
            raise ValueError(f"invalid byte count: {path}")
    value["archive"] = repo_path(root, str((logical.parent / archive).relative_to(root)))
    return value


def restore(logical: Path, value: dict) -> str:
    expected = value["original_sha256"], value["original_bytes"]
    if logical.exists():
        if digest(logical) != expected:
            raise ValueError(f"existing logical validation differs from receipt: {logical}")
        return "present_verified"
    archive = value["archive"]
    if digest(archive) != (value["archive_sha256"], value["archive_bytes"]):
        raise ValueError(f"archive differs from receipt: {archive}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=logical.parent, prefix=".validation-", delete=False) as output:
            temporary = Path(output.name)
            size = 0
            with gzip.open(archive, "rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(block)
                    if size > value["original_bytes"]:
                        raise ValueError(f"decoded validation exceeds receipt size: {logical}")
                    output.write(block)
        if digest(temporary) != expected:
            raise ValueError(f"decoded validation differs from receipt: {logical}")
        # Atomic create, refusing to overwrite a file created concurrently.
        os.link(temporary, logical)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return "restored_verified"


def hydrate(root: Path, pull=None) -> list[dict]:
    root = root.resolve()
    config_path = root / ".benchrec.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    records = repo_path(root, config.get("records_dir", "benchmarks/records"))
    names = set()
    for record in sorted(records.glob("*.json")):
        value = json.loads(record.read_text()).get("validation")
        if value is not None:
            names.add(value)
    plans = []
    for name in sorted(names):
        logical = repo_path(root, name)
        value = receipt(root, logical)
        if value is not None:
            plans.append((logical, value))
    missing = sorted({str(value["archive"]) for logical, value in plans
                      if not logical.exists() and not value["archive"].exists()})
    if missing:
        if pull is None:
            subprocess.run([sys.executable, str(root / "tools/artifacts/artifacts.py"), "pull", *missing], cwd=root, check=True)
        else:
            pull(missing)
    return [{"path": str(logical.relative_to(root)), "status": restore(logical, value)}
            for logical, value in plans]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(hydrate(args.repo_root), indent=2))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"validation hydration failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
