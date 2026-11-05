#!/usr/bin/env python3
"""Inspect an IC continuation bundle. Never submits jobs or approves research."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCIENTIFIC = {'succeeded', 'failed', 'timeout', 'cancelled', 'infra_error', 'interrupted'}


def load(path):
    return json.loads(Path(path).read_text())


def validate(program, root=ROOT):
    errors = []
    if program.get('schema') != 'ic.continuation-plan/v1':
        errors.append('unsupported plan schema')
    if program.get('authority') != 'proposal_only':
        errors.append('this bundle cannot confer scientific approval')
    tracks = program.get('workstreams', [])
    ids = [t['id'] for t in tracks]
    if len(set(ids)) != len(ids):
        errors.append('duplicate workstream id')
    required = ('question', 'lead_refs', 'sources', 'next_step', 'deliverables',
                'controls', 'metrics', 'scaling', 'outcomes', 'dependencies', 'owner_repository')
    for t in tracks:
        for field in required:
            if not t.get(field) and field != 'dependencies':
                errors.append(f"{t['id']}: missing {field}")
        if t.get('execution_state') != 'not_started':
            errors.append(f"{t['id']}: plan entries are not execution receipts")
        for dep in t.get('dependencies', []):
            if dep not in ids:
                errors.append(f"{t['id']}: unknown dependency {dep}")
        if t.get('kind') == 'performance':
            for cost in program['complete_cost_fields']:
                if cost not in t.get('metrics', []):
                    errors.append(f"{t['id']}: missing complete-cost field {cost}")
        for outcome in ('positive', 'null', 'inconclusive'):
            if not t.get('outcomes', {}).get(outcome):
                errors.append(f"{t['id']}: no {outcome} continuation")
    graph = {t['id']: t.get('dependencies', []) for t in tracks}
    seen, active = set(), set()
    def visit(node):
        if node in active:
            errors.append('dependency cycle at ' + node)
            return
        if node in seen or node not in graph:
            return
        active.add(node)
        for dep in graph[node]:
            visit(dep)
        active.remove(node)
        seen.add(node)
    for node in graph:
        visit(node)
    sources = {s['id']: s for s in program.get('source_lock', [])}
    for source in sources.values():
        if len(source.get('commit', '')) != 40 or len(source.get('sha256', '')) != 64:
            errors.append(source['id'] + ': missing immutable source pin')
        relative = Path(source['snapshot'])
        if relative.is_absolute() or '..' in relative.parts:
            errors.append(source['id'] + ': unsafe snapshot path')
            continue
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            errors.append(source['id'] + ': missing or changed source snapshot')
    for t in tracks:
        for sid in t['sources']:
            if sid not in sources:
                errors.append(t['id'] + ': unknown source ' + sid)
    return errors


def coverage(expected, observed):
    """An accounting diagnostic; does not verify witnesses, counters or protocols."""
    keys = ('arm', 'instance_id', 'seed', 'replicate', 'warmup')
    if isinstance(observed, dict):
        if observed.get('schema') != 'experiment.export/v1':
            raise ValueError('expected canonical experiment.export/v1')
        observed = observed['runs']
    def key(row):
        return tuple(row[k] for k in keys)
    planned = [key(row) for row in expected]
    if len(planned) != len(set(planned)):
        raise ValueError('duplicate planned row')
    by_key = {}
    for row in observed:
        k = key(row)
        if k in by_key:
            raise ValueError('duplicate observed row')
        if row.get('status') not in SCIENTIFIC:
            raise ValueError('unrecognized row status')
        by_key[k] = row
    unknown = set(by_key) - set(planned)
    if unknown:
        raise ValueError('unplanned observations')
    missing = [k for k in planned if k not in by_key]
    incomplete = [k for k in planned if k in by_key and (by_key[k]['status'] != 'succeeded'
                      or by_key[k].get('verification', {}).get('status') != 'verified'
                      or by_key[k].get('exclusion', {}).get('excluded') is not False)]
    return {'planned': len(planned), 'observed': len(by_key),
            'missing': missing, 'incomplete': incomplete,
            'panel_complete': not missing and not incomplete,
            'research_verified': False,
            'note': 'Accounting only. Use canonical experiment.export/v1 validation and independent review.'}


def status(program, evidence=None):
    # A plan never certifies live WIP, a checkpoint, funds, or experiment approval.
    evidence = evidence or {}
    requirements = ('wip_admitted', 'checkpoint_uploaded', 'inputs_published',
                    'protocol_approved', 'owner_lane_available', 'resources_available')
    gates = {k: evidence.get(k) for k in requirements}
    missing = [k for k, value in gates.items() if value is not True]
    return {'authority': 'advisory_only', 'submission_performed': False,
            'admission_evidence': gates, 'unmet_or_unknown': missing,
            'workstreams': [{'id': t['id'], 'execution_state': 'not_started',
                            'next_step': t['next_step']} for t in program['workstreams']],
            'note': 'Even all-true supplied values are assertions, not launch authority. '
                    'The existing runner must recheck live admission and independently bound receipts.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'status', 'coverage'))
    parser.add_argument('--program', type=Path, default=ROOT/'program.json')
    parser.add_argument('--expected', type=Path)
    parser.add_argument('--observed', type=Path)
    args = parser.parse_args()
    program = load(args.program)
    errors = validate(program, args.program.parent)
    if errors:
        print(json.dumps({'valid': False, 'errors': errors}, indent=2))
        return 1
    if args.action == 'check':
        result = {'valid': True, 'workstreams': len(program['workstreams']),
                  'source_pins': len(program['source_lock']), 'research_verified': False}
    elif args.action == 'status':
        result = status(program)
    else:
        if not args.expected or not args.observed:
            parser.error('coverage requires --expected and --observed JSON arrays')
        result = coverage(load(args.expected), load(args.observed))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
