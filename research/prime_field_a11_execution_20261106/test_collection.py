"""Small public group checks for affine streams before native admission."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
import affine_core as core
from check_solver import check
import affine_solver as solver
import check_source

def rules():return dict(software_control=True,domain='a11-software-controls/v1',fields=[dict(p=211,base_size=5)],a=1,curves_per_field=1,maximum_curve_candidates=128,maximum_scalar_candidates=256,maximum_target_candidates=256,excluded_curves=[],sources=16,targets=3,seeds=[0],prefixes=[0,8,16],source_prefixes=[8,16],target_prefixes=[1,2,4],target_queries_per_point=4,target_policies=['walk','hash_offset','general'],prerequisite=8,max_pair_entries=128,max_retained_rows=4096,max_affine_labels=8192)
def setup():
 r=rules();generated=core.generate(r,lambda v:None);check_source.check_generation(r,generated);cell=generated['cells'][0];collected=core.collect_sources(cell,r,lambda v:None)
 verified,oracle=check_source.collection(cell,r,collected);assert verified['checked'];m=solver.Meter(cell['fixture']);selection=core.recipes(cell,collected,r,m,lambda v:None);cache=core.QueryCache(cell,collected,r,lambda v:None)
 return r,cell,collected,selection,cache,oracle

def test_three_policies_general_u_and_public_certificates():
 r,cell,collected,selection,cache,oracle=setup()
 for policy in r['target_policies']:
  branch=core.construct_branch(cell,collected,r,selection['policies'][policy],'ap0',8,policy,cache,lambda v:None)
  for budget in r['target_prefixes']:
   for scope in ('relations','anchors'):
    c=core.case_input(cell,collected,branch,cache,budget,scope,solver.Meter(cell['fixture']));out=[]
    for arm in ('sparse_joint','sparse_cancel'):
     met=solver.Meter(cell['fixture']);result=solver.solve(c,arm,met)
     # Public check uses the independent arithmetic in check_source, without
     # adding a fictitious producer phase that was not executed by this control.
     for rec,target in zip(result['recoveries'],c['targets'],strict=True):
      if rec['identifiable']:assert check_source.old.multiply(cell['fixture']['p'],0,cell['fixture']['a'],rec['scalar'],tuple(cell['fixture']['P']))==tuple(target['point'])
     out.append(result)
    assert check(c,out)['checked']
 for rec in cache.records:
  point=None if rec['point']is None else tuple(rec['point'])
  assert sorted((tuple(v['triple']),tuple(v['signs'])) for v in rec['rows'])==sorted(oracle.get(point,[]))
def test_native_target_construction_refuses_unadmitted_inputs():
 r=rules();r['fields']=[dict(p=8191,base_size=16)];r['software_control']=False
 with pytest.raises(ValueError):core.QueryCache({},None,r,lambda v:None)
 with pytest.raises(ValueError):core.construct_branch({},None,r,None,None,0,None,None,lambda v:None)
 with pytest.raises(ValueError):core.recipes({},None,r,None,lambda v:None)
def test_partial_branch_failure_keeps_affine_points_and_phase_prefix():
 r,cell,collected,selection,cache,_=setup();journal=[];seen=0
 def event(v):
  nonlocal seen
  journal.append(v)
  if v['kind']=='affine_endpoint':
   seen+=1
   if seen==5:raise RuntimeError('injected affine construction failure')
 with pytest.raises(RuntimeError,match='injected'):core.construct_branch(cell,collected,r,selection['policies']['general'],'ap0',8,'general',cache,event)
 assert any(v['kind']=='affine_point' for v in journal)
 assert any(v['kind']=='affine_phase' and v['phase']['status']=='failed' and v['phase']['counters'] for v in journal)

@pytest.mark.parametrize('corruption',['recipe','future_scalar','future_label','outside_rhs','base_sign','alias','policy','phase'])
def test_independent_affine_checker_rejects_corruptions(corruption):
 from copy import deepcopy
 import affine_check as checker
 r,cell,collected,selection,cache,_=setup();oracle=checker.GroupOracle(cell['fixture'],collected['target_generation']['targets']);policy='general'
 branch=core.construct_branch(cell,collected,r,selection['policies'][policy],'ap0',8,policy,cache,lambda v:None)
 assert checker.recipes(cell,r,selection)
 assert checker.branch(cell,collected,r,selection['policies'][policy],branch,cache,oracle)['checked']
 if corruption=='recipe':branch['recipe'][0][1]['alpha']+=1
 elif corruption=='future_scalar':next(v for v in branch['scalar_events'] if v['step']>1)['step']=1
 elif corruption=='future_label':next(v for v in branch['labels'] if v['budget']>1)['budget']=1
 elif corruption=='outside_rhs':next(v for v in branch['equations'] if v['kind']=='point_coincidence')['rhs']+=1
 elif corruption=='base_sign':next(v for v in branch['equations'] if v['kind']=='base_match')['witness']['sign']*=-1
 elif corruption=='alias':branch['requests'][0]['query_id']=len(cache.records)
 elif corruption=='policy':branch['selections']['P']['candidates'][0]['uncached_ec_adds']+=1
 elif corruption=='phase':branch['counters']['scalar_uncached_ec_adds']+=1
 with pytest.raises(ValueError):checker.branch(cell,collected,r,selection['policies'][policy],branch,cache,oracle)

def test_physical_query_cache_oracle_and_false_miss_refusal():
 import affine_check as checker
 r,cell,collected,selection,cache,triples=setup()
 for policy in r['target_policies']:core.construct_branch(cell,collected,r,selection['policies'][policy],'ap0',8,policy,cache,lambda v:None)
 assert checker.query_cache(cell,collected,cache,triples)['checked']
 cache.records[-1]['trace'][0]['bucket']=[999]
 with pytest.raises(ValueError,match='query/miss'):checker.query_cache(cell,collected,cache,triples)
