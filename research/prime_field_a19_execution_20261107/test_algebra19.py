"""Marked p<=211 controls only; algebra fixtures are explicit synthetic rows."""
from copy import deepcopy
import pytest
from deps19 import solver,core,known_checks,public_verify,native_case,public_base,check_base,check_pairs
import cancel19,information19,check_algebra19,pool19,collection19,check_collection19,branch19


def fixture():return dict(p=211,a=1,b=1,r=101,P=[0,1],factor_base=[])


def matrix(source,target,width=3,old=2):
    case=dict(width=width,target_count=1,modulus=101,source=source,target=target,targets=[dict(index=0)])
    case['source_origins']=[dict(kind='collected_source')for v,b in source]
    prepared=dict(known=[],basis=[[j,1]for j in range(width)],norm_size=old,
        projection=dict(U=old,native_to_projected=[['unknown',j,1]for j in range(old)]))
    return case,prepared


def row(v,u,b):return dict(vector=v,outside=u,rhs=b,kind='decomposition')


def test_raw_rank_is_not_old_base_information_and_target_columns_also_cancel():
    M=[([1,0],2)]
    case,p=matrix([([1,0,0],2),([0,1,1],5)],[row([0,0,1],[1],7)])
    got=information19.measure(M,case,p,solver.Meter(fixture()))
    assert got['views']['full']['total']['delta']==0
    assert check_algebra19.information(M,case,p,got)['checked']
    case['source'].append(([0,0,1],3));case['source_origins'].append(dict(kind='constructed_source_anchor'))
    got=information19.measure(M,case,p,solver.Meter(fixture()))
    assert got['views']['full']['total']['delta']==1
    assert got['views']['full']['total']['outside_rank']==2
    assert got['views']['full']['total']['direct_base_gain']==0
    assert got['views']['full']['total']['cross_row_gain']==1
    assert got['views']['full']['supplied']['delta']==0
    checked=check_algebra19.information(M,case,p,got)
    assert checked['views']['full']['total']['old_kernel_syndromes']
    corrupt=deepcopy(got);corrupt['views']['full']['total']['cancellations'][-1]['rhs']+=1
    with pytest.raises(ValueError):check_algebra19.information(M,case,p,corrupt)


def test_cancel_first_recovers_target_while_old_base_deficient():
    case,p=matrix([([1,0,0],2),([0,0,1],7)],[row([0,0,1],[100],0)])
    result=cancel19.solve(case,p,solver.Meter(fixture()))
    assert result['recoveries'][0]['scalar']==7
    checked=check_algebra19.cancelled_target(case,p,result)
    assert checked['native_joint_rank']==3<4
    joint=solver.solve(case,'sparse_joint',solver.Meter(fixture()))
    assert joint['recoveries'][0]['scalar']==7
    broken=deepcopy(result);broken['recoveries'][0]['original_row_weights'][0]=1
    with pytest.raises(ValueError):check_algebra19.cancelled_target(case,p,broken)


def test_known_units_signed_old_basis_lift_and_unrecovered_negative():
    case,p=matrix([([0,1,0],11),([1,0,1],18)],[row([1,1,1],[100],0)],old=2)
    p.update(known=[[1,11]],basis=[[0,-1],[2,1]],projection=dict(U=1,native_to_projected=[['unknown',0,-1],['known',11]]))
    result=cancel19.solve(case,p,solver.Meter(fixture()))
    assert result['recoveries'][0]['scalar']==29
    assert check_algebra19.cancelled_target(case,p,result)['checked']
    case['target'][0]=row([1,1,0],[100],0)
    result=cancel19.solve(case,p,solver.Meter(fixture()))
    assert result['recoveries'][0]['identifiable']is False
    assert result['recoveries'][0]['original_row_weights']is None
    assert check_algebra19.cancelled_target(case,p,result)['checked']


def test_paid_K_is_separate_and_outside_rank_not_outside_count():
    case,p=matrix([([1,0,0],2),([0,1,0],5)],[row([0,0,0],[1],7)])
    case['source_origins'][1]['kind']='constructed_source_anchor'
    got=information19.measure([([1,0],2)],case,p,solver.Meter(fixture()))
    total=got['views']['full']['total'];assert total['outside_rank']==1<got['projection']['outside_width']
    assert total['delta']==got['views']['full']['supplied']['delta']==1
    assert got['views']['full']['collected_after_own_K']==0
    assert check_algebra19.information([([1,0],2)],case,p,got)['checked']


def test_pool_and_complete_tiny_unknown_collector():
    rules=dict(software_control=True,domain='a19-marked-software/v1',fields=[dict(p=211,base_size=3)],
        a=1,curves_per_field=1,maximum_curve_candidates=128,sources=8,prerequisite=2,excluded_curves=[],
        seeds=[0],maximum_scalar_candidates=256,maximum_target_candidates=256,max_pair_entries=8192,
        max_retained_rows=4096,targets=2,target_policies=['general'],target_queries_per_point=2,target_prefixes=[2],
        max_affine_labels=8192,pool_size=2,maximum_pool_candidates=256,program_id='unknown16',maximum_target_cache_points=4)
    original=core.generate(rules,lambda v:None)['cells'][0]
    pool=pool19.build(original,rules,lambda v:None)
    assert pool19.check(original,rules,pool)['checked']
    corrupt=deepcopy(pool);corrupt['search_trace'][0]['sha256']='bad'
    with pytest.raises(ValueError):pool19.check(original,rules,corrupt)
    p=collection19.prepare(original,rules,None,lambda v:None,pool=pool)
    assert check_collection19.preparation(original,rules,None,p,pool)['checked']
    meter=solver.Meter(original['fixture']);targets=core.old.targets(original,rules,meter,lambda v:None)
    c=collection19.collect(p,targets,rules,lambda v:None)
    assert check_collection19.collection(p,rules,c)[0]['checked']
    recipe=core.recipes(original,c,rules,meter,lambda v:None)
    cache=branch19.OwnedCache(c,rules,lambda v:None)
    branch=branch19.build(p,c,rules,recipe['policies']['general'],cache,lambda v:None)
    assert branch19.check(p,c,rules,recipe['policies']['general'],cache,branch)['checked']
    case=native_case.build(p,c,branch,cache,2,'anchors',solver.Meter(p['cell']['fixture']))
    result=cancel19.solve(case,p,solver.Meter(p['cell']['fixture']))
    assert check_algebra19.cancelled_target(case,p,result,p['cell']['fixture'])['checked']
    reference=solver.solve(case,'sparse_joint',solver.Meter(p['cell']['fixture']))
    assert [(v['identifiable'],v['scalar'])for v in result['recoveries']]==[(v['identifiable'],v['scalar'])for v in reference['recoveries']]


