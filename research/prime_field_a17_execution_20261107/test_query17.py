"""Marked p211 actual-query controls, with explicit three-atom fixtures only."""
from copy import deepcopy
from itertools import product
from collections import Counter
import pytest
from deps17 import core,Meter,checker,check_source,solver,partial_solver,check_partial,known_checks,public_verify,collection16,checks16
import geometry
from ownership17 import OwnedCache
import preconstruct17,query17,check_construct17,check_online17
from test_preconstruct17 import toy,fresh,rules


def completed(prep,col,recipe,r,arm):
    events=[];cloud=preconstruct17.build(prep['cell'],col,r,recipe,events.append,arm)
    assert check_construct17.check(prep['cell'],col,r,recipe,cloud,arm)['checked']
    cache=OwnedCache(prep['cell'],col,r,recipe,arm,events.append)
    result=query17.execute(prep,col,cloud,cache,r,arm,events.append)
    return result,cloud,cache,events


def joint(result,fixture):
    m=Meter(fixture);value=solver.solve(result['case'],'sparse_joint',m);public_verify(value,result['case'],fixture,m)
    assert known_checks.joint_case(result['case'],value,fixture)['checked']
    return [(v['identifiable'],v['scalar']) for v in value['recoveries']]


def test_real_query_schedule_and_both_pool_joint_controls(toy):
    results={}
    for arm in ('suppress','full'):
        prep,col,recipe,r=fresh(toy,arm);result,cloud,cache,events=completed(prep,col,recipe,r,arm)
        assert len(result['schedule'])==48 and len([v for v in result['schedule'] if v.get('origin')=='mandatory_natural'])==2
        assert result['scheduling_counters']['extra_slots_considered']==46
        assert joint(result,prep['cell']['fixture'])
        if arm=='suppress':
            expected=[(v['identifiable'],v['scalar']) for v in result['online']['recoveries']]
            assert joint(result,prep['cell']['fixture'])==expected
            for cert in result['online']['certificates']:assert check_online17.prefix(result['case'],cert,prep['cell']['fixture'],cloud['owner'])['checked']
        else:
            assert all(v['kind']=='slot_queried' for v in result['schedule'])
            m=Meter(prep['cell']['fixture']);value=partial_solver.solve(result['case'],prep['known'],[],m);public_verify(value,result['case'],prep['cell']['fixture'],m)
            assert check_partial.check(result['case'],prep['known'],[],value,prep['cell']['fixture'])['checked']
        results[arm]=joint(result,prep['cell']['fixture'])
    assert results['suppress']==results['full']


def special_fixture(toy,arm):
    """Choose a test-only scalar fixture that needs a real post-setup query.

    This marked software-control oracle is over r=233, never native data. The
    producer receives only Q, supplied base labels, and a fixed nonrandom beta
    recipe. Selection is solely to exercise the query/update/skip boundary.
    """
    original,f,_,_=toy;f=deepcopy(f);r=rules();r.update(targets=1,maximum_target_cache_points=24)
    modulus=f['r'];assert modulus==233
    labels=[17,62,109]
    mul=lambda k:list(check_source.old.multiply(f['p'],0,f['a'],k,tuple(f['P'])))
    f['factor_base']=[dict(point=mul(k)) for k in labels];f['uid']='marked-p211-three-atom-forced-real-query'
    _,window=checker.expected_selection(modulus,{0,1,modulus-1},list(range(2,25)))
    integer=checker.IntegerConstructor(modulus,{0,1,modulus-1},window)
    for beta in range(2,25):integer.mul(beta)
    beta_labels=integer.known|{-v%modulus for v in integer.known}
    public={v%modulus for k in [1,*labels] for v in (k,-k)}
    smooth={sum(a*b for a,b in zip(signs,labels,strict=True))%modulus for signs in product((-1,1),repeat=3)}
    secret=next(q for q in range(1,modulus) if q not in smooth and
        not(public&{b*q%modulus for b in beta_labels if b}) and
        sum(beta*q%modulus in smooth for beta in range(2,25))>=2)
    targets=dict(targets=[dict(index=0,point=mul(secret))],search_trace=[dict(kind='marked_software_positive_fixture',native=False)])
    meter=Meter(f);initial=collection16.signed_owned(f,[dict(scalar=k,point=mul(k),origin='marked_software_paid_label') for k in [1,*labels]],meter)
    geom=geometry.build(f,0,dict(enumerate(labels)),meter)
    prep=collection16.Prepared(program_id='known48_24',target_horizon=24,cell=dict(id=original['id'],fixture=f),norm_size=0,projection=None,
        known=list(enumerate(labels)),basis=[],prerequisites=[],initial=initial,supplied=[],geometry=geom,
        selection=dict(orders={},ap={},trace=[]),phases=[],counters={},complete=True,arm_owner=arm)
    col=collection16.collect_known(prep,targets,r,lambda v:None);col['arm_owner']=arm
    assert checks16.collection(prep,r,col)[0]['checked']
    recipe=[[dict(alpha=0,beta=j+1) for j in range(24)]]
    return prep,col,recipe,r,secret


def test_real_query_produces_certificate_before_later_slots_skip(toy):
    outcomes={};query_counts={};construction={}
    for arm in ('suppress','full'):
        prep,col,recipe,r,secret=special_fixture(toy,arm)
        result,cloud,cache,events=completed(prep,col,recipe,r,arm)
        assert joint(result,prep['cell']['fixture'])==[(True,secret)]
        query_counts[arm]=len(cache.records);construction[arm]=cloud
        if arm=='suppress':
            events_by_kind=[v['kind'] for v in events]
            assert events_by_kind.index('full_preconstruction_complete')<events_by_kind.index('online_start')
            certified=next(v for v in events if v['kind']=='online_target_certified')
            assert isinstance(certified['certificate']['origin'],dict) and 'extra_slot'in certified['certificate']['origin']
            assert any(v['kind']=='slot_queried' and v.get('origin')=='extra' for v in result['schedule'])
            skipped=[v for v in result['schedule'] if v['kind']=='slot_skipped'];assert skipped
            assert all(v['certificate_id']==certified['certificate_id'] for v in skipped)
            assert events_by_kind.index('online_target_certified')<events_by_kind.index('slot_skipped')
        outcomes[arm]=joint(result,prep['cell']['fixture'])
    assert outcomes['suppress']==outcomes['full'] and query_counts['suppress']<query_counts['full']
    for key in ('endpoints','selections','labels','equations','counters'):
        assert construction['suppress'][key]==construction['full'][key]


def test_failed_query_retains_schedule_and_paid_construction(toy,monkeypatch):
    prep,col,recipe,r,_=special_fixture(toy,'suppress');events=[]
    cloud=preconstruct17.build(prep['cell'],col,r,recipe,events.append,'suppress');cache=OwnedCache(prep['cell'],col,r,recipe,'suppress',events.append)
    def fail(*args,**kwargs):raise RuntimeError('marked software query failure after full setup')
    monkeypatch.setattr(col.query_index,'query',fail)
    with pytest.raises(RuntimeError,match='query failure'):query17.execute(prep,col,cloud,cache,r,'suppress',events.append)
    assert events[-1]['kind']=='query_program_failed' and events[-1]['partial_work_unknown']
    assert events[-1]['case_prefix'] and any(p['status']=='failed' for p in events[-1]['cache_phases'])
    assert events[-1]['schedule_prefix'] and cloud['complete']
