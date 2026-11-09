"""A12 symbolic target construction with an owned-cache sign lookup floor.

All four A14 programs use the same branch implementation. P-cache closure pays
only missing signs; Q coefficients remain symbolic. No old source is edited.
"""
from shared import core
from baseline import construct
from affine_registry import Registry
from guards import require_fields

ProgressMeter = core.ProgressMeter
ScalarCurve, Constructor, select = construct.ScalarCurve, construct.Constructor, construct.select


def build(cell,collected,rules,recipe,arm,prefix,policy,cache,event,capability=None):
    require_fields(rules,cell['fixture'],capability)
    f=cell['fixture'];r=f['r'];nt=rules['targets'];context=dict(source_schedule=arm,source_prefix=prefix,target_policy=policy);meter=ProgressMeter(f,event,context);targets=collected['target_generation']['targets'];registry=meter.stage('affine_registry_setup',lambda:Registry(f,targets,meter,lambda v:event(dict(context=context,**v)),cache.base_index));scalar_events=[];selections={};sources=collected['arms'][arm]
    def initial():
        known={0:None}
        for item in sources['knowledge']:
            if item['prefix']>prefix:continue
            q=tuple(item['point']);s=item['scalar'];known[s]=q
        for s,q in list(known.items()):
            if s:
                negative=meter.ring.sub(0,s);meter.other['target_owned_sign_lookups']+=1
                if negative not in known:known[negative]=meter.neg(q)
        for t in targets:
            beta=[0]*nt;beta[t['index']]=1;registry.add(tuple(t['point']),0,beta,'public_target')
        return known
    known=meter.stage('source_cache_and_public_target_setup',initial)
    def callback(point,scalar,basis,origin):
        rec=dict(point=None if point is None else list(point),scalar=scalar,basis=basis,origin=origin,step=registry.budget);scalar_events.append(rec);event(dict(kind='affine_scalar_point',context=context,record=rec))
        beta=[0]*nt
        if basis=='P':alpha=scalar
        else:alpha=0;beta[int(basis[1:])]=scalar
        registry.add(point,alpha,beta,dict(kind='scalar_basis',basis=basis,scalar=scalar,origin=origin))
    Pcurve=meter.stage('target_P_cache_hydration',lambda:ScalarCurve(meter,f['p'],r,tuple(f['P']),known,callback,'P'))
    def choose(basis,curve,workload):
        result=select(r,list(curve.known),workload);selections[basis]=result;meter.other['constructor_policy_candidates']+=9
        meter.other['constructor_policy_simulated_ec_adds']+=sum(v['uncached_ec_adds'] for v in result['candidates']);meter.other['constructor_policy_simulated_wrapper_adds']+=sum(v['wrapper_add_calls'] for v in result['candidates'])
        return Constructor(curve,result)
    alpha_work=[recipe[t][j]['alpha'] for j in range(1,rules['target_queries_per_point']) for t in range(nt)]
    Pconstructor=None if policy=='walk' else meter.stage('target_P_policy',lambda:choose('P',Pcurve,alpha_work))
    Qconstructors={}
    if policy=='general':
        for t in targets:
            i=t['index'];q=tuple(t['point'])
            def make(i=i,q=q):
                curve=ScalarCurve(meter,f['p'],r,q,{1:q,r-1:meter.neg(q)},callback,'Q'+str(i));return choose('Q'+str(i),curve,[recipe[i][j]['beta'] for j in range(1,rules['target_queries_per_point'])])
            Qconstructors[i]=meter.stage('target_Q'+str(i)+'_policy',make)
    points={t['index']:tuple(t['point']) for t in targets};requests=[];budget_records=[]
    for j in range(rules['target_queries_per_point']):
        registry.budget=j+1;phase_start=len(meter.phases)
        def construct():
            expressions=[]
            for t in targets:
                i=t['index'];rec=recipe[i][j];alpha,beta=rec['alpha'],rec['beta'];Q=tuple(t['point'])
                if j==0:point=Q
                elif policy=='walk':point=meter.e.add(points[i],tuple(f['P']));meter.other['affine_walk_adds']+=1
                else:
                    A=Pconstructor.mul(alpha);B=Q if policy=='hash_offset' else Qconstructors[i].mul(beta)
                    point=meter.e.add(A,B);meter.other['affine_combination_adds']+=1
                points[i]=point;b=[0]*nt;b[i]=beta;registry.add(point,alpha,b,dict(kind='requested_endpoint',target_index=i,index=j,policy=policy))
                item=dict(target_index=i,index=j,step=j+1,alpha=alpha,beta=beta,point=None if point is None else list(point));expressions.append(item);event(dict(kind='affine_endpoint',context=context,record=item))
            return expressions
        expressions=meter.stage('target_step_'+str(j+1)+'_construction_knowledge',construct)
        def lookup():
            for item in expressions:
                point=None if item['point']is None else tuple(item['point']);qid=cache.request(point,dict(**context,target_index=item['target_index'],index=j));requests.append(dict(**item,query_id=qid));meter.other['branch_query_reference_lookups']+=1
        meter.stage('target_step_'+str(j+1)+'_query_references',lookup)
        if j+1 in rules['target_prefixes']:
            budget_records.append(dict(target_prefix=j+1,requests=len(requests),labels=len(registry.labels),equations=len(registry.equations),phase_ids=[p['phase'] for p in meter.phases],counters=meter.counters()));event(dict(kind='affine_budget_complete',context=context,record=budget_records[-1]))
        if len(registry.labels)>rules['max_affine_labels'] or len(registry.equations)>rules['max_retained_rows']:raise ValueError('affine knowledge size gate')
    return dict(context=context,recipe=recipe,requests=requests,selections=selections,scalar_events=scalar_events,labels=registry.labels,equations=registry.equations,budgets=budget_records,phases=meter.phases,counters=meter.counters(),complete=True)
