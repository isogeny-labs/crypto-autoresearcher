#!/usr/bin/env python3
"""Guarded single-owner launch of the frozen 16-input bounded D4 continuation."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

GIB = 1 << 30


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--protocol', type=Path, required=True)
    p.add_argument('--gate-dir', type=Path, required=True)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    protocol = json.loads(args.protocol.read_text())
    if protocol['freeze']['status'] != 'frozen' or sha(args.plan) != protocol['links']['plan_sha256']:
        raise ValueError('plan is not bound to a frozen protocol')
    if len(plan['items']) != 16 or plan['selection']['scope'].find('All 16') < 0:
        raise ValueError('full retained cohort missing')
    output = Path(plan['selection']['output_root'])
    if output.exists():
        raise FileExistsError('output root already exists: ' + str(output))
    if plan['memory_bytes'] != 28991029248 or plan['reserve_bytes'] != 2147483648:
        raise ValueError('unexpected memory envelope')
    args.gate_dir.mkdir(parents=True, exist_ok=True)
    lock_path = args.gate_dir / 'owner.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if output.exists():
            raise FileExistsError('output root appeared after lock')
        available = available_bytes()
        required = 64 * GIB
        if available < required:
            raise RuntimeError(f'MemAvailable {available} below concurrent guard {required}')
        argv = [sys.executable,
                '/home/ec2-user/crypto-autoresearcher-fall-degree-submission-20261029/analysis/semaev-degree-five-quotient-lift/run_retained_bounded_d4.py',
                '--plan', str(args.plan), '--runtime', '/home/ec2-user/fall-degree-runtime-20261029',
                '--dossier', '/home/ec2-user/crypto-autoresearcher-fall-degree-submission-20261029/analysis/semaev-m2-last-fall-degree',
                '--binary', '/home/ec2-user/fall-degree-runtime-20261029/bin/quotient_lift_checkpoint_bounded',
                '--out', str(output), '--memory', str(plan['memory_bytes']),
                '--chunk', str(plan['chunk_rows']), '--timeout', '21600']
        gate = {'schema': 'semaev.concurrent-d4-launch-gate/v1',
                'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'plan_sha256': sha(args.plan), 'protocol_sha256': sha(args.protocol),
                'available_bytes': available, 'required_bytes': required,
                'output_root_absent': True, 'items': len(plan['items']),
                'binary_sha256': sha(Path(plan['binary'])), 'argv': argv,
                'scope': 'Operational admission only; no D4 mathematical result'}
        if gate['binary_sha256'] != plan['binary_sha256']:
            raise ValueError('binary changed before launch')
        gate_path = args.gate_dir / 'launch-gate.json'
        with gate_path.open('x') as destination:
            json.dump(gate, destination, indent=2, sort_keys=True)
            destination.write('\n')
        print(json.dumps({'admitted': True, 'gate': str(gate_path), 'items': len(plan['items'])}), flush=True)
        return subprocess.run(argv, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
