#!/usr/bin/env python3
"""One bounded direct W4 trial after the named n51 D5 attempt is terminal."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / 'n51-poly01-direct-w4-rank-plan-002.json'
PROTOCOL = ROOT / 'n51-poly01-direct-w4-rank-protocol-002.json'
MANIFEST = ROOT / 'n51-poly01-direct-w4-runner-manifest-001.json'
FINAL = re.compile(r'^W4_dims(?:\s+\d+){5}\s+W4_one\s+[01]\s+iters\s+\d+\s+ncols\s+\d+$')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_once(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def mem_available():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def budget_readback(reservation):
    account = subprocess.check_output(
        ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
        text=True, timeout=20).strip()
    data = json.loads(subprocess.check_output(
        ['aws', 'budgets', 'describe-budgets', '--account-id', account, '--output', 'json'],
        text=True, timeout=30))
    names = ('isolab-daily-cost-100', 'spot-experiments-daily-25',
             'isolab-monthly-account-cost')
    rows = {}
    for budget in data['Budgets']:
        name = budget['BudgetName']
        if name in names:
            limit = float(budget['BudgetLimit']['Amount'])
            actual = float(budget['CalculatedSpend']['ActualSpend']['Amount'])
            rows[name] = {'limit_usd': limit, 'actual_usd': actual}
            if actual + reservation > limit:
                raise RuntimeError('budget reservation refused: ' + name)
    if set(rows) != set(names):
        raise RuntimeError('required budget readback missing')
    return rows


def parse_stdout(stdout, expected_columns):
    lines = [line for line in stdout.splitlines() if line.startswith('W4_dims')]
    if len(lines) != 1 or not FINAL.fullmatch(lines[0]):
        raise ValueError('exactly one complete W4 line required')
    words = lines[0].split()
    dims = list(map(int, words[1:6]))
    one = int(words[7])
    columns = int(words[11])
    if columns != expected_columns or any(a > b for a, b in zip(dims, dims[1:])):
        raise ValueError('invalid direct W4 dimensions')
    return {'dims': dims, 'rank': dims[-1], 'contains_one': bool(one),
            'columns': columns, 'iterations': int(words[9])}


def run(source_revision):
    plan = json.loads(PLAN.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if (manifest['runner_sha256'] != sha(__file__) or
            manifest['plan_sha256'] != sha(PLAN) or
            manifest['protocol_file_sha256'] != sha(PROTOCOL)):
        raise RuntimeError('runner manifest hash mismatch')
    if plan['schema'] != 'semaev.direct-w4-rank-plan/v2' or plan['status'] != 'frozen_queued_not_launched':
        raise RuntimeError('wrong or unfrozen plan')
    if protocol['freeze']['status'] != 'frozen':
        raise RuntimeError('protocol not frozen')
    if sha(PROTOCOL) != plan['protocol_file_sha256']:
        raise RuntimeError('protocol file changed')
    output = Path(plan['output_root'])
    if not output.is_dir() or (output / 'v2.started.json').exists():
        raise RuntimeError('V2 output root missing or attempt already started')
    if not (output / 'build.finished.json').exists():
        raise RuntimeError('V1 build failure receipt missing')
    root = Path(__file__).parents[2]
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                   text=True, timeout=20).strip()
    branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'],
                                     text=True, timeout=20).strip()
    remote = subprocess.check_output(
        ['git', '-C', str(root), 'ls-remote', 'origin', 'refs/heads/' + branch],
        text=True, timeout=30).split()[0]
    if source_revision != head or remote != head:
        raise RuntimeError('exact runner revision is not published on GitHub')
    fixed = ((root / plan['input_path'], plan['input_sha256']),
             (root / plan['input_check_path'], plan['input_check_sha256']),
             (root / plan['source_path'], plan['source_sha256']),
             (Path(plan['binary_path']), plan['binary_sha256']))
    for path, expected in fixed:
        if sha(path) != expected:
            raise RuntimeError('pinned input/source/binary mismatch: ' + str(path))

    gate = plan['queue_gate']
    d5_root = Path(gate['existing_n51_d5_output_root'])
    d5_result = d5_root / 'result.json'
    if not d5_result.exists() or not (d5_root / 'produce5.finished.json').exists():
        raise RuntimeError('existing D5 attempt lacks terminal receipts')
    status = json.loads(d5_result.read_text())['status']
    if status not in ('projection_kills_one', 'failed'):
        raise RuntimeError('D5 status does not admit direct W4 fallback: ' + status)
    # The named child command must not still be running, even if receipts exist.
    ps = subprocess.check_output(['ps', '-eo', 'args='], text=True, timeout=15)
    if any('quotient_lift_checkpoint' in line and str(d5_root / 'degree5.bin') in line
           for line in ps.splitlines()):
        raise RuntimeError('existing D5 native child is still live')

    ceiling = plan['resource_ceiling']
    deadline = dt.datetime.fromisoformat(ceiling['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=ceiling['producer_timeout_seconds']) > deadline:
        raise RuntimeError('original deadline cannot accommodate full timeout')
    memory = mem_available()
    disk = os.statvfs(output)
    disk_available = disk.f_bavail * disk.f_frsize
    if memory < gate['require_host_available_bytes'] or disk_available < gate['require_host_disk_available_bytes']:
        raise RuntimeError('host memory or disk admission refused')
    budgets = budget_readback(ceiling['usd_reservation'])
    locks = []
    try:
        for path in gate['locks']:
            stream = open(path, 'r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + path)
            locks.append(stream)
        argv = plan['producer_argv']
        if argv[-4:] != [plan['binary_path'], '4', '1', '20000']:
            raise RuntimeError('launch argv differs from frozen plan')
        write_once(output / 'v2.admission.json', {
            'plan_sha256': sha(PLAN), 'protocol_sha256': sha(PROTOCOL),
            'runner_sha256': sha(__file__), 'source_revision': source_revision,
            'd5_status': status, 'd5_result_sha256': sha(d5_result),
            'input_sha256': plan['input_sha256'], 'binary_sha256': plan['binary_sha256'],
            'mem_available_bytes': memory, 'disk_available_bytes': disk_available,
            'budget_readback': budgets, 'admitted_utc': now.isoformat()})
        with (root / plan['input_path']).open('rb') as stdin, \
             (output / 'v2.stdout.txt').open('xb') as stdout, \
             (output / 'v2.stderr.txt').open('xb') as stderr:
            child = subprocess.Popen(argv, stdin=stdin, stdout=stdout, stderr=stderr,
                                     start_new_session=True)
            try:
                write_once(output / 'v2.started.json', {
                    'argv': argv, 'pid': child.pid, 'started_utc':
                    dt.datetime.now(dt.timezone.utc).isoformat(),
                    'input_sha256': plan['input_sha256']})
            except BaseException:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=10)
                raise
            began = time.monotonic()
            timed_out = False
            try:
                code = child.wait(timeout=ceiling['producer_timeout_seconds'] + 20)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    code = child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
        stdout_path = output / 'v2.stdout.txt'
        stderr_path = output / 'v2.stderr.txt'
        finished = {'returncode': code, 'timed_out': timed_out,
                    'elapsed_seconds': time.monotonic() - began,
                    'stdout_sha256': sha(stdout_path), 'stderr_sha256': sha(stderr_path),
                    'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        write_once(output / 'v2.finished.json', finished)
        result = {'schema': 'semaev.direct-w4-rank-result/v2', 'status': 'unknown',
                  'target_rank': plan['reference']['seed_kernel_dimension'],
                  'finished': finished}
        if code == 0 and not timed_out:
            try:
                observed = parse_stdout(stdout_path.read_text(),
                                        plan['reference']['monomial_dimension'])
                result['observed'] = observed
                if observed['contains_one'] or observed['rank'] > result['target_rank']:
                    result['status'] = 'contradiction_requires_diagnosis'
                elif observed['rank'] == result['target_rank']:
                    result['status'] = 'seed_exact_dimension'
                else:
                    result['status'] = 'seed_coarse'
            except ValueError as error:
                result['error'] = str(error)
        write_once(output / 'v2.result.json', result)
        print(json.dumps(result, sort_keys=True))
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    run(args.source_revision)
