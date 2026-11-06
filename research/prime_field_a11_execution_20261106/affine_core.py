"""Fresh source streams and cold affine-target branches, with physical query aliases."""
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import sys
import affine_solver as solver
from affine_construct import ScalarCurve,Constructor,select
from affine_registry import Registry
ROOT=Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT/'research/prime_field_a10_execution_20261106'))
source=solver.module('_a11_source_collector','research/prime_field_a10_execution_20261106/core.py')
Meter=solver.Meter;old=solver.old
PARAMETERS=dict(curves=4,targets=8,seeds=[0,1,2],sources=128,source_prefixes=[64,128],target_prefixes=[1,2,4,8],target_policies=['walk','hash_offset','general'],systems=1152,solver_calls=2304,maximum_rows=4096,maximum_width=64)
_NATIVE_CAPABILITY=object()

def require(rules,capability):
    if capability is not _NATIVE_CAPABILITY and not (rules.get('software_control')is True and all(v['p']<=211 for v in rules['fields'])):raise ValueError('A11 native admission required')

def generate(rules,event,capability=None):
    require(rules,capability);return source.generate(rules,event,source._NATIVE_CAPABILITY)

def collect_sources(cell,rules,event,capability=None):
    require(rules,capability);return source.collect(cell,rules,event,source._NATIVE_CAPABILITY)

class ProgressMeter(Meter):
    def __init__(self,fixture,event,context):super().__init__(fixture);self.event=event;self.context=context
    def stage(self,name,operation):
        try:return super().stage(name,operation)
        finally:self.event(dict(kind='affine_phase',context=self.context,phase=self.phases[-1]))

def recipes(cell,collected,rules,meter,event,capability=None):
    require(rules,capability)
    r=cell['fixture']['r'];uid=cell['fixture']['ec1']['curve_uid'];result={};trace=[]
    for policy in rules['target_policies']:
        rows=[]
        for t in range(rules['targets']):
            values=[dict(alpha=0,beta=1)];used={(0,1)}
            for j in range(1,rules['target_queries_per_point']):
                if policy=='walk':values.append(dict(alpha=j,beta=1));continue
                for counter in range(rules['maximum_scalar_candidates']):
                    if policy=='hash_offset':
                        alpha=1+int(source.hashed(rules['domain'],'target-offset',uid,t,j,counter),16)%(r-1);beta=1;hashes=1
                    elif policy=='general':
                        alpha=int(source.hashed(rules['domain'],'target-alpha',uid,t,j,counter),16)%r
                        beta=1+int(source.hashed(rules['domain'],'target-beta',uid,t,j,counter),16)%(r-1);hashes=2
                    else:raise ValueError('target policy')
                    meter.other['target_recipe_hashes']+=hashes;selected=(alpha,beta)not in used
                    rec=dict(policy=policy,target_index=t,index=j,counter=counter,alpha=alpha,beta=beta,selected=selected);trace.append(rec);event(dict(kind='target_recipe_candidate',record=rec))
                    if selected:values.append(dict(alpha=alpha,beta=beta));used.add((alpha,beta));break
                else:raise ValueError('target scalar candidate gate exhausted')
            rows.append(values)
        result[policy]=rows
    return dict(policies=result,trace=trace)

