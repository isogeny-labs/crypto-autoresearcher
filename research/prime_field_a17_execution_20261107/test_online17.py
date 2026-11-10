"""Marked p211 software controls; no native curves or admissions are executed."""
from copy import deepcopy
import pytest
from deps17 import core,Meter,check_source,solver,known_checks,public_verify,commitment
from online17 import Online
import check_online17


@pytest.fixture(scope='module')
def toy():
    rules=dict(software_control=True,domain='a17-online-software/v1',fields=[dict(p=211,base_size=3)],a=1,
        curves_per_field=1,maximum_curve_candidates=128,maximum_base_candidates=256,excluded_curves=[],
        maximum_target_candidates=256,maximum_scalar_candidates=256,prerequisite=4,sources=8,seeds=[0],targets=2)
    original=core.generate(rules,lambda v:None)['cells'][0];f=deepcopy(original['fixture']);labels=[1,2,3]
    mul=lambda k:list(check_source.old.multiply(f['p'],0,f['a'],k,tuple(f['P'])))
    f['factor_base']=[dict(point=mul(k)) for k in labels];f['uid']='marked-p211-a17-online-control'
    # Secret values are test-only oracle inputs for a positive software fixture.
    # They are never passed to the Online producer, whose only target input is Q.
    target_values=[7,11]
    case=dict(width=3,target_count=2,modulus=f['r'],source=[([int(i==j) for i in range(3)],k) for j,k in enumerate(labels)],
        target=[],targets=[dict(index=j,point=mul(k)) for j,k in enumerate(target_values)])
    return rules,f,labels,case


def start(toy,events=None,**kwargs):
    rules,f,labels,case=toy;events=[] if events is None else events
    return Online(deepcopy(case),labels,f,rules,events.append,'software-only-owner',**kwargs),events


def row(vector,outside,rhs):return dict(vector=vector,outside=outside,rhs=rhs,kind='marked_software_equation')


def test_cross_target_membership_and_public_native_lifts(toy):
    online,events=start(toy)
    online.append(row([1,0,0],[1,1],19));online.scan('joint-only')
    assert not online.can_skip(0) and not online.can_skip(1)
    online.append(row([0,1,0],[0,1],13));new=online.scan('second-independent-row')
    assert len(new)==2 and online.can_skip(0) and online.can_skip(1)
    result=online.snapshot();assert [v['scalar'] for v in result['recoveries']]==[7,11]
    for certificate in result['certificates']:assert check_online17.prefix(online.case,certificate,toy[1],online.owner)['checked']
    m=Meter(toy[1]);reference=solver.solve(online.case,'sparse_joint',m);public_verify(reference,online.case,toy[1],m)
    assert known_checks.joint_case(online.case,reference,toy[1])['checked']
    assert [v['scalar'] for v in reference['recoveries']]==[7,11]
    assert result['counters']['public_target_certificates_verified']==2
    assert len([e for e in events if e['kind']=='online_target_certified'])==2


def test_old_positive_proof_padding_and_current_negative_residual(toy):
    online,_=start(toy);online.append(row([0,0,1],[1,0],10));online.scan('first')
    assert online.can_skip(0) and not online.can_skip(1)
    first=deepcopy(online.certificates[0]);online.append(row([1,0,0],[0,0],1))
    with pytest.raises(ValueError,match='current successful scan'):online.can_skip(0)
    online.scan('redundant-row');result=online.snapshot()
    assert result['recoveries'][0]['original_row_weights'][-1]==0 and not result['recoveries'][1]['identifiable']
    assert first==online.certificates[0]
    assert check_online17.prefix(online.case,first,toy[1],online.owner)['checked']


def test_public_failure_cannot_authorize_a_skip_and_preserves_paid_prefix(toy):
    online,events=start(toy);online.append(row([0,0,0],[1,0],8))
    with pytest.raises(ValueError,match='public target'):online.scan('wrong-scalar')
    assert 0 not in online.certificates and online.failed
    assert events[-1]['kind']=='online_failed' and events[-1]['native_rows_retained']==1
    assert any(p['status']=='failed' for p in events[-1]['phases'])
    assert events[-1]['counters'].get('Fr.field_sub',0)>0
    with pytest.raises(ValueError):online.can_skip(0)
    with pytest.raises(ValueError):online.snapshot()


def test_future_or_other_owner_or_altered_proof_is_rejected(toy):
    online,_=start(toy);early=deepcopy(online.case)
    online.append(row([1,0,0],[1,0],8));online.scan('positive');certificate=deepcopy(online.certificates[0])
    with pytest.raises(ValueError,match='future'):check_online17.prefix(early,certificate,toy[1],online.owner)
    with pytest.raises(ValueError,match='owner'):check_online17.prefix(online.case,certificate,toy[1],'borrowed-reference-owner')
    certificate['recovery']['scalar']=8
    with pytest.raises(ValueError):check_online17.prefix(online.case,certificate,toy[1],online.owner)


def test_missing_known_unit_or_stale_final_scan_refused(toy):
    rules,f,labels,case=toy;bad=deepcopy(case);bad['source'].pop()
    with pytest.raises(ValueError):Online(bad,labels,f,rules,lambda v:None,'software-only')
    online,_=start(toy);online.append(row([0,0,0],[0,0],0))
    with pytest.raises(ValueError,match='scan'):online.snapshot()
    assert online.failed


def test_tiny_row_gate_retains_exact_available_prefix(toy):
    online,events=start(toy,max_rows=4);online.append(row([0,0,0],[0,0],0))
    with pytest.raises(ValueError,match='row size'):online.append(row([0,0,0],[0,0],0))
    assert len(online.case['target'])==1 and events[-1]['native_rows_retained']==1
