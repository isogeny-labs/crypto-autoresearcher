"""Tiny affine/public controls for the A9 four-arm functional experiment."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'research/prime_field_a9_json_control_20261105'/(name+'.py');s=importlib.util.spec_from_file_location('_tiny_a9json_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
core=load('core');checker=load('check');F=dict(p=101,r=101,a=2,b=3,P=[1,1],software_control=True);ARMS=('dense_joint','dense_cancel','sparse_joint','sparse_cancel')
def case():return dict(width=3,target_count=3,modulus=101,source=[([1,0,0],2)],target=[dict(target_index=0,vector=[0,1,0],rhs=0),dict(target_index=0,vector=[0,2,0],rhs=3),dict(target_index=1,vector=[0,1,1],rhs=5)],targets=[])
def run(c):return [core.solve(c,arm,core.Meter(F)) for arm in ARMS]

def test_complete_factorial_affine_oracle_and_unchanged_certificates():
 c=case();r=run(c);v=checker.check(c,r,None)
 assert v['factorial_arms']==4 and v['all_modes_equal'] and v['identified']==1
 for dense,sparse in ((r[0],r[2]),(r[1],r[3])):
  assert dense['recoveries']==sparse['recoveries'] and dense['system']==sparse['system']
  assert dense['counters'].get('functional_coefficients_scanned')is None
  assert sparse['counters']['functional_coefficients_scanned']>0
  assert sparse['counters'].get('Fr.field_mul',0)<=dense['counters'].get('Fr.field_mul',0)
  assert sparse['counters'].get('Fr.field_sub',0)==dense['counters'].get('Fr.field_sub',0)

@pytest.mark.parametrize('vector',[[0,0,0],[0,1,0],[0,100,0],[0,2,0],[1,100,0],[0,0,1]])
def test_support_unit_nonunit_and_zero_syndromes(vector):
 meters=[core.Meter(F),core.Meter(F)];systems=[core.CertifiedSystem(3,meters[0]),core.SparseCertifiedSystem(3,meters[1])]
 for s in systems:s.add([1,0,0],2)
 values=[s.identify(vector,s.kernel()) for s in systems]
 assert values[0]==values[1]
 if vector==[0,1,0]:assert meters[1].other['kernel_coordinate_reads']==2
 if vector==[0,100,0]:assert meters[1].other.get('kernel_coordinate_reads',0)==0

@pytest.mark.parametrize('kind',['weight','syndrome','phase','count','scan','support','coordinate','ident_sub','ident_inv','mode'])
def test_independent_checks_refuse_factorial_corruption(kind):
 c=case();r=run(c)
 if kind=='weight':r[2]['recoveries'][0]['original_row_weights'][0]+=1
 elif kind=='syndrome':r[2]['recoveries'][0]['syndrome'].append(1)
 elif kind=='phase':r[2]['phases'][0]['counters']['Fr.field_add']=1;r[2]['counters']['Fr.field_add']=r[2]['counters'].get('Fr.field_add',0)+1
 elif kind=='count':r[2]['counters']['Fr.field_mul']+=1
 elif kind=='scan':
  r[2]['counters']['functional_coefficients_scanned']+=1
  next(p for p in r[2]['phases'] if p['phase']=='identification')['counters']['functional_coefficients_scanned']+=1
 elif kind in ('support','coordinate','ident_sub','ident_inv'):
  key={'support':'functional_support_entries','coordinate':'kernel_coordinate_reads','ident_sub':'Fr.field_sub','ident_inv':'Fr.field_inv'}[kind]
  r[2]['counters'][key]=r[2]['counters'].get(key,0)+1
  phase=next(p for p in r[2]['phases'] if p['phase']=='identification');phase['counters'][key]=phase['counters'].get(key,0)+1
 elif kind=='mode':r[3]['arm']='sparse_joint'
 with pytest.raises(ValueError):checker.check(c,r,None)


def test_public_and_retention_failure_controls(monkeypatch):
 fixture=next(f for b in range(1,101) if (f:=core.old.describe(101,2,b,8)[0])is not None and f['r']!=101);fixture['software_control']=True
 q=core.Meter(fixture).e.mul(3,tuple(fixture['P']));c=dict(width=1,target_count=1,modulus=fixture['r'],source=[([1],3)],target=[dict(target_index=0,vector=[1],rhs=0)],targets=[dict(index=0,point=list(q))]);results=core.compare(c,fixture);checker.check(c,results,fixture)
 oldsolve=core.solve;retained=[];failed=[]
 def fault(case,arm,meter):
  if arm=='sparse_joint':
   def fail():meter.ring.mul(1,2);raise ValueError('third-arm fault')
   meter.stage('injected_failure',fail)
  return oldsolve(case,arm,meter)
 monkeypatch.setattr(core,'solve',fault)
 with pytest.raises(ValueError,match='third-arm'):core.compare(c,fixture,on_result=retained.append,on_failure=lambda arm,phases,result,error:failed.append((arm,phases)))
 assert [r['arm'] for r in retained]==['dense_joint','dense_cancel']
 assert failed[0][1][-1]['status']=='failed' and failed[0][1][-1]['counters']['Fr.field_mul']==1
 with pytest.raises(ValueError,match='admission'):core.compare(c,{**fixture,'software_control':False})

@pytest.mark.parametrize('width,nt',[(0,0),(0,2),(2,0),(2,2)])
def test_empty_cases_and_deterministic_aa(width,nt):
 c=dict(width=width,target_count=nt,modulus=101,source=[([0]*width,0)],target=[],targets=[]);a=run(c);b=run(c);checker.check(c,a,None)
 for x,y in zip(a,b,strict=True):assert x['system']==y['system'] and x['recoveries']==y['recoveries'] and x['counters']==y['counters']


def test_tiny_dense_modes_replay_original_a8_phase_vectors():
 spec=importlib.util.spec_from_file_location('_tiny_original_a8',ROOT/'research/prime_field_a8_execution_20261105/core.py');a8=importlib.util.module_from_spec(spec);spec.loader.exec_module(a8)
 c=case();control=dict(results=[a8.solve(c,arm,a8.Meter(F)) for arm in ('full_joint','cancellation_first')])
 assert checker.check(c,run(c),None,control=control)['a8_dense_control']
 bad=deepcopy(control);bad['results'][0]['counters']['Fr.field_mul']+=1
 with pytest.raises(ValueError,match='A8 dense'):checker.check(c,run(c),None,control=bad)


def test_actual_json_roundtrip_reproduces_old_failure_and_fixed_comparison():
 import json
 spec=importlib.util.spec_from_file_location('_old_frozen_a9_check',ROOT/'research/prime_field_a9_execution_20261105/check.py');oldcheck=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldcheck)
 spec=importlib.util.spec_from_file_location('_json_control_original_a8',ROOT/'research/prime_field_a8_execution_20261105/core.py');a8=importlib.util.module_from_spec(spec);spec.loader.exec_module(a8)
 c=case();control=dict(results=[a8.solve(c,arm,a8.Meter(F)) for arm in ('full_joint','cancellation_first')]);archived=json.loads(json.dumps(control))
 with pytest.raises(ValueError,match='representatives'):oldcheck.check(c,run(c),None,control=archived)
 assert checker.check(c,run(c),None,control=archived)['a8_dense_control']
 bad=deepcopy(archived);first=next(iter(bad['results'][1]['representatives']));bad['results'][1]['representatives'][first]+=1
 with pytest.raises(ValueError,match='representatives'):checker.check(c,run(c),None,control=bad)
 assert checker.canonical_representatives({'1':7,3:9})=={1:7,3:9}
 with pytest.raises(ValueError,match='noncanonical'):checker.canonical_representatives({'01':7})


def test_original_cumulative_budget_and_deadline_are_not_reset():
 from datetime import datetime,timezone,timedelta
 spec=importlib.util.spec_from_file_location('_json_repair_budget',ROOT/'research/prime_field_a9_json_control_20261105/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 now=datetime(2026,11,5,22,30,tzinfo=timezone.utc);release=dict(campaign_max_cpu_wall_seconds=21600,watchdog_seconds=21600,absolute_deadline=(now+timedelta(seconds=100)).isoformat());prior=dict(cpu_user_seconds=1.694653,cpu_sys_seconds=1.384321,diagnostic_wall_seconds=3.458040659)
 assert m.remaining_watchdog(release,prior,now)==100
 assert m.remaining_watchdog(release,{**prior,'cpu_user_seconds':21598,'cpu_sys_seconds':1},now)==1
 assert m.remaining_watchdog(release,{**prior,'diagnostic_wall_seconds':21599},now)==1
 for kwargs in (dict(absolute_deadline=now.isoformat()),dict(watchdog_seconds=0)):
  with pytest.raises(ValueError,match='exhausted'):m.remaining_watchdog({**release,**kwargs},prior,now)


def test_failed_prefix_accounting_does_not_require_finalized_case_files():
 spec=importlib.util.spec_from_file_location('_json_repair_journal_accounting',ROOT/'research/prime_field_a9_json_control_20261105/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 events=[dict(kind='case_input',shared_phases=[dict(counters={'Fr.field_mul':7})]),dict(kind='solver_complete',result=dict(arm='dense_joint',counters={'Fr.field_mul':11})),dict(kind='solver_failed',arm='dense_cancel',phases=[dict(status='complete',counters={'Fr.field_mul':3}),dict(status='failed',counters={'Fr.field_sub':2})]),dict(kind='failure')]
 out=m.observed_journal_work(events)
 assert out['observed_completed_producer_calls']==1 and out['failed_solver_events']==1
 assert out['observed_arm_counters']['dense_joint']=={'Fr.field_mul':11}
 assert out['observed_arm_counters']['dense_cancel']=={'Fr.field_mul':3,'Fr.field_sub':2}
 assert out['shared_projection_counters']=={'Fr.field_mul':7} and out['partial_work_unknown']


def test_hard_killed_journal_without_failure_marker_keeps_unknown_work():
 spec=importlib.util.spec_from_file_location('_json_hardkill_accounting',ROOT/'research/prime_field_a9_json_control_20261105/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 descriptor=dict(cell_id='toy',arm='window',prefix=0,scope='relations')
 out=m.observed_journal_work([dict(kind='case_started',descriptor=descriptor),dict(kind='case_input',shared_phases=[dict(counters={'Fr.field_mul':7})])])
 assert out['partial_work_unknown'] and out['failure_events']==0 and out['observed_completed_producer_calls']==0
 assert out['shared_projection_counters']=={'Fr.field_mul':7}
