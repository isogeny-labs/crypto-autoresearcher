"""Admitted matched bases, streamed outputs and source-free known control."""
import argparse
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter, process_time
import json

from baseline import core, solver, checker, check_source, check_solver, batch_check, NATIVE_CAPABILITY
import paid_base, known_collection, known_checks, known_solver
from custody import ROOT, SOURCES, PARAMETERS, load, write_once, descriptors, methods
from streams import append, close_encodings, checkpoint_curve
from crypto_autoresearcher.index_calculus.execution_gate import admit


def timed(operation):
    wall, cpu = perf_counter(), process_time()
    value = operation()
    return dict(verification=value, wall_seconds=perf_counter()-wall,
                cpu_seconds=process_time()-cpu, wall_valid=False)


def public_verify(result, case, fixture, meter):
    def operation():
        for rec, target in zip(result['recoveries'], case['targets'], strict=True):
            if rec['identifiable']:
                if not meter.equal(meter.e.mul(rec['scalar'], tuple(fixture['P'])), tuple(target['point'])):
                    raise ValueError('public target equation')
                meter.other['public_target_certificates_verified'] += 1
    meter.stage('public_target_verification', operation)
    result['phases'] = list(meter.phases)
    result['counters'] = solver.counters(meter.phases)


def main():
    parser = argparse.ArgumentParser()
    for name in ('inputs', 'protocol', 'release', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('fresh output required')
    admission = admit(ROOT, args.protocol, args.inputs, SOURCES, PARAMETERS, args.release)
    rules = load(args.inputs)
    plans = dict(descriptors(rules))
    if len(plans) != rules['systems'] or sum(len(methods(v)) for v in plans.values()) != rules['solver_calls']:
        raise ValueError('case or solver census differs')
    args.out.mkdir(parents=True)
    write_once(args.out/'admission.json', admission)
    with (args.out/'generation.events.jsonl').open('x') as stream:
        event = lambda v: append(stream, v)
        try:
            generated = core.generate(rules, event, core._NATIVE_CAPABILITY)
            write_once(args.out/'generated.json', generated)
            def check_generation():
                value = check_source.check_generation(rules, generated)
                value['field_prime_selection'] = batch_check.field_selection(rules, generated)
                return value
            write_once(args.out/'generation-check.json', timed(check_generation))
        except BaseException as error:
            event(dict(kind='failure', error_type=type(error).__name__, error=str(error)))
            raise
    count, calls, curves = 0, 0, 0
    for original in generated['cells']:
        cid = original['id']
        with ExitStack() as stack:
            streams = {name: stack.enter_context((args.out/(cid+'.'+name+'.jsonl')).open('x'))
                       for name in ('events', 'branches', 'case-inputs', 'solver-outputs', 'case-checks')}
            def event(value):
                return append(streams['events'], value)
            try:
                # Fix the replacement base before generating or reading targets.
                built = paid_base.build(original, rules, lambda v: event(dict(base_arm='known', **v)),
                                        NATIVE_CAPABILITY)
                write_once(args.out/(cid+'.known.base.json'), built, compact=True)
                write_once(args.out/(cid+'.known.base-check.json'), timed(lambda: known_checks.public_base(original, rules, built)))
                norm = core.collect_sources(original, rules, lambda v: event(dict(base_arm='norm', **v)), core._NATIVE_CAPABILITY)
                write_once(args.out/(cid+'.norm.source.json'), dict(cell=original, collection=norm), compact=True)
                def norm_check():
                    value, oracle = check_source.collection(original, rules, norm)
                    value['query_engines'] = batch_check.records(original, norm['query_engine_records'],
                        [t['point'] for t in norm['target_generation']['targets']] +
                        [v['point'] for arm in norm['selection']['orders'] for v in norm['arms'][arm]['sources']])
                    return value, oracle
                started = perf_counter(), process_time()
                norm_checked, norm_oracle = norm_check()
                write_once(args.out/(cid+'.norm.source-check.json'), dict(verification=norm_checked,
                    wall_seconds=perf_counter()-started[0], cpu_seconds=process_time()-started[1], wall_valid=False))
                known = known_collection.collect(built, norm['target_generation'], rules,
                    lambda v: event(dict(base_arm='known', **v)), NATIVE_CAPABILITY)
                write_once(args.out/(cid+'.known.source.json'), dict(cell=built['cell'], collection=known), compact=True)
                started = perf_counter(), process_time()
                known_checked, known_oracle = known_checks.collection(built, norm['target_generation'], known)
                known_checked['query_engines'] = batch_check.records(built['cell'], known['query_engine_records'],
                    [t['point'] for t in norm['target_generation']['targets']])
                write_once(args.out/(cid+'.known.source-check.json'), dict(verification=known_checked,
                    wall_seconds=perf_counter()-started[0], cpu_seconds=process_time()-started[1], wall_valid=False))
                recipe_meter = core.ProgressMeter(original['fixture'], event, dict(kind='target_recipes'))
                recipes = recipe_meter.stage('target_recipes', lambda: core.recipes(original, norm, rules,
                    recipe_meter, event, core._NATIVE_CAPABILITY))
                checker.recipes(original, rules, recipes)
                write_once(args.out/(cid+'.target-recipes.json'), dict(selection=recipes,
                    phases=recipe_meter.phases, counters=recipe_meter.counters()))
                for base, cell, collected, triple_oracle in (
                    ('norm', original, norm, norm_oracle), ('known', built['cell'], known, known_oracle)):
                    emit = lambda v, base=base: event(dict(base_arm=base, **v))
                    cache = core.QueryCache(cell, collected, rules, emit, core._NATIVE_CAPABILITY)
                    group_oracle = checker.GroupOracle(cell['fixture'], collected['target_generation']['targets'])
                    schedules = [kind+str(seed) for seed in rules['seeds'] for kind in ('ap', 'hash')] if base == 'norm' else ['known']
                    source_prefix = rules['sources'] if base == 'norm' else 0
                    for schedule in schedules:
                        for policy in rules['target_policies']:
                            context = dict(source_schedule=schedule, source_prefix=source_prefix, target_policy=policy)
                            branch = core.construct_branch(cell, collected, rules, recipes['policies'][policy],
                                schedule, source_prefix, policy, cache, emit, core._NATIVE_CAPABILITY)
                            receipt = append(streams['branches'], dict(base_arm=base, context=context, branch=branch))
                            event(dict(kind='branch_output', base_arm=base, context=context, record=receipt))
                            checked = timed(lambda: checker.branch(cell, collected, rules, recipes['policies'][policy], branch, cache, group_oracle))
                            event(dict(kind='branch_checked', base_arm=base, context=context, **checked))
                            for budget in rules['target_prefixes']:
                                for scope in (rules['norm_scopes'] if base == 'norm' else [rules['known_scope']]):
                                    desc = dict(cell_id=cid, base_arm=base, **context, target_prefix=budget, scope=scope)
                                    if plans.get(count) != desc:
                                        raise ValueError('descriptor execution order differs')
                                    projection = solver.Meter(cell['fixture'])
                                    internal_scope = scope if base == 'norm' else 'anchors'
                                    case = projection.stage('shared_projection', lambda:
                                        known_collection.case_input(cell, collected, branch, cache, budget, projection)
                                        if base == 'known' else core.case_input(cell, collected,
                                            branch, cache, budget, internal_scope, projection))
                                    receipt = append(streams['case-inputs'], dict(case_id=count, descriptor=desc,
                                        case=case, shared_phases=projection.phases))
                                    event(dict(kind='case_input', case_id=count, descriptor=desc, record=receipt, shared_phases=projection.phases))
                                    outputs = []
                                    for method in methods(desc):
                                        meter = solver.Meter(cell['fixture'])
                                        result = None
                                        try:
                                            result = known_solver.solve(case, built['signed_labels'], meter) if method == 'known_direct' else solver.solve(case, method, meter)
                                            public_verify(result, case, cell['fixture'], meter)
                                            receipt = append(streams['solver-outputs'], dict(case_id=count, arm=method, result=result))
                                            event(dict(kind='solver_complete', case_id=count, descriptor=desc, arm=method,
                                                record=receipt, counters=result['counters']))
                                            outputs.append(result)
                                            calls += 1
                                        except BaseException as error:
                                            event(dict(kind='solver_failed', case_id=count, descriptor=desc, arm=method,
                                                partial_result=result, phases=meter.phases, error_type=type(error).__name__, error=str(error)))
                                            raise
                                    def verify_case():
                                        expected = checker.expected_case(cell, collected, branch, cache, budget, internal_scope)
                                        if core.source.code(case) != core.source.code(expected):
                                            raise ValueError('independent case projection')
                                        value = known_checks.joint_case(case, next(v for v in outputs if v['arm'] == 'sparse_joint'), cell['fixture'])
                                        if base == 'norm':
                                            value = check_solver.check(case, outputs, cell['fixture'])
                                        if base == 'known':
                                            value['direct'] = known_checks.known_case(case, built['signed_labels'], outputs[0], cell['fixture'])
                                            if [(v['identifiable'], v['scalar']) for v in outputs[0]['recoveries']] != [(v['identifiable'], v['scalar']) for v in outputs[1]['recoveries']]:
                                                raise ValueError('known direct/joint outcome mismatch')
                                        return value
                                    checked = timed(verify_case)
                                    receipt = append(streams['case-checks'], dict(case_id=count, descriptor=desc, **checked))
                                    event(dict(kind='case_checked', case_id=count, descriptor=desc, record=receipt, verification=checked['verification']))
                                    count += 1
                    write_once(args.out/(cid+'.'+base+'.query-cache.json'), dict(records=cache.records,
                        engine_records=cache.engines.records[cache.engine_start:], phases=cache.meter.phases,
                        counters=cache.meter.counters()), compact=True)
                    def verify_queries():
                        value = checker.query_cache(cell, collected, cache, triple_oracle)
                        value['query_engines'] = batch_check.records(cell, cache.engines.records[cache.engine_start:],
                            [v['point'] for v in cache.records if not v['seeded_natural']], start=cache.engine_start)
                        return value
                    write_once(args.out/(cid+'.'+base+'.query-check.json'), timed(verify_queries))
                write_once(args.out/(cid+'.complete.json'), dict(complete=True, cases_checked=count,
                    solver_calls=calls, curve_index=curves))
            except BaseException as error:
                event(dict(kind='failure', error_type=type(error).__name__, error=str(error)))
                raise
        curves += 1
        close_encodings(args.out, cid)
        if rules['closed_curve_checkpoint']:
            checkpoint_curve(args.out.parent, cid, count, curves)
    if count != rules['systems'] or calls != rules['solver_calls']:
        raise ValueError('incomplete fixed census')
    print(json.dumps(dict(complete=True, systems=count, solver_calls=calls,
        physical_processes=1, closed_curve_checkpoints=curves, software_control=rules.get('software_control', False))))


if __name__ == '__main__':
    main()
