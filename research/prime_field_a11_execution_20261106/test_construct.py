"""Cache-aware construction and general affine knowledge controls on tiny curves."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
import affine_solver as solver
from affine_construct import ScalarModel,model,ScalarCurve,Constructor,select
from affine_registry import Registry

def fixture():
 for b in range(1,50):
  f,_=solver.old.describe(211,1,b,5)
  if f:return f
 raise ValueError('toy fixture')
def independent_model(r,known,scalars,window):
 known=set(known)|{0};calls=0;api=0;tables=[]
 def add(a,b):
  nonlocal calls,api
  api+=1;v=(a+b)%r
  if v not in known:calls+=1;known.add(v)
  return v
 if window and any(v not in known for v in scalars):
  left=r-1;power=1
  while left:
   largest=min(2**window-1,left);digits=[0,power]
   for _ in range(2,largest+1):digits.append(add(digits[-1],power))
   tables.append(digits);left//=2**window
   if left:
    for _ in range(window):power=add(power,power)
 for scalar in scalars:
  if scalar in known:continue
  value=0;k=scalar
  if window:
   i=0
   while k:
    d=k%(2**window)
    if d:value=add(value,tables[i][d])
    k//=2**window;i+=1
  else:
   power=1
   while k:
    if k%2:value=add(value,power)
    power=add(power,power);k//=2
  assert value==scalar
 return dict(window=window,uncached_ec_adds=calls,wrapper_add_calls=api,table_entries=sum(map(len,tables)),known_labels=len(known))
@pytest.mark.parametrize('window',range(9))
def test_independent_scalar_models_and_actual_ec_counts(window):
 f=fixture();r=f['r'];m=solver.Meter(f);P=tuple(f['P']);known={i:m.e.mul(i,P) for i in (1,2,3,5,8)};work=[7,19,31,44,2]
 predicted=model(r,list(known),work,window);assert predicted==independent_model(r,list(known),work,window)
 records=[];curve=ScalarCurve(m,f['p'],r,P,known,lambda *v:records.append(v),'P');start=m.counters();constructor=Constructor(curve,dict(window=window))
 points=[constructor.mul(i) for i in work]
 assert all(q==m.e.mul(i,P) for i,q in zip(work,points,strict=True))
 assert m.other['scalar_uncached_ec_adds']==predicted['uncached_ec_adds']
 assert m.other['scalar_wrapper_add_calls']==predicted['wrapper_add_calls']
def test_affine_coincidence_has_correct_sign_and_identity():
 f=fixture();m=solver.Meter(f);P=tuple(f['P']);Q=m.e.mul(7,P);registry=Registry(f,[dict(index=0,point=list(Q))],m,lambda v:None)
 registry.add(m.e.mul(12,P),12,[0],'public_source')
 registry.add(m.e.mul(12,P),5,[1],'affine_target')
 rows=[v for v in registry.equations if any(v['outside']) and not any(v['coefficients'])]
 assert any((v['outside'][0]*7-v['rhs'])%f['r']==0 for v in rows)
 registry.add(None,f['r']-7,[1],'target_identity')
 assert all((v['rhs']-sum(a*7 for a in v['outside']))%f['r']==0 for v in registry.equations if not any(v['coefficients']))
def test_cross_target_coincidence_never_fabricates_individual_scalar_cache():
 f=fixture();m=solver.Meter(f);P=tuple(f['P']);Q0=m.e.mul(7,P);Q1=m.e.mul(11,P);registry=Registry(f,[dict(index=0,point=list(Q0)),dict(index=1,point=list(Q1))],m,lambda v:None)
 point=m.e.mul(12,P);registry.add(point,5,[1,0],'target0');registry.add(point,1,[0,1],'target1')
 cross=[v for v in registry.equations if all(v['outside']) and not any(v['coefficients'])]
 assert cross and all((v['outside'][0]*7+v['outside'][1]*11-v['rhs'])%f['r']==0 for v in cross)
 assert not hasattr(registry,'known_scalars')
def test_q_basis_coefficients_are_not_p_scalar_labels():
 f=fixture();m=solver.Meter(f);P=tuple(f['P']);Q=m.e.mul(7,P);seen=[]
 curve=ScalarCurve(m,f['p'],f['r'],Q,{1:Q},lambda *v:seen.append(v),'Q0');c=Constructor(curve,select(f['r'],list(curve.known),[2,3,9]))
 assert c.mul(2)==m.e.mul(14,P) and c.mul(2)!=m.e.mul(2,P)
 assert all(v[2]=='Q0' for v in seen)
