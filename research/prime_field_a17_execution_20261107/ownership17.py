"""Disjoint arm contracts for a GENERAL full24 known-base target program."""
from dataclasses import dataclass,asdict
from deps17 import TargetCache,require_fields,commitment


@dataclass(frozen=True)
class Owner:
    arm:str
    fixture_sha256:str
    targets_sha256:str
    paid_knowledge_sha256:str
    recipe_sha256:str
    horizon:int
    cache_limit:int


def contract(cell,collected,rules,recipe,arm,capability=None):
    f=cell['fixture'];require_fields(rules,f,capability)
    if arm not in ('full','suppress') or rules['target_policies']!=['general'] or rules['target_queries_per_point']!=24 or rules['target_prefixes']!=[24]:
        raise ValueError('fixed GENERAL full24 arm')
    if not 0<rules['targets']<=8 or len(recipe)!=rules['targets'] or any(len(v)!=24 for v in recipe):raise ValueError('complete24 recipe')
    if not rules.get('software_control') and len(f['factor_base'])!=48:raise ValueError('native supplied-known48 only')
    if (collected['program_id']!='known48_24' or collected['target_horizon']!=24 or
        collected.get('arm_owner')!=arm or collected.query_index.fixture!=f):raise ValueError('own prelude/collection required')
    knowledge=collected['arms']['known']
    if knowledge['rows'] or knowledge['sources'] or knowledge['anchors'] or collected['selection']['orders']:
        raise ValueError('source-free program gained source work')
    cap=rules['targets']*24
    if cap>192 or rules.get('maximum_target_cache_points')!=cap:raise ValueError('prospective GENERAL-only cache cap')
    return Owner(arm,commitment(f),commitment(collected['target_generation']['targets']),
        commitment(knowledge['knowledge']),commitment(recipe),24,cap)


class OwnedCache(TargetCache):
    def __init__(self,cell,collected,rules,recipe,arm,event,capability=None):
        self.owner=contract(cell,collected,rules,recipe,arm,capability)
        self.collected=collected;self.cell=cell;self.recipe=recipe;self.capability=capability
        super().__init__(collected.query_index,collected['natural_records'],rules,event,capability)

    def request(self,Q,context):
        if context.get('arm_owner')!=self.owner.arm or contract(self.cell,self.collected,self.rules,self.recipe,self.owner.arm,self.capability)!=self.owner:
            raise ValueError('borrowed or mutated arm cache')
        return super().request(Q,context)

    def descriptor(self):return asdict(self.owner)
