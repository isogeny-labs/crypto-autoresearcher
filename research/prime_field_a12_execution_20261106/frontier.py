"""Declared finite information/counter frontiers, never runtime dominance."""
from collections import Counter,defaultdict
ARITHMETIC=tuple(field+'.field_'+op for field in ('Fp','Fr') for op in ('add','sub','mul','inv'))+('query_array_allocated_bytes',)

def dominates(a,b,dimensions):
    if a['identified_mask']&b['identified_mask']!=b['identified_mask'] or a['delta']<b['delta']:return False
    ac=a['counters'];bc=b['counters']
    if any(ac.get(k,0)>bc.get(k,0) for k in dimensions):return False
    return a['identified_mask']!=b['identified_mask'] or a['delta']>b['delta'] or any(ac.get(k,0)<bc.get(k,0) for k in dimensions)

def build(cells,costs):
    lookup={(v['cell_id'],v['context']['source_schedule'],v['context']['source_prefix'],v['context']['target_policy'],v['target_prefix']):v for v in costs};options=[];groups=defaultdict(list)
    for case in cells:
        if not case['verified']:continue
        key=tuple(case[k] for k in ('cell_id','source_schedule','source_prefix','target_policy','target_prefix'));cold=lookup[key]
        for solver in ('sparse_joint','sparse_cancel'):
            for engine in ('scalar','batch'):
                counters=Counter(cold['cold_engine_collection_counters'][engine])+Counter(case['projection_counters'])+Counter(case['solver_counters'][solver]);counters['cold.logical_target_requests']+=cold['logical_requests'];counters['cold.derived_cache_hits']+=cold['derived_cold_cache_hits']
                row=dict(case_id=case['case_id'],cell_id=case['cell_id'],source_schedule=case['source_schedule'],source_prefix=case['source_prefix'],scope=case['scope'],target_policy=case['target_policy'],target_prefix=case['target_prefix'],solver=solver,query_engine=engine,identified_mask=case['identified_mask'],identified_targets=case['identified_targets'],delta=case['delta'],counters=dict(counters));row['option_id']=len(options);options.append(row)
                groups[tuple(row[k] for k in ('cell_id','source_schedule','source_prefix','scope','solver'))].append(row)
    summaries=[]
    for key,rows in groups.items():
        full=sorted({k for row in rows for k in row['counters']});sets={}
        for name,dims in [('arithmetic_and_explicit_query_allocations',ARITHMETIC),('all_retained_operational_counters',full)]:
            sets[name]=[row['option_id'] for row in rows if not any(dominates(other,row,dims) for other in rows if other is not row)]
        summaries.append(dict(group=list(key),option_ids=[v['option_id'] for v in rows],frontiers=sets))
    return dict(options=options,groups=summaries,arithmetic_dimensions=list(ARITHMETIC),definition='Same curve/source schedule/prefix/knowledge scope/solver. Dominance requires recovered target mask superset, Delta >= and no larger included counter, with a strict improvement in an observable/counter. Delta compares dimensions, not row-span containment. All views reference retained computation, not new executions.',limits='Arithmetic frontier omits other counters. Full retained-counter frontier still excludes unexpanded generation/checker/OS/IO/pow internals and calibrated weights; neither establishes all-cost/runtime/whole-attack dominance or signed standing.')
