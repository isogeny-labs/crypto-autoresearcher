"""Marked p211/three-atom construction controls; not a native48 pilot."""
from copy import deepcopy
from collections import Counter
import pytest
from deps17 import core,Meter,check_source,checker,collection16,branch16,checks16
import geometry
from ownership16 import OwnedTargetCache as LegacyCache
from ownership17 import OwnedCache
import preconstruct17,check_construct17


def rules():
    return dict(software_control=True,domain='a17-preconstruction-software/v1',fields=[dict(p=211,base_size=5)],a=1,
        curves_per_field=1,maximum_curve_candidates=128,sources=8,prerequisite=4,excluded_curves=[],seeds=[0],
        maximum_scalar_candidates=256,maximum_target_candidates=256,max_pair_entries=8192,max_retained_rows=4096,
        targets=2,target_policies=['general'],target_queries_per_point=24,target_prefixes=[24],
        max_affine_labels=8192,norm_scopes=['relations','anchors'],known_scope='supplied',
        program_id='known48_24',base_kind='known48',maximum_target_cache_points=48)


@pytest.fixture(scope='module')
def toy():
    r=rules();original=core.generate(r,lambda v:None)['cells'][0];f=deepcopy(original['fixture']);labels=[1,2,3]
    f['factor_base']=[dict(point=list(check_source.old.multiply(f['p'],0,f['a'],k,tuple(f['P'])))) for k in labels]
    f['uid']='marked-p211-a17-three-known-atoms'
    targets=core.old.targets(original,r,Meter(original['fixture']),lambda v:None)
    return original,f,labels,targets


def fresh(toy,arm):
    original,f,labels,targets=toy;r=rules();m=Meter(f)
    initial=collection16.signed_owned(f,[dict(scalar=k,point=v['point'],origin='marked_tiny_paid_fixture') for k,v in zip(labels,f['factor_base'],strict=True)],m)
    geom=geometry.build(f,0,dict(enumerate(labels)),m)
    prep=collection16.Prepared(program_id='known48_24',target_horizon=24,cell=dict(id=original['id'],fixture=deepcopy(f)),
        norm_size=0,projection=None,known=list(enumerate(labels)),basis=[],prerequisites=[],initial=initial,supplied=[],geometry=geom,
        selection=dict(orders={},ap={},trace=[]),phases=[],counters={},complete=True,arm_owner=arm)
    col=collection16.collect_known(prep,targets,r,lambda v:None);col['arm_owner']=arm
    assert checks16.collection(prep,r,col)[0]['checked']
    recipe=core.recipes(original,col,r,Meter(f),lambda v:None)
    assert checker.recipes(original,r,recipe)
    return prep,col,recipe['policies']['general'],r


def test_all24_points_and_registry_paid_before_any_extra_query(toy,monkeypatch):
    prep,col,recipe,r=fresh(toy,'suppress');events=[]
    before=len(col.query_index.engines.records)
    def no_query(*a,**k):raise AssertionError('preconstruction attempted an endpoint query')
    monkeypatch.setattr(col.query_index,'query',no_query)
    result=preconstruct17.build(prep['cell'],col,r,recipe,events.append,'suppress')
    assert len(result['endpoints'])==48 and 'requests'not in result
    assert len(col.query_index.engines.records)==before
    proof=check_construct17.check(prep['cell'],col,r,recipe,result,'suppress')
    assert proof['checked'] and proof['native_query_calls_by_adapter']==0
    assert len([v for v in events if v['kind']=='horizon_constructor_selection'])==3
    assert events[-1]['kind']=='full_preconstruction_complete'


def test_preconstruction_equals_existing_full24_workload_and_costs(toy):
    prep,col,recipe,r=fresh(toy,'full');result=preconstruct17.build(prep['cell'],col,r,recipe,lambda v:None,'full')
    oldprep,oldcol,oldrecipe,oldrules=fresh(toy,'full')
    cache=LegacyCache(oldcol.query_index,oldcol['natural_records'],oldrules,lambda v:None)
    old=branch16.build(oldprep['cell'],oldcol,oldrules,oldrecipe,'known',0,'general',cache,lambda v:None)
    assert checks16.branch(oldprep['cell'],oldcol,oldrules,oldrecipe,old,cache,checker.GroupOracle(oldprep['cell']['fixture'],oldcol['target_generation']['targets']))['checked']
    assert result['endpoints']==[{k:v for k,v in item.items() if k!='query_id'} for item in old['requests']]
    for key in ('recipe','scalar_events','selections','labels','equations'):assert result[key]==old[key]
    a,b=Counter(result['counters']),Counter(old['counters']);assert a.pop('fully_preconstructed_endpoint_slots')==48;assert b.pop('branch_query_reference_lookups')==48
    assert a==b


def test_other_arm_cache_and_mutated_rules_are_rejected(toy):
    prep,col,recipe,r=fresh(toy,'full');cache=OwnedCache(prep['cell'],col,r,recipe,'full',lambda v:None)
    with pytest.raises(ValueError,match='borrowed'):cache.request(tuple(col['target_generation']['targets'][0]['point']),dict(arm_owner='suppress'))
    with pytest.raises(ValueError,match='own prelude'):preconstruct17.build(prep['cell'],col,r,recipe,lambda v:None,'suppress')
    r['maximum_target_cache_points']=49
    with pytest.raises(ValueError,match='cache cap'):cache.request(tuple(col['target_generation']['targets'][0]['point']),dict(arm_owner='full'))


def test_missing_full_workload_and_scalar_count_tampering_rejected(toy):
    prep,col,recipe,r=fresh(toy,'full');result=preconstruct17.build(prep['cell'],col,r,recipe,lambda v:None,'full')
    bad=deepcopy(result);bad['endpoints'].pop()
    with pytest.raises(ValueError):check_construct17.check(prep['cell'],col,r,recipe,bad,'full')
    bad=deepcopy(result);bad['selections']['P']['window']=(bad['selections']['P']['window']+1)%9
    with pytest.raises(ValueError,match='policy'):check_construct17.check(prep['cell'],col,r,recipe,bad,'full')
    bad=deepcopy(result);bad['counters']['scalar_uncached_ec_adds']+=1
    with pytest.raises(ValueError,match='prediction'):check_construct17.check(prep['cell'],col,r,recipe,bad,'full')


def test_failed_constructor_keeps_selection_and_paid_phase_prefix(toy,monkeypatch):
    prep,col,recipe,r=fresh(toy,'suppress');events=[]
    def fail(*args,**kwargs):raise RuntimeError('marked software failure after paid selection')
    monkeypatch.setattr(preconstruct17,'Constructor',fail)
    with pytest.raises(RuntimeError,match='paid selection'):preconstruct17.build(prep['cell'],col,r,recipe,events.append,'suppress')
    failed=events[-1]
    assert failed['kind']=='full_preconstruction_failed' and len(failed['paid_prefix']['selections'])==1
    phases=[v['phase'] for v in events if v['kind']=='affine_phase']
    assert phases[-1]['status']=='failed' and phases[-1]['counters']['constructor_policy_candidates']==9
