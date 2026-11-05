"""Marked tiny-field controls for prefix knowledge, cached costs and certificates."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/prime_field_a7_execution_20261104'
def load(name):
    spec=importlib.util.spec_from_file_location('_budget_control_'+name,HERE/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

@pytest.fixture(scope='module')
def panel():
    core=load('core');check=load('check')
    f=next(f for b in range(1,101) if (f:=core.previous.describe(101,2,b,8)[0])is not None and f['r']!=101)
    f=core.previous.attach_ec1(f);f['software_control']=True
    rules=dict(domain='budget-software-control',sources=16,anchor_prerequisite_sources=8,seeds=[0,1,2],maximum_scalar_candidates=10000,targets=2,prefixes=[0,2,4,8,12,16],collision_multipliers=4,max_pair_entries=4096,max_retained_rows=4096)
    order=list(range(1,9));cell=dict(id='tiny',fixture=f,old_source_order=order,projection=check.old.public_projection(f,order),target_generation=dict(targets=[dict(index=0,point=f['factor_base'][2]['point']),dict(index=1,point=f['P'])],search_trace=[]))
    events=[];result,meter=core.collect(cell,rules,events.append)
    for arm in ('window','hash0','hash1','hash2'):
        for count in rules['prefixes']:
            for anchors in (False,True):result['prefixes'].append(core.analyze_prefix(cell,rules,result,meter,arm,count,anchors))
    result['total_counters']=meter.counters()
    return core,check,cell,rules,result,events

def test_complete_oracle_and_exact_budget_costs(panel):
    core,check,cell,rules,result,events=panel;v=check.check(cell,rules,result,events)
    assert v['checked'] and v['source_queries_checked']==4*16*16
    for p in result['prefixes']:
        c=p['budget_costs']['construction']['counters']
        assert c.get('source_scalar_multiplications',0)+c.get('source_point_cache_hits',0)==p['prefix']
        assert p['budget_costs']['queries']['counters'].get('source_queries',0)==p['prefix']*16
    at8=next(p for p in result['prefixes'] if p['arm']=='window' and p['prefix']==8)
    assert at8['budget_costs']['construction']['counters'].get('source_scalar_multiplications',0)==0
    assert at8['budget_costs']['prerequisite']['counters']['prerequisite_scalar_multiplications']==8

def test_no_future_anchor_or_diagnostic_credit(panel):
    core,check,cell,rules,result,events=panel
    for arm,value in result['arms'].items():
        zero=next(p for p in result['prefixes'] if p['arm']==arm and p['prefix']==0 and p['scope']=='anchors')
        assert zero['anchor_rows_inserted']==0
        assert value['budget_records'][0]['available_sources']==[]
        assert all(not m['from_schedule'] for d in value['budget_records'][0]['collision_diagnostics'] for m in d['bounded_multiple_matches'])
    assert any(v['anchor_rows'] for v in result['arms'].values())

@pytest.mark.parametrize('kind',['future_anchor','future_diagnostic','query','kernel','certificate','cost','cache','hash','journal'])
def test_corrupted_prefix_or_cost_records_refuse(panel,kind):
    core,check,cell,rules,result,events=panel;r=deepcopy(result);e=deepcopy(events)
    if kind=='future_anchor':next(p for p in r['prefixes'] if p['scope']=='anchors')['anchor_rows_inserted']=1
    elif kind=='future_diagnostic':r['arms']['hash0']['budget_records'][0]['available_sources']=[999]
    elif kind=='query':r['arms']['hash0']['status_blocks'][0]['queries'][0]['bucket'].append(999)
    elif kind=='kernel':r['prefixes'][0]['base']['kernel'].append([0]*cell['projection']['U'])
    elif kind=='certificate':
        p=next(t for p in r['prefixes'] for t in p['joint_recoveries'] if t['identifiable']);p['row_weights'].append(1)
    elif kind=='cost':r['prefixes'][0]['budget_costs']['construction']['counters']['source_scalar_multiplications']=100
    elif kind=='cache':
        p=next(p for p in r['collection_phases'] if p['phase']=='window_8_source_construction');p['counters']['source_point_cache_hits']=0
    elif kind=='hash':r['selection']['search_trace'][0]['scalar']+=1
    elif kind=='journal':e.pop(next(i for i,x in enumerate(e) if x['kind']=='budget_complete'))
    with pytest.raises(ValueError):check.check(cell,rules,r,e)

def test_admission_and_aa(panel):
    core,check,cell,rules,result,events=panel;r,_=core.collect(cell,rules,lambda v:None)
    for k in ('selection','projection','pair_entries','arms','target_collection','target_multiple_cache'):assert r[k]==result[k]
    native=deepcopy(cell);native['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'):core.collect(native,rules,lambda e:pytest.fail('native ran'))


def test_cumulative_row_cap_across_individually_small_blocks(panel):
    from collections import Counter
    core,_,cell,rules,result,_=panel;largest=0
    for arm,value in result['arms'].items():
        order=result['selection']['schedules'][arm];lo=0
        for hi in rules['prefixes']:
            largest=max(largest,sum(row['source_scalar'] in order[lo:hi] for row in value['rows']));lo=hi
    cap=largest+1
    assert all(len(v['rows'])>cap for v in result['arms'].values())
    limited=deepcopy(rules);limited['max_retained_rows']=cap;events=[]
    with pytest.raises(ValueError,match='cumulative retained-row'):core.collect(cell,limited,events.append)
    accepted=Counter(e['arm'] for e in events if e['kind']=='source_accepted')
    assert max(accepted.values())==cap+1
