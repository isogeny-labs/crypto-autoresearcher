"""Cold references for one actual base/source/policy/budget, without free unions."""
from collections import Counter
from shared import core
from baseline import costs

prior = core.solver.module('_a14_prior_analysis_utilities', 'research/prime_field_a12_execution_20261106/analyze.py')
total = prior.total
ARITHMETIC = tuple(field+'.field_'+op for field in ('Fp', 'Fr') for op in ('add', 'sub', 'mul', 'inv')) + ('query_array_allocated_bytes',)


def collection_view(base, prepared, collected, built, branch, cache, recipes, targets, budget, rules):
    context = branch['context']
    chosen = next(v for v in branch['budgets'] if v['target_prefix'] == budget)
    phases = {v['phase']: v['counters'] for v in cache['phases']}
    ids = sorted({v['query_id'] for v in branch['requests'] if v['step'] <= budget})
    new = [i for i in ids if not cache['records'][i]['seeded_natural']]
    query = Counter()
    for i in new:
        for name in cache['records'][i]['phase_ids']:
            query.update(phases[name])
    prelude = Counter(prepared['counters'])
    source_recipe = Counter()
    if base in ('norm', 'hybrid'):
        recipe_phase = next(v for v in prepared['phases'] if v['phase'] == 'source_schedule_derivation')
        prelude.subtract(recipe_phase['counters'])
        if any(v < 0 for v in prelude.values()): raise ValueError('source recipe partition exceeds physical work')
        schedule = context['source_schedule']
        kind, seed = ('ap', int(schedule[2:])) if schedule.startswith('ap') else ('hash', int(schedule[4:]))
        trace = [v for v in prepared['selection']['trace'] if v['kind'] == kind+'_candidate' and v['seed'] == seed]
        source_recipe['source_hash_attempts'] = len(trace)*(2 if kind == 'ap' else 1)
        if kind == 'ap': source_recipe['ap_horizon_scalar_tests'] = len(trace)*rules['sources']
    common = prelude+Counter(collected['collection_counters'])
    common.update(targets['counters'])
    own_builder = 16 if base == 'hybrid' else int(base[5:]) if base.startswith('known') else None
    base_construction = Counter() if own_builder is None else Counter(built[own_builder]['counters'])
    source = Counter() if base.startswith('known') else Counter(collected['arms'][context['source_schedule']]['counters'])
    hashes = 0 if context['target_policy'] == 'walk' else sum(1 if v['policy'] == 'hash_offset' else 2
        for v in recipes['selection']['trace'] if v['policy'] == context['target_policy'])
    requests = rules['targets']*budget
    lookup = Counter(logical_target_requests=requests, target_cache_lookups=requests,
        target_cache_hits=requests-len(new), target_recipe_hashes=hashes)
    setup = Counter(phases['natural_decomposition_cache_seed'])
    components = dict(own_base=base_construction, prelude_index_natural_targets=common,
        selected_source=source, selected_source_recipe=source_recipe, target_construction=Counter(chosen['counters']),
        unique_extra_queries=query, target_cache_setup=setup, conditional_lookups=lookup)
    physical = sum(components.values(), Counter())
    return dict(base_arm=base, context=context, target_prefix=budget, query_ids=ids,
        new_query_ids=new, logical_requests=requests, derived_cache_hits=requests-len(new),
        component_counters={key: dict(value) for key, value in components.items()},
        physical_engine_collection_counters=dict(physical),
        engine_collection_counters={engine: costs.select_engine(physical, engine) for engine in costs.ENGINES},
        scope='Conditional cold reference for one actual owned base/source(if used)/policy/budget. Own16/32/48 constructor only; shared target generation charged once; selected source only; every used nonnatural query charged once even if physically cached by another branch. Both query engines physically execute; one-engine view removes the other replay. Dependent views are not additive. Old-base information diagnostics/checkers, curve/norm-base generation, hash/pow/NumPy/Python/OS/IO internals and clocks remain separate/unexpanded; no complete-cost or runtime advantage inferred.')


def dominates(left, right, dimensions):
    """Exact target inclusion plus included counters; no cross-base rank metric."""
    if left['identified_mask'] & right['identified_mask'] != right['identified_mask']:
        return False
    no_larger = all(left['counters'].get(k, 0) <= right['counters'].get(k, 0) for k in dimensions)
    strict = left['identified_mask'] != right['identified_mask'] or any(
        left['counters'].get(k, 0) < right['counters'].get(k, 0) for k in dimensions)
    return no_larger and strict
