"""A12 committed-only metrics refuse inflated aliases, rank/cost and custody."""
import contextlib,copy,importlib.util,io,json,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location('batch_metrics',Path(__file__).resolve().parents[1]/'tools/progress_metrics.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
PATH='research/prime_field_a12_execution_20261106/runs/a12-batched-holdout-6ba98a/metrics.json'
def fixture():
 rows=[];queries=[];checkpoints=[]
 for p in (262139,524287):
  for i in (0,1):
   cid=f'p{p}-i{i}';queries.append(dict(cell_id=cid,physical_cached_points=8,queries=16*32,logical_requests=2304));checkpoints.append(dict(cell_id=cid,valid=True,receipt=dict(returncode=0,closed_curve=cid)))
   for seed in range(3):
    for kind in ('ap','hash'):
     for sp in (64,128):
      for policy in ('walk','hash_offset','general'):
       for tp in (1,2,4,8):
        for scope in ('relations','anchors'):
         row=dict(case_id=len(rows),cell_id=cid,source_schedule=kind+str(seed),source_prefix=sp,target_policy=policy,target_prefix=tp,scope=scope,verified=True,base_columns=32,source_rank=2,outside_rank=1,delta=1,after_cancellation_rank=3,identified_targets=0,identified_mask=0,source_rows=2,target_rows=2,decomposition_rows=2,knowledge_rows=0,joint_rank=4,joint_columns=40,cancel_rank=3,cancel_columns=32)
         for arm in ('joint','cancel'):
          for k in ('add','sub','mul','inv'):row[arm+'_fr_'+k]=0
         rows.append(row)
 columns=list(rows[0]);return dict(query_engine_totals=dict(scalar={'Fp.group_add':198656},batch={}),schema='prime-field-a12-metrics/v1',panel_complete=True,physical_attempts=1,planned_systems=1152,planned_solver_calls=2304,verified_systems=1152,partial_work_unknown=False,columns=columns,rows=[[r[k] for k in columns] for r in rows],physical_counters=dict(source={'query_scalar.Fp.group_add':198656,**dict(source_queries=196608,pair_table_insertions=7936,target_queries=2048)},target_queries=dict(target_queries=0,logical_target_requests=9216)),query_summary=queries,closed_curve_checkpoints=checkpoints,observed_arm_counters=dict(sparse_joint={},sparse_cancel={}))
def read(ref):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):M.prime_field_batched_holdout_panel(ref,'2026-11-06')
 return [json.loads(s) for s in out.getvalue().splitlines()]
def test_committed_only_complete_affine_scope_and_corruption_refusal(tmp_path,monkeypatch):
 def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
 git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path);p=tmp_path/PATH;p.parent.mkdir(parents=True)
 def commit(d):p.write_text(json.dumps(d));git('add',PATH);git('commit','-qm','software fixture');return git('rev-parse','HEAD')
 d=fixture();first=commit(d);out=read(first);assert len(out)==17295 and all(v['source']==PATH+'@'+first and v['better']=='neutral' for v in out)
 p.write_text('{}');assert read(first)==out
 def row(v,k,value):v['rows'][0][v['columns'].index(k)]=value
 mutations=[lambda v:v['rows'].pop(),lambda v:v.update(panel_complete=False),lambda v:v.update(partial_work_unknown=True),lambda v:v['physical_counters']['source'].update(source_queries=196608*3),lambda v:v['query_summary'][0].update(physical_cached_points=177),lambda v:v['query_summary'][0].update(queries=0),lambda v:v['closed_curve_checkpoints'][0]['receipt'].update(returncode=1),lambda v:row(v,'delta',9),lambda v:row(v,'identified_mask',1),lambda v:row(v,'joint_fr_mul',True),lambda v:v['observed_arm_counters']['sparse_cancel'].update({'Fr.field_mul':1}),lambda v:v['query_engine_totals']['scalar'].update({'Fp.group_add':198657}),lambda v:row(v,'base_columns',31)]
 for mutate in mutations:
  bad=copy.deepcopy(d);mutate(bad);assert read(commit(bad))==[]
 assert read(first)==out
