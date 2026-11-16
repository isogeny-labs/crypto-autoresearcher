#!/usr/bin/env python3
"""One bounded native-checker control on the accepted original n51 D4 map."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

from run_n51_poly00_d5_local_v2 import budgets, mem_available, run_stage, save, sha


def main(plan_path: Path, source_revision: str) -> int:
    plan = json.loads(plan_path.read_text())
    if plan['schema'] != 'semaev.native-original-d4-control/v1':
        raise RuntimeError('wrong control plan')
    if sha(__file__) != plan['runner_sha256']:
        raise RuntimeError('runner hash mismatch')
    repo = Path(__file__).resolve().parents[2]
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    branch = subprocess.check_output(['git', '-C', str(repo), 'branch', '--show-current'], text=True).strip()
    remote = subprocess.check_output(['git', '-C', str(repo), 'ls-remote', 'origin', 'refs/heads/' + branch], text=True).split()[0]
    if source_revision != head or remote != head:
        raise RuntimeError('exact control source revision is not on GitHub')
    checker_source = subprocess.check_output(
        ['git', '-C', str(repo), 'show', 'HEAD:' + plan['checker_source_path']])
    if hashlib.sha256(checker_source).hexdigest() != plan['checker_source_sha256']:
        raise RuntimeError('checker source hash mismatch')
    for path, digest in plan['hashes'].items():
        if sha(path) != digest:
            raise RuntimeError('pinned control input changed: ' + path)
    deadline = dt.datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00'))
    now = dt.datetime.now(dt.timezone.utc)
    if now + dt.timedelta(seconds=plan['timeout_seconds']) > deadline:
        raise RuntimeError('original deadline cannot contain the bounded control')
    root = Path(plan['output_root'])
    if root.exists():
        raise RuntimeError('control output root already exists')
    with Path(plan['lock_path']).open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        available = mem_available()
        if available < plan['memory_bytes'] + plan['reserve_bytes']:
            raise RuntimeError('host memory admission refused')
        if root.parent.stat().st_dev != Path(plan['certificate']).stat().st_dev:
            raise RuntimeError('unexpected output filesystem')
        budget_rows = budgets(plan['reserved_usd'])
        root.mkdir(mode=0o700)
        save(root / 'admission.json', {
            'plan_sha256': sha(plan_path), 'runner_sha256': sha(__file__),
            'source_revision': source_revision, 'admitted_utc': now.isoformat(),
            'memory_available_bytes': available, 'budget_readback': budget_rows})
        argv = [plan['checker_binary'], plan['certificate'], plan['generators'],
                plan['hashes'][plan['certificate']], plan['hashes'][plan['generators']]]
        result = {'schema': 'semaev.native-original-d4-control-result/v1',
                  'status': 'started', 'expected': plan['expected']}
        try:
            output = run_stage(root, 'check4original', argv, None, plan['memory_bytes'],
                               plan['timeout_seconds'], dict(os.environ, OMP_NUM_THREADS='1'))
            parsed = json.loads(output)
            for key, value in plan['expected'].items():
                if parsed.get(key) != value:
                    raise RuntimeError('checker field mismatch: ' + key)
            result.update(status='accepted_fullsize_original_control', observed=parsed)
        except Exception as error:
            result.update(status='failed', error=str(error))
        save(root / 'result.json', result)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result['status'] == 'accepted_fullsize_original_control' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.plan, args.source_revision))
