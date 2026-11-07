"""Explicit correlated/empty p211 row fixtures; not native holdouts."""
from copy import deepcopy
import pytest
from deps22 import solver,check_source
from test_formal20 import tiny
import followup_functionals as F


def fixture(tiny,rows=True):
    original,_=tiny;f=deepcopy(original['fixture']);r=f['r'];P=tuple(f['P']);mul=lambda k:check_source.old.multiply(f['p'],0,f['a'],k%r,P)
    f['factor_base']=[dict(point=list(mul(3)))]
    targets=[dict(index=i,point=list(mul(3+i)))for i in range(8)]
    equations=[]
    if rows:
        for i in range(8):
            outside=[0]*8;outside[i]=r-1;equations.append(dict(vector=[1],outside=outside,rhs=-i%r))
    return dict(width=1,target_count=8,modulus=r,source=[],target=equations,targets=targets),f


@pytest.mark.parametrize('rows',[True,False])
def test_differences_without_units_and_explicit_no_supplied_information(tiny,rows):
    case,f=fixture(tiny,rows);out=F.solve(case,f,solver.Meter(f));proof=F.check(case,f,out)
    assert proof['unit_identified']==0 and proof['difference_identified']==(28 if rows else 0)
    assert out['system']['rank']<out['system']['columns']and len(out['recoveries'])==36
    assert out['counters']['functional_public_point_terms']==64


@pytest.mark.parametrize('change',['weight','query','point','census'])
def test_general_certificate_and_functional_census_corruption(tiny,change):
    case,f=fixture(tiny);out=F.solve(case,f,solver.Meter(f));out=deepcopy(out)
    if change=='weight':out['recoveries'][8]['original_row_weights'][0]=(out['recoveries'][8]['original_row_weights'][0]+1)%case['modulus']
    elif change=='query':out['recoveries'][8]['coefficients'][0]=0
    elif change=='point':out['recoveries'][8]['public_point']=(0,0)
    else:out['target_unknowns']=36
    with pytest.raises(ValueError):F.check(case,f,out)


def test_native_followup_cannot_run_without_new_admission_contract(tiny):
    case,f=fixture(tiny);f['p']=1048573;meter=solver.Meter(f)
    with pytest.raises(ValueError,match='native admission contract'):F.solve(case,f,meter)
    assert not meter.phases
