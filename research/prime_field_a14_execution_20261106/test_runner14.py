"""Tiny mocked-admission driver controls; no native release, S3 or benchmark."""
import json
import gzip
from pathlib import Path
import shutil
import subprocess
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import custody14, driver14, streams14, prepare14, analyze14
from test_mixed import rules as small_rules


def tiny_rules():
    value = small_rules()
    value.update(sources=8, source_prefixes=[8], targets=1, target_queries_per_point=2,
        target_prefixes=[1, 2], base_arms=['norm', 'hybrid', 'known32', 'known48'],
        norm_scopes=['relations', 'anchors'], known_scope='supplied', closed_curve_checkpoint=False)
    plans = list(custody14.descriptors(value))
    value['systems'] = len(plans)
    value['solver_calls'] = sum(len(custody14.methods(desc)) for _, desc in plans)
    value['information_audits'] = sum(desc['base_arm'] == 'hybrid' for _, desc in plans)
    return value


def test_native_census_and_exclusions_without_native_generation():
    value = custody14.load(custody14.INPUTS)
    plans = list(custody14.descriptors(value))
    assert len(plans) == 1248
    assert sum(len(custody14.methods(desc)) for _, desc in plans) == 2496
    assert sum(desc['base_arm'] == 'hybrid' for _, desc in plans) == 576
    assert len(value['excluded_curves']) == 24
    for item in value['exclusion_sources']:
        assert custody14.digest(custody14.ROOT/item['path']) == item['sha256']
    protocol = prepare14.make_protocol(custody14.git('rev-parse', 'HEAD'))
    assert custody14.tools().schema_errors(protocol, 'experiment.protocol/v1') == []
    assert custody14.tools().lint_protocol(protocol, custody14.HERE) == []
    assert protocol['freeze']['status'] == 'draft'


def test_admission_refusal_precedes_raw_directory_or_generation(tmp_path, monkeypatch):
    calls = []
    def refuse(*args): raise ValueError('real admission refused')
    monkeypatch.setattr(driver14, 'admit', refuse)
    monkeypatch.setattr(driver14.core, 'generate', lambda *args: calls.append(args))
    monkeypatch.setattr(sys, 'argv', ['driver14', '--inputs', 'absent', '--protocol', 'absent',
        '--release', 'absent', '--out', str(tmp_path/'refused')])
    with pytest.raises(ValueError, match='admission refused'):
        driver14.main()
    assert not calls and not (tmp_path/'refused').exists()


