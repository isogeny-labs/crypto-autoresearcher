"""Marked tiny mocked-admission controls; no native A13 execution or S3."""
from pathlib import Path
import json
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import custody
from baseline import core
from test_known import small_rules
import streams
from cold_costs import compare

driver = core.solver.module('_a13_driver_test', 'research/prime_field_a13_execution_20261106/driver.py')
analysis = core.solver.module('_a13_analysis_test', 'research/prime_field_a13_execution_20261106/analyze.py')
prepare = core.solver.module('_a13_prepare_test', 'research/prime_field_a13_execution_20261106/prepare.py')


def test_exact_native_grid_provenance_and_protocol_schema():
    rules = custody.load(custody.INPUTS)
    plans = list(custody.descriptors(rules))
    assert len(plans) == 624
    assert sum(len(custody.methods(v)) for i, v in plans) == 1248
    assert len(rules['excluded_curves']) == 20
    for item in rules['exclusion_sources']:
        assert custody.digest(custody.ROOT/item['path']) == item['sha256']
    proto = prepare.make_protocol(custody.git('rev-parse', 'HEAD'))
    assert custody.tools().schema_errors(proto, 'experiment.protocol/v1') == []
    assert custody.tools().lint_protocol(proto, custody.HERE) == []
    assert len(proto['arms']) == 2 and proto['sample_size']['instances'] == 624


def test_admission_failure_has_no_raw_generation(tmp_path, monkeypatch):
    out = tmp_path/'refused'
    calls = []
    def refuse(*args):
        raise ValueError('real admission refused')
    monkeypatch.setattr(driver, 'admit', refuse)
    monkeypatch.setattr(driver.core, 'generate', lambda *args: calls.append(args))
    monkeypatch.setattr(sys, 'argv', ['driver', '--inputs', 'absent', '--protocol', 'absent',
        '--release', 'absent', '--out', str(out)])
    with pytest.raises(ValueError, match='admission refused'):
        driver.main()
    assert not calls and not out.exists()


def test_cross_base_comparison_uses_exact_targets_not_rank_or_count():
    a = dict(identified_mask=3, delta=999, counters={'Fp.field_mul': 2})
    b = dict(identified_mask=5, delta=0, counters={'Fp.field_mul': 3})
    assert not compare(a, b, ['Fp.field_mul'])
    a['identified_mask'] = 7
    assert compare(a, b, ['Fp.field_mul'])
    a['counters']['Fp.field_mul'] = 4
    assert not compare(a, b, ['Fp.field_mul'])


def test_tiny_complete_driver_analysis_and_export(tmp_path, monkeypatch):
    # Admission alone is mocked, explicitly and only for tiny software rules.
    # Resource placeholders below are test fixtures, not claimed measurements.
    rules = small_rules()
    rules.update(base_arms=['norm', 'known'], norm_scopes=['relations', 'anchors'],
                 known_scope='supplied', closed_curve_checkpoint=False)
    rules['systems'] = len(list(custody.descriptors(rules)))
    rules['solver_calls'] = sum(len(custody.methods(v)) for i, v in custody.descriptors(rules))
    inputs = tmp_path/'tiny-inputs.json'
    inputs.write_text(json.dumps(rules))
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    monkeypatch.setattr(streams, 'ROOT', tmp_path)
    monkeypatch.setattr(driver, 'admit', lambda *args: dict(software_control=True, admission_mocked=True))
    run, protocol_path = tmp_path/'tiny-run', tmp_path/'tiny-protocol.json'
    protocol = prepare.make_protocol(custody.git('rev-parse', 'HEAD'))
    protocol['protocol_id'] = 'SOFTWARE-A13-TINY-CONTROL'
    protocol['question'] = 'Tiny mocked-admission stream/export software control only; no native data'
    protocol['sample_size']['instances'] = rules['systems']
    protocol['randomization']['seed_derivation']['seeds'] = [0]*rules['solver_calls']
    custody.write_once(protocol_path, protocol)
    custody.tools().freeze(protocol_path, custody.git('rev-parse', 'HEAD'), True)
    monkeypatch.setattr(sys, 'argv', ['driver', '--inputs', str(inputs), '--protocol', str(protocol_path),
        '--release', 'software-mocked-only', '--out', str(run/'raw')])
    driver.main()
    assert len(list(streams.lines(run/'raw/p211-i0.case-checks.jsonl'))) == rules['systems']
    host = dict(cpu_model=None, logical_cpus=1, memory_bytes=None, kernel='software-control',
                hypervisor=None, isolation_tier_max=None, python='software-control',
                executable_sha256=custody.digest(Path(sys.executable).resolve()), git_dirty=True)
    execution = dict(returncode=0, timeout=False, exception=None, source_unchanged_after=True,
        observed_git_head=custody.git('rev-parse', 'HEAD'), source_commit=custody.git('rev-parse', 'HEAD'),
        protocol_sha256=custody.load(protocol_path)['freeze']['protocol_sha256'], owner='software-control-only',
        started_at='2026-11-06T00:00:00+00:00', finished_at='2026-11-06T00:00:01+00:00',
        diagnostic_wall_seconds=1, cpu_user_seconds=0, cpu_sys_seconds=0, max_rss_bytes=0,
        software_control=True, synthetic_resource_placeholders=True)
    custody.write_once(run/'host.json', host)
    custody.write_once(run/'execution.json', execution)
    monkeypatch.setattr(analysis, 'INPUTS', inputs)
    monkeypatch.setattr(sys, 'argv', ['analyze', '--run', str(run), '--protocol', str(protocol_path)])
    analysis.main()
    metrics = custody.load(run/'metrics.json')
    assert metrics['panel_complete'] and metrics['verified_systems'] == rules['systems']
    assert metrics['verified_solver_calls'] == rules['solver_calls']
    export = custody.load(run/'export.json')
    assert len(export['runs']) == rules['solver_calls']
    assert custody.tools().lint_export(export, custody.load(protocol_path), run, True) == []
    data = custody.load(run/'analysis.json')
    known = [v for v in data['cold_views'] if v['descriptor']['base_arm'] == 'known']
    assert len(known) == len(rules['target_policies'])*len(rules['target_prefixes'])
    assert all('source_queries' not in v['collection']['source_or_base_counters'] for v in known)
    assert len(data['matched_comparisons']) == 2*len(rules['seeds'])*2*len(rules['target_policies'])*len(rules['target_prefixes'])*2