class QueryCache:
    def __init__(self,cell,collected,rules,event,capability=None):
        require(rules,capability)
        self.cell=cell;self.collected=collected;self.rules=rules;self.event=event;self.fixture=cell['fixture'];self.meter=ProgressMeter(self.fixture,event,dict(kind='shared_target_queries'));self.records=[];self.lookup={};self.table=defaultdict(list);self.pairs=collected['pairs'];self.n=len(self.fixture['factor_base']);self.base_index={}
        def setup():
            for i,pair in enumerate(self.pairs):self.table[None if pair['point']is None else tuple(pair['point'])].append(i);self.meter.other['pair_table_reuse_entries']+=1
            signed={}
            for j,atom in enumerate(self.fixture['factor_base']):
                q=tuple(atom['point']);self.base_index.setdefault(q,[]).append(j);self.meter.other['affine_base_index_entries']+=1;signed[j,1]=q;signed[j,-1]=self.meter.neg(q)
            return signed
        self.signed=self.meter.stage('target_query_cache_setup',setup)
        def seed():
            for target in collected['target_generation']['targets']:
                t=target['index'];point=tuple(target['point']);rows=[{k:v for k,v in row.items() if k not in ('target_index','target_point')} for row in collected['target_collection']['rows'] if row['target_index']==t]
                trace=[row for row in collected['target_collection']['trace'] if row['index']==t]
                rec=dict(id=len(self.records),point=list(point),rows=rows,trace=trace,seeded_natural=True,phase_ids=['source.target_queries'])
                self.lookup[point]=rec['id'];self.records.append(rec);self.meter.other['query_cache_seed_points']+=1;self.meter.other['seed_relation_references']+=len(rows);self.meter.other['seed_trace_references']+=len(trace)
        self.meter.stage('natural_decomposition_cache_seed',seed)
    def request(self,point,context):
        serial=self.meter.other.get('logical_target_requests',0)
        def lookup():
            self.meter.other['logical_target_requests']+=1;self.meter.other['target_cache_lookups']+=1
            index=self.lookup.get(point);hit=index is not None
            if hit:self.meter.other['target_cache_hits']+=1
            return index,hit
        index,hit=self.meter.stage('target_cache_lookup_'+str(serial),lookup)
        self.event(dict(kind='target_request',context=context,point=None if point is None else list(point),cache_hit=hit))
        if hit:return index
        maximum=self.rules['targets']*(1+len(self.rules['target_policies'])*(self.rules['target_queries_per_point']-1))
        if len(self.records)>=maximum:raise ValueError('fixed affine endpoint cache gate')
        index=len(self.records);self.lookup[point]=index;record=dict(id=index,point=None if point is None else list(point),rows=[],trace=[],seeded_natural=False,phase_ids=['target_query_'+str(index)])
        self.records.append(record)
        def query():
            self.meter.other['target_cache_records_added']+=1
            e=self.meter.e
            for third,sign in product(range(self.n),(1,-1)):
                self.meter.other['target_queries']+=1;wanted=e.add(point,self.meter.neg(self.signed[third,sign]));bucket=self.table.get(wanted,[]);accepted=[];self.meter.other['table_lookups']+=1
                for pi in bucket:
                    self.meter.other['bucket_entries_inspected']+=1;pair=self.pairs[pi]
                    if pair['indices'][1]>=third:continue
                    row=old.direct.make_row(self.fixture,0,pair['indices']+[third],pair['signs']+[sign]);total=None
                    for j,s in zip(row['triple'],row['signs'],strict=True):total=e.add(total,self.signed[j,s])
                    if not self.meter.equal(total,point):raise ValueError('affine target decomposition certificate')
                    record['rows'].append(row);accepted.append(pi);self.meter.other['target_certificates']+=1;self.event(dict(kind='affine_relation_accepted',query_id=index,row=row))
                    if len(record['rows'])>self.rules['max_retained_rows']:raise ValueError('target query row gate')
                rec=dict(index=index,third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=bucket,accepted=accepted);record['trace'].append(rec);self.event(dict(kind='affine_query_observed',query_id=index,record=rec))
            record['rows'].sort(key=lambda x:(tuple(x['triple']),tuple(x['signs'])))
        self.meter.stage('target_query_'+str(index),query);self.event(dict(kind='target_cache_record',record=record));return index

def construct_branch(cell,collected,rules,recipe,arm,prefix,policy,cache,event,capability=None):
    require(rules,capability)
    f=cell['fixture'];r=f['r'];nt=rules['targets'];context=dict(source_schedule=arm,source_prefix=prefix,target_policy=policy);meter=ProgressMeter(f,event,context);targets=collected['target_generation']['targets'];registry=meter.stage('affine_registry_setup',lambda:Registry(f,targets,meter,lambda v:event(dict(context=context,**v)),cache.base_index));scalar_events=[];selections={};sources=collected['arms'][arm]
    def initial():
        known={0:None}
        for item in sources['knowledge']:
            if item['prefix']>prefix:continue
            q=tuple(item['point']);s=item['scalar'];known[s]=q
            opposite=meter.neg(q);known[meter.ring.sub(0,s)]=opposite
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

def case_input(cell,collected,branch,cache,prefix,scope,meter):
    context=branch['context'];arm=context['source_schedule'];source_prefix=context['source_prefix'];r=cell['fixture']['r'];nt=len(collected['target_generation']['targets']);projection=collected['projection'];sources=collected['arms'][arm];order=collected['selection']['orders'][arm][:source_prefix]
    raw=[v for v in sources['rows'] if v['source_scalar']in order]
    if scope=='anchors':raw += [v for v in sources['anchors'] if v['prefix']<=source_prefix]
    M=[old.direct.project(row,projection,meter) for row in raw];target=[]
    for request in branch['requests']:
        if request['step']>prefix:continue
        for generic in cache.records[request['query_id']]['rows']:
            row=dict(generic,source_scalar=request['alpha']);v,b=old.direct.project(row,projection,meter);outside=[0]*nt;outside[request['target_index']]=meter.ring.sub(0,request['beta'])
            target.append(dict(vector=v,outside=outside,rhs=b,kind='decomposition',request=request))
    if scope=='anchors':
        for row in branch['equations']:
            if row['budget']>prefix:continue
            v,b=old.direct.project(dict(coefficients=row['coefficients'],source_scalar=row['rhs']),projection,meter)
            target.append(dict(vector=v,outside=row['outside'],rhs=b,kind=row['kind'],witness=row['witness']))
    return dict(width=projection['U'],target_count=nt,modulus=r,source=M,target=target,targets=collected['target_generation']['targets'])
