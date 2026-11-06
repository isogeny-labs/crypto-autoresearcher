"""Committed A13 metrics reject knowledge inflation, target alias and cost leaks."""
import contextlib, copy, importlib.util, io, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paid_base_metrics', ROOT/'tools/progress_metrics.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
PATH = 'research/prime_field_a13_execution_20261106/runs/a13-paid-known-base-62d664/metrics.json'


def read(ref):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        M.prime_field_paid_known_base_panel(ref, '2026-11-06')
    return [json.loads(v) for v in output.getvalue().splitlines()]


def test_committed_snapshot_and_corruption_refusal(tmp_path, monkeypatch):
    # Use the already committed compact producer record, never a working result.
    data = json.loads(subprocess.check_output(['git', 'show', 'HEAD:'+PATH], cwd=ROOT))
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tmp_path), '-c', 'user.name=test',
            '-c', 'user.email=test@example.invalid', *args], text=True).strip()
    git('init', '-q')
    monkeypatch.setattr(M, 'REPO', tmp_path)
    path = tmp_path/PATH
    path.parent.mkdir(parents=True)
    def commit(value):
        path.write_text(json.dumps(value))
        git('add', PATH)
        git('commit', '-qm', 'software snapshot')
        return git('rev-parse', 'HEAD')
    first = commit(data)
    observed = read(first)
    assert len(observed) > 3744
    assert all(v['source'] == PATH+'@'+first and v['better'] == 'neutral' for v in observed)
    path.write_text('{}')
    assert read(first) == observed
    known = next(i for i, row in enumerate(data['rows']) if row[data['columns'].index('base_arm')] == 'known')
    def row(value, index, key, replacement):
        value['rows'][index][value['columns'].index(key)] = replacement
    mutations = [lambda v: v['rows'].pop(), lambda v: v.update(unknown_systems=1),
        lambda v: v.update(verified_solver_calls=2496), lambda v: row(v, known, 'source_prefix', 128),
        lambda v: row(v, known, 'delta', 1), lambda v: row(v, known, 'source_rank', 31),
        lambda v: row(v, known, 'source_rows', 31), lambda v: row(v, 0, 'identified_mask', 255),
        lambda v: row(v, 0, 'target_rows', True),
        lambda v: v['physical_counters']['known.known_base_collection'].update(source_queries=1),
        lambda v: v['physical_counters']['known.known_base_construction'].update(public_base_certificates_verified=0),
        lambda v: v['physical_counters']['norm_collection'].update(source_queries=0),
        lambda v: v['closed_curve_checkpoints'][0]['receipt'].update(returncode=1),
        lambda v: v['query_engine_totals']['scalar'].update({'Fp.group_add': 0})]
    for mutate in mutations:
        altered = copy.deepcopy(data)
        mutate(altered)
        assert read(commit(altered)) == []
    assert read(first) == observed
