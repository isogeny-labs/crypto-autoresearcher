"""Independent plain group, full signed-triple, dense rank and certificate checks."""
from collections import Counter,defaultdict
from itertools import combinations,product
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=module('_a11_source_check_a4','research/prime_field_a4_execution_20261030/check.py')
rank=old.dense_rank

def system(summary,rows,values,r):
    width=summary['columns'];rr=rank(rows,r)
    if summary['kernel_computed']is not False or 'kernel'in summary:raise ValueError('production kernel present')
    if (summary['rank'],summary['nullity'],summary['rows'])!=(rr,width-rr,len(rows)):raise ValueError('system rank/shape')
    if rank([v+[b] for v,b in zip(rows,values,strict=True)],r)!=rr:raise ValueError('affine inconsistency')
    echelon=summary['echelon'];pivots=[]
    for entry in echelon:
        v=entry['vector'];weights=entry['row_weights'];j=entry['pivot'];pivots.append(j)
        if len(v)!=width or len(weights)!=len(rows) or v[j]!=1 or any(v[:j]):raise ValueError('echelon shape')
        if [sum(a*b[k] for a,b in zip(weights,rows,strict=True))%r for k in range(width)]!=v or sum(a*b for a,b in zip(weights,values,strict=True))%r!=entry['rhs']:raise ValueError('echelon certificate')
    if pivots!=sorted(set(pivots)) or len(echelon)!=rr:raise ValueError('incomplete echelon span')
    return rr

def check(case,results,fixture=None):
    w=case['width'];nt=case['target_count'];r=case['modulus'];M=[v for v,b in case['source']];bm=[b for v,b in case['source']]
    rows=[v+[0]*nt for v in M];values=list(bm)
    for row in case['target']:
        suffix=[0]*nt;suffix[row['target_index']]=r-1;rows.append(row['vector']+suffix);values.append(row['rhs'])
    rr=rank(rows,r);outside=rank([v[w:] for v in rows],r);before=rank(M,r);first={};C=[];d=[];diff=[]
    for i,row in enumerate(case['target']):
        t=row['target_index']
        if t not in first:first[t]=i;continue
        j=first[t];other=case['target'][j];v=[(x-y)%r for x,y in zip(row['vector'],other['vector'],strict=True)];b=(row['rhs']-other['rhs'])%r
        C.append(v);d.append(b);diff.append(dict(i=i,j=j,vector=v,rhs=b))
    if rr-outside!=rank(M+C,r):raise ValueError('outside-column cancellation identity')
    if [a['arm'] for a in results]!=['sparse_joint','sparse_cancel']:raise ValueError('paired solver coverage')
    for result in results:
        full=result['arm']=='sparse_joint';A=rows if full else M+C;b=values if full else bm+d
        if result['system']['columns']!=(w+nt if full else w):raise ValueError('wrong solver width')
        system(result['system'],A,b,r)
        if not full and ({int(k):v for k,v in result['representatives'].items()}!=first or result['cancellations']!=diff):raise ValueError('cancellation recipe')
        if len(result['recoveries'])!=nt:raise ValueError('missing target outcomes')
        for t,rec in enumerate(result['recoveries']):
            unit=[0]*(w+nt);unit[w+t]=1;identified=rank(rows+[unit],r)==rr
            if rec['target_index']!=t or rec['identifiable']is not identified:raise ValueError('dense target membership')
            query=unit if full else None if t not in first else case['target'][first[t]]['vector']
            if not full and rec['representative']!=first.get(t):raise ValueError('target representative')
            if query is not None:
                residual=list(query)
                for entry in result['system']['echelon']:
                    scale=residual[entry['pivot']]
                    residual=[(x-scale*y)%r for x,y in zip(residual,entry['vector'],strict=True)]
                if rec['residual']!=residual or (not any(residual))is not identified:raise ValueError('residual certificate')
            if identified:
                weights=rec['original_row_weights']
                if len(weights)!=len(rows) or [sum(a*v[j] for a,v in zip(weights,rows,strict=True))%r for j in range(w+nt)]!=unit:raise ValueError('original-row coefficient certificate')
                if sum(a*b for a,b in zip(weights,values,strict=True))%r!=rec['scalar']:raise ValueError('original-row RHS certificate')
                reduced_weights=rec['row_weights']
                if len(reduced_weights)!=len(A) or [sum(a*v[j] for a,v in zip(reduced_weights,A,strict=True))%r for j in range(len(query))]!=query:raise ValueError('functional coefficient certificate')
                if sum(a*b for a,b in zip(reduced_weights,b,strict=True))%r!=rec['value']:raise ValueError('functional RHS certificate')
                scalar=rec['value'] if full else (rec['value']-case['target'][first[t]]['rhs'])%r
                if scalar!=rec['scalar']:raise ValueError('target offset')
                if fixture is not None and old.multiply(fixture['p'],0,fixture['a'],scalar,tuple(fixture['P']))!=tuple(case['targets'][t]['point']):raise ValueError('independent public certificate')
            elif any(rec[k]is not None for k in ('scalar','value','row_weights','original_row_weights')):raise ValueError('fabricated nonmembership value')
        totals=Counter();names=[]
        for phase in result['phases']:
            if phase['status']!='complete' or phase['wall_valid']is not False or any(type(v)is not int or v<0 for v in phase['counters'].values()):raise ValueError('phase validity')
            names.append(phase['phase']);totals.update(phase['counters'])
        expected=['joint_matrix_construction' if full else 'cancellation_construction','elimination','identification','certificate_lifting','original_row_certificate_verification']+(['public_target_verification'] if fixture else [])
        if names!=expected or dict(totals)!=result['counters']:raise ValueError('phase accounting')
    outcome=lambda x:[(v['identifiable'],v['scalar']) for v in x['recoveries']]
    if outcome(results[0])!=outcome(results[1]):raise ValueError('paired outcomes disagree')
    return dict(checked=True,identified=sum(v['identifiable'] for v in results[0]['recoveries']),joint_rank=rr,outside_rank=outside,source_rank=before,delta=rr-outside-before,base_rank_after_cancellation=rr-outside)

