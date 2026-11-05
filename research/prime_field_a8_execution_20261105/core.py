"""Cold paired affine solvers. Native panel access belongs to the admitted driver."""
from collections import Counter
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
old=module('_a8_affine','research/prime_field_a4_execution_20261030/core.py')
class ScalarField:
    """Logical Fr primitive calls; inversion internals are not expanded."""
    def __init__(self,p):self.p=p;self.counts=Counter()
    def add(self,x,y):self.counts['field_add']+=1;return (x+y)%self.p
    def sub(self,x,y):self.counts['field_sub']+=1;return (x-y)%self.p
    def mul(self,x,y):self.counts['field_mul']+=1;return x*y%self.p
    def inv(self,x):self.counts['field_inv']+=1;return pow(x,-1,self.p)

class Meter(old.direct.Meter):
    def __init__(self,fixture):
        super().__init__(fixture);self.ring=ScalarField(fixture['r'])

CertifiedSystem=old.CertifiedSystem
PARAMETERS=dict(systems=288,targets=8,cold_rebuild=True,original_row_certificates=True,maximum_rows=4096,maximum_width=64)
_NATIVE_CAPABILITY=object()


def counters(phases):
    total=Counter()
    for phase in phases:
        if phase['status']!='complete':raise ValueError('incomplete solver phase')
        total.update(phase['counters'])
    return dict(total)


def validate(case):
    width=case['width'];nt=case['target_count'];r=case['modulus']
    if width<0 or nt<0 or width+nt>64 or len(case['source'])+len(case['target'])>4096:raise ValueError('matrix size gate')
    if r<3:raise ValueError('invalid modulus')
    for vector,rhs in case['source']:
        if len(vector)!=width or any(type(x)is not int or not 0<=x<r for x in vector+[rhs]):raise ValueError('source shape/encoding')
    for row in case['target']:
        if len(row['vector'])!=width or not 0<=row['target_index']<nt or any(type(x)is not int or not 0<=x<r for x in row['vector']+[row['rhs']]):raise ValueError('target shape/encoding')


def joint_rows(case):
    width=case['width'];nt=case['target_count'];r=case['modulus']
    rows=[v+[0]*nt for v,b in case['source']];rhs=[b for v,b in case['source']]
    for row in case['target']:
        suffix=[0]*nt;suffix[row['target_index']]=r-1;rows.append(row['vector']+suffix);rhs.append(row['rhs'])
    return rows,rhs


def verify_original(case,records,meter):
    rows,values=joint_rows(case);width=case['width'];nt=case['target_count'];f=meter.ring
    for t,record in enumerate(records):
        if record['target_index']!=t:raise ValueError('target order')
        if not record['identifiable']:
            if record['scalar'] is not None or record['original_row_weights']is not None:raise ValueError('fabricated unidentified value')
            continue
        weights=record['original_row_weights']
        if len(weights)!=len(rows):raise ValueError('lifted certificate length')
        for j in range(width+nt):
            value=0
            for w,row in zip(weights,rows,strict=True):
                if w and row[j]:value=f.add(value,f.mul(w,row[j]))
            if value!=int(j==width+t):raise ValueError('lifted certificate column')
        value=0
        for w,b in zip(weights,values,strict=True):
            if w and b:value=f.add(value,f.mul(w,b))
        if value!=record['scalar']:raise ValueError('lifted certificate RHS')
        meter.other['original_row_certificates_verified']+=1


def solve(case,arm,meter):
    validate(case);width=case['width'];nt=case['target_count'];r=case['modulus'];start=len(meter.phases)
    if arm=='full_joint':
        matrix,values=meter.stage('joint_matrix_construction',lambda:joint_rows(case))
        system=CertifiedSystem(width+nt,meter)
        meter.stage('elimination',lambda:[system.add(v,b) for v,b in zip(matrix,values,strict=True)])
        kernel=meter.stage('kernel',system.kernel)
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
        system=CertifiedSystem(width,meter)
        def insert():
            for v,b in case['source']:system.add(v,b)
            for row in differences:system.add(row['vector'],row['rhs'])
        meter.stage('elimination',insert);kernel=meter.stage('kernel',system.kernel)
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
    return dict(arm=arm,system=system.summary(kernel),recoveries=records,phases=phases,counters=counters(phases),**extra)


def compare(case,fixture,*,capability=None,on_result=None,on_failure=None):
    if capability is not _NATIVE_CAPABILITY and not (fixture.get('software_control')is True and fixture['p']<=211):raise ValueError('native solver comparison requires admission')
    results=[]
    for arm in ('full_joint','cancellation_first'):
        meter=Meter(fixture);result=None
        try:
            result=solve(case,arm,meter)
        except BaseException as error:
            if on_failure:on_failure(arm,list(meter.phases),result,error)
            raise
        def public():
            for record,target in zip(result['recoveries'],case['targets'],strict=True):
                if record['identifiable']:
                    if not meter.equal(meter.e.mul(record['scalar'],tuple(fixture['P'])),tuple(target['point'])):raise ValueError('public target equation')
                    meter.other['public_target_certificates_verified']+=1
        try:
            meter.stage('public_target_verification',public)
        except BaseException as error:
            if on_failure:on_failure(arm,list(meter.phases),result,error)
            raise
        result['phases']=list(meter.phases);result['counters']=counters(meter.phases);results.append(result)
        if on_result:on_result(result)
    return results
