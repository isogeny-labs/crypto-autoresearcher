"""Independent dense ranks, kernel action and native cancellation witnesses."""
from deps19 import solver,check_source,check_solver,known_checks,commitment
from check_information import kernel


def combine_sparse(weights,rows,rhs,width,r):
    dense=[0]*len(rows);seen=[]
    for i,a in weights:
        if type(i)is not int or not 0<=i<len(rows)or type(a)is not int or not 0<a<r:raise ValueError('sparse weight encoding')
        seen.append(i);dense[i]=a
    if seen!=sorted(set(seen)):raise ValueError('repeated/unordered sparse weight')
    return check_solver.combine(dense,rows,rhs,width,r)


def cancelled_target(case,prepared,result,fixture=None):
    r=case['modulus'];known=prepared['known'];basis=prepared['basis'];old=prepared['projection']['U'];aux=len(basis)-old;nt=case['target_count']
    raw,values=solver.joint_rows(case)
    rows=[];rhs=[]
    for vector,b in zip(raw[len(known):],values[len(known):],strict=True):
        rows.append([vector[j]*sign%r for j,sign in basis]+vector[case['width']:])
        rhs.append((b-sum(vector[j]*value for j,value in known))%r)
    U=[v[old:old+aux]for v in rows];rankU=check_source.system(result['outside'],U,[0]*len(U),r)
    C=[];d=[];pivots=[]
    for item in result['cancellations']:
        weights=item['original_reduced_weights']
        if not weights or weights[-1][1]!=1:raise ValueError('auxiliary basis normalization')
        pivots.append(weights[-1][0])
        vector,b=combine_sparse(item['original_reduced_weights'],rows,rhs,len(basis)+nt,r)
        if any(vector[old:old+aux])or item['vector']!=vector[:old]+vector[old+aux:]or item['rhs']!=b:raise ValueError('auxiliary cancellation witness')
        C.append(item['vector']);d.append(b)
    if pivots!=sorted(set(pivots))or len(C)!=len(rows)-rankU:raise ValueError('incomplete auxiliary cancellation kernel')
    check_source.system(result['system'],C,d,r)
    if result['arm']!='aux_cancel_joint'or result['old_columns']!=old or result['auxiliary_columns']!=aux:raise ValueError('auxiliary solver role census')
    rank=check_source.rank(raw,r)
    if len(result['recoveries'])!=nt:raise ValueError('requested target census')
    for t,rec in enumerate(result['recoveries']):
        unit=[0]*(old+nt);unit[old+t]=1
        check_solver.member(rec,unit,C,d,result['system'],r)
        native=[0]*(case['width']+nt);native[case['width']+t]=1
        yes=check_source.rank(raw+[native],r)==rank
        if rec['target_index']!=t or rec['identifiable']is not yes or rec['scalar']!=rec['value']:raise ValueError('native target membership')
        if yes:
            if check_solver.combine(rec['original_row_weights'],raw,values,len(native),r)!=(native,rec['scalar']):raise ValueError('native target certificate')
            if fixture and check_source.old.multiply(fixture['p'],0,fixture['a'],rec['scalar'],tuple(fixture['P']))!=tuple(case['targets'][t]['point']):raise ValueError('public target equation')
        elif rec['original_row_weights']is not None:raise ValueError('fabricated unrecovered target')
    known_checks.phase_counts(result)
    return dict(checked=True,native_joint_rank=rank,auxiliary_rank=rankU,identified=sum(v['identifiable']for v in result['recoveries']))


def projected(case,prepared):
    r=case['modulus'];n=prepared['norm_size'];mapping=prepared['projection']['native_to_projected'];old=prepared['projection']['U'];basis=[None]*old
    common=[(j,v[1])for j,v in enumerate(mapping)if v[0]=='known']
    for j,v in enumerate(mapping):
        if v[0]=='unknown':basis[v[1]]=(j,v[2])
    raw,rhs=solver.joint_rows(case);rows=[]
    for i,(v,b)in enumerate(zip(raw,rhs,strict=True)):
        if i<len(case['source']):kind='collected_source'if case['source_origins'][i]['kind']=='collected_source'else'own_K_source'
        else:
            target=case['target'][i-len(case['source'])]
            kind='own_K_target'if target.get('kind')=='base_match'and not any(target['outside'])else'collected_target'
        rows.append(dict(vector=[v[j]*s%r for j,s in basis],outside=v[n:],rhs=(b-sum(v[j]*a for j,a in common))%r,
            original_index=i,common_unit_weights=[-v[j]%r for j,a in common],kind=kind))
    return dict(old_width=old,outside_width=case['width']-n+case['target_count'],common_units=[list(v)for v in common],basis=[list(v)for v in basis],rows=rows)


