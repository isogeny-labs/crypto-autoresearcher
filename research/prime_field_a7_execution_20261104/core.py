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
previous=module('_a7_previous','research/prime_field_a4_execution_20261030/core.py')
direct=previous.direct
PARAMETERS=dict(prefixes=[0,8,16,24,32,48,64,96,128],seeds=[0,1,2],sources=128,fixed_projection=True,max_retained_rows=4096,max_pair_entries=4096,prefix_anchors=True,incremental_construction=True)
_NATIVE_CAPABILITY=object()
def code(value):return json.dumps(value,sort_keys=True,separators=(',',':'))


def schedules(cell,rules,event):
    extended=sorted(range(rules['anchor_prerequisite_sources']+1,rules['sources']+1),key=lambda s:previous.hashed(rules['domain'],'window-extension',cell['fixture']['ec1']['curve_uid'],s))
    result={'window':cell['old_source_order']+extended};trace=[]
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
    def derive():
        meter.other['window_extension_hashes']+=max(0,rules['sources']-rules['anchor_prerequisite_sources'])
        def schedule_event(v):
            if v['kind']=='scalar_candidate':meter.other['source_hash_attempts']+=1
            event(v)
        return schedules(cell,rules,schedule_event)
    selection=meter.stage('schedule_derivation',derive)
    orders=selection['schedules']
    def setup():
        for q in [tuple(f['P'])]+base:
            if not e.on(q) or e.mul(r,q)is not None:raise ValueError('invalid subgroup point')
    meter.stage('setup',setup)
    signed=meter.stage('sign_construction',lambda:{(j,s):q if s==1 else meter.neg(q) for j,q in enumerate(base) for s in (1,-1)})
    def prerequisite():
        points={}
        for s in cell['old_source_order']:
            meter.other['prerequisite_scalar_multiplications']+=1;points[s]=e.mul(s,tuple(f['P']))
        return points
    original=meter.stage('original_window_anchor_construction',prerequisite)
    sources={arm:{} for arm in orders}
    projection=meter.stage('fixed_public_projection',lambda:direct.public_projection(dict(fixture=f,source_order=cell['old_source_order']),original,meter))
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
    def query(points,target=False,arm=None,start_attempts=0,digest=None,retained_before=0):
        rows=[];blocks=[];attempts=start_attempts;digest=sha256() if digest is None else digest
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
                    if retained_before+len(rows)>rules['max_retained_rows']:raise ValueError('cumulative retained-row gate exceeded; prefix retained')
                record=dict(third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=list(bucket),accepted=accepted)
                records.append(record);digest.update((code([index,record])+'\n').encode());meter.other['query_digest_updates']+=1
            block=dict(index=index,queries=records,attempts=attempts);blocks.append(block);event(dict(kind='query_complete',target=target,arm=arm,**block))
        rows.sort(key=lambda row:(row['target_index'] if target else row['source_scalar'],tuple(row['triple']),tuple(row['signs'])))
        return dict(rows=rows,status_blocks=blocks,attempts=attempts,branch_sha256=digest.hexdigest())
    targets=cell['target_generation']['targets']
    natural=meter.stage('target_queries_extraction_certification',lambda:query([(t['index'],tuple(t['point'])) for t in targets],True))
    def target_multiples():
        values=[]
        for t in targets:
            multiples=[]
            for k in range(1,rules['collision_multipliers']+1):
                meter.other['diagnostic_scalar_multiplications']+=1;q=e.mul(k,tuple(t['point']));multiples.append(None if q is None else list(q))
            values.append(dict(target_index=t['index'],multiples=multiples))
        return values
    multiples=meter.stage('shared_target_multiple_cache',target_multiples)
    def anchors(arm,lo,hi):
        rows=[]
        for scalar in orders[arm][lo:hi]:
            for j,q in enumerate(base):
                for sign in (1,-1):
                    meter.other['anchor_point_comparisons']+=1
                    if not meter.equal(sources[arm][scalar],signed[j,sign]):continue
                    coefficients=[0]*n;coefficients[j]=sign%r
                    row=dict(schema='explicit-public-anchor/v1',source_scalar=scalar,atom=j,sign=sign,coefficients=coefficients,public_point=list(sources[arm][scalar]),projection_atom=projection['native_to_projected'][j])
                    row['projected_vector'],row['projected_rhs']=direct.project(row,projection,meter)
                    rows.append(row)
        return rows
    def collisions(arm,count):
        known={}
        for s,Q in sources[arm].items():known[Q]=s;known[meter.neg(Q)]=(-s)%r
        for s,Q in original.items():known[Q]=s;known[meter.neg(Q)]=(-s)%r
        schedule_points={point for Q in sources[arm].values() for point in (Q,meter.neg(Q))}
        original_points={point for Q in original.values() for point in (Q,meter.neg(Q))}
        base_lookup={point:[j,s] for (j,s),point in signed.items()};values=[]
        for t in targets:
            Q=tuple(t['point']);matches=[]
            for k,encoded in enumerate(multiples[t['index']]['multiples'],1):
                point=None if encoded is None else tuple(encoded);meter.other['public_multiple_lookups']+=1
                if point in known:matches.append(dict(multiplier=k,public_source_scalar=known[point],from_schedule=point in schedule_points,from_original=point in original_points))
            values.append(dict(target_index=t['index'],direct_public_scalar=known.get(Q),signed_base_atom=base_lookup.get(Q),bounded_multiple_matches=matches))
        return values
    arms={}
    for arm,order in orders.items():
        value=dict(rows=[],status_blocks=[],attempts=0,anchor_rows=[],budget_records=[]);digest=sha256();arms[arm]=value;lo=0
        for hi in rules['prefixes']:
            label=arm+'_'+str(hi)+'_';phase_start=len(meter.phases)
            def construct():
                for s in order[lo:hi]:
                    if s in original:
                        sources[arm][s]=original[s];meter.other['source_point_cache_hits']+=1
                    else:
                        meter.other['source_scalar_multiplications']+=1;sources[arm][s]=e.mul(s,tuple(f['P']))
            meter.stage(label+'source_construction',construct)
            block=meter.stage(label+'queries_extraction_certification',lambda:query([(s,sources[arm][s]) for s in order[lo:hi]],arm=arm,start_attempts=value['attempts'],digest=digest,retained_before=len(value['rows'])))
            value['rows'].extend(block['rows']);value['status_blocks'].extend(block['status_blocks']);value['attempts']=block['attempts'];value['branch_sha256']=block['branch_sha256']
            value['anchor_rows'].extend(meter.stage(label+'explicit_anchors',lambda:anchors(arm,lo,hi)))
            diag=meter.stage(label+'public_collisions',lambda:collisions(arm,hi));value['budget_records'].append(dict(prefix=hi,collision_diagnostics=diag,available_sources=order[:hi]))
            event(dict(kind='budget_complete',arm=arm,record=value['budget_records'][-1],phases=meter.phases[phase_start:]))
            lo=hi
        value['rows']=meter.stage(arm+'_canonical_row_order',lambda:sorted(value['rows'],key=direct.row_key))
    return dict(schema='source-control-collection/v1',cell_id=cell['id'],selection=selection,projection=projection,pair_entries=pairs,
                arms=arms,target_generation=cell['target_generation'],target_collection=natural,target_multiple_cache=multiples,prefixes=[],
                collection_phases=list(meter.phases),collection_counters=meter.counters(),complete=True),meter


