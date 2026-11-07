"""Outcome verification, failure accounting and artifact replay at campaign scope."""
import copy
import json
from pathlib import Path
import pytest
from orchestration.eval import capability_tasks as tasks
from orchestration.eval import capability_campaign as campaign
from orchestration.eval import capability_actor as actors
from orchestration.eval import capability_report as reports

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def spec():
    return tasks.load(ROOT/'examples/capability-campaign/smoke.json')

@pytest.mark.parametrize('mode,verified,false_success',[('control',True,False),('negative_control',False,True)])
def test_end_to_end(spec,tmp_path,mode,verified,false_success):
    out=tmp_path/'run'
    report=campaign.run(spec,out,mode=mode)
    rows=[json.loads(p.read_text()) for p in out.glob('trial-*/result.json')]
    assert len(rows)==18
    assert all(r['verified']==verified and r['false_success']==false_success for r in rows)
    assert all(r['status']=='software_control_only' for r in report['matrix'])
    assert campaign.replay(out)['trials']==18
    with pytest.raises(FileExistsError): campaign.run(spec,out,mode=mode)

@pytest.mark.parametrize('family',tasks.FAMILIES)
def test_independent_solver_and_rejection(family):
    for seed in range(30):
        public,truth=tasks.instance({'family':family,'difficulty':4},seed)
        assert tasks.grade(actors.reference_answer(public),truth)
        assert not tasks.grade({'fabricated':True},truth)
        assert not tasks.grade(None,truth)
    assert not tasks.grade({'solutions':[True], 'exists':True},{'solutions':[1],'exists':True})

@pytest.mark.parametrize('field,value',[('seed',True),('instances',0),('arms',['single','single']),('tasks',[]),('budget',None)])
def test_reject_bad_spec(spec,field,value):
    spec[field]=value
    with pytest.raises(ValueError): tasks.validate(spec)

def test_matched_schedule_and_split(spec):
    a=campaign.schedule(spec)
    assert a==campaign.schedule(spec)
    assert len({r['seed'] for r in a})==6
    spec['split']='held_out'
    assert {r['seed'] for r in a}.isdisjoint({r['seed'] for r in campaign.schedule(spec)})

def test_failure_retention_and_unknown_usage(spec,tmp_path):
    def fail(*args,**kwargs): raise RuntimeError('backend unavailable')
    report=campaign.run(spec,tmp_path/'failed',mode='live',actor=fail,model='fake')
    assert all(r['attempted_trials']==2 and r['verified_trials']==0 for r in report['matrix'])
    assert all(r['cost_usd'] is None and r['total_tokens'] is None for r in report['matrix'])
    assert campaign.replay(tmp_path/'failed')['verified']

def test_reviewer_claim_is_not_a_grade(spec,tmp_path):
    def actor(stage,public,previous,**kw):
        return actors.scripted(stage,public,previous,corrupt=True)
    result=campaign.run(spec,tmp_path/'wrong',mode='live',actor=actor)
    assert all(r['verified_trials']==0 and r['false_success_trials']==2 for r in result['matrix'])

def test_tamper_and_resealed_inconsistency(spec,tmp_path):
    out=tmp_path/'run';campaign.run(spec,out)
    path=out/'trial-0000/result.json'; row=json.loads(path.read_text());row['answer']={'forged':True}
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='changed artifact'): campaign.replay(out)
    (out/'sha256.json').unlink();campaign.seal(out)
    with pytest.raises(ValueError,match='reconciliation'): campaign.replay(out)

def test_repeats_are_clustered_and_dev_cannot_qualify(spec,tmp_path):
    spec['repeats']=2
    spec['reliability']={'minimum_instances':1,'minimum_success_lower_bound':0,'maximum_false_success_upper_bound':1}
    report=campaign.run(spec,tmp_path/'run',mode='live',actor=lambda s,p,v,**kw: actors.scripted(s,p,v))
    assert all(r['complete_instances']==2 and r['verified_trials']==4 for r in report['matrix'])
    assert all(r['status']=='demonstrated_on_cases' for r in report['matrix'])