def expected_case(cell,collected,arm,prefix,scope):
    values=collected['selection']['orders'][arm][:prefix];projection=collected['projection'];r=cell['fixture']['r']
    rows=[v for v in collected['arms'][arm]['rows'] if v['source_scalar']in values]
    if scope=='anchors':rows += [v for v in collected['arms'][arm]['anchors'] if v['prefix']<=prefix]
    source=[old.project(v,projection,r) for v in rows]
    target=[dict(target_index=v['target_index'],vector=pair[0],rhs=pair[1]) for v in collected['target_collection']['rows'] for pair in [old.project(v,projection,r)]]
    if scope=='anchors':
        public={match['target_index']:match['scalar'] for point in collected['arms'][arm]['knowledge'] if point['prefix']<=prefix for match in point.get('direct_targets',[])}
        target += [dict(target_index=t,vector=[0]*projection['U'],rhs=-s%r) for t,s in sorted(public.items())]
    return dict(width=projection['U'],target_count=len(collected['target_generation']['targets']),modulus=r,source=source,target=target,targets=collected['target_generation']['targets'])


def scalar_replay(r,window,workloads,original):
    """Independent integer implementation of positional digits and binary calls."""
    known=set(original)|{0};discovery=[];calls=0;tables=[]
    def add(a,b):
        nonlocal calls
        calls+=1;s=(a+b)%r
        if s not in known:known.add(s);discovery.append(s)
        return s
    if window and any(s not in known for s in workloads):
        remaining=r-1;base=1
        while remaining:
            largest=min((1<<window)-1,remaining);digits=[0,base]
            for _ in range(2,largest+1):digits.append(add(digits[-1],base))
            tables.append(digits);remaining>>=window
            if remaining:
                for _ in range(window):base=add(base,base)
    prefix=[]
    for s in workloads:
        if s not in known:
            out=0;k=s
            if window:
                i=0
                while k:
                    digit=k&((1<<window)-1)
                    if digit:out=add(out,tables[i][digit])
                    k>>=window;i+=1
            else:
                point=1
                while k:
                    if k&1:out=add(out,point)
                    point=add(point,point);k>>=1
            if out!=s:raise ValueError('independent scalar constructor')
        prefix.append(list(discovery))
    return dict(calls=calls,known=known,discovery=discovery,prefix=prefix,table_entries=sum(map(len,tables)))

