#!/usr/bin/env python3
"""Fail-closed, one-attempt runner for the frozen retained n50/n51 W3 panel."""

import argparse
import datetime as dt
from decimal import Decimal
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write_new(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with Path(path).open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def write_bytes_new(path, data):
    with Path(path).open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def committed(repo, path):
    relative = Path(path).resolve().relative_to(repo)
    prior = subprocess.check_output(
        ['git', '-C', str(repo), 'show', 'HEAD:' + relative.as_posix()], timeout=30)
    if prior != Path(path).read_bytes():
        raise RuntimeError('file differs from published HEAD: ' + str(relative))


def budget_readback(reservation, monthly_cap):
    account = json.loads(subprocess.check_output(
        ['aws', 'sts', 'get-caller-identity', '--output', 'json'],
        text=True, timeout=30))['Account']
    budgets = json.loads(subprocess.check_output(
        ['aws', 'budgets', 'describe-budgets', '--account-id', account,
         '--output', 'json'], text=True, timeout=30))['Budgets']
    required = {'isolab-monthly-account-cost': ('MONTHLY', monthly_cap),
                'isolab-daily-cost-100': ('DAILY', Decimal('200')),
                'spot-experiments-daily-25': ('DAILY', Decimal('200'))}
    rows = {}
    for budget in budgets:
        name = budget['BudgetName']
        if name not in required:
            continue
        period, ceiling = required[name]
        actual = Decimal(budget['CalculatedSpend']['ActualSpend']['Amount'])
        live_limit = Decimal(budget['BudgetLimit']['Amount'])
        if (budget['BudgetType'] != 'COST' or budget['TimeUnit'] != period or
                budget['BudgetLimit']['Unit'] != 'USD' or
                budget['CalculatedSpend']['ActualSpend']['Unit'] != 'USD' or
                live_limit != ceiling or actual + reservation > live_limit):
            raise RuntimeError('Budget admission refused: ' + name)
        rows[name] = {'actual_usd': str(actual), 'limit_usd': str(live_limit),
                      'last_updated_utc': str(budget.get('LastUpdatedTime'))}
    if set(rows) != set(required):
        raise RuntimeError('required Budget readback missing')
    return rows


def available_memory():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def limit_child(memory, cpu):
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))


