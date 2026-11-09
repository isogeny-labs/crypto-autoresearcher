"""Conditional cold-program counter references, with no cross-base free cache."""
from collections import Counter
from baseline import core, costs

prior = core.solver.module('_a13_prior_analysis', 'research/prime_field_a12_execution_20261106/analyze.py')
total = prior.total


def collection_view(base, collected, norm_collected, built, branch, cache, recipes, budget, rules):
    context = branch['context']
    chosen = next(v for v in branch['budgets'] if v['target_prefix'] == budget)
    phases = {v['phase']: v['counters'] for v in cache['phases']}
    ids = sorted({v['query_id'] for v in branch['requests'] if v['step'] <= budget})
    new = [i for i in ids if not cache['records'][i]['seeded_natural']]
    query = Counter()
    for index in new:
        for name in cache['records'][index]['phase_ids']:
            query.update(phases[name])
    setup = Counter()
    for name in ('target_query_cache_setup', 'natural_decomposition_cache_seed'):
        setup.update(phases[name])
    if base == 'norm':
        source = Counter(prior.source_cost(collected, context['source_schedule'], context['source_prefix'], rules))
    else:
        source = Counter(collected['collection_counters']) + Counter(built['counters'])
        # This public target-generation stage executed once in norm collection;
        # either deployable program must pay it.  No source/prerequisite cache
        # or unrelated norm base/query work is imported with this reference.
        target_phases = [v for v in norm_collected['collection_phases'] if v['phase'] == 'target_generation']
        if len(target_phases) != 1:
            raise ValueError('shared target-generation reference missing')
        source.update(total(target_phases))
    policy = context['target_policy']
    hashes = 0 if policy == 'walk' else sum(1 if v['policy'] == 'hash_offset' else 2
        for v in recipes['selection']['trace'] if v['policy'] == policy)
    requests = rules['targets'] * budget
    lookup = Counter(logical_target_requests=requests, target_cache_lookups=requests,
                     target_cache_hits=requests-len(new), target_recipe_hashes=hashes)
    counts = source + Counter(chosen['counters']) + query + setup + lookup
    return dict(base_arm=base, context=context, target_prefix=budget, query_ids=ids,
        new_query_ids=new, logical_requests=requests, derived_cache_hits=requests-len(new),
        source_or_base_counters=dict(source), branch_counters=chosen['counters'],
        query_counters=dict(query), cache_setup_counters=dict(setup),
        conditional_lookup_counters=dict(lookup), physical_engine_collection_counters=dict(counts),
        engine_collection_counters={engine: costs.select_engine(counts, engine) for engine in costs.ENGINES},
        scope='Conditional counter reference for one base/source(if any)/policy/budget; includes own base/cache and shared target generation, no other source/base/future cache. Scalar replay physically executed as control; deployable batch subtracts it. Nested views are dependent and not added.')


def target_superset(left, right):
    return left & right == right


def compare(known, norm, dimensions):
    """Across different bases, compare target masks only, never Delta/ranks."""
    no_larger = all(known['counters'].get(k, 0) <= norm['counters'].get(k, 0) for k in dimensions)
    strict = known['identified_mask'] != norm['identified_mask'] or any(
        known['counters'].get(k, 0) < norm['counters'].get(k, 0) for k in dimensions)
    return target_superset(known['identified_mask'], norm['identified_mask']) and no_larger and strict