def test_supervisor_cli_bootstraps_runtime_before_help():
    result = subprocess.run([sys.executable, str(custody14.HERE/'supervise14.py'), '--help'],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '--release' in result.stdout and '--owner' in result.stdout


def tiny_driver(tmp_path, monkeypatch):
    value = tiny_rules()
    inputs = tmp_path/'tiny-inputs.json'
    inputs.write_text(json.dumps(value))
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    monkeypatch.setattr(streams14, 'ROOT', tmp_path)
    monkeypatch.setattr(driver14, 'admit', lambda *args: dict(software_control=True, admission_mocked=True))
    raw = tmp_path/'tiny-run/raw'
    monkeypatch.setattr(sys, 'argv', ['driver14', '--inputs', str(inputs), '--protocol', 'software-mocked-only',
        '--release', 'software-mocked-only', '--out', str(raw)])
    driver14.main()
    return value, inputs, raw


def synthetic_analysis_context(tmp_path, monkeypatch, raw, inputs, value, returncode=0):
    run = raw.parent
    commit = custody14.git('rev-parse', 'HEAD')
    protocol = prepare14.make_protocol(commit)
    protocol['protocol_id'] = 'SOFTWARE-A14-TINY-MOCKED-ADMISSION-ONLY'
    protocol['question'] = 'Tiny mocked-admission stream/export control; synthetic resources, no native observations'
    protocol['sample_size']['instances'] = value['systems']
    protocol['randomization']['seed_derivation']['seeds'] = [0]*value['solver_calls']
    protocol_path = tmp_path/'tiny-protocol.json'
    custody14.write_once(protocol_path, protocol)
    custody14.tools().freeze(protocol_path, commit, True)
    host = dict(cpu_model=None, logical_cpus=1, memory_bytes=None, kernel='software-control',
        hypervisor=None, isolation_tier_max=None, python='software-control',
        executable_sha256=custody14.digest(Path(sys.executable).resolve()), git_dirty=True)
    execution = dict(returncode=returncode, timeout=False, exception=None, source_unchanged_after=True,
        observed_git_head=commit, source_commit=commit, protocol_sha256=custody14.load(protocol_path)['freeze']['protocol_sha256'],
        owner='software-control-only', started_at='2026-11-06T00:00:00+00:00', finished_at='2026-11-06T00:00:01+00:00',
        diagnostic_wall_seconds=1, cpu_user_seconds=0, cpu_sys_seconds=0, max_rss_bytes=0,
        software_control=True, synthetic_resource_placeholders=True)
    custody14.write_once(run/'host.json', host)
    custody14.write_once(run/'execution.json', execution)
    monkeypatch.setattr(analyze14, 'INPUTS', inputs)
    monkeypatch.setattr(sys, 'argv', ['analyze14', '--run', str(run), '--protocol', str(protocol_path)])
    analyze14.main()
    return protocol_path


def test_tiny_all_program_driver_analysis_cold_references_and_export(tmp_path, monkeypatch):
    value, inputs, raw = tiny_driver(tmp_path, monkeypatch)
    checked = list(streams14.lines(raw/'p211-i0.case-checks.jsonl'))
    outputs = list(streams14.lines(raw/'p211-i0.solver-outputs.jsonl'))
    info = list(streams14.lines(raw/'p211-i0.information.jsonl'))
    info_checks = list(streams14.lines(raw/'p211-i0.information-checks.jsonl'))
    assert len(checked) == value['systems']
    assert len(outputs) == value['solver_calls']
    assert len(info) == value['information_audits']
    assert len(info_checks) == value['information_audits']
    assert all(item['verification']['checked'] for item in checked+info_checks)
    assert set(item['descriptor']['base_arm'] for item in checked) == set(value['base_arms'])
    assert all(item['verification']['partial']['original_unknown_columns'] == 0
               for item in checked if item['descriptor']['base_arm'].startswith('known'))
    complete = custody14.load(raw/'p211-i0.complete.json')
    assert complete['complete'] and complete['solver_calls'] == value['solver_calls']
    run = raw.parent
    protocol_path = synthetic_analysis_context(tmp_path, monkeypatch, raw, inputs, value)
    metrics = custody14.load(run/'metrics.json')
    assert metrics['panel_complete'] and metrics['verified_systems'] == value['systems']
    assert metrics['verified_solver_calls'] == value['solver_calls']
    assert metrics['verified_information_audits'] == value['information_audits']
    export = custody14.load(run/'export.json')
    assert len(export['runs']) == value['solver_calls']
    assert custody14.tools().lint_export(export, custody14.load(protocol_path), run, True) == []
    analysis = custody14.load(run/'analysis.json')
    assert len(analysis['cold_views']) == value['systems']
    assert len(analysis['matched_comparisons']) == 252
    for view in analysis['cold_views']:
        base = view['descriptor']['base_arm']
        parts = view['collection']['component_counters']
        assert not parts['prelude_index_natural_targets'].get('source_hash_attempts', 0)
        if base.startswith('known'):
            assert not parts['selected_source'] and not parts['selected_source_recipe']
        else:
            assert parts['selected_source_recipe']['source_hash_attempts'] > 0
        own_size = 16 if base == 'hybrid' else int(base[5:]) if base.startswith('known') else None
        expected = custody14.load(raw/('p211-i0.base'+str(own_size)+'.json'))['counters'] if own_size else {}
        assert parts['own_base'] == expected
    # A copied software fixture with a modified raw row must fail its original
    # append-journal binding, even while all producer check flags still say true.
    corrupt = tmp_path/'corrupt-software-copy'
    shutil.copytree(raw, corrupt/'raw')
    for name in ('host.json', 'execution.json'):
        shutil.copyfile(run/name, corrupt/name)
    path = corrupt/'raw/p211-i0.case-inputs.jsonl.gz'
    with gzip.open(path, 'rt') as source:
        material = [json.loads(line) for line in source]
    material[0]['case']['source'][0][1] += 1
    with gzip.open(path, 'wt') as output:
        for item in material: output.write(json.dumps(item, sort_keys=True, separators=(',', ':'))+'\n')
    monkeypatch.setattr(sys, 'argv', ['analyze14', '--run', str(corrupt), '--protocol', str(protocol_path)])
    with pytest.raises(ValueError, match='case stream/journal binding'):
        analyze14.main()


@pytest.mark.parametrize('failure', ['mid_audit', 'checker_rejection'])
def test_information_failure_preserves_paid_prefix_and_output_before_checker(tmp_path, monkeypatch, failure):
    raw = tmp_path/'tiny-run/raw'
    if failure == 'mid_audit':
        def refuse(*args):
            meter = args[-1]
            def fail_after_paid_add():
                meter.ring.add(1, 1)
                raise ValueError('forced software mid-audit failure')
            meter.stage('forced_software_audit_prefix', fail_after_paid_add)
        monkeypatch.setattr(driver14.information, 'compare', refuse)
    else:
        def reject(*args):
            output = list(streams14.lines(raw/'p211-i0.information.jsonl'))
            assert len(output) == 1 and output[0]['result'] == args[-1]
            assert list(streams14.lines(raw/'p211-i0.information-checks.jsonl')) == []
            raise ValueError('forced software checker rejection')
        monkeypatch.setattr(driver14.check_information, 'check', reject)
    with pytest.raises(ValueError, match='forced software'):
        tiny_driver(tmp_path, monkeypatch)
    events = list(streams14.lines(raw/'p211-i0.events.jsonl'))
    phases = [v for v in events if v['kind'] == 'affine_phase' and v['context'].get('kind') == 'information_diagnostic']
    failures = [v for v in events if v['kind'] == 'information_failed']
    assert len(failures) == 1 and phases
    assert [v['phase'] for v in phases] == failures[0]['phases']
    if failure == 'mid_audit':
        assert phases[-1]['phase']['counters']['Fr.field_add'] == 1
        assert phases[-1]['phase']['status'] == 'failed'
        assert not failures[0]['output_record']
    else:
        assert failures[0]['output_record']
        assert any(v['kind'] == 'information_output' for v in events)
    assert not any(v['kind'] == 'information_checked' for v in events)
    synthetic_analysis_context(tmp_path, monkeypatch, raw, tmp_path/'tiny-inputs.json', tiny_rules(), returncode=1)
    metrics = custody14.load(raw.parent/'metrics.json')
    assert not metrics['panel_complete'] and metrics['partial_work_unknown']
    paid = metrics['physical_counters']['hybrid.information_diagnostic']
    expected = {}
    for event in phases:
        for key, value in event['phase']['counters'].items():
            expected[key] = expected.get(key, 0)+value
    assert paid == expected
    if failure == 'mid_audit':
        assert paid['Fr.field_add'] == 1
    else:
        data = custody14.load(raw.parent/'analysis.json')
        assert len(data['information_audits']) == 1
        assert not data['information_audits'][0]['verified']
