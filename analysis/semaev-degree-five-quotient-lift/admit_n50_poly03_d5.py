#!/usr/bin/env python3
"""Fail-closed operational admission for the frozen n50 polynomial03 D5 run."""

import argparse
import datetime as dt
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            value.update(block)
    return value.hexdigest()


def aws_json(*args):
    return json.loads(subprocess.check_output(
        ['aws', *args, '--output', 'json'], text=True, timeout=30))


def budget_readback(reservation, monthly_cap):
    account = aws_json('sts', 'get-caller-identity')['Account']
    rows = aws_json('budgets', 'describe-budgets', '--account-id', account)['Budgets']
    names = {'isolab-daily-cost-100', 'spot-experiments-daily-25',
             'isolab-monthly-account-cost'}
    seen = {}
    for item in rows:
        name = item['BudgetName']
        if name not in names:
            continue
        actual = Decimal(item['CalculatedSpend']['ActualSpend']['Amount'])
        limit = Decimal(item['BudgetLimit']['Amount'])
        expected_time_unit = 'MONTHLY' if name == 'isolab-monthly-account-cost' else 'DAILY'
        if item['BudgetType'] != 'COST' or item['TimeUnit'] != expected_time_unit or \
                item['BudgetLimit']['Unit'] != 'USD' or \
                item['CalculatedSpend']['ActualSpend']['Unit'] != 'USD':
            raise RuntimeError('budget type, period or currency differs: ' + name)
        seen[name] = {'actual_usd': str(actual), 'limit_usd': str(limit),
                      'last_updated_utc': str(item.get('LastUpdatedTime'))}
        if actual + reservation > limit:
            raise RuntimeError('account budget headroom refused: ' + name)
        if name == 'isolab-monthly-account-cost':
            if limit != monthly_cap or actual + reservation > monthly_cap:
                raise RuntimeError('owner monthly ceiling refused')
        elif limit != Decimal('200'):
            raise RuntimeError('shared daily ceiling differs: ' + name)
    if set(seen) != names:
        raise RuntimeError('required AWS Budget readback missing')
    return seen


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def git_head(repo, branch):
    head = subprocess.check_output(
        ['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True, timeout=20).strip()
    current = subprocess.check_output(
        ['git', '-C', str(repo), 'branch', '--show-current'],
        text=True, timeout=20).strip()
    if current != branch:
        raise RuntimeError('wrong checkout branch')
    remote = subprocess.check_output(
        ['git', '-C', str(repo), 'ls-remote', 'origin', 'refs/heads/' + branch],
        text=True, timeout=30).split()[0]
    if remote != head:
        raise RuntimeError('exact source revision is not on GitHub')
    return head


def require_committed_bytes(repo, paths):
    for path in paths:
        absolute = Path(path).resolve()
        try:
            relative = absolute.relative_to(repo.resolve())
        except ValueError:
            raise RuntimeError('launch file is outside repository: ' + str(path))
        committed = subprocess.check_output(
            ['git', '-C', str(repo), 'show', 'HEAD:' + relative.as_posix()],
            timeout=30)
        if committed != absolute.read_bytes():
            raise RuntimeError('launch file is not the pushed revision: ' + str(relative))


def admission(plan_path, protocol_path, operations_path, source_revision):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    operations = json.loads(operations_path.read_text())
    if operations['schema'] != 'semaev.n50-poly03-d5-admission/v1':
        raise RuntimeError('wrong operational schema')
    if operations['authorization_status'] != 'authorized' or not operations['authorization_note']:
        raise RuntimeError('owner spending authorization is not recorded')
    if plan['id'] != operations['run_id'] or plan['record']['name'] != 'fresh-n50-poly-03':
        raise RuntimeError('wrong scientific target')
    if digest(plan_path) != operations['plan_sha256'] or \
            digest(protocol_path) != operations['protocol_sha256'] or \
            protocol['links']['plan_sha256'] != operations['plan_sha256'] or \
            protocol['freeze']['status'] != 'frozen':
        raise RuntimeError('scientific plan or frozen protocol changed')
    repo = Path(__file__).resolve().parents[2]
    runner = repo / operations['runner_path']
    if digest(runner) != operations['runner_sha256'] or \
            digest(__file__) != operations['admission_source_sha256']:
        raise RuntimeError('launch source changed')
    head = git_head(repo, operations['branch'])
    if source_revision != head:
        raise RuntimeError('source revision argument changed')
    require_committed_bytes(repo, (plan_path, protocol_path, operations_path,
                                   runner, Path(__file__)))
    root = Path(plan['output_root'])
    if root.exists():
        raise RuntimeError('write-once output root already exists')
    deadline = dt.datetime.fromisoformat(
        operations['deadline_utc'].replace('Z', '+00:00'))
    stages = 2 * plan['check_timeout_seconds'] + plan['count_timeout_seconds'] \
        + plan['produce_timeout_seconds']
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=stages + operations['admission_margin_seconds']) > deadline:
        raise RuntimeError('absolute deadline cannot contain all stage watchdogs')
    memory = available_bytes()
    if memory < plan['memory_bytes'] + plan['reserve_bytes']:
        raise RuntimeError('host memory admission refused')
    stat = os.statvfs(root.parent)
    disk_free = stat.f_bavail * stat.f_frsize
    if disk_free < plan['disk_capacity_bytes'] + plan['disk_reserve_bytes']:
        raise RuntimeError('host disk admission refused')
    locks = []
    try:
        for name in plan['locks']:
            stream = Path(name).open('r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + name)
            locks.append(stream)
        reservation = Decimal(str(operations['reserved_usd']))
        cap = Decimal(str(operations['monthly_cap_usd']))
        if reservation != Decimal('20') or cap != Decimal('1500'):
            raise RuntimeError('operational dollar bounds changed')
        budgets = budget_readback(reservation, cap)
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()
    return {'schema': 'semaev.n50-poly03-d5-admission-readback/v1',
            'run_id': plan['id'], 'source_revision': head,
            'plan_sha256': digest(plan_path),
            'protocol_sha256': digest(protocol_path),
            'operations_sha256': digest(operations_path),
            'checked_utc': now.isoformat(), 'deadline_utc': operations['deadline_utc'],
            'stage_watchdogs_seconds': stages, 'memory_available_bytes': memory,
            'disk_free_bytes': disk_free, 'budget_readback': budgets,
            'reserved_usd': str(reservation)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--operations', required=True, type=Path)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    try:
        result = admission(args.plan, args.protocol, args.operations,
                           args.source_revision)
    except Exception as error:
        print('ADMISSION_REFUSED: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True), flush=True)
    if not args.launch:
        return 0
    output = Path(json.loads(args.plan.read_text())['output_root'])
    receipt = output.parent / (output.name + '.prelaunch-admission.json')
    with receipt.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    runner = Path(__file__).resolve().parents[2] / \
        json.loads(args.operations.read_text())['runner_path']
    return subprocess.call([sys.executable, str(runner), '--plan', str(args.plan),
                            '--protocol', str(args.protocol)])


if __name__ == '__main__':
    raise SystemExit(main())