def information(reference,case,prepared,actual):
    r=case['modulus'];p=projected(case,prepared);width=p['old_width'];uw=p['outside_width']
    if actual['projection']!=p or commitment(actual['reference'])!=commitment(reference):raise ValueError('independent old projection/reference')
    M=[v for v,b in reference];mvalues=[b for v,b in reference];rankM=check_source.rank(M,r);N=kernel(M,width,r)
    if rankM+len(N)!=width or check_source.rank(N,r)!=len(N):raise ValueError('old kernel dimension')
    own={(tuple(v['vector']),v['rhs'])for v in p['rows']if v['kind']=='collected_source'and not any(v['outside'])}
    if not {(tuple(v),b)for v,b in reference}<=own:raise ValueError('missing common floor')
    native,native_rhs=solver.joint_rows(case);common_indices=[]
    for j,label in p['common_units']:
        unit=[int(k==j)for k in range(case['width'])]
        common_indices.append(next(i for i,(v,b)in enumerate(case['source'])if v==unit and b==label))
    verified={}
    for name in ('source','full'):
        rows=[v for v in p['rows']if name=='full'or v['original_index']<len(case['source'])]
        K=[v for v in rows if v['kind'].startswith('own_K')];view=actual['views'][name]
        if view['row_indices']!=[v['original_index']for v in rows]or view['K_indices']!=[v['original_index']for v in K]:raise ValueError('K/collection provenance partition')
        results={}
        for label,subset in (('total',rows),('supplied',K)):
            got=view[label];U=[v['outside']for v in subset];B=[v['vector']for v in subset];rhs=[v['rhs']for v in subset]
            check_source.system(got['reference'],M,mvalues,r)
            ur=check_source.system(got['outside'],U,[0]*len(U),r)
            block=[v+[0]*uw for v in M]+[b+u for b,u in zip(B,U,strict=True)]
            delta=check_source.rank(block,r)-ur-rankM
            direct=check_source.rank(M+[v['vector']for v in subset if not any(v['outside'])],r)-rankM
            C=[];d=[];syndromes=[];pivots=[]
            for item in got['cancellations']:
                weights=item['original_weights']
                if not weights or weights[-1][1]!=1:raise ValueError('cancellation basis normalization')
                pivots.append(weights[-1][0])
                u,_=combine_sparse(weights,U,[0]*len(U),uw,r)
                vector,value=combine_sparse(weights,B,rhs,width,r)
                if any(u)or (vector,value)!=(item['vector'],item['rhs']):raise ValueError('U cancellation/rhs')
                check_solver.member(item['old_rowspace'],vector,M,mvalues,got['reference'],r)
                # Lift the projected cancellation through COMMON prerequisite units
                # and check it against complete original native rows, not just B/U.
                lifted=[0]*len(native)
                for i,a in weights:
                    row=subset[i];lifted[row['original_index']]=(lifted[row['original_index']]+a)%r
                    for j,b in zip(common_indices,row['common_unit_weights'],strict=True):lifted[j]=(lifted[j]+a*b)%r
                if item['original_native_weights']!=[[i,a]for i,a in enumerate(lifted)if a]:raise ValueError('native information sparse weights')
                expected=[0]*(case['width']+case['target_count'])
                for a,(j,s)in zip(vector,p['basis'],strict=True):expected[j]=a*s%r
                if check_solver.combine(lifted,native,native_rhs,len(expected),r)!=(expected,value):raise ValueError('native cancellation lift')
                C.append(vector);d.append(value);syndromes.append([sum(a*b for a,b in zip(vector,n,strict=True))%r for n in N])
            if pivots!=sorted(set(pivots))or len(C)!=len(U)-ur:raise ValueError('incomplete cancellation basis')
            final=check_source.system(got['final'],M+C,mvalues+d,r)
            expected=dict(reference_rank=rankM,outside_rank=ur,base_rank_after=final,delta=delta,direct_base_gain=direct,cross_row_gain=delta-direct,rows=len(subset))
            if any(got[k]!=v for k,v in expected.items())or check_source.rank(syndromes,r)!=delta:raise ValueError('corrected rank/kernel identity')
            results[label]=dict(**expected,old_kernel_syndromes=syndromes)
        if view['collected_after_own_K']!=results['total']['delta']-results['supplied']['delta']:raise ValueError('K conditional delta')
        verified[name]=results
    if actual['target_marginal_delta']!=verified['full']['total']['delta']-verified['source']['total']['delta']:raise ValueError('target marginal information')
    known_checks.phase_counts(actual)
    return dict(checked=True,old_kernel=N,views=verified,producer_output_sha256=commitment(actual))
