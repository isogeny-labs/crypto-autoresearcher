"""Committed A15 export rejects incomplete/corrupted component counter custody."""
import contextlib,copy,importlib.util,io,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pair_metrics',ROOT/'tools/progress_metrics.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
PATH='research/prime_field_a15_execution_20261107/runs/a15-batched-pairs-06ab77/metrics.json'


def read(ref,since='2026-11-07'):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):M.prime_field_batched_pair_panel(ref,since)
    return [json.loads(v) for v in out.getvalue().splitlines()]


def test_actual_committed_snapshot_and_corruption(tmp_path,monkeypatch):
    data=json.loads(subprocess.check_output(['git','show','HEAD:'+PATH],cwd=ROOT))
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path=tmp_path/PATH;path.parent.mkdir(parents=True)
    def commit(value):
        path.write_text(json.dumps(value));git('add',PATH);git('commit','-qm','software snapshot');return git('rev-parse','HEAD')
    first=commit(data);observed=read(first)
    assert len(observed)==964
    assert len({v['metric'] for v in observed})==964
    assert all(v['source']==PATH+'@'+first and v['better']=='neutral' for v in observed)
    path.write_text('{}');assert read(first)==observed
    assert read(first,'2026-11-08')==[]
    mutations=[lambda v:v['rows'].pop(),lambda v:v.update(new_target_solver_calls=1),
        lambda v:v.update(conditioned_input_reuse=False),lambda v:v.update(independent_new_target_draws=32),
        lambda v:v.update(verified_builds=31),lambda v:v.update(partial_work_unknown=True),
        lambda v:v['rows'][0].update(queries=1),lambda v:v['rows'][0].update(method='batched'),
        lambda v:v['rows'][0]['build']['counters'].update({'Fp.field_mul':True}),
        lambda v:v['rows'][0]['build'].update(ordered_pairs=1),
        lambda v:v['rows'][0]['build'].update(pairs_sha256='f'*64),
        lambda v:v['rows'][0]['build']['phases'][0].update(status='failed'),
        lambda v:v['rows'][0]['observed_phase_counters'].update({'Fp.field_mul':1}),
        lambda v:v['physical_counters'].update({'Fp.field_mul':1}),
        lambda v:v['checkpoints'][0].update(closed_curve='p524287-i1'),
        lambda v:v['checkpoints'][0].update(completed_tables=8),lambda v:v['checkpoints'][0].update(returncode=1)]
    for mutate in mutations:
        altered=copy.deepcopy(data);mutate(altered);assert read(commit(altered))==[]
    assert read(first)==observed
