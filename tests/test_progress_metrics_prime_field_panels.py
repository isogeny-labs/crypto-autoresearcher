"""Fixed-panel metrics cannot read dirty bytes or count incomplete trials."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess

spec=importlib.util.spec_from_file_location('fixed_panel_metrics',Path(__file__).resolve().parents[1]/'tools/progress_metrics.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


def test_source_budget_metrics_keep_prefix_and_shared_cost_boundaries(monkeypatch):
    cells=[dict(cell_id=f'p{p}-i{i}',arm=a,prefix=b,scope=s,verified=True,status='verified',base_columns=16,base_rank=0,base_nullity=16,base_rank_after_target_cancellation=0,target_base_rank_gain=0,single_targets=0,joint_targets=0,early_joint_targets=0,construction_scalar_multiplications=b,construction_cache_hits=0,construction_field_multiplications=b*100,construction_group_additions=b*10,prerequisite_scalar_multiplications=64,source_queries=b*(16 if p==8191 else 32)*2)
        for p in (8191,65537) for i in (0,1) for a in ('window','hash0','hash1','hash2') for b in (0,8,16,24,32,48,64,96,128) for s in ('relations','anchors')]
    data=dict(panel_complete=True,cells=cells,physical_work=dict(source_queries=98304,target_queries=1536,pair_entries=4928))
    def read(value):
        monkeypatch.setattr(M,'show',lambda ref,path:json.dumps(value));stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_source_budget_panel('committed-ref','2026-11-04')
        return [json.loads(v) for v in stream.getvalue().splitlines()]
    assert len(read(data))==1731
    for change in (lambda v:v['cells'].pop(),lambda v:v['cells'][0].update(construction_cache_hits=1),lambda v:v['cells'][1].update(prerequisite_scalar_multiplications=0),lambda v:v['cells'][2].update(source_queries=999),lambda v:v['physical_work'].update(source_queries=98304*9)):
        bad=copy.deepcopy(data);change(bad);assert read(bad)==[]


def test_source_control_rejects_incomplete_or_inflated_rank_and_physical_counts(monkeypatch):
    cells=[dict(cell_id=f'p{p}-i{i}',arm=a,prefix=n,scope=s,verified=True,status='verified',base_columns=16,base_rank=2,base_nullity=14,anchor_gain=1,target_base_rank_gain=1,base_rank_after_target_cancellation=3,single_targets=0,joint_targets=0,early_joint_targets=0)
           for p in (8191,65537) for i in (0,1) for a in ('window','hash0','hash1','hash2') for n in (0,16,64) for s in ('relations','anchors')]
    data=dict(panel_complete=True,cells=cells,physical_work=dict(source_queries=49152,target_queries=1536,pair_entries=4928))
    def read(d):
        monkeypatch.setattr(M,'show',lambda ref,path:json.dumps(d));stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_source_control_panel('committed-ref','2026-11-04')
        return [json.loads(v) for v in stream.getvalue().splitlines()]
    assert len(read(data))==579
    for change in (lambda d:d['cells'].pop(),lambda d:d['cells'][0].update(target_base_rank_gain=9),lambda d:d['physical_work'].update(source_queries=49152*6),lambda d:d['cells'][0].update(joint_targets=9)):
        bad=copy.deepcopy(data);change(bad);assert read(bad)==[]


def test_fresh_source_metrics_preserve_per_arm_costs_without_prefix_multiplication(monkeypatch):
    cells=[dict(cell_id=f'p{p}-i{i}',arm=a,prefix=n,scope=s,verified=True,status='verified',base_columns=16,base_rank=2,base_nullity=14,anchor_gain=1,target_base_rank_gain=1,base_rank_after_target_cancellation=3,single_targets=0,joint_targets=0,early_joint_targets=0)
           for p in (8191,65537) for i in (0,1) for a in ('window','hash0','hash1','hash2') for n in (0,16,64) for s in ('relations','anchors')]
    costs=[dict(cell_id=f'p{p}-i{i}',arm=a,source_construction=dict(counters={'source_scalar_multiplications':64,'Fp.field_mul':900,'Fp.group_add':300,'Fp.field_inv':280})) for p in (8191,65537) for i in (0,1) for a in ('window','hash0','hash1','hash2')]
    data=dict(panel_complete=True,cells=cells,per_arm_costs=costs,physical_work=dict(source_queries=49152,target_queries=1536,pair_entries=4928))
    def read(d):
        monkeypatch.setattr(M,'show',lambda ref,path:json.dumps(d));stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_fresh_source_panel('committed-ref','2026-11-04')
        return [json.loads(v) for v in stream.getvalue().splitlines()]
    out=read(data);assert len(out)==643
    assert sum(r['value'] for r in out if r['metric'].endswith('construction.source_scalar_multiplications'))==1024
    for mutate in (lambda d:d['per_arm_costs'].pop(),lambda d:d['per_arm_costs'][0]['source_construction']['counters'].update(source_scalar_multiplications=0),lambda d:d['physical_work'].update(source_queries=49152*6)):
        bad=copy.deepcopy(data);mutate(bad);assert read(bad)==[]


def test_committed_only_exact_panels_and_invalid_recoveries(tmp_path,monkeypatch):
    def git(*args):
        return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test',
             '-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_d1_execution_20261030/runs/d1-fixed-panel-a91d96/analysis.json'
    target=tmp_path/path;target.parent.mkdir(parents=True)
    data=dict(panel_complete=True,cells=[dict(curve_uid='marked-control-'+str(i//4),target_index=i%4,
         attempts=11,verified=True,status='verified',identified_target=i%2) for i in range(8)])
    def commit(value):
        target.write_text(json.dumps(value));git('add',path);git('commit','-qm','fixture');return git('rev-parse','HEAD')
    def read(ref):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_fixed_panels(ref,'2026-10-30')
        return [json.loads(line) for line in stream.getvalue().splitlines()]
    first=commit(data);samples=read(first)
    assert {r['metric'].rsplit('.',1)[-1]:r['value'] for r in samples}==dict(collection_branches=88,verified_cells=8,identified_targets=4)
    assert all(r['source']==path+'@'+first and r['better']=='neutral' for r in samples)
    target.write_text('{}');assert read(first)==samples
    for transform in (lambda d:d.update(panel_complete=False),lambda d:d['cells'][0].update(identified_target=True),
                      lambda d:d['cells'][0].update(attempts=None),lambda d:d['cells'][0].update(verified=False),
                      lambda d:d['cells'].__setitem__(1,copy.deepcopy(d['cells'][0]))):
        bad=copy.deepcopy(data);transform(bad);assert read(commit(bad))==[]
    assert read(first)==samples


def test_residual_metrics_subtract_unknowns_and_charge_shared_stream_once(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a1_execution_20261030/runs/a1-fixed-panel-8e34c5/analysis.json';p=tmp_path/path;p.parent.mkdir(parents=True)
    cells=[dict(cell_id=b,arm=a,verified=True,status='verified',delta=1,direct_base_gain=0,cross_row_cancellation_gain=1,stacked_rank=4,outside_rank=2,base_rank_before=1) for b in ('b13','b16') for a in ('smooth','pool16','pool32')]
    data=dict(panel_complete=True,cells=cells,physical_collection_attempts_observed=4587520,physical_replay_attempts_observed=4587520)
    def commit(value):p.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-source-control');return git('rev-parse','HEAD')
    def read(ref):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_residual_panels(ref,'2026-10-30')
        return [json.loads(line) for line in stream.getvalue().splitlines()]
    first=commit(data);rows=read(first)
    assert len(rows)==9 and next(r['value'] for r in rows if r['metric'].endswith('.collection_branches'))==4587520
    assert all(r['value']==1 for r in rows if r['metric'].endswith('.base_rank_gain'))
    p.write_text('{}');assert read(first)==rows
    bad=copy.deepcopy(data);bad['cells'][0]['delta']=3;assert read(commit(bad))==[]
    bad=copy.deepcopy(data);bad['physical_collection_attempts_observed']*=3;assert read(commit(bad))==[]


def test_direct_metrics_preserve_units_equivalence_and_committed_state(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a3_execution_20261030/runs/a3-fixed-panel-0cddd8/analysis.json';p=tmp_path/path;p.parent.mkdir(parents=True)
    data=dict(panel_complete=True,cells=[dict(cell_id=b,arm=a,verified=True,status='verified',accepted_witnesses=31,
        distinct_equations=20,new_rank=15,combined_rank=15,rank_gain=2,attempts=286720 if a=='enumeration' else 2048)
        for b in ('b13','b16') for a in ('enumeration','pair_table')])
    def commit(value):p.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-direct-source');return git('rev-parse','HEAD')
    def read(ref):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):M.prime_field_direct_panel(ref,'2026-10-30')
        return [json.loads(line) for line in stream.getvalue().splitlines()]
    first=commit(data);samples=read(first)
    assert len(samples)==11
    assert [(s['value'],s['unit']) for s in samples[:2]]==[(573440,'descriptors'),(4096,'queries')]
    p.write_text('{}');assert read(first)==samples
    for mutate in (lambda d:d['cells'][0].update(attempts=2048),lambda d:d['cells'][1].update(distinct_equations=21),
                   lambda d:d.update(panel_complete=False),lambda d:d['cells'][0].update(verified=False)):
        bad=copy.deepcopy(data);mutate(bad);assert read(commit(bad))==[]


def test_holdout_metrics_charge_each_stream_once_and_reject_incomplete(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a4_execution_20261030/runs/a4-holdout-panel-c47bc8/analysis.json';target=tmp_path/path;target.parent.mkdir(parents=True)
    cells=[]
    for p,n in ((8191,16),(65537,32)):
        for i in (0,1):
            for count in (0,16,64): cells.append(dict(cell_id=f'p{p}-i{i}',prefix=count,verified=True,status='verified',base_columns=n,base_rank=0,base_nullity=n,
                single_targets=0,joint_targets=0,early_joint_targets=0,source_queries=64*n*2,target_queries=8*n*2,pair_entries=n*(n-1)*2))
    data=dict(panel_complete=True,cells=cells)
    def commit(value):target.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-holdout-metadata');return git('rev-parse','HEAD')
    def read(ref):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):M.prime_field_holdout_panel(ref,'2026-10-30')
        return [json.loads(line) for line in output.getvalue().splitlines()]
    first=commit(data);rows=read(first)
    assert len(rows)==51 and [r['value'] for r in rows[:3]]==[12288,1536,4928]
    target.write_text('{}');assert read(first)==rows
    for mutate in (lambda d:d.update(panel_complete=False),lambda d:d['cells'].pop(),lambda d:d['cells'][0].update(base_rank=17),lambda d:d['cells'][0].update(joint_targets=9)):
        bad=copy.deepcopy(data);mutate(bad);assert read(commit(bad))==[]


def test_cancellation_metrics_keep_split_units_and_complete_pairs(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a8_execution_20261105/runs/a8-cold-solvers-7f32b1/analysis.json';target=tmp_path/path;target.parent.mkdir(parents=True)
    cells=[];i=0
    for p in (8191,65537):
        for curve in (0,1):
            for schedule in ('window','hash0','hash1','hash2'):
                for budget in (0,8,16,24,32,48,64,96,128):
                    for scope in ('relations','anchors'):
                        for arm in ('full_joint','cancellation_first'):
                            cells.append(dict(cell_id=f'p{p}-i{curve}',schedule=schedule,prefix=budget,scope=scope,arm=arm,instance_id=str(i),verified=True,status='verified',identified_targets=1,matrix_columns=3,matrix_rank=2,matrix_nullity=1,fr_add=2,fr_sub=3,fr_mul=4,fr_inv=1,certificate_lift_sub=1,verified_original_certificates=1))
                        i+=1
    data=dict(panel_complete=True,cells=cells,physical_processes=1,solver_calls_verified=576)
    def commit(value):target.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-solver-metadata');return git('rev-parse','HEAD')
    def read(ref):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):M.prime_field_cancellation_solver_panel(ref,'2026-11-05')
        return [json.loads(v) for v in output.getvalue().splitlines()]
    ref=commit(data);rows=read(ref);assert len(rows)==3457
    assert {v['unit'] for v in rows}>={'Fr additions','Fr subtractions','Fr multiplications','Fr inversions'}
    target.write_text('{}');assert read(ref)==rows
    for mutate in (lambda d:d['cells'].pop(),lambda d:d['cells'][0].update(fr_sub=True),lambda d:d['cells'][0].update(identified_targets=2),lambda d:d.update(panel_complete=False)):
        bad=copy.deepcopy(data);mutate(bad);assert read(commit(bad))==[]

def test_sparse_metrics_keep_four_modes_and_committed_scope(tmp_path,monkeypatch):
    def git(*args):return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test','-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q');monkeypatch.setattr(M,'REPO',tmp_path)
    path='research/prime_field_a9_execution_20261105/runs/a9-sparse-functionals-6be915/analysis.json';target=tmp_path/path;target.parent.mkdir(parents=True)
    cells=[];i=0
    for p in (8191,65537):
        for curve in (0,1):
            for schedule in ('window','hash0','hash1','hash2'):
                for budget in (0,8,16,24,32,48,64,96,128):
                    for scope in ('relations','anchors'):
                        for arm in ('dense_joint','dense_cancel','sparse_joint','sparse_cancel'):
                            cells.append(dict(cell_id=f'p{p}-i{curve}',schedule=schedule,prefix=budget,scope=scope,arm=arm,instance_id=str(i),verified=True,status='verified',identified_targets=1,matrix_columns=3,matrix_rank=2,matrix_nullity=1,fr_add=2,fr_sub=3,fr_mul=4,fr_inv=1,certificate_lift_sub=1,verified_original_certificates=1))
                        i+=1
    data=dict(panel_complete=True,cells=cells,physical_processes=1,solver_calls_verified=1152)
    def commit(value):target.write_text(json.dumps(value));git('add',path);git('commit','-qm','marked-solver-metadata');return git('rev-parse','HEAD')
    def read(ref):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):M.prime_field_sparse_functional_panel(ref,'2026-11-05')
        return [json.loads(v) for v in output.getvalue().splitlines()]
    ref=commit(data);rows=read(ref);assert len(rows)==6913
    assert {v['unit'] for v in rows}>={'Fr additions','Fr subtractions','Fr multiplications','Fr inversions'}
    target.write_text('{}');assert read(ref)==rows
    for mutate in (lambda d:d['cells'].pop(),lambda d:d['cells'][0].update(fr_sub=True),lambda d:d['cells'][0].update(identified_targets=2),lambda d:d.update(panel_complete=False)):
        bad=copy.deepcopy(data);mutate(bad);assert read(commit(bad))==[]
