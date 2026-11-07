"""Original-base information after eliminating auxiliary AND target columns."""
from deps19 import solver
from cancel19 import combination


def project(case,prepared,meter):
    """Only the common prerequisite units disappear; private knowledge stays rows."""
    projection=prepared['projection'];old=projection['U'];n=prepared['norm_size'];w=case['width'];nt=case['target_count']
    common=[(j,v[1])for j,v in enumerate(projection['native_to_projected'])if v[0]=='known']
    basis=[None]*old
    for j,v in enumerate(projection['native_to_projected']):
        if v[0]=='unknown':basis[v[1]]=(j,v[2])
    rows,rhs=solver.joint_rows(case);result=[]
    for i,(vector,value) in enumerate(zip(rows,rhs,strict=True)):
        units=[]
        for j,label in common:
            x=vector[j];units.append(meter.ring.sub(0,x)if x else 0)
            if x:value=meter.ring.sub(value,meter.ring.mul(x,label))
        B=[]
        for j,sign in basis:
            x=vector[j];B.append(x if sign==1 or not x else meter.ring.sub(0,x))
        U=vector[n:w]+vector[w:]
        if i<len(case['source']):kind='collected_source'if case['source_origins'][i]['kind']=='collected_source'else'own_K_source'
        else:
            target=case['target'][i-len(case['source'])]
            kind='own_K_target'if target.get('kind')=='base_match'and not any(target['outside'])else'collected_target'
        result.append(dict(vector=B,outside=U,rhs=value,original_index=i,common_unit_weights=units,kind=kind))
        meter.other['information_projected_coefficients_copied']+=len(B)+len(U)
    return dict(old_width=old,outside_width=w-n+nt,common_units=[list(v)for v in common],basis=[list(v)for v in basis],rows=result)


def block(M,rows,width,uw,meter,native_context):
    """Complete left-kernel cancellation, with row weights and direct/cross split."""
    reference=solver.KernelFreeSystem(width,meter);final=solver.KernelFreeSystem(width,meter)
    for v,b in M:reference.add(v,b);final.add(v,b)
    outside=solver.OutsideSystem(uw,meter);cancelled=[];direct=solver.KernelFreeSystem(width,meter)
    for v,b in M:direct.add(v,b)
    B=[v['vector']for v in rows];rhs=[v['rhs']for v in rows]
    for row in rows:
        if not any(row['outside']):direct.add(row['vector'],row['rhs'])
        weights=outside.add_relation(row['outside'])
        if weights is None:continue
        vector,value=combination(weights,B,rhs,width,meter)
        native_weights={}
        for index,a in weights:
            row=rows[index];j=row['original_index']
            native_weights[j]=meter.ring.add(native_weights.get(j,0),a)
            for j,b in zip(native_context['common_indices'],row['common_unit_weights'],strict=True):
                meter.other['information_common_unit_lift_coefficients_scanned']+=1
                if b:native_weights[j]=meter.ring.add(native_weights.get(j,0),meter.ring.mul(a,b))
        native_weights=[[i,a]for i,a in sorted(native_weights.items())if a]
        native_vector,native_value=combination(native_weights,native_context['rows'],native_context['rhs'],native_context['width'],meter)
        expected=[0]*native_context['width']
        for a,(j,s)in zip(vector,native_context['basis'],strict=True):expected[j]=a if s==1 or not a else meter.ring.sub(0,a)
        if native_vector!=expected or native_value!=value:raise ValueError('original native information certificate')
        meter.other['information_original_native_certificates_verified']+=1
        meter.other['information_native_sparse_weight_records']+=len(native_weights)
        cancelled.append(dict(vector=vector,rhs=value,original_weights=weights,original_native_weights=native_weights,old_rowspace=reference.identify(vector)))
        final.add(vector,value)
    rankM=len(reference.pivots);delta=len(final.pivots)-rankM;direct_gain=len(direct.pivots)-rankM
    return dict(reference=reference.summary(),outside=outside.summary(),final=final.summary(),cancellations=cancelled,
        reference_rank=rankM,outside_rank=len(outside.pivots),base_rank_after=len(final.pivots),delta=delta,
        direct_base_gain=direct_gain,cross_row_gain=delta-direct_gain,rows=len(rows))


def measure(reference,case,prepared,meter):
    start=len(meter.phases)
    projected=meter.stage('original_norm_projection',lambda:project(case,prepared,meter))
    width,uw=projected['old_width'],projected['outside_width']
    def context():
        native_rows,native_rhs=solver.joint_rows(case)
        meter.other['information_native_row_coefficients_copied']+=len(native_rows)*(case['width']+case['target_count'])
        common_indices=[]
        for j,label in projected['common_units']:
            unit=[int(k==j)for k in range(case['width'])]
            index=next(i for i,(v,b)in enumerate(case['source'])if v==unit and b==label)
            common_indices.append(index);meter.other['information_common_unit_row_references']+=1
        return dict(rows=native_rows,rhs=native_rhs,width=case['width']+case['target_count'],common_indices=common_indices,basis=projected['basis'])
    native_context=meter.stage('information_native_lift_context',context)
    # Each arm must actually contain the complete norm-only source floor.
    own={(tuple(v['vector']),v['rhs'])for v in projected['rows']if v['kind']=='collected_source'and not any(v['outside'])}
    if not {(tuple(v),b)for v,b in reference}<=own:raise ValueError('own query stream omitted common norm floor')
    result={}
    for name in ('source','full'):
        rows=[v for v in projected['rows']if name=='full'or v['original_index']<len(case['source'])]
        K=[v for v in rows if v['kind'].startswith('own_K')]
        result[name]=dict(row_indices=[v['original_index']for v in rows],K_indices=[v['original_index']for v in K],
            total=meter.stage(name+'_complete_cancellation',lambda rows=rows:block(reference,rows,width,uw,meter,native_context)),
            supplied=meter.stage(name+'_own_K_cancellation',lambda K=K:block(reference,K,width,uw,meter,native_context)))
        result[name]['collected_after_own_K']=result[name]['total']['delta']-result[name]['supplied']['delta']
    phases=meter.phases[start:]
    return dict(schema='prime-field-auxiliary-cancelled-information/v1',projection=projected,reference=reference,views=result,
        target_marginal_delta=result['full']['total']['delta']-result['source']['total']['delta'],
        phases=phases,counters=solver.counters(phases))

