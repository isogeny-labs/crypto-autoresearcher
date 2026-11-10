"""Own horizon-specific geometry caches and target constructor contracts."""
from dataclasses import dataclass
from deps16 import TargetCache,require_fields,commitment
from programs16 import get


@dataclass(frozen=True)
class Owner:
    program: str
    horizon: int
    maximum_cache_points: int


def expected(rules):
    p=get(rules['program_id'])
    maximum=rules['targets']*(1+len(rules['target_policies'])*(p['horizon']-1))
    if rules['base_kind']!=p['base'] or rules['target_queries_per_point']!=p['horizon'] or rules['maximum_target_cache_points']!=maximum:
        raise ValueError('program/horizon/cache declaration mismatch')
    prefixes=[24] if p['horizon']==24 else list(rules['short_target_prefixes'])
    if rules['target_prefixes']!=prefixes or any(type(v)is not int or not 1<=v<=p['horizon'] for v in prefixes):
        raise ValueError('target horizon prefix gate')
    if not 1<=maximum<=560:raise ValueError('bounded horizon cache gate')
    return Owner(p['id'],p['horizon'],maximum)


class OwnedTargetCache(TargetCache):
    def __init__(self,index,natural_records,rules,event,capability=None):
        require_fields(rules,index.fixture,capability)
        self.owner=expected(rules)
        super().__init__(index,natural_records,rules,event,capability)

    def request(self,Q,context):
        if expected(self.rules)!=self.owner:raise ValueError('mutated horizon cache owner')
        return super().request(Q,context)


def contract(cell,collected,rules,recipe,schedule,prefix,policy,cache,capability=None):
    require_fields(rules,cell['fixture'],capability)
    owner=expected(rules);p=get(owner.program)
    if cache.owner!=owner or expected(cache.rules)!=owner:
        raise ValueError('borrowed geometry cache from another target horizon')
    if collected.get('program_id')!=owner.program or collected.get('target_horizon')!=owner.horizon:
        raise ValueError('borrowed collection from another horizon')
    if cache.index.fixture!=cell['fixture'] or len(recipe)!=rules['targets'] or any(len(row)!=owner.horizon for row in recipe):
        raise ValueError('target recipe/index horizon mismatch')
    if not p['source'] and (schedule!='known' or prefix!=0):raise ValueError('source-free horizon gained source knowledge')
    if policy not in rules['target_policies']:raise ValueError('undeclared target policy')
    sources=collected['arms'][schedule]
    return dict(schema='a16-target-horizon-contract/v1',program=owner.program,horizon=owner.horizon,
        maximum_cache_points=owner.maximum_cache_points,target_prefixes=rules['target_prefixes'],
        source_schedule=schedule,source_prefix=prefix,target_policy=policy,recipe_sha256=commitment(recipe),
        initial_knowledge_sha256=commitment([v for v in sources['knowledge'] if v['prefix']<=prefix]),
        public_targets_sha256=commitment(collected['target_generation']['targets']),
        scope='Own complete-horizon constructor prediction/tables/caches; no first8-from24 cold borrowing.')
