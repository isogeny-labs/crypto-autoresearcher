"""Eliminate auxiliary columns, then recover requested target units.

This is existing linear algebra with explicit original-native certificates.
The control solves the full native system independently. No target is skipped.
"""
from deps19 import solver,partial_solver


def combination(sparse,rows,rhs,width,meter):
    f=meter.ring;vector=[0]*width;value=0
    for index,weight in sparse:
        meter.other['cancellation_weight_visits']+=1
        for j,x in enumerate(rows[index]):
            meter.other['cancellation_coefficients_scanned']+=1
            if x:vector[j]=f.add(vector[j],f.mul(weight,x))
        if rhs[index]:value=f.add(value,f.mul(weight,rhs[index]))
    return vector,value


def solve(case,prepared,meter):
    known,basis=prepared['known'],prepared['basis']
    partial_solver.validate(case,known,basis)
    old=prepared['projection']['U'];nt=case['target_count'];start=len(meter.phases)
    reduced=meter.stage('supplied_unit_substitution',lambda:partial_solver.reduce_case(case,known,basis,meter))
    if old>reduced['width']:raise ValueError('original coordinates missing')
    rows,rhs=meter.stage('reduced_joint_rows',lambda:solver.joint_rows(reduced))
    aux=reduced['width']-old;outside=solver.OutsideSystem(aux,meter);cancellations=[]
    def cancel():
        for i,row in enumerate(rows):
            weights=outside.add_relation(row[old:old+aux])
            if weights is None:continue
            vector,value=combination(weights,rows,rhs,len(row),meter)
            if any(vector[old:old+aux]):raise ValueError('auxiliary cancellation failed')
            cancellations.append(dict(vector=vector[:old]+vector[old+aux:],rhs=value,original_reduced_weights=weights))
    meter.stage('auxiliary_elimination_and_cancellation',cancel)
    system=solver.KernelFreeSystem(old+nt,meter)
    meter.stage('old_base_and_requested_target_elimination',lambda:[system.add(v['vector'],v['rhs'])for v in cancellations])
    def identify():
        records=[]
        for t in range(nt):
            unit=[0]*(old+nt);unit[old+t]=1;rec=system.identify(unit)
            records.append(dict(target_index=t,**rec,scalar=rec['value']))
        return records
    records=meter.stage('requested_target_unit_membership',identify)
    def lift():
        raw_rows=[v for v,b in case['source'][len(known):]]+[v['vector']for v in case['target']]
        for rec in records:
            if not rec['identifiable']:rec['original_row_weights']=None;continue
            weights=[0]*len(rows)
            for coefficient,row in zip(rec['row_weights'],cancellations,strict=True):
                if not coefficient:continue
                for j,x in row['original_reduced_weights']:
                    weights[j]=meter.ring.add(weights[j],meter.ring.mul(coefficient,x))
                    meter.other['auxiliary_native_lift_support']+=1
            units=[0]*len(known)
            for coefficient,row in zip(weights,raw_rows,strict=True):
                if not coefficient:continue
                for k,(j,value) in enumerate(known):
                    meter.other['known_unit_lift_coefficients_scanned']+=1
                    if row[j]:units[k]=meter.ring.sub(units[k],meter.ring.mul(coefficient,row[j]))
            rec['original_row_weights']=units+weights
            meter.other['original_row_weight_coefficients_emitted']+=len(units)+len(weights)
    meter.stage('auxiliary_and_known_unit_native_lifting',lift)
    meter.stage('original_native_certificate_verification',lambda:solver.verify_original(case,records,meter))
    phases=meter.phases[start:]
    return dict(arm='aux_cancel_joint',system=system.summary(),outside=outside.summary(),
        cancellations=cancellations,recoveries=records,old_columns=old,auxiliary_columns=aux,
        phases=phases,counters=solver.counters(phases))
