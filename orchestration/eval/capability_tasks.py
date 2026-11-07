"""Frozen, domain-neutral capability challenges and evaluator-held ground truth."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import random
import re
from pathlib import Path

SCHEMA = 'autoresearch.capability-campaign/v1'
ARMS = ('single', 'planned', 'reviewed')
FAMILIES = ('data_analysis', 'source_synthesis', 'finite_theory')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                     separators=(',', ':')).encode()).hexdigest()


def positive(value, name, *, integer=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0
            or (integer and not isinstance(value, int))):
        raise ValueError(f'{name} must be a positive {"integer" if integer else "finite number"}')


def validate(spec):
    if not isinstance(spec, dict) or spec.get('schema') != SCHEMA:
        raise ValueError(f'expected {SCHEMA}')
    if spec.get('split') not in ('dev', 'held_out'):
        raise ValueError('split must be dev or held_out')
    if not isinstance(spec.get('arms'), list) or not all(isinstance(a,str) for a in spec['arms']) or not spec['arms'] or len(set(spec['arms'])) != len(spec['arms']) or set(spec['arms']) - set(ARMS):
        raise ValueError('arms must be unique supported arms')
    for key in ('instances', 'repeats', 'seed'):
        positive(spec.get(key), key, integer=True)
    if not isinstance(spec.get('tasks'), list) or not spec['tasks']:
        raise ValueError('at least one task is required')
    ids = set()
    for task in spec['tasks']:
        if not isinstance(task, dict):
            raise ValueError('task must be an object')
        name = task.get('id', '')
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in ids:
            raise ValueError('task ids must be unique literal path components')
        ids.add(name)
        if task.get('family') not in FAMILIES:
            raise ValueError(f'{name}: unsupported family')
        if not isinstance(task.get('domain'), str) or not task['domain'].strip():
            raise ValueError(f'{name}: domain is required')
        positive(task.get('difficulty'), 'difficulty', integer=True)
        if task['difficulty'] > 100:
            raise ValueError('difficulty exceeds bounded fixture limit 100')
    budget = spec.get('budget', {})
    if not isinstance(budget,dict): raise ValueError('budget must be an object')
    for key in ('wall_seconds', 'memory_mb', 'max_sessions_per_trial', 'max_output_bytes', 'max_request_bytes'):
        positive(budget.get(key), f'budget.{key}', integer=True)
    if 'max_actor_file_bytes' in budget:
        positive(budget['max_actor_file_bytes'],'budget.max_actor_file_bytes',integer=True)
        if budget['max_actor_file_bytes'] < budget['max_output_bytes']:
            raise ValueError('actor file limit must accommodate output limit')
    required = max({'single': 1, 'planned': 2, 'reviewed': 4}[a] for a in spec['arms'])
    if budget['max_sessions_per_trial'] < required:
        raise ValueError('max_sessions_per_trial is below the selected stage count')
    if budget.get('billing') != 'subscription_unknown':
        raise ValueError('native transport requires billing=subscription_unknown; no dollar cap is asserted')
    gate = spec.get('reliability', {})
    if not isinstance(gate,dict): raise ValueError('reliability must be an object')
    positive(gate.get('minimum_instances'), 'reliability.minimum_instances', integer=True)
    for key in ('minimum_success_lower_bound', 'maximum_false_success_upper_bound'):
        v = gate.get(key)
        if isinstance(v, bool) or not isinstance(v, (int,float)) or not 0 <= v <= 1:
            raise ValueError(f'reliability.{key} must lie in [0,1]')
    return copy.deepcopy(spec)


def load(path):
    return validate(json.loads(Path(path).read_text()))


def instance(task, seed):
    """Return public input and private reference; never put the latter in a sandbox."""
    rng = random.Random(seed)
    n = task['difficulty'] + 3
    family = task['family']
    if family == 'data_analysis':
        rows = [{'group': rng.choice(['A', 'B']), 'value': rng.randint(-20, 30)} for _ in range(n * 4)]
        reference = {g: {'count': sum(r['group'] == g for r in rows),
                         'sum': sum(r['value'] for r in rows if r['group'] == g)} for g in ('A', 'B')}
        public = {'question': 'Compute count and sum of value for each group A and B, including negative values.',
                  'rows': rows, 'answer_shape': {'A': {'count': 'integer', 'sum': 'integer'},
                                               'B': {'count': 'integer', 'sum': 'integer'}}}
    elif family == 'source_synthesis':
        sources = []
        reference = {'supported': [], 'contradicted': [], 'unresolved': []}
        for i in range(n):
            claim = f'claim-{i}'
            signs = rng.choice([(True,), (False,), (True, False), ()])
            refs = []
            for sign in signs:
                sid = f'source-{len(sources)}'
                sources.append({'id': sid, 'claim': claim, 'supports': sign})
                refs.append(sid)
            category = ('supported' if signs == (True,) else 'contradicted' if signs == (False,) else 'unresolved')
            reference[category].append({'claim': claim, 'sources': sorted(refs)})
        public = {'question': 'Classify each claim from this synthetic source register: supported if only positive evidence, contradicted if only negative evidence, unresolved if conflicting or absent. Cite all source IDs for each claim. Do not infer beyond this register.',
                  'claims': [f'claim-{i}' for i in range(n)], 'sources': sources,
                  'answer_shape': {k: [{'claim': 'claim-ID', 'sources': ['source-ID']}] for k in reference}}
    else:
        modulus = rng.randint(3, n + 4)
        a, b = rng.randrange(modulus), rng.randrange(modulus)
        witnesses = [x for x in range(modulus) if (a*x+b) % modulus == 0]
        reference = {'solutions': witnesses, 'exists': bool(witnesses)}
        public = {'question': 'Find every x in 0..modulus-1 satisfying (a*x+b) mod modulus = 0. State whether any exists.',
                  'a': a, 'b': b, 'modulus': modulus,
                  'answer_shape': {'solutions': ['integer, ascending'], 'exists': 'boolean'}}
    return public, reference


def grade(answer, reference):
    """Strict types avoid accepting True as 1. Alternative source order is immaterial."""
    try:
        normalized = copy.deepcopy(answer)
        if isinstance(normalized, dict) and set(normalized) == {'supported', 'contradicted', 'unresolved'}:
            for key in normalized:
                for entry in normalized[key]:
                    entry['sources'] = sorted(entry['sources'])
                normalized[key] = sorted(normalized[key], key=lambda x: x['claim'])
            reference = copy.deepcopy(reference)
            for key in reference:
                reference[key] = sorted(reference[key], key=lambda x: x['claim'])
        return digest(normalized) == digest(reference)
    except (ValueError, TypeError, KeyError):
        return False


def controls(spec):
    """Test known answers and incorrect claimed answers before any live inference."""
    checks = []
    for task in spec['tasks']:
        _, truth = instance(task, spec['seed'])
        checks.append({'task': task['id'], 'positive': grade(truth, truth),
                       'negative': not grade({'fabricated': True}, truth),
                       'empty': not grade({}, truth)})
    if not all(all(row[k] for k in ('positive','negative','empty')) for row in checks):
        raise ValueError('grader controls failed')
    return checks
