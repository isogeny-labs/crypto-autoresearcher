#!/usr/bin/env python3
"""One-shot, write-once memory and ownership gate for a concurrent local lift."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def proc_table():
    rows = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            status = (path / 'status').read_text()
            fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
            ppid = int(fields['PPid'].strip())
            rss_kib = int(fields.get('VmRSS', '0 kB').split()[0])
            cmd = (path / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            rows[int(path.name)] = (ppid, rss_kib * 1024, cmd)
        except (FileNotFoundError, ProcessLookupError, PermissionError, KeyError, ValueError):
            continue
    return rows


def subtree(rows, owner):
    selected = {owner}
    changed = True
    while changed:
        old = len(selected)
        selected.update(pid for pid, (ppid, _, _) in rows.items() if ppid in selected)
        changed = len(selected) != old
    return selected


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise ValueError('MemAvailable missing')


def total_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemTotal:'):
            return int(line.split()[1]) * 1024
    raise ValueError('MemTotal missing')


def gate(plan):
    rows = proc_table()
    owners = []
    for item in plan['concurrent_owners']:
        pid = item['pid']
        if pid not in rows or item['command_contains'] not in rows[pid][2]:
            raise ValueError(f"named owner not live with expected command: {pid}")
        if sha(item['plan']) != item['plan_sha256']:
            raise ValueError(f"owner plan changed: {pid}")
        owner_plan = json.loads(Path(item['plan']).read_text())
        if owner_plan['memory_bytes'] != item['memory_bytes']:
            raise ValueError(f"owner cap changed: {pid}")
        pids = subtree(rows, pid)
        resident = sum(rows[p][1] for p in pids)
        owners.append(dict(pid=pid, pids=sorted(pids), resident_bytes=resident,
                           cap_bytes=item['memory_bytes'],
                           possible_growth_bytes=max(0, item['memory_bytes'] - resident)))
    cap = plan['memory_bytes']
    reserve = plan['reserve_bytes']
    maximum = cap + reserve + sum(x['cap_bytes'] for x in owners)
    if total_bytes() < maximum:
        raise ValueError('declared caps plus reserve exceed MemTotal')
    required = cap + reserve + sum(x['possible_growth_bytes'] for x in owners)
    available = available_bytes()
    if available < required:
        raise ValueError(f'insufficient future-growth headroom: {available} < {required}')
    if Path(plan['output_root']).exists():
        raise ValueError('output root already exists')
    bucket, slash, prefix = plan['checkpoint_prefix'].removeprefix('s3://').partition('/')
    if not plan['checkpoint_prefix'].startswith('s3://') or not slash or not prefix:
        raise ValueError('invalid checkpoint prefix')
    listing = subprocess.run(['aws', 's3api', 'list-objects-v2', '--bucket', bucket,
                              '--prefix', prefix.rstrip('/') + '/', '--max-items', '1',
                              '--region', 'us-east-2', '--output', 'json'],
                             capture_output=True, text=True, check=True)
    if json.loads(listing.stdout).get('Contents'):
        raise ValueError('checkpoint prefix is not empty')
    return dict(status='admitted', checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                owners=owners, mem_available_bytes=available, mem_total_bytes=total_bytes(),
                required_available_bytes=required, declared_total_bytes=maximum,
                checkpoint_prefix=plan['checkpoint_prefix'], checkpoint_prefix_empty=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', required=True, type=Path)
    ap.add_argument('--protocol', required=True, type=Path)
    ap.add_argument('--gate-out', required=True, type=Path)
    args = ap.parse_args()
    plan = json.loads(args.plan.read_text())
    protocol = json.loads(args.protocol.read_text())
    if protocol['freeze']['status'] != 'frozen' or protocol['links']['plan_sha256'] != sha(args.plan):
        raise ValueError('plan is not bound to frozen protocol')
    for path, expected in plan['hashes'].items():
        if sha(path) != expected:
            raise ValueError('pinned file changed: ' + path)
    value = gate(plan)
    value.update(plan_sha256=sha(args.plan), protocol_sha256=protocol['freeze']['protocol_sha256'])
    args.gate_out.parent.mkdir(parents=True, exist_ok=True)
    with args.gate_out.open('x') as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write('\n')
    print(json.dumps(value), flush=True)
    cmd = [plan['python'], str(Path(__file__).parent / 'launch_local_lift.py'),
           '--plan', str(args.plan), '--protocol', str(args.protocol)]
    return subprocess.run(cmd, check=False).returncode


if __name__ == '__main__':
    sys.exit(main())
