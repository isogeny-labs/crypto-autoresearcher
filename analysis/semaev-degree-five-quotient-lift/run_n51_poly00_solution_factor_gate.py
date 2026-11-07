#!/usr/bin/env python3
"""One bounded root-list and complete D4 solution-factorization attempt."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess

from run_n51_poly00_d5_local_v2 import budgets, mem_available, run_stage, save, sha


def run(plan_path, protocol_path, source_revision):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    if plan['schema'] != 'semaev.solution-factor-gate-plan/v1':
        raise RuntimeError('wrong plan schema')
    if protocol['freeze']['status'] != 'frozen' or protocol['links']['plan_sha256'] != sha(plan_path):
        raise RuntimeError('plan is not bound to frozen protocol')
    if sha(__file__) != plan['hashes'][str(Path(__file__).resolve())]:
        raise RuntimeError('runner source changed')
    repo = Path(__file__).resolve().parents[2]
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                   text=True, timeout=20).strip()
    branch = subprocess.check_output(['git', '-C', str(repo), 'branch', '--show-current'],
                                     text=True, timeout=20).strip()
    remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin',
                                      'refs/heads/' + branch], text=True, timeout=30).split()[0]
    if source_revision != head or remote != head:
        raise RuntimeError('exact source revision is not published on GitHub')
    for path, expected in plan['hashes'].items():
        if sha(path) != expected:
            raise RuntimeError('pinned source or input changed: ' + path)
    if Path(plan['output_root']).exists():
        raise RuntimeError('write-once output root already exists')
    deadline = dt.datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=sum(plan['timeouts_seconds'].values())) > deadline:
        raise RuntimeError('deadline cannot contain full bounded attempt')
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
        fs = os.statvfs(output.parent)
        disk_free = fs.f_bavail * fs.f_frsize
        if disk_free < plan['maximum_output_bytes'] + plan['disk_reserve_bytes']:
            raise RuntimeError('disk admission refused')
        budget_rows = budgets(plan['reserved_usd'])
        output.mkdir(mode=0o700)
        save(output / 'admission.json', {
            'plan_sha256': sha(plan_path), 'protocol_sha256': sha(protocol_path),
            'source_revision': source_revision, 'memory_available_bytes': memory,
            'disk_free_bytes': disk_free, 'budget_readback': budget_rows,
            'admitted_utc': now.isoformat()})
        result = {'schema': 'semaev.solution-factor-gate-result/v1',
                  'id': plan['id'], 'status': 'started', 'count': None,
                  'pairs_sha256': None, 'factorization': None}
        env = dict(os.environ)
        env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        rec = plan['record']
        count_args = [rec['n'], rec['modulus_hex'], rec['z_hex'], rec['a6_hex'],
                      len(rec['V_basis_hex']), *rec['V_basis_hex']]
        try:
            emitter = output / 'enumerate_original_pairs'
            run_stage(output, 'build',
                      ['/usr/bin/cc', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
                       '-mpclmul', '-msse4.1', '-o', emitter, plan['emitter_source']],
                      None, plan['memory_bytes'], plan['timeouts_seconds']['build'], env)
            result['emitter_binary_sha256'] = sha(emitter)
            count_out = run_stage(output, 'count',
                                  [plan['count_binary'], *count_args], None,
                                  plan['memory_bytes'], plan['timeouts_seconds']['count'], env)
            if count_out.strip() != str(plan['expected_exact_solutions']):
                raise RuntimeError('fresh exact count differs from fixed six')
            result['count'] = int(count_out.strip())
            run_stage(output, 'pairs', [emitter, *count_args], None,
                      plan['memory_bytes'], plan['timeouts_seconds']['pairs'], env)
            pair_file = output / 'pairs.stdout.txt'
            result['pairs_sha256'] = sha(pair_file)
            if (output / 'pairs.stderr.txt').read_text().strip() != 'ordered_pairs 6':
                raise RuntimeError('emitter count differs from fixed six')
            python = plan['python_binary']
            verified = run_stage(output, 'factor', [python, plan['factor_checker'],
                    '--plan', plan_path, '--generator', plan['generator_file'],
                    '--generator-sha256', plan['hashes'][plan['generator_file']],
                    '--pairs', pair_file, '--pairs-sha256', result['pairs_sha256'],
                    '--count-stdout', output / 'count.stdout.txt',
                    '--count-sha256', sha(output / 'count.stdout.txt'),
                    '--seed', plan['seed_file']], None, plan['memory_bytes'],
                    plan['timeouts_seconds']['factor'], env)
            evidence = json.loads(verified)
            if (not evidence['factorization'] or evidence['checked_pairs'] != 6 or
                    evidence['codimension'] != plan['seed_codimension'] or
                    evidence['columns'] != plan['seed_columns']):
                raise RuntimeError('factor checker returned unexpected fields')
            result.update(status='factorization_verified', factorization=True,
                          factor_stdout_sha256=sha(output / 'factor.stdout.txt'))
        except Exception as error:
            result.update(status='failed', error=str(error))
        save(output / 'result.json', result)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result['status'] == 'factorization_verified' else 1
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
