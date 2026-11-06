"""Kernel-free joint and outside-first solvers for arbitrary affine U columns."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
parent=module('_a12_kernel_free','research/prime_field_a10_execution_20261106/solver.py')
Meter=parent.Meter;old=parent.old;counters=parent.counters

def normalize_pivot(row,value,weights,pivot,meter):
    f=meter.ring;lead=row[pivot]
    if lead==1:
        meter.other['unit_pivot_shortcuts']+=1;return row,value,weights
    if lead==f.p-1:
        meter.other['negative_unit_pivot_shortcuts']+=1
        return {j:f.sub(0,x) for j,x in row.items()},f.sub(0,value) if value else 0,{j:f.sub(0,x) for j,x in weights.items()}
    inverse=f.inv(lead)
    return {j:f.mul(x,inverse) for j,x in row.items()},f.mul(value,inverse) if value else 0,{j:f.mul(x,inverse) for j,x in weights.items()}

class KernelFreeSystem(parent.KernelFreeSystem):
    def add(self,vector,rhs):
        if len(vector)!=self.width:raise ValueError('affine width')
        f=self.f;row={j:x%f.p for j,x in enumerate(vector) if x%f.p};i=len(self.rows)
        reduced,value,weights=self.reduce(dict(row),rhs%f.p,{i:1})
        if not reduced and value:raise ValueError('inconsistent affine system')
        if reduced:
            pivot=min(reduced);self.pivots[pivot]=normalize_pivot(reduced,value,weights,pivot,self.meter)
        self.rows.append([row.get(j,0) for j in range(self.width)]);self.rhs.append(rhs%f.p);self.meter.other['affine_rows_inserted']+=1

def validate(case):
    w=case['width'];nt=case['target_count'];r=case['modulus']
    if w<0 or nt<0 or w+nt>64 or len(case['source'])+len(case['target'])>4096:raise ValueError('matrix size gate')
    if r<3:raise ValueError('modulus')
    for v,b in case['source']:
        if len(v)!=w or any(type(x)is not int or not 0<=x<r for x in v+[b]):raise ValueError('source encoding')
    for row in case['target']:
        if len(row['vector'])!=w or len(row['outside'])!=nt or any(type(x)is not int or not 0<=x<r for x in row['vector']+row['outside']+[row['rhs']]):raise ValueError('affine target encoding')

def joint_rows(case):
    nt=case['target_count'];rows=[v+[0]*nt for v,b in case['source']];rhs=[b for v,b in case['source']]
    for row in case['target']:rows.append(row['vector']+row['outside']);rhs.append(row['rhs'])
    return rows,rhs

def weighted(coefficients,rows,values,width,meter):
    f=meter.ring;vector=[0]*width;value=0
    meter.other['weighted_row_coefficients_scanned']+=len(coefficients)
    for a,row,b in zip(coefficients,rows,values,strict=True):
        if not a:continue
        for j,x in enumerate(row):
            if x:vector[j]=f.add(vector[j],f.mul(a,x));meter.other['weighted_support_visits']+=1
        if b:value=f.add(value,f.mul(a,b))
    return vector,value

class OutsideSystem(KernelFreeSystem):
    def add_relation(self,vector):
        f=self.f;index=len(self.rows);row={j:x%f.p for j,x in enumerate(vector) if x%f.p}
        residual,value,weights=self.reduce(dict(row),0,{index:1})
        self.rows.append([row.get(j,0) for j in range(self.width)]);self.rhs.append(0)
        self.meter.other['outside_rows_inserted']+=1
        if residual:
            pivot=min(residual);self.pivots[pivot]=normalize_pivot(residual,0,weights,pivot,self.meter)
            return None
        return [[i,a] for i,a in sorted(weights.items()) if a]

def verify_original(case,records,meter):
    rows,values=joint_rows(case);w=case['width'];nt=case['target_count'];f=meter.ring
    for t,rec in enumerate(records):
        if rec['target_index']!=t:raise ValueError('target order')
        if not rec['identifiable']:
            if rec['scalar']is not None or rec['original_row_weights']is not None:raise ValueError('fabricated unresolved target')
            continue
        coefficients=rec['original_row_weights']
        if len(coefficients)!=len(rows):raise ValueError('original certificate length')
        v,b=weighted(coefficients,rows,values,w+nt,meter);unit=[0]*(w+nt);unit[w+t]=1
        if v!=unit or b!=rec['scalar']:raise ValueError('original coefficient/RHS certificate')
        meter.other['original_row_certificates_verified']+=1

def solve(case,arm,meter):
    validate(case);w=case['width'];nt=case['target_count'];r=case['modulus'];f=meter.ring;start=len(meter.phases);extra={}
    if arm=='sparse_joint':
        rows,rhs=meter.stage('joint_matrix_construction',lambda:joint_rows(case));system=KernelFreeSystem(w+nt,meter)
        meter.stage('elimination',lambda:[system.add(v,b) for v,b in zip(rows,rhs,strict=True)])
        def identify():
            records=[]
            for t in range(nt):
                unit=[0]*(w+nt);unit[w+t]=1;value=system.identify(unit)
                records.append(dict(target_index=t,**value,scalar=value['value']))
            return records
        records=meter.stage('identification',identify)
        def lift():
            for rec in records:
                rec['original_row_weights']=rec['row_weights'];meter.other['original_row_weight_coefficients_emitted']+=0 if rec['row_weights']is None else len(rec['row_weights'])
        meter.stage('certificate_lifting',lift)
    elif arm=='sparse_cancel':
        outside=OutsideSystem(nt,meter);cancellations=[];B=[row['vector'] for row in case['target']];bB=[row['rhs'] for row in case['target']]
        def cancel():
            for i,row in enumerate(case['target']):
                coefficients=outside.add_relation(row['outside'])
                if coefficients is None:continue
                v=[0]*w;b=0
                for i,a in coefficients:
                    for j,x in enumerate(B[i]):
                        if x:v[j]=f.add(v[j],f.mul(a,x));meter.other['weighted_support_visits']+=1
                    if bB[i]:b=f.add(b,f.mul(a,bB[i]))
                meter.other['sparse_cancellation_coefficients']+=len(coefficients)
                cancellations.append(dict(vector=v,rhs=b,original_target_weights=coefficients));meter.other['cancellation_rows_constructed']+=1
        meter.stage('outside_elimination_cancellation',cancel)
        system=KernelFreeSystem(w,meter)
        def eliminate():
            for v,b in case['source']:system.add(v,b)
            for row in cancellations:system.add(row['vector'],row['rhs'])
        meter.stage('elimination',eliminate)
        def identify():
            records=[]
            for t in range(nt):
                unit=[0]*nt;unit[t]=1;outer=outside.identify(unit)
                if not outer['identifiable']:
                    records.append(dict(target_index=t,identifiable=False,scalar=None,value=None,row_weights=None,outer=outer,base_query=None,base_rhs=None,residual=None));continue
                query,offset=weighted(outer['row_weights'],B,bB,w,meter);value=system.identify(query)
                scalar=f.sub(offset,value['value']) if value['identifiable'] else None
                records.append(dict(target_index=t,**value,scalar=scalar,outer=outer,base_query=query,base_rhs=offset))
            return records
        records=meter.stage('identification',identify)
        def lift():
            m=len(case['source']);n=len(B)
            for rec in records:
                if not rec['identifiable']:rec['original_row_weights']=None;continue
                weights=[0]*(m+n)
                for i,a in enumerate(rec['outer']['row_weights']):weights[m+i]=a
                for i,a in enumerate(rec['row_weights'][:m]):
                    if a:weights[i]=f.sub(0,a)
                for a,row in zip(rec['row_weights'][m:],cancellations,strict=True):
                    if not a:continue
                    for j,b in row['original_target_weights']:weights[m+j]=f.sub(weights[m+j],f.mul(a,b))
                rec['original_row_weights']=weights;meter.other['original_row_weight_coefficients_emitted']+=len(weights)
        meter.stage('certificate_lifting',lift);extra=dict(outside=outside.summary(),cancellations=cancellations)
    else:raise ValueError('unknown solver')
    meter.stage('original_row_certificate_verification',lambda:verify_original(case,records,meter));phases=meter.phases[start:]
    return dict(arm=arm,system=system.summary(),recoveries=records,phases=phases,counters=counters(phases),**extra)
