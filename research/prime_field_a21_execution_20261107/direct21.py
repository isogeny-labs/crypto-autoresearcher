"""Meter formal-coordinate substitution and lift to original native rows.

Formal definitions are symbolic identities, never numeric scalar labels.
Every method has the same public input boundary; no checker output is input.
"""
from deps21 import solver,partial_solver,NATIVE_CAPABILITY


def solve(case,prepared,meter,capability=None):
    if prepared['cell']['fixture']['p']>211 and capability is not NATIVE_CAPABILITY:
        raise ValueError('native direct substitution requires admitted driver')
    start=len(meter.phases);f=meter.ring;n=prepared['norm_size'];w=case['width'];nt=case['target_count']
    known=prepared['known'];definitions=prepared['formal_definitions'];k=len(known);d=len(definitions)
    product=lambda a,b:partial_solver.known_solver.product(a,b,meter)

    def acquire():
        partial_solver.validate(case,known,prepared['basis'])
        if prepared['auxiliary_role']!='formalpair16' or d!=w-n or any(j>=n for j,_ in known):
            raise ValueError('formal role/one definition/no numeric auxiliary labels')
        basis=[list(v)for v in prepared['basis']if v[0]<n]
        if len(basis)!=prepared['projection']['U'] or len(known)+len(basis)!=n:
            raise ValueError('old projection width')
        mapping=prepared['projection']['native_to_projected']
        if len(mapping)!=n:raise ValueError('old projection map width')
        for j,label in known:
            if mapping[j]!=['known',label]:raise ValueError('common known map mismatch')
        for i,(j,sign)in enumerate(basis):
            if mapping[j]!=['unknown',i,sign]:raise ValueError('signed ordered old projection mismatch')
        signed=[]
        for i,item in enumerate(definitions):
            meter.other['formal_mapping_component_records_scanned']+=len(item['components'])
            if item['auxiliary_index']!=i or len(item['components'])!=2 or len({j for j,s in item['components']})!=2:
                raise ValueError('two distinct signed old components')
            vector=[0]*n
            for j,sign in item['components']:
                if type(j)is not int or not 0<=j<n or type(sign)is not int or sign not in (-1,1):
                    raise ValueError('signed component encoding')
                vector[j]=1 if sign==1 else f.sub(0,1)
            if vector!=item['old_coefficients']:raise ValueError('formal coefficient multiplicity/sign mismatch')
            native=[f.sub(0,v)if v else 0 for v in vector]+[int(j==i)for j in range(d)]
            meter.other['formal_definition_native_coefficients_compared']+=w
            if case['source'][k+i]!=[native,0] and case['source'][k+i]!=(native,0):
                raise ValueError('ordered original formal definition row mismatch')
            if case['source_origins'][k+i]['kind']!='formal_definition':raise ValueError('definition provenance mismatch')
            signed.append([(j,vector[j])for j,_ in item['components']])
        meter.other['formal_old_mapping_records_scanned']+=n
        return basis,signed
    basis,signed=meter.stage('formal_mapping_acquisition_and_validation',acquire)
    native,native_rhs=meter.stage('native_joint_row_acquisition',lambda:solver.joint_rows(case))
    indices=list(range(k+d,len(native)))

    def project():
        rows=[];rhs=[]
        for index in indices:
            row=native[index];value=native_rhs[index];old=list(row[:n])
            meter.other['formal_native_coefficients_scanned']+=w+nt
            for coefficient,components in zip(row[n:w],signed,strict=True):
                if not coefficient:continue
                for j,sign in components:
                    old[j]=f.add(old[j],product(coefficient,sign))
                    meter.other['formal_signed_component_accumulations']+=1
            for j,label in known:
                if old[j]:value=f.sub(value,product(old[j],label))
                meter.other['formal_common_unit_substitutions_scanned']+=1
            vector=[old[j]if sign==1 or not old[j]else f.sub(0,old[j])for j,sign in basis]
            vector+=row[w:];rows.append(vector);rhs.append(value)
            meter.other['formal_projected_coefficients_emitted']+=len(vector)
        meter.other['formal_definition_rows_elided']+=d
        meter.other['formal_common_unit_rows_elided']+=k
        return rows,rhs
    rows,rhs=meter.stage('formal_signed_expansion_and_common_unit_substitution',project)
    old=len(basis);system=solver.KernelFreeSystem(old+nt,meter)
    meter.stage('direct_old_and_requested_target_elimination',lambda:[system.add(v,b)for v,b in zip(rows,rhs,strict=True)])
    def identify():
        values=[]
        for t in range(nt):
            unit=[0]*(old+nt);unit[old+t]=1;rec=system.identify(unit)
            values.append(dict(target_index=t,**rec,scalar=rec['value']))
        return values
    records=meter.stage('direct_requested_target_unit_membership',identify)

    def lift():
        for rec in records:
            if not rec['identifiable']:rec['original_row_weights']=None;continue
            weights=[0]*len(native)
            for index,a in zip(indices,rec['row_weights'],strict=True):weights[index]=a
            # Actual native combination is charged. Cancel its auxiliary
            # coefficients with original definition rows, then common units.
            vector,_=solver.weighted(weights,native,native_rhs,w+nt,meter)
            for i,coefficient in enumerate(vector[n:w]):
                if not coefficient:continue
                a=f.sub(0,coefficient);weights[k+i]=a
                for j,label in known:
                    x=case['source'][k+i][0][j]
                    if x:vector[j]=f.add(vector[j],product(a,x))
                    meter.other['formal_definition_known_lift_scans']+=1
                meter.other['formal_definition_native_lift_support']+=1
            for i,(j,label)in enumerate(known):weights[i]=f.sub(0,vector[j])if vector[j]else 0
            rec['original_row_weights']=weights
            meter.other['original_row_weight_coefficients_emitted']+=len(weights)
    meter.stage('formal_definition_and_common_unit_native_lifting',lift)
    meter.stage('original_native_certificate_verification',lambda:solver.verify_original(case,records,meter))
    phases=meter.phases[start:]
    return dict(arm='direct_formal',system=system.summary(),recoveries=records,old_columns=old,auxiliary_columns=d,
        projection=dict(rows=rows,rhs=rhs,original_indices=indices,old_basis=basis),phases=phases,counters=solver.counters(phases))
