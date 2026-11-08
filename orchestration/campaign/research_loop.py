"""Curvesmash-style challenge/candidate/evidence/review scheduling for any goal.

The planner reads committed, hash-bound records. It never runs submitted code,
calls a judge, changes the ledger, or equates a worker exit with acceptance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from yaml import YAMLError

from .. import fast_yaml
from .projection import (ProjectionError, SourceFile, _assert_committed_sources,
                         _assert_plain_source_path, load_materialized_goal)

SCHEMAS = {
    "problem": {"goal_id", "question", "scope", "acceptance_criteria", "evidence_requirements", "max_followups", "frontier"},
    "candidate": {"problem_sha256", "parent_review_sha256", "producer_session", "claims",
                  "response_to_findings", "frontier_target", "evidence_plan", "experiments", "followup_experiments", "artifacts"},
    "evidence": {"candidate_sha256", "experiment_ids", "execution_outcome", "boundary_observation", "artifacts"},
    "review": {"candidate_sha256", "evidence_sha256", "reviewer_session", "decision", "reason", "findings", "boundary_assessment"},
    "decision": {"review_sha256", "supersedes_sha256", "coordinator_decision", "next_step", "next_action", "frontier_update"},
}
HEX = re.compile(r"[0-9a-f]{64}\Z")
ATTEMPT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*-[0-9a-f]{6}\Z")


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


def _texts(value, name, *, empty=False):
    if not isinstance(value, list) or (not empty and not value):
        raise ValueError(f"{name} must be a {'possibly empty' if empty else 'nonempty'} list")
    for item in value:
        _text(item, name)


def _hash(value, expected, name):
    if not isinstance(value, str) or not HEX.fullmatch(value) or value != expected:
        raise ValueError(f"{name} binding mismatch")


class Reader:
    def __init__(self, repo):
        self.repo = repo
        self.sources = {}

    def bytes(self, relative):
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError(f"unsafe loop source path: {relative}")
        path = self.repo / relative
        _assert_plain_source_path(self.repo, path)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        self.sources[relative] = SourceFile(relative, digest)
        return data, digest

    def record(self, path, kind):
        data, digest = self.bytes(path)
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError(f"duplicate JSON key in {path}: {key}")
                result[key] = value
            return result
        value = json.loads(data, object_pairs_hook=pairs,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        fields = SCHEMAS[kind] | {"schema"}
        if not isinstance(value, dict) or set(value) != fields:
            raise ValueError(f"{path} must contain exactly {sorted(fields)}")
        if value['schema'] != f"autoresearch.challenge-{kind}/v1":
            raise ValueError(f"wrong {kind} schema in {path}")
        return value, digest

    def refs(self, refs, *, empty=False):
        if not isinstance(refs, list) or (not empty and not refs):
            raise ValueError("artifact references must be a nonempty list")
        paths = set()
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
                raise ValueError("artifact reference requires path and sha256")
            _text(ref['path'], 'artifact path')
            if ref['path'] in paths:
                raise ValueError("duplicate artifact reference")
            paths.add(ref['path'])
            _, digest = self.bytes(ref['path'])
            _hash(ref['sha256'], digest, ref['path'])


def problem_template(repo: Path, goal_id: str) -> dict:
    goal = load_materialized_goal(repo, goal_id)
    return {'schema': 'autoresearch.challenge-problem/v1', 'goal_id': goal_id,
            'question': goal.record.get('objective', ''), 'scope': '',
            'acceptance_criteria': goal.record.get('completion_criteria') or [''],
            'evidence_requirements': [''], 'max_followups': 1,
            'frontier': {'domain': '', 'axes': [], 'incumbents': [], 'open_boundary': ''}}


def goal_ids(repo: Path) -> list[str]:
    """Discover goal identities; authoritative reads happen in plan()."""
    goals = repo / 'ledger/goals'
    return sorted({path.stem for path in goals.glob('GOAL-*.yaml')} |
                  {path.parent.name for path in goals.glob('GOAL-*/goal.yaml')})


def plan(repo: Path, goal_id: str, *, inspect_terminal=False) -> dict:
    """Return the next bounded phase; only artifact state advances the loop."""
    repo = Path(repo).resolve()
    goal = load_materialized_goal(repo, goal_id)
    reader = Reader(repo)
    base = f'coordination/goals/{goal_id}/challenge'
    frontier_context = None
    history = []

    def result(phase, kind, instruction, *, attempt=None, experiment=None, feedback=None):
        _assert_committed_sources(repo, list(reader.sources.values()))
        return {'schema': 'autoresearch.challenge-next/v1', 'goal_id': goal_id,
                'phase': phase, 'kind': kind, 'attempt': attempt, 'experiment_id': experiment,
                'instruction': instruction, 'feedback': feedback,
                'frontier': frontier_context, 'boundary_history': history,
                'source_files': [s.__dict__ for s in reader.sources.values()],
                'goal_projection_hash': goal.projection_hash,
                'authority': 'scheduling only; no scientific transition'}

    if goal.status not in {'active', 'draft'} and not inspect_terminal:
        return result('terminal', None, 'The committed goal is terminal; select no work.')
    if not (repo / base / 'problem.json').exists():
        return result('define_problem', 'prepare',
            f'Define and commit {base}/problem.json from campaign problem-template. '
            'Keep the goal scope and completion criteria, state its evidence requirements, '
            'and freeze the question before proposing a candidate. Reuse existing work.')
    problem, problem_hash = reader.record(base + '/problem.json', 'problem')
    if problem['goal_id'] != goal_id:
        raise ValueError('problem belongs to another goal')
    for field in ('question', 'scope'):
        _text(problem[field], field)
    for field in ('acceptance_criteria', 'evidence_requirements'):
        _texts(problem[field], field)
    if type(problem['max_followups']) is not int or problem['max_followups'] not in (0, 1):
        raise ValueError('max_followups must be 0 or 1')
    frontier_context = problem['frontier']
    if not isinstance(frontier_context, dict) or set(frontier_context) != {'domain', 'axes', 'incumbents', 'open_boundary'}:
        raise ValueError('frontier needs domain, axes, incumbents and open_boundary')
    for field in ('domain', 'open_boundary'):
        _text(frontier_context[field], 'frontier.' + field)
    axes = frontier_context['axes']
    if not isinstance(axes, list) or not axes:
        raise ValueError('frontier needs at least one objective or qualitative axis')
    names = set()
    for axis in axes:
        if not isinstance(axis, dict) or set(axis) != {'name', 'direction', 'unit'}:
            raise ValueError('frontier axis needs name, direction and unit')
        for field in ('name', 'unit'):
            _text(axis[field], 'axis.' + field)
        if axis['name'] in names or axis['direction'] not in {'minimize', 'maximize', 'satisfy'}:
            raise ValueError('invalid or duplicate frontier axis')
        names.add(axis['name'])
    reader.refs(frontier_context['incumbents'], empty=True)

    candidates = {}
    for path in sorted((repo / base / 'attempts').glob('*/candidate.json')):
        attempt = path.parent.name
        if not ATTEMPT.fullmatch(attempt):
            raise ValueError('attempt ids need a random six-hex suffix')
        candidate, digest = reader.record(path.relative_to(repo).as_posix(), 'candidate')
        _hash(candidate['problem_sha256'], problem_hash, 'candidate problem')
        _text(candidate['producer_session'], 'producer_session')
        _text(candidate['frontier_target'], 'frontier_target')
        if candidate['parent_review_sha256'] is None:
            if candidate['response_to_findings'] is not None:
                raise ValueError('initial candidate has no parent findings')
        else:
            _text(candidate['response_to_findings'], 'response_to_findings')
        _texts(candidate['claims'], 'claims')
        _text(candidate['evidence_plan'], 'evidence_plan')
        for field in ('experiments', 'followup_experiments'):
            _texts(candidate[field], field, empty=True)
            if len(set(candidate[field])) != len(candidate[field]) or any(
                    not re.fullmatch(r'EXP-[A-Za-z0-9-]+', eid) for eid in candidate[field]):
                raise ValueError('experiments must be distinct safe EXP-* identifiers')
        if set(candidate['experiments']) & set(candidate['followup_experiments']):
            raise ValueError('follow-up experiments must use fresh declared experiment ids')
        if not problem['max_followups'] and candidate['followup_experiments']:
            raise ValueError('this problem permits no follow-up')
        reader.refs(candidate['artifacts'])
        candidates[attempt] = candidate, digest
    if not candidates:
        return result('propose_candidate', 'design',
            f'Propose a concrete candidate in {base}/attempts/ATTEMPT-<six-hex>/candidate.json. '
            'Freeze its original claims, evidence plan, artifact hashes and initial/optional '
            'follow-up experiment ids. Reuse existing hypotheses and protocols. '
            'Do not run experiments in this design action.')

    roots = [a for a, (c, _) in candidates.items() if c['parent_review_sha256'] is None]
    if len(roots) != 1:
        raise ValueError('the attempt chain must have exactly one initial candidate')
    current = roots[0]
    visited = set()
    while True:
        if current in visited:
            raise ValueError('cyclic attempt chain')
        visited.add(current)
        candidate, candidate_hash = candidates[current]
        prefix = f'{base}/attempts/{current}'
        failed_evidence = {}

        def experiment_progress(eid):
            from tools.newest_experiments import execution_progress
            data, _ = reader.bytes(f'experiments/{eid}/specification.yaml')
            parsed = fast_yaml.safe_load(data)
            spec = parsed.get('experiment') if isinstance(parsed, dict) else None
            if not isinstance(spec, dict):
                raise ValueError(f'{eid} has no experiment specification')
            if spec.get('goal_id') != goal_id:
                raise ValueError(f'{eid} does not belong to {goal_id}')
            return execution_progress(repo / 'experiments' / eid, repo)

        def evidence_phase(filename, experiments, phase):
            if not (repo / prefix / filename).exists():
                from tools.newest_experiments import newest_runnable
                admitted = {r['id']: r for r in newest_runnable(repo, include_blocked=True,
                            goal=goal_id)}
                for eid in experiments:
                    if not (repo / 'experiments' / eid / 'specification.yaml').exists():
                        return None, result('prepare_' + phase, 'prepare',
                            f'Design and admit declared {eid} for {goal_id}; do not execute '
                            'an unapproved experiment or change this candidate.', attempt=current)
                    progress = experiment_progress(eid)
                    row = admitted.get(eid)
                    if row and row.get('off_main_runs'):
                        return None, result('reconcile_' + phase, 'review',
                            f'Reconcile existing off-main runs of {eid}: {row["off_main_runs"]}. '
                            'Do not repeat executed trials.', attempt=current)
                    if row and row['execution_state'] == 'ready':
                        return None, result(phase, 'run',
                            f'Use $run for {eid} only, preserving this candidate and all attempts. '
                            f'Coordinator later binds its outputs in {prefix}/{filename}.',
                            attempt=current, experiment=eid)
                    if progress['execution_state'] != 'measurement_complete':
                        return None, result('prepare_' + phase, 'prepare',
                            f'Prepare or reconcile declared {eid} through existing admission, '
                            f'ownership and protocol rules; state={progress["execution_state"]}. '
                            'A hold or infrastructure failure is not mathematical rejection.', attempt=current)
                return None, result('snapshot_' + phase, 'review',
                    f'Archive actual supporting outputs and write {prefix}/{filename} with '
                    'their hashes and exact experiment ids; include proof/literature evidence '
                    'when no experiment is applicable. Worker prose is not evidence.', attempt=current)
            evidence, digest = reader.record(prefix + '/' + filename, 'evidence')
            _hash(evidence['candidate_sha256'], candidate_hash, 'evidence candidate')
            if evidence['experiment_ids'] != experiments:
                raise ValueError('evidence must name the exact declared experiment ids')
            if evidence['execution_outcome'] not in {'complete', 'infrastructure_failure'}:
                raise ValueError('invalid execution_outcome')
            _text(evidence['boundary_observation'], 'boundary_observation')
            failed_evidence[filename] = evidence['execution_outcome'] == 'infrastructure_failure'
            if not failed_evidence[filename]:
                for eid in experiments:
                    if experiment_progress(eid)['execution_state'] != 'measurement_complete':
                        raise ValueError('complete evidence needs validated experiment output')
            reader.refs(evidence['artifacts'])
            return digest, None

        def review_phase(filename, evidence_hash, *, final=False, failed=False):
            if not (repo / prefix / filename).exists():
                return None, None, result('review_final' if final else 'review_initial', 'review',
                    f'Arrange an independent review of every original claim against the '
                    f'frozen problem and evidence; write {prefix}/{filename}. Use the existing '
                    'review plan and policy. Accept or reject with concrete findings, or request '
                    + ('no further follow-up. ' if final else 'one bounded declared follow-up. ')
                    + 'Exploratory acceptance alone never promotes or closes the goal.', attempt=current)
            review, digest = reader.record(prefix + '/' + filename, 'review')
            _hash(review['candidate_sha256'], candidate_hash, 'review candidate')
            _hash(review['evidence_sha256'], evidence_hash, 'review evidence')
            _text(review['reviewer_session'], 'reviewer_session')
            if review['reviewer_session'] == candidate['producer_session']:
                raise ValueError('candidate producer cannot be its reviewer')
            _text(review['reason'], 'review reason')
            _text(review['boundary_assessment'], 'boundary_assessment')
            _texts(review['findings'], 'findings', empty=True)
            if review['decision'] not in {'accept', 'reject', 'followup', 'infrastructure_failure'}:
                raise ValueError('invalid review decision')
            if failed and review['decision'] != 'infrastructure_failure':
                raise ValueError('infrastructure failure cannot accept or reject a scientific claim')
            if review['decision'] == 'followup' and (final or not problem['max_followups']):
                raise ValueError('another follow-up is not allowed')
            return review, digest, None

        evidence_hash, pending = evidence_phase('evidence.json', candidate['experiments'], 'experiments')
        if pending:
            return pending
        review, review_hash, pending = review_phase('review.json', evidence_hash,
                                                    failed=failed_evidence['evidence.json'])
        if pending:
            return pending
        if review['decision'] == 'followup':
            if not candidate['followup_experiments']:
                raise ValueError('follow-up must use declared experiments')
            followup_hash, pending = evidence_phase('followup.json', candidate['followup_experiments'], 'followup')
            if pending:
                return pending
            # Bind the final review to both initial judgment and follow-up bytes.
            combined = hashlib.sha256((review_hash + followup_hash).encode()).hexdigest()
            review, review_hash, pending = review_phase('final-review.json', combined, final=True,
                                                       failed=failed_evidence['followup.json'])
            if pending:
                return pending
        history.append({'attempt': current, 'candidate_sha256': candidate_hash,
                        'review_sha256': review_hash, 'verdict': review['decision'],
                        'boundary_assessment': review['boundary_assessment'],
                        'frontier_update': None})
        if not (repo / prefix / 'decision.json').exists():
            return result('integrate_review', 'review',
                f'Consume the {review["decision"]} findings, not the worker exit status. '
                f'Use /coordinate to arrange required scientific review/archive and record '
                f'{prefix}/decision.json pointing to the Coordinator decision and one next_action. '
                'Preserve all failures. Infrastructure failure calls for repair; rejection '
                'calls for a changed candidate; acceptance still needs ordinary promotion gates.',
                attempt=current, feedback=review)
        decision, decision_hash = reader.record(prefix + '/decision.json', 'decision')
        if decision['supersedes_sha256'] is not None:
            raise ValueError('initial iteration decision cannot supersede another decision')
        resolutions = {}
        for path in sorted((repo / prefix / 'resolutions').glob('*.json')):
            if not ATTEMPT.fullmatch(path.stem):
                raise ValueError('resolution ids need a random six-hex suffix')
            record, digest = reader.record(path.relative_to(repo).as_posix(), 'decision')
            if digest in resolutions:
                raise ValueError('duplicate decision resolution')
            resolutions[digest] = record
        while True:
            _hash(decision['review_sha256'], review_hash, 'decision review')
            _text(decision['next_action'], 'next_action')
            if decision['next_step'] not in {'iterate', 'recheck', 'complete'}:
                raise ValueError('next_step must be iterate, recheck or complete')
            reader.refs([decision['coordinator_decision']])
            if not re.fullmatch(r'ledger/decisions/DEC-[A-Za-z0-9-]+\.yaml',
                                decision['coordinator_decision']['path']):
                raise ValueError('iteration requires an archived Coordinator decision')
            data, _ = reader.bytes(decision['coordinator_decision']['path'])
            parsed = fast_yaml.safe_load(data)
            coordinator = parsed.get('coordinator_decision') if isinstance(parsed, dict) else None
            if not isinstance(coordinator, dict):
                raise ValueError('missing Coordinator decision')
            if (coordinator.get('decided_by') != 'coordinator' or
                    goal_id not in [coordinator.get('goal_id'), *(coordinator.get('target_ids') or [])]):
                raise ValueError('Coordinator decision must name this goal')
            successors = [digest for digest, record in resolutions.items()
                          if record['supersedes_sha256'] == decision_hash]
            if len(successors) > 1:
                raise ValueError('ambiguous decision resolutions')
            if not successors:
                if resolutions:
                    raise ValueError('orphan decision resolution')
                break
            decision_hash = successors[0]
            decision = resolutions.pop(decision_hash)
        update = decision['frontier_update']
        if not isinstance(update, dict) or set(update) != {'relation', 'evidence', 'remaining_gap', 'next_test'}:
            raise ValueError('frontier_update needs relation, evidence, remaining_gap and next_test')
        if update['relation'] not in {'advances', 'trade', 'matches', 'regresses', 'inadmissible', 'unresolved'}:
            raise ValueError('invalid frontier relation')
        for field in ('remaining_gap', 'next_test'):
            _text(update[field], 'frontier_update.' + field)
        reader.refs(update['evidence'], empty=update['relation'] == 'unresolved')
        if (review['decision'] == 'infrastructure_failure' and update['relation'] not in {'inadmissible', 'unresolved'}
                or review['decision'] == 'reject' and update['relation'] in {'advances', 'trade'}):
            raise ValueError('a failed or rejected candidate cannot advance the frontier')
        history[-1]['frontier_update'] = update
        children = [a for a, (c, _) in candidates.items() if c['parent_review_sha256'] == review_hash]
        if len(children) > 1:
            raise ValueError('ambiguous successor candidates; Coordinator must select one chain')
        if decision['next_step'] != 'iterate':
            if children or set(candidates) != visited:
                raise ValueError('successor candidate contradicts the Coordinator next_step')
            return result('recheck' if decision['next_step'] == 'recheck' else 'reconcile_completion',
                None if decision['next_step'] == 'recheck' else 'review',
                decision['next_action'] + ('; the goal stays active until its committed status changes.'
                if decision['next_step'] == 'complete' else ''), attempt=current, feedback=review)
        if not children:
            if set(candidates) != visited:
                raise ValueError('orphan candidate or candidate based on an unfinalized review')
            return result('repair' if review['decision'] == 'infrastructure_failure' else 'next_attempt',
                'repair' if review['decision'] == 'infrastructure_failure' else 'design',
                f'Follow the archived next_action: {decision["next_action"]}. '
                f'Boundary gap: {update["remaining_gap"]}. Next boundary test: {update["next_test"]}. '
                f'Keep this attempt immutable; a successor candidate must bind parent_review_sha256={review_hash}. '
                'State which finding it addresses and retain the frozen problem. '
                'If no justified action is possible, record an impediment and recheck; do not invent work.',
                attempt=current, feedback=review)
        current = children[0]


def action_for(view: dict):
    from .autopilot import Action
    if view['kind'] is None:
        return None
    state_hash = hashlib.sha256(json.dumps([view['goal_projection_hash'], view['source_files']],
                                           sort_keys=True).encode()).hexdigest()[:12]
    target = view['experiment_id'] or f"{view['goal_id']}/{view['attempt'] or 'problem'}/{view['phase']}/{state_hash}"
    return Action(view['kind'], target,
        f"Default research loop for {view['goal_id']}; phase={view['phase']}. "
        'Read docs/challenge-research-loop.md. As dispatcher, use the appropriate '
        'existing skill and role; Coordinator acts remain in its subagent. '
        + view['instruction'] + '\nFrozen frontier context: ' + json.dumps(view['frontier'])
        + '\nLatest reviewed boundary observations: ' + json.dumps(view['boundary_history'][-3:]),
        'executor' if view['kind'] == 'run' else 'coordinator')


def select(repo: Path, *, excluded: set[str], allowed_kinds=None):
    from tools.ecc_priority import load_policy, sort_key
    policy = load_policy(repo / 'orchestration/research-priority.yaml')
    priority = {'run': 0, 'review': 1, 'repair': 2, 'prepare': 3, 'design': 4}
    selected = None
    selected_rank = None
    for goal_id in sorted(goal_ids(repo), key=lambda gid: sort_key(gid, policy)):
        group = sort_key(goal_id, policy)[0]
        if selected_rank is not None and selected_rank[0] < group:
            break
        try:
            # Historical terminal checkpoints need no scheduling/materialization.
            heads = [path for path in (repo / f'ledger/goals/{goal_id}.yaml',
                     repo / f'ledger/goals/{goal_id}/goal.yaml') if path.exists()]
            if len(heads) == 1:
                reader = Reader(repo)
                data, _ = reader.bytes(heads[0].relative_to(repo).as_posix())
                header = fast_yaml.safe_load(data)
                record = header.get('research_goal') if isinstance(header, dict) else None
                if isinstance(record, dict) and record.get('status') in {'completed', 'closed_at_budget', 'cancelled'}:
                    _assert_committed_sources(repo, list(reader.sources.values()))
                    continue
            action = action_for(plan(repo, goal_id))
        except (OSError, ValueError, ProjectionError, YAMLError) as exc:
            from .autopilot import Action
            action = Action('repair', goal_id + '/challenge-records',
                f'Use /coordinate to repair challenge-loop custody for {goal_id}: {exc}. '
                'Do not run trials, alter frozen attempts, or infer a scientific outcome.', 'coordinator')
        if action and action.key not in excluded and (allowed_kinds is None or action.kind in allowed_kinds):
            rank = (group, priority[action.kind], goal_id)
            if selected_rank is None or rank < selected_rank:
                selected, selected_rank = action, rank
            if priority[action.kind] == 0:
                break
    return selected


def candidate_template(repo: Path, goal_id: str) -> dict:
    """Print a deliberately incomplete candidate for the currently selected phase."""
    view = plan(repo, goal_id)
    if view['phase'] not in {'propose_candidate', 'next_attempt', 'repair'}:
        raise ValueError('finish the current evidence/review phase before drafting another candidate')
    base = Path(repo) / f'coordination/goals/{goal_id}/challenge'
    parent = None
    if view['attempt']:
        final = base / 'attempts' / view['attempt'] / 'final-review.json'
        review = final if final.exists() else base / 'attempts' / view['attempt'] / 'review.json'
        parent = hashlib.sha256(review.read_bytes()).hexdigest()
    return {'schema': 'autoresearch.challenge-candidate/v1',
            'problem_sha256': hashlib.sha256((base / 'problem.json').read_bytes()).hexdigest(),
            'parent_review_sha256': parent, 'response_to_findings': '' if parent else None,
            'producer_session': '', 'claims': [''], 'frontier_target': '', 'evidence_plan': '',
            'experiments': [], 'followup_experiments': [], 'artifacts': []}
