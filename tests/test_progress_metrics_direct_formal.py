"""A21 committed-only phase and target metrics bind immutable public inputs."""
import contextlib,copy,hashlib,importlib.util,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('direct_formal_progress',ROOT/'tools/progress_metrics.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
RUN='research/prime_field_a21_execution_20261107/runs/a21-direct-formal-a4de6f'
METRICS=RUN+'/metrics.json';EXEC=RUN+'/execution.json';ANALYSIS=RUN+'/analysis.json'


def read(ref):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):M.prime_field_direct_formal_algebra_panel(ref,'2026-11-07')
    return [json.loads(v)for v in out.getvalue().splitlines()]


def test_committed_phases_inputs_and_corruptions(tmp_path,monkeypatch):
    ids=['p'+str(p)+'-i'+str(i)for p in (262139,524287)for i in (0,1)];methods=('direct_formal','aux_cancel_joint','sparse_joint')
    paths=[METRICS,EXEC,ANALYSIS,*[RUN+'/checkpoint-'+cid+'.json'for cid in ids],*[RUN+'/raw/'+cid+'.complete.json'for cid in ids],
        *[RUN+'/raw/'+cid+'.'+method+suffix+'.json'for cid in ids for method in methods for suffix in ('','-check')]]
    data={p:json.loads(subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT))for p in paths}
    for cid in ids:
        complete=data[RUN+'/raw/'+cid+'.complete.json']
        for binding in complete['descriptor']['producer'].values():data[binding['path']]=subprocess.check_output(['git','show','HEAD:'+binding['path']],cwd=ROOT,text=True)
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    def commit(values):
        values=copy.deepcopy(values);values[ANALYSIS]['metrics_sha256']=hashlib.sha256(json.dumps(values[METRICS]).encode()).hexdigest()
        for path,value in values.items():
            p=tmp_path/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value if isinstance(value,str)else json.dumps(value))
        git('add','.');git('commit','-qm','explicit committed metadata fixture');return git('rev-parse','HEAD')
    first=commit(data);observed=read(first)
    assert len(observed)==411 and all(v['source']==METRICS+'@'+first and v['better']=='neutral'for v in observed)
    (tmp_path/METRICS).write_text('{}');assert read(first)==observed
    def row(values,index,key,value):values[METRICS]['rows'][index][values[METRICS]['columns'].index(key)]=value
    prefix=RUN+'/raw/p262139-i0.direct_formal';complete=RUN+'/raw/p262139-i0.complete.json'
    source=data[complete]['descriptor']['producer']['case']['path']
    mutations=[lambda v:v[METRICS].update(physical_attempts=True),lambda v:v[METRICS].update(unknown_systems=False),
        lambda v:v[METRICS].update(planned_systems=4),lambda v:v[METRICS].update(planned_batch_calls=8),
        lambda v:v[METRICS].update(observed_completed_batch_calls=11),lambda v:v[METRICS].update(panel_complete=False),
        lambda v:row(v,0,'case_id',False),lambda v:row(v,0,'identified_mask',256),lambda v:row(v,0,'identified_targets',7),
        lambda v:row(v,0,'system_columns',56),lambda v:row(v,0,'system_rank',64),lambda v:row(v,0,'fr_mul',0),
        lambda v:row(v,0,'fr_inv',True),lambda v:v[EXEC].update(source_unchanged_after=False),
        lambda v:v[EXEC].update(source_commit='0'*40),lambda v:v[ANALYSIS].update(new_curves=4),
        lambda v:v[RUN+'/checkpoint-p262139-i0.json'].update(checked_batch_solver_calls=2),
        lambda v:v[complete].update(actual_solver_calls=2),lambda v:v[complete].update(historical_outcomes_agree=False),
        lambda v:v[complete]['descriptor']['producer']['case'].update(sha256='0'*64),
        lambda v:v.update({source:v[source]+'\n'}),lambda v:v[prefix+'-check.json']['verification'].update(identified=0),
        lambda v:v[prefix+'-check.json']['verification'].update(prepared_sha256='0'*64),
        lambda v:v[prefix+'-check.json']['verification'].update(native_joint_rank=0),
        lambda v:v[prefix+'.json']['recoveries'][0].update(identifiable=False),
        lambda v:v[prefix+'.json']['counters'].update({'Fr.field_mul':0}),
        lambda v:v[ANALYSIS]['phases'][0].update(method='sparse_joint'),
        lambda v:v[ANALYSIS]['physical_counters'].update({'Fr.field_mul':-1})]
    for mutation in mutations:
        changed=copy.deepcopy(data);mutation(changed);assert read(commit(changed))==[]
    assert read(first)==observed
