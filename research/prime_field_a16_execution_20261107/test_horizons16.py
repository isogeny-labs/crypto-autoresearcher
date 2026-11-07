"""Marked p211 software controls, with an explicit small three-atom fixture.

The horizon24 positive matrix control uses three known atoms rather than48.
The prior A14 dense known48 control records the unchanged4096row refusal;
this file does not claim a complete native-width48/horizon24 toy replay.
No retained native A14/A15 points or new native curves are evaluated here.
"""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from deps16 import core,Meter,check_source,solver,checker,partial_solver,check_partial,native_case
import geometry
import collection16,branch16,checks16
from ownership16 import OwnedTargetCache
from programs16 import rules_for,descriptors,recipe_prefix
from driver14 import public_verify


def rules():
    return dict(software_control=True,domain='a16-horizon-software/v1',fields=[dict(p=211,base_size=5)],
        a=1,curves_per_field=1,maximum_curve_candidates=128,sources=16,prerequisite=4,excluded_curves=[],
        seeds=[0],maximum_scalar_candidates=256,maximum_target_candidates=256,max_pair_entries=8192,
        max_retained_rows=4096,targets=2,target_policies=['walk','hash_offset','general'],
        short_target_prefixes=[1,2,4,8],target_queries_per_point=8,target_prefixes=[1,2,4,8],
        max_affine_labels=8192,norm_scopes=['relations','anchors'],known_scope='supplied')


@pytest.fixture(scope='module')
def control():
    r=rules();original=core.generate(r,lambda v:None)['cells'][0];f=deepcopy(original['fixture'])
    labels=[1,2,3];f['factor_base']=[dict(point=list(check_source.old.multiply(f['p'],0,f['a'],k,tuple(f['P'])))) for k in labels]
    f['uid']='marked-p211-three-known-atom-horizon-control'
    m=Meter(f);initial=collection16.signed_owned(f,[dict(scalar=k,point=v['point'],origin='marked_tiny_known_fixture') for k,v in zip(labels,f['factor_base'],strict=True)],m)
    geom=geometry.build(f,0,dict(enumerate(labels)),m)
    targets=core.old.targets(original,r,Meter(original['fixture']),lambda v:None)
    prepared={};collected={};recipes={};caches={}
    for name in ('known48_8','known48_24'):
        rr=rules_for(r,name)
        p=collection16.Prepared(program_id=name,target_horizon=rr['target_queries_per_point'],cell=dict(id=original['id'],fixture=deepcopy(f)),
            norm_size=0,projection=None,known=list(enumerate(labels)),basis=[],prerequisites=[],initial=deepcopy(initial),supplied=[],geometry=deepcopy(geom),
            selection=dict(orders={},ap={},trace=[]),phases=[],counters={},complete=True)
        c=collection16.collect_known(p,targets,rr,lambda v:None)
        assert checks16.collection(p,rr,c)[0]['checked']
        recipes[name]=core.recipes(original,c,rr,Meter(f),lambda v:None)
        checker.recipes(original,rr,recipes[name])
        prepared[name],collected[name]=p,c
    assert recipe_prefix(recipes['known48_8'],recipes['known48_24'],r['targets'],r['target_policies'])
    return original,prepared,collected,recipes


def fresh(control,name,event=lambda v:None):
    _,prepared,collected,recipes=control;r=rules_for(rules(),name);c=collected[name]
    cache=OwnedTargetCache(c.query_index,c['natural_records'],r,event)
    return prepared[name],c,recipes[name],r,cache


