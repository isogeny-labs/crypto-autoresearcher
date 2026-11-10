#!/usr/bin/env python3
"""crypto-autoresearcher research vault (AES-256-SIV over git).

Design goals
------------
* Files are stored in Git as authenticated ciphertext; the working tree stays
  plaintext through a Git clean/smudge filter.
* AES-256-SIV (RFC 5297) gives deterministic authenticated encryption: the same
  plaintext yields the same ciphertext, so Git deduplicates and never reports a
  spurious modification.  Equality of plaintexts is therefore observable in the
  object store; this is an accepted trade-off for a Git filter.
* The 64-byte SIV key is derived with HKDF-SHA256 from the deployment secret
  ``KEY``.  The secret is never printed, echoed, or written to a log.
* Filters are idempotent: ``clean`` passes ciphertext through, ``smudge`` passes
  plaintext through.  That makes forward encryption, ``git add
  --renormalize`` and a historical blob rewrite compose without double
  encryption.
* Missing or malformed keys fail closed (exit non-zero); encrypted content is
  never silently committed as plaintext.

Key resolution order (never logged):
  1. ``$KEY``
  2. ``$HOME/.cavault-key`` (0600, CI convenience for later Git commands)
  3. ``$HOME/.zshrc`` ``export KEY=...`` (developer workstations only)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

MAGIC = b"VLT1"
SALT = b"crypto-autoresearcher/vault/v1"
INFO = b"aes-256-siv/v1"
KEY_FILE_NAME = ".cavault-key"
PROCESS_SCRIPT_ENV = "CAVAULT_SCRIPT"

# Paths that must stay readable before the vault is unlocked.  GitHub parses
# workflows before any step runs; Git needs .gitattributes to apply filters.
PLAINTEXT_PREFIXES = (
    ".gitattributes",
    ".gitignore",
    ".github/",
    ".artifacts/",
    "tools/vault/",
)
PLAINTEXT_FILES = {"VAULT.md"}
LFS_POINTER_PREFIX = b"version https://git-lfs"


class VaultError(RuntimeError):
    """An error whose message is safe to show.  Never contains key material."""


# --------------------------------------------------------------------------
# Key material
# --------------------------------------------------------------------------

def _read_zshrc_key() -> str | None:
    path = Path.home() / ".zshrc"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = re.search(
        r"^[ \t]*(?:export[ \t]+)?KEY[ \t]*=[ \t]*(?:'([^']*)'|\"([^\"]*)\"|([^ \t\r\n]*))",
        text,
        re.MULTILINE,
    )
    if not match:
        return None
    value = next((g for g in match.groups() if g is not None), "")
    return value or None


def _raw_key() -> str:
    raw = os.environ.get("KEY")
    if raw:
        return raw
    key_file = Path.home() / KEY_FILE_NAME
    try:
        if key_file.is_file():
            mode = stat.S_IMODE(key_file.stat().st_mode)
            if mode & 0o077:
                raise VaultError(f"vault: {key_file} must not be group/world readable")
            raw = key_file.read_text(encoding="utf-8").strip()
            if raw:
                return raw
    except OSError:
        pass
    raw = _read_zshrc_key()
    if raw:
        return raw
    raise VaultError(
        "vault: KEY is not set (expected $KEY, ~/.cavault-key, or export KEY= in ~/.zshrc)"
    )


def _derive_key() -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF

    return HKDF(
        algorithm=hashes.SHA256(),
        length=64,  # AES-256-SIV keys are 2 x 256 bits
        salt=SALT,
        info=INFO,
    ).derive(_raw_key().encode("utf-8"))


_CIPHER = None


def _cipher():
    global _CIPHER
    if _CIPHER is None:
        from cryptography.hazmat.primitives.ciphers.aead import AESSIV

        _CIPHER = AESSIV(_derive_key())
    return _CIPHER


def is_ciphertext(data: bytes) -> bool:
    return data.startswith(MAGIC)


def encrypt(data: bytes) -> bytes:
    if is_ciphertext(data):
        return data
    return MAGIC + _cipher().encrypt(data, [SALT + b"|" + INFO])


def decrypt(data: bytes) -> bytes:
    if not is_ciphertext(data):
        return data
    try:
        return _cipher().decrypt(data[len(MAGIC) :], [SALT + b"|" + INFO])
    except Exception as exc:  # noqa: BLE001 - never leak ciphertext or key
        raise VaultError("vault: authentication failed (wrong KEY or tampered file)") from exc


# --------------------------------------------------------------------------
# Long-running Git filter process (pkt-line protocol v2)
# --------------------------------------------------------------------------

_FLUSH = object()
_DELIM = object()


def _dbg(message: str) -> None:
    """Opt-in protocol tracing.  Never receives file content or key material."""
    path = os.environ.get("CAVAULT_DEBUG")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(message + "\n")
    except OSError:
        pass


def _read_exact(stream, count: int) -> bytes:
    chunks = []
    remaining = count
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            raise EOFError
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _read_packet(stream):
    header = _read_exact(stream, 4)
    if header == b"0000":
        return _FLUSH
    if header == b"0001":
        return _DELIM
    try:
        length = int(header, 16)
    except ValueError as exc:
        raise VaultError("vault: bad pkt-line header") from exc
    if length < 4:
        raise VaultError("vault: bad pkt-line length")
    return _read_exact(stream, length - 4)


def _write_packet(stream, payload: bytes) -> None:
    stream.write(f"{len(payload) + 4:04x}".encode("ascii") + payload)
    stream.flush()


def _write_flush(stream) -> None:
    stream.write(b"0000")
    stream.flush()


def _read_packet_list(stream) -> list[bytes]:
    packets = []
    while True:
        packet = _read_packet(stream)
        if packet is _FLUSH:
            return packets
        if packet is _DELIM:
            continue
        packets.append(packet)


def _write_content(stream, content: bytes) -> None:
    view = memoryview(content)
    step = 65500
    for offset in range(0, len(view), step):
        _write_packet(stream, bytes(view[offset : offset + step]))
    _write_flush(stream)


def filter_process() -> int:
    """Serve Git's long-running filter protocol on stdin/stdout."""
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    try:
        welcome = _read_packet_list(stdin)
        if not welcome or not welcome[0].startswith(b"git-filter-client"):
            raise VaultError("vault: unexpected filter handshake")
        _write_packet(stdout, b"git-filter-server\n")
        _write_packet(stdout, b"version=2\n")
        _write_flush(stdout)

        # Capability negotiation (mandatory in protocol v2).
        offered = _read_packet_list(stdin)
        _dbg(f"offered capabilities={offered!r}")
        wanted = []
        for packet in offered:
            text = packet.rstrip(b"\n")
            if text in (b"capability=clean", b"capability=smudge"):
                wanted.append(text)
        for packet in wanted:
            _write_packet(stdout, packet + b"\n")
        _write_flush(stdout)
        _dbg("handshake ok")

        while True:
            try:
                headers = _read_packet_list(stdin)
            except EOFError:
                return 0
            if not headers:
                _dbg("empty header list")
                continue
            _dbg(f"raw headers={headers!r}")
            fields = {}
            for header in headers:
                text = header.rstrip(b"\n").decode("utf-8", "surrogateescape")
                if "=" in text:
                    name, value = text.split("=", 1)
                    fields[name] = value
            command = fields.get("command", "")
            _dbg(f"headers command={command!r} path={fields.get('path') or fields.get('pathname')!r}")
            content = b""
            try:
                packets = _read_packet_list(stdin)
                content = b"".join(packets)
            except EOFError:
                return 0
            _dbg(f"content bytes={len(content)}")
            try:
                if command == "clean":
                    result = encrypt(content)
                elif command == "smudge":
                    result = decrypt(content)
                elif command == "list_available_blobs":
                    # Delay is not advertised; answer with the empty list.
                    _write_flush(stdout)
                    _write_packet(stdout, b"status=success\n")
                    _write_flush(stdout)
                    continue
                else:
                    raise VaultError("vault: unsupported filter command")
            except VaultError:
                _write_packet(stdout, b"status=error\n")
                _write_flush(stdout)
                continue
            _write_packet(stdout, b"status=success\n")
            _write_flush(stdout)
            _write_content(stdout, result)
            _write_flush(stdout)  # empty status list
            _dbg(f"responded bytes={len(result)}")
    except BrokenPipeError:
        return 0
    except EOFError:
        return 0


