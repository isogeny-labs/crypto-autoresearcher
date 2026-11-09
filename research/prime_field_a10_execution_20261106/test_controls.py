"""Small exact controls only; no frozen fresh-panel generation or trial."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core,solver,check
from construct import select,LabelledCurve,Constructor

def toy():return dict(p=101,r=101,a=2,b=3,P=[1,39],software_control=True)
def cases():
    yield dict(width=2,target_count=2,modulus=101,source=[([1,0],3)],target=[dict(target_index=0,vector=[0,1],rhs=4),dict(target_index=0,vector=[0,2],rhs=9)],targets=[])
    yield dict(width=2,target_count=2,modulus=101,source=[],target=[],targets=[])
    yield dict(width=0,target_count=1,modulus=101,source=[([],0)],target=[dict(target_index=0,vector=[],rhs=5)],targets=[])
    yield dict(width=2,target_count=2,modulus=101,source=[([1,0],3),([0,1],5)],target=[dict(target_index=0,vector=[1,1],rhs=2),dict(target_index=1,vector=[0,1],rhs=8)],targets=[])
def results(case):return [solver.solve(case,arm,solver.Meter(dict(toy(),r=case['modulus']))) for arm in ('sparse_joint','sparse_cancel')]
@pytest.mark.parametrize('case',list(cases()))
def test_dense_certificates_json_and_old_kernel_equivalence(case):
    out=results(case);assert check.check(case,json.loads(json.dumps(out)))['checked']
    for result,arm in zip(out,('sparse_joint','sparse_cancel'),strict=True):
        parent=solver.parent.solve(case,arm,solver.parent.Meter(toy()))
        assert [(v['identifiable'],v['scalar']) for v in result['recoveries']]==[(v['identifiable'],v['scalar']) for v in parent['recoveries']]
        assert result['system']['kernel_computed']is False
        assert all(p['phase']!='kernel' for p in result['phases'])
@pytest.mark.parametrize('change',['rank','echelon','certificate','residual','identified','phase','missing'])
def test_solver_corruptions_refused(change):
    case=list(cases())[-1];out=results(case)
    if change=='rank':out[0]['system']['rank']+=1
    elif change=='echelon':out[0]['system']['echelon'][0]['row_weights'][0]+=1
    elif change=='certificate':out[0]['recoveries'][0]['original_row_weights'][0]+=1
    elif change=='residual':out[0]['recoveries'][0]['residual'][0]=1
    elif change=='identified':out[0]['recoveries'][0]['identifiable']=False
    elif change=='phase':out[0]['counters']['Fr.field_mul']+=1
    elif change=='missing':out[0]['recoveries'].pop()
    with pytest.raises(ValueError):check.check(case,out)
@pytest.mark.parametrize('window',range(9))
def test_scalar_predictor_independent_portfolio(window):
    from construct import ScalarModel,evaluate
    r=211;work=[80,191,13,120,81];known=list(range(1,9))
    model=ScalarModel(r,known);entries=evaluate(model,work,window,r,1)
    other=check.scalar_replay(r,window,work,known)
    assert (model.calls,entries,set(model.known))==(other['calls'],other['table_entries'],other['known'])
def test_native_generation_and_collection_refuse_without_admission():
    rules=dict(fields=[dict(p=8191,base_size=16)])
    with pytest.raises(ValueError):core.generate(rules,lambda v:None)
    with pytest.raises(ValueError):core.collect({},rules,lambda v:None)
def test_split_subtraction_units():
    m=solver.Meter(toy());m.f.sub(3,1);m.ring.sub(3,1)
    assert m.counters()=={'Fp.field_sub':1,'Fr.field_sub':1}

def small_rules():return dict(software_control=True,domain='a10-software-only',fields=[dict(p=211,base_size=5)],a=1,curves_per_field=1,maximum_curve_candidates=128,maximum_scalar_candidates=256,maximum_target_candidates=256,excluded_curves=[],sources=16,targets=3,seeds=[0],prefixes=[0,4,8,16],prerequisite=8,max_pair_entries=128,max_retained_rows=128)
def test_full_small_collector_future_knowledge_and_dense_targets():
    rules=small_rules();generated=core.generate(rules,lambda v:None);assert check.check_generation(rules,generated)['checked']
    cell=generated['cells'][0];collected=core.collect(cell,rules,lambda v:None)
    assert check.collection(cell,rules,json.loads(json.dumps(collected)))['checked']
    for arm in collected['arms']:
        assert all(v['origin']=='shared_prerequisite' for v in collected['arms'][arm]['knowledge'] if v['prefix']==0)
        for b in rules['prefixes']:
            case=core.case_input(cell,collected,arm,b,'anchors',solver.Meter(cell['fixture']))
            assert json.dumps(case,sort_keys=True)==json.dumps(check.expected_case(cell,collected,arm,b,'anchors'),sort_keys=True)
            assert check.check(case,results(case))['checked']
    broken=deepcopy(collected);item=next(v for v in broken['arms']['ap0']['knowledge'] if v['prefix']>0);item['prefix']=0
    with pytest.raises(ValueError,match='future'):check.collection(cell,rules,broken)

@pytest.mark.parametrize('corruption',['query_miss','anchor','future_source','policy','coefficients'])
def test_collector_corruptions(corruption):
    rules=small_rules();cell=core.generate(rules,lambda v:None)['cells'][0];collected=core.collect(cell,rules,lambda v:None)
    if corruption=='query_miss':collected['arms']['ap0']['query_trace'][0]['bucket']=[999]
    elif corruption=='anchor':collected['arms']['ap0']['anchors'][0]['coefficients']=[0]*5
    elif corruption=='future_source':collected['arms']['ap0']['sources'][0]['prefix']=0
    elif corruption=='coefficients':collected['target_collection']['rows'][0]['coefficients'][0]+=1
    elif corruption=='policy':collected['arms']['ap0']['selection']['candidates'][0]['group_add_calls']+=1
    with pytest.raises(ValueError):check.collection(cell,rules,collected)

def test_mid_construction_failure_keeps_points_sources_and_partial_phase():
    rules=small_rules();cell=core.generate(rules,lambda v:None)['cells'][0];journal=[];seen=0
    def event(value):
        nonlocal seen
        journal.append(deepcopy(value))
        if value['kind']=='source_constructed':
            seen+=1
            if seen==3:raise RuntimeError('injected mid-block failure')
    with pytest.raises(RuntimeError,match='injected'):core.collect(cell,rules,event)
    assert len([v for v in journal if v['kind']=='source_constructed'])==3
    assert any(v['kind']=='constructor_point' and v['prefix']>0 for v in journal)
    failed=[v['phase'] for v in journal if v['kind']=='collection_phase' and v['phase']['status']=='failed']
    assert len(failed)==1 and failed[0]['counters']['constructor_group_add_calls']>0