def check_admission(plan_path, protocol_path, ops_path):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    ops = json.loads(ops_path.read_text())
    if (plan['schema'] != 'semaev.retained-m2-w3-rank-panel-plan/v1' or
            plan['id'] != 'n50n51-w3-rank-panel-001' or
            ops['schema'] != 'semaev.retained-m2-w3-panel-admission/v1'):
        raise RuntimeError('wrong frozen panel identity')
    if (ops['authorization_status'] != 'authorized' or
            not ops.get('authorization_note') or
            not ops.get('external_jobs_reconciliation')):
        raise RuntimeError('owner spending authorization or job reconciliation is pending')
    if (sha(plan_path) != ops['plan_sha256'] or
            sha(protocol_path) != ops['protocol_file_sha256'] or
            protocol['freeze']['status'] != 'frozen' or
            protocol['freeze']['protocol_sha256'] != ops['frozen_protocol_sha256'] or
            protocol['links']['plan_sha256'] != ops['plan_sha256']):
        raise RuntimeError('frozen scientific packet changed')
    here = Path(__file__).resolve()
    repo = here.parents[2]
    source_plan = here.parent / plan['source_plan']
    verifier = here.parent / plan['verifier']
    audit = here.parent / 'validation/n50n51-w3-equation-audit-001/stdout.json'
    if (sha(here) != ops['runner_sha256'] or
            sha(source_plan) != plan['source_plan_sha256'] or
            sha(verifier) != plan['verifier_sha256'] or
            sha(audit) != ops['equation_audit_sha256']):
        raise RuntimeError('pinned source, input or equation audit changed')
    for path in (here, plan_path, protocol_path, ops_path, source_plan, verifier,
                 audit):
        committed(repo, path)
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                   text=True, timeout=20).strip()
    branch = subprocess.check_output(['git', '-C', str(repo), 'branch',
                                      '--show-current'], text=True, timeout=20).strip()
    remote = subprocess.check_output(
        ['git', '-C', str(repo), 'ls-remote', 'origin', 'refs/heads/' + branch],
        text=True, timeout=30).split()[0]
    if branch != ops['branch'] or head != remote:
        raise RuntimeError('exact checkout revision is not published on GitHub')
    root = Path(ops['output_root'])
    if root.exists() or not root.parent.is_dir():
        raise RuntimeError('write-once output root exists or parent is missing')
    limits = plan['limits']
    deadline = dt.datetime.fromisoformat(limits['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=limits['total_wall_seconds'] + 60) > deadline:
        raise RuntimeError('absolute deadline cannot contain the attempt')
    if (Decimal(str(ops['reserved_usd'])) != Decimal('1') or
            Decimal(str(limits['max_total_cost_usd'])) != Decimal('1') or
            limits['per_item_wall_seconds'] != 60 or
            limits['per_item_cpu_seconds'] != 60 or
            limits['per_item_address_space_bytes'] != 4294967296 or
            limits['total_wall_seconds'] != 600 or
            limits['max_concurrent_items'] != 1 or
            limits['max_total_attempts_per_item'] != 1):
        raise RuntimeError('operational limits differ from frozen plan')
    memory = available_memory()
    if memory < limits['per_item_address_space_bytes'] + 1073741824:
        raise RuntimeError('host memory admission refused')
    fs = os.statvfs(root.parent)
    disk = fs.f_bavail * fs.f_frsize
    if disk < 1073741824:
        raise RuntimeError('host disk admission refused')
    items = json.loads(source_plan.read_text())['items']
    by_id = {item['id']: item for item in items}
    if (len(items) != 16 or len(by_id) != 16 or
            set(plan['execution_order']) != set(by_id) or
            plan['execution_order'] != plan['controls'] + plan['new_rank_items']):
        raise RuntimeError('fixed item inventory changed')
    for item in items:
        if sha(item['seed_path']) != item['seed_sha256']:
            raise RuntimeError('retained D3 seed changed: ' + item['id'])
    audit_rows = json.loads(audit.read_text())['rows']
    masks = {row['item_id']: row['equation_masks_sha256'] for row in audit_rows}
    if len(masks) != 16 or set(masks) != set(by_id):
        raise RuntimeError('equation audit inventory changed')
    budgets = budget_readback(Decimal('1'), Decimal(str(ops['monthly_cap_usd'])))
    return plan, ops, source_plan, verifier, by_id, masks, root, deadline, {
        'schema': 'semaev.retained-m2-w3-panel-admission-readback/v1',
        'checked_utc': now.isoformat(), 'source_revision': head,
        'plan_sha256': sha(plan_path), 'protocol_sha256': sha(protocol_path),
        'operations_sha256': sha(ops_path), 'memory_available_bytes': memory,
        'disk_free_bytes': disk, 'reserved_usd': '1', 'budget_readback': budgets,
        'external_jobs_reconciliation': ops['external_jobs_reconciliation']}


def run(plan_path, protocol_path, ops_path, launch):
    plan, ops, source_plan, verifier, by_id, masks, root, deadline, admission = \
        check_admission(plan_path, protocol_path, ops_path)
    if not launch:
        print(json.dumps(admission, sort_keys=True))
        return 0
    locks = []
    try:
        for lock in ops['locks']:
            stream = Path(lock).open('r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + lock)
            locks.append(stream)
        if root.exists():
            raise RuntimeError('write-once output root appeared after admission')
        admission['budget_readback'] = budget_readback(
            Decimal('1'), Decimal(str(ops['monthly_cap_usd'])))
        if available_memory() < plan['limits']['per_item_address_space_bytes'] + 1073741824:
            raise RuntimeError('host memory changed after admission')
        root.mkdir(mode=0o700)
        write_new(root / 'admission.json', admission)
        began = time.monotonic()
        rows = []
        controls_ok = True
        for item_id in plan['execution_order']:
            elapsed = time.monotonic() - began
            remaining = min(plan['limits']['total_wall_seconds'] - elapsed,
                            (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds())
            if remaining <= 0 or (item_id not in plan['controls'] and not controls_ok):
                rows.append({'item_id': item_id, 'status': 'unrun'})
                continue
            index = len(rows)
            tag = 'item-%02d' % index
            args = [sys.executable, str(verifier), '--plan', str(source_plan),
                    '--item-id', item_id]
            write_new(root / (tag + '.started.json'), {
                'item_id': item_id, 'argv': args,
                'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'verifier_sha256': plan['verifier_sha256'],
                'source_plan_sha256': plan['source_plan_sha256']})
            began_item = time.monotonic()
            timeout = min(plan['limits']['per_item_wall_seconds'], remaining)
            status = 'incomplete'
            stdout = b''
            stderr = b''
            exit_code = None
            try:
                result = subprocess.run(args, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=timeout,
                    env={**os.environ, 'PYTHONHASHSEED': '0'},
                    preexec_fn=lambda: limit_child(
                        plan['limits']['per_item_address_space_bytes'],
                        plan['limits']['per_item_cpu_seconds']))
                stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
                if exit_code == 0:
                    data = json.loads(stdout)
                    item = by_id[item_id]
                    if (data['item_id'] != item_id or
                            data['plan_sha256'] != plan['source_plan_sha256'] or
                            data['equation_masks_sha256'] != masks[item_id] or
                            data['expected_seed_codimension'] != item['seed_codimension'] or
                            data['named_input'] != item['record']['name'] or
                            data['columns'] != sum(math.comb(2 * item['record']['k'], j)
                                                   for j in range(4)) or
                            data['rank'] < 0 or data['rank'] > data['columns'] or
                            data['quotient_dimension'] != data['columns'] - data['rank'] or
                            data['contains_one'] or
                            data['quotient_matches_seed'] !=
                            (data['quotient_dimension'] == item['seed_codimension'])):
                        status = 'mismatch'
                    else:
                        status = 'exact_seed_verified' if data['quotient_matches_seed'] \
                            else 'seed_dimension_mismatch'
                    if item_id in plan['controls']:
                        expected = {'fresh-n50-poly-03': 8130,
                                    'fresh-n51-poly-00': 10970}[item['record']['name']]
                        controls_ok &= data['rank'] == expected and status == 'exact_seed_verified'
                else:
                    status = 'nonzero_exit'
            except subprocess.TimeoutExpired as error:
                stdout, stderr = error.stdout or b'', error.stderr or b''
                status = 'timeout'
            except Exception as error:
                stderr += ('\nrunner validation error: ' + str(error)).encode()
                status = 'mismatch'
            if item_id in plan['controls'] and status != 'exact_seed_verified':
                controls_ok = False
            write_bytes_new(root / (tag + '.stdout.json'), stdout)
            write_bytes_new(root / (tag + '.stderr.txt'), stderr)
            row = {'item_id': item_id, 'status': status, 'exit_code': exit_code,
                   'elapsed_seconds': round(time.monotonic() - began_item, 3),
                   'started_sha256': sha(root / (tag + '.started.json')),
                   'stdout_sha256': sha(root / (tag + '.stdout.json')),
                   'stderr_sha256': sha(root / (tag + '.stderr.txt'))}
            write_new(root / (tag + '.finished.json'), row)
            rows.append(row)
        summary = {'schema': 'semaev.retained-m2-w3-panel-result/v1',
                   'plan_sha256': sha(plan_path), 'protocol_sha256': sha(protocol_path),
                   'operations_sha256': sha(ops_path), 'rows': rows,
                   'controls_ok': controls_ok,
                   'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        write_new(root / 'result.json', summary)
        print(json.dumps(summary, sort_keys=True))
        return 0 if controls_ok and all(row['status'] in (
            'exact_seed_verified', 'seed_dimension_mismatch') for row in rows) else 1
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--protocol', required=True, type=Path)
    parser.add_argument('--operations', required=True, type=Path)
    parser.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.plan, args.protocol, args.operations,
                             args.launch))
    except Exception as error:
        print('ADMISSION_REFUSED: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
