"""Fresh paired AP/hash sources, explicit public knowledge and shared collection."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations,product
import json
from solver import Meter,KernelFreeSystem,old
from construct import LabelledCurve,Constructor,select
from batch_query import QueryEngines,Collected
_NATIVE_CAPABILITY=object()
def code(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def hashed(*v):return sha256('|'.join(map(str,v)).encode()).hexdigest()
def require(rules,capability):
    if capability is not _NATIVE_CAPABILITY and not (rules.get('software_control')is True and all(v['p']<=211 for v in rules['fields'])):raise ValueError('fresh experiment needs native admission')
def generate(rules,event,capability=None):
    require(rules,capability);cells=[];trace=[];used={tuple(v) for v in rules['excluded_curves']}
    for field in rules['fields']:
        p=field['p']
        for index in range(rules['curves_per_field']):
            for counter in range(rules['maximum_curve_candidates']):
                b=1+int(hashed(rules['domain'],'curve',p,index,counter),16)%(p-1)
                fixture,trial=old.describe(p,rules['a'],b,field['base_size'])
                if (p,b) in used:fixture=None;trial={**trial,'reason':'excluded_or_duplicate_curve'}
                if fixture is not None and fixture['r']==p:fixture=None;trial={**trial,'reason':'anomalous_order_excluded'}
                rec=dict(p=p,curve_index=index,counter=counter,b=b,**trial);trace.append(rec);event(dict(kind='curve_candidate',**rec))
                if fixture is None:continue
                if fixture['r']<=rules['sources']:raise ValueError('field too small for fixed source horizon')
                fixture=old.attach_ec1(fixture);used.add((p,b));cell=dict(id='p'+str(p)+'-i'+str(index),fixture=fixture)
                cells.append(cell);event(dict(kind='curve_selected',cell=cell));break
            else:raise ValueError('finite curve candidate gate exhausted')
    return dict(cells=cells,search_trace=trace,complete=True)
def schedules(cell,rules,meter,event):
    r=cell['fixture']['r'];uid=cell['fixture']['ec1']['curve_uid'];orders={};traces=[];ap={}
    for seed in rules['seeds']:
        for counter in range(rules['maximum_scalar_candidates']):
            a=1+int(hashed(rules['domain'],'ap-start',uid,seed,counter),16)%(r-1)
            d=1+int(hashed(rules['domain'],'ap-step',uid,seed,counter),16)%(r-1)
            values=[(a+i*d)%r for i in range(rules['sources'])];selected=0 not in values
            meter.other['source_hash_attempts']+=2;meter.other['ap_horizon_scalar_tests']+=len(values)
            rec=dict(kind='ap_candidate',seed=seed,counter=counter,a=a,d=d,selected=selected,reason='selected' if selected else 'zero_in_horizon')
            traces.append(rec);event(rec)
            if selected:orders['ap'+str(seed)]=values;ap['ap'+str(seed)]=dict(a=a,d=d);break
        else:raise ValueError('finite AP candidate gate exhausted')
        values=[];used=set()
        for index in range(rules['sources']):
            for counter in range(rules['maximum_scalar_candidates']):
                value=1+int(hashed(rules['domain'],'hash',uid,seed,index,counter),16)%(r-1)
                meter.other['source_hash_attempts']+=1;selected=value not in used
                rec=dict(kind='hash_candidate',seed=seed,index=index,counter=counter,scalar=value,selected=selected)
                traces.append(rec);event(rec)
                if selected:values.append(value);used.add(value);break
            else:raise ValueError('finite hash candidate gate exhausted')
        orders['hash'+str(seed)]=values
    return dict(orders=orders,ap=ap,trace=traces)
class CollectionMeter(Meter):
    def __init__(self,fixture,event):
        super().__init__(fixture);self.progress=event;self.current_arm=None;self.current_prefix=None
    def stage(self,name,operation):
        try:return super().stage(name,operation)
        finally:self.progress(dict(kind='collection_phase',phase=self.phases[-1]))

def collect(cell,rules,event,capability=None):
    require(rules,capability);f=cell['fixture'];r=f['r'];n=len(f['factor_base']);meter=CollectionMeter(f,event);e=meter.e
    order=meter.stage('schedule_derivation',lambda:schedules(cell,rules,meter,event))
    base=[tuple(a['point']) for a in f['factor_base']]
    def validate():
        for q in [tuple(f['P'])]+base:
            if not e.on(q) or e.mul(r,q)is not None:raise ValueError('invalid group point')
    meter.stage('public_setup_verification',validate)
    signed=meter.stage('sign_construction',lambda:{(j,s):q if s==1 else meter.neg(q) for j,q in enumerate(base) for s in (1,-1)})
    engines=meter.stage('query_engine_index_setup',lambda:QueryEngines(f,base,signed,meter,event))
    def prerequisites():
        values={1:tuple(f['P'])}
        for scalar in range(2,rules['prerequisite']+1):values[scalar]=e.add(values[scalar-1],tuple(f['P']))
        return values
    original=meter.stage('prerequisite_walk',prerequisites)
    projection=meter.stage('fixed_projection',lambda:old.direct.public_projection(dict(fixture=f,source_order=list(original)),original,meter))
    cell['projection']=projection
    targets=meter.stage('target_generation',lambda:old.targets(cell,rules,meter,event))
    pairs=[];table=defaultdict(list)
    def build():
        for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
            q=e.add(signed[j,signs[0]],signed[k,signs[1]]);index=len(pairs)
            pairs.append(dict(indices=[j,k],signs=list(signs),point=None if q is None else list(q)));table[q].append(index)
            meter.other['pair_table_insertions']+=1
            if len(pairs)>rules['max_pair_entries']:raise ValueError('pair entries gate')
    meter.stage('pair_construction',build)
    def query(points,target=False,arm=None):
        rows=[];trace=[]
        for index,Q in points:
            wanted_points=engines.evaluate(Q,meter,dict(target=target,arm=arm,index=index))
            for third,sign in product(range(n),(1,-1)):
                meter.other['target_queries' if target else 'source_queries']+=1
                wanted=wanted_points[2*third+(sign==-1)];bucket=table.get(wanted,[]);accepted=[]
                meter.other['table_lookups']+=1
                for pi in bucket:
                    meter.other['bucket_entries_inspected']+=1;pair=pairs[pi]
                    if pair['indices'][1]>=third:continue
                    row=old.direct.make_row(f,0 if target else index,pair['indices']+[third],pair['signs']+[sign])
                    if target:row.update(target_index=index,target_point=list(Q))
                    total=None
                    for j,s in zip(row['triple'],row['signs'],strict=True):total=e.add(total,signed[j,s])
                    if not meter.equal(total,Q):raise ValueError('relation public certificate')
                    meter.other['target_certificates' if target else 'source_certificates']+=1;rows.append(row);accepted.append(pi);event(dict(kind='relation_accepted',target=target,arm=arm,row=row))
                rec=dict(index=index,third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=bucket,accepted=accepted)
                trace.append(rec);event(dict(kind='query_observed',target=target,arm=arm,record=rec))
                if len(rows)>rules['max_retained_rows']:raise ValueError('query retained rows gate')
        event(dict(kind='queries_complete',target=target,arm=arm,queries=len(trace),accepted=len(rows)))
        return dict(rows=rows,trace=trace,branch_sha256=hashed(code(trace)))
    natural=meter.stage('target_queries',lambda:query([(t['index'],tuple(t['point'])) for t in targets['targets']],True))
    arms={}
    for arm,values in order['orders'].items():
        meter.current_arm=arm;meter.current_prefix=0
        phase_start=len(meter.phases)
        curve=meter.stage(arm+'_label_cache_setup',lambda:LabelledCurve(meter,f,original))
        workloads=[order['ap'][arm][key] for key in ('a','d')] if arm.startswith('ap') else values
        def policy():
            result=select(r,list(curve.known),workloads)
            meter.other['constructor_policy_simulated_adds']+=sum(v['group_add_calls'] for v in result['candidates'])
            meter.other['constructor_policy_candidates']+=len(result['candidates']);return result
        selected=meter.stage(arm+'_constructor_selection',policy);constructor=Constructor(curve,selected['window'])
        result=dict(selection=selected,rows=[],query_trace=[],knowledge=[],anchors=[],budgets=[],sources=[]);arms[arm]=result
        scanned=0;lo=0;A=D=None;anchor_keys=set()
        for hi in rules['prefixes']:
            meter.current_prefix=hi
            label=arm+'_'+str(hi)+'_';start=len(meter.phases)
            def construct():
                nonlocal A,D
                new=[]
                if hi and arm.startswith('ap'):
                    if A is None:
                        A=constructor.mul(order['ap'][arm]['a']);D=constructor.mul(order['ap'][arm]['d'])
                    for i in range(lo,hi):
                        if i:A=curve.add(A,D)
                        new.append((values[i],A));event(dict(kind='source_constructed',arm=arm,prefix=hi,scalar=values[i],point=list(A)))
                elif hi:
                    for scalar in values[lo:hi]:
                        point=constructor.mul(scalar);new.append((scalar,point));event(dict(kind='source_constructed',arm=arm,prefix=hi,scalar=scalar,point=list(point)))
                result['sources'].extend([dict(scalar=s,point=list(q),prefix=hi) for s,q in new])
                return new
            new=meter.stage(label+'source_construction',construct)
            block=meter.stage(label+'queries_extraction_verification',lambda:query(new,arm=arm));result['rows'].extend(block['rows']);result['query_trace'].extend(block['trace'])
            if len(result['rows'])>rules['max_retained_rows']:raise ValueError('arm retained rows gate')
            def knowledge():
                nonlocal scanned
                for item in curve.points[scanned:]:
                    point=tuple(item['point']);opposite=meter.neg(point);scalar=item['scalar'];opposite_scalar=meter.ring.sub(0,scalar)
                    record=dict(**item,prefix=hi);result['knowledge'].append(record)
                    for j,q in enumerate(base):
                        for sign,Q in ((1,point),(-1,opposite)):
                            meter.other['knowledge_base_scans']+=1
                            if not meter.equal(q,Q):continue
                            rhs=scalar if sign==1 else opposite_scalar;key=(j,rhs)
                            if key in anchor_keys:continue
                            anchor_keys.add(key);coeff=[0]*n;coeff[j]=1
                            result['anchors'].append(dict(source_scalar=rhs,coefficients=coeff,prefix=hi,atom=j,known_point=record,sign=sign))
                    for t in targets['targets']:
                        for sign,Q in ((1,point),(-1,opposite)):
                            meter.other['knowledge_target_scans']+=1
                            if meter.equal(tuple(t['point']),Q):record.setdefault('direct_targets',[]).append(dict(target_index=t['index'],scalar=scalar if sign==1 else opposite_scalar))
                scanned=len(curve.points)
            meter.stage(label+'knowledge_scan',knowledge)
            result['budgets'].append(dict(prefix=hi,source_rows=len(result['rows']),anchor_rows=len(result['anchors']),labelled_points=len(curve.points),point_coordinate_bytes=len(curve.points)*2*((f['p'].bit_length()+7)//8),phase_ids=[p['phase'] for p in meter.phases[start:]],source_count=hi))
            event(dict(kind='budget_complete',arm=arm,record=result['budgets'][-1],phases=meter.phases[start:]));lo=hi
        result['rows'].sort(key=old.direct.row_key)
        result['phase_ids']=[p['phase'] for p in meter.phases[phase_start:]]
    result=Collected(complete=True,selection=order,projection=projection,target_generation=targets,target_collection=natural,pairs=pairs,arms=arms,collection_phases=meter.phases,collection_counters=meter.counters(),query_engine_setup=engines.descriptor,query_engine_records=list(engines.records));result.query_engines=engines;return result

def case_input(cell,collected,arm,prefix,scope,meter):
    records=collected['arms'][arm];order=collected['selection']['orders'][arm][:prefix]
    selected=[row for row in records['rows'] if row['source_scalar']in order]
    if scope=='anchors':selected += [row for row in records['anchors'] if row['prefix']<=prefix]
    source=[old.direct.project(row,collected['projection'],meter) for row in selected]
    target=[dict(target_index=row['target_index'],vector=v,rhs=b) for row in collected['target_collection']['rows'] for v,b in [old.direct.project(row,collected['projection'],meter)]]
    if scope=='anchors':
        public={}
        for point in records['knowledge']:
            if point['prefix']<=prefix:
                for match in point.get('direct_targets',[]):public[match['target_index']]=match['scalar']
        for t,s in sorted(public.items()):
            target.append(dict(target_index=t,vector=[0]*collected['projection']['U'],rhs=meter.ring.sub(0,s)))
            meter.other['explicit_public_target_rows']+=1
    return dict(width=collected['projection']['U'],target_count=len(collected['target_generation']['targets']),modulus=cell['fixture']['r'],source=source,target=target,targets=collected['target_generation']['targets'])
