"""Plain A14 group/constructor checks plus A16 own-horizon and batch costs."""
from collections import Counter
from deps16 import old_check,checker,check_pairs,commitment,check_base

EXPECTED={'norm8':('norm',8),'hybrid8':('hybrid',8),'known32_8':('known32',8),'known48_8':('known48',8),'known48_24':('known48',24)}


def collection(prepared,rules,actual):
    family,horizon=EXPECTED[rules['program_id']]
    if any(value.get('program_id')!=rules['program_id'] or value.get('target_horizon')!=horizon for value in (prepared,actual)):
        raise ValueError('independent collection program/horizon identity')
    if rules['base_kind']!=family or rules['target_queries_per_point']!=horizon:
        raise ValueError('independent collection horizon rule')
    value,oracle=old_check.collection(prepared,rules,actual)
    phases=[]
    for phase in actual['collection_phases']:
        if phase['phase']=='natural_target_queries':break
        phases.append(phase)
    value['pair_construction']=check_pairs(prepared['cell']['fixture'],prepared['geometry'],'batched',actual['pairs'],phases)
    value['producer_output_sha256']=commitment(actual)
    return value,oracle


def branch(cell,collected,rules,recipe,actual,cache,oracle):
    program=rules['program_id'];family,horizon=EXPECTED[program]
    h=actual['horizon_contract'];ctx=actual['context']
    maximum=rules['targets']*(1+len(rules['target_policies'])*(horizon-1))
    initial=[v for v in collected['arms'][ctx['source_schedule']]['knowledge'] if v['prefix']<=ctx['source_prefix']]
    expected=dict(schema='a16-target-horizon-contract/v1',program=program,horizon=horizon,
        maximum_cache_points=maximum,target_prefixes=[24] if horizon==24 else list(rules['short_target_prefixes']),
        source_schedule=ctx['source_schedule'],source_prefix=ctx['source_prefix'],target_policy=ctx['target_policy'],
        recipe_sha256=commitment(recipe),initial_knowledge_sha256=commitment(initial),
        public_targets_sha256=commitment(collected['target_generation']['targets']),
        scope='Own complete-horizon constructor prediction/tables/caches; no first8-from24 cold borrowing.')
    if h!=expected or cache.owner.program!=program or cache.owner.horizon!=horizon or cache.owner.maximum_cache_points!=maximum:
        raise ValueError('independent full-horizon owner contract')
    if rules['base_kind']!=family or rules['target_queries_per_point']!=horizon or len(cache.records)>maximum:
        raise ValueError('independent horizon/cache bound')
    if horizon==24 and [v['target_prefix'] for v in actual['budgets']]!=[24]:
        raise ValueError('long horizon presented as cold short-prefix program')
    value=checker.branch(cell,collected,rules,recipe,actual,cache,oracle)
    return dict(checked=True,program=program,target_horizon=horizon,maximum_cache_points=maximum,
        plain_group_constructor=value,producer_output_sha256=commitment(actual))


def public_base(original,rules,program,actual):
    family,horizon=EXPECTED[program]
    size=16 if family=='hybrid' else 32 if family=='known32' else 48 if family=='known48' else None
    if size is None or actual.get('owner_program')!=program or actual.get('target_horizon')!=horizon:
        raise ValueError('public constructor owner/horizon provenance')
    value=check_base.check(original,rules,size,actual)
    return dict(checked=True,program=program,public_base_size=size,plain_group=value,
        producer_output_sha256=commitment(actual))


def cache_payload(cache):
    return dict(records=cache.records,engine_records=cache.engines.records[cache.engine_start:],
        engine_start=cache.engine_start,phases=cache.meter.phases,counters=cache.meter.counters(),
        owner=dict(program=cache.owner.program,horizon=cache.owner.horizon,maximum_cache_points=cache.owner.maximum_cache_points))


def target_cache(prepared,collected,cache,oracle,rules):
    family,horizon=EXPECTED[rules['program_id']]
    if cache.owner.program!=rules['program_id'] or cache.owner.horizon!=horizon:
        raise ValueError('closed target cache owner mismatch')
    result=old_check.target_cache(prepared,collected,cache,oracle)
    return dict(checked=True,program=rules['program_id'],query_check=result,
        producer_output_sha256=commitment(cache_payload(cache)))