def collection(cell,rules,collected):
    f=cell['fixture'];p=f['p'];r=f['r'];base=[tuple(v['point']) for v in f['factor_base']];n=len(base);uid=f['ec1']['curve_uid']
    add=lambda a,b:old.add(p,0,f['a'],a,b)
    mul=lambda s:old.multiply(p,0,f['a'],s,tuple(f['P']))
    signed={(j,s):q if s==1 else (q[0],-q[1]%p) for j,q in enumerate(base) for s in (1,-1)}
    triples=defaultdict(list);oracle_count=0
    for triple,signs in product(combinations(range(n),3),product((1,-1),repeat=3)):
        q=None
        for j,s in zip(triple,signs,strict=True):q=add(q,signed[j,s])
        triples[q].append((triple,signs));oracle_count+=1
    def descriptors(rows):
        for row in rows:
            coefficients=[0]*n
            for j,sign in zip(row['triple'],row['signs'],strict=True):coefficients[j]=(coefficients[j]+sign)%r
            if row['coefficients']!=coefficients or row['curve_uid']!=f['uid']:raise ValueError('relation coefficient/curve encoding')
        return sorted((tuple(v['triple']),tuple(v['signs'])) for v in rows)
    if collected['projection']!=old.public_projection(f,list(range(1,rules['prerequisite']+1))):raise ValueError('fixed public projection')
    pair_table=defaultdict(list);expected_pairs=[]
    for (j,k),signs in product(combinations(range(n),2),product((1,-1),repeat=2)):
        point=add(signed[j,signs[0]],signed[k,signs[1]])
        pair_table[point].append(len(expected_pairs));expected_pairs.append(dict(indices=[j,k],signs=list(signs),point=None if point is None else list(point)))
    if collected['pairs']!=expected_pairs:raise ValueError('pair table completeness')
    def queries(points,trace):
        expected=[]
        for index,Q in points:
            for third,sign in product(range(n),(1,-1)):
                q=signed[third,sign];wanted=add(Q,(q[0],-q[1]%p));bucket=pair_table.get(wanted,[])
                accepted=[i for i in bucket if expected_pairs[i]['indices'][1]<third]
                expected.append(dict(index=index,third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=bucket,accepted=accepted))
        if trace!=expected:raise ValueError('query/miss/bucket trace')
    targets=collected['target_generation']['targets'];used=set();trace=[]
    roots={}
    for y in range(p):roots.setdefault(y*y%p,y)
    for t in targets:
        for counter in range(rules['maximum_target_candidates']):
            x=int(old.hashed(rules['domain'],'target',uid,t['index'],counter),16)%p;y=roots.get((x**3+f['a']*x+f['b'])%p);q=None if y is None else (x,y)
            reason='not_rational' if y is None else 'duplicate_target' if q in used else 'selected'
            trace.append(dict(target_index=t['index'],counter=counter,x=x,y=y,reason=reason))
            if reason=='selected':
                if list(q)!=t['point']:raise ValueError('target recipe')
                used.add(q);break
        else:raise ValueError('target gate')
        rows=[v for v in collected['target_collection']['rows'] if v['target_index']==t['index']]
        if any(v['source_scalar']!=0 or v['target_point']!=t['point'] for v in rows):raise ValueError('target row encoding')
        if descriptors(rows)!=sorted(triples[tuple(t['point'])]):raise ValueError('full natural target oracle')
    queries([(t['index'],tuple(t['point'])) for t in targets],collected['target_collection']['trace'])
    if trace!=collected['target_generation']['search_trace']:raise ValueError('target candidate trace')
    original=list(range(1,rules['prerequisite']+1));orders=collected['selection']['orders'];selection_trace=[]
    for seed in rules['seeds']:
        for counter in range(rules['maximum_scalar_candidates']):
            a=1+int(old.hashed(rules['domain'],'ap-start',uid,seed,counter),16)%(r-1);d=1+int(old.hashed(rules['domain'],'ap-step',uid,seed,counter),16)%(r-1)
            order=[(a+i*d)%r for i in range(rules['sources'])];selected=0 not in order
            selection_trace.append(dict(kind='ap_candidate',seed=seed,counter=counter,a=a,d=d,selected=selected,reason='selected' if selected else 'zero_in_horizon'))
            if selected:
                if orders['ap'+str(seed)]!=order or collected['selection']['ap']['ap'+str(seed)]!=dict(a=a,d=d):raise ValueError('AP recipe')
                break
        else:raise ValueError('AP candidate gate')
        order=[];seen=set()
        for index in range(rules['sources']):
            for counter in range(rules['maximum_scalar_candidates']):
                s=1+int(old.hashed(rules['domain'],'hash',uid,seed,index,counter),16)%(r-1);selected=s not in seen
                selection_trace.append(dict(kind='hash_candidate',seed=seed,index=index,counter=counter,scalar=s,selected=selected))
                if selected:order.append(s);seen.add(s);break
            else:raise ValueError('hash candidate gate')
        if orders['hash'+str(seed)]!=order:raise ValueError('hash recipe')
    if selection_trace!=collected['selection']['trace']:raise ValueError('source candidate trace')
    checks=[]
    for arm,rec in collected['arms'].items():
        values=orders[arm]
        if [v['scalar'] for v in rec['sources']]!=values:raise ValueError('source prefix completeness')
        if len(rec['knowledge'])!=len({v['scalar'] for v in rec['knowledge']}):raise ValueError('duplicate known point')
        for point in rec['sources']:
            expected_budget=next(b for b in rules['prefixes'] if b>values.index(point['scalar']))
            if point['prefix']!=expected_budget:raise ValueError('source prefix availability')
        queries([(v['scalar'],tuple(v['point'])) for v in rec['sources']],rec['query_trace'])
        work=[collected['selection']['ap'][arm][k] for k in ('a','d')] if arm.startswith('ap') else values
        predictions=[scalar_replay(r,w,work,original) for w in range(9)]
        expected=[dict(window=w,group_add_calls=v['calls'],table_entries=v['table_entries'],known_labels=len(v['known'])) for w,v in enumerate(predictions)]
        choice=min(expected,key=lambda v:(v['group_add_calls'],v['window']))
        if rec['selection']['candidates']!=expected or rec['selection']['window']!=choice['window']:raise ValueError('constructor selection')
        predicted=predictions[choice['window']];first_budget={s:0 for s in original}
        for b in rules['prefixes']:
            if not b:continue
            labels=predicted['discovery'] if arm.startswith('ap') else predicted['prefix'][b-1]
            for s in labels:first_budget.setdefault(s,b)
            if arm.startswith('ap'):
                for s in values[:b]:first_budget.setdefault(s,b)
        actual={v['scalar']:v for v in rec['knowledge']}
        if set(actual)!=set(first_budget):raise ValueError('constructor point knowledge completeness')
        for scalar,item in actual.items():
            if item['prefix']!=first_budget[scalar] or tuple(item['point'])!=mul(scalar):raise ValueError('future or false known point')
            direct=[]
            for t in targets:
                for sign,q in ((1,tuple(item['point'])),(-1,(item['point'][0],-item['point'][1]%p))):
                    if tuple(t['point'])==q:direct.append(dict(target_index=t['index'],scalar=scalar if sign==1 else -scalar%r))
            if item.get('direct_targets',[])!=direct:raise ValueError('direct target knowledge')
        expected_anchors=set()
        for scalar,item in actual.items():
            for j,q in enumerate(base):
                if q==tuple(item['point']):expected_anchors.add((j,scalar,item['prefix']))
                if q==(item['point'][0],-item['point'][1]%p):expected_anchors.add((j,-scalar%r,item['prefix']))
        # Repeated scalar knowledge may discover the same anchor at different times;
        # producer keeps only the earliest public availability.
        earliest={}
        for j,s,b in expected_anchors:earliest[j,s]=min(b,earliest.get((j,s),b))
        if {(v['atom'],v['source_scalar'],v['prefix']) for v in rec['anchors']}!={(j,s,b) for (j,s),b in earliest.items()}:raise ValueError('explicit anchors completeness')
        for anchor in rec['anchors']:
            unit=[0]*n;unit[anchor['atom']]=1
            if anchor['coefficients']!=unit:raise ValueError('anchor coefficients')
        for point in rec['sources']:
            if tuple(point['point'])!=mul(point['scalar']):raise ValueError('source construction')
            rows=[v for v in rec['rows'] if v['source_scalar']==point['scalar']]
            if descriptors(rows)!=sorted(triples[tuple(point['point'])]):raise ValueError('full source signed triple oracle')
        calls=sum(v['counters'].get('constructor_group_add_calls',0) for v in collected['collection_phases'] if v['phase'].startswith(arm+'_'))
        if calls!=choice['group_add_calls']+(rules['sources']-1 if arm.startswith('ap') else 0):raise ValueError('constructor physical call prediction')
        checks.append(dict(arm=arm,constructor_calls=calls,source_rows=len(rec['rows']),known_points=len(actual)))
    return dict(checked=True,signed_triple_oracle=oracle_count,arms=checks),dict(triples)

