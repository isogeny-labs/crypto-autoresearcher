"""Committed A14 export refuses coordinate inflation and incomplete custody."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mixed_helper_metrics', ROOT/'tools/progress_metrics.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
PATH = 'research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/metrics.json'


def read(ref):
    output = io.StringIO()
    with contextlib.redirect_stdout(output): M.prime_field_mixed_known_helper_panel(ref,'2026-11-06')
    return [json.loads(value) for value in output.getvalue().splitlines()]


def test_committed_snapshot_and_corruptions(tmp_path,monkeypatch):
    data = json.loads(subprocess.check_output(['git','show','HEAD:'+PATH],cwd=ROOT))
    def git(*args):
        return subprocess.check_output(['git','-C',str(tmp_path),'-c','user.name=test',
            '-c','user.email=test@example.invalid',*args],text=True).strip()
    git('init','-q')
    monkeypatch.setattr(M,'REPO',tmp_path)
    path = tmp_path/PATH
    path.parent.mkdir(parents=True)
    def commit(value):
        path.write_text(json.dumps(value));git('add',PATH);git('commit','-qm','software snapshot')
        return git('rev-parse','HEAD')
    first = commit(data)
    observed = read(first)
    assert len(observed)>11232
    assert all(v['source']==PATH+'@'+first and v['better']=='neutral' for v in observed)
    path.write_text('{}')
    assert read(first)==observed
    indices = {base:next(i for i,row in enumerate(data['rows']) if row[data['columns'].index('base_arm')]==base)
        for base in ('norm','hybrid','known32','known48')}
    def row(value,base,key,replacement):
        value['rows'][indices[base]][value['columns'].index(key)] = replacement
    mutations = [lambda v:v['rows'].pop(),lambda v:v.update(unknown_systems=1),
        lambda v:v.update(verified_information_audits=575),lambda v:v.update(verified_solver_calls=1248),
        lambda v:row(v,'known32','base_columns',32),lambda v:row(v,'known48','source_rank',48),
        lambda v:row(v,'known32','source_prefix',128),lambda v:row(v,'hybrid','native_columns',32),
        lambda v:row(v,'hybrid','supplied_columns',0),lambda v:row(v,'hybrid','delta',99),
        lambda v:row(v,'norm','identified_mask',256),lambda v:row(v,'norm','target_rows',True),
        lambda v:v['physical_counters']['public_base16.known_base_construction'].update(public_base_certificates_verified=128),
        lambda v:v['physical_counters']['known48.source_construction'].update(signed_point_queries=1)
            if 'known48.source_construction' in v['physical_counters'] else v['physical_counters'].update({'known48.source_construction':{'signed_point_queries':1}}),
        lambda v:v['physical_counters']['hybrid.source_construction'].update(signed_point_queries=0),
        lambda v:v['closed_curve_checkpoints'][0]['receipt'].update(returncode=1),
        lambda v:v['query_engine_totals']['scalar'].update({'Fp.group_add':0})]
    for mutate in mutations:
        altered=copy.deepcopy(data);mutate(altered)
        assert read(commit(altered))==[]
    assert read(first)==observed
