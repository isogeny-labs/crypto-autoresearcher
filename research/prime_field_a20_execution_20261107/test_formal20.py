"""Marked tiny controls for formal definitions; no native pilot."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from deps20 import core,solver,check_source,public_base,check_base,collection19,check_collection19,branch19,pool19,cancel19,information19,check_algebra19
import formal_pool20,preparation20,native_case20,check_formal20


def rules():
    return dict(software_control=True,domain='a20-formal-software/v1',fields=[dict(p=211,base_size=5)],a=1,curves_per_field=1,
        maximum_curve_candidates=128,sources=8,prerequisite=2,excluded_curves=[],seeds=[0],maximum_scalar_candidates=256,
        maximum_target_candidates=256,maximum_base_candidates=256,max_pair_entries=8192,max_retained_rows=4096,targets=2,
        target_policies=['general'],target_queries_per_point=2,target_prefixes=[2],max_affine_labels=8192,pool_size=2,
        formal_pool_size=2,maximum_pool_candidates=256,maximum_target_cache_points=4,public_base_sizes=[16])


@pytest.fixture(scope='module')
def tiny():
    rr=rules();original=core.generate(rr,lambda v:None)['cells'][0]
    pool=formal_pool20.build(original,rr,lambda v:None)
    assert formal_pool20.check(original,rr,pool)['checked']
    return original,pool


def test_formal_recipe_native_signs_and_no_numeric_labels(tiny):
    original,pool=tiny;rr=rules();proof=formal_pool20.check(original,rr,pool)
    assert proof['definition_only_old_base_delta']==0 and pool['scalar_labels_generated']is False
    assert not pool['rejected_collision_equations_used']
    assert len(pool['points'])==len(pool['definitions'])==2
    assert 'knowledge'not in pool and 'signed_labels'not in pool
    for mutation in ('coefficient','point','rejected','duplicate'):
        bad=deepcopy(pool)
        if mutation=='coefficient':bad['definitions'][0]['old_coefficients'][0]+=1
        elif mutation=='point':bad['points'][0][1]+=1
        elif mutation=='rejected':bad['rejected_collision_equations_used']=True
        else:bad['points'][1]=bad['points'][0]
        with pytest.raises(ValueError):formal_pool20.check(original,rr,bad)


def test_all_four_tiny_cold_programs_native_and_expanded(tiny):
    original,formal=tiny;rr0=rules();targets=core.old.targets(original,rr0,solver.Meter(original['fixture']),lambda v:None);reference=None
    for program in ('norm32','unknown16','formalpair16','known16'):
        rr=dict(rr0,program_id=program);helper=pool=None
        if program=='unknown16':pool=pool19.build(original,rr,lambda v:None)
        if program=='formalpair16':pool=deepcopy(formal)
        if program=='known16':helper=public_base.build(original,rr,16,lambda v:None)
        p=preparation20.prepare(original,rr,helper,lambda v:None,pool=pool)
        assert preparation20.check(original,rr,helper,p,pool)['checked']
        c=collection19.collect(p,targets,rr,lambda v:None);assert check_collection19.collection(p,rr,c)[0]['checked']
        recipe=core.recipes(original,c,rr,solver.Meter(original['fixture']),lambda v:None)
        cache=branch19.OwnedCache(c,rr,lambda v:None);branch=branch19.build(p,c,rr,recipe['policies']['general'],cache,lambda v:None)
        assert branch19.check(p,c,rr,recipe['policies']['general'],cache,branch)['checked']
        case=native_case20.build(p,c,branch,cache,2,'anchors',solver.Meter(p['cell']['fixture']))
        assert json.dumps(case,sort_keys=True)==json.dumps(native_case20.expected(p,c,branch,cache,2,'anchors'),sort_keys=True)
        if reference is None:
            projected=check_algebra19.projected(case,p);reference=[(v['vector'],v['rhs'])for v in projected['rows']if v['kind']=='collected_source']
        info=information19.measure(reference,case,p,solver.Meter(p['cell']['fixture']))
        assert check_algebra19.information(reference,case,p,info)['checked']
        out=cancel19.solve(case,p,solver.Meter(p['cell']['fixture']));assert check_algebra19.cancelled_target(case,p,out,p['cell']['fixture'])['checked']
        joint=solver.solve(case,'sparse_joint',solver.Meter(p['cell']['fixture']))
        assert [(v['identifiable'],v['scalar'])for v in out['recoveries']]==[(v['identifiable'],v['scalar'])for v in joint['recoveries']]
        expanded=check_formal20.check(case,p,out,info)
        assert expanded['applicable']is(program=='formalpair16')
        if program=='formalpair16':
            assert expanded['definition_only_old_base_delta']==0
            assert expanded['native_joint_rank']==expanded['expanded_joint_rank']+2
            assert sum(v['kind']=='formal_definition'for v in case['source_origins'])==2
            assert p['initial']==collection19.prepare(original,rr,None,lambda v:None,pool=pool)['initial']


def test_definition_only_zero_but_legitimate_public_K_can_gain():
    # Explicit algebra fixture, independent of any newly generated curve.
    f=dict(p=211,a=1,b=1,r=101,P=[0,1],factor_base=[])
    p=dict(norm_size=2,known=[],basis=[[0,1],[1,1],[2,1]],projection=dict(U=2,native_to_projected=[['unknown',0,1],['unknown',1,1]]))
    case=dict(width=3,target_count=0,modulus=101,source=[([100,100,1],0)],source_origins=[dict(kind='formal_definition')],target=[],targets=[])
    pure=information19.measure([],case,p,solver.Meter(f))
    assert pure['views']['full']['total']['delta']==0
    assert check_algebra19.information([],case,p,pure)['checked']
    case['source'].append(([0,0,1],7));case['source_origins'].append(dict(kind='constructed_source_anchor'))
    actual=information19.measure([],case,p,solver.Meter(f))
    assert actual['views']['full']['supplied']['delta']==1
    assert actual['views']['full']['collected_after_own_K']==0
    assert check_algebra19.information([],case,p,actual)['checked']


def test_expansion_keeps_six_old_occurrences_and_cancellations(tiny):
    original,_=tiny;f=deepcopy(original['fixture']);r=f['r'];P=tuple(f['P']);pfield=f['p'];a=f['a']
    points=[check_source.old.multiply(pfield,0,a,k,P)for k in (1,3,7,4,8,10)]
    definitions=[];orientations=[]
    for i,(components,vector)in enumerate((([[0,1],[1,1]],[1,1,0]),([[0,1],[2,1]],[1,0,1]),([[1,1],[2,1]],[0,1,1]))):
        q=points[3+i];canonical=min(q,(q[0],-q[1]%pfield));sign=1 if canonical==q else -1
        points[3+i]=canonical;orientations.append(sign)
        definitions.append(dict(auxiliary_index=i,components=[[j,s*sign]for j,s in components],old_coefficients=[v*sign%r for v in vector],point=list(canonical)))
    f['factor_base']=[dict(point=list(q))for q in points]
    p=dict(cell=dict(fixture=f),norm_size=3,known=[],basis=[[j,1]for j in range(6)],projection=dict(U=3,native_to_projected=[['unknown',j,1]for j in range(3)]),formal_definitions=definitions,auxiliary_role='formalpair16')
    source,origins=native_case20.definition_rows(p)
    Q=check_source.old.multiply(pfield,0,a,22,P)
    case=dict(width=6,target_count=1,modulus=r,source=source,source_origins=origins,target=[dict(vector=[0,0,0]+[v%r for v in orientations],outside=[r-1],rhs=0,kind='decomposition')],targets=[dict(index=0,point=list(Q))])
    rows,_=check_formal20.expand(case,p);assert rows[-1]==[2,2,2,r-1]
    out=cancel19.solve(case,p,solver.Meter(f));info=information19.measure([],case,p,solver.Meter(f))
    assert check_formal20.check(case,p,out,info)['checked']
    bad=deepcopy(case);bad['target'][0]['vector']=[1,0,0,orientations[0]%r,-orientations[1]%r,0]
    assert check_formal20.expand(bad,p)[0][-1][:3]==[1,1,r-1]
    corrupt=deepcopy(p);corrupt['formal_definitions'][0]['old_coefficients'][0]=0
    with pytest.raises(ValueError):check_formal20.expand(case,corrupt)
    corrupt=deepcopy(p);corrupt['cell']['fixture']['factor_base'][3]['point'][1]+=1
    with pytest.raises(ValueError,match='public native point definition'):check_formal20.check(case,corrupt,out,info)


def test_native_formal_pool_refuses_before_candidates():
    events=[]
    with pytest.raises(ValueError,match='admission'):formal_pool20.build(dict(fixture=dict(p=262139)),dict(fields=[dict(p=262139)]),events.append)
    assert not events


def test_scripted_hash_alias_rejections_never_become_definitions(tiny,monkeypatch):
    # Explicitly mocked hash candidate order, solely for rejection/knowledge
    # plumbing. The separate unmocked tiny recipe control checks real SHA256.
    original,_=tiny;original=deepcopy(original);f=original['fixture'];P=tuple(f['P'])
    f['factor_base']=[dict(point=list(check_source.old.multiply(f['p'],0,f['a'],k,P)))for k in (1,2,3)]
    f['uid']='marked-a20-scripted-three-atom-alias-fixture'
    rr=rules();rr['fields']=[dict(p=211,base_size=3)];rr['program_id']='formalpair16'
    class Digest:
        def __init__(self,value):self.value=value
        def hexdigest(self):return format(self.value,'064x')
    def scripted(message):
        index,counter=map(int,message.decode().split('|')[-2:])
        return Digest({(0,0):0,(0,1):4,(1,0):4,(1,1):3}[index,counter])
    monkeypatch.setattr(formal_pool20,'sha256',scripted)
    pool=formal_pool20.build(original,rr,lambda v:None)
    assert [v['reason']for v in pool['search_trace']]==['old_or_previous_sign_class','selected','old_or_previous_sign_class','selected']
    assert all(v['rejected_equation_used']is False for v in pool['search_trace'])
    p=preparation20.prepare(original,rr,None,lambda v:None,pool=pool)
    assert len(p['formal_definitions'])==2 and len(native_case20.definition_rows(p)[0])==2
    assert {v['scalar']for v in p['initial']}=={1,2,f['r']-1,f['r']-2}
    assert 'knowledge'not in pool and not pool['rejected_collision_equations_used']


def test_prospective_grid_and_budget_metadata_only():
    import custody20,prepare20
    from datetime import datetime,timezone
    r=custody20.load(custody20.INPUTS);custody20.validate_rules(r)
    assert len(list(custody20.descriptors(r)))==16 and len(list(custody20.executions(r)))==32
    assert len(r['excluded_curves'])==44 and r['query_suppression']is False and r['formal_pool_size']==16
    assert len(custody20.SOURCES)==194 and len(custody20.BUDGET_INPUTS)==19
    for bad in (dict(r,formal_pool_size=True),dict(r,rejected_collision_equations_used=True),dict(r,maximum_target_cache_points=65)):
        with pytest.raises(ValueError):custody20.validate_rules(bad)
    p=prepare20.make_protocol('0'*40);t=custody20.tools()
    assert not t.schema_errors(p,'experiment.protocol/v1')and not t.lint_protocol(p,custody20.HERE)
    assert len(p['arms'])==8 and len(p['randomization']['seed_derivation']['seeds'])==32
    budget=prepare20.remaining_budget(datetime.now(timezone.utc))
    assert budget['absolute_deadline']=='2026-11-07T07:46:38.570520+00:00'
    assert abs(budget['known_prior_cpu_seconds']-1123.977703)<1e-6
