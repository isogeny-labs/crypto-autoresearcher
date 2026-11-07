#!/usr/bin/env python3
"""One bounded D5 producer on the exact-seed zero-solution n47 instance."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import struct
import subprocess

from run_n51_poly00_d5_local_v2 import budgets, mem_available, run_stage, save, sha


def run(plan_path, protocol_path, source_revision):
    plan = json.loads(plan_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    if plan['schema'] != 'semaev.n47-rand00-d5-local-plan/v1':
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
        raise RuntimeError('exact source revision is not on GitHub')
    for path, expected in plan['hashes'].items():
        if sha(path) != expected:
            raise RuntimeError('pinned source or input changed: ' + path)
    seed = Path(plan['seed_path'])
    with seed.open('rb') as stream:
        header = stream.read(32)
    if len(header) != 32 or struct.unpack('<4q', header) != (48, 4, 213053, 61196):
        raise RuntimeError('wrong accepted D4 seed dimensions')
    if seed.stat().st_size != plan['seed_bytes']:
        raise RuntimeError('D4 seed size mismatch')
    if 'VALID: 1 is not in W_4(F), and codim W_4(F) >= 61196' not in Path(plan['seed_check_stdout']).read_text():
        raise RuntimeError('accepted D4 checker line missing')
    rank = json.loads(Path(plan['rank_result']).read_text())
    if (rank['status'] != 'rank_match' or rank['observed']['rank'] != 151857 or
            rank['observed']['columns'] != 213053 or rank['observed']['contains_one']):
        raise RuntimeError('independent D4 rank premise differs')
    if plan['source_derived_envelope_bytes'] > plan['memory_bytes']:
        raise RuntimeError('blocked source envelope exceeds child cap')
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
        if output.exists():
            raise RuntimeError('write-once output root already exists')
        fs = os.statvfs(output.parent)
        disk_free = fs.f_bavail * fs.f_frsize
        if disk_free < plan['maximum_certificate_bytes'] + plan['disk_reserve_bytes']:
            raise RuntimeError('disk admission refused')
        budget_rows = budgets(plan['reserved_usd'])
        output.mkdir(mode=0o700)
        save(output / 'admission.json', {'plan_sha256': sha(plan_path),
            'protocol_sha256': sha(protocol_path), 'source_revision': source_revision,
            'seed_sha256': plan['hashes'][plan['seed_path']],
            'rank_result_sha256': plan['hashes'][plan['rank_result']],
            'memory_available_bytes': memory, 'disk_free_bytes': disk_free,
            'budget_readback': budget_rows, 'admitted_utc': now.isoformat()})
        result = {'schema': 'semaev.n47-rand00-d5-local-result/v1',
                  'id': plan['id'], 'status': 'started', 'exact_solutions': None,
                  'candidate_codimension': None, 'certificate_sha256': None}
        env = {k: v for k, v in os.environ.items() if not k.startswith('SEMAEV_CHECKPOINT_')}
        env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        bundle = Path(plan['bundle_path'])
        env['LD_LIBRARY_PATH'] = str(bundle / 'lib') + os.pathsep + env.get('LD_LIBRARY_PATH', '')
        rec = plan['record']
        try:
            count_args = [rec['n'], rec['modulus_hex'], rec['z_hex'], rec['a6_hex'],
                          len(rec['V_basis_hex']), *rec['V_basis_hex']]
            count = run_stage(output, 'count', [plan['count_binary'], *count_args],
                              None, 1 << 30, plan['timeouts_seconds']['count'], env)
            if count.strip() != '0':
                raise RuntimeError('fresh exact count differs from frozen zero')
            result['exact_solutions'] = 0
            candidate = output / 'degree5.bin'
            stdout = run_stage(output, 'produce5', [plan['producer_binary'], seed,
                candidate, plan['chunk_rows'], plan['memory_bytes']], None,
                plan['memory_bytes'], plan['timeouts_seconds']['produce5'], env)
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