# --------------------------------------------------------------------------
# One-shot filter entry points (fallback when a process filter is unavailable)
# --------------------------------------------------------------------------

def _one_shot(transform) -> int:
    data = sys.stdin.buffer.read()
    sys.stdout.buffer.write(transform(data))
    sys.stdout.buffer.flush()
    return 0


def cmd_clean(_: argparse.Namespace) -> int:
    return _one_shot(encrypt)


def cmd_smudge(_: argparse.Namespace) -> int:
    return _one_shot(decrypt)


# --------------------------------------------------------------------------
# Git plumbing
# --------------------------------------------------------------------------

def _git(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def _repo_root() -> Path:
    out = _git("rev-parse", "--show-toplevel", capture=True).stdout
    return Path(out.decode("utf-8", "surrogateescape").strip())


def _is_plaintext_path(path: str) -> bool:
    return (
        path in PLAINTEXT_FILES
        or path.endswith(".artifacts.json")
        or any(path == prefix or path.startswith(prefix) for prefix in PLAINTEXT_PREFIXES)
    )


def _is_lfs_pointer(data: bytes) -> bool:
    return data.startswith(LFS_POINTER_PREFIX)


def _default_script() -> str:
    return os.environ.get(PROCESS_SCRIPT_ENV) or str(Path(__file__).resolve())


def _configure(script: str) -> None:
    python = sys.executable or "python3"
    command = f'"{python}" "{script}"'
    _git("config", "filter.vault.process", f"{command} filter")
    _git("config", "filter.vault.clean", f"{command} clean")
    _git("config", "filter.vault.smudge", f"{command} smudge")
    _git("config", "filter.vault.required", "true")


def _tracked_paths() -> list[str]:
    raw = _git("ls-files", "-z", capture=True).stdout
    return [
        item.decode("utf-8", "surrogateescape")
        for item in raw.split(b"\0")
        if item
    ]


def _sample_locked_state(paths: list[str]) -> bool | None:
    """Return True when the worktree looks like ciphertext, False plaintext."""
    for rel in paths:
        if _is_plaintext_path(rel):
            continue
        candidate = Path(rel)
        try:
            if candidate.is_symlink() or not candidate.is_file():
                continue
            with candidate.open("rb") as handle:
                head = handle.read(64)
        except OSError:
            continue
        if head.startswith(LFS_POINTER_PREFIX):
            continue  # LFS payloads are not vaulted; never sample them.
        return is_ciphertext(head)
    return None


def _needs_smudge(path: str) -> bool:
    """True only for regular, non-LFS, non-bootstrap files with ciphertext."""
    if _is_plaintext_path(path):
        return False
    candidate = Path(path)
    try:
        if candidate.is_symlink() or not candidate.is_file():
            return False
        with candidate.open("rb") as handle:
            head = handle.read(64)
    except OSError:
        return False
    return not head.startswith(LFS_POINTER_PREFIX)


def _dirty_paths() -> list[bytes]:
    raw = _git("status", "--porcelain", "-uno", "-z", check=False, capture=True).stdout
    return [item for item in raw.split(b"\0") if item]


def _status_path(item: bytes) -> str:
    text = item.decode("utf-8", "surrogateescape")
    return text[3:] if len(text) > 3 else text


def cmd_setup(args: argparse.Namespace) -> int:
    _configure(args.script or _default_script())
    if not args.quiet:
        print("vault: git filters configured (AES-256-SIV)")
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    _repo_root()
    _configure(args.script or _default_script())
    paths = _tracked_paths()
    locked = _sample_locked_state(paths)
    if locked is False:
        if not args.quiet:
            print("vault: working tree already unlocked")
        return 0
    if locked is None:
        if not args.quiet:
            print("vault: no vaulted paths present in this checkout")
        return 0

    dirty = _dirty_paths()
    if dirty and not args.force:
        # A case-insensitive filesystem cannot hold two tracked paths that
        # differ only by case; Git reports one as dirty forever.  Tolerate
        # exactly that, never arbitrary local edits.
        folded = {path.lower() for path in paths}
        collisions_only = all(
            _status_path(item).lower() in folded for item in dirty
        )
        if not collisions_only:
            raise VaultError(
                "vault: refusing to unlock over local changes (use --force to discard)"
            )

    existing = [rel for rel in paths if _needs_smudge(rel)]
    if not existing:
        if not args.quiet:
            print("vault: nothing to unlock")
        return 0
    # Decrypt the index blobs directly.  This avoids Git's smudge fast path,
    # empty-content edge cases, and sparse-checkout interactions entirely.
    import tempfile

    # Use the index blob ids, not :path specs: path-based batch input breaks
    # on names that Git's object-spec parser treats specially.
    index_oids = {}
    raw = _git("ls-files", "-s", "-z", capture=True).stdout
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        parts = meta.split(b" ")
        if len(parts) >= 3:
            index_oids[path.decode("utf-8", "surrogateescape")] = parts[1].decode()
    with tempfile.NamedTemporaryFile("wb", delete=False) as request:
        for rel in existing:
            request.write(index_oids[rel].encode() + b"\n")
        request_path = request.name
    written = 0
    try:
        with open(request_path, "rb") as stdin:
            proc = subprocess.Popen(
                ["git", "cat-file", "--batch"],
                stdin=stdin,
                stdout=subprocess.PIPE,
            )
            assert proc.stdout
            for rel in existing:
                header = proc.stdout.readline().split()
                if len(header) < 3 or header[1] != b"blob":
                    raise VaultError("vault: cannot read index blob during unlock")
                size = int(header[2])
                data = proc.stdout.read(size)
                proc.stdout.read(1)
                if data.startswith(LFS_POINTER_PREFIX):
                    # The worktree holds the materialised LFS object; leaving
                    # the pointer here would silently replace it.
                    continue
                if len(data) == len(MAGIC) + 16:
                    # A 20-byte ciphertext (4-byte magic + 16-byte SIV tag)
                    # can only represent empty plaintext.
                    plain = b""
                else:
                    try:
                        plain = decrypt(data)
                    except VaultError:
                        raise VaultError(
                            f"vault: authentication failed for {rel} "
                            "(wrong KEY or tampered blob)"
                        )
                with open(rel, "wb") as handle:
                    handle.write(plain)
                written += 1
            proc.stdout.close()
            proc.wait()
    finally:
        os.unlink(request_path)
    if not args.quiet:
        print(f"vault: unlocked {written} files (AES-256-SIV)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    paths = _tracked_paths()
    locked = _sample_locked_state(paths)
    state = "unknown" if locked is None else ("locked" if locked else "unlocked")
    print(f"vault: worktree state={state} tracked={len(paths)}")
    return 0


def _iter_head_blobs():
    """Yield (path, mode, oid) for every blob in HEAD."""
    raw = _git("ls-tree", "-r", "-z", "--full-tree", "HEAD", capture=True).stdout
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid = meta.split(b" ")
        if kind == b"blob":
            yield path.decode("utf-8", "surrogateescape"), mode.decode(), oid.decode()


def cmd_verify(args: argparse.Namespace) -> int:
    """Prove that every non-bootstrap blob in HEAD is ciphertext."""
    entries = list(_iter_head_blobs())
    plaintext: list[str] = []
    lfs = 0
    encrypted = 0
    exempt = 0
    batch = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert batch.stdin and batch.stdout
    for path, mode, oid in entries:
        if mode in ("160000", "120000"):
            exempt += 1
            continue
        if _is_plaintext_path(path):
            exempt += 1
            continue
        batch.stdin.write(oid.encode() + b"\n")
        batch.stdin.flush()
        header = batch.stdout.readline().split()
        if len(header) < 3 or header[1] == b"missing":
            raise VaultError("vault: cannot read object during verify")
        size = int(header[2])
        data = batch.stdout.read(size)
        batch.stdout.read(1)  # trailing LF
        if _is_lfs_pointer(data):
            lfs += 1
        elif is_ciphertext(data):
            encrypted += 1
        else:
            plaintext.append(path)
    batch.stdin.close()
    batch.wait()
    print(
        "vault: verify "
        f"encrypted={encrypted} lfs_pointer={lfs} exempt={exempt} plaintext={len(plaintext)}"
    )
    for path in plaintext[: args.max_report]:
        print(f"vault: PLAINTEXT {path}")
    return 1 if plaintext else 0


def cmd_fingerprint(_: argparse.Namespace) -> int:
    digest = hashlib.sha256(_derive_key()).hexdigest()
    print(f"vault: key fingerprint sha256:{digest[:16]}")
    return 0


def cmd_install_key(args: argparse.Namespace) -> int:
    """Persist $KEY to ~/.cavault-key with 0600 for later Git invocations."""
    raw = os.environ.get("KEY")
    if not raw:
        raise VaultError("vault: $KEY is not set; cannot install key file")
    target = Path.home() / KEY_FILE_NAME
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, raw.encode("utf-8"))
    finally:
        os.close(fd)
    os.chmod(target, 0o600)
    if not args.quiet:
        print("vault: key file installed (mode 0600)")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vaultctl", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, help_text):
        item = sub.add_parser(name, help=help_text)
        item.set_defaults(func=func)
        return item

    add("clean", cmd_clean, "one-shot clean filter (stdin -> ciphertext)")
    add("smudge", cmd_smudge, "one-shot smudge filter (stdin -> plaintext)")
    filter_parser = add("filter", lambda _: filter_process(), "long-running Git filter process")
    filter_parser.add_argument("--unused", help=argparse.SUPPRESS)

    setup = add("setup", cmd_setup, "configure repository Git filters")
    setup.add_argument("--script", help="absolute path to this script for filter commands")
    setup.add_argument("--quiet", action="store_true")

    unlock = add("unlock", cmd_unlock, "re-check out the worktree through the smudge filter")
    unlock.add_argument("--script", help="absolute path to this script for filter commands")
    unlock.add_argument("--force", action="store_true", help="discard local worktree changes")
    unlock.add_argument("--quiet", action="store_true")

    status = add("status", cmd_status, "report whether the worktree is locked")
    status.add_argument("--quiet", action="store_true")

    verify = add("verify", cmd_verify, "verify every non-bootstrap HEAD blob is ciphertext")
    verify.add_argument("--max-report", type=int, default=20)

    add("fingerprint", cmd_fingerprint, "print a non-reversible key fingerprint")
    install = add("install-key", cmd_install_key, "write $KEY to ~/.cavault-key (0600)")
    install.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except VaultError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