@pytest.mark.parametrize('name',['known48_8','known48_24'])
@pytest.mark.parametrize('policy',['walk','hash_offset','general'])
def test_separate_full_horizon_branches_native_lifts(control,name,policy):
    p,c,recipes,r,cache=fresh(control,name);f=p['cell']['fixture'];events=[]
    branch=branch16.build(p['cell'],c,r,recipes['policies'][policy],'known',0,policy,cache,events.append)
    assert checks16.branch(p['cell'],c,r,recipes['policies'][policy],branch,cache,checker.GroupOracle(f,c['target_generation']['targets']))['checked']
    assert branch['horizon_contract']['horizon']==r['target_queries_per_point']
    assert len(branch['requests'])==r['targets']*r['target_queries_per_point']
    for budget in r['target_prefixes']:
        case=native_case.build(p,c,branch,cache,budget,'supplied',Meter(f))
        partial_meter=Meter(f)
        result=partial_solver.solve(case,p['known'],p['basis'],partial_meter)
        public_verify(result,case,f,partial_meter)
        assert check_partial.check(case,p['known'],p['basis'],result,f)['checked']
        joint_meter=Meter(f)
        reference=solver.solve(case,'sparse_joint',joint_meter)
        public_verify(reference,case,f,joint_meter)
        assert [(v['identifiable'],v['scalar']) for v in result['recoveries']]==[(v['identifiable'],v['scalar']) for v in reference['recoveries']]
    selection_events=[v for v in events if v['kind']=='horizon_constructor_selection']
    assert len(selection_events)==(0 if policy=='walk' else 1 if policy=='hash_offset' else 1+r['targets'])
    assert all(len(v['workload'])==(r['targets']*(r['target_queries_per_point']-1) if v['basis']=='P' else r['target_queries_per_point']-1) for v in selection_events)


def test_native_catalogue_and_provenance_without_native_math():
    r=json.loads((Path(__file__).parent/'inputs.json').read_text());plans=list(descriptors(r))
    assert len(plans)==1260
    assert sum(v['base_arm']=='hybrid' for _,v in plans)==576
    assert sum(v['program']=='known48_24' for _,v in plans)==12
    assert {v['target_prefix'] for _,v in plans if v['program']=='known48_24'}=={24}
    assert len(r['excluded_curves'])==28
    assert rules_for(r,'known48_8')['maximum_target_cache_points']==176
    assert rules_for(r,'known48_24')['maximum_target_cache_points']==560


def test_horizon8_refuses_long_cache_or_recipe_before_work(control):
    p,c,short,r,cache=fresh(control,'known48_8');_,_,long,longr,longcache=fresh(control,'known48_24')
    for recipe,used in [(short['policies']['general'],longcache),(long['policies']['general'],cache)]:
        events=[]
        with pytest.raises(ValueError,match='horizon'):branch16.build(p['cell'],c,r,recipe,'known',0,'general',used,events.append)
        assert events==[]
    cache.rules['target_queries_per_point']=24
    with pytest.raises(ValueError):cache.request(None,{})


def test_independent_checker_rejects_retagged_full_horizon_branch(control):
    p,c,recipe,r,cache=fresh(control,'known48_24');f=p['cell']['fixture']
    branch=branch16.build(p['cell'],c,r,recipe['policies']['general'],'known',0,'general',cache,lambda v:None)
    for field,value in [('horizon',8),('program','known48_8'),('maximum_cache_points',44),('recipe_sha256','0'*64)]:
        b=deepcopy(branch);b['horizon_contract'][field]=value
        with pytest.raises(ValueError):checks16.branch(p['cell'],c,r,recipe['policies']['general'],b,cache,checker.GroupOracle(f,c['target_generation']['targets']))


def test_failed_long_constructor_retains_paid_selection_and_phases(control,monkeypatch):
    p,c,recipe,r,cache=fresh(control,'known48_24');events=[];original=cache.request;calls=0
    def fail(Q,context):
        nonlocal calls
        calls+=1
        if calls==4:raise RuntimeError('injected paid horizon prefix')
        return original(Q,context)
    monkeypatch.setattr(cache,'request',fail)
    with pytest.raises(RuntimeError,match='paid horizon'):branch16.build(p['cell'],c,r,recipe['policies']['general'],'known',0,'general',cache,events.append)
    failure=events[-1]
    assert failure['kind']=='horizon_branch_failed' and failure['partial_work_unknown']
    assert len(failure['paid_prefix']['selections'])==1+r['targets']
    assert failure['paid_prefix']['scalar_point_events']>0
    assert any(v.get('kind')=='affine_phase' and v['phase']['status']=='failed' for v in events)
