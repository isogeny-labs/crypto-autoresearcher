"""Owned full-program component vectors; controls and shared costs stay explicit."""
from collections import Counter
from deps17 import core  # bootstrap the pinned legacy import paths
from baseline import costs

ARITHMETIC=tuple(field+'.field_'+op for field in ('Fp','Fr') for op in ('add','sub','mul','inv'))+('pair_array_allocated_bytes','query_array_allocated_bytes')


def phase_total(phases):return dict(sum((Counter(v['counters']) for v in phases),Counter()))


def cache_payload(cache):
    return dict(owner=cache.descriptor(),records=cache.records,engine_records=cache.engines.records[cache.engine_start:],
        engine_start=cache.engine_start,phases=cache.meter.phases,counters=cache.meter.counters())


def cold(arm,built,prepared,collected,recipe,targets,cloud,query,cache,primary):
    if (built['arm_owner']!=arm or prepared['arm_owner']!=arm or collected['arm_owner']!=arm or
        cloud['owner']['arm']!=arm or query['owner']!=cloud['owner'] or cache['owner']!=cloud['owner']):
        raise ValueError('cold cost borrowed another arm')
    components=dict(own_public_base=built['counters'],own_known_prelude=prepared['counters'],
        own_pair_index_and_natural_queries=collected['collection_counters'],own_target_recipe=recipe['counters'],
        shared_target_generation=targets['counters'],own_full24_construction=cloud['counters'],
        own_cache_and_derived_queries=cache['counters'],own_native_assembly=query['assembly_counters'],
        own_query_decisions=query['scheduling_counters'],primary_target_algebra=primary['counters'])
    physical=dict(sum((Counter(v) for v in components.values()),Counter()))
    return dict(program=arm,component_counters=components,physical_engine_counters=physical,
        single_engine_counters={engine:costs.select_engine(physical,engine) for engine in costs.ENGINES},
        scope='One complete independently owned full24 GENERAL known48 program. All base/recipe/index/natural/point/registry construction is paid before extra queries. Shared public target generation is charged once in this view; paired views are nonadditive. Both endpoint engines physically execute; single-engine views remove only the other measured replay. Native joint controls, independent causal/group/row-consequence checks and curve/norm-fixture generation are separately retained. Hash/pow/Python/NumPy/OS/IO and complete calibration remain partly unexpanded; explicit array bytes are traffic, not RSS; clocks invalid.')


def dominates(left,right,dimensions=ARITHMETIC):
    if left['identified_mask']&right['identified_mask']!=right['identified_mask']:return False
    a,b=left['counters'],right['counters']
    return all(a.get(k,0)<=b.get(k,0) for k in dimensions) and (left['identified_mask']!=right['identified_mask'] or any(a.get(k,0)<b.get(k,0) for k in dimensions))
