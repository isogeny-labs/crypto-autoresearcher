#!/usr/bin/env python3
"""Encrypt a commit tree at the object level and upload it in bounded pushes.

This is the bulk rollout companion to vaultctl.py.  It never materialises the
plaintext working tree: it reads blobs from the object database, writes
AES-256-SIV ciphertext blobs, and builds trees/commits with Git plumbing.

GitHub rejects pushes over 2 GB.  The tool therefore uploads the ciphertext in
``--chunk-bytes`` seed commits (default 1 GB), then force-pushes one clean final
commit whose tree references the already-uploaded blobs.  The seed commits are
only transport; the final branch history is ``<base>`` + one encryption commit.

Nothing here prints the key, plaintext contents, or file contents.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vaultctl  # noqa: E402


def git(*args: str, input_bytes: bytes | None = None, check: bool = True,
        capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        input=input_bytes,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=check,
    )


def rev(spec: str) -> str:
    return git("rev-parse", spec).stdout.decode().strip()


def object_format() -> str:
    try:
        return git("rev-parse", "--show-object-format").stdout.decode().strip()
    except subprocess.CalledProcessError:
        return "sha1"


def list_tree(commit: str):
    """Yield (path, mode, oid) for every blob in the commit."""
    raw = git("ls-tree", "-r", "-z", "--full-tree", commit).stdout
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid = meta.split(b" ")
        if kind != b"blob":
            continue
        yield path.decode("utf-8", "surrogateescape"), mode.decode(), oid.decode()


def batch_sizes(oids: list[str]) -> dict[str, int]:
    if not oids:
        return {}
    payload = ("\n".join(oids) + "\n").encode()
    out = git("cat-file", "--batch-check", input_bytes=payload).stdout
    sizes: dict[str, int] = {}
    for oid, line in zip(oids, out.splitlines()):
        parts = line.split()
        if len(parts) >= 3 and parts[1] == b"blob":
            sizes[oid] = int(parts[2])
    return sizes


def read_blobs(oids: list[str]):
    """Yield (oid, content) using a single cat-file --batch process.

    The request list goes through a temporary file: writing a large list to a
    pipe while Git is streaming multi-megabyte blobs back can deadlock.
    """
    if not oids:
        return
    with tempfile.NamedTemporaryFile("wb", delete=False) as request:
        request.write(("\n".join(oids) + "\n").encode())
        request_path = request.name
    try:
        with open(request_path, "rb") as stdin:
            proc = subprocess.Popen(
                ["git", "cat-file", "--batch"],
                stdin=stdin,
                stdout=subprocess.PIPE,
            )
            assert proc.stdout
            try:
                for expected in oids:
                    header = proc.stdout.readline().split()
                    if len(header) < 3 or header[1] != b"blob":
                        raise RuntimeError("encrypt_tree: unexpected cat-file header")
                    size = int(header[2])
                    data = proc.stdout.read(size)
                    proc.stdout.read(1)
                    yield expected, data
            finally:
                proc.stdout.close()
                proc.wait()
    finally:
        os.unlink(request_path)


def hash_blobs(paths: list[str]) -> list[str]:
    if not paths:
        return []
    payload = ("\n".join(paths) + "\n").encode()
    out = git("hash-object", "-w", "--stdin-paths", input_bytes=payload).stdout
    return out.decode().split()


def hash_trees(paths: list[str]) -> list[str]:
    if not paths:
        return []
    payload = ("\n".join(paths) + "\n").encode()
    out = git(
        "hash-object", "-t", "tree", "-w", "--stdin-paths", input_bytes=payload
    ).stdout
    return out.decode().split()


def make_seed_commit(blob_oids: list[str], parent: str, message: str) -> str:
    entries = []
    width = max(6, len(str(len(blob_oids) - 1)))
    for index, oid in enumerate(blob_oids):
        entries.append(f"100644 blob {oid}\t{index:0{width}d}\0")
    tree = git(
        "mktree", "-z", input_bytes="".join(entries).encode()
    ).stdout.decode().strip()
    return git(
        "commit-tree", tree, "-p", parent, "-m", message
    ).stdout.decode().strip()


def build_final_tree(entries, replacements: dict[str, str], workdir: Path) -> str:
    """Build all tree objects for ``entries`` with replacement blob OIDs."""
    root: dict = {}
    for path, mode, oid in entries:
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (mode, replacements.get(path, oid))

    tree_files: list[str] = []
    counter = 0

    def emit(node: dict) -> str:
        nonlocal counter
        rows = []
        for name, value in node.items():
            if isinstance(value, dict):
                child = emit(value)
                rows.append((name, "40000", child, True))
            else:
                mode, oid = value
                rows.append((name, mode, oid, False))
        rows.sort(key=lambda r: r[0].encode("utf-8", "surrogateescape") + (b"/" if r[3] else b""))
        content = b"".join(
            f"{mode} {name}".encode("utf-8", "surrogateescape") + b"\0" + bytes.fromhex(oid)
            for name, mode, oid, _ in rows
        )
        oid = hashlib.new(object_format(), f"tree {len(content)}\0".encode() + content).hexdigest()
        target = workdir / f"tree-{counter:07d}"
        counter += 1
        target.write_bytes(content)
        tree_files.append(str(target))
        return oid

    root_oid = emit(root)
    written = hash_trees(tree_files)
    if root_oid not in written:
        raise RuntimeError("encrypt_tree: root tree object was not written")
    return root_oid


def push(branch: str, force: bool, attempts: int = 4) -> None:
    for attempt in range(1, attempts + 1):
        args = ["push", "origin", f"refs/heads/{branch}:refs/heads/{branch}"]
        if force:
            args.insert(1, "--force")
        proc = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            return
        if attempt == attempts:
            sys.stderr.write(proc.stderr.decode("utf-8", "replace")[-2000:] + "\n")
            raise SystemExit(f"encrypt_tree: push failed for {branch}")
        time.sleep(2 * attempt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--branch", default=None)
    parser.add_argument("--chunk-bytes", type=int, default=1_000_000_000)
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--start-chunk", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--temp-dir", default=None)
    args = parser.parse_args()

    base = rev(args.base)
    branch = args.branch or git("rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
    entries = list(list_tree(base))
    sizes = batch_sizes([oid for _, _, oid in entries])
    candidates = []
    for path, mode, oid in entries:
        if mode == "120000":
            continue
        if vaultctl._is_plaintext_path(path):
            continue
        candidates.append((path, mode, oid, sizes.get(oid, 0)))
    candidates.sort(key=lambda item: item[0])

    chunks: list[list] = []
    current: list = []
    current_bytes = 0
    for item in candidates:
        size = item[3]
        if current and current_bytes + size > args.chunk_bytes:
            chunks.append(current)
            current = []
            current_bytes = 0
        current.append(item)
        current_bytes += size
    if current:
        chunks.append(current)

    print(
        f"encrypt_tree: base={base[:12]} blobs={len(entries)} "
        f"candidates={len(candidates)} chunks={len(chunks)} "
        f"bytes={sum(sizes.get(oid,0) for _,_,oid,_ in candidates)/1e9:.2f}GB",
        flush=True,
    )
    if args.dry_run:
        return 0

    git("update-ref", f"refs/heads/{branch}", base)
    parent = base
    replacements: dict[str, str] = {}
    if args.temp_dir:
        Path(args.temp_dir).mkdir(parents=True, exist_ok=True)
    tmp_root = Path(tempfile.mkdtemp(prefix="cavault-bulk-", dir=args.temp_dir))
    try:
        for index, chunk in enumerate(chunks):
            if index < args.start_chunk:
                continue
            started = time.time()
            tmp = tmp_root / f"chunk-{index:04d}"
            tmp.mkdir()
            blob_paths: list[str] = []
            blob_targets: list[str] = []
            kept = 0
            for oid, data in read_blobs([item[2] for item in chunk]):
                if vaultctl.is_ciphertext(data) or data.startswith(vaultctl.LFS_POINTER_PREFIX):
                    kept += 1
                    continue
                blob_paths.append(str(tmp / f"{len(blob_paths):07d}"))
                blob_targets.append(oid)
                (tmp / f"{len(blob_paths)-1:07d}").write_bytes(vaultctl.encrypt(data))
            new_oids = hash_blobs(blob_paths)
            if len(new_oids) != len(blob_targets):
                raise RuntimeError("encrypt_tree: hash-object count mismatch")
            for path, mode, old_oid, _ in chunk:
                replacements.setdefault(path, old_oid)
            by_old = dict(zip(blob_targets, new_oids))
            for path, mode, old_oid, _ in chunk:
                if old_oid in by_old:
                    replacements[path] = by_old[old_oid]
            parent = make_seed_commit(
                new_oids,
                parent,
                f"vault: seed chunk {index + 1}/{len(chunks)}",
            )
            git("update-ref", f"refs/heads/{branch}", parent)
            shutil.rmtree(tmp)
            elapsed = time.time() - started
            print(
                f"encrypt_tree: chunk {index+1}/{len(chunks)} "
                f"encrypted={len(new_oids)} kept={kept} "
                f"commit={parent[:12]} {elapsed:.1f}s",
                flush=True,
            )
            if args.push:
                push(branch, force=(index > 0))

        started = time.time()
        tree = build_final_tree(entries, replacements, tmp_root)
        final = git(
            "commit-tree", tree, "-p", base, "-m",
            "vault: encrypt tracked tree with AES-256-SIV (KEY-derived)",
        ).stdout.decode().strip()
        git("update-ref", f"refs/heads/{branch}", final)
        print(
            f"encrypt_tree: final tree={tree[:12]} commit={final[:12]} "
            f"{time.time()-started:.1f}s",
            flush=True,
        )
        if args.push:
            push(branch, force=True)
            print("encrypt_tree: pushed final commit", flush=True)
    finally:
        if not args.keep_temp:
            shutil.rmtree(tmp_root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