def test_request_cap_prevents_launch(spec,monkeypatch):
    def forbidden(*a,**kw): raise AssertionError('process must not launch')
    monkeypatch.setattr(actors.subprocess,'Popen',forbidden)
    public,_=tasks.instance(spec['tasks'][0],5)
    budget={**spec['budget'],'max_request_bytes':1}
    assert actors.codex('execute',public,{},seconds=1,model='fake',effort='xhigh',budget=budget)['status']=='budget_exhausted'

def test_live_export_replays_and_validates(tmp_path):
    from tools import experiment_protocol as ep
    spec=tasks.load(ROOT/'examples/capability-campaign/qualification.json')
    protocol=json.loads((ROOT/'examples/capability-campaign/protocol.json').read_text())
    protocol['freeze']={'status':'draft','protocol_sha256':None,'commit':None,'frozen_at':None,'filed_before_affected_data':False}
    protocol['links']['source_sha256']=tasks.digest(campaign.fingerprint())
    protocol['analysis_plan']['script']={'path':str(ROOT/'orchestration/eval/capability_report.py'), 'sha256':campaign.fingerprint()['orchestration/eval/capability_report.py']}
    path=tmp_path/'protocol.json';path.write_text(json.dumps(protocol))
    ep.freeze(path,None,True)
    binding=campaign.check_protocol(path,spec)
    out=tmp_path/'run'
    campaign.run(spec,out,mode='live',model='test-double',protocol=binding,
                 actor=lambda s,p,v,**kw: actors.scripted(s,p,v))
    export=json.loads((out/'export.json').read_text())
    frozen=json.loads(path.read_text())
    assert not ep.schema_errors(export,'experiment.export/v1')
    assert not ep.lint_export(export,frozen,out,True)
    assert campaign.replay(out)['trials']==6
    frozen['links']['capability_campaign_sha256']='0'*64
    frozen['freeze']['protocol_sha256']=ep.protocol_hash(frozen)
    path.write_text(json.dumps(frozen))
    with pytest.raises(ValueError,match='does not bind'): campaign.check_protocol(path,spec)

def test_cli_routes_capability(spec,tmp_path):
    from orchestration.eval.cli import main
    path=tmp_path/'spec.json';path.write_text(json.dumps(spec))
    assert main(['capability','validate','--spec',str(path)])==0

@pytest.mark.parametrize('bad_tool', [False,True])
def test_native_transport_structured_output(spec,tmp_path,monkeypatch,bad_tool):
    import sys
    import subprocess
    script=tmp_path/'fake_codex.py'
    script.write_text('''import sys,json,pathlib
request=sys.stdin.read()
out=pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1])
out.write_text(json.dumps({'claim_success':True,'artifact_json':'{"answer": 42}'}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':12,'output_tokens':5}}))
''' + ("print(json.dumps({'type':'item.completed','item':{'type':'command_execution'}}))\n" if bad_tool else ''))
    original=subprocess.Popen
    def fake(cmd,**kwargs):
        assert 'features.shell_tool=false' in cmd
        return original([sys.executable,str(script),*cmd[2:]],**kwargs)
    monkeypatch.setattr(actors.subprocess,'Popen',fake)
    result=actors.codex('execute',{'question':'test','answer_shape':{}},{},seconds=5,
                        model='fake',effort='xhigh',budget=spec['budget'])
    assert result['status']==('scope_violation' if bad_tool else 'completed')
    assert result['artifact']=={'answer':42}
    assert result['usage']['output_tokens']==5
    assert result['cost_usd'] is None

def test_output_limit_is_separate_from_native_storage(spec,tmp_path,monkeypatch):
    import sys,subprocess
    script=tmp_path/'fake_codex.py'
    script.write_text("import sys\nsys.stdin.read()\nprint('x'*20000)\n")
    original=subprocess.Popen
    monkeypatch.setattr(actors.subprocess,'Popen',lambda cmd,**kw: original([sys.executable,str(script)],**kw))
    budget={**spec['budget'],'max_output_bytes':1024,'max_actor_file_bytes':1048576}
    result=actors.codex('execute',{}, {},seconds=5,model='fake',effort='xhigh',budget=budget)
    assert result['status']=='budget_exhausted'
    assert len(json.dumps(result['trace']))<2000
