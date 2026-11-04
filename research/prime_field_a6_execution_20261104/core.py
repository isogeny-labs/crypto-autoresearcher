"""Matched public-source schedules, fixed columns and natural targets."""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations,product
import importlib.util
import json
from pathlib import Path
from time import perf_counter,process_time

ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
previous=module('_a6_previous','research/prime_field_a4_execution_20261030/core.py')
direct=previous.direct
PARAMETERS=dict(prefixes=[0,16,64],seeds=[0,1,2],sources=64,fixed_projection=True,max_retained_rows=2048,max_pair_entries=4096,fresh_generation=True,per_arm_construction=True)
_NATIVE_CAPABILITY=object()
def code(value):return json.dumps(value,sort_keys=True,separators=(',',':'))


def generate(rules,event,*,capability=None):
    if capability is not _NATIVE_CAPABILITY and not (rules.get('software_control')is True and all(f['p']<=211 for f in rules['fields'])):
        raise ValueError('fresh holdout generation requires native admission')
    cells=[];trace=[];used=set();excluded={tuple(v) for v in rules['excluded_curves']};wall,cpu=perf_counter(),process_time()
    for field in rules['fields']:
        p=field['p']
        for index in range(rules['curves_per_field']):
            for counter in range(rules['maximum_curve_candidates']):
                b=1+int(previous.hashed(rules['domain'],'curve',p,index,counter),16)%(p-1);fixture=None
                if (p,b) in excluded:trial=dict(reason='prior_curve_excluded',point_tests=0)
                elif (p,b) in used:trial=dict(reason='duplicate_selected_curve',point_tests=0)
                else:
                    fixture,trial=previous.describe(p,rules['a'],b,field['base_size'])
                    if fixture is not None and fixture['r']==p:fixture=None;trial={**trial,'reason':'anomalous_order_excluded'}
                record=dict(p=p,curve_index=index,counter=counter,b=b,**trial);trace.append(record);event(dict(kind='curve_candidate',**record))
                if fixture is None:continue
                fixture=previous.attach_ec1(fixture);used.add((p,b));uid=fixture['ec1']['curve_uid']
                order=sorted(range(1,rules['sources']+1),key=lambda s:previous.hashed(rules['domain'],'source',uid,s))
                cell=dict(id='p'+str(p)+'-i'+str(index),fixture=fixture,old_source_order=order)
                meter=direct.Meter(fixture)
                points=meter.stage('generation_window_points',lambda:{s:meter.e.mul(s,tuple(fixture['P'])) for s in order})
                cell['projection']=meter.stage('generation_fixed_projection',lambda:direct.public_projection(dict(fixture=fixture,source_order=order),points,meter))
                def target_event(v):event(dict(cell_id=cell['id'],**v))
                cell['target_generation']=meter.stage('generation_targets',lambda:previous.targets(cell,rules,meter,target_event))
                cell['generation_phases']=list(meter.phases);cell['generation_counters']=meter.counters()
                cells.append(cell);event(dict(kind='curve_selected',cell=cell));break
            else:raise ValueError('curve candidate gate exhausted; prefix retained')
    return dict(schema='fresh-source-generated/v1',cells=cells,search_trace=trace,complete=True,
                generation_diagnostics=dict(wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False),
                cost_scope='Candidate point tests plus selected fixture public-window/projection/target meters; generation and collection scopes separate, no hidden reuse.')


def schedules(cell,rules,event):
    result={'window':cell['old_source_order']};trace=[]
    for seed in rules['seeds']:
        values=[];used=set()
        for index in range(rules['sources']):
            for counter in range(rules['maximum_scalar_candidates']):
                payload='|'.join(map(str,[rules['domain'],cell['fixture']['ec1']['curve_uid'],seed,index,counter]))
                scalar=1+int(sha256(payload.encode()).hexdigest(),16)%(cell['fixture']['r']-1)
                record=dict(seed=seed,index=index,counter=counter,scalar=scalar,selected=scalar not in used,payload_sha256=sha256(payload.encode()).hexdigest(),reason='duplicate' if scalar in used else 'selected')
                trace.append(record);event(dict(kind='scalar_candidate',**record))
                if scalar in used:continue
                used.add(scalar);values.append(scalar);break
            else:raise ValueError('source scalar candidate gate exhausted; prefix retained')
        result['hash'+str(seed)]=values
    return dict(schedules=result,search_trace=trace)


