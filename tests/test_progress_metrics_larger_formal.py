"""A22 committed-only exporter binds cancelled information, targets and costs."""
import contextlib,copy,hashlib,importlib.util,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('formal_pair_progress',ROOT/'tools/progress_metrics.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
RUN='research/prime_field_a22_execution_20261107/runs/a22-larger-formal-ddbe8b'
METRICS=RUN+'/metrics.json';EXEC=RUN+'/execution.json';ANALYSIS=RUN+'/analysis.json'


def read(ref):
    out=io.StringIO()
    with contextlib.redirect_stdout(out):M.prime_field_larger_formal_transfer_panel(ref,'2026-11-07')
    return [json.loads(v)for v in out.getvalue().splitlines()]


def test_committed_native_snapshot_and_coordinated_corruptions(tmp_path,monkeypatch):
    ids=['p'+str(p)+'-i'+str(i)for p in (1048573,2097143)for i in (0,1)]
    paths=[METRICS,EXEC,ANALYSIS,*[RUN+'/checkpoint-'+cid+'.json'for cid in ids],
        *[RUN+'/raw/'+cid+'.'+program+'.'+name+'.json'for cid in ids for program in ('norm32','unknown16','formalpair16','known16')
          for name in ('information-check','aux_cancel_joint-check','sparse_joint-check','case-check','aux_cancel_joint','expanded-check')],
        *[RUN+'/raw/'+cid+'.formalpair16.'+suffix+'.json'for cid in ids for suffix in ('direct_formal','direct_formal-check')]]
    data={p:json.loads(subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT))for p in paths}
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    def commit(values):
        # The fixture reserializes JSON. Rebind only that metadata byte hash;
        # all independent rank/native/endpoint receipts stay as supplied.
        values=copy.deepcopy(values)
        values[ANALYSIS]['metrics_sha256']=hashlib.sha256(json.dumps(values[METRICS]).encode()).hexdigest()
        for path,value in values.items():
            p=tmp_path/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
        git('add','.');git('commit','-qm','explicit software archive snapshot');return git('rev-parse','HEAD')
    first=commit(data);observed=read(first)
    assert len(observed)==943 and all(v['source']==METRICS+'@'+first and v['better']=='neutral'for v in observed)
    (tmp_path/METRICS).write_text('{}');assert read(first)==observed
    def row(values,index,key,value):values[METRICS]['rows'][index][values[METRICS]['columns'].index(key)]=value
    def coordinated_delta(values):
        for key in ('full_delta','base_rank_after','collected_after_K','cross_row_gain','target_marginal_delta'):
            j=values[METRICS]['columns'].index(key);values[METRICS]['rows'][7][j]+=1
    prefix=RUN+'/raw/p2097143-i0.unknown16.'
    mutations=[lambda v:v[METRICS].update(physical_attempts=True),lambda v:v[METRICS].update(unknown_systems=False),
        lambda v:v[METRICS].update(planned_systems=4),lambda v:v[METRICS].update(observed_completed_batch_calls=12),
        lambda v:v[METRICS].update(unknown_systems=1),lambda v:v[METRICS].update(partial_work_unknown=True),
        lambda v:row(v,0,'case_id',False),lambda v:row(v,1,'auxiliary_slots',0),lambda v:row(v,0,'native_columns',48),
        lambda v:row(v,1,'identified_mask',256),lambda v:row(v,1,'identified_targets',5),lambda v:row(v,7,'full_delta',28),
        lambda v:row(v,7,'outside_rank',25),lambda v:row(v,7,'geometric_queries',65),lambda v:row(v,7,'supplied_K_delta',2),
        lambda v:row(v,7,'direct_base_gain',99),coordinated_delta,
        lambda v:v[EXEC].update(source_unchanged_after=False),lambda v:v[EXEC].update(source_commit='0'*40),
        lambda v:v[RUN+'/checkpoint-p1048573-i0.json'].update(checked_batch_solver_calls=3),
        lambda v:v[prefix+'information-check.json']['verification']['views']['full']['total'].update(delta=99),
        lambda v:v[prefix+'aux_cancel_joint-check.json']['verification'].update(identified=0),
        lambda v:v[prefix+'case-check.json']['verification'].update(prepared_sha256='0'*64),
        lambda v:v[prefix+'aux_cancel_joint.json']['recoveries'][0].update(identifiable=False),
        lambda v:v[ANALYSIS]['checked_query_engine_totals']['scalar'].update({'Fp.group_add':0}),
        lambda v:v[METRICS]['physical_counters']['p2097143-i0.unknown16.native_collection'].update({'Fp.field_mul':-1})]
    formal=RUN+'/raw/p1048573-i0.formalpair16.expanded-check.json'
    mutations.extend([lambda v:row(v,2,'formal_definition_rows',0),lambda v:row(v,2,'definition_only_delta',False),
        lambda v:row(v,0,'expanded_old_joint_rank',0),lambda v:v[formal]['verification'].update(applicable=False),
        lambda v:v[formal]['verification'].update(expanded_joint_rank=0),lambda v:v[formal]['verification'].update(accepted_definitions_public_checked=15),
        lambda v:v[formal]['verification'].update(definition_only_old_base_delta=1)])
    direct=RUN+'/raw/p1048573-i0.formalpair16.'
    mutations.extend([lambda v:row(v,2,'direct_identified_targets',0),lambda v:row(v,2,'direct_fr_mul',-1),
        lambda v:row(v,0,'direct_identified_mask',0),lambda v:v[direct+'direct_formal-check.json']['verification'].update(native_joint_rank=0),
        lambda v:v[direct+'direct_formal.json']['counters'].update({'Fr.field_mul':0}),
        lambda v:v[ANALYSIS]['direct_cold_views'][0]['components'].update(auxiliary_construction={}),
        lambda v:v[ANALYSIS]['direct_cold_views'][0]['single_engine_counters']['batch'].update({'Fp.field_mul':0})])
    for mutation in mutations:
        changed=copy.deepcopy(data);mutation(changed);assert read(commit(changed))==[]
    assert read(first)==observed
