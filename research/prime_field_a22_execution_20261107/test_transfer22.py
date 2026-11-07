"""Marked tiny four-ID archives, mocked metadata; no native transfer pilot."""
from copy import deepcopy
from pathlib import Path
import json,shutil,sys
import pytest
from deps22 import solver,public_verify,commitment,direct21,check21
from test_archive20 import software_archive
import custody22,prepare22,analyze22,driver22


def write(path,value):path.write_text(json.dumps(value)+'\n')


@pytest.fixture(scope='module')
def transfer_archive(software_archive,tmp_path_factory):
    source,rules,execution=software_archive;run=tmp_path_factory.mktemp('a22-marked-repeat')/'run';shutil.copytree(source,run)
    raw=run/'raw'
    for i in range(4):
        cid='p211-i'+str(i);prefix=cid+'.formalpair16.';case=json.loads((raw/(prefix+'case.json')).read_text());prep=json.loads((raw/(prefix+'prelude.json')).read_text())
        # Real additional direct calls on the marked tiny fixture only.
        meter=solver.Meter(prep['cell']['fixture']);result=direct21.solve(case,prep,meter);public_verify(result,case,prep['cell']['fixture'],meter)
        proof=check21.verify(case,prep,result)
        write(raw/(prefix+'direct_formal.json'),result);write(raw/(prefix+'direct_formal-check.json'),dict(verification=proof))
        with (raw/(prefix+'events.jsonl')).open('a')as out:
            out.write(json.dumps(dict(kind='batch_solver_start',execution_arm='direct_on_formalpair16',case_id=4*i+2))+'\n')
            out.write(json.dumps(dict(kind='batch_solver_complete',execution_arm='direct_on_formalpair16',case_id=4*i+2,counters=result['counters']))+'\n')
        for program in custody22.PROGRAMS:
            path=raw/(cid+'.'+program+'.complete.json');value=json.loads(path.read_text());value.update(solver_calls=3 if program=='formalpair16'else 2,direct_checked=program=='formalpair16');write(path,value)
        path=run/('checkpoint-'+cid+'.json');value=json.loads(path.read_text());value['checked_batch_solver_calls']=9*(i+1);write(path,value)
    return run,rules,execution


def test_actual_three_formal_solvers_and_nonadditive_cold_acquisition(transfer_archive):
    run,rules,execution=transfer_archive;data=analyze22.summarize(run,rules,execution)
    assert data['panel_complete']and len(data['cells'])==16 and data['observed_completed_batch_calls']==36
    assert len(data['cold_views'])==16 and len(data['direct_cold_views'])==4 and len(data['observed_algorithm_counters'])==9
    for v in data['direct_cold_views']:
        original=next(x for x in data['cold_views']if(x['cell_id'],x['program'])==(v['cell_id'],v['program']))
        assert {k:x for k,x in original['components'].items()if k!='primary_target_algebra'}=={k:x for k,x in v['components'].items()if k!='primary_target_algebra'}
        assert original['identified_mask']==v['identified_mask']and v['acquisition_shared_with']


@pytest.mark.parametrize('change',['input','output','cost','missing','call_census'])
def test_direct_custody_corruption_refused_or_unknown(transfer_archive,tmp_path,change):
    original,rules,execution=transfer_archive;run=tmp_path/'changed';shutil.copytree(original,run);prefix=run/'raw/p211-i0.formalpair16.'
    if change=='missing':
        Path(str(prefix)+'direct_formal.json').unlink();data=analyze22.summarize(run,rules,execution)
        assert not data['panel_complete']and not data['cells'][2]['verified'];return
    path=Path(str(prefix)+('direct_formal-check.json'if change=='input'else'complete.json'if change=='call_census'else'direct_formal.json'))
    value=json.loads(path.read_text())
    if change=='input':value['verification']['prepared_sha256']='0'*64
    elif change=='call_census':value['solver_calls']=2
    elif change=='output':value['recoveries'][0]['identifiable']=not value['recoveries'][0]['identifiable']
    else:value['counters']['Fr.field_mul']=value['counters'].get('Fr.field_mul',0)+1
    write(path,value)
    with pytest.raises(ValueError):analyze22.summarize(run,rules,execution)


