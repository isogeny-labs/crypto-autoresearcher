"""Tiny actual-array arithmetic equivalence, exception and counter controls."""
import copy,json,sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
import pytest
import batch_query as b,batch_check as c
from affine_solver import Meter
from crypto_autoresearcher.index_calculus import _accel

def fixture():
 f=dict(p=211,r=19,a=210,b=0);points=[(x,y) for x in range(211) for y in range(211) if (y*y-x*x*x+x)%211==0]
 base=[(0,0),(1,0),(210,0)]+[q for q in points if q[1]!=0][:2]
 return f,base,points

@pytest.mark.parametrize('n',[1,2,3,5])
def test_all_small_points_match_scalar_production_numpy_and_count_oracle(n):
 f,base,points=fixture();base=base[:n];signed={(i,s):(x,y if s==1 else -y%211) for i,(x,y) in enumerate(base) for s in (1,-1)};events=[];parent=Meter(f);engine=b.QueryEngines(f,base,signed,parent,events.append);arr=_accel.FBArrays(SimpleNamespace(p=211,points=base));requests=[None,*points[:17],*base]
 for Q in requests:
  result=engine.evaluate(Q,parent,dict(software_control=True))
  if Q is not None:
   ix=np.repeat(np.arange(n),2);sg=np.tile([1,-1],n);xx,yy,zero=_accel.subtract_many(arr,*Q,ix,sg);expected=[]
   for i,(x,y,z) in enumerate(zip(xx,yy,zero,strict=True)):
    expected.append(c.check_source.old.add(211,0,210,Q,signed[i//2,-int(sg[i])]) if z else (int(x),int(y)))
   assert result==expected
 cell=dict(fixture=dict(f,factor_base=[dict(point=list(q)) for q in base]))
 verification=c.records(cell,engine.records,[None if q is None else list(q) for q in requests]);assert verification['endpoint_records']==len(requests)
 for arm in ('scalar','batch'):
  for key,value in verification['engine_totals'][arm].items():assert parent.counters().get('query_'+arm+'.'+key,0)==value
 record=copy.deepcopy(engine.records);record[0]['points_sha256']='0'*64
 with pytest.raises(ValueError,match='point hash'):c.records(cell,record,[None if q is None else list(q) for q in requests])
 record=copy.deepcopy(engine.records);record[1]['engines']['batch']['counters']['Fp.field_inv']=999;record[1]['engines']['batch']['phases'][0]['counters']['Fp.field_inv']=999
 with pytest.raises(ValueError,match='field-count'):c.records(cell,record,[None if q is None else list(q) for q in requests])


def test_tree_nonzero_gate_uint64_domain_and_failed_prefix():
 f,base,points=fixture();m=Meter(f)
 with pytest.raises(ValueError,match='nonempty nonzero'):b.batch_inverse(np.array([0],dtype=np.uint64),b.VectorField(m))
 with pytest.raises(ValueError,match='nonempty nonzero'):b.batch_inverse(np.array([],dtype=np.uint64),b.VectorField(m))
 signed={(i,s):(x,s*y%211) for i,(x,y) in enumerate(base) for s in (1,-1)}
 with pytest.raises(ValueError,match='uint64'):b.QueryEngines(dict(f,p=2**32),base,signed,m,lambda v:None)
 events=[];e=b.QueryEngines(f,base,signed,m,events.append)
 original=e.batch
 def bad(Q,meter):
  result,indices=original(Q,meter);result[0]=None;return result,indices
 e.batch=bad
 with pytest.raises(ValueError,match='disagreement'):e.evaluate(points[20],m,dict(injected_failure=True))
 assert events[-1]['kind']=='query_engines_failed' and len(events[-1]['partial_points'])==2
 assert m.counters()['query_scalar.Fp.group_add']==2*len(base)

def test_cold_engine_views_do_not_borrow_control_arithmetic_or_batch_setup():
 from costs import select_engine
 f,base,points=fixture();signed={(i,s):(x,s*y%211) for i,(x,y) in enumerate(base) for s in (1,-1)};m=Meter(f);e=b.QueryEngines(f,base,signed,m,lambda v:None);e.evaluate(points[20],m,{})
 combined=m.counters();scalar=select_engine(combined,'scalar');batch=select_engine(combined,'batch');record=e.records[0]
 for engine,view in [('scalar',scalar),('batch',batch)]:
  for key in ('Fp.field_add','Fp.field_sub','Fp.field_mul','Fp.field_inv','Fp.group_add'):assert view.get(key,0)==record['engines'][engine]['counters'].get(key,0)
  assert not any(key.startswith(('query_scalar.','query_batch.','query_batch_index.')) for key in view)
  assert 'query_engine_point_comparisons' not in view
 assert scalar.get('query_array_allocated_bytes',0)==0 and batch['query_array_allocated_bytes']>0
 bad=copy.deepcopy(combined);bad['query_batch.Fp.field_inv']=999
 with pytest.raises(ValueError,match='exceeds'):select_engine(bad,'scalar')

def test_midbatch_failure_retains_executed_counts_and_failed_phase(monkeypatch):
 f,base,points=fixture();signed={(i,s):(x,s*y%211) for i,(x,y) in enumerate(base) for s in (1,-1)};events=[];m=Meter(f);e=b.QueryEngines(f,base,signed,m,events.append);original=b.VectorField.mul;calls=0
 def injected(self,left,right):
  nonlocal calls
  calls+=1
  if calls==4:raise RuntimeError('injected vector failure')
  return original(self,left,right)
 monkeypatch.setattr(b.VectorField,'mul',injected)
 with pytest.raises(RuntimeError,match='injected'):e.evaluate(points[20],m,{})
 record=events[-1];assert record['kind']=='query_engines_failed'
 assert record['engines']['batch']['phases'][0]['status']=='failed'
 assert record['engines']['batch']['counters']['Fp.field_mul']>0
 assert m.counters()['query_batch.Fp.field_mul']==record['engines']['batch']['counters']['Fp.field_mul']


def test_field_candidate_checker_refuses_bad_first_prime_or_work_trace():
 rules=dict(fields=[dict(bits=4,p=13)],maximum_field_candidates=3);trace=[dict(bits=4,candidate=15,counter=0,prime=False,trial_divisions=2,divisor=3),dict(bits=4,candidate=14,counter=1,prime=False,trial_divisions=1,divisor=2),dict(bits=4,candidate=13,counter=2,prime=True,trial_divisions=2,divisor=None)]
 assert c.field_selection(rules,dict(field_prime_selection=trace))['checked']
 bad=copy.deepcopy(trace);bad[0]['trial_divisions']=1
 with pytest.raises(ValueError,match='primality trace'):c.field_selection(rules,dict(field_prime_selection=bad))
 with pytest.raises(ValueError,match='first-prime'):c.field_selection(dict(rules,fields=[dict(bits=4,p=11)]),dict(field_prime_selection=trace))

def test_target_identity_sets_and_counter_scope_in_frontier():
 import frontier
 a=dict(identified_mask=1,delta=0,counters={'Fp.field_mul':3,'lookup':8});b0=dict(identified_mask=2,delta=0,counters={'Fp.field_mul':4,'lookup':9})
 assert not frontier.dominates(a,b0,['Fp.field_mul','lookup']) and not frontier.dominates(b0,a,['Fp.field_mul','lookup'])
 b1=dict(b0,identified_mask=1,counters={'Fp.field_mul':4,'lookup':1})
 assert frontier.dominates(a,b1,['Fp.field_mul'])
 assert not frontier.dominates(a,b1,['Fp.field_mul','lookup'])
 b2=dict(b0,identified_mask=3)
 assert not frontier.dominates(a,b2,['Fp.field_mul'])
