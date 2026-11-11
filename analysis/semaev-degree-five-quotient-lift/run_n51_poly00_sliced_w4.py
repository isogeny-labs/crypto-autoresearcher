#!/usr/bin/env python3
"""Fail-closed one-attempt direct W4 rank runner for n51 polynomial00 slice."""
import argparse
import datetime as dt
from decimal import Decimal
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PLAN = HERE / 'n51-poly00-sliced-direct-w4-rank-plan-001.json'
PROTOCOL = HERE / 'n51-poly00-sliced-direct-w4-rank-protocol-001.json'
ADMISSION = HERE / 'n51-poly00-sliced-direct-w4-rank-admission-001.json'
MAX_AUTHORIZED_MONTHLY_USD = Decimal('1300')
FINAL = re.compile(r'^W4_dims(?:\s+\d+){5}\s+W4_one\s+[01]\s+iters\s+\d+\s+ncols\s+\d+$')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_once(path, record):
    with Path(path).open('x') as output:
        json.dump(record, output, sort_keys=True, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def parse_utc(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('UTC timestamp lacks timezone')
    return parsed.astimezone(dt.timezone.utc)


def committed(path):
    rel = path.resolve().relative_to(REPO)
    stored = subprocess.check_output(['git', '-C', str(REPO), 'show',
                                      'HEAD:' + rel.as_posix()], timeout=30)
    if stored != path.read_bytes():
        raise RuntimeError('file differs from committed HEAD: ' + rel.as_posix())


def published_revision(expected_branch):
    head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                                   text=True, timeout=20).strip()
    branch = subprocess.check_output(['git', '-C', str(REPO), 'branch', '--show-current'],
                                     text=True, timeout=20).strip()
    remote_rows = subprocess.check_output(
        ['git', '-C', str(REPO), 'ls-remote', 'origin', 'refs/heads/' + branch],
        text=True, timeout=30).split()
    if branch != expected_branch or len(remote_rows) < 1 or remote_rows[0] != head:
        raise RuntimeError('exact branch revision not published on GitHub')
    return head


def budget_readback(reservation, other_reservations, expected_monthly_cap):
    account = json.loads(subprocess.check_output(
        ['aws', 'sts', 'get-caller-identity', '--output', 'json'],
        text=True, timeout=30))['Account']
    budgets = json.loads(subprocess.check_output(
        ['aws', 'budgets', 'describe-budgets', '--account-id', account,
         '--output', 'json'], text=True, timeout=30))['Budgets']
    expected = {'isolab-monthly-account-cost': ('MONTHLY', expected_monthly_cap),
                'isolab-daily-cost-100': ('DAILY', Decimal('200')),
                'spot-experiments-daily-25': ('DAILY', Decimal('200'))}
    result = {}
    for budget in budgets:
        name = budget['BudgetName']
        if name not in expected:
            continue
        period, ceiling = expected[name]
        limit = Decimal(budget['BudgetLimit']['Amount'])
        actual = Decimal(budget['CalculatedSpend']['ActualSpend']['Amount'])
        if (budget['BudgetType'] != 'COST' or budget['TimeUnit'] != period or
                budget['BudgetLimit']['Unit'] != 'USD' or
                budget['CalculatedSpend']['ActualSpend']['Unit'] != 'USD' or
                limit != ceiling or actual + reservation + other_reservations > limit):
            raise RuntimeError('Budget admission refused: ' + name)
        result[name] = {'actual_usd': str(actual), 'limit_usd': str(limit),
                        'last_updated_utc': str(budget.get('LastUpdatedTime'))}
    if set(result) != set(expected):
        raise RuntimeError('required Budget readback missing')
    return result


def mem_available():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def parse_stdout(stdout, expected_columns):
    lines = [line for line in stdout.splitlines() if line.startswith('W4_dims')]
    if len(lines) != 1 or not FINAL.fullmatch(lines[0]):
        raise ValueError('exactly one complete W4_dims line required')
    words = lines[0].split()
    dims = list(map(int, words[1:6]))
    one = int(words[7])
    columns = int(words[11])
    if columns != expected_columns or any(a > b for a, b in zip(dims, dims[1:])):
        raise ValueError('invalid W4 rank dimensions')
    return {'dims': dims, 'rank': dims[-1], 'contains_one': bool(one),
            'columns': columns, 'iterations': int(words[9])}


def static_packet():
    plan = json.loads(PLAN.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    ops = json.loads(ADMISSION.read_text())
    if (plan['schema'] != 'semaev.direct-w4-rank-plan/v1' or
            plan['id'] != 'n51-poly00-sliced-direct-w4-rank-001' or
            ops['schema'] != 'semaev.direct-w4-rank-admission/v1' or
            ops['plan_sha256'] != sha(PLAN) or
            ops['protocol_file_sha256'] != sha(PROTOCOL) or
            plan['protocol_file_sha256'] != sha(PROTOCOL) or
            protocol['freeze']['status'] != 'frozen' or
            protocol['freeze']['protocol_sha256'] != plan['protocol_canonical_sha256'] or
            ops['protocol_canonical_sha256'] != plan['protocol_canonical_sha256'] or
            ops['runner_sha256'] != sha(__file__)):
        raise RuntimeError('frozen packet or runner hash mismatch')
    for path in (Path(__file__), PLAN, PROTOCOL, ADMISSION):
        committed(path)
    source_revision = published_revision(ops['branch'])
    if not source_revision:
        raise RuntimeError('missing published revision')
    for pathkey, hashkey in (('input_path', 'input_sha256'),
                             ('input_check_path', 'input_check_sha256'),
                             ('source_path', 'source_sha256'),
                             ('binary_path', 'binary_sha256')):
        path = Path(plan[pathkey])
        if not path.is_absolute():
            path = REPO / path
        if sha(path) != plan[hashkey]:
            raise RuntimeError('pinned file changed: ' + pathkey)
    reference = plan['reference']
    for path, expected in ((HERE / 'validation/n51-poly00-affine-witness-001.json',
                            reference['affine_witness_sha256']),
                           (Path('/home/ec2-user/fall-degree-data-20261029/n50n51-bounded-d4-concurrent-001/fresh-n51-poly-00-D5-cascade01-bounded-D4-001/attempt-001/degree4.bin'),
                            reference['original_d4_map_sha256']),
                           (Path('/home/ec2-user/fall-degree-data-20261029/n50n51-bounded-d4-concurrent-001/fresh-n51-poly-00-D5-cascade01-bounded-D4-001/attempt-001/check4.stdout.txt'),
                            reference['original_d4_checker_stdout_sha256'])):
        if sha(path) != expected:
            raise RuntimeError('original map, checker or witness changed')
    if (reference['sliced_monomial_dimension'] -
            reference['transferred_quotient_dimension'] != reference['target_w4_rank'] or
            plan['producer_argv'] != ['/usr/bin/prlimit', '--as=34359738368', '--',
                                      '/usr/bin/timeout', '14400', plan['binary_path'],
                                      '4', '1', '20000']):
        raise RuntimeError('rank target or launch command changed')
    return plan, ops, source_revision


def preflight(plan, ops, source_revision):
    if (ops['authorization_status'] != 'authorized' or
            not ops.get('authorization_note') or
            not ops.get('external_jobs_reconciliation')):
        raise RuntimeError('owner authorization or EKS job reconciliation pending')
    monthly_cap = Decimal(str(ops['monthly_cap_usd']))
    reservation = Decimal(str(plan['limits']['reserved_usd']))
    other = Decimal(str(ops['other_live_reservations_usd']))
    if (monthly_cap > MAX_AUTHORIZED_MONTHLY_USD or monthly_cap <= 0 or
            reservation != Decimal('15') or other < 0):
        raise RuntimeError('monthly authorization or reservation mismatch')
    external = ops['external_jobs_reconciliation']
    observed = parse_utc(external['observed_utc'])
    now = utcnow()
    if (external['source'] != 'mcp__isolab_eks' or
            external['active_conflicting_jobs'] or
            not dt.timedelta(0) <= now - observed <= dt.timedelta(minutes=10)):
        raise RuntimeError('EKS job reconciliation stale or conflicting')
    root = Path(plan['output_root'])
    if root.exists() or not root.parent.is_dir():
        raise RuntimeError('write-once output root exists or parent missing')
    limit = plan['limits']
    deadline = parse_utc(limit['deadline_utc'])
    if (now + dt.timedelta(seconds=limit['producer_timeout_seconds'] + 60) > deadline or
            limit['max_attempts'] != 1 or limit['automatic_retries'] != 0 or
            limit['checkpoint_policy'] != 'none' or limit['cpu_threads'] != 1 or
            limit['child_address_space_bytes'] != 34359738368):
        raise RuntimeError('deadline or frozen attempt limits refuse launch')
    memory = mem_available()
    fs = os.statvfs(root.parent)
    disk = fs.f_bavail * fs.f_frsize
    if (memory < limit['host_memory_reservation_bytes'] or
            disk < limit['disk_reserve_bytes']):
        raise RuntimeError('host memory or disk admission refused')
    ps = subprocess.check_output(['ps', '-eo', 'args='], text=True, timeout=15)
    if any((plan['binary_path'] in line or 'quotient_lift_checkpoint' in line)
           for line in ps.splitlines()):
        raise RuntimeError('conflicting local native process is live')
    budgets = budget_readback(reservation, other, monthly_cap)
    return {'schema': 'semaev.direct-w4-rank-admission-readback/v1',
            'checked_utc': now.isoformat(), 'source_revision': source_revision,
            'plan_sha256': sha(PLAN), 'protocol_file_sha256': sha(PROTOCOL),
            'runner_sha256': sha(__file__), 'ops_sha256': sha(ADMISSION),
            'input_sha256': plan['input_sha256'], 'binary_sha256': plan['binary_sha256'],
            'memory_available_bytes': memory, 'disk_available_bytes': disk,
            'budget_readback': budgets,
            'external_jobs_reconciliation': external}


def run(launch):
    plan, ops, revision = static_packet()
    admission = preflight(plan, ops, revision)
    if not launch:
        print(json.dumps(admission, sort_keys=True))
        return
    locks = []
    try:
        for path in ops['locks']:
            stream = Path(path).open('r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + path)
            locks.append(stream)
        admission = preflight(plan, ops, revision)
        root = Path(plan['output_root'])
        root.mkdir(mode=0o700)
        write_once(root / 'admission.json', admission)
        with (REPO / plan['input_path']).open('rb') as stdin, \
             (root / 'stdout.txt').open('xb') as stdout, \
             (root / 'stderr.txt').open('xb') as stderr:
            child = subprocess.Popen(plan['producer_argv'], stdin=stdin,
                                     stdout=stdout, stderr=stderr,
                                     start_new_session=True)
            try:
                write_once(root / 'started.json', {
                    'argv': plan['producer_argv'], 'pid': child.pid,
                    'started_utc': utcnow().isoformat(),
                    'input_sha256': plan['input_sha256']})
            except BaseException:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=10)
                raise
            began = time.monotonic()
            timed_out = False
            try:
                code = child.wait(timeout=plan['limits']['producer_timeout_seconds'] + 20)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    code = child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
        finished = {'returncode': code, 'timed_out': timed_out,
                    'elapsed_seconds': time.monotonic() - began,
                    'stdout_sha256': sha(root / 'stdout.txt'),
                    'stderr_sha256': sha(root / 'stderr.txt'),
                    'finished_utc': utcnow().isoformat()}
        write_once(root / 'finished.json', finished)
        result = {'schema': 'semaev.direct-w4-rank-result/v1', 'status': 'unknown',
                  'target_rank': plan['reference']['target_w4_rank'],
                  'finished': finished}
        if code == 0 and not timed_out:
            try:
                observed = parse_stdout((root / 'stdout.txt').read_text(),
                                        plan['reference']['sliced_monomial_dimension'])
                result['observed'] = observed
                if observed['contains_one'] or observed['rank'] > result['target_rank']:
                    result['status'] = 'contradiction_requires_diagnosis'
                elif observed['rank'] == result['target_rank']:
                    result['status'] = 'seed_exact_dimension'
                else:
                    result['status'] = 'seed_coarse'
            except ValueError as error:
                result['error'] = str(error)
        write_once(root / 'result.json', result)
        print(json.dumps(result, sort_keys=True))
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch', action='store_true',
                        help='Start the single attempt only after all admission gates')
    args = parser.parse_args()
    try:
        run(args.launch)
    except (OSError, KeyError, TypeError, ValueError, RuntimeError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parser.exit(1, 'REFUSED: %s\n' % error)


if __name__ == '__main__':
    main()
