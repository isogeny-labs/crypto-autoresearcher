#!/usr/bin/env python3
"""One bounded original-system D5 lift, queued behind the n51 W4 trial."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


ROOT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def mem_available():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable unavailable')


def budgets(reservation):
    account = subprocess.check_output(
        ['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'],
        text=True, timeout=20).strip()
    data = json.loads(subprocess.check_output(
        ['aws', 'budgets', 'describe-budgets', '--account-id', account, '--output', 'json'],
        text=True, timeout=30))
    names = {'isolab-daily-cost-100', 'spot-experiments-daily-25',
             'isolab-monthly-account-cost'}
    result = {}
    for item in data['Budgets']:
        if item['BudgetName'] in names:
            actual = float(item['CalculatedSpend']['ActualSpend']['Amount'])
            limit = float(item['BudgetLimit']['Amount'])
            result[item['BudgetName']] = {'actual_usd': actual, 'limit_usd': limit}
            if actual + reservation > limit:
                raise RuntimeError('budget headroom refused: ' + item['BudgetName'])
    if set(result) != names:
        raise RuntimeError('required budget readback missing')
    return result


def run_stage(root, label, argv, stdin_path, cap, timeout, env):
    stdout_path = root / (label + '.stdout.txt')
    stderr_path = root / (label + '.stderr.txt')
    command = ['/usr/bin/prlimit', '--as=' + str(cap), '--'] + list(map(str, argv))
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        stdin = Path(stdin_path).open('rb') if stdin_path else subprocess.DEVNULL
        try:
            child = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=stderr,
                                     env=env, start_new_session=True)
            try:
                save(root / (label + '.started.json'), {'argv': command, 'pid': child.pid,
                    'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'address_space_bytes': cap})
            except BaseException:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=10)
                raise
            began = time.monotonic()
            expired = False
            try:
                code = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                expired = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    code = child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
        finally:
            if stdin_path:
                stdin.close()
    receipt = {'returncode': code, 'timed_out': expired,
               'elapsed_seconds': time.monotonic() - began,
               'stdout_sha256': sha(stdout_path), 'stderr_sha256': sha(stderr_path),
               'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
    save(root / (label + '.finished.json'), receipt)
    if code or expired:
        raise RuntimeError(label + ' failed or timed out')
    return stdout_path.read_text()


def run(plan_path, protocol_path, source_revision):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    if plan['schema'] != 'semaev.original-d5-local-plan/v1':
        raise RuntimeError('wrong plan schema')
    if protocol['freeze']['status'] != 'frozen' or protocol['links']['plan_sha256'] != sha(plan_path):
        raise RuntimeError('plan is not bound to frozen protocol')
    if plan['runner_sha256'] != sha(__file__):
        raise RuntimeError('runner source differs from plan')
    repo = ROOT.parents[1]
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                   text=True, timeout=20).strip()
    branch = subprocess.check_output(['git', '-C', str(repo), 'branch', '--show-current'],
                                     text=True, timeout=20).strip()
    remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin',
                                      'refs/heads/' + branch], text=True, timeout=30).split()[0]
    if source_revision != head or remote != head:
        raise RuntimeError('exact source revision is not on GitHub')

    rank_root = Path(plan['predecessor_rank_root'])
    if not (rank_root / 'v2.finished.json').exists() or not (rank_root / 'v2.result.json').exists():
        raise RuntimeError('predecessor W4 rank attempt is not terminal')
    rank_result = json.loads((rank_root / 'v2.result.json').read_text())
    if rank_result['status'] != plan['required_predecessor_status']:
        raise RuntimeError('predecessor rank result does not admit poly00 D5 launch')
    ps = subprocess.check_output(['ps', '-eo', 'args='], text=True, timeout=15)
    if any('lfdclose2 4 1 20000' in line for line in ps.splitlines()):
        raise RuntimeError('predecessor W4 native child remains live')

    for name, expected in plan['hashes'].items():
        if sha(name) != expected:
            raise RuntimeError('pinned source/input changed: ' + name)
    seed = Path(plan['seed_path'])
    if seed.stat().st_size != plan['seed_bytes']:
        raise RuntimeError('D4 seed size mismatch')
    checker = Path(plan['seed_check_stdout'])
    if 'VALID: 1 is not in W_4(F), and codim W_4(F) >= 45615' not in checker.read_text():
        raise RuntimeError('accepted D4 checker line missing')
    profile = json.loads(Path(plan['profile_path']).read_text())
    if (profile['seed_sha256'] != plan['seed_sha256'] or
            profile['working_coordinates'] != plan['working_coordinates'] or
            profile['next_degree_columns'] != plan['next_degree_columns']):
        raise RuntimeError('profile differs from fixed seed')
    if plan['source_derived_envelope_bytes'] > plan['memory_bytes']:
        raise RuntimeError('native envelope exceeds address-space cap')
    deadline = dt.datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=plan['count_timeout_seconds'] + plan['produce_timeout_seconds']) > deadline:
        raise RuntimeError('original deadline cannot contain full bounded attempt')

    locks = []
    try:
        for name in plan['locks']:
            stream = open(name, 'r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + name)
            locks.append(stream)
        memory = mem_available()
        if memory < plan['memory_bytes'] + plan['reserve_bytes']:
            raise RuntimeError('host memory admission refused')
        output = Path(plan['output_root'])
        if output.exists():
            raise RuntimeError('output root already exists')
        stat = os.statvfs(output.parent)
        disk_free = stat.f_bavail * stat.f_frsize
        if disk_free < plan['maximum_certificate_bytes'] + plan['disk_reserve_bytes']:
            raise RuntimeError('disk admission refused')
        budget_rows = budgets(plan['reserved_usd'])
        output.mkdir(mode=0o700)
        save(output / 'admission.json', {
            'plan_sha256': sha(plan_path), 'protocol_sha256': sha(protocol_path),
            'runner_sha256': sha(__file__), 'source_revision': source_revision,
            'predecessor_result_sha256': sha(rank_root / 'v2.result.json'),
            'seed_sha256': plan['seed_sha256'], 'memory_available_bytes': memory,
            'disk_free_bytes': disk_free, 'budget_readback': budget_rows,
            'admitted_utc': now.isoformat()})
        result = {'schema': 'semaev.original-d5-local-result/v1',
                  'id': plan['id'], 'status': 'started', 'exact_solutions': None,
                  'candidate_codimension': None, 'certificate_sha256': None}
        bundle = Path(plan['bundle_path'])
        env = {key: value for key, value in os.environ.items()
               if not key.startswith('SEMAEV_CHECKPOINT_')}
        env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                   LD_LIBRARY_PATH=str(bundle / 'lib') + os.pathsep + env.get('LD_LIBRARY_PATH', ''))
        rec = plan['record']
        try:
            count_argv = [bundle / 'bin/count_by_sum', rec['n'], rec['modulus_hex'],
                          rec['z_hex'], rec['a6_hex'], len(rec['V_basis_hex']),
                          *rec['V_basis_hex']]
            count = int(run_stage(output, 'count', count_argv, None, 1 << 30,
                                  plan['count_timeout_seconds'], env).strip())
            if count != plan['expected_exact_solutions']:
                raise RuntimeError('fresh exact count differs from frozen input')
            result['exact_solutions'] = count
            candidate = output / 'degree5.bin'
            stdout = run_stage(output, 'produce5',
                [bundle / 'bin/quotient_lift_checkpoint', seed, candidate,
                 plan['chunk_rows'], plan['memory_bytes']], None,
                plan['memory_bytes'], plan['produce_timeout_seconds'], env)
            produced = json.loads(stdout.strip())
            if produced['status'] == 'projection_kills_one':
                if candidate.exists():
                    raise RuntimeError('unexpected certificate after killed projection')
                result['status'] = 'projection_kills_one'
            elif produced['status'] == 'candidate_certificate':
                if not candidate.is_file():
                    raise RuntimeError('missing D5 candidate file')
                result.update(status='candidate_unchecked',
                              candidate_codimension=produced['codimension'],
                              certificate_sha256=sha(candidate),
                              certificate_bytes=candidate.stat().st_size)
            else:
                raise RuntimeError('unknown producer status')
        except Exception as error:
            result.update(status='failed', error=str(error))
            partial = output / 'degree5.bin'
            if partial.exists():
                result.update(partial_certificate_sha256=sha(partial),
                              partial_certificate_bytes=partial.stat().st_size)
        result['checkpoint_files'] = len(list(output.glob('checkpoint-*.bin')))
        save(output / 'result.json', result)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 1 if result['status'] == 'failed' else 0
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.plan, args.protocol, args.source_revision))
