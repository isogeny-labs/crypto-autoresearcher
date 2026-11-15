"""Read committed plaintext through the research vault, never the worktree.

Object IDs and revisions remain the source of truth. Plain historical blobs
pass through; authenticated ciphertext is decrypted before any text decoding.
Batch input uses a temporary file so large responses cannot deadlock a pipe.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Iterator

from .vaultctl import decrypt


def read_blob(repo: str | Path, spec: str, *, missing_ok: bool = False) -> bytes | None:
    result = subprocess.run(['git', '-C', str(repo), 'cat-file', 'blob', spec], capture_output=True)
    if result.returncode:
        if missing_ok:
            return None
        raise subprocess.CalledProcessError(result.returncode, result.args, stderr=result.stderr)
    return decrypt(result.stdout)


def read_blobs(repo: str | Path, oids: Iterable[str]) -> Iterator[bytes]:
    """Yield authenticated contents for full blob IDs in their supplied order."""
    ids = list(oids)
    if not ids:
        return
    if any(re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}', oid) is None for oid in ids):
        raise ValueError('batch reads require full object IDs')
    with tempfile.TemporaryFile() as request, tempfile.TemporaryFile() as errors:
        request.write(('\n'.join(ids) + '\n').encode('ascii'))
        request.seek(0)
        with subprocess.Popen(['git', '-C', str(repo), 'cat-file', '--batch'],
                              stdin=request, stdout=subprocess.PIPE, stderr=errors) as proc:
            assert proc.stdout is not None
            try:
                for oid in ids:
                    header = proc.stdout.readline().split()
                    if len(header) != 3 or header[0].decode('ascii') != oid.lower() or header[1] != b'blob':
                        raise ValueError('Git batch response is not the requested blob')
                    size = int(header[2])
                    data = proc.stdout.read(size)
                    if len(data) != size or proc.stdout.read(1) != b'\n':
                        raise ValueError('truncated Git batch response')
                    yield decrypt(data)
            finally:
                # Early consumer termination must also release the Git process.
                proc.stdout.close()
            code = proc.wait()
            if code:
                errors.seek(0)
                raise subprocess.CalledProcessError(code, proc.args, stderr=errors.read())


def read_text(repo: str | Path, ref: str, path: str) -> str | None:
    """UTF-8 committed content; a missing path contributes no invented data."""
    data = read_blob(repo, f"{ref}:{path}", missing_ok=True)
    return None if data is None else data.decode("utf-8")
