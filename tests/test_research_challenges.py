"""Challenge discovery, source integrity and the actual task preparation boundary."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from orchestration import challenges, cli, research_task, task_context, verification


def test_catalog_covers_registered_tracks_with_exact_problem_and_score():
    entries = challenges.catalog()
    assert {entry['track'] for entry in entries} == set(verification.source_lock()['tracks'])
    assert len(entries) == 6
    for entry in entries:
        directory = verification.SOURCE / 'tracks' / entry['track']
        profile = json.loads((directory / 'target-profile.json').read_text())
        config = json.loads((directory / 'verifier.json').read_text())
        assert entry['problem_statement'] == profile['challenge']
        assert entry['solution_acceptance'] == profile['acceptance']
        assert entry['input'] == profile['input']
        assert entry['output'] == profile['output']
        assert entry['objectives'] == config['objectives']
        assert entry['status'] == 'open'
        assert entry['success_probability_minimum'] == .39


def test_tracks_keep_auxiliary_inputs_pairing_directions_and_p256_prices_distinct():
    powers = challenges.get('bls12-381-g1-ecdlp')
    assert powers['scoring_n'] == 2**20
    assert set(powers['input']) == {'n', 'A', 'T'}
    plain = challenges.get('bls12-381-g1-ecdlp-plain')
    assert set(plain['input']) == {'T'}
    assert plain['scoring_n'] is None
    for track, fixed, returned in [('bls12-381-fixed-g1-invert-g2', 'P', 'Q'),
                                   ('bls12-381-fixed-g2-invert-g1', 'Q', 'P')]:
        entry = challenges.get(track)
        assert set(entry['input']) == {fixed, 'z'}
        assert set(entry['output']) == {returned}
        assert entry['scoring_n'] is None
    assert 'not a P-256 addition price' in challenges.get('p256-ecdlp')['reference_operation']


@pytest.mark.parametrize('track', verification.source_lock()['tracks'])
def test_draft_needs_design_then_survives_task_preparation(track, tmp_path):
    value = challenges.task_template('curvesmash/' + track)
    with pytest.raises(ValueError, match='procedure'):
        research_task.validate(value)
    value['procedure'] = ['Derive and independently check the proposed algorithm.']
    value['evidence_plan'] = {key: 'Supply the concrete evidence for ' + key
                              for key in research_task.METHODS[value['method']]}
    expected = deepcopy(value)
    prepared = task_context.prepare_task(task_context.load_task({'handoff': {
        'id': 'TASK-challenge-test', 'to': 'executor', 'research': value,
    }}), repo_root=tmp_path)
    manifest = task_context.context_manifest(prepared)
    assert manifest['research'] == expected
    assert manifest['research']['extensions']['challenge']['id'] == 'curvesmash/' + track
    assert manifest['research']['extensions']['challenge']['source']['files']
    assert 'approved' not in manifest['research']


def test_corrupt_protected_contract_fails_before_discovery_or_scaffolding(tmp_path, monkeypatch):
    source = tmp_path / 'source'
    shutil.copytree(verification.SOURCE, source)
    (source / 'tracks/p256-ecdlp/target-profile.json').write_text('{}')
    monkeypatch.setattr(verification, 'SOURCE', source)
    for operation in (challenges.catalog, lambda: challenges.task_template('secp256k1-ecdlp')):
        with pytest.raises(ValueError, match='protected source changed'):
            operation()


def test_cli_discovery_draft_errors_and_legacy_arguments(capsys):
    assert cli.main(['research', 'challenges']) == 0
    assert len(json.loads(capsys.readouterr().out)) == 6
    assert cli.main(['research', 'challenge', 'curvesmash/p256-ecdlp']) == 0
    assert json.loads(capsys.readouterr().out)['track'] == 'p256-ecdlp'
    assert cli.main(['research', 'template', '--challenge', 'secp256k1-ecdlp',
                     '--method', 'computational']) == 0
    draft = json.loads(capsys.readouterr().out)
    assert draft['method'] == 'computational'
    assert set(draft['evidence_plan']) == set(research_task.METHODS['computational'])
    for args in [['challenge', '../escape'], ['template', '--challenge', 'unknown'],
                 ['template', '--challenge', 'p256-ecdlp', '--question', 'different target'],
                 ['template', '--domain', 'history', '--question', 'question']]:
        assert cli.main(['research', *args]) == 2
        assert 'research error:' in capsys.readouterr().err


def test_all_skill_surfaces_refer_to_challenge_workflow():
    root = Path(__file__).resolve().parents[1]
    for directory in ('.claude/skills', '.agents/skills',
                      'plugins/crypto-autoresearcher-harness/skills'):
        for path in (root / directory).glob('*/SKILL.md'):
            assert 'docs/research-challenges.md' in path.read_text(), path
