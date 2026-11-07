"""Own complete GENERAL horizon and cache; no recovery-based query suppression."""
from deps19 import TargetCache,commitment,checker
from guards import require_fields
from branch16 import _execute


class OwnedCache(TargetCache):
    def __init__(self,collected,rules,event,capability=None):
        self.owner=(rules['program_id'],rules['target_queries_per_point'],rules['maximum_target_cache_points'])
        super().__init__(collected.query_index,collected['natural_records'],rules,event,capability)


def build(prepared,collected,rules,recipe,cache,event,capability=None):
    cell=prepared['cell'];require_fields(rules,cell['fixture'],capability)
    if cache.owner!=(rules['program_id'],rules['target_queries_per_point'],rules['targets']*rules['target_queries_per_point']):raise ValueError('owned cache horizon differs')
    if collected['program_id']!=rules['program_id']or collected['target_horizon']!=rules['target_queries_per_point']:raise ValueError('borrowed collection')
    if len(recipe)!=rules['targets']or any(len(v)!=rules['target_queries_per_point']for v in recipe):raise ValueError('complete recipe horizon differs')
    header=dict(program=rules['program_id'],horizon=rules['target_queries_per_point'],maximum_cache_points=rules['maximum_target_cache_points'],
        initial_knowledge_sha256=commitment(collected['arms']['ap0']['knowledge']),public_targets_sha256=commitment(collected['target_generation']['targets']),recipe_sha256=commitment(recipe))
    event(dict(kind='unknown_pool_branch_start',contract=header))
    result=_execute(cell,collected,rules,recipe,'ap0',rules['sources'],'general',cache,event,capability)
    result['ownership_contract']=header
    return result


def check(prepared,collected,rules,recipe,cache,actual):
    expected=dict(program=rules['program_id'],horizon=rules['target_queries_per_point'],maximum_cache_points=rules['maximum_target_cache_points'],
        initial_knowledge_sha256=commitment(collected['arms']['ap0']['knowledge']),public_targets_sha256=commitment(collected['target_generation']['targets']),recipe_sha256=commitment(recipe))
    if actual['ownership_contract']!=expected or len(actual['requests'])!=rules['targets']*rules['target_queries_per_point']:raise ValueError('branch owner/full census')
    if len(cache.records)>rules['maximum_target_cache_points']:raise ValueError('owned cache size')
    return checker.branch(prepared['cell'],collected,rules,recipe,actual,cache,checker.GroupOracle(prepared['cell']['fixture'],collected['target_generation']['targets']))

