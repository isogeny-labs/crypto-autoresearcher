"""Read committed Git blobs after the repository's authenticated vault filter."""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class GitBlobError(RuntimeError):
    """A Git or vault read failed without exposing blob or key material."""


def show_bytes(repo: Path, ref: str, path: str) -> bytes | None:
    """Return a committed blob as plaintext, or None when the blob is absent."""
    repo = Path(repo)
    try:
        result = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                                capture_output=True, check=False)
    except OSError as exc:
        raise GitBlobError("git is unavailable") from exc
    if result.returncode != 0:
        return None
    return decode_bytes(repo, result.stdout)


def decode_bytes(repo: Path, blob: bytes) -> bytes:
    """Decode bytes from `git show` or `git cat-file`, authenticating vault data."""
    if not blob.startswith(b"VLT1"):
        return blob
    try:
        config = subprocess.run(["git", "-C", str(repo), "config", "--get", "filter.vault.smudge"],
                                capture_output=True, text=True, check=False)
    except OSError as exc:
        raise GitBlobError("git is unavailable") from exc
    if config.returncode != 0 or not config.stdout.strip():
        raise GitBlobError("vault smudge filter is not configured")
    try:
        command = shlex.split(config.stdout.strip())
        return subprocess.run(command, input=blob, capture_output=True, check=True).stdout
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise GitBlobError("could not decrypt committed blob") from exc


def show_text(repo: Path, ref: str, path: str) -> str | None:
    blob = show_bytes(repo, ref, path)
    if blob is None:
        return None
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GitBlobError("committed blob is not UTF-8") from exc
