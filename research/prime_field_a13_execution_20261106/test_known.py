"""Small software controls only (p <= 211); no A13 native panel or admission."""
from copy import deepcopy
from pathlib import Path
import json
import random
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baseline import core, solver, checker, check_source, batch_check
import paid_base
import known_solver
import known_checks
import known_collection


def small_rules():
    return dict(software_control=True, domain='a13-software-control/v1',
                fields=[dict(p=211, base_size=5)], a=1, curves_per_field=1,
                maximum_curve_candidates=128, maximum_base_candidates=128,
                maximum_scalar_candidates=256, maximum_target_candidates=256,
                excluded_curves=[], sources=16, targets=3, seeds=[0],
                prefixes=[0, 16], source_prefixes=[16], target_prefixes=[1, 2, 4],
                target_queries_per_point=4, target_policies=['walk', 'hash_offset', 'general'],
                prerequisite=8, max_pair_entries=128, max_retained_rows=4096,
                max_affine_labels=8192)


@pytest.fixture(scope='module')
def base_control():
    rules = small_rules()
    cell = core.generate(rules, lambda v: None)['cells'][0]
    built = paid_base.build(cell, rules, lambda v: None)
    return rules, cell, built


def test_paid_base_complete_public_replay_and_repeatability(base_control):
    rules, cell, built = base_control
    assert known_checks.public_base(cell, rules, json.loads(json.dumps(built)))['checked']
    again = paid_base.build(cell, rules, lambda v: None)
    for key in ('raw_labels', 'signed_labels', 'knowledge', 'selection', 'cell', 'counters'):
        assert built[key] == again[key]
    assert built['counters']['public_base_certificates_verified'] == 5
    assert built['counters']['scalar_uncached_ec_adds'] > 0
    assert built['counters']['Fp.field_inv'] > 0


@pytest.mark.parametrize('change', ['sign', 'point', 'trace', 'future', 'missing', 'policy', 'counter'])
def test_public_base_checker_refuses_corruptions(base_control, change):
    rules, cell, original = base_control
    built = deepcopy(original)
    if change == 'sign':
        built['signed_labels'][0] = -built['signed_labels'][0] % cell['fixture']['r']
    elif change == 'point':
        built['cell']['fixture']['factor_base'][0]['point'][0] += 1
    elif change == 'trace':
        built['draw_trace'][0]['scalar'] += 1
    elif change == 'future':
        built['knowledge'][0]['prefix'] = 1
    elif change == 'missing':
        built['knowledge'].pop()
    elif change == 'policy':
        built['selection']['window'] = (built['selection']['window'] + 1) % 9
    elif change == 'counter':
        built['counters']['public_base_certificates_verified'] += 1
    with pytest.raises(ValueError):
        known_checks.public_base(cell, rules, built)


def test_no_native_builder_without_admission(base_control):
    rules, cell, _ = base_control
    rules = dict(rules, software_control=False, fields=[dict(p=262139, base_size=32)])
    with pytest.raises(ValueError, match='admission'):
        paid_base.build(cell, rules, lambda v: None)


def test_draw_gate_and_zero_duplicate_trace(base_control, monkeypatch):
    rules, cell, _ = base_control
    rules = dict(rules, maximum_base_candidates=3)
    monkeypatch.setattr(paid_base, 'hashed', lambda *v: '0')
    events = []
    with pytest.raises(ValueError, match='candidate gate'):
        paid_base.build(cell, rules, events.append)
    assert [v['record']['reason'] for v in events if v['kind'] == 'known_base_label_candidate'] == ['identity'] * 3
    assert any(v['kind'] == 'affine_phase' and v['phase']['status'] == 'failed' for v in events)


def matrix_case(B, U, labels, targets, r=101):
    return dict(width=len(labels), target_count=len(targets), modulus=r,
                source=paid_base.unit_rows(labels), targets=[],
                target=[dict(vector=v, outside=u,
                             rhs=(sum(a*b for a, b in zip(v, labels, strict=True)) +
                                  sum(a*b for a, b in zip(u, targets, strict=True))) % r)
                        for v, u in zip(B, U, strict=True)])


def solve_control(case):
    fixture = dict(p=101, r=case['modulus'], a=2, b=3, P=[1, 39])
    labels = [b for v, b in case['source']]
    direct = known_solver.solve(case, labels, solver.Meter(fixture))
    assert known_checks.known_case(case, labels, json.loads(json.dumps(direct)))['checked']
    joint = solver.solve(case, 'sparse_joint', solver.Meter(fixture))
    assert [(v['identifiable'], v['scalar']) for v in direct['recoveries']] == [(v['identifiable'], v['scalar']) for v in joint['recoveries']]
    return direct


@pytest.mark.parametrize('case', [
    matrix_case([[1, 100], [0, 1]], [[100, 0], [1, 1]], [3, 8], [7, 11]),
    matrix_case([[1], [100]], [[1, 1], [100, 100]], [3], [7, 11]),
    matrix_case([[], []], [[2, 0], [1, 1]], [], [7, 11]),
    matrix_case([], [], [3, 8], [7, 11]),
    matrix_case([[], []], [[0, 0], [0, 0]], [], [7, 11]),
    matrix_case([], [], [], []),
])
def test_full_and_deficient_target_spans(case):
    solve_control(case)


