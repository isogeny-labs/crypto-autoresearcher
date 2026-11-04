"""Separate E arithmetic and dense algebra; reconstruct complete finite panel."""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations,product
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('_a5_separate',ROOT/'research/prime_field_a4_execution_20261030/check.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
add=old.add;multiply=old.multiply;rank=old.dense_rank
def code(v):return json.dumps(v,sort_keys=True,separators=(',',':'))


def selection(cell,rules):
    result={'window':cell['old_source_order']};trace=[];r=cell['fixture']['r']
    for seed in rules['seeds']:
        values=[]
        for index in range(rules['sources']):
            for counter in range(rules['maximum_scalar_candidates']):
                payload=rules['domain']+'|'+cell['fixture']['ec1']['curve_uid']+'|'+str(seed)+'|'+str(index)+'|'+str(counter)
                s=1+int.from_bytes(sha256(payload.encode('utf-8')).digest(),'big')%(r-1)
                selected=s not in values;trace.append(dict(seed=seed,index=index,counter=counter,scalar=s,selected=selected,payload_sha256=sha256(payload.encode()).hexdigest(),reason='selected' if selected else 'duplicate'))
                if selected:values.append(s);break
            else:raise ValueError('reference scalar gate exhausted')
        result['hash'+str(seed)]=values
    return dict(schedules=result,search_trace=trace)


def check_prefix(cell,rules,result,rec):
    f=cell['fixture'];p,r=f['p'],f['r'];projection=result['projection'];width=projection['U'];nt=rules['targets']
    order=result['selection']['schedules'][rec['arm']];arm=result['arms'][rec['arm']]
    ids=[i for i,row in enumerate(arm['rows']) if row['source_scalar'] in order[:rec['prefix']]]
    anchors=arm['anchor_rows'] if rec['scope']=='anchors' else []
    if rec['source_row_indices']!=ids or rec['anchor_rows_inserted']!=len(anchors):raise ValueError('wrong prefix or anchors')
    projected=[old.project(arm['rows'][i],projection,r) for i in ids]+[old.project(row,projection,r) for row in anchors]
    M=[v for v,b in projected];rhs=[b for v,b in projected]
    if rec['base']['columns']!=width:raise ValueError('fixed columns changed')
    old.check_system(rec['base'],M,rhs,r)
    eq=set()
    for v,b in projected:
        row=v+[b];first=next((x for x in row if x),None);eq.add(tuple(x*pow(first,-1,r)%r for x in row) if first else tuple(row))
    if rec['distinct_equations']!=len(eq):raise ValueError('distinct affine count differs')
    target_rows=result['target_collection']['rows'];natural=[old.project(row,projection,r) for row in target_rows]
    first={};cancel=[]
    for i,(row,(v,b)) in enumerate(zip(target_rows,natural,strict=True)):
        t=row['target_index']
        if t not in first:first[t]=i;continue
        j=first[t];oldv,offset=natural[j];weights=[0]*len(natural);weights[i]=1;weights[j]=r-1
        cancel.append(dict(target_row_weights=weights,vector=[(x-y)%r for x,y in zip(v,oldv)],rhs=(b-offset)%r))
    if rec['target_cancellations']!=cancel:raise ValueError('target cancellation certificate differs')
    if len(rec['singles'])!=len(natural):raise ValueError('missing single records')
    for i,(row,(v,b),ident) in enumerate(zip(target_rows,natural,rec['singles'],strict=True)):
        if (ident['target_row_index'],ident['target_index'],ident['offset'])!=(i,row['target_index'],b):raise ValueError('target identity differs')
        old.check_identified(ident,v,M,rhs,rec['base']['kernel'],r)
        if ident['identifiable'] and (ident['scalar']!=(ident['value']-b)%r or multiply(p,0,f['a'],ident['scalar'],tuple(f['P']))!=tuple(row['target_point'])):raise ValueError('single public recovery differs')
    J=[v+[0]*nt for v in M];jr=list(rhs)
    for row,(v,b) in zip(target_rows,natural,strict=True):
        suffix=[0]*nt;suffix[row['target_index']]=r-1;J.append(v+suffix);jr.append(b)
    if rec['joint']['columns']!=width+nt:raise ValueError('joint columns changed')
    old.check_system(rec['joint'],J,jr,r)
    if len(rec['joint_recoveries'])!=nt:raise ValueError('missing target units')
    for t,ident in zip(result['target_generation']['targets'],rec['joint_recoveries'],strict=True):
        v=[0]*(width+nt);v[width+t['index']]=1
        if ident['target_index']!=t['index']:raise ValueError('wrong target unit')
        old.check_identified(ident,v,J,jr,rec['joint']['kernel'],r)
        if ident['identifiable'] and (ident['scalar']!=ident['value'] or multiply(p,0,f['a'],ident['scalar'],tuple(f['P']))!=tuple(t['point'])):raise ValueError('joint public recovery differs')
    outside=rank([v[width:] for v in J],r);after=rank(J,r)-outside
    if rank(M+[v['vector'] for v in cancel],r)!=after:raise ValueError('base-only cancellation rank differs')
    singles=sorted({v['target_index'] for v in rec['singles'] if v['identifiable']});joint=[v['target_index'] for v in rec['joint_recoveries'] if v['identifiable']]
    if (rec['outside_target_rank']!=outside or rec['base_rank_after_target_cancellation']!=after or rec['target_base_rank_gain']!=after-rank(M,r) or rec['single_identified_targets']!=singles or rec['joint_identified_targets']!=joint):raise ValueError('outside-adjusted rank/targets differ')
    A=[old.project(row,projection,r)[0] for row in arm['anchor_rows']];relations=[old.project(arm['rows'][i],projection,r)[0] for i in ids]
    return dict(arm=rec['arm'],prefix=rec['prefix'],scope=rec['scope'],base_columns=width,base_rank=rec['base']['rank'],base_nullity=rec['base']['nullity'],
        source_rows=len(ids),anchor_rows=len(arm['anchor_rows']),anchor_rank=rank(A,r),relation_rank=rank(relations,r),
        anchor_augmented_rank=rank(relations+A,r),distinct_equations=len(eq),outside_target_rank=outside,base_rank_after_target_cancellation=after,
        target_base_rank_gain=after-rank(M,r),single_targets=len(singles),joint_targets=len(joint),
        early_single_targets=len(singles) if rec['base']['nullity'] else 0,early_joint_targets=len(joint) if after<width else 0)


def check(cell,rules,result,events):
    f=cell['fixture'];p,r=f['p'],f['r'];n=len(f['factor_base']);old.verify_fixture(f)
    selected=selection(cell,rules)
    if result['selection']!=selected:raise ValueError('source scalar recipe differs')
    if [{k:v for k,v in e.items() if k!='kind'} for e in events if e.get('kind')=='scalar_candidate']!=selected['search_trace']:raise ValueError('scalar journal differs')
    if result['projection']!=cell['projection'] or result['projection']!=old.public_projection(f,cell['old_source_order']):raise ValueError('old public projection differs')
    if result['target_generation']!=cell['target_generation']:raise ValueError('fixed targets changed')
    orders=selected['schedules'];base=[tuple(a['point']) for a in f['factor_base']]
    signed={(j,s):(q[0],s*q[1]%p) for j,q in enumerate(base) for s in (1,-1)}
    plus=lambda x,y:add(p,0,f['a'],x,y)
    sources={arm:{s:multiply(p,0,f['a'],s,tuple(f['P'])) for s in order} for arm,order in orders.items()}
    targets=cell['target_generation']['targets'];wanted={q for values in sources.values() for q in values.values()}|{tuple(t['point']) for t in targets}
    oracle=defaultdict(list);digest=sha256();count=0
    for triple in combinations(range(n),3):
        for signs in product((1,-1),repeat=3):
            count+=1;Q=plus(plus(signed[triple[0],signs[0]],signed[triple[1],signs[1]]),signed[triple[2],signs[2]])
            digest.update((code([triple,signs,Q])+'\n').encode())
            if Q in wanted:oracle[Q].append((triple,signs))
    def row(s,triple,signs):
        v=[0]*n
        for j,sign in zip(triple,signs):v[j]=sign%r
        return dict(schema='direct-three-sum-row/v1',curve_uid=f['uid'],source_scalar=s,triple=list(triple),signs=list(signs),coefficients=v)
    pairs=[];table=defaultdict(list)
    for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
        Q=plus(signed[j,signs[0]],signed[k,signs[1]]);pairs.append(dict(indices=[j,k],signs=list(signs),point=None if Q is None else list(Q)));table[Q].append(len(pairs)-1)
    if result['pair_entries']!=pairs:raise ValueError('complete pair table differs')
    pair_events=[e for e in events if e.get('kind')=='pair_entry']
    if [e['index'] for e in pair_events]!=list(range(len(pairs))) or [{k:v for k,v in e.items() if k not in ('kind','index')} for e in pair_events]!=pairs:raise ValueError('pair journal differs')
    def queries(points):
        blocks=[];attempts=0;digest=sha256()
        for index,Q in points:
            records=[]
            for third,sign in product(range(n),(1,-1)):
                v=signed[third,sign];key=plus(Q,(v[0],-v[1]%p));bucket=table.get(key,[])
                rec=dict(third=third,sign=sign,wanted=None if key is None else list(key),bucket=list(bucket),accepted=[i for i in bucket if pairs[i]['indices'][1]<third])
                records.append(rec);digest.update((code([index,rec])+'\n').encode());attempts+=1
            blocks.append(dict(index=index,queries=records,attempts=attempts))
        return dict(status_blocks=blocks,attempts=attempts,branch_sha256=digest.hexdigest())
    for arm,order in orders.items():
        value=result['arms'][arm];rows=sorted([row(s,triple,signs) for s,Q in sources[arm].items() for triple,signs in oracle[Q]],key=old.row_key)
        expected=queries([(s,sources[arm][s]) for s in order])
        if value['rows']!=rows or any(value[k]!=v for k,v in expected.items()):raise ValueError('source complete census/query differs')
        actual=sorted([e['row'] for e in events if e.get('kind')=='source_accepted' and e['arm']==arm],key=old.row_key)
        blocks=[{k:v for k,v in e.items() if k not in ('kind','arm','target')} for e in events if e.get('kind')=='query_complete' and e['arm']==arm]
        if actual!=rows or blocks!=expected['status_blocks']:raise ValueError('source journal differs')
        anchors=[]
        for s in order:
            for j,Q in enumerate(base):
                for sign in (1,-1):
                    if sources[arm][s]!=(Q[0],sign*Q[1]%p):continue
                    v=[0]*n;v[j]=sign%r;anchor=dict(schema='explicit-public-anchor/v1',source_scalar=s,atom=j,sign=sign,coefficients=v,public_point=list(sources[arm][s]),projection_atom=result['projection']['native_to_projected'][j])
                    anchor['projected_vector'],anchor['projected_rhs']=old.project(anchor,result['projection'],r);anchors.append(anchor)
        if value['anchor_rows']!=anchors:raise ValueError('explicit anchor equation differs')
        known={}
        for which in (arm,'window'):
            for s,Q in sources[which].items():known[Q]=s;known[(Q[0],-Q[1]%p)]=(-s)%r
        diagnostics=[]
        for t in targets:
            Q=tuple(t['point']);matches=[]
            for k in range(1,rules['collision_multipliers']+1):
                q=multiply(p,0,f['a'],k,Q)
                if q in known:matches.append(dict(multiplier=k,public_source_scalar=known[q]))
            diagnostics.append(dict(target_index=t['index'],direct_public_scalar=known.get(Q),bounded_multiple_matches=matches))
        if value['collision_diagnostics']!=diagnostics:raise ValueError('public collision diagnostic differs')
    rows=[]
    for t in targets:
        for triple,signs in oracle[tuple(t['point'])]:
            v=row(0,triple,signs);v.update(schema='holdout-target-row/v1',target_index=t['index'],target_point=t['point']);rows.append(v)
    rows.sort(key=old.target_key);natural=result['target_collection'];expected=queries([(t['index'],tuple(t['point'])) for t in targets])
    if natural['rows']!=rows or any(natural[k]!=v for k,v in expected.items()):raise ValueError('natural target complete census/query differs')
    blocks=[{k:v for k,v in e.items() if k not in ('kind','arm','target')} for e in events if e.get('kind')=='query_complete' and e['target']]
    if blocks!=expected['status_blocks'] or sorted([e['row'] for e in events if e.get('kind')=='target_accepted'],key=old.target_key)!=rows:raise ValueError('target journal differs')
    planned=[(a,c,s) for a in orders for c in rules['prefixes'] for s in ('relations','anchors')]
    if [(v['arm'],v['prefix'],v['scope']) for v in result['prefixes']]!=planned:raise ValueError('incomplete analysis panel')
    summaries=[check_prefix(cell,rules,result,v) for v in result['prefixes']]
    total=Counter();phases=result['collection_phases']+[p for rec in result['prefixes'] for p in rec['phases']]
    if len({p['phase'] for p in phases})!=len(phases):raise ValueError('duplicate phase label')
    for phase in phases:
        if phase['status']!='complete' or phase['wall_valid']is not False or any(type(v)is not int or v<0 for v in phase['counters'].values()):raise ValueError('invalid disjoint phase')
        total.update(phase['counters'])
    if dict(total)!=result['total_counters'] or total.get('source_queries')!=4*rules['sources']*n*2 or total.get('target_queries')!=rules['targets']*n*2 or total.get('pair_table_insertions')!=len(pairs):raise ValueError('physical counter conservation differs')
    return dict(checked=True,complete_sum_oracle=True,signed_triples_enumerated=count,sum_oracle_sha256=digest.hexdigest(),pair_entries_checked=len(pairs),source_queries_checked=4*rules['sources']*n*2,target_queries_checked=rules['targets']*n*2,prefixes=summaries,
                scope='Separate arithmetic complete sum/table/query/anchor/affine/kernel/certificate/public identity checks; not staffed scientific review or primitive-cost audit.')