def analyze_prefix(cell,rules,result,meter,arm,count,with_anchors):
    """Keep original U columns; anchor knowledge is explicit affine data."""
    start=len(meter.phases);projection=result['projection'];width=projection['U'];r=cell['fixture']['r'];nt=rules['targets']
    scope='anchors' if with_anchors else 'relations';label=arm+'_'+str(count)+'_'+scope+'_'
    order=result['selection']['schedules'][arm]
    indices=[i for i,row in enumerate(result['arms'][arm]['rows']) if row['source_scalar'] in order[:count]]
    raw=[result['arms'][arm]['rows'][i] for i in indices]
    anchor_rows=[row for row in result['arms'][arm]['anchor_rows'] if row['source_scalar'] in order[:count]] if with_anchors else []
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
                target_cancellations=cancellations,budget_costs=budget_costs(result,arm,count),phases=meter.phases[start:],cumulative_counters=meter.counters())


def budget_costs(result,arm,count):
    from collections import Counter
    groups={key:[] for key in ('construction','queries','anchors')}
    for phase in result['collection_phases']:
        for key,suffix in [('construction','source_construction'),('queries','queries_extraction_certification'),('anchors','explicit_anchors')]:
            if not phase['phase'].startswith(arm+'_') or not phase['phase'].endswith('_'+suffix):continue
            value=phase['phase'][len(arm)+1:-len(suffix)-1]
            if value.isdigit() and int(value)<=count:groups[key].append(phase)
    output={}
    for key,phases in groups.items():
        counts=Counter()
        for phase in phases:counts.update(phase['counters'])
        output[key]=dict(counters=dict(counts),phase_ids=[v['phase'] for v in phases])
    prerequisite=next(p for p in result['collection_phases'] if p['phase']=='original_window_anchor_construction')
    output['prerequisite']=dict(counters=prerequisite['counters'],phase_id=prerequisite['phase'])
    output['scope']='References to physical phase counters, not extra executions. Cold cost also includes shared setup/sign/projection/table/target/prepaid schedule derivation. Analysis and diagnostic phases remain separately charged.'
    return output