def collect(cell,rules,event,*,capability=None):
    f=cell['fixture'];n=len(f['factor_base']);r=f['r']
    if capability is not _NATIVE_CAPABILITY and not (f.get('software_control')is True and f['p']<=211):
        raise ValueError('source-control collection requires native admission')
    meter=direct.Meter(f);e=meter.e;base=[tuple(a['point']) for a in f['factor_base']]
    selection=meter.stage('schedule_derivation',lambda:schedules(cell,rules,event))
    orders=selection['schedules']
    def setup():
        for q in [tuple(f['P'])]+base:
            if not e.on(q) or e.mul(r,q)is not None:raise ValueError('invalid subgroup point')
    meter.stage('setup',setup)
    signed=meter.stage('sign_construction',lambda:{(j,s):q if s==1 else meter.neg(q) for j,q in enumerate(base) for s in (1,-1)})
    sources={}
    for arm,order in orders.items():
        def construct(order=order):
            values={}
            for s in order:
                meter.other['source_scalar_multiplications']+=1;values[s]=e.mul(s,tuple(f['P']))
            return values
        sources[arm]=meter.stage(arm+'_source_construction',construct)
    projection=meter.stage('fixed_public_projection',lambda:direct.public_projection(dict(fixture=f,source_order=orders['window']),sources['window'],meter))
    if projection!=cell['projection']:raise ValueError('fixed generated public projection changed')
    pairs=[];table=defaultdict(list)
    def build():
        for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
            point=e.add(signed[j,signs[0]],signed[k,signs[1]])
            pair=dict(indices=[j,k],signs=list(signs),point=None if point is None else list(point))
            meter.other['pair_table_insertions']+=1;table[point].append(len(pairs));pairs.append(pair)
            event(dict(kind='pair_entry',index=len(pairs)-1,**pair))
            if len(pairs)>rules['max_pair_entries']:raise ValueError('pair-table gate exceeded; prefix retained')
    meter.stage('pair_construction',build)
    def query(points,target=False,arm=None):
        rows=[];blocks=[];attempts=0;digest=sha256()
        for index,Q in points:
            records=[]
            for third,sign in product(range(n),(1,-1)):
                attempts+=1;meter.other['target_queries' if target else 'source_queries']+=1
                wanted=e.add(Q,meter.neg(signed[third,sign]));bucket=table.get(wanted,[])
                meter.other['table_lookups']+=1;accepted=[]
                for pi in bucket:
                    meter.other['bucket_entries_inspected']+=1;pair=pairs[pi]
                    if pair['indices'][1]>=third:continue
                    accepted.append(pi);row=direct.make_row(f,0 if target else index,pair['indices']+[third],pair['signs']+[sign])
                    if target:row.update(schema='holdout-target-row/v1',target_index=index,target_point=list(Q))
                    total=None
                    for j,s in zip(row['triple'],row['signs']):total=e.add(total,signed[j,s])
                    if not meter.equal(total,Q):raise ValueError('public relation certificate fails')
                    meter.other['target_certificates' if target else 'source_certificates']+=1
                    rows.append(row);event(dict(kind='target_accepted' if target else 'source_accepted',arm=arm,row=row))
                    if len(rows)>rules['max_retained_rows']:raise ValueError('retained-row gate exceeded; prefix retained')
                record=dict(third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=list(bucket),accepted=accepted)
                records.append(record);digest.update((code([index,record])+'\n').encode());meter.other['query_digest_updates']+=1
            block=dict(index=index,queries=records,attempts=attempts);blocks.append(block);event(dict(kind='query_complete',target=target,arm=arm,**block))
        rows.sort(key=lambda row:(row['target_index'] if target else row['source_scalar'],tuple(row['triple']),tuple(row['signs'])))
        return dict(rows=rows,status_blocks=blocks,attempts=attempts,branch_sha256=digest.hexdigest())
    arms={}
    for arm,order in orders.items():
        arms[arm]=meter.stage(arm+'_queries_extraction_certification',lambda arm=arm,order=order:query([(s,sources[arm][s]) for s in order],arm=arm))
    targets=cell['target_generation']['targets']
    natural=meter.stage('target_queries_extraction_certification',lambda:query([(t['index'],tuple(t['point'])) for t in targets],True))
    def anchors(arm):
        rows=[]
        for scalar in orders[arm]:
            for j,q in enumerate(base):
                for sign in (1,-1):
                    meter.other['anchor_point_comparisons']+=1
                    if not meter.equal(sources[arm][scalar],signed[j,sign]):continue
                    coefficients=[0]*n;coefficients[j]=sign%r
                    row=dict(schema='explicit-public-anchor/v1',source_scalar=scalar,atom=j,sign=sign,coefficients=coefficients,public_point=list(sources[arm][scalar]),projection_atom=projection['native_to_projected'][j])
                    row['projected_vector'],row['projected_rhs']=direct.project(row,projection,meter)
                    rows.append(row)
        return rows
    def collisions(arm):
        known={}
        for s,Q in sources[arm].items():known[Q]=s;known[meter.neg(Q)]=(-s)%r
        # Old public information remains available in every arm.
        for s,Q in sources['window'].items():known[Q]=s;known[meter.neg(Q)]=(-s)%r
        schedule_points={point for Q in sources[arm].values() for point in (Q,meter.neg(Q))}
        original_points={point for Q in sources['window'].values() for point in (Q,meter.neg(Q))}
        base_lookup={point:[j,s] for (j,s),point in signed.items()};values=[]
        for t in targets:
            Q=tuple(t['point']);matches=[]
            for k in range(1,rules['collision_multipliers']+1):
                point=e.mul(k,Q);meter.other['public_multiple_lookups']+=1
                if point in known:matches.append(dict(multiplier=k,public_source_scalar=known[point],from_schedule=point in schedule_points,from_original=point in original_points))
            values.append(dict(target_index=t['index'],direct_public_scalar=known.get(Q),signed_base_atom=base_lookup.get(Q),bounded_multiple_matches=matches))
        return values
    for arm in orders:
        arms[arm]['anchor_rows']=meter.stage(arm+'_explicit_anchors',lambda arm=arm:anchors(arm))
        arms[arm]['collision_diagnostics']=meter.stage(arm+'_public_collisions',lambda arm=arm:collisions(arm))
    return dict(schema='source-control-collection/v1',cell_id=cell['id'],selection=selection,projection=projection,pair_entries=pairs,
                arms=arms,target_generation=cell['target_generation'],target_collection=natural,prefixes=[],
                collection_phases=list(meter.phases),collection_counters=meter.counters(),complete=True),meter


