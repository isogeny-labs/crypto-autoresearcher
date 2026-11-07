"""Marked p211 component and explicit mocked-I/O transfer controls; native0."""
from copy import deepcopy
from datetime import datetime,timedelta
from pathlib import Path
import json,shutil,sys
import pytest
from deps18 import commitment
import custody18,prepare18,analyze18,check_query18,driver18
from test_preconstruct17 import toy
from test_query17 import special_fixture,completed
from deps17 import checks16
import test_controller17


def test_fixed_rules_fields_exclusions_caps_and_no_boolean_retagging():
    value=custody18.load(custody18.INPUTS);custody18.validate_rules(value)
    assert [v['bits'] for v in value['fields']]==[20,21] and len(value['excluded_curves'])==36
    assert value['public_base_sizes']==[48] and value['maximum_target_cache_points']==192
    changed=deepcopy(value);changed['targets']=True
    with pytest.raises(ValueError,match='rules'):custody18.validate_rules(changed)
    changed=deepcopy(value);changed['fields'][0]['p']=262139
    with pytest.raises(ValueError,match='rules'):custody18.validate_rules(changed)
    assert len(custody18.SOURCES)==168 and len(custody18.BUDGET_INPUTS)==9


def test_prospective_protocol_grid_attribution_and_remaining_old_window():
    p=prepare18.make_protocol('0'*40);t=custody18.tools()
    assert not t.schema_errors(p,'experiment.protocol/v1') and not t.lint_protocol(p,custody18.HERE)
    assert p['sample_size']['instances']==4 and len(p['randomization']['seed_derivation']['seeds'])==16
    assert {'construction_mask','natural_mask','extra_mask','construction_target_rank'}<={v['id'] for v in p['metrics']['primary']}
    original=custody18.load(custody18.BUDGET_INPUTS[0]);budget=prepare18.remaining_budget(datetime.fromisoformat(original['issued_utc'])+timedelta(seconds=7200))
    assert budget['absolute_deadline']==original['absolute_deadline'] and budget['known_prior_cpu_seconds']>697
    assert budget['watchdog_seconds']<14400


def test_existing_causal_check_retains_actual_prefix_rank_diagnostics(toy):
    p,c,recipe,r,_=special_fixture(toy,'suppress');result,cloud,cache,events=completed(p,c,recipe,r,'suppress')
    _,oracle=checks16.collection(p,r,c);proof=check_query18.check(p,c,cloud,cache,result,events,r,'suppress',oracle)
    scans=proof['prefix_diagnostics'];assert scans[0]['target_column_rank']==0 and scans[-1]['target_column_rank']==1
    assert scans[0]['identified_mask']==0 and scans[-1]['identified_mask']==1
    assert all(v['not_target_solver'] and v['namespace']=='independent_prefix_rank_diagnostic' for v in scans)
    import check_query17
    old=check_query17.check(p,c,cloud,cache,result,events,r,'suppress',oracle)
    assert {k:v for k,v in proof.items() if k!='prefix_diagnostics'}==old


@pytest.fixture(scope='module')
def software_archive18(tmp_path_factory,toy):
    # Reuse the already explicit mocked generation/base/prelude/S3 I/O fixture;
    # its actual p211 queries/constructors/causal/native rows use the new checker.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(test_controller17.check_query17,'check',check_query18.check)
        return test_controller17.software_archive.__wrapped__(tmp_path_factory,toy)


