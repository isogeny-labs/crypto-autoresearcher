#!/usr/bin/env python3
"""Opt-in bounded-frequency publisher for native seed-phase checkpoints.

The unchanged native producer still saves after every chunk. Unselected seed
snapshots are deleted locally; a later restore replays those chunks from the
latest published state. Phase boundaries and closure rounds are always sent
through the existing verified publisher and export admission hook.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys


MAGIC = 0x315450434c5153


def read_identity(snapshot):
    if snapshot.is_symlink() or not snapshot.is_file():
        raise ValueError('checkpoint is not a regular file')
    with snapshot.open('rb') as stream:
        header = stream.read(176)
    if len(header) != 176:
        raise ValueError('short checkpoint header')
    words = struct.unpack('<14Q', header[:112])
    if words[0] != MAGIC or words[1] != 1 or not words[13] or words[8] > 2:
        raise ValueError('unsupported checkpoint header')
    if snapshot.name != f'checkpoint-{words[13]}.bin':
        raise ValueError('checkpoint sequence/name mismatch')
    work, rank = words[4], words[12]
    if not work or rank > work or snapshot.stat().st_size != 208 + rank * ((work + 63) // 64) * 8:
        raise ValueError('checkpoint shape mismatch')
    return dict(sequence=words[13], phase=words[8],
                seed_sha256=header[112:144].hex(), binary_sha256=header[144:176].hex())


def publish_due(identity, cadence):
    return identity['phase'] != 0 or identity['sequence'] % cadence == 0


def run(snapshot):
    directory = Path(os.environ['SEMAEV_CHECKPOINT_DIR']).resolve(strict=True)
    if snapshot.parent.resolve(strict=True) != directory or not re.fullmatch(r'checkpoint-[1-9][0-9]*\.bin', snapshot.name):
        raise ValueError('checkpoint outside declared directory')
    request_bytes = Path(os.environ['SEMAEV_CHECKPOINT_REQUEST']).read_bytes()
    context = json.loads(Path(os.environ['SEMAEV_CHECKPOINT_CONTEXT']).read_text())
    if hashlib.sha256(request_bytes).hexdigest() != context['request_sha256']:
        raise ValueError('checkpoint request/context mismatch')
    request = json.loads(request_bytes)
    cadence = request.get('checkpoint_publish_every', 1)
    if type(cadence) is not int or not 1 <= cadence <= 1_000_000:
        raise ValueError('invalid checkpoint publication cadence')
    identity = read_identity(snapshot)
    if any(identity[key] != context[key] for key in ('seed_sha256', 'binary_sha256')):
        raise ValueError('checkpoint identity/context mismatch')
    if publish_due(identity, cadence):
        guard = Path(__file__).with_name('checkpoint_export_guard.py')
        subprocess.run([sys.executable, str(guard), str(snapshot)], check=True)
        return
    if os.environ.get('SEMAEV_CHECKPOINT_PRUNE_LOCAL') != '1':
        raise ValueError('bounded cadence requires local pruning')
    snapshot.unlink()
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    print(f'skipped publication of seed checkpoint {identity["sequence"]}', file=sys.stderr, flush=True)


def main():
    if len(sys.argv) != 2:
        raise ValueError('usage: checkpoint_cadence_hook.py SNAPSHOT')
    run(Path(sys.argv[1]))


if __name__ == '__main__':
    main()
