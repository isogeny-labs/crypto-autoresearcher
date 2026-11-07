"""A17 committed metrics refuse grid, cost, proof-census and checkpoint inflation."""
import contextlib,copy,importlib.util,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('certified_query_metrics',ROOT/'tools/progress_metrics.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
RUN='research/prime_field_a17_execution_20261107/runs/a17-certified-query-178e0d'
METRICS=RUN+'/metrics.json';EXEC=RUN+'/execution.json'


def read(ref):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):M.prime_field_certified_query_panel(ref,'2026-11-07')
    return [json.loads(v) for v in out.getvalue().splitlines()]


def test_committed_native_snapshot_and_corruptions(tmp_path,monkeypatch):
    paths=[METRICS,EXEC,*[RUN+'/checkpoint-p'+str(p)+'-i'+str(i)+'.json' for p in (262139,524287) for i in (0,1)]]
    data={p:json.loads(subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT)) for p in paths}
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    def commit(values):
        for path,value in values.items():
            p=tmp_path/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
        git('add','.');git('commit','-qm','explicit software archive snapshot');return git('rev-parse','HEAD')
    first=commit(data);observed=read(first)
    assert len(observed)==304 and all(v['source']==METRICS+'@'+first and v['better']=='neutral' for v in observed)
    (tmp_path/METRICS).write_text('{}');assert read(first)==observed
    def row(values,index,key,value):values[METRICS]['rows'][index][values[METRICS]['columns'].index(key)]=value
    prefix='p262139-i0.suppress.'
    mutations=[lambda v:v[METRICS].update(planned_systems=4),lambda v:v[METRICS].update(observed_completed_batch_solver_calls=16),
        lambda v:v[METRICS].update(verified_export_execution_rows=12),lambda v:v[METRICS].update(observed_online_starts=8),
        lambda v:row(v,0,'case_id',False),lambda v:row(v,0,'certified_targets',7),lambda v:row(v,1,'skipped_slots',1),
        lambda v:row(v,0,'geometric_queries',193),lambda v:row(v,0,'native_columns',32),lambda v:row(v,0,'base_columns',48),
        lambda v:row(v,0,'formal_endpoints',8),lambda v:row(v,0,'identified_mask',256),lambda v:row(v,0,'omitted_reference_rows',0),
        lambda v:v[METRICS]['physical_counters'][prefix+'known_base_construction'].update(public_base_certificates_verified=0),
        lambda v:v[METRICS]['physical_counters'][prefix+'native_collection'].update(pair_array_allocated_bytes=0),
        lambda v:v[METRICS]['physical_counters'][prefix+'construction'].update(fully_preconstructed_endpoint_slots=191),
        lambda v:v[METRICS]['physical_counters'][prefix+'shared_target_queries'].update(logical_target_requests=192),
        lambda v:v[METRICS]['query_engine_totals']['scalar'].update({'Fp.group_add':0}),
        lambda v:v[RUN+'/checkpoint-p262139-i0.json'].update(returncode=1),
        lambda v:v[RUN+'/checkpoint-p262139-i0.json'].update(checked_batch_solver_calls=4),
        lambda v:v[EXEC].update(source_unchanged_after=False),lambda v:v[EXEC].update(source_commit='0'*40),
        lambda v:v[METRICS].update(unknown_systems=1)]
    for mutation in mutations:
        changed=copy.deepcopy(data);mutation(changed);assert read(commit(changed))==[]
    assert read(first)==observed
