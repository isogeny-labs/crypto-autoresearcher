"""Metadata/refusal/cost-binding controls; no native mathematical execution."""
from copy import deepcopy
from pathlib import Path
import json,subprocess,sys
import pytest
from deps16 import commitment
import driver16,analyze16,prepare16,custody16


def test_exact_native_protocol_metadata_without_generation():
    r=custody16.load(custody16.INPUTS);custody16.validate_rules(r)
    p=prepare16.make_protocol(custody16.git('rev-parse','HEAD'))
    assert custody16.tools().schema_errors(p,'experiment.protocol/v1')==[]
    assert custody16.tools().lint_protocol(p,custody16.HERE)==[]
    assert p['sample_size']['instances']==1260
    assert len(p['randomization']['seed_derivation']['seeds'])==2520
    assert p['freeze']['status']=='draft'
    assert p['extensions']['cache_gates']=={'8':176,'24':560}


@pytest.mark.parametrize('change',[('closed_curve_checkpoint',False),('domain','old-domain'),
    ('max_retained_rows',8192),('target_horizons',[8,25]),('sources',256),('target_queries_per_point',24)])
def test_fixed_native_contract_refuses_mutation(change):
    r=custody16.load(custody16.INPUTS);r[change[0]]=change[1]
    with pytest.raises(ValueError):custody16.validate_rules(r)


def test_normal_admission_refusal_precedes_generation_or_output(tmp_path,monkeypatch):
    generated=[]
    def refuse(*args):raise ValueError('normal admission refused')
    monkeypatch.setattr(driver16,'admit',refuse)
    monkeypatch.setattr(driver16.core,'generate',lambda *args:generated.append(args))
    monkeypatch.setattr(sys,'argv',['driver16','--inputs','absent','--protocol','absent','--release','absent','--out',str(tmp_path/'refused')])
    with pytest.raises(ValueError,match='admission refused'):driver16.main()
    assert generated==[] and not (tmp_path/'refused').exists()


def test_complete_output_counter_hash_and_phase_conservation():
    value=dict(counters={'Fp.field_mul':4},phases=[dict(phase='test',status='complete',wall_valid=False,counters={'Fp.field_mul':4})])
    check=dict(verification=dict(checked=True,producer_output_sha256=commitment(value)))
    assert analyze16.bound(value,check) and analyze16.phase_binding(value)
    changed=deepcopy(value);changed['counters']['Fp.field_mul']=5
    with pytest.raises(ValueError):analyze16.bound(changed,check)
    with pytest.raises(ValueError):analyze16.phase_binding(changed)
    changed=deepcopy(value);changed['counters']['Fp.field_mul']=True
    with pytest.raises(ValueError):analyze16.phase_binding(changed)
    assert analyze16.bound(value,None)is False


def test_missing_attempt_artifacts_remain_unknown_without_new_math(tmp_path):
    r=custody16.load(custody16.INPUTS)
    e=dict(returncode=1,timeout=False,exception=None,source_unchanged_after=True)
    observed=analyze16.summarize(tmp_path,r,e)
    assert observed['panel_complete']is False and len(observed['cells'])==1260
    assert not any(v['verified'] or v['certificate_checked'] for v in observed['cells'])
    assert observed['cold_views']==[] and observed['observed_completed_solver_calls']==0
    assert len(observed['errors'])>=5 # admission/start + four missing checkpoints


def test_supervisor_cli_bootstraps_dependency_closure():
    p=subprocess.run([sys.executable,str(custody16.HERE/'supervise16.py'),'--help'],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert '--release' in p.stdout and '--owner' in p.stdout
