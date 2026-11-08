"""Drive real goal scheduling across frozen candidate and review artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from orchestration.campaign import autopilot, cli, research_loop as loop
from tools import check_merge_hygiene as hygiene

GOAL = 'GOAL-TEST-abcdef'
BASE = f'coordination/goals/{GOAL}/challenge'
ATTEMPT = 'ATTEMPT-123abc'


def write(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2))
    return hashlib.sha256(target.read_bytes()).hexdigest()


def stage(root, name, value, attempt=ATTEMPT, kind=None):
    kind = kind or {'followup': 'evidence', 'final-review': 'review'}.get(name, name)
    return write(root, f'{BASE}/attempts/{attempt}/{name}.json',
                 {'schema': f'autoresearch.challenge-{kind}/v1', **value})


@pytest.fixture
def goal(tmp_path):
    write(tmp_path, f'ledger/goals/{GOAL}.yaml', {'research_goal': {
        'id': GOAL, 'status': 'active', 'objective': 'Explain an observation.',
        'completion_criteria': ['Check the stated explanation.'], 'next_action': 'Inspect sources.'}})
    write(tmp_path, 'orchestration/research-priority.yaml', {'ecc_areas': ['TEST']})
    return tmp_path


def problem(root):
    value = loop.problem_template(root, GOAL)
    value.update(scope='Only the stated dataset.', evidence_requirements=['A derivation and a control.'])
    value['frontier'] = {'domain': 'A fixed synthetic problem domain.',
        'axes': [{'name': 'criterion', 'direction': 'satisfy', 'unit': 'predicate'}],
        'incumbents': [], 'open_boundary': 'Whether the missing case satisfies the criterion.'}
    return write(root, f'{BASE}/problem.json', value)


def candidate(root, parent=None, attempt=ATTEMPT, experiments=None, followups=None):
    path = f'{BASE}/attempts/{attempt}/argument.md'
    artifact_hash = write(root, path, {'argument': 'Synthetic software fixture, not research evidence.'})
    return stage(root, 'candidate', dict(problem_sha256=problem_hash(root),
        parent_review_sha256=parent, producer_session='producer-session', claims=['The scoped claim.'],
        response_to_findings='Handle the missing case.' if parent else None,
        frontier_target='Test the missing case at the known boundary.',
        evidence_plan='Check the derivation with a known false control.',
        experiments=experiments or [], followup_experiments=followups or [],
        artifacts=[{'path': path, 'sha256': artifact_hash}]), attempt=attempt)


def problem_hash(root):
    return hashlib.sha256((root / BASE / 'problem.json').read_bytes()).hexdigest()


def evidence(root, chash, name='evidence', experiments=None, outcome='complete'):
    path = f'{BASE}/attempts/{ATTEMPT}/observations.md'
    digest = write(root, path, {'observation': 'Fixture output only.'})
    return stage(root, name, dict(candidate_sha256=chash, experiment_ids=experiments or [],
        boundary_observation='The missing case remains unresolved in this fixture.',
        execution_outcome=outcome, artifacts=[{'path': path, 'sha256': digest}]))


def review(root, chash, ehash, decision='reject', name='review', reviewer='independent-session'):
    return stage(root, name, dict(candidate_sha256=chash, evidence_sha256=ehash,
        reviewer_session=reviewer, decision=decision, reason='Worked objection in this fixture.',
        boundary_assessment='No supported frontier movement.',
        findings=['The candidate omitted a necessary case.']))


def decision(root, rhash):
    path = 'ledger/decisions/DEC-20261108-abc123.yaml'
    digest = write(root, path, {'coordinator_decision': {'goal_id': GOAL,
        'decided_by': 'coordinator', 'decision': 'revise_after_review'}})
    return stage(root, 'decision', dict(review_sha256=rhash, next_action='Handle the missing case.',
        next_step='iterate', supersedes_sha256=None,
        frontier_update={'relation': 'unresolved', 'evidence': [],
            'remaining_gap': 'The missing case.', 'next_test': 'Check that case independently.'},
        coordinator_decision={'path': path, 'sha256': digest}))


def test_default_scheduler_drives_candidate_evidence_review_and_successor(goal):
    assert loop.plan(goal, GOAL)['phase'] == 'define_problem'
    assert autopilot.select_next(goal).kind == 'prepare'
    problem(goal)
    assert loop.plan(goal, GOAL)['phase'] == 'propose_candidate'
    chash = candidate(goal)
    assert loop.plan(goal, GOAL)['phase'] == 'snapshot_experiments'
    ehash = evidence(goal, chash)
    assert loop.plan(goal, GOAL)['phase'] == 'review_initial'
    rhash = review(goal, chash, ehash)
    view = loop.plan(goal, GOAL)
    assert view['phase'] == 'integrate_review'
    assert view['feedback']['decision'] == 'reject'
    decision(goal, rhash)
    view = loop.plan(goal, GOAL)
    assert view['phase'] == 'next_attempt'
    assert 'Handle the missing case' in view['instruction']
    assert rhash in view['instruction']
    candidate(goal, parent=rhash, attempt='ATTEMPT-456def')
    assert loop.plan(goal, GOAL)['attempt'] == 'ATTEMPT-456def'
    assert loop.plan(goal, GOAL)['phase'] == 'snapshot_experiments'


def test_acceptance_never_completes_a_goal(goal):
    problem(goal)
    chash = candidate(goal)
    rhash = review(goal, chash, evidence(goal, chash), decision='accept')
    assert loop.plan(goal, GOAL)['phase'] == 'integrate_review'
    decision(goal, rhash)
    assert loop.plan(goal, GOAL)['phase'] == 'next_attempt'
    path = goal / f'ledger/goals/{GOAL}.yaml'
    doc = json.loads(path.read_text())
    doc['research_goal']['status'] = 'completed'
    path.write_text(json.dumps(doc))
    assert loop.plan(goal, GOAL)['phase'] == 'terminal'
    assert autopilot.select_next(goal) is None


def test_infrastructure_failure_is_not_mathematical_rejection(goal):
    problem(goal)
    chash = candidate(goal)
    ehash = evidence(goal, chash, outcome='infrastructure_failure')
    review(goal, chash, ehash, decision='reject')
    with pytest.raises(ValueError, match='infrastructure failure cannot'):
        loop.plan(goal, GOAL)
    rhash = review(goal, chash, ehash, decision='infrastructure_failure')
    decision(goal, rhash)
    assert loop.plan(goal, GOAL)['phase'] == 'repair'


def test_followup_is_bounded_declared_and_bound_to_initial_review(goal, monkeypatch):
    problem(goal)
    exp = 'EXP-TEST-456def'
    chash = candidate(goal, followups=[exp])
    first = review(goal, chash, evidence(goal, chash), decision='followup')
    assert loop.plan(goal, GOAL)['phase'] == 'prepare_followup'
    write(goal, f'experiments/{exp}/specification.yaml',
          {'experiment': {'id': exp, 'goal_id': GOAL}})
    import tools.newest_experiments as newest
    monkeypatch.setattr(newest, 'newest_runnable', lambda *a, **kw:
                        [{'id': exp, 'execution_state': 'ready'}])
    monkeypatch.setattr(newest, 'execution_progress', lambda *a, **kw: {'execution_state': 'ready'})
    assert loop.plan(goal, GOAL)['phase'] == 'followup'
    assert autopilot.select_next(goal).target == exp
    monkeypatch.setattr(newest, 'execution_progress', lambda *a, **kw:
                        {'execution_state': 'measurement_complete'})
    followup = evidence(goal, chash, name='followup', experiments=[exp])
    assert loop.plan(goal, GOAL)['phase'] == 'review_final'
    combined = hashlib.sha256((first + followup).encode()).hexdigest()
    review(goal, chash, combined, name='final-review', decision='followup')
    with pytest.raises(ValueError, match='another follow-up'):
        loop.plan(goal, GOAL)
    review(goal, chash, combined, name='final-review', decision='accept')
    assert loop.plan(goal, GOAL)['phase'] == 'integrate_review'


def test_fabricated_complete_execution_and_self_review_are_refused(goal, monkeypatch):
    problem(goal)
    exp = 'EXP-TEST-456def'
    write(goal, f'experiments/{exp}/specification.yaml', {'experiment': {'goal_id': GOAL}})
    chash = candidate(goal, experiments=[exp])
    evidence(goal, chash, experiments=[exp])
    import tools.newest_experiments as newest
    monkeypatch.setattr(newest, 'execution_progress', lambda *a, **kw:
                        {'execution_state': 'needs_reconciliation'})
    with pytest.raises(ValueError, match='validated experiment output'):
        loop.plan(goal, GOAL)
    # A separate proof-only fixture checks author/reviewer separation.
    chash = candidate(goal)
    review(goal, chash, evidence(goal, chash), reviewer='producer-session')
    with pytest.raises(ValueError, match='producer cannot'):
        loop.plan(goal, GOAL)


def test_scope_bindings_tampering_orphans_and_forks_fail(goal):
    problem(goal)
    chash = candidate(goal)
    ehash = evidence(goal, chash)
    review(goal, chash, '0' * 64)
    with pytest.raises(ValueError, match='review evidence binding'):
        loop.plan(goal, GOAL)
    rhash = review(goal, chash, ehash)
    decision(goal, rhash)
    candidate(goal, parent='0' * 64, attempt='ATTEMPT-456def')
    with pytest.raises(ValueError, match='orphan candidate'):
        loop.plan(goal, GOAL)
    candidate(goal, parent=rhash, attempt='ATTEMPT-456def')
    candidate(goal, parent=rhash, attempt='ATTEMPT-789abc')
    with pytest.raises(ValueError, match='ambiguous successor'):
        loop.plan(goal, GOAL)


def test_cooldowns_and_admission_do_not_skip_a_required_review(goal):
    problem(goal)
    chash = candidate(goal)
    evidence(goal, chash)
    action = autopilot.select_next(goal)
    assert action.kind == 'review'
    assert autopilot.select_next(goal, allowed_kinds={'run', 'design'}) is None
    assert autopilot.select_next(goal, excluded={action.key}) is None
    before = action.key
    review(goal, chash, evidence(goal, chash))
    assert autopilot.select_next(goal).key != before


def test_cli_and_noncryptographic_goal_have_no_model_calls(goal, capsys):
    assert cli.main(['next', '--repo', str(goal), '--goal', GOAL]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value['model_calls'] == 0
    assert value['loop']['phase'] == 'define_problem'
    assert cli.main(['problem-template', '--repo', str(goal), '--goal', GOAL]) == 0
    template = json.loads(capsys.readouterr().out)
    assert template['question'] == 'Explain an observation.'
    assert template['scope'] == ''
    assert 'score' not in template


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def test_uncommitted_or_rewritten_stages_cannot_advance_committed_loop(goal, monkeypatch):
    git(goal, 'init', '-b', 'main')
    git(goal, 'config', 'user.name', 'Fixture')
    git(goal, 'config', 'user.email', 'fixture@example.invalid')
    git(goal, 'add', '.')
    git(goal, 'commit', '-m', 'goal')
    problem(goal)
    with pytest.raises(ValueError, match='not a tracked HEAD blob'):
        loop.plan(goal, GOAL)
    git(goal, 'add', '.')
    git(goal, 'commit', '-m', 'frozen problem')
    before = git(goal, 'rev-parse', 'HEAD')
    assert loop.plan(goal, GOAL)['phase'] == 'propose_candidate'
    path = goal / BASE / 'problem.json'
    path.write_text(path.read_text().replace('Only the stated dataset.', 'Changed scope.'))
    with pytest.raises(ValueError, match='byte-match'):
        loop.plan(goal, GOAL)
    git(goal, 'add', '.')
    monkeypatch.setattr(hygiene, 'REPO', goal)
    assert any('frozen challenge record changed' in e for e in hygiene.check_challenge_records(before))
    git(goal, 'restore', '--source=HEAD', '--staged', '--worktree', '.')
    candidate(goal)
    git(goal, 'add', '.')
    assert hygiene.check_challenge_records(before) == []


def test_frontier_observations_drive_next_test_and_reject_false_advances(goal, capsys):
    problem(goal)
    chash = candidate(goal)
    rhash = review(goal, chash, evidence(goal, chash), decision='reject')
    decision(goal, rhash)
    view = loop.plan(goal, GOAL)
    assert 'Check that case independently' in view['instruction']
    assert view['boundary_history'][0]['frontier_update']['relation'] == 'unresolved'
    assert cli.main(['frontier', '--repo', str(goal), '--goal', GOAL]) == 0
    boundary = json.loads(capsys.readouterr().out)
    assert boundary['frontier']['axes'][0]['unit'] == 'predicate'
    assert boundary['boundary_history'][0]['verdict'] == 'reject'
    path = goal / BASE / 'attempts' / ATTEMPT / 'decision.json'
    doc = json.loads(path.read_text())
    doc['frontier_update']['relation'] = 'advances'
    proof = f'{BASE}/attempts/{ATTEMPT}/argument.md'
    doc['frontier_update']['evidence'] = [{'path': proof,
        'sha256': hashlib.sha256((goal / proof).read_bytes()).hexdigest()}]
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='cannot advance the frontier'):
        loop.plan(goal, GOAL)


def test_recheck_resumes_only_through_additive_coordinator_resolution(goal):
    problem(goal)
    chash = candidate(goal)
    rhash = review(goal, chash, evidence(goal, chash))
    decision(goal, rhash)
    path = goal / BASE / 'attempts' / ATTEMPT / 'decision.json'
    doc = json.loads(path.read_text())
    doc['next_step'] = 'recheck'
    path.write_text(json.dumps(doc))
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    assert loop.plan(goal, GOAL)['phase'] == 'recheck'
    assert autopilot.select_next(goal) is None
    doc['supersedes_sha256'] = before
    doc['next_step'] = 'iterate'
    stage(goal, 'resolutions/RESUME-abc123', doc, kind='decision')
    assert loop.plan(goal, GOAL)['phase'] == 'next_attempt'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    template = loop.candidate_template(goal, GOAL)
    assert template['parent_review_sha256'] == rhash
    assert template['response_to_findings'] == ''


def test_frozen_source_and_wrong_goal_experiment_cannot_transfer_score(goal):
    problem(goal)
    chash = candidate(goal, experiments=['EXP-TEST-123abc'])
    write(goal, 'experiments/EXP-TEST-123abc/specification.yaml',
          {'experiment': {'goal_id': 'GOAL-OTHER-123abc'}})
    evidence(goal, chash, experiments=['EXP-TEST-123abc'])
    with pytest.raises(ValueError, match='does not belong'):
        loop.plan(goal, GOAL)


def test_all_skill_surfaces_link_the_default_loop():
    root = Path(__file__).resolve().parents[1]
    for folder in ('.claude/skills', '.agents/skills', 'plugins/crypto-autoresearcher-harness/skills'):
        for path in (root / folder).glob('*/SKILL.md'):
            assert 'docs/challenge-research-loop.md' in path.read_text(), path


def test_existing_review_outranks_preparing_another_problem(goal):
    other = 'GOAL-TEST-000001'
    write(goal, f'ledger/goals/{other}.yaml', {'research_goal': {'id': other,
          'status': 'active', 'objective': 'Another scoped question.', 'completion_criteria': ['Check it.']}})
    assert autopilot.select_next(goal).kind == 'prepare'
    problem(goal)
    chash = candidate(goal)
    evidence(goal, chash)
    selected = autopilot.select_next(goal)
    assert selected.kind == 'review'
    assert GOAL in selected.target


def test_terminal_historical_checkpoint_does_not_schedule_repair(goal):
    historical = 'GOAL-TEST-000001'
    write(goal, f'ledger/goals/{historical}/goal.yaml', {'research_goal': {
        'id': historical, 'status': 'completed'}})
    path = goal / f'ledger/goals/{historical}/checkpoints/old.yaml'
    path.parent.mkdir(parents=True)
    path.write_text('not: [parseable')
    selected = autopilot.select_next(goal)
    assert selected.kind == 'prepare'
    assert GOAL in selected.target