def test_malformed_direct_result_keeps_paid_prefix_and_unknown_case(transfer_archive,tmp_path):
    original,rules,execution=transfer_archive;run=tmp_path/'truncated';shutil.copytree(original,run)
    (run/'raw/p211-i0.formalpair16.direct_formal.json').write_text('{explicit truncated software result')
    value=analyze22.summarize(run,rules,execution)
    assert not value['panel_complete']and not value['cells'][2]['verified']
    assert value['observed_completed_batch_calls']==36 and value['observed_algorithm_counters']['direct_on_formalpair16']
    assert any(v['error_type']=='JSONDecodeError'for v in value['errors'])


@pytest.mark.parametrize('complete',[True,False])
def test_actual_36row_export_including_all_unknowns(transfer_archive,tmp_path,monkeypatch,complete):
    source,rules,execution=transfer_archive;run=tmp_path/'run'
    if complete:shutil.copytree(source,run)
    else:run.mkdir();execution=dict(execution,returncode=1)
    protocol=prepare22.make_protocol('0'*40);path=tmp_path/'explicit-software.protocol.json';write(path,protocol)
    t=custody22.tools();t.freeze(path,'0'*40,True);protocol=json.loads(path.read_text());interpreter=protocol['arms'][0]['instrument']['binary_sha256']
    write(run/'execution.json',dict(execution,source_commit='0'*40,observed_git_head='0'*40,protocol_sha256=protocol['freeze']['protocol_sha256'],started_at='2026-11-07T00:00:00+00:00',finished_at='2026-11-07T00:00:01+00:00',owner='explicit repeated tiny fixture'))
    write(run/'host.json',dict(cpu_model='explicit software fixture',logical_cpus=1,memory_bytes=2147483648,kernel='software',hypervisor=None,isolation_tier_max=None,git_dirty=True,executable_sha256=interpreter))
    inputs=tmp_path/'software.inputs.json';write(inputs,rules);monkeypatch.setattr(analyze22,'INPUTS',inputs)
    monkeypatch.setattr(sys,'argv',['analyze22','--run',str(run),'--protocol',str(path)]);analyze22.main()
    export=json.loads((run/'export.json').read_text());metrics=json.loads((run/'metrics.json').read_text())
    assert len(export['runs'])==36 and len({v['instance_id']for v in export['runs']})==4
    assert not t.schema_errors(export,'experiment.export/v1')and not t.lint_export(export,protocol,run,True)
    assert metrics['verified_systems']==(16 if complete else 0)


def test_exact_prospective_grid_exclusions_budget_and_admission(tmp_path,monkeypatch):
    p=prepare22.make_protocol('0'*40);t=custody22.tools()
    assert not t.schema_errors(p,'experiment.protocol/v1')and not t.lint_protocol(p,custody22.HERE)
    assert len(p['arms'])==9 and len(list(t.seeds_table(p)))==36
    rules=custody22.expected_rules();assert len(rules['excluded_curves'])==48 and [v['p']for v in rules['fields']]==[1048573,2097143]
    assert [v['bits']for v in rules['fields']]==[20,21]
    assert len(custody22.BUDGET_INPUTS)==29
    monkeypatch.setattr(sys,'argv',['driver22','--inputs',str(tmp_path/'i'),'--protocol',str(tmp_path/'p'),'--release',str(tmp_path/'r'),'--out',str(tmp_path/'new-raw')])
    def refuse(*args):raise ValueError('marked admission refusal')
    def forbidden(*args):raise AssertionError('generation before admission')
    monkeypatch.setattr(driver22,'admit',refuse);monkeypatch.setattr(driver22.core,'generate',forbidden)
    with pytest.raises(ValueError,match='admission refusal'):driver22.main()
    assert not(tmp_path/'new-raw').exists()


@pytest.mark.parametrize('change',['missing_bits','boolean_bits','wrong_bits'])
def test_field_configuration_shape_only_refuses_missing_native_metadata(change):
    # This reads declared integers only: no primality, field selection,
    # curve generation, point arithmetic or native-field pilot is called.
    fields=deepcopy(custody22.expected_rules()['fields'])
    custody22.validate_field_metadata(fields)
    if change=='missing_bits':del fields[0]['bits']
    elif change=='boolean_bits':fields[0]['bits']=True
    else:fields[0]['bits']=21
    with pytest.raises(ValueError,match='explicit field bits'):custody22.validate_field_metadata(fields)
