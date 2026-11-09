#!/usr/bin/env python3
"""Execute the frozen independent n47 x1 count once and retain every stage."""
import argparse
import hashlib
import json
import os
import resource
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def rusage():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'user_seconds': usage.ru_utime, 'system_seconds': usage.ru_stime,
            'max_rss_kib': usage.ru_maxrss}


def run_stage(stage, argv, root, cwd):
    out = root / (stage + '.stdout')
    err = root / (stage + '.stderr')
    start = utc_now()
    before = rusage()
    with out.open('xb') as stdout, err.open('xb') as stderr:
        try:
            exit_code = subprocess.call(argv, cwd=str(cwd), stdout=stdout, stderr=stderr)
        except OSError as exc:
            stderr.write((str(exc) + '\n').encode())
            exit_code = 127
    after = rusage()
    return {'argv': argv, 'exit_code': exit_code, 'start_utc': start,
            'finish_utc': utc_now(), 'stdout_path': out.name,
            'stdout_sha256': digest(out), 'stderr_path': err.name,
            'stderr_sha256': digest(err), 'rusage_children_before': before,
            'rusage_children_after': after}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('repository', type=Path)
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    repo = args.repository.resolve()
    plan = json.loads(plan_path.read_text())
    limits = plan['limits']
    root = Path(plan['output_root'])
    if plan['id'] != 'n47-rand00-x1-count-local-002' or limits['max_attempts'] != 1 or limits['automatic_retries'] != 0:
        raise SystemExit('unexpected plan or attempt policy')
    if datetime.now(timezone.utc) >= datetime.fromisoformat(limits['deadline_utc'].replace('Z', '+00:00')):
        raise SystemExit('original deadline expired')
    for path, expected in ((repo / plan['source_path'], plan['source_sha256']),
                           (repo / plan['named_plan_path'], plan['named_plan_sha256']),
                           (Path(plan['original_input_system_path']), plan['input_sys_sha256'])):
        if digest(path) != expected:
            raise SystemExit('pinned input mismatch: ' + str(path))
    # mkdir is exclusive: an existing root is evidence of an earlier attempt.
    root.mkdir(mode=0o700)
    receipt = {'schema': 'semaev.n47-rand00-x1-count-run/v1',
               'plan_sha256': digest(plan_path), 'source_sha256': plan['source_sha256'],
               'attempts': 1, 'retries': 0, 'hostname': socket.gethostname(),
               'pid': os.getpid(), 'start_utc': utc_now(),
               'usd_reserved': limits['usd_reservation'],
               'charged_cost_status': 'pending_aws_billing', 'controls': []}
    start_monotonic = time.monotonic()
    try:
        receipt['build'] = run_stage('build', plan['build_launch_argv'], root, repo)
        if receipt['build']['exit_code'] != 0:
            return 1
        receipt['binary_sha256'] = digest(Path(plan['build_argv'][-1]))
        for control in plan['controls']:
            stage = run_stage(control['id'], control['launch_argv'], root, repo)
            stage['id'] = control['id']
            receipt['controls'].append(stage)
            if stage['exit_code'] != 0 or (root / stage['stdout_path']).read_bytes() != ('%d\n' % control['expected_exact_count']).encode() or (root / stage['stderr_path']).stat().st_size:
                return 2
        if time.monotonic() - start_monotonic >= limits['total_watchdog_seconds'] - limits['target_timeout_seconds']:
            receipt['stop_reason'] = 'watchdog_before_target'
            return 3
        receipt['target'] = run_stage('target', plan['target_launch_argv'], root, repo)
        if receipt['target']['exit_code'] != 0:
            return 4
        return 0
    finally:
        receipt['finish_utc'] = utc_now()
        receipt['elapsed_seconds'] = time.monotonic() - start_monotonic
        receipt['status'] = ('target_complete' if receipt.get('target', {}).get('exit_code') == 0 else
                             'stopped_or_failed')
        receipt_path = root / 'receipt.json'
        with receipt_path.open('x') as stream:
            json.dump(receipt, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({'receipt': str(receipt_path), 'status': receipt['status'],
                          'elapsed_seconds': receipt['elapsed_seconds']}, sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())
