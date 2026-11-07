"""Independent plain expansion, dense membership and native/public certificates."""
from deps21 import check_formal20,check_source,check_solver,known_checks,solver,commitment


def verify(case,prepared,actual):
    r=case['modulus'];n=prepared['norm_size'];w=case['width'];nt=case['target_count']
    expanded,values=check_formal20.expand(case,prepared)
    k=len(prepared['known']);d=len(prepared['formal_definitions']);basis=[v for v in prepared['basis']if v[0]<n]
    indices=list(range(k+d,len(expanded)));rows=[];rhs=[]
    for i in indices:
        vector=expanded[i]
        rows.append([vector[j]*s%r for j,s in basis]+vector[n:])
        rhs.append((values[i]-sum(vector[j]*a for j,a in prepared['known']))%r)
    if actual['arm']!='direct_formal' or actual['projection']!=dict(rows=rows,rhs=rhs,original_indices=indices,old_basis=basis):
        raise ValueError('independent direct projection mismatch')
    rank=check_source.system(actual['system'],rows,rhs,r)
    native,native_rhs=solver.joint_rows(case);native_rank=check_source.rank(native,r)
    if native_rank!=rank+k+d:raise ValueError('direct/native rank bridge')
    if len(actual['recoveries'])!=nt:raise ValueError('direct requested target census')
    for t,rec in enumerate(actual['recoveries']):
        unit=[0]*(len(basis)+nt);unit[len(basis)+t]=1
        check_solver.member(rec,unit,rows,rhs,actual['system'],r)
        native_unit=[0]*(w+nt);native_unit[w+t]=1
        yes=check_source.rank(native+[native_unit],r)==native_rank
        if rec['target_index']!=t or rec['identifiable']is not yes or rec['scalar']!=rec['value']:raise ValueError('direct/native target membership')
        if yes:
            if check_solver.combine(rec['original_row_weights'],native,native_rhs,w+nt,r)!=(native_unit,rec['scalar']):raise ValueError('direct original native certificate')
            f=prepared['cell']['fixture']
            if check_source.old.multiply(f['p'],0,f['a'],rec['scalar'],tuple(f['P']))!=tuple(case['targets'][t]['point']):raise ValueError('direct public target equation')
        elif rec['original_row_weights']is not None:raise ValueError('direct fabricated unresolved target')
    known_checks.phase_counts(actual)
    return dict(checked=True,input_case_sha256=commitment(case),prepared_sha256=commitment(prepared),producer_output_sha256=commitment(actual),
        direct_rank=rank,native_joint_rank=native_rank,common_units=k,formal_definitions=d,identified=sum(v['identifiable']for v in actual['recoveries']))
