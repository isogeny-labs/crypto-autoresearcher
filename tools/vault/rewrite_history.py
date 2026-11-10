#!/usr/bin/env python3
"""Guarded full-history re-encryption for the research vault.

This is a one-time, destructive operation. It is intentionally *not* run by CI.

Default mode is a dry-run: it inventories the repository and writes the exempt
path/blob sets, but changes nothing. Execution requires an explicit mirror and
confirmation, never pushes, and prints the force-push/LFS steps for the
operator.

What it does
------------
Rewrites every commit so that non-bootstrap blobs are AES-256-SIV ciphertext,
using ``git filter-repo --blob-callback``.  Idempotent: already-encrypted blobs
and LFS pointers are left alone.

Exempt blobs (kept plaintext in every historical commit)
--------------------------------------------------------
* blobs that ever appear under the bootstrap paths:
  .gitattributes, .gitignore, .github/, .artifacts/, **/.artifacts.json,
  tools/vault/, VAULT.md
* symlink blobs (mode 120000), collected from every distinct tree object
* Git LFS pointer blobs (detected by content)

Known limitation: a blob whose content is shared between an exempt path and a
non-exempt path stays plaintext. This is rare; the dry-run manifest records the
sets so they can be audited before execution.

Usage
-----
    python3 tools/vault/rewrite_history.py plan
    python3 tools/vault/rewrite_history.py plan --exempt-out /secure/exempt.txt
    python3 tools/vault/rewrite_history.py execute \
        --mirror /Volumes/backup/crypto-autoresearcher-$(date +%F).mirror.git \
        --exempt-file /secure/exempt.txt --confirm crypto-autoresearcher
    python3 tools/vault/rewrite_history.py verify --samples 20

Nothing here prints key material or blob contents.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vaultctl  # noqa: E402

BOOTSTRAP_PATHS = [
    ".gitattributes",
    ".gitignore",
    ".github",
    ".artifacts",
    "tools/vault",
    "VAULT.md",
    ":(glob)**/.artifacts.json",
]
SYMLINK_MODE = "120000"


def git(*args: str, input_bytes: bytes | None = None, check: bool = True) -> bytes:
    proc = subprocess.run(["git", *args], input=input_bytes, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if check and proc.returncode:
        raise SystemExit(proc.stderr.decode("utf-8", "replace")[-1200:])
    return proc.stdout


def is_bare() -> bool:
    return git("rev-parse", "--is-bare-repository").decode().strip() == "true"


def repo_root() -> Path:
    if is_bare():
        return Path(git("rev-parse", "--git-dir").decode().strip()).resolve()
    return Path(git("rev-parse", "--show-toplevel").decode().strip())


def object_types(oids: list[str]) -> dict[str, str]:
    if not oids:
        return {}
    out = git("cat-file", "--batch-check=%(objectname) %(objecttype)",
              input_bytes=("\n".join(oids) + "\n").encode())
    result = {}
    for line in out.decode().splitlines():
        parts = line.split()
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result


def blobs_under_bootstrap() -> set[str]:
    """Blob ids reachable through the bootstrap paths in any commit."""
    out = git("rev-list", "--objects", "--all", "--", *BOOTSTRAP_PATHS)
    oids = [line.split()[0] for line in out.decode("utf-8", "replace").splitlines() if line.strip()]
    # Pathspec glob support varies; collect every historical .artifacts.json
    # manifest by its rev-list object name as well.
    for line in git("rev-list", "--objects", "--all").decode("utf-8", "replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[1].endswith(".artifacts.json"):
            oids.append(parts[0])
    for entry in git("ls-tree", "-r", "-z", "HEAD").split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid = meta.split(b" ")
        if kind == b"blob" and path.decode("utf-8", "surrogateescape").endswith(".artifacts.json"):
            oids.append(oid.decode())
    types = object_types(oids)
    return {oid for oid, kind in types.items() if kind == "blob"}


def symlink_blobs() -> set[str]:
    """Blob ids used with mode 120000 in any tree object in the repository."""
    listing = git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)")
    trees = [line.split()[0] for line in listing.decode().splitlines()
             if line.endswith(" tree")]
    found: set[str] = set()
    for index, tree in enumerate(trees, 1):
        if index % 5000 == 0:
            print(f"  scanned {index}/{len(trees)} trees, {len(found)} symlink blobs", flush=True)
        out = git("ls-tree", "-z", tree)
        for entry in out.split(b"\0"):
            if not entry:
                continue
            meta, _path = entry.split(b"\t", 1)
            mode, kind, oid = meta.split(b" ")
            if mode.decode() == SYMLINK_MODE and kind == b"blob":
                found.add(oid.decode())
    return found


def plan(exempt_out: str | None) -> int:
    root = repo_root()
    print(f"repository: {root}", flush=True)
    print("collecting bootstrap-path history...", flush=True)
    bootstrap = blobs_under_bootstrap()
    print(f"  {len(bootstrap)} bootstrap blobs", flush=True)
    print("collecting symlink history (tree scan)...", flush=True)
    symlinks = symlink_blobs()
    print(f"  {len(symlinks)} symlink blobs", flush=True)
    exempt = bootstrap | symlinks
    print(f"exempt total: {len(exempt)} blobs", flush=True)

    all_blobs = git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)")
    blob_count = sum(1 for line in all_blobs.decode().splitlines() if line.endswith(" blob"))
    print(f"repository blobs: {blob_count}; to encrypt: {blob_count - len(exempt)}", flush=True)
    print(git("count-objects", "-vH").decode(), flush=True)
    if exempt_out:
        Path(exempt_out).write_text("\n".join(sorted(exempt)) + "\n")
        os.chmod(exempt_out, 0o600)
        print(f"wrote exempt set to {exempt_out} (mode 0600)", flush=True)
    print("dry-run complete; nothing changed.", flush=True)
    return 0


def execution_callback(exempt_file: str) -> str:
    tool_dir = str(Path(__file__).resolve().parent)
    return f'''
import sys
sys.path.insert(0, {tool_dir!r})
import vaultctl
_raw = open({exempt_file!r}).read().split()
_exempt = set(_raw) | {{item.encode() for item in _raw}}

def _encrypt(blob):
    oid = blob.original_id
    if isinstance(oid, bytes):
        oid = oid.decode("ascii", "replace")
    if oid in _exempt:
        return
    if blob.data.startswith(vaultctl.MAGIC):
        return
    if blob.data.startswith(vaultctl.LFS_POINTER_PREFIX):
        return
    blob.data = vaultctl.encrypt(blob.data)

_encrypt(blob)
'''


def execute(mirror: str, exempt_file: str, confirm: str) -> int:
    root = repo_root()
    if confirm != root.name:
        raise SystemExit(f"refusing: --confirm must equal repository name {root.name!r}")
    if not os.path.isfile(exempt_file):
        raise SystemExit("refusing: --exempt-file is required and must exist")
    mirror_path = Path(mirror)
    if not mirror_path.exists():
        raise SystemExit(f"refusing: mirror {mirror} does not exist")
    if not (mirror_path / "HEAD").exists() and not (mirror_path / "config").exists():
        raise SystemExit(f"refusing: {mirror} is not a git mirror")
    if not is_bare():
        dirty = git("status", "--porcelain", "-uno").decode().strip()
        if dirty:
            raise SystemExit("refusing: worktree has local changes; run on a clean mirror clone")
    if subprocess.run(["git", "filter-repo", "--version"], capture_output=True).returncode != 0:
        raise SystemExit("git-filter-repo is not installed (pip install git-filter-repo)")

    code = execution_callback(exempt_file)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(code)
        callback_path = handle.name
    try:
        print("running git filter-repo (this rewrites all refs)...", flush=True)
        proc = subprocess.run(
            ["git", "filter-repo", "--force", "--no-gc", "--blob-callback", code],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        sys.stdout.write(proc.stdout.decode("utf-8", "replace")[-4000:])
        sys.stderr.write(proc.stderr.decode("utf-8", "replace")[-4000:])
        if proc.returncode:
            raise SystemExit(f"git filter-repo failed with status {proc.returncode}")
    finally:
        os.unlink(callback_path)

    print("\\nrewrite complete. Next steps (NOT executed here):", flush=True)
    print("  1. verify:  python3 tools/vault/rewrite_history.py verify", flush=True)
    print("  2. git fsck --full && git reflog expire --expire=now --all && git gc --prune=now", flush=True)
    print("  3. re-add remotes removed by filter-repo and force-push every ref:", flush=True)
    print("       git remote add origin <url>", flush=True)
    print("       git push --mirror --force origin", flush=True)
    print("       git push --mirror --force isogeny", flush=True)
    print("  4. re-upload/encrypt LFS objects; LFS payloads are NOT covered by Git filters", flush=True)
    print("  5. recreate worktrees/open PRs; every existing clone is invalid", flush=True)
    print("  6. roll back only by restoring the mirror at " + mirror, flush=True)
    return 0


def verify(samples: int) -> int:
    branches = git("for-each-ref", "--format=%(refname:short)", "refs/heads").decode().split()
    if not branches:
        raise SystemExit("no branches to verify")
    import random
    random.seed(0)
    checked = 0
    problems = 0
    for branch in branches:
        commits = git("rev-list", f"--max-count={samples}", branch).decode().split()
        for commit in commits:
            tree = git("rev-parse", f"{commit}^{{tree}}").decode().strip()
            entries = git("ls-tree", "-r", "-z", tree).split(b"\0")
            random.shuffle(entries)
            for entry in entries[:samples]:
                if not entry:
                    continue
                meta, path = entry.split(b"\t", 1)
                mode, kind, oid = meta.split(b" ")
                if kind != b"blob":
                    continue
                rel = path.decode("utf-8", "surrogateescape")
                if mode == b"120000" or vaultctl._is_plaintext_path(rel):
                    continue
                data = git("cat-file", "blob", oid.decode())
                if not data.startswith(vaultctl.MAGIC):
                    print(f"PLAINTEXT {commit[:12]} {rel}")
                    problems += 1
                checked += 1
    print(f"checked {checked} vaulted blobs across branches; problems={problems}")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan", help="inventory only; no changes")
    p.add_argument("--exempt-out", help="write the exempt blob ids here (0600)")
    e = sub.add_parser("execute", help="rewrite all history (destructive)")
    e.add_argument("--mirror", required=True, help="verified mirror path")
    e.add_argument("--exempt-file", required=True, help="from plan --exempt-out")
    e.add_argument("--confirm", required=True, help="repository directory name")
    v = sub.add_parser("verify", help="sample rewritten history")
    v.add_argument("--samples", type=int, default=20)
    args = parser.parse_args()
    if args.command == "plan":
        return plan(args.exempt_out)
    if args.command == "execute":
        return execute(args.mirror, args.exempt_file, args.confirm)
    return verify(args.samples)


if __name__ == "__main__":
    sys.exit(main())
