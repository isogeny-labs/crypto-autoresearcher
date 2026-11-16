#!/usr/bin/env python3
"""Bounded independent check of a pinned original-system D5 candidate."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

from run_n51_poly00_d5_local_v2 import budgets, mem_available, run_stage, save, sha


def require_published(repo: Path, source_revision: str) -> None:
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    branch = subprocess.check_output(['git', '-C', str(repo), 'branch', '--show-current'], text=True).strip()
    remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin',
                                      'refs/heads/' + branch], text=True).split()[0]
    if source_revision != head or remote != head:
        raise RuntimeError('exact checker source revision is not on GitHub')


def validate_candidate(plan: dict) -> dict:
    for name in ('certificate', 'generators', 'checker_binary', 'helper_source',
                 'producer_result',
                 'produce_finish', 'count_finish', 'count_stdout'):
        if plan[name] not in plan['hashes']:
            raise RuntimeError('unbound checker input: ' + name)
    producer = json.loads(Path(plan['producer_result']).read_text())
    if producer['status'] != 'candidate_unchecked' or producer['exact_solutions'] != 6:
        raise RuntimeError('producer lacks a candidate with fresh exact count six')
    if (producer['certificate_sha256'] != plan['hashes'][plan['certificate']] or
            producer['certificate_bytes'] != Path(plan['certificate']).stat().st_size):
        raise RuntimeError('candidate differs from producer receipt')
    if (not isinstance(producer['candidate_codimension'], int) or
            producer['candidate_codimension'] < 1):
        raise RuntimeError('invalid candidate codimension')
    produce = json.loads(Path(plan['produce_finish']).read_text())
    if produce['returncode'] != 0 or produce['timed_out']:
        raise RuntimeError('candidate producer did not complete')
    count = json.loads(Path(plan['count_finish']).read_text())
    if count['returncode'] != 0 or count['timed_out']:
        raise RuntimeError('fresh exact count did not complete')
    if count['stdout_sha256'] != plan['hashes'][plan['count_stdout']]:
        raise RuntimeError('count receipt does not bind stdout')
    if Path(plan['count_stdout']).read_text().strip() != '6':
        raise RuntimeError('fresh count stdout is not six')
    return producer


def main(plan_path: Path, source_revision: str) -> int:
    plan = json.loads(plan_path.read_text())
    if plan['schema'] != 'semaev.original-d5-native-check-plan/v1':
        raise RuntimeError('wrong checker plan schema')
    if plan['attempts'] != 1 or plan['automatic_retries'] != 0:
        raise RuntimeError('checker attempt limit changed')
    if sha(__file__) != plan['runner_sha256']:
        raise RuntimeError('checker runner hash mismatch')
    repo = Path(__file__).resolve().parents[2]
    require_published(repo, source_revision)
    source = subprocess.check_output(['git', '-C', str(repo), 'show',
                                      'HEAD:' + plan['checker_source_path']])
    if hashlib.sha256(source).hexdigest() != plan['checker_source_sha256']:
        raise RuntimeError('native checker source hash mismatch')
    for path, digest in plan['hashes'].items():
        if sha(path) != digest:
            raise RuntimeError('pinned candidate/checker input changed: ' + path)
    producer = validate_candidate(plan)
    deadline = dt.datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=plan['timeout_seconds']) > deadline:
        raise RuntimeError('original deadline cannot contain the bounded check')
    root = Path(plan['output_root'])
    if root.exists():
        raise RuntimeError('checker output root already exists')
    locks = []
    try:
        for path in plan['locks']:
            stream = open(path, 'r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + path)
            locks.append(stream)
        available = mem_available()
        if available < plan['memory_bytes'] + plan['reserve_bytes']:
            raise RuntimeError('host memory admission refused')
        budget_rows = budgets(plan['reserved_usd'])
        root.mkdir(mode=0o700)
        save(root / 'admission.json', {
            'plan_sha256': sha(plan_path), 'runner_sha256': sha(__file__),
            'source_revision': source_revision, 'producer_result_sha256':
            plan['hashes'][plan['producer_result']], 'admitted_utc': now.isoformat(),
            'memory_available_bytes': available, 'budget_readback': budget_rows})
        argv = [plan['checker_binary'], plan['certificate'], plan['generators'],
                plan['hashes'][plan['certificate']], plan['hashes'][plan['generators']]]
        result = {'schema': 'semaev.original-d5-native-check-result/v1',
                  'status': 'started', 'exact_solutions': 6,
                  'producer_codimension': producer['candidate_codimension']}
        try:
            output = run_stage(root, 'check5original', argv, None, plan['memory_bytes'],
                               plan['timeout_seconds'], dict(os.environ, OMP_NUM_THREADS='1'))
            parsed = json.loads(output)
            expected = {'status': 'valid_native_quotient_nonmembership',
                        'degree': 5, 'variables': 52, 'generators': 51,
                        'certificate_sha256': plan['hashes'][plan['certificate']],
                        'generators_sha256': plan['hashes'][plan['generators']],
                        'codimension_lower_bound': producer['candidate_codimension']}
            for key, value in expected.items():
                if parsed.get(key) != value:
                    raise RuntimeError('independent checker field mismatch: ' + key)
            result.update(status='native_certificate_verified', observed=parsed,
                          exceeds_solution_count=parsed['codimension_lower_bound'] > 6)
        except Exception as error:
            result.update(status='failed', error=str(error))
        save(root / 'result.json', result)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result['status'] == 'native_certificate_verified' else 1
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.plan, args.source_revision))
