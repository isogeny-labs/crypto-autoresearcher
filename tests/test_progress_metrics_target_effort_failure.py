"""Committed A16 failure telemetry cannot invent a target-recovery observation."""
import contextlib,copy,importlib.util,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('a16_failure_progress',ROOT/'tools/progress_metrics.py');M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
PATH='research/prime_field_a16_execution_20261107/runs/a16-target-effort-3d7f9e/metrics.json'


def read(ref):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):M.prime_field_target_effort_admission_failure(ref,'2026-11-07')
    return [json.loads(v) for v in out.getvalue().splitlines()]


def test_actual_committed_failure_and_corruptions(tmp_path,monkeypatch):
    actual=json.loads(subprocess.check_output(['git','show','HEAD:'+PATH],cwd=ROOT))
    def git(*argv):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*argv],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path);path=tmp_path/PATH;path.parent.mkdir(parents=True)
    def commit(v):path.write_text(json.dumps(v));git('add',PATH);git('commit','-qm','software snapshot');return git('rev-parse','HEAD')
    first=commit(actual);observed=read(first)
    assert len(observed)==5 and all(v['better']=='neutral' and v['source']==PATH+'@'+first for v in observed)
    path.write_text('{}');assert read(first)==observed
    mutations=[lambda v:v.update(physical_attempts=True),lambda v:v.update(observed_completed_solver_calls=False),lambda v:v.update(panel_complete=True),lambda v:v.update(unknown_systems=0),lambda v:v.update(observed_completed_solver_calls=1),
        lambda v:v.update(verified_systems=1),lambda v:v['physical_counters'].update({'invented':{'Fp.field_mul':1}}),
        lambda v:v['rows'].pop(),lambda v:v['rows'][0].__setitem__(v['columns'].index('identified_mask'),0),
        lambda v:v['closed_curve_checkpoints'][0].update(valid=True),lambda v:v['query_engine_totals']['scalar'].update({'Fp.group_add':1})]
    for mutate in mutations:
        v=copy.deepcopy(actual);mutate(v);assert read(commit(v))==[]
    assert read(first)==observed