def check_generation(rules,generated):
    roots={};used={tuple(v) for v in rules['excluded_curves']};cells=[];trace=[];point_tests=0
    for field in rules['fields']:
        p=field['p'];root={}
        for y in range(p): root.setdefault(y*y%p,y)
        roots[p]=root
        for index in range(rules['curves_per_field']):
            for counter in range(rules['maximum_curve_candidates']):
                b=1+int(old.hashed(rules['domain'],'curve',p,index,counter),16)%(p-1);a=rules['a'];fixture=None
                if b%p==0 or (4*a*a*a+27*b*b)%p==0: trial=dict(reason='singular_or_zero_B',point_tests=0)
                else:
                    r=p+1+sum(0 if (u:=(x**3+a*x+b)%p)==0 else 1 if u in root else -1 for x in range(p));point_tests+=p
                    trial=dict(reason='composite_order',r=r,point_tests=p)
                    if r>2 and old.prime(r):
                        P=next((x,root[(x**3+a*x+b)%p]) for x in range(p) if (x**3+a*x+b)%p in root)
                        base=[];seen=set()
                        for x in range(p):
                            u=x*x%p;y=root.get((u**3+a*u+b)%p)
                            if y is None or u in seen: continue
                            seen.add(u);base.append(dict(point=[u,y],lift=[x,y]))
                            if len(base)==field['base_size']: break
                        if len(base)!=field['base_size']: trial.update(reason='insufficient_distinct_factor_base',base_size=len(base))
                        else:
                            fixture=dict(p=p,a=a,b=b,r=r,P=list(P),factor_base=base)
                            trial['reason']='eligible'
                if (p,b) in used: fixture=None;trial['reason']='excluded_or_duplicate_curve'
                if fixture is not None and fixture['r']==p: fixture=None;trial['reason']='anomalous_order_excluded'
                trace.append(dict(p=p,curve_index=index,counter=counter,b=b,**trial))
                if fixture is None: continue
                actual=generated['cells'][len(cells)];f=actual['fixture']
                if any(f[k]!=v for k,v in fixture.items()): raise ValueError('holdout selection/base differs from independent construction')
                uid=__import__('hashlib').sha256(old.encoded(fixture).encode()).hexdigest()
                if f['uid']!=uid: raise ValueError('fixture UID differs')
                field_data=dict(characteristic=p,degree=1,representation='Z/pZ',element_encoding='canonical integers 0..p-1')
                curve=dict(model='short_weierstrass',a4=a,a6=b,subgroup_order=f['r'],cofactor=1,generator=f['P'],target_group='E(Fp)')
                identity=old.curve_identity(field_data,curve,'prymtoy');curve['curve_id']=identity['curve_id']
                if f['ec1']!=dict(field=field_data,curve=curve,**identity): raise ValueError('canonical EC1 identity differs')
                if actual['id']!='p'+str(p)+'-i'+str(index):raise ValueError('cell identity')
                old.verify_fixture(f);cells.append(actual);used.add((p,b));break
            else: raise ValueError('independent candidate gate exhausted')
    if generated.get('complete')is not True or generated['search_trace']!=trace or len(generated['cells'])!=len(cells): raise ValueError('full curve selection trace differs')
    return dict(checked=True,curves=len(cells),candidate_records=len(trace),order_point_tests=point_tests,scope='Independent complete eligibility/base construction and EC1 metadata; producer field-operation counts not audited.')
