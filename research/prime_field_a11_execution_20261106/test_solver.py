"""Small consistent general-U controls; no fresh study generation or execution."""
import json
from copy import deepcopy
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import affine_solver as solver
from check_solver import check

def fixture(r=101):return dict(p=101,r=r,a=2,b=3,P=[1,39],software_control=True)
def case(w,nt,M,B,U,z,q):
 r=101
 return dict(width=w,target_count=nt,modulus=r,source=[(v,sum(a*b for a,b in zip(v,z,strict=True))%r) for v in M],target=[dict(vector=v,outside=u,rhs=(sum(a*b for a,b in zip(v,z,strict=True))+sum(a*b for a,b in zip(u,q,strict=True)))%r) for v,u in zip(B,U,strict=True)],targets=[])
def cases():
 yield case(2,2,[[1,0]],[[0,1],[0,2],[1,0]],[[99,0],[98,0],[0,100]],[3,8],[7,11])
 yield case(1,2,[],[[0],[0]],[[1,1],[100,100]],[5],[7,11])
 yield case(0,2,[],[[],[]],[[2,0],[1,1]],[],[7,11])
 yield case(2,3,[],[],[],[3,8],[7,11,13])
 yield case(1,2,[[1]],[[1],[0],[0]],[[0,2],[1,1],[0,0]],[5],[7,11])
 yield case(0,0,[[]],[[]],[[]],[],[])
 yield case(2,2,[],[[1,0],[0,1]],[[100,0],[0,100]],[3,8],[7,11])
def solve(c):return [solver.solve(c,arm,solver.Meter(fixture(c['modulus']))) for arm in ('sparse_joint','sparse_cancel')]
@pytest.mark.parametrize('c',list(cases()))
def test_general_u_dense_and_json_controls(c):
 result=solve(c);assert check(c,json.loads(json.dumps(result)))['checked']
 assert all(v['system']['kernel_computed']is False for v in result)
@pytest.mark.parametrize('change',['outside_weight','cancel_rhs','lift','outside_rank','negative','residual','missing','phase'])
def test_false_general_certificates_refuse(change):
 c=list(cases())[0];result=solve(c)
 if change=='outside_weight':result[1]['cancellations'][0]['original_target_weights'][0][1]+=1
 elif change=='cancel_rhs':result[1]['cancellations'][0]['rhs']+=1
 elif change=='lift':result[1]['recoveries'][0]['original_row_weights'][0]+=1
 elif change=='outside_rank':result[1]['outside']['rank']+=1
 elif change=='negative':result[0]['recoveries'][0]['identifiable']=False
 elif change=='residual':result[1]['recoveries'][0]['residual'][0]=1
 elif change=='missing':result[0]['recoveries'].pop()
 elif change=='phase':result[1]['counters']['Fr.field_mul']+=1
 with pytest.raises(ValueError):check(c,result)
def test_correlated_targets_do_not_fabricate_individual_logs():
 c=list(cases())[1];out=solve(c);assert check(c,out)['outside_rank']==1
 assert not any(v['identifiable'] for a in out for v in a['recoveries'])
def test_unit_beta_singleton_matches_old_kernel_free_methods():
 c=case(2,2,[[1,0]],[[0,1],[0,2],[1,0]],[[100,0],[100,0],[0,100]],[3,8],[7,11]);result=solve(c)
 oldcase=deepcopy(c)
 for row in oldcase['target']:
  row['target_index']=next(i for i,x in enumerate(row.pop('outside')) if x)
 for arm,new in zip(('sparse_joint','sparse_cancel'),result,strict=True):
  old=solver.parent.solve(oldcase,arm,solver.parent.Meter(fixture()))
  assert [(v['identifiable'],v['scalar']) for v in old['recoveries']]==[(v['identifiable'],v['scalar']) for v in new['recoveries']]
def test_inconsistent_and_malformed_rows_refuse():
 c=case(1,1,[[0]],[],[],[3],[7]);c['source'][0]=(c['source'][0][0],1)
 for arm in ('sparse_joint','sparse_cancel'):
  with pytest.raises(ValueError,match='inconsistent'):solver.solve(c,arm,solver.Meter(fixture()))
 c=case(1,1,[],[[1]],[[100]],[3],[7]);c['target'][0]['outside']=[]
 with pytest.raises(ValueError,match='encoding'):solver.solve(c,'sparse_joint',solver.Meter(fixture()))

def test_unit_sign_pivot_shortcuts_keep_old_canonical_certificates():
 c=list(cases())[0]
 for arm in ('sparse_joint','sparse_cancel'):
  first=solver.solve(c,arm,solver.Meter(fixture()));second=solver.solve(c,arm,solver.Meter(fixture()))
  assert first['counters']==second['counters']
  assert first['recoveries']==second['recoveries'] and first['system']==second['system']
 m=solver.Meter(fixture());new=solver.KernelFreeSystem(2,m);old=solver.parent.KernelFreeSystem(2,solver.parent.Meter(fixture()))
 for vector,b in [([100,0],5),([1,1],8),([0,2],26)]:
  # Use a consistent span: -z0=5, z0+z1=8 => z1=13.
  new.add(vector,b);old.add(vector,b)
 assert new.summary()==old.summary()
 assert m.other['negative_unit_pivot_shortcuts'] and m.other['unit_pivot_shortcuts']
