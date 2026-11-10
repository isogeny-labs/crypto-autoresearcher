"""Prepared general-functional component: marked software controls ONLY.

Native rollout needs a new published/frozen/admitted contract. In particular,
36 queries are not 36 target unknowns or 36 batch solver calls. This module
cannot be used to run the four conditioned native follow-up cases yet.
"""
from deps22 import solver,check_source,known_checks,commitment
from deps21 import check_solver
from check_information import kernel


def family(r):
    values=[]
    for i in range(8):
        v=[0]*8;v[i]=1;values.append(v)
    for i in range(8):
        for j in range(i+1,8):
            v=[0]*8;v[i]=1;v[j]=r-1;values.append(v)
    return values


def marked_only(fixture):
    if fixture['p']>211:raise ValueError('follow-up native admission contract is not implemented')


def solve(case,fixture,meter):
    marked_only(fixture);solver.validate(case)
    if case['target_count']!=8:raise ValueError('eight target unknowns required')
    w=case['width'];queries=family(case['modulus']);start=len(meter.phases)
    def construct():
        points=[]
        for v in queries:
            point=None
            for i,a in enumerate(v):
                if not a:continue
                q=tuple(case['targets'][i]['point'])
                if a==case['modulus']-1:q=meter.neg(q)
                point=q if point is None else meter.e.add(point,q)
                meter.other['functional_public_point_terms']+=1
            points.append(point)
        return points
    points=meter.stage('all_prespecified_public_functionals_before_outcomes',construct)
    rows,rhs=meter.stage('native_joint_matrix',lambda:solver.joint_rows(case));system=solver.KernelFreeSystem(w+8,meter)
    meter.stage('native_rowspace_elimination',lambda:[system.add(v,b)for v,b in zip(rows,rhs,strict=True)])
    def identify():
        records=[]
        for i,v in enumerate(queries):
            rec=system.identify([0]*w+v)
            records.append(dict(query_index=i,coefficients=v,public_point=points[i],**rec,
                scalar=rec['value'],original_row_weights=rec['row_weights']if rec['identifiable']else None))
        return records
    records=meter.stage('all_36_functional_membership_queries',identify)
    def verify():
        for rec in records:
            if not rec['identifiable']:
                if rec['scalar']is not None or rec['original_row_weights']is not None:raise ValueError('fabricated unresolved functional')
                continue
            vector,value=solver.weighted(rec['original_row_weights'],rows,rhs,w+8,meter)
            if vector!=[0]*w+rec['coefficients']or value!=rec['scalar']:raise ValueError('general functional native certificate')
            if not meter.equal(meter.e.mul(value,tuple(fixture['P'])),rec['public_point']):raise ValueError('general functional public equation')
    meter.stage('general_native_and_public_functional_certificates',verify)
    phases=meter.phases[start:]
    return dict(arm='prepared_native_functionals',target_unknowns=8,functional_queries=36,actual_batch_calls=1,
        system=system.summary(),recoveries=records,phases=phases,counters=solver.counters(phases))


def check(case,fixture,actual):
    marked_only(fixture);r=case['modulus'];w=case['width'];rows,rhs=solver.joint_rows(case)
    rank=check_source.system(actual['system'],rows,rhs,r);N=kernel(rows,w+8,r)
    if len(N)+rank!=w+8 or check_source.rank(N,r)!=len(N):raise ValueError('independent native kernel dimension')
    # Independent query enumeration; never choose functions from this kernel.
    queries=[[int(i==j)for j in range(8)]for i in range(8)]
    queries.extend([int(k==i)-int(k==j)for k in range(8)]for i in range(8)for j in range(i+1,8))
    queries=[[a%r for a in v]for v in queries]
    if (actual['target_unknowns'],actual['functional_queries'],actual['actual_batch_calls'])!=(8,36,1)or len(actual['recoveries'])!=36:raise ValueError('functional/unknown/call census')
    syndromes=[]
    for i,(rec,v)in enumerate(zip(actual['recoveries'],queries,strict=True)):
        query=[0]*w+v;syndrome=[sum(a*b for a,b in zip(query,n,strict=True))%r for n in N];syndromes.append(syndrome)
        if rec['query_index']!=i or rec['coefficients']!=v or rec['identifiable']is not(not any(syndrome)):raise ValueError('prespecified functional/kernel criterion')
        check_solver.member(rec,query,rows,rhs,actual['system'],r)
        p=fixture['p'];point=None
        for a,target in zip(v,case['targets'],strict=True):
            if not a:continue
            q=tuple(target['point']);q=q if a==1 else(q[0],-q[1]%p)
            point=check_source.old.add(p,0,fixture['a'],point,q)
        if rec['public_point']!=point and rec['public_point']!=(None if point is None else list(point)):raise ValueError('functional public construction')
        if rec['identifiable']:
            if check_solver.combine(rec['original_row_weights'],rows,rhs,w+8,r)!=(query,rec['scalar']):raise ValueError('functional native weights')
            if check_source.old.multiply(p,0,fixture['a'],rec['scalar'],tuple(fixture['P']))!=point:raise ValueError('functional public certificate')
        elif rec['original_row_weights']is not None:raise ValueError('unresolved functional weights')
    known_checks.phase_counts(actual)
    return dict(checked=True,kernel=N,functional_syndromes=syndromes,producer_output_sha256=commitment(actual),
        unit_identified=sum(v['identifiable']for v in actual['recoveries'][:8]),difference_identified=sum(v['identifiable']for v in actual['recoveries'][8:]))
