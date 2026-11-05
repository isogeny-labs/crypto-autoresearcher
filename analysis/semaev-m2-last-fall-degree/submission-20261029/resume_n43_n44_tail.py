#!/usr/bin/env python3
"""Continue the fixed n43/n44 D4 panel after a checked capacity pause."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace


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


def available_bytes():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'data', 'dossier', 'binary', 'count-binary', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--validate-only', action='store_true')
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    source = args.dossier / 'submission-20261029'
    if sha(Path(__file__).with_name('n43n44-d4-resume-plan-001.json')) != plan['parent_plan_sha256']:
        raise RuntimeError('parent resume plan hash mismatch')
    prior_root = args.data / 'n43n44-d4-resume-local-001'
    prior_terminal = prior_root / 'terminal.json'
    if sha(prior_terminal) != plan['prior_terminal_sha256']:
        raise RuntimeError('prior capacity-pause terminal hash mismatch')
    prior = json.loads(prior_terminal.read_text())
    if prior['status'] != 'capacity_paused' or [r['id'] for r in prior['items']] != plan['prior_ids']:
        raise RuntimeError('prior window identity or status changed')
    for row in prior['items']:
        root = args.data / 'expansion' / row['id']
        if sha(root / 'attempt-001/result.json') != row['result_sha256']:
            raise RuntimeError('prior result hash mismatch: ' + row['id'])
        for name in row['inference_files']:
            if not (root / name).is_file():
                raise RuntimeError('prior inference missing: ' + row['id'])
    original_path = args.data / 'expansion/plan.json'
    if sha(original_path) != plan['original_plan_sha256']:
        raise RuntimeError('original 190-input plan hash mismatch')
    if sha(args.binary) != plan['binary_sha256'] or sha(args.count_binary) != plan['count_binary_sha256']:
        raise RuntimeError('binary hash mismatch')
    for name, expected in plan['source_sha256'].items():
        if sha(source / name) != expected:
            raise RuntimeError('source hash mismatch: ' + name)
    for name, expected in plan['dossier_sha256'].items():
        if sha(args.dossier / name) != expected:
            raise RuntimeError('dossier hash mismatch: ' + name)
    if sha(Path(__file__)) != plan['driver_sha256']:
        raise RuntimeError('driver hash mismatch')
    original = json.loads(original_path.read_text())
    ids = [item['id'] for item in original['items'] if item['degree'] == 4 and item['record']['n'] in (43, 44)]
    if len(ids) != 20 or ids != plan['prior_ids'] + plan['ids']:
        raise RuntimeError('fixed n43/n44 input selection changed')
    if args.out != Path(plan['output_root']):
        raise RuntimeError('tail output root differs from frozen plan')
    if args.validate_only:
        print(json.dumps({'status': 'validated', 'prior_completed': len(plan['prior_ids']),
                          'remaining': len(plan['ids']), 'plan_sha256': sha(args.plan)}), flush=True)
        return 0
    by_id = {item['id']: item for item in original['items']}
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location('frozen_expand_instances', source / 'expand_instances.py')
    expansion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(expansion)
    handles = []
    try:
        for path in plan['locks']:
            handle = Path(path).open('a')
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            handles.append(handle)
        args.out.mkdir(parents=True, exist_ok=False)
        summary = {'schema': 'semaev.expansion-resume-window/v1',
                   'plan_sha256': sha(args.plan), 'original_plan_sha256': plan['original_plan_sha256'],
                   'prior_terminal_sha256': plan['prior_terminal_sha256'],
                   'prior_completed': len(plan['prior_ids']), 'items': [], 'status': 'started'}
        save(args.out / 'started.json', summary)
        worker = SimpleNamespace(out=args.data / 'expansion', dossier=args.dossier,
                                 binary=args.binary, count_binary=args.count_binary,
                                 source_commit=plan['source_commit'],
                                 memory=plan['memory_bytes'], chunk=plan['chunk_rows'],
                                 timeout=plan['timeout_seconds'])
        try:
            for name in plan['ids']:
                root = args.data / 'expansion' / name
                if list(root.glob('attempt-*/result.json')):
                    raise RuntimeError(name + ': already terminal; reconcile before a second invocation')
                if list(root.glob('attempt-*')):
                    raise RuntimeError(name + ': partial attempt; recover before rerunning closure')
                free = available_bytes()
                gate = {'id': name, 'available_bytes': free,
                        'required_bytes': plan['memory_bytes'] + plan['reserve_bytes'],
                        'admitted': free >= plan['memory_bytes'] + plan['reserve_bytes']}
                save(args.out / f'{name}.gate.json', gate)
                if not gate['admitted']:
                    summary['status'] = 'capacity_paused'
                    break
                result = expansion.process(by_id[name], worker, plan['original_plan_sha256'])
                path = root / 'attempt-001/result.json'
                if not path.is_file():
                    raise RuntimeError(name + ': producer did not close attempt-001')
                row = {'id': name, 'status': result['status'], 'result_sha256': sha(path),
                       'inference_files': sorted(p.name for p in root.glob('inference-*.json'))}
                summary['items'].append(row)
                save(args.out / f'{name}.closed.json', row)
            else:
                summary['status'] = 'complete'
        except BaseException as exc:
            summary.update(status='failed', error=repr(exc))
            raise
        finally:
            save(args.out / 'terminal.json', summary)
    finally:
        for handle in handles:
            handle.close()
    print(json.dumps({'status': summary['status'], 'closed': len(summary['items'])}), flush=True)
    return int(summary['status'] == 'failed')


if __name__ == '__main__':
    raise SystemExit(main())