@pytest.mark.parametrize('complete',[True,False])
def test_actual_transfer_export_schema_shared_seeds_origins_and_unknowns(tmp_path,software_archive18,monkeypatch,complete):
    source,rules,execution=software_archive18;run=tmp_path/'software-run'
    if complete:shutil.copytree(source,run)
    else:run.mkdir();execution=dict(execution,returncode=1)
    protocol=prepare18.make_protocol('0'*40);path=tmp_path/'software-only.protocol.json';test_controller17.write(path,protocol)
    t=custody18.tools();t.freeze(path,'0'*40,True);protocol=json.loads(path.read_text());interpreter=protocol['arms'][0]['instrument']['binary_sha256']
    execution=dict(execution,source_commit='0'*40,observed_git_head='0'*40,protocol_sha256=protocol['freeze']['protocol_sha256'],started_at='2026-11-07T00:00:00+00:00',finished_at='2026-11-07T00:00:01+00:00',owner='explicit-software-fixture')
    test_controller17.write(run/'execution.json',execution)
    test_controller17.write(run/'host.json',dict(cpu_model='explicit software fixture',logical_cpus=1,memory_bytes=2147483648,kernel='software',hypervisor=None,isolation_tier_max=None,git_dirty=True,executable_sha256=interpreter))
    inputs=tmp_path/'software-only.inputs.json';test_controller17.write(inputs,rules);monkeypatch.setattr(analyze18,'INPUTS',inputs)
    monkeypatch.setattr(sys,'argv',['analyze18','--run',str(run),'--protocol',str(path)]);analyze18.main()
    export=json.loads((run/'export.json').read_text());metrics=json.loads((run/'metrics.json').read_text())
    assert len(export['runs'])==16 and not t.schema_errors(export,'experiment.export/v1') and not t.lint_export(export,protocol,run,True)
    assert metrics['schema']=='prime-field-a18-metrics/v1'
    rows=[dict(zip(metrics['columns'],v,strict=True)) for v in metrics['rows']]
    if complete:
        for row in rows:
            if row['program']=='suppress':
                assert row['construction_mask']==0 and row['natural_mask']==0 and row['extra_mask']==1
                assert row['construction_certified']+row['natural_certified']+row['extra_certified']==row['identified_targets']
            else:assert row['construction_mask']is None
    else:assert all(not row['verified'] and row['construction_mask']is None for row in rows)


def test_transfer_driver_refuses_before_any_generation(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['driver18','--inputs',str(tmp_path/'i'),'--protocol',str(tmp_path/'p'),'--release',str(tmp_path/'r'),'--out',str(tmp_path/'raw')])
    def refused(*args):raise ValueError('marked software admission refusal')
    monkeypatch.setattr(driver18,'admit',refused)
    def forbidden(*args):raise AssertionError('native generation before admission')
    monkeypatch.setattr(driver18.core,'generate',forbidden)
    with pytest.raises(ValueError,match='admission refusal'):driver18.main()
    assert not(tmp_path/'raw').exists()


def test_truncated_journal_retains_complete_paid_prefix_and_marks_unknown(tmp_path):
    raw=tmp_path/'raw';raw.mkdir()
    event=dict(kind='affine_phase',context=dict(kind='query_scheduling'),phase=dict(counters={'paid_prefix':7}))
    (raw/'p211-i0.suppress.events.jsonl').write_text(json.dumps(event)+'\n'+ '{explicit_truncated_software_tail')
    rules=dict(software_control=True,fields=[dict(p=211)],curves_per_field=4,targets=1)
    execution=dict(returncode=1,timeout=False,exception=None,source_unchanged_after=True)
    data=analyze18.summarize(tmp_path,rules,execution)
    assert not data['panel_complete'] and all(not v['verified'] for v in data['cells'])
    assert data['physical_counters']['p211-i0.suppress.query_scheduling']['paid_prefix']==7
    assert any(v.get('paid_prefix_retained') for v in data['errors'])


def test_marked_p101_general_sqrt_branch_against_enumerated_squares():
    from deps18 import core
    field=core.old.Field(101);expected={}
    for y in range(101):expected.setdefault(y*y%101,[]).append(y)
    for x in range(101):assert field.sqrt(x)==(min(expected[x]) if x in expected else None)
    assert field.counts['sqrt_calls']==101 and field.counts['modular_pow']>101
