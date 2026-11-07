"""Own program/horizon cold vectors, keeping pair and query array traffic."""
from deps16 import costs
from programs16 import get
from cold14 import collection_view as reference_view,dominates,total,prior

ARITHMETIC=tuple(field+'.field_'+op for field in ('Fp','Fr') for op in ('add','sub','mul','inv'))+(
    'pair_array_allocated_bytes','query_array_allocated_bytes')


def collection_view(program,prepared,collected,built,branch,cache,recipes,targets,budget,rules):
    p=get(program)
    if (prepared['program_id']!=program or collected['program_id']!=program or
        branch['horizon_contract']['program']!=program or cache['owner']['program']!=program or
        rules['program_id']!=program or rules['target_queries_per_point']!=p['horizon']):
        raise ValueError('conditional cold vector borrowed another horizon')
    if budget not in rules['target_prefixes']:raise ValueError('undeclared cold prefix for horizon')
    builders={}
    if p['base_size']is not None:
        if built['owner_program']!=program or built['target_horizon']!=p['horizon']:
            raise ValueError('conditional cold constructor is not owned')
        builders[p['base_size']]=built
    view=reference_view(p['base'],prepared,collected,builders,branch,cache,recipes,targets,budget,rules)
    view.update(program=program,target_horizon=p['horizon'],horizon_contract=branch['horizon_contract'])
    view['scope']='One nonadditive cold program/source/policy/prefix; own full8-or24-horizon constructor prediction/tables/caches and recipe derivation, own public base constructor and measured A15 batch pair setup. Query controls execute separately; single-engine view removes only the other endpoint-engine replay. Geometric reuse within this program is charged once per used point, no cross-horizon knowledge/cost subsidy. Array traffic is not RSS; generation/hash/pow/Python/NumPy/checker/OS/IO unexpanded; no calibrated complete-cost/runtime claim.'
    return view
