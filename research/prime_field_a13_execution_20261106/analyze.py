"""Stream-bound descriptive A13 metrics, cold references and unified export."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path

from baseline import costs
from custody import HERE, ROOT, INPUTS, load, write_once, digest, tools, descriptors, methods, arm_id, export_arm
from streams import lines
from cold_costs import prior, total, collection_view, compare

COLS = ['case_id', 'cell_id', 'base_arm', 'source_schedule', 'source_prefix',
    'target_policy', 'target_prefix', 'scope', 'verified', 'base_columns',
    'source_rank', 'outside_rank', 'delta', 'after_cancellation_rank',
    'identified_targets', 'identified_mask', 'source_rows', 'target_rows',
    'decomposition_rows', 'knowledge_rows']
ARITHMETIC = tuple(field+'.field_'+op for field in ('Fp', 'Fr') for op in ('add', 'sub', 'mul', 'inv')) + ('query_array_allocated_bytes',)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    args = parser.parse_args()
    rules, protocol = load(INPUTS), load(args.protocol)
    raw = args.run/'raw'
    execution, host = load(args.run/'execution.json'), load(args.run/'host.json')
    plans = dict(descriptors(rules))
    rows, errors, checkpoints, curves, cold = {}, [], [], [], []
    refs, branch_refs = {}, {}
    physical = defaultdict(Counter)
    observed = defaultdict(Counter)
    verified_engines = {name: Counter() for name in costs.ENGINES}

    def read(path):
        try:
            return prior.optional(path)
        except Exception as error:
            errors.append(dict(path=str(path), error_type=type(error).__name__, error=str(error)))

    def readlines(path):
        try:
            yield from lines(path)
        except Exception as error:
            errors.append(dict(path=str(path), error_type=type(error).__name__, error=str(error)))

    generation = read(raw/'generation-check.json')
    generation_valid = bool(generation and generation['verification']['checked'] and
                            generation['verification']['curves'] == len(rules['fields'])*rules['curves_per_field'])
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid = 'p'+str(field['p'])+'-i'+str(ci)
            for event in readlines(raw/(cid+'.events.jsonl')):
                kind, base = event['kind'], event.get('base_arm')
                if kind == 'branch_output':
                    branch_refs[cid, base, json.dumps(event['context'], sort_keys=True)] = event['record']
                elif kind in ('case_input', 'case_checked', 'solver_complete'):
                    label = 'input' if kind == 'case_input' else 'check' if kind == 'case_checked' else event['arm']
                    refs[event['case_id'], label] = event['record']
                    if kind == 'case_input':
                        physical['matrix_assembly'].update(total(event['shared_phases']))
                    elif kind == 'solver_complete':
                        observed[arm_id(event['descriptor'], event['arm'])].update(event['counters'])
                elif kind == 'collection_phase':
                    physical['norm_collection'].update(event['phase']['counters'])
                elif kind == 'affine_phase':
                    context = event['context']
                    label = context.get('kind', 'target_construction')
                    physical[(base+'.' if base else '')+label].update(event['phase']['counters'])
                elif kind == 'solver_failed':
                    observed[arm_id(event['descriptor'], event['arm'])].update(total(event['phases']))
                    errors.append(dict(cell_id=cid, event=event))
                elif kind == 'failure':
                    errors.append(dict(cell_id=cid, event=event))
            sources = {base: read(raw/(cid+'.'+base+'.source.json')) for base in rules['base_arms']}
            caches = {base: read(raw/(cid+'.'+base+'.query-cache.json')) for base in rules['base_arms']}
            checks = {base: [read(raw/(cid+'.'+base+'.'+suffix+'.json')) for suffix in ('source-check', 'query-check')]
                      for base in rules['base_arms']}
            built, basecheck = read(raw/(cid+'.known.base.json')), read(raw/(cid+'.known.base-check.json'))
            recipes, complete = read(raw/(cid+'.target-recipes.json')), read(raw/(cid+'.complete.json'))
            curve_valid = bool(generation_valid and all(sources.values()) and all(caches.values()) and built and
                basecheck and basecheck['verification']['checked'] and recipes and complete and complete['complete'] and
                all(v and v['verification']['checked'] for group in checks.values() for v in group))
            ordinal = len(checkpoints)+1
            if rules['closed_curve_checkpoint']:
                receipt = read(args.run/('checkpoint-'+cid+'.json'))
                expected_cases = ordinal * len(plans) // (len(rules['fields'])*rules['curves_per_field'])
                valid = prior.checkpoint_valid(receipt, cid, ordinal, expected_cases)
                checkpoints.append(dict(cell_id=cid, valid=valid, receipt=receipt))
                if not valid:
                    errors.append(dict(cell_id=cid, error='missing/failed closed-curve canonical checkpoint'))
            if curve_valid:
                curves.append(dict(cell_id=cid, norm_fixture=sources['norm']['cell']['fixture'],
                                   known_fixture=sources['known']['cell']['fixture']))
                for base in rules['base_arms']:
                    for check in checks[base]:
                        for engine in costs.ENGINES:
                            verified_engines[engine].update(check['verification']['query_engines']['engine_totals'][engine])
            branches = iter(readlines(raw/(cid+'.branches.jsonl')))
            outputs = iter(readlines(raw/(cid+'.solver-outputs.jsonl')))
            checked = iter(readlines(raw/(cid+'.case-checks.jsonl')))
            current = None
            for item in readlines(raw/(cid+'.case-inputs.jsonl')):
                idx, desc = item['case_id'], item['descriptor']
                if plans.get(idx) != desc or idx in rows:
                    raise ValueError('fixed case descriptor/order')
                base = desc['base_arm']
                context = {k: desc[k] for k in ('source_schedule', 'source_prefix', 'target_policy')}
                if current is None or current['base_arm'] != base or current['context'] != context:
                    current = next(branches, None)
                    if current and (current['base_arm'] != base or current['context'] != context or not prior.record_binding(
                            current, branch_refs.get((cid, base, json.dumps(context, sort_keys=True))))):
                        raise ValueError('branch stream order/journal binding')
                results = [next(outputs, None) for method in methods(desc)]
                check = next(checked, None)
                valid = bool(curve_valid and current and check and check['case_id'] == idx and
                    check['verification']['checked'] and all(v and v['case_id'] == idx and v['arm'] == method
                        for method, v in zip(methods(desc), results, strict=True)))
                row = dict(case_id=idx, **desc, verified=valid)
                if valid:
                    for label, value in [('input', item), ('check', check),
                            *[(method, value) for method, value in zip(methods(desc), results, strict=True)]]:
                        if not prior.record_binding(value, refs.get((idx, label))):
                            raise ValueError('input/output/check stream-journal binding')
                    case, info = item['case'], check['verification']
                    row.update(base_columns=case['width'], source_rank=info['source_rank'],
                        outside_rank=info['outside_rank'], delta=info['delta'],
                        after_cancellation_rank=info['base_rank_after_cancellation'],
                        identified_targets=info['identified'], source_rows=len(case['source']), target_rows=len(case['target']),
                        decomposition_rows=sum(v['kind'] == 'decomposition' for v in case['target']),
                        knowledge_rows=sum(v['kind'] != 'decomposition' for v in case['target']),
                        assembly_counters=total(item['shared_phases']), solver_counters={})
                    for method, result in zip(methods(desc), results, strict=True):
                        value = result['result']
                        if total(value['phases']) != value['counters']:
                            raise ValueError('solver phase conservation')
                        mask = sum(1 << v['target_index'] for v in value['recoveries'] if v['identifiable'])
                        if 'identified_mask' in row and row['identified_mask'] != mask:
                            raise ValueError('known direct/joint target identities differ')
                        row['identified_mask'] = mask
                        row['solver_counters'][method] = value['counters']
                    view = collection_view(base, sources[base]['collection'], sources['norm']['collection'], built,
                        current['branch'], caches[base], recipes, desc['target_prefix'], rules)
                    options = {}
                    for method in methods(desc):
                        options[method] = {engine: dict(Counter(view['engine_collection_counters'][engine]) +
                            Counter(row['assembly_counters']) + Counter(row['solver_counters'][method])) for engine in costs.ENGINES}
                    cold.append(dict(case_id=idx, descriptor=desc, identified_mask=row['identified_mask'],
                        collection=view, solver_engine_counters=options))
                rows[idx] = row
            if curve_valid and any(next(stream, None) is not None for stream in (branches, outputs, checked)):
                raise ValueError('extra records beyond complete fixed census')
    cells = [rows.get(idx, dict(case_id=idx, **desc, verified=False)) for idx, desc in plans.items()]
    full = bool(execution['returncode'] == 0 and not execution['timeout'] and not execution['exception'] and
        execution['source_unchanged_after'] and len(curves) == len(rules['fields'])*rules['curves_per_field'] and
        not errors and all(v['verified'] for v in cells))
    engine_totals = {engine: dict(sum((Counter(costs.engine_arithmetic(v)[engine]) for v in physical.values()), Counter())) for engine in costs.ENGINES}
    if full and any(engine_totals[engine] != dict(verified_engines[engine]) for engine in costs.ENGINES):
        raise ValueError('physical and independently checked query-engine counter conservation')
    metrics = dict(schema='prime-field-a13-metrics/v1', panel_complete=full, physical_attempts=1,
        planned_systems=len(plans), planned_solver_calls=sum(len(methods(d)) for d in plans.values()),
        verified_systems=sum(v['verified'] for v in cells), unknown_systems=sum(not v['verified'] for v in cells),
        verified_solver_calls=sum(len(methods(v)) for v in cells if v['verified']), columns=COLS,
        rows=[[v.get(k) for k in COLS] for v in cells], physical_counters={k: dict(v) for k, v in physical.items()},
        observed_arm_counters={k: dict(v) for k, v in observed.items()}, query_engine_totals=engine_totals,
        closed_curve_checkpoints=checkpoints, source_commit=execution['source_commit'],
        protocol_sha256=execution['protocol_sha256'], partial_work_unknown=not full)
    write_once(args.run/'metrics.json', metrics, compact=True)
    paired = []
    known = {(v['descriptor']['cell_id'], v['descriptor']['target_policy'], v['descriptor']['target_prefix']): v
             for v in cold if v['descriptor']['base_arm'] == 'known'}
    for norm in cold:
        desc = norm['descriptor']
        if desc['base_arm'] != 'norm':
            continue
        match = known.get(tuple(desc[k] for k in ('cell_id', 'target_policy', 'target_prefix')))
        if not match:
            continue
        for engine in costs.ENGINES:
            a = dict(identified_mask=match['identified_mask'], counters=match['solver_engine_counters']['known_direct'][engine])
            b = dict(identified_mask=norm['identified_mask'], counters=norm['solver_engine_counters']['sparse_joint'][engine])
            dimensions = sorted(a['counters'].keys() | b['counters'].keys())
            paired.append(dict(norm_case_id=norm['case_id'], known_case_id=match['case_id'], query_engine=engine,
                known_mask=a['identified_mask'], norm_mask=b['identified_mask'],
                known_dominates_arithmetic=compare(a, b, ARITHMETIC), norm_dominates_arithmetic=compare(b, a, ARITHMETIC),
                known_dominates_retained=compare(a, b, dimensions), norm_dominates_retained=compare(b, a, dimensions)))
    analysis = dict(schema='prime-field-a13-analysis/v1', panel_complete=full, cells=cells,
        cold_views=cold, matched_comparisons=paired, curves=curves, errors=errors,
        diagnostic_resources=execution, metrics_sha256=digest(args.run/'metrics.json'),
        inference='Different point bases: exact target masks and conditional counter vectors only; no cross-base Delta/rank dominance. Known supplied equations are not learned relations. Reused known results across six source schedules and two scopes are dependent, not fresh trials. Unexpanded generation/hash/pow/checker/Python/NumPy-internal/OS/IO costs and unisolated clocks prevent calibrated whole-attack/runtime claims. Producer local controls, no trusted signed standing.')
    write_once(args.run/'analysis.json', analysis, compact=True)
    prior.encode_large(args.run/'analysis.json')
    export = tools().export_skeleton(protocol, str(args.protocol.resolve()), 'local', 'A13-'+args.run.name)
    export['producer'] = dict(runtime='codex', model=None, session=None, role='executor')
    export['source'] = dict(repo='crypto-autoresearcher', commit=execution['observed_git_head'], dirty=host['git_dirty'])
    export['host'].update(path='host.json', sha256=digest(args.run/'host.json'), summary={k: host[k] for k in export['host']['summary']})
    export['runs'] = []
    for cell in cells:
        for method in methods(cell):
            idx = len(export['runs'])
            counted = {k: cell[k] for k in COLS if k in cell and type(cell[k]) is int}
            if cell['verified']:
                counted.update({'fr_'+op: cell['solver_counters'][method].get('Fr.field_'+op, 0) for op in ('add', 'sub', 'mul', 'inv')})
            export['runs'].append(tools().run_row(run_id='A13-'+str(idx), arm=export_arm(method), instance_id=str(cell['case_id']),
                seed=0, replicate=0, warmup=False, status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'interrupted',
                measurements=dict(counted={k: v for k, v in counted.items() if k in {d['id'] for d in protocol['metrics']['primary']}},
                    counters={}, wall_seconds=None, wall_valid=False, cpu_user_seconds=None, cpu_sys_seconds=None, max_rss_bytes=None),
                isolation=dict(tier=None, contended=None, blockers=['sharedhost']),
                verification=dict(status='verified' if cell['verified'] else 'not_run', verifier='producer separately coded group/dense/oracle controls; no signed standing'),
                started_at=execution['started_at'], finished_at=execution['finished_at'], worker=execution['owner']))
    for arm in export['arms']:
        arm.update(binary_sha256=host['executable_sha256'], commit=execution['source_commit'])
    export['backend_record'] = dict(physical_attempts=1, planned_systems=len(plans), planned_solver_calls=len(export['runs']),
        verified_solver_calls=metrics['verified_solver_calls'], physical_counters=metrics['physical_counters'],
        observed_arm_counters=metrics['observed_arm_counters'], partial_work_unknown=not full)
    export['files'] = [tools().file_entry(args.run, str(path.relative_to(args.run)), 'raw') for path in sorted(args.run.rglob('*'))
                       if path.is_file() and path.name != '.gitignore']
    export['analysis']['script'] = dict(path=os.path.relpath(HERE/'analyze.py', args.run.resolve()),
        sha256=digest(HERE/'analyze.py'), bytes=(HERE/'analyze.py').stat().st_size)
    export['analysis']['outputs'] = [tools().file_entry(args.run, name, 'analysis') for name in ('analysis.json', 'metrics.json')]
    export['flow'] = tools().compute_flow(export['runs'])
    findings = tools().schema_errors(export, 'experiment.export/v1') or tools().lint_export(export, protocol, args.run, True)
    if findings:
        raise ValueError(json.dumps(findings))
    write_once(args.run/'export.json', export, compact=True)
    prior.encode_large(args.run/'export.json')
    print(json.dumps(dict(panel_complete=full, verified_systems=metrics['verified_systems'],
        verified_solver_calls=metrics['verified_solver_calls'], unknown_systems=metrics['unknown_systems'])))


if __name__ == '__main__':
    main()
