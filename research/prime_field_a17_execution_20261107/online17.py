"""Maintain known-base target membership; publish positive proofs before skips."""
from copy import deepcopy
from functools import wraps
from deps17 import core,solver,known_solver,require_fields,commitment


def unresolved(index):
    return dict(target_index=index,identifiable=False,value=None,scalar=None,row_weights=None,
                original_row_weights=None,residual=None)


def guarded(method):
    @wraps(method)
    def call(self,*args,**kwargs):
        if self.failed:raise ValueError('online engine already failed; no continuation')
        try:return method(self,*args,**kwargs)
        except BaseException as error:
            self.failed=True
            self.event(dict(kind='online_failed',owner=self.owner,method=method.__name__,
                error_type=type(error).__name__,error=str(error),native_rows_retained=len(self.case['target']),
                certified_prefix=sorted(self.certificates),phases=deepcopy(self.meter.phases),
                counters=self.meter.counters(),partial_work_unknown=True))
            raise
    return call


class Online:
    def __init__(self,case,labels,fixture,rules,event,owner,capability=None,max_rows=4096):
        require_fields(rules,fixture,capability)
        known_solver.validate_labels(case,labels)
        if case['target'] or not 0<case['target_count']<=8 or not 0<case['width']<=48 or case['width']!=len(fixture['factor_base']):
            raise ValueError('online starts from complete known native units and no target rows')
        if not 1<=max_rows<=4096 or not rules.get('software_control') and max_rows!=4096:
            raise ValueError('unchanged native row gate')
        if len(case['source'])>max_rows:raise ValueError('initial row gate')
        self.case=deepcopy(case);self.labels=list(labels);self.fixture=fixture;self.event=event
        self.owner=owner;self.maximum=max_rows;self.certificates={};self.last={};self.serial=0;self.failed=False;self.scanned_rows=None
        self.meter=core.ProgressMeter(fixture,event,dict(kind='online_target_membership',owner=owner))
        self.system=solver.KernelFreeSystem(case['target_count'],self.meter)
        event(dict(kind='online_start',owner=owner,known_case_sha256=commitment(case),target_count=case['target_count']))

    @guarded
    def append(self,row):
        w,nt,r=self.case['width'],self.case['target_count'],self.case['modulus']
        if len(self.case['source'])+len(self.case['target'])>=self.maximum:raise ValueError('online native row size gate')
        if (len(row['vector'])!=w or len(row['outside'])!=nt or
            any(type(v)is not int or not 0<=v<r for v in row['vector']+row['outside']+[row['rhs']])):
            raise ValueError('online native row encoding')
        index=len(self.case['target']);value=deepcopy(row)
        # The row and its prefix are recorded before elimination/correctness can fail.
        self.case['target'].append(value)
        self.event(dict(kind='online_native_row',owner=self.owner,index=index,row=value))
        def insert():
            rhs=value['rhs'];self.meter.other['known_base_coefficients_scanned']+=w
            for coefficient,label in zip(value['vector'],self.labels,strict=True):
                if coefficient:
                    rhs=self.meter.ring.sub(rhs,known_solver.product(coefficient,label,self.meter))
                    self.meter.other['known_base_substitution_support']+=1
            self.system.add(value['outside'],rhs)
        self.meter.stage('online_insert_'+str(index),insert)

    def _lift(self,rec):
        w=self.case['width'];weights=[0]*w
        for weight,row in zip(rec['row_weights'],self.case['target'],strict=True):
            self.meter.other['known_lift_row_weights_scanned']+=1
            if not weight:continue
            for j,value in enumerate(row['vector']):
                self.meter.other['known_lift_base_coefficients_scanned']+=1
                if value:
                    weights[j]=self.meter.ring.sub(weights[j],known_solver.product(weight,value,self.meter))
                    self.meter.other['known_lift_support_visits']+=1
        rec['original_row_weights']=weights+rec['row_weights']
        self.meter.other['original_row_weight_coefficients_emitted']+=len(rec['original_row_weights'])

    @guarded
    def scan(self,origin):
        """Test unresolved coordinates in fixed order; certify before changing state."""
        scan=self.serial;self.serial+=1;new=[]
        for t in range(self.case['target_count']):
            if t in self.certificates:continue
            unit=[int(j==t) for j in range(self.case['target_count'])]
            found=self.meter.stage('online_identify_'+str(scan)+'_'+str(t),lambda:self.system.identify(unit))
            rec=dict(target_index=t,**found,scalar=found['value'])
            self.last[t]=deepcopy(rec)
            if not rec['identifiable']:continue
            self.meter.stage('online_lift_'+str(scan)+'_'+str(t),lambda:self._lift(rec))
            prefix=commitment(self.case);certificate=dict(owner=self.owner,target_index=t,
                rows_at_certificate=len(self.case['target']),case_sha256=prefix,origin=origin,recovery=deepcopy(rec))
            identifier=commitment(certificate)
            self.event(dict(kind='online_certificate_proposed',certificate_id=identifier,certificate=deepcopy(certificate)))
            records=[unresolved(j) for j in range(self.case['target_count'])];records[t]=rec
            self.meter.stage('online_original_certificate_'+str(scan)+'_'+str(t),lambda:solver.verify_original(self.case,records,self.meter))
            def public():
                target=tuple(self.case['targets'][t]['point'])
                if not self.meter.equal(self.meter.e.mul(rec['scalar'],tuple(self.fixture['P'])),target):raise ValueError('online public target certificate')
                self.meter.other['public_target_certificates_verified']+=1
            self.meter.stage('online_public_certificate_'+str(scan)+'_'+str(t),public)
            # Only this post-verification assignment can authorize a future skip.
            certificate['certificate_id']=identifier;certificate['native_verified']=True;certificate['public_verified']=True
            self.certificates[t]=deepcopy(certificate);new.append(identifier)
            self.event(dict(kind='online_target_certified',certificate_id=identifier,certificate=deepcopy(certificate)))
        self.event(dict(kind='online_scan_complete',owner=self.owner,origin=origin,certified_targets=sorted(self.certificates),new_certificates=new))
        self.scanned_rows=len(self.case['target'])
        return new

    def can_skip(self,target):
        if self.failed or self.scanned_rows!=len(self.case['target']):raise ValueError('online skip requires current successful scan')
        if type(target)is not int or not 0<=target<self.case['target_count']:raise ValueError('target index')
        return target in self.certificates

    @guarded
    def snapshot(self):
        if self.scanned_rows!=len(self.case['target']):raise ValueError('final online scan missing')
        count=len(self.case['target']);recoveries=[]
        def materialize():
            for t in range(self.case['target_count']):
                if t in self.certificates:
                    certificate=self.certificates[t];rec=deepcopy(certificate['recovery']);padding=count-certificate['rows_at_certificate']
                    if padding<0:raise ValueError('certificate comes from future rows')
                    rec['row_weights']+=[0]*padding;rec['original_row_weights']+=[0]*padding
                    self.meter.other['online_certificate_zero_padding_coefficients']+=2*padding
                    recoveries.append(rec)
                else:
                    rec=deepcopy(self.last.get(t,unresolved(t)));rec['original_row_weights']=None;recoveries.append(rec)
        self.meter.stage('online_final_certificate_materialization',materialize)
        return dict(arm='online_known',owner=self.owner,system=self.system.summary(),recoveries=recoveries,
            certificates=list(self.certificates.values()),phases=deepcopy(self.meter.phases),counters=self.meter.counters(),
            native_case_sha256=commitment(self.case),complete=True)