def test_cross_target_equation_alone_does_not_disclose_individual_logs():
    case = matrix_case([[1], [100]], [[1, 1], [100, 100]], [3], [7, 11])
    direct = solve_control(case)
    assert not any(v['identifiable'] for v in direct['recoveries'])


def test_random_small_consistent_systems_against_joint():
    rng = random.Random(713)
    for _ in range(32):
        width, nt, n = rng.randrange(5), rng.randrange(5), rng.randrange(10)
        labels = [rng.randrange(101) for _ in range(width)]
        target_values = [rng.randrange(101) for _ in range(nt)]
        B = [[rng.randrange(101) for _ in range(width)] for _ in range(n)]
        U = [[rng.randrange(101) for _ in range(nt)] for _ in range(n)]
        solve_control(matrix_case(B, U, labels, target_values))


@pytest.mark.parametrize('change', ['labels', 'unit', 'rhs', 'weights', 'negative', 'residual', 'counter'])
def test_solver_checker_and_admission_refuse_corruptions(change):
    case = matrix_case([[1], [1]], [[100, 0], [0, 0]], [3], [7, 11])
    labels = [3]
    direct = solve_control(case)
    if change == 'labels':
        with pytest.raises(ValueError, match='unit equation'):
            known_solver.solve(case, [4], solver.Meter(dict(p=101, r=101, a=2, b=3)))
        return
    if change == 'unit':
        case['source'][0][0][0] = 2
        with pytest.raises(ValueError, match='unit equation'):
            known_solver.solve(case, labels, solver.Meter(dict(p=101, r=101, a=2, b=3)))
        return
    if change == 'rhs':
        direct['reduced_rhs'][0] += 1
    elif change == 'weights':
        direct['recoveries'][0]['original_row_weights'][0] += 1
    elif change == 'negative':
        direct['recoveries'][1]['identifiable'] = True
    elif change == 'residual':
        direct['recoveries'][1]['residual'][1] = 0
    elif change == 'counter':
        direct['counters']['Fr.field_sub'] += 1
    with pytest.raises(ValueError):
        known_checks.known_case(case, labels, direct)


def test_source_free_collection_all_policies_and_prefixes(base_control):
    rules, original, built = base_control
    norm = core.collect_sources(deepcopy(original), rules, lambda v: None)
    known = known_collection.collect(built, norm['target_generation'], rules, lambda v: None)
    verified, triples = known_checks.collection(built, norm['target_generation'], known)
    assert verified['source_queries'] == 0
    assert 'source_queries' not in known['collection_counters']
    batch_check.records(built['cell'], known['query_engine_records'], [v['point'] for v in norm['target_generation']['targets']])
    cell = built['cell']
    recipe_meter = solver.Meter(cell['fixture'])
    recipes = core.recipes(cell, known, rules, recipe_meter, lambda v: None)
    cache = core.QueryCache(cell, known, rules, lambda v: None)
    oracle = checker.GroupOracle(cell['fixture'], known['target_generation']['targets'])
    for policy in rules['target_policies']:
        branch = core.construct_branch(cell, known, rules, recipes['policies'][policy], 'known', 0, policy, cache, lambda v: None)
        assert checker.branch(cell, known, rules, recipes['policies'][policy], branch, cache, oracle)['checked']
        for budget in rules['target_prefixes']:
            case = known_collection.case_input(cell, known, branch, cache, budget, solver.Meter(cell['fixture']))
            expected = checker.expected_case(cell, known, branch, cache, budget, 'anchors')
            assert core.source.code(case) == core.source.code(expected)
            result = known_solver.solve(case, built['signed_labels'], solver.Meter(cell['fixture']))
            # The full original-unit certificate is also checked against the
            # independently implemented group law, without fictitious phases.
            for t, rec in enumerate(result['recoveries']):
                if rec['identifiable']:
                    assert check_source.old.multiply(cell['fixture']['p'], 0, cell['fixture']['a'], rec['scalar'], tuple(cell['fixture']['P'])) == tuple(case['targets'][t]['point'])
            assert known_checks.known_case(case, built['signed_labels'], result)['checked']
    assert checker.query_cache(cell, known, cache, triples)['checked']


@pytest.mark.parametrize('change', ['source', 'knowledge', 'projection', 'pair', 'miss', 'row', 'anchor'])
def test_source_free_collection_checker_rejects_leaks_and_corruptions(base_control, change):
    rules, original, built = base_control
    norm = core.collect_sources(deepcopy(original), rules, lambda v: None)
    known = known_collection.collect(built, norm['target_generation'], rules, lambda v: None)
    if change == 'source':
        known['arms']['known']['sources'].append(dict(scalar=2, point=[1, 1]))
    elif change == 'knowledge':
        known['arms']['known']['knowledge'] = known['arms']['known']['knowledge'] + [dict(scalar=2, point=[1, 1])]
    elif change == 'projection':
        known['projection']['U'] -= 1
    elif change == 'pair':
        known['pairs'].pop()
    elif change == 'miss':
        known['target_collection']['trace'][0]['wanted'] = [1, 1]
    elif change == 'row':
        known['target_collection']['rows'][0]['coefficients'][0] += 1
    elif change == 'anchor':
        known['arms']['known']['anchors'][0]['source_scalar'] += 1
    with pytest.raises(ValueError):
        known_checks.collection(built, norm['target_generation'], known)