def test_native_pool_requires_admission_before_any_candidate():
    seen=[]
    with pytest.raises(ValueError,match='admission'):pool19.build(dict(fixture=dict(p=262139)),dict(fields=[dict(p=262139)]),seen.append)
    assert not seen


def test_three_cold_tiny_programs_preserve_floor_and_charge_helper():
    rules=dict(software_control=True,domain='a19-three-program-software/v1',fields=[dict(p=211,base_size=3)],
        a=1,curves_per_field=1,maximum_curve_candidates=128,sources=8,prerequisite=2,excluded_curves=[],
        seeds=[0],maximum_scalar_candidates=256,maximum_target_candidates=256,maximum_base_candidates=256,max_pair_entries=8192,
        max_retained_rows=4096,targets=2,target_policies=['general'],target_queries_per_point=2,target_prefixes=[2],
        max_affine_labels=8192,pool_size=2,maximum_pool_candidates=256,maximum_target_cache_points=4,public_base_sizes=[16])
    original=core.generate(rules,lambda v:None)['cells'][0];reference=None;basis=None
    targets=core.old.targets(original,rules,solver.Meter(original['fixture']),lambda v:None)
    for program in ('norm32','unknown16','known16'):
        rr=dict(rules,program_id=program);helper=pool=None
        if program=='unknown16':pool=pool19.build(original,rr,lambda v:None)
        if program=='known16':
            helper=public_base.build(original,rr,16,lambda v:None)
            assert check_base.check(original,rr,16,helper)['checked']
            assert helper['counters']
        p=collection19.prepare(original,rr,helper,lambda v:None,pool=pool)
        assert check_collection19.preparation(original,rr,helper,p,pool)['checked']
        if basis is None:basis=deepcopy(p['projection'])
        assert p['projection']==basis
        c=collection19.collect(p,targets,rr,lambda v:None)
        assert check_collection19.collection(p,rr,c)[0]['checked']
        pair_phases=[v for v in c['collection_phases']if v['phase']!='natural_target_queries']
        assert check_pairs(p['cell']['fixture'],p['geometry'],'batched',c['pairs'],pair_phases)['checked']
        recipe=core.recipes(original,c,rr,solver.Meter(original['fixture']),lambda v:None)
        cache=branch19.OwnedCache(c,rr,lambda v:None)
        branch=branch19.build(p,c,rr,recipe['policies']['general'],cache,lambda v:None)
        assert branch19.check(p,c,rr,recipe['policies']['general'],cache,branch)['checked']
        case=native_case.build(p,c,branch,cache,2,'anchors',solver.Meter(p['cell']['fixture']))
        if reference is None:
            projected=information19.project(case,p,solver.Meter(p['cell']['fixture']))
            reference=[(v['vector'],v['rhs'])for v in projected['rows']if v['kind']=='collected_source']
        info=information19.measure(reference,case,p,solver.Meter(p['cell']['fixture']))
        assert check_algebra19.information(reference,case,p,info)['checked']
        meter=solver.Meter(p['cell']['fixture']);result=cancel19.solve(case,p,meter)
        public_verify(result,case,p['cell']['fixture'],meter)
        assert check_algebra19.cancelled_target(case,p,result,p['cell']['fixture'])['checked']
        joint=solver.solve(case,'sparse_joint',solver.Meter(p['cell']['fixture']))
        assert [(v['identifiable'],v['scalar'])for v in result['recoveries']]==[(v['identifiable'],v['scalar'])for v in joint['recoveries']]


def test_metadata_only_native_grid_budget_and_protocol():
    import custody19,prepare19
    from datetime import datetime,timezone
    rules=custody19.load(custody19.INPUTS);custody19.validate_rules(rules)
    assert len(list(custody19.descriptors(rules)))==12
    assert len(list(custody19.executions(rules)))==24
    assert len(rules['excluded_curves'])==40
    assert rules['maximum_target_cache_points']==64 and rules['query_suppression']is False
    for bad in (dict(rules,pool_size=True),dict(rules,sources=129),dict(rules,maximum_target_cache_points=65)):
        with pytest.raises(ValueError):custody19.validate_rules(bad)
    p=prepare19.make_protocol('0'*40)
    assert not custody19.tools().schema_errors(p,'experiment.protocol/v1')
    assert not custody19.tools().lint_protocol(p,custody19.HERE)
    budget=prepare19.remaining_budget(datetime.now(timezone.utc))
    assert budget['absolute_deadline']=='2026-11-07T07:46:38.570520+00:00'
    assert budget['known_prior_cpu_seconds']>960 and len(budget['prior_measured_records'])==12
