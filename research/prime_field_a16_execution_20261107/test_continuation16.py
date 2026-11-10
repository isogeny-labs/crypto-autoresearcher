"""Marked software-only wrapper fixtures; no real admission/checkpoint/native execution."""
import copy,hashlib,importlib.util,json,os,sys
from pathlib import Path
import pytest

SPEC=importlib.util.spec_from_file_location('launch_fixture',Path(__file__).with_name('launch_continuation16.py'))
L=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(L)


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    root=tmp_path;here=root/'research/a16';prior=here/'prior';prior.mkdir(parents=True)
    charged=9.066162;old=dict(returncode=1,release_sha256='a'*64,cpu_user_seconds=5.,cpu_sys_seconds=4.,supervisor_cpu_user_seconds=.066162,supervisor_cpu_sys_seconds=0.)
    (prior/'execution.json').write_text(json.dumps(old));(root/'.resume').mkdir();(root/'.resume'/('a16-attempt-'+'a'*64+'.json')).write_text('{}')
    budget=dict(additional_attempts=1,automatic_retries=0,new_paid_capacity=False,memory_bytes=2147483648,original_deadline='2099-01-01T00:00:00+00:00',total_attempts_including_failed_admission=2,prior_attempt='research/a16/prior',prior_release_sha256='a'*64,prior_cpu_seconds=charged,remaining_cpu_seconds=21590,git_config={'core.packedGitWindowSize':'32m','core.packedGitLimit':'128m'})
    value=dict(infrastructure_continuation=budget,memory_bytes=2147483648,absolute_deadline=budget['original_deadline'],watchdog_seconds=21590,max_attempts=1,interpreter_sha256=hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest())
    release=here/'release.json';release.write_text(json.dumps(value));calls=[]
    monkeypatch.setattr(L,'HERE',here);monkeypatch.setattr(L,'ROOT',root);monkeypatch.setattr(sys,'argv',['fixture','--release',str(release),'--protocol','software-only','--out','software-only','--owner','software-only'])
    def output(argv,**kwargs):
        calls.append(argv)
        return budget['git_config'][argv[-1]]+'\n' if argv[:3]==['git','config','--get'] else release.read_bytes()
    monkeypatch.setattr(L.subprocess,'check_output',output)
    monkeypatch.setattr(L.os,'execve',lambda *args:calls.append(('mocked_execve',args)))
    return value,release,calls


def test_preserves_inherited_config_and_normal_supervisor(fixture,monkeypatch):
    value,path,calls=fixture
    monkeypatch.setenv('GIT_CONFIG_COUNT','1');monkeypatch.setenv('GIT_CONFIG_KEY_0','fixture.retained');monkeypatch.setenv('GIT_CONFIG_VALUE_0','software-placeholder')
    L.main();kind,args=calls[-1];assert kind=='mocked_execve'
    executable,argv,env=args
    assert argv[2].endswith('supervise16.py') and env['GIT_CONFIG_COUNT']=='3'
    assert env['GIT_CONFIG_KEY_0']=='fixture.retained' and env['GIT_CONFIG_VALUE_0']=='software-placeholder'
    assert env['GIT_CONFIG_KEY_1']=='core.packedGitWindowSize' and env['GIT_CONFIG_VALUE_1']=='32m'
    assert env['GIT_CONFIG_KEY_2']=='core.packedGitLimit' and env['GIT_CONFIG_VALUE_2']=='128m'


@pytest.mark.parametrize('mutate',[
    lambda v:v.update(memory_bytes=4294967296),lambda v:v.update(watchdog_seconds=21600),
    lambda v:v.update(absolute_deadline='2099-02-01T00:00:00+00:00'),lambda v:v.update(max_attempts=2),
    lambda v:v['infrastructure_continuation'].update(prior_cpu_seconds=0.),lambda v:v['infrastructure_continuation'].update(automatic_retries=1),
    lambda v:v['infrastructure_continuation'].update(new_paid_capacity=True),lambda v:v['infrastructure_continuation']['git_config'].update({'core.packedGitLimit':'4g'})])
def test_budget_and_mapping_mutations_refused_before_execution(fixture,mutate):
    value,path,calls=fixture;mutate(value);path.write_text(json.dumps(value))
    with pytest.raises(ValueError):L.main()
    assert not any(v[0]=='mocked_execve' for v in calls)
