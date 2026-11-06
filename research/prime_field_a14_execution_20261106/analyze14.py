"""Stream-bound A14 measurements, owned cold references and unified export."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path

from shared import core
from baseline import costs
from custody14 import HERE, ROOT, INPUTS, load, write_once, digest, tools, descriptors, methods, arm_id, export_arm
from streams14 import lines
from cold14 import prior, total, collection_view, dominates, ARITHMETIC

COLS = ['case_id', 'cell_id', 'base_arm', 'source_schedule', 'source_prefix', 'target_policy',
    'target_prefix', 'scope', 'verified', 'base_columns', 'native_columns', 'supplied_columns',
    'source_rank', 'native_source_rank', 'outside_rank', 'delta', 'after_cancellation_rank',
    'identified_targets', 'identified_mask', 'source_rows', 'target_rows', 'decomposition_rows', 'knowledge_rows']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    args = parser.parse_args()
    rules, protocol = load(INPUTS), load(args.protocol)
    raw, plans = args.run/'raw', dict(descriptors(rules))
    execution, host = load(args.run/'execution.json'), load(args.run/'host.json')
    errors, rows, cold, curves, checkpoints, audits = [], {}, [], [], [], []
    refs, branch_refs, info_refs = {}, {}, {}
    physical, observed = defaultdict(Counter), defaultdict(Counter)
    checked_engines = {engine: Counter() for engine in costs.ENGINES}

    def read(path):
        try: return prior.optional(path)
        except Exception as error:
            errors.append(dict(path=str(path), error_type=type(error).__name__, error=str(error)))

    def readlines(path):
        try: yield from lines(path)
        except Exception as error:
            errors.append(dict(path=str(path), error_type=type(error).__name__, error=str(error)))

    generation = read(raw/'generation-check.json')
    expected_curves = len(rules['fields'])*rules['curves_per_field']
    generation_valid = bool(generation and generation['verification']['checked'] and generation['verification']['curves'] == expected_curves)
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid = 'p'+str(field['p'])+'-i'+str(ci)
            for event in readlines(raw/(cid+'.events.jsonl')):
                kind, base = event['kind'], event.get('base_arm')
                if kind == 'affine_phase':
                    label = event['context'].get('kind', 'target_construction')
                    owner = base or ('public_base'+str(event['public_base_size']) if 'public_base_size' in event else 'shared')
                    physical[owner+'.'+label].update(event['phase']['counters'])
                elif kind == 'branch_output':
                    branch_refs[cid, base, json.dumps(event['context'], sort_keys=True)] = event['record']
                elif kind in ('case_input', 'case_checked', 'solver_complete'):
                    label = 'input' if kind == 'case_input' else 'check' if kind == 'case_checked' else event['arm']
                    refs[event['case_id'], label] = event['record']
                    if kind == 'solver_complete': observed[arm_id(event['descriptor'], event['arm'])].update(event['counters'])
                elif kind == 'information_checked':
                    info_refs[event['case_id']] = event['record']
                    physical['hybrid.information_diagnostic'].update(event['counters'])
                elif kind == 'solver_failed':
                    observed[arm_id(event['descriptor'], event['arm'])].update(total(event['phases']))
                    errors.append(dict(cell_id=cid, event=event))
                elif kind == 'failure': errors.append(dict(cell_id=cid, event=event))
            preludes = {base: read(raw/(cid+'.'+base+'.prelude.json')) for base in rules['base_arms']}
            sources = {base: read(raw/(cid+'.'+base+'.source.json')) for base in rules['base_arms']}
            caches = {base: read(raw/(cid+'.'+base+'.query-cache.json')) for base in rules['base_arms']}
            checks = {base: [read(raw/(cid+'.'+base+'.'+suffix+'.json'))
                for suffix in ('prelude-check', 'source-check', 'query-check')] for base in rules['base_arms']}
            built = {size: read(raw/(cid+'.base'+str(size)+'.json')) for size in rules['public_base_sizes']}
            build_checks = [read(raw/(cid+'.base'+str(size)+'-check.json')) for size in rules['public_base_sizes']]
            targets, target_check = read(raw/(cid+'.targets.json')), read(raw/(cid+'.targets-check.json'))
            recipes, complete = read(raw/(cid+'.target-recipes.json')), read(raw/(cid+'.complete.json'))
            curve_valid = bool(generation_valid and all(preludes.values()) and all(sources.values()) and all(caches.values())
                and all(built.values()) and targets and recipes and complete and complete['complete']
                and target_check and target_check['verification']['checked']
                and all(v and v['verification']['checked'] for v in build_checks)
                and all(v and v['verification']['checked'] for group in checks.values() for v in group))
            if rules['closed_curve_checkpoint']:
                receipt = read(args.run/('checkpoint-'+cid+'.json'))
                ordinal = len(checkpoints)+1
                valid = prior.checkpoint_valid(receipt, cid, ordinal, ordinal*len(plans)//expected_curves)
                checkpoints.append(dict(cell_id=cid, valid=valid, receipt=receipt))
                if not valid: errors.append(dict(cell_id=cid, error='missing/failed closed-curve canonical checkpoint'))
            if curve_valid:
                curves.append(dict(cell_id=cid, fixtures={base: preludes[base]['cell']['fixture'] for base in rules['base_arms']}))
                for base in rules['base_arms']:
                    for check in checks[base][1:]:
                        for engine in costs.ENGINES:
                            checked_engines[engine].update(check['verification']['query_engines']['engine_totals'][engine])
            branches, outputs, checked = (iter(readlines(raw/(cid+'.'+name+'.jsonl')))
                for name in ('branches', 'solver-outputs', 'case-checks'))
            current = None
            for item in readlines(raw/(cid+'.case-inputs.jsonl')):
                idx, desc = item['case_id'], item['descriptor']
                if plans.get(idx) != desc or idx in rows: raise ValueError('fixed case descriptor/order')
                base = desc['base_arm']
                context = {key: desc[key] for key in ('source_schedule', 'source_prefix', 'target_policy')}
                if current is None or current['base_arm'] != base or current['context'] != context:
                    current = next(branches, None)
                    if current and (current['base_arm'] != base or current['context'] != context or not prior.record_binding(
                        current, branch_refs.get((cid, base, json.dumps(context, sort_keys=True))))):
                        raise ValueError('branch stream order/journal binding')
                results, check = [next(outputs, None) for method in methods(desc)], next(checked, None)
                valid = bool(curve_valid and current and check and check['case_id'] == idx and check['descriptor'] == desc
                    and check['verification']['checked'] and all(v and v['case_id'] == idx and v['arm'] == method
                        for method, v in zip(methods(desc), results, strict=True)))
                row = dict(case_id=idx, **desc, verified=valid)
                if valid:
                    for label, value in [('input', item), ('check', check), *[(method, value) for method, value in zip(methods(desc), results, strict=True)]]:
                        if not prior.record_binding(value, refs.get((idx, label))): raise ValueError('case stream/journal binding')
                    case, info = item['case'], check['verification']['partial']
                    row.update(base_columns=info['original_unknown_columns'], native_columns=case['width'], supplied_columns=info['supplied_columns'],
                        source_rank=info['source_rank'], native_source_rank=info['native_source_rank'], outside_rank=info['outside_rank'],
                        delta=info['delta'], after_cancellation_rank=info['base_rank_after_cancellation'], identified_targets=info['identified'],
                        source_rows=len(case['source']), target_rows=len(case['target']),
                        decomposition_rows=sum(v['kind'] == 'decomposition' for v in case['target']),
                        knowledge_rows=sum(v['kind'] != 'decomposition' for v in case['target']),
                        assembly_counters=total(item['shared_phases']), solver_counters={})
                    for method, result in zip(methods(desc), results, strict=True):
                        value = result['result']
                        if total(value['phases']) != value['counters']: raise ValueError('solver phase conservation')
                        mask = sum(1 << v['target_index'] for v in value['recoveries'] if v['identifiable'])
                        if 'identified_mask' in row and row['identified_mask'] != mask: raise ValueError('partial/native joint target mask')
                        row['identified_mask'], row['solver_counters'][method] = mask, value['counters']
                    view = collection_view(base, preludes[base], sources[base]['collection'], built,
                        current['branch'], caches[base], recipes, targets, desc['target_prefix'], rules)
                    options = {method: {engine: dict(Counter(view['engine_collection_counters'][engine])+
                        Counter(row['assembly_counters'])+Counter(row['solver_counters'][method])) for engine in costs.ENGINES}
                        for method in methods(desc)}
                    cold.append(dict(case_id=idx, descriptor=desc, identified_mask=row['identified_mask'], collection=view, solver_engine_counters=options))
                rows[idx] = row
            for item in readlines(raw/(cid+'.information.jsonl')):
                idx, norm_idx = item['hybrid_case_id'], item['norm_case_id']
                if not prior.record_binding(item, info_refs.get(idx)): raise ValueError('information stream/journal binding')
                if plans.get(idx) != item['descriptor'] or plans[idx]['base_arm'] != 'hybrid' or plans.get(norm_idx, {}).get('base_arm') != 'norm':
                    raise ValueError('information matched case identities')
                if any(plans[idx][key] != plans[norm_idx][key] for key in plans[idx] if key != 'base_arm'):
                    raise ValueError('information source/policy/budget/scope differs')
                valid = bool(rows.get(idx, {}).get('verified') and rows.get(norm_idx, {}).get('verified') and item['verification']['checked'])
                audits.append(dict(norm_case_id=norm_idx, hybrid_case_id=idx, descriptor=item['descriptor'], verified=valid,
                    ranks=item['result']['ranks'], increments=item['result']['increments'], delta_vs_old=item['result']['delta_vs_old'],
                    outside_rank=item['verification']['outside_rank'], counters=item['result']['counters'],
                    old_kernel_dimension=len(item['verification']['old_kernel'])))
            if curve_valid and any(next(stream, None) is not None for stream in (branches, outputs, checked)):
                raise ValueError('extra records beyond fixed census')
    cells = [rows.get(idx, dict(case_id=idx, **desc, verified=False)) for idx, desc in plans.items()]
    full = bool(execution['returncode'] == 0 and not execution['timeout'] and not execution['exception']
        and execution['source_unchanged_after'] and len(curves) == expected_curves and not errors
        and all(v['verified'] for v in cells) and len(audits) == rules['information_audits'] and all(v['verified'] for v in audits))
    if len({v['hybrid_case_id'] for v in audits}) != len(audits): raise ValueError('duplicate information audit')
    engines = {engine: dict(sum((Counter(costs.engine_arithmetic(v)[engine]) for v in physical.values()), Counter())) for engine in costs.ENGINES}
    if full and any(engines[engine] != dict(checked_engines[engine]) for engine in costs.ENGINES):
        raise ValueError('physical and independently checked query-engine counters differ')
    metrics = dict(schema='prime-field-a14-metrics/v1', panel_complete=full, physical_attempts=1,
        planned_systems=len(plans), planned_solver_calls=sum(len(methods(d)) for d in plans.values()),
        verified_systems=sum(v['verified'] for v in cells), unknown_systems=sum(not v['verified'] for v in cells),
        verified_solver_calls=sum(len(methods(v)) for v in cells if v['verified']), verified_information_audits=sum(v['verified'] for v in audits),
        columns=COLS, rows=[[v.get(key) for key in COLS] for v in cells],
        physical_counters={key: dict(value) for key, value in physical.items()}, observed_arm_counters={key: dict(value) for key, value in observed.items()},
        query_engine_totals=engines, closed_curve_checkpoints=checkpoints, source_commit=execution['source_commit'],
        protocol_sha256=execution['protocol_sha256'], partial_work_unknown=not full)
    write_once(args.run/'metrics.json', metrics, compact=True)
    index = {(v['descriptor']['base_arm'], *(v['descriptor'][key] for key in ('cell_id', 'target_policy', 'target_prefix'))): v
             for v in cold if v['descriptor']['base_arm'].startswith('known')}
    norm = {tuple(v['descriptor'][key] for key in ('cell_id', 'source_schedule', 'target_policy', 'target_prefix', 'scope')): v
            for v in cold if v['descriptor']['base_arm'] == 'norm'}
    paired = []
    for candidate in cold:
        desc, peers = candidate['descriptor'], []
        if desc['base_arm'] in ('norm', 'hybrid'):
            peers += [index.get((base, *(desc[key] for key in ('cell_id', 'target_policy', 'target_prefix')))) for base in ('known32', 'known48')]
            if desc['base_arm'] == 'hybrid': peers.append(norm.get(tuple(desc[key] for key in ('cell_id', 'source_schedule', 'target_policy', 'target_prefix', 'scope'))))
        elif desc['base_arm'] == 'known48': peers.append(index.get(('known32', *(desc[key] for key in ('cell_id', 'target_policy', 'target_prefix')))))
        for reference in (v for v in peers if v is not None):
            for engine in costs.ENGINES:
                a = dict(identified_mask=candidate['identified_mask'], counters=candidate['solver_engine_counters']['partial_joint'][engine])
                b = dict(identified_mask=reference['identified_mask'], counters=reference['solver_engine_counters']['partial_joint'][engine])
                dimensions = sorted(a['counters'].keys() | b['counters'].keys())
                paired.append(dict(candidate_case_id=candidate['case_id'], reference_case_id=reference['case_id'], query_engine=engine,
                    candidate_mask=a['identified_mask'], reference_mask=b['identified_mask'], candidate_dominates_arithmetic=dominates(a,b,ARITHMETIC),
                    reference_dominates_arithmetic=dominates(b,a,ARITHMETIC), candidate_dominates_retained=dominates(a,b,dimensions), reference_dominates_retained=dominates(b,a,dimensions)))
    analysis = dict(schema='prime-field-a14-analysis/v1', panel_complete=full, cells=cells, cold_views=cold,
        matched_comparisons=paired, information_audits=audits, curves=curves, errors=errors,
        diagnostic_resources=execution, metrics_sha256=digest(args.run/'metrics.json'),
        inference='Matched target identities/cold included vectors; old-base Delta only for matched norm/hybrid coordinates. Supplied unit/cache information precedes newly collected directions; ranks of known32/48 are never cross-base gains. Reused targets/cold views dependent. Separate paid information diagnostics and checker work; unexpanded generation/hash/pow/NumPy/Python/OS/IO and unisolated clocks forbid calibrated complete-cost/runtime advantage. Producer checks/hash custody do not confer trusted signed standing.')
    write_once(args.run/'analysis.json', analysis, compact=True)
    prior.encode_large(args.run/'analysis.json')
    export = tools().export_skeleton(protocol, str(args.protocol.resolve()), 'local', 'A14-'+args.run.name)
    export['producer'] = dict(runtime='codex', model=None, session=None, role='executor')
    export['source'] = dict(repo='crypto-autoresearcher', commit=execution['observed_git_head'], dirty=host['git_dirty'])
    export['host'].update(path='host.json', sha256=digest(args.run/'host.json'), summary={key: host[key] for key in export['host']['summary']})
    export['runs'] = []
    metric_ids = {v['id'] for v in protocol['metrics']['primary']}
    for cell in cells:
        for method in methods(cell):
            counted = {key: cell[key] for key in COLS if key in cell and type(cell[key]) is int and key in metric_ids}
            if cell['verified']: counted.update({'fr_'+op: cell['solver_counters'][method].get('Fr.field_'+op,0) for op in ('add','sub','mul','inv')})
            export['runs'].append(tools().run_row(run_id='A14-'+str(len(export['runs'])), arm=export_arm(method), instance_id=str(cell['case_id']),
                seed=0, replicate=0, warmup=False, status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'interrupted',
                measurements=dict(counted=counted, counters={}, wall_seconds=None, wall_valid=False, cpu_user_seconds=None, cpu_sys_seconds=None, max_rss_bytes=None),
                isolation=dict(tier=None, contended=None, blockers=['sharedhost']),
                verification=dict(status='verified' if cell['verified'] else 'not_run', verifier='producer separate plain-group/dense/oracle checks; no signed standing'),
                started_at=execution['started_at'], finished_at=execution['finished_at'], worker=execution['owner']))
    for arm in export['arms']: arm.update(binary_sha256=host['executable_sha256'], commit=execution['source_commit'])
    export['backend_record'] = dict(physical_attempts=1, planned_systems=len(plans), planned_solver_calls=len(export['runs']),
        verified_solver_calls=metrics['verified_solver_calls'], verified_information_audits=metrics['verified_information_audits'],
        physical_counters=metrics['physical_counters'], observed_arm_counters=metrics['observed_arm_counters'], partial_work_unknown=not full)
    export['files'] = [tools().file_entry(args.run, str(path.relative_to(args.run)), 'raw') for path in sorted(args.run.rglob('*')) if path.is_file() and path.name != '.gitignore']
    export['analysis']['script'] = dict(path=os.path.relpath(HERE/'analyze14.py', args.run.resolve()), sha256=digest(HERE/'analyze14.py'), bytes=(HERE/'analyze14.py').stat().st_size)
    export['analysis']['outputs'] = [tools().file_entry(args.run, name, 'analysis') for name in ('analysis.json', 'metrics.json')]
    export['flow'] = tools().compute_flow(export['runs'])
    findings = tools().schema_errors(export, 'experiment.export/v1') or tools().lint_export(export, protocol, args.run, True)
    if findings: raise ValueError(json.dumps(findings))
    write_once(args.run/'export.json', export, compact=True)
    prior.encode_large(args.run/'export.json')
    print(json.dumps(dict(panel_complete=full, verified_systems=metrics['verified_systems'], verified_solver_calls=metrics['verified_solver_calls'], information_audits=metrics['verified_information_audits'])))


if __name__ == '__main__':
    main()
