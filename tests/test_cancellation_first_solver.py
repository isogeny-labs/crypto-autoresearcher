"""Small synthetic affine systems; no A8 native data or target logs are evaluated."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'research/prime_field_a8_execution_20261105'/(name+'.py');s=importlib.util.spec_from_file_location('_tiny_a8_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
core=load('core');checker=load('check')
F=dict(p=101,r=101,a=2,b=3,P=[1,1],software_control=True)
def fixture():
 return dict(width=3,target_count=3,modulus=101,source=[([1,0,0],2)],target=[dict(target_index=0,vector=[0,1,0],rhs=0),dict(target_index=0,vector=[0,2,0],rhs=3),dict(target_index=1,vector=[0,1,1],rhs=5)],targets=[])
def run(case):return [core.solve(case,arm,core.Meter(F)) for arm in ('full_joint','cancellation_first')]
def test_joint_cancellation_and_lifting_with_missing_target():
 c=fixture();results=run(c);v=checker.check(c,results,None)
 assert v['identified']==1 and v['base_rank_after_cancellation']==2
 assert results[1]['system']['nullity']==1
 assert [(x['identifiable'],x['scalar']) for x in results[0]['recoveries']]==[(True,3),(False,None),(False,None)]
 assert results[1]['recoveries'][0]['original_row_weights']==[0,99,1,0]
 assert results[1]['recoveries'][2]['representative']is None
 assert results[1]['counters']['Fr.field_sub']>0
 assert results[0]['counters']['Fr.field_sub']>0

@pytest.mark.parametrize('kind',['weight','rhs','kernel','cancellation','missing','phase','count','outcome'])
def test_independent_checker_refuses_corruption(kind):
 c=fixture();a=run(c)
 if kind=='weight':a[1]['recoveries'][0]['original_row_weights'][1]+=1
 elif kind=='rhs':a[1]['recoveries'][0]['scalar']+=1
 elif kind=='kernel':a[1]['system']['kernel'].append([0,0,0])
 elif kind=='cancellation':a[1]['cancellations'][0]['vector'][1]+=1
 elif kind=='missing':a[1]['recoveries'][2]['representative']=0
 elif kind=='phase':a[1]['phases'].pop()
 elif kind=='count':a[1]['counters']['Fr.field_mul']+=1
 elif kind=='outcome':a[1]['recoveries'][1]['identifiable']=True
 with pytest.raises(ValueError):checker.check(c,a,None)

@pytest.mark.parametrize('width,nt',[(0,0),(0,2),(2,0),(2,2)])
def test_empty_and_dependent_systems(width,nt):
 c=dict(width=width,target_count=nt,modulus=101,source=[([0]*width,0)]*3,target=[],targets=[])
 checker.check(c,run(c),None)


def test_aa_and_gate_and_shape():
 c=fixture();a=run(c);b=run(c)
 for x,y in zip(a,b,strict=True):
  assert x['system']==y['system'] and x['recoveries']==y['recoveries'] and x['counters']==y['counters']
 with pytest.raises(ValueError,match='admission'):core.compare(c,{**F,'software_control':False})
 c['source'][0]=([1,2],0)
 with pytest.raises(ValueError,match='shape'):run(c)


def test_inconsistent_affine_rows_refuse_and_counter_split():
 c=fixture();c['source'] += [([1,0,0],4)]
 for arm in ('full_joint','cancellation_first'):
  with pytest.raises(ValueError,match='inconsistent'):core.solve(c,arm,core.Meter(F))
 f=core.ScalarField(101);f.add(2,3);f.sub(2,3);f.mul(2,3);f.inv(2)
 assert dict(f.counts)==dict(field_add=1,field_sub=1,field_mul=1,field_inv=1)


def test_marked_public_target_check_and_counter_conservation():
 fixture=next(f for b in range(1,101) if (f:=core.old.describe(101,2,b,8)[0])is not None and f['r']!=101)
 fixture['software_control']=True;meter=core.Meter(fixture);q=meter.e.mul(3,tuple(fixture['P']))
 c=dict(width=1,target_count=2,modulus=fixture['r'],source=[([1],3)],target=[dict(target_index=0,vector=[1],rhs=0)],targets=[dict(index=0,point=list(q)),dict(index=1,point=fixture['P'])])
 result=core.compare(c,fixture);checker.check(c,result,fixture)
 for v in result:
  assert v['counters']['public_target_certificates_verified']==1
  assert v['phases'][-1]['phase']=='public_target_verification'
  assert v['counters']['Fp.group_add']>0
 c['targets'][0]['point']=fixture['P']
 with pytest.raises(ValueError,match='public'):core.compare(c,fixture)


def test_completed_arm_survives_second_arm_failure(monkeypatch):
 fixture=next(f for b in range(1,101) if (f:=core.old.describe(101,2,b,8)[0])is not None and f['r']!=101);fixture['software_control']=True
 q=core.Meter(fixture).e.mul(3,tuple(fixture['P']));c=dict(width=1,target_count=1,modulus=fixture['r'],source=[([1],3)],target=[dict(target_index=0,vector=[1],rhs=0)],targets=[dict(index=0,point=list(q))])
 oldsolve=core.solve;retained=[];failures=[]
 def broken(case,arm,meter):
  if arm=='cancellation_first':
   def fail():meter.ring.sub(2,1);raise ValueError('injected second-arm failure')
   meter.stage('injected_failure',fail)
  return oldsolve(case,arm,meter)
 monkeypatch.setattr(core,'solve',broken)
 with pytest.raises(ValueError,match='injected'):core.compare(c,fixture,on_result=retained.append,on_failure=lambda arm,phases,result,error:failures.append((arm,phases,result,str(error))))
 assert len(retained)==1 and retained[0]['arm']=='full_joint' and retained[0]['recoveries'][0]['scalar']==3
 assert failures[0][0]=='cancellation_first' and failures[0][1][-1]['status']=='failed' and failures[0][1][-1]['counters']['Fr.field_sub']==1
