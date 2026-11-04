"""Small marked control: fixed columns, actual anchor gain and corruptions."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'research/prime_field_a5_execution_20261104'
def load(name):
    s=importlib.util.spec_from_file_location('_source_control_'+name,HERE/(name+'.py'))
    v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v

@pytest.fixture(scope='module')
def panel():
    core=load('core');check=load('check')
    f=next(f for b in range(1,101) if (f:=core.previous.describe(101,2,b,8)[0])is not None and f['r']!=101)
    f=core.previous.attach_ec1(f);f['software_control']=True
    rules=dict(domain='software-control-only',sources=8,seeds=[0,1,2],maximum_scalar_candidates=10000,targets=2,prefixes=[0,2,8],collision_multipliers=4,max_pair_entries=4096,max_retained_rows=2048)
    order=list(range(1,9));projection=check.old.public_projection(f,order)
    cell=dict(id='tiny',fixture=f,old_source_order=order,projection=projection,target_generation=dict(targets=[dict(index=0,point=f['factor_base'][2]['point']),dict(index=1,point=f['P'])],search_trace=[]))
    events=[];result,meter=core.collect(cell,rules,events.append)
    for arm in ('window','hash0','hash1','hash2'):
        for count in rules['prefixes']:
            for anchors in (False,True):result['prefixes'].append(core.analyze_prefix(cell,rules,result,meter,arm,count,anchors))
    result['total_counters']=meter.counters()
    return core,check,cell,rules,result,events

def test_complete_oracle_and_fixed_columns(panel):
    core,check,cell,rules,result,events=panel
    verification=check.check(cell,rules,result,events)
    assert verification['checked'] and len(verification['prefixes'])==24
    assert verification['source_queries_checked']==4*8*16
    assert all(v['base_columns']==cell['projection']['U'] for v in verification['prefixes'])
    assert any(v['anchor_rank'] for v in verification['prefixes'])
    assert any(v['anchor_augmented_rank']>v['relation_rank'] for v in verification['prefixes'])

@pytest.mark.parametrize('kind',['selection','projection','anchor','query','rank','kernel','weights','cancellation','journal','cost'])
def test_false_records_refuse(panel,kind):
    core,check,cell,rules,result,events=panel;v=deepcopy(result);e=deepcopy(events)
    if kind=='selection':v['selection']['search_trace'][0]['scalar']+=1
    elif kind=='projection':v['projection']['U']+=1
    elif kind=='anchor':
        arm=next(a for a in v['arms'].values() if a['anchor_rows']);arm['anchor_rows'][0]['projected_rhs']+=1
    elif kind=='query':v['arms']['hash0']['status_blocks'][0]['queries'][0]['bucket'].append(999)
    elif kind=='rank':v['prefixes'][0]['base']['rank']+=1
    elif kind=='kernel':v['prefixes'][0]['base']['kernel'].append([0]*cell['projection']['U'])
    elif kind=='weights':
        rec=next(t for p in v['prefixes'] for t in p['joint_recoveries'] if t['identifiable']);rec['row_weights'].append(1)
    elif kind=='cancellation':v['prefixes'][0]['target_cancellations'].append(dict(target_row_weights=[],vector=[],rhs=0))
    elif kind=='journal':e.pop(next(i for i,x in enumerate(e) if x['kind']=='query_complete'))
    elif kind=='cost':v['total_counters']['source_queries']=0
    with pytest.raises(ValueError):check.check(cell,rules,v,e)

def test_native_admission_required(panel):
    core,_,cell,rules,_,_=panel;cell=deepcopy(cell);cell['fixture'].pop('software_control')
    with pytest.raises(ValueError,match='admission'):core.collect(cell,rules,lambda v:pytest.fail('native began'))
