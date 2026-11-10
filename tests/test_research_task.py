"""Domain-independent contracts survive the real task boundary, without authority."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from orchestration import cli, research_task as research, task_context

REPO = Path(__file__).resolve().parents[1]


def contract(method='theoretical'):
    return dict(schema=research.SCHEMA, domains=['an unfamiliar domain', 'mathematics'],
                question='Does the stated property follow from these assumptions?',
                method=method, procedure=['Construct the argument and check each step.'],
                evidence_plan={key: f'Declare and check {key}.' for key in research.METHODS[method]},
                acceptance_criteria=['Every inference is supported by the supplied assumptions.'],
                limitations=['Only the stated assumptions are covered.'], required_capabilities=['read_files'])


def task(value):
    return task_context.load_task({'handoff': {'id': 'TASK-test', 'to': 'executor',
        'research': value, 'artifact_paths': ['outputs/report.md'], 'read_scope': ['inputs']}})


@pytest.mark.parametrize('method', research.METHODS)
def test_each_method_and_unregistered_domain_survive_preparation(method, tmp_path):
    value = contract(method)
    original = task(value)
    before = deepcopy(original)
    prepared = task_context.prepare_task(original, repo_root=tmp_path)
    manifest = task_context.context_manifest(prepared)
    assert manifest['research'] == value
    assert prepared['read_scope'] == ['inputs']
    assert original == before
    manifest['research']['domains'].append('another')
    assert original == before


@pytest.mark.parametrize('field,value', [
    ('schema', 'unknown/v2'), ('domains', []), ('domains', 'biology'),
    ('question', '  '), ('method', 'unregistered'), ('method', []),
    ('procedure', []), ('acceptance_criteria', ['']), ('limitations', None),
    ('required_capabilities', 'read_files'), ('evidence_plan', {}),
    ('extensions', []), ('extensions', {'not_finite': float('nan')}),
])
def test_invalid_contracts_fail_before_preparation(field, value, tmp_path):
    bad = contract()
    bad[field] = value
    with pytest.raises(ValueError):
        task_context.prepare_task(task(bad), repo_root=tmp_path)


def test_unknown_fields_and_null_are_not_legacy():
    bad = contract()
    bad['acceptence_criteria'] = ['typo']
    with pytest.raises(ValueError, match='unknown research fields'):
        research.validate(bad)
    with pytest.raises(ValueError, match='must be an object'):
        research.from_task({'handoff': {'research': None}})
    with pytest.raises(ValueError, match='inside handoff'):
        research.from_task({'research': contract(), 'handoff': {}})


def test_legacy_task_has_no_new_manifest_fields(tmp_path):
    original = task_context.load_task({'id': 'TASK-old', 'to': 'executor'})
    prepared = task_context.prepare_task(original, repo_root=tmp_path)
    assert research.from_task(prepared) is None
    assert 'research' not in task_context.context_manifest(prepared)


def test_contract_cannot_grant_a_capability(tmp_path):
    value = contract()
    value['required_capabilities'] = ['operate_wet_lab']
    with pytest.raises(ValueError, match='not guaranteed by role'):
        task_context.prepare_task(task(value), repo_root=tmp_path)


def test_custom_method_keeps_extension_and_additional_evidence():
    value = contract('custom')
    value['extensions'] = {'coding_method': 'thematic', 'version': 1}
    value['evidence_plan']['inter_coder_disagreement'] = 'Retain discordant coding.'
    assert research.validate(value) == value
    del value['evidence_plan']['method_justification']
    with pytest.raises(ValueError, match='method_justification'):
        research.validate(value)


def test_cli_template_is_incomplete_and_never_approved(capsys, tmp_path):
    assert cli.main(['research', 'template', '--domain', 'history', '--method', 'literature',
                     '--question', 'What do these sources establish?']) == 0
    value = json.loads(capsys.readouterr().out)
    path = tmp_path / 'draft.json'
    path.write_text(json.dumps(value))
    assert cli.main(['research', 'validate', str(path)]) == 2
    assert 'research.procedure' in capsys.readouterr().err


@pytest.mark.parametrize('envelope', [False, True])
def test_cli_validates_and_renders_complete_contract(envelope, capsys, tmp_path):
    value = contract()
    path = tmp_path / 'task.json'
    path.write_text(json.dumps({'handoff': {'research': value}} if envelope else value))
    assert cli.main(['research', 'validate', str(path)]) == 0
    assert json.loads(capsys.readouterr().out)['valid'] is True
    assert cli.main(['research', 'brief', str(path)]) == 0
    output = capsys.readouterr().out
    assert value['question'] in output
    assert 'not execution approval' in output


@pytest.mark.parametrize('contents', ['[', 'null', 'handoff: null', 'handoff: [a]', 'schema: other/v1'])
def test_cli_malformed_inputs_have_diagnostics(contents, capsys, tmp_path):
    path = tmp_path / 'bad.yaml'
    path.write_text(contents)
    assert cli.main(['research', 'validate', str(path)]) == 2
    assert 'research error:' in capsys.readouterr().err


def test_documented_examples_are_valid():
    for path in sorted((REPO / 'examples/research-tasks').glob('*.json')):
        research.validate(json.loads(path.read_text()))