def analyze_prefix(cell,rules,result,meter,arm,count,with_anchors):
    """Keep original U columns; anchor knowledge is explicit affine data."""
    start=len(meter.phases);projection=result['projection'];width=projection['U'];r=cell['fixture']['r'];nt=rules['targets']
    scope='anchors' if with_anchors else 'relations';label=arm+'_'+str(count)+'_'+scope+'_'
    order=result['selection']['schedules'][arm]
    indices=[i for i,row in enumerate(result['arms'][arm]['rows']) if row['source_scalar'] in order[:count]]
    raw=[result['arms'][arm]['rows'][i] for i in indices]
    anchor_rows=result['arms'][arm]['anchor_rows'] if with_anchors else []
    projected=meter.stage(label+'projection',lambda:[direct.project(row,projection,meter) for row in raw+anchor_rows])
    def window_union():
        window_order=result['selection']['schedules']['window'][:count]
        window=[direct.project(row,projection,meter) for row in result['arms']['window']['rows'] if row['source_scalar'] in window_order]
        union=previous.CertifiedSystem(width,meter)
        for v,b in window:union.add(v,b)
        before=len(union.pivots)
        for v,b in projected:union.add(v,b)
        return dict(reference_base_rank=before,stacked_rank_with_window=len(union.pivots),rank_gain_over_window=len(union.pivots)-before)
    comparison=meter.stage(label+'window_union',window_union)
    natural=meter.stage(label+'target_projection',lambda:[direct.project(row,projection,meter) for row in result['target_collection']['rows']])
    def cancel():
        first={};rows=[]
        for i,(row,(v,b)) in enumerate(zip(result['target_collection']['rows'],natural,strict=True)):
            target=row['target_index']
            if target not in first:first[target]=i;continue
            j=first[target];old,offset=natural[j];weights=[0]*len(natural);weights[i]=1;weights[j]=r-1
            rows.append(dict(target_row_weights=weights,vector=[meter.ring.sub(x,y) for x,y in zip(v,old)],rhs=meter.ring.sub(b,offset)))
        return rows
    cancellations=meter.stage(label+'target_column_cancellation',cancel)
    system=previous.CertifiedSystem(width,meter)
    meter.stage(label+'elimination',lambda:[system.add(v,b) for v,b in projected])
    kernel=meter.stage(label+'kernel',system.kernel)
    equations=meter.stage(label+'normalization',lambda:direct.normalize(projected,meter))
    def singles():
        values=[]
        for i,(row,(v,b)) in enumerate(zip(result['target_collection']['rows'],natural,strict=True)):
            identified=system.identify(v,kernel);scalar=None
            if identified['identifiable']:
                scalar=meter.ring.sub(identified['value'],b)
                if not meter.equal(meter.e.mul(scalar,tuple(cell['fixture']['P'])),tuple(row['target_point'])):raise ValueError('single public recovery fails')
            values.append(dict(target_row_index=i,target_index=row['target_index'],offset=b,**identified,scalar=scalar))
        return values
    single=meter.stage(label+'single_recovery',singles)
    joint=previous.CertifiedSystem(width+nt,meter)
    def insert():
        for v,b in projected:joint.add(v+[0]*nt,b)
        for row,(v,b) in zip(result['target_collection']['rows'],natural,strict=True):
            suffix=[0]*nt;suffix[row['target_index']]=r-1;joint.add(v+suffix,b)
    meter.stage(label+'joint_elimination',insert);jk=meter.stage(label+'joint_kernel',joint.kernel)
    def recover():
        values=[]
        for t in result['target_generation']['targets']:
            unit=[0]*(width+nt);unit[width+t['index']]=1;value=joint.identify(unit,jk)
            if value['identifiable'] and not meter.equal(meter.e.mul(value['value'],tuple(cell['fixture']['P'])),tuple(t['point'])):raise ValueError('joint public recovery fails')
            values.append(dict(target_index=t['index'],**value,scalar=value['value']))
        return values
    combined=meter.stage(label+'joint_recovery',recover)
    outside=len({row['target_index'] for row in result['target_collection']['rows']});after=len(joint.pivots)-outside
    return dict(arm=arm,prefix=count,scope=scope,source_row_indices=indices,anchor_rows_inserted=len(anchor_rows),**comparison,
                base=system.summary(kernel),distinct_equations=len(equations),singles=single,joint=joint.summary(jk),joint_recoveries=combined,
                outside_target_rank=outside,base_rank_after_target_cancellation=after,target_base_rank_gain=after-len(system.pivots),
                single_identified_targets=sorted({v['target_index'] for v in single if v['identifiable']}),
                joint_identified_targets=[v['target_index'] for v in combined if v['identifiable']],
                target_cancellations=cancellations,phases=meter.phases[start:],cumulative_counters=meter.counters())
