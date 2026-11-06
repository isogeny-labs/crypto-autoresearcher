"""Symmetric kernel-free row-space recovery and original-row lifting."""
from collections import Counter
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
parent=module('_a10_a9','research/prime_field_a9_json_control_20261105/core.py')
old=parent.old
validate=parent.validate
joint_rows=parent.joint_rows
verify_original=parent.verify_original
counters=parent.counters
class SplitField(old.Field):
    def sub(self,x,y):self.counts['field_sub']+=1;return (x-y)%self.p
class Meter(old.direct.Meter):
    def __init__(self,fixture):
        super().__init__(fixture)
        self.f=SplitField(fixture['p']);self.ring=SplitField(fixture['r'])
        self.e=old.direct.Elliptic(self.f,0,fixture['a'],fixture['b'])
class KernelFreeSystem(old.CertifiedSystem):
    def identify(self,vector,kernel=None):
        if kernel is not None:raise ValueError('production kernel is prohibited')
        if len(vector)!=self.width:raise ValueError('functional width')
        f=self.f;self.meter.other['functional_coefficients_scanned']+=len(vector)
        row={j:x%f.p for j,x in enumerate(vector) if x%f.p}
        self.meter.other['functional_support_entries']+=len(row)
        remaining,value,weights=self.reduce(row,0,{})
        residual=[remaining.get(j,0) for j in range(self.width)]
        self.meter.other['residual_coefficients_emitted']+=self.width
        if remaining:return dict(identifiable=False,value=None,row_weights=None,residual=residual)
        return dict(identifiable=True,value=f.sub(0,value),row_weights=[f.sub(0,weights.get(i,0)) for i in range(len(self.rows))],residual=residual)
    def summary(self):
        return dict(rows=len(self.rows),columns=self.width,rank=len(self.pivots),nullity=self.width-len(self.pivots),kernel_computed=False,
            echelon=[dict(pivot=j,vector=[row.get(k,0) for k in range(self.width)],rhs=b,row_weights=[weights.get(i,0) for i in range(len(self.rows))]) for j,(row,b,weights) in sorted(self.pivots.items())])
def solve(case,arm,meter):
    arm_id=arm
    if arm not in ('sparse_joint','sparse_cancel'):raise ValueError('unknown controlled arm')
    mode,method=arm.split('_');System=KernelFreeSystem
    arm='full_joint' if method=='joint' else 'cancellation_first'
    validate(case);width=case['width'];nt=case['target_count'];r=case['modulus'];start=len(meter.phases)
    if arm=='full_joint':
        matrix,values=meter.stage('joint_matrix_construction',lambda:joint_rows(case))
        system=System(width+nt,meter)
        meter.stage('elimination',lambda:[system.add(v,b) for v,b in zip(matrix,values,strict=True)])
        kernel=None
        def identify():
            result=[]
            for t in range(nt):
                unit=[0]*(width+nt);unit[width+t]=1;value=system.identify(unit,kernel)
                result.append(dict(target_index=t,**value,scalar=value['value']))
            return result
        records=meter.stage('identification',identify)
        def certificates():
            for record in records:
                record['original_row_weights']=record['row_weights']
                meter.other['original_row_weight_coefficients_emitted']+=0 if record['row_weights']is None else len(record['row_weights'])
        meter.stage('certificate_lifting',certificates)
        extra={}
    elif arm=='cancellation_first':
        first={};differences=[];f=meter.ring
        def cancel():
            for i,row in enumerate(case['target']):
                t=row['target_index']
                if t not in first:first[t]=i;continue
                j=first[t];other=case['target'][j]
                differences.append(dict(i=i,j=j,vector=[f.sub(x,y) for x,y in zip(row['vector'],other['vector'],strict=True)],rhs=f.sub(row['rhs'],other['rhs'])))
                meter.other['cancellation_rows_constructed']+=1
        meter.stage('cancellation_construction',cancel)
        system=System(width,meter)
        def insert():
            for v,b in case['source']:system.add(v,b)
            for row in differences:system.add(row['vector'],row['rhs'])
        meter.stage('elimination',insert);kernel=None
        def identify():
            result=[]
            for t in range(nt):
                if t not in first:
                    result.append(dict(target_index=t,representative=None,identifiable=False,value=None,row_weights=None,syndrome=None,scalar=None));continue
                j=first[t];row=case['target'][j];value=system.identify(row['vector'],kernel)
                scalar=f.sub(value['value'],row['rhs']) if value['identifiable'] else None
                result.append(dict(target_index=t,representative=j,**value,scalar=scalar))
            return result
        records=meter.stage('identification',identify)
        def lift():
            for record in records:
                weights=None
                if record['identifiable']:
                    m=len(case['source']);weights=list(record['row_weights'][:m])+[0]*len(case['target'])
                    for w,row in zip(record['row_weights'][m:],differences,strict=True):
                        if not w:continue
                        weights[m+row['i']]=f.add(weights[m+row['i']],w)
                        weights[m+row['j']]=f.sub(weights[m+row['j']],w)
                    rep=m+record['representative'];weights[rep]=f.sub(weights[rep],1)
                    meter.other['original_row_weight_coefficients_emitted']+=len(weights)
                record['original_row_weights']=weights
        meter.stage('certificate_lifting',lift)
        extra=dict(representatives=first,cancellations=differences)
    else:raise ValueError('unknown solver')
    meter.stage('original_row_certificate_verification',lambda:verify_original(case,records,meter))
    phases=meter.phases[start:]
    return dict(arm=arm_id,functional_mode=mode,solver_method=arm,system=system.summary(),recoveries=records,phases=phases,counters=counters(phases),**extra)

