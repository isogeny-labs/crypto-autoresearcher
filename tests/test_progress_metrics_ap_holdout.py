"""A10 export reads committed measurements and refuses incomplete/inflated scope."""
import contextlib,copy,importlib.util,io,json,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location('ap_metrics',Path(__file__).resolve().parents[1]/'tools/progress_metrics.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
PATH='research/prime_field_a10_execution_20261106/runs/a10-ap-holdout-276654/analysis.json'
def data():
 cells=[];cost=[];index=0
 for p in (8191,65537):
  for i in (0,1):
   for seed in range(3):
    for kind in ('ap','hash'):
     for b in (0,8,16,24,32,48,64,96,128):
      cost.append(dict(cell_id=f'p{p}-i{i}',schedule=kind+str(seed),prefix=b,source_count=b,constructor_counters={'constructor_group_add_calls':b,'Fp.field_mul':b*3}))
      for scope in ('relations','anchors'):
       for arm in ('sparse_joint','sparse_cancel'):
        cells.append(dict(cell_id=f'p{p}-i{i}',schedule=kind+str(seed),prefix=b,scope=scope,arm=arm,instance_id=str(index),verified=True,status='verified',identified_targets=0,identified_indices=[],source_rank=2,delta=1,base_rank_after_cancellation=3,base_columns=16,matrix_rank=4,matrix_columns=24,distinct_equations=4,fr_add=0,fr_sub=10,fr_mul=10,fr_inv=2))
       index+=1
 return dict(panel_complete=True,generation_valid=True,physical_attempts=1,solver_calls_verified=864,partial_work_unknown=False,cells=cells,construction=cost,collection_counters=dict(source_queries=147456,target_queries=1536,pair_table_insertions=4928))
def read(ref):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):M.prime_field_ap_holdout_panel(ref,'2026-11-06')
 return [json.loads(v) for v in out.getvalue().splitlines()]
def test_committed_only_and_scope_corruptions(tmp_path,monkeypatch):
 def git(*a):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*a],text=True).strip()
 git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path);path=tmp_path/PATH;path.parent.mkdir(parents=True)
 def commit(d):path.write_text(json.dumps(d));git('add',PATH);git('commit','-qm','software fixture');return git('rev-parse','HEAD')
 d=data();first=commit(d);out=read(first)
 assert len(out)==7996 and all(v['source']==PATH+'@'+first and v['better']=='neutral' for v in out)
 assert next(v['value'] for v in out if v['metric'].endswith('.physical.source_queries'))==147456
 path.write_text('{}');assert read(first)==out
 mutations=[lambda v:v['cells'].pop(),lambda v:v.update(generation_valid=False),lambda v:v.update(partial_work_unknown=True),lambda v:v['collection_counters'].update(source_queries=147456*9),lambda v:v['cells'][0].update(delta=9),lambda v:v['construction'].pop(),lambda v:v['cells'][0].update(fr_mul=True),lambda v:v['cells'][0].update(identified_indices=[0],identified_targets=1)]
 for mutate in mutations:
  bad=copy.deepcopy(d);mutate(bad);assert read(commit(bad))==[]
 assert read(first)==out
