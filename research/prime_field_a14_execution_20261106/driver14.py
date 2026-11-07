"""One admitted A14 attempt, all fixed programs, native certificates and audits."""
import argparse
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter, process_time
import json

from shared import core, solver, check_source, batch_check
from baseline import checker
from guards import NATIVE_CAPABILITY
import public_base, check_base, mixed_collection, check_mixed, affine_branch
import native_case, partial_solver, check_partial, known_checks
import information, check_information
from target_cache import TargetCache
from custody14 import ROOT, SOURCES, PARAMETERS, load, write_once, descriptors, methods
from streams14 import append, close_encodings, checkpoint_curve
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
    result['phases'], result['counters'] = list(meter.phases), solver.counters(meter.phases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'protocol', 'release', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('fresh output required')
    admission = admit(ROOT, args.protocol, args.inputs, SOURCES, PARAMETERS, args.release)
    rules = load(args.inputs)
    plans = dict(descriptors(rules))
    if len(plans) != rules['systems'] or sum(len(methods(v)) for v in plans.values()) != rules['solver_calls']:
        raise ValueError('fixed case/solver census')
    args.out.mkdir(parents=True)
    write_once(args.out/'admission.json', admission)
    with (args.out/'generation.events.jsonl').open('x') as journal:
        event = lambda v: append(journal, v)
        try:
            generated = core.generate(rules, event, core._NATIVE_CAPABILITY)
            write_once(args.out/'generated.json', generated)
            def generation_check():
                value = check_source.check_generation(rules, generated)
                value['field_prime_selection'] = batch_check.field_selection(rules, generated)
                return value
            write_once(args.out/'generation-check.json', timed(generation_check))
        except BaseException as error:
            event(dict(kind='failure', error_type=type(error).__name__, error=str(error)))
            raise
    count, calls, audits, curves = 0, 0, 0, 0
    for original in generated['cells']:
        cid = original['id']
        with ExitStack() as stack:
            streams = {name: stack.enter_context((args.out/(cid+'.'+name+'.jsonl')).open('x'))
                       for name in ('events', 'branches', 'case-inputs', 'solver-outputs', 'case-checks', 'information', 'information-checks')}
            def event(value): return append(streams['events'], value)
            try:
                # All independent paid constructors and base choices precede targets.
                built = {}
                for size in rules['public_base_sizes']:
                    emit = lambda value, size=size: event(dict(public_base_size=size, **value))
                    built[size] = public_base.build(original, rules, size, emit, NATIVE_CAPABILITY)
                    write_once(args.out/(cid+'.base'+str(size)+'.json'), built[size], compact=True)
                    write_once(args.out/(cid+'.base'+str(size)+'-check.json'),
                               timed(lambda size=size: check_base.check(original, rules, size, built[size])))
                prepared = {}
                for base in rules['base_arms']:
                    emit = lambda value, base=base: event(dict(base_arm=base, **value))
                    prepared[base] = (mixed_collection.prepare(original, rules, built[16] if base == 'hybrid' else None,
                        emit, NATIVE_CAPABILITY) if base in ('norm', 'hybrid') else
                        mixed_collection.prepare_known(built[int(base[5:])], rules, emit, NATIVE_CAPABILITY))
                    write_once(args.out/(cid+'.'+base+'.prelude.json'), prepared[base], compact=True)
                    check = (lambda base=base: check_mixed.preparation(original, rules, built[16] if base == 'hybrid' else None, prepared[base])) if base in ('norm', 'hybrid') else (
                        lambda base=base: check_mixed.known_preparation(original, rules, built[int(base[5:])], prepared[base]))
                    write_once(args.out/(cid+'.'+base+'.prelude-check.json'), timed(check))
                target_meter = core.ProgressMeter(original['fixture'], event, dict(kind='shared_public_targets'))
                targets = target_meter.stage('target_generation', lambda: core.old.targets(original, rules, target_meter, event))
                write_once(args.out/(cid+'.targets.json'), dict(generation=targets, phases=target_meter.phases, counters=target_meter.counters()))
                write_once(args.out/(cid+'.targets-check.json'), timed(lambda: check_mixed.targets(original, rules, targets)))
                norm_cases = {}
                for base in rules['base_arms']:
                    emit = lambda value, base=base: event(dict(base_arm=base, **value))
                    prep = prepared[base]
                    cell, source_program = prep['cell'], base in ('norm', 'hybrid')
                    f = cell['fixture']
                    collected = (mixed_collection.collect if source_program else mixed_collection.collect_known)(
                        prep, targets, rules, emit, NATIVE_CAPABILITY)
                    write_once(args.out/(cid+'.'+base+'.source.json'), dict(cell=cell, collection=collected), compact=True)
                    wall, cpu = perf_counter(), process_time()
                    collection_check, oracle = check_mixed.collection(prep, rules, collected)
                    write_once(args.out/(cid+'.'+base+'.source-check.json'), dict(verification=collection_check,
                        wall_seconds=perf_counter()-wall, cpu_seconds=process_time()-cpu, wall_valid=False))
                    if base == 'norm':
                        recipe_meter = core.ProgressMeter(original['fixture'], event, dict(kind='target_recipes'))
                        recipes = recipe_meter.stage('target_recipes', lambda: core.recipes(original, collected,
                            rules, recipe_meter, event, core._NATIVE_CAPABILITY))
                        checker.recipes(original, rules, recipes)
                        write_once(args.out/(cid+'.target-recipes.json'), dict(selection=recipes,
                            phases=recipe_meter.phases, counters=recipe_meter.counters()))
                    cache = TargetCache(collected.query_index, collected['natural_records'], rules, emit, NATIVE_CAPABILITY)
                    group_oracle = checker.GroupOracle(f, targets['targets'])
                    schedules = [kind+str(seed) for seed in rules['seeds'] for kind in ('ap', 'hash')] if source_program else ['known']
                    prefix = rules['sources'] if source_program else 0
                    for schedule in schedules:
                        for policy in rules['target_policies']:
                            context = dict(source_schedule=schedule, source_prefix=prefix, target_policy=policy)
                            branch = affine_branch.build(cell, collected, rules, recipes['policies'][policy],
                                schedule, prefix, policy, cache, emit, NATIVE_CAPABILITY)
                            receipt = append(streams['branches'], dict(base_arm=base, context=context, branch=branch))
                            emit(dict(kind='branch_output', context=context, record=receipt))
                            checked = timed(lambda: checker.branch(cell, collected, rules, recipes['policies'][policy], branch, cache, group_oracle))
                            emit(dict(kind='branch_checked', context=context, **checked))
                            for budget in rules['target_prefixes']:
                                for scope in (rules['norm_scopes'] if source_program else [rules['known_scope']]):
                                    desc = dict(cell_id=cid, base_arm=base, **context, target_prefix=budget, scope=scope)
                                    if plans.get(count) != desc: raise ValueError('descriptor execution order differs')
                                    assembly = core.ProgressMeter(f, emit, dict(kind='native_matrix_assembly', case_id=count))
                                    case = assembly.stage('native_matrix_assembly', lambda: native_case.build(prep, collected, branch, cache, budget, scope, assembly))
                                    receipt = append(streams['case-inputs'], dict(case_id=count, descriptor=desc, case=case, shared_phases=assembly.phases))
                                    emit(dict(kind='case_input', case_id=count, descriptor=desc, record=receipt, shared_phases=assembly.phases))
                                    outputs = []
                                    for method in methods(desc):
                                        meter, result = solver.Meter(f), None
                                        try:
                                            result = partial_solver.solve(case, prep['known'], prep['basis'], meter) if method == 'partial_joint' else solver.solve(case, method, meter)
                                            public_verify(result, case, f, meter)
                                            receipt = append(streams['solver-outputs'], dict(case_id=count, arm=method, result=result))
                                            emit(dict(kind='solver_complete', case_id=count, descriptor=desc, arm=method, record=receipt, counters=result['counters']))
                                            outputs.append(result)
                                            calls += 1
                                        except BaseException as error:
                                            emit(dict(kind='solver_failed', case_id=count, descriptor=desc, arm=method,
                                                partial_result=result, phases=meter.phases, error_type=type(error).__name__, error=str(error)))
                                            raise
                                    def check_case():
                                        if core.source.code(case) != core.source.code(native_case.expected(prep, collected, branch, cache, budget, scope)):
                                            raise ValueError('independent native case assembly')
                                        partial = check_partial.check(case, prep['known'], prep['basis'], outputs[0], f)
                                        joint = known_checks.joint_case(case, outputs[1], f)
                                        if [(v['identifiable'], v['scalar']) for v in outputs[0]['recoveries']] != [(v['identifiable'], v['scalar']) for v in outputs[1]['recoveries']]:
                                            raise ValueError('partial/native joint outcomes differ')
                                        return dict(checked=True, partial=partial, joint=joint)
                                    checked = timed(check_case)
                                    receipt = append(streams['case-checks'], dict(case_id=count, descriptor=desc, **checked))
                                    emit(dict(kind='case_checked', case_id=count, descriptor=desc, record=receipt, verification=checked['verification']))
                                    key = (schedule, policy, budget, scope)
                                    if base == 'norm': norm_cases[key] = (count, case)
                                    if base == 'hybrid':
                                        norm_id, old_case = norm_cases[key]
                                        diagnostic_meter = core.ProgressMeter(f, emit,
                                            dict(kind='information_diagnostic', case_id=count, norm_case_id=norm_id))
                                        diagnostic, output_receipt = None, None
                                        try:
                                            diagnostic = information.compare(old_case, prepared['norm'], case, prep, diagnostic_meter)
                                            output_receipt = append(streams['information'], dict(norm_case_id=norm_id,
                                                hybrid_case_id=count, descriptor=desc, result=diagnostic))
                                            emit(dict(kind='information_output', case_id=count, norm_case_id=norm_id,
                                                record=output_receipt, counters=diagnostic['counters']))
                                            checked = timed(lambda: check_information.check(old_case, prepared['norm'], case, prep, diagnostic))
                                            receipt = append(streams['information-checks'], dict(norm_case_id=norm_id,
                                                hybrid_case_id=count, descriptor=desc, **checked))
                                            emit(dict(kind='information_checked', case_id=count, norm_case_id=norm_id,
                                                record=receipt, verification=checked['verification']))
                                            audits += 1
                                        except BaseException as error:
                                            emit(dict(kind='information_failed', case_id=count, norm_case_id=norm_id,
                                                output_record=output_receipt, phases=diagnostic_meter.phases,
                                                error_type=type(error).__name__, error=str(error)))
                                            raise
                                    count += 1
                    write_once(args.out/(cid+'.'+base+'.query-cache.json'), dict(records=cache.records,
                        engine_records=cache.engines.records[cache.engine_start:], engine_start=cache.engine_start,
                        phases=cache.meter.phases, counters=cache.meter.counters()), compact=True)
                    write_once(args.out/(cid+'.'+base+'.query-check.json'), timed(lambda: check_mixed.target_cache(prep, collected, cache, oracle)))
                write_once(args.out/(cid+'.complete.json'), dict(complete=True, cases_checked=count,
                    solver_calls=calls, information_audits=audits, curve_index=curves))
            except BaseException as error:
                event(dict(kind='failure', error_type=type(error).__name__, error=str(error), partial_case=getattr(error, 'partial_case', None)))
                raise
        curves += 1
        close_encodings(args.out, cid)
        if rules['closed_curve_checkpoint']: checkpoint_curve(args.out.parent, cid, count, curves)
    if count != rules['systems'] or calls != rules['solver_calls'] or audits != rules['information_audits']:
        raise ValueError('incomplete fixed census')
    print(json.dumps(dict(complete=True, systems=count, solver_calls=calls, information_audits=audits,
        physical_processes=1, closed_curve_checkpoints=curves, software_control=rules.get('software_control', False))))


if __name__ == '__main__':
    main()
