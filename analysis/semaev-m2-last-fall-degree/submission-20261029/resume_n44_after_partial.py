#!/usr/bin/env python3
"""Continue the two untouched n44 panel inputs after a partial tail interruption."""
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


def memory_state(owner):
    rows = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = dict(line.split(':', 1) for line in (path / 'status').read_text().splitlines() if ':' in line)
            rows[int(path.name)] = (int(fields['PPid'].strip()),
                                    int(fields.get('VmRSS', '0 kB').split()[0]) * 1024,
                                    (path / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace'))
        except (FileNotFoundError, ProcessLookupError, PermissionError, KeyError, ValueError):
            pass
    pid = owner['pid']
    if pid not in rows or owner['command_contains'] not in rows[pid][2]:
        raise RuntimeError('pinned concurrent owner is not live; reconcile capacity before a new launch')
    pids = {pid}
    while True:
        old = len(pids)
        pids.update(p for p, (ppid, _, _) in rows.items() if ppid in pids)
        if len(pids) == old:
            break
    resident = sum(rows[p][1] for p in pids)
    meminfo = dict((line.split(':', 1)[0], int(line.split()[1]) * 1024)
                   for line in Path('/proc/meminfo').read_text().splitlines() if ':' in line)
    return dict(owner_pids=sorted(pids), owner_resident_bytes=resident,
                owner_possible_growth_bytes=max(0, owner['memory_bytes'] - resident),
                mem_available_bytes=meminfo['MemAvailable'], mem_total_bytes=meminfo['MemTotal'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'data', 'dossier', 'binary', 'count-binary', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--validate-only', action='store_true')
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    if plan['schema'] != 'semaev.expansion-after-partial-plan/v1' or sha(Path(__file__)) != plan['driver_sha256']:
        raise RuntimeError('driver or plan identity mismatch')
    if args.out != Path(plan['output_root']):
        raise RuntimeError('output root differs from frozen plan')
    if sha(args.data / 'expansion/plan.json') != plan['original_plan_sha256']:
        raise RuntimeError('original 190-input plan changed')
    if sha(args.binary) != plan['binary_sha256'] or sha(args.count_binary) != plan['count_binary_sha256']:
        raise RuntimeError('binary changed')
    source = args.dossier / 'submission-20261029'
    for name, expected in plan['source_sha256'].items():
        if sha(source / name) != expected:
            raise RuntimeError('source changed: ' + name)
    for name, expected in plan['dossier_sha256'].items():
        if sha(args.dossier / name) != expected:
            raise RuntimeError('dossier changed: ' + name)
    if sha(args.data / 'n43n44-d4-tail-local-001/started.json') != plan['interrupted_started_sha256']:
        raise RuntimeError('interrupted tail identity changed')
    if sha(args.data / 'n43n44-d4-tail-local-001/fresh-n44-rand-02.recovered.json') != plan['recovery_receipt_sha256']:
        raise RuntimeError('partial recovery receipt changed')
    original = json.loads((args.data / 'expansion/plan.json').read_text())
    ids = [item['id'] for item in original['items'] if item['degree'] == 4 and item['record']['n'] in (43, 44)]
    if ids != plan['prior_ids'] + plan['ids'] or len(ids) != 20 or len(plan['ids']) != 2:
        raise RuntimeError('fixed panel selection changed')
    for name, expected in plan['prior_result_sha256'].items():
        path = args.data / 'expansion' / name / 'attempt-001/result.json'
        if sha(path) != expected:
            raise RuntimeError('prior result changed: ' + name)
        if not list(path.parent.parent.glob('inference-*.json')):
            raise RuntimeError('prior inference missing: ' + name)
    owner = plan['concurrent_owner']
    if sha(owner['plan']) != owner['plan_sha256']:
        raise RuntimeError('concurrent owner plan changed')
    if json.loads(Path(owner['plan']).read_text())['memory_bytes'] != owner['memory_bytes']:
        raise RuntimeError('concurrent owner cap changed')
    for name in plan['ids']:
        if list((args.data / 'expansion' / name).glob('attempt-*')):
            raise RuntimeError('target already has an attempt: ' + name)
    if args.out.exists():
        raise RuntimeError('output root already exists')
    if args.validate_only:
        print(json.dumps({'status': 'validated', 'ids': plan['ids'], 'plan_sha256': sha(args.plan)}), flush=True)
        return 0
    handles = []
    try:
        for path in plan['locks']:
            handle = Path(path).open('a')
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            handles.append(handle)
        args.out.mkdir(parents=True, exist_ok=False)
        summary = {'schema': 'semaev.expansion-after-partial-window/v1',
                   'plan_sha256': sha(args.plan), 'prior_completed': len(plan['prior_ids']),
                   'items': [], 'status': 'started'}
        save(args.out / 'started.json', summary)
        worker = SimpleNamespace(out=args.data / 'expansion', dossier=args.dossier,
                                 binary=args.binary, count_binary=args.count_binary,
                                 source_commit=plan['source_commit'], memory=plan['memory_bytes'],
                                 chunk=plan['chunk_rows'], timeout=plan['timeout_seconds'])
        sys.path.insert(0, str(source))
        spec = importlib.util.spec_from_file_location('frozen_expand_instances', source / 'expand_instances.py')
        expansion = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(expansion)
        by_id = {item['id']: item for item in original['items']}
        try:
            for name in plan['ids']:
                state = memory_state(owner)
                required = plan['memory_bytes'] + plan['reserve_bytes'] + state['owner_possible_growth_bytes']
                gate = dict(id=name, **state, required_available_bytes=required,
                            declared_total_bytes=plan['memory_bytes'] + plan['reserve_bytes'] + owner['memory_bytes'],
                            admitted=(state['mem_available_bytes'] >= required and
                                      state['mem_total_bytes'] >= plan['memory_bytes'] + plan['reserve_bytes'] + owner['memory_bytes']))
                save(args.out / f'{name}.gate.json', gate)
                if not gate['admitted']:
                    summary['status'] = 'capacity_paused'
                    break
                result = expansion.process(by_id[name], worker, plan['original_plan_sha256'])
                path = args.data / 'expansion' / name / 'attempt-001/result.json'
                if not path.is_file():
                    raise RuntimeError(name + ': result missing after producer returned')
                row = {'id': name, 'status': result['status'], 'result_sha256': sha(path),
                       'inference_files': sorted(p.name for p in path.parent.parent.glob('inference-*.json'))}
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
