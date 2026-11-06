"""End-to-end tiny native rows, symbolic targets and lifted certificates."""
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import core, solver, check_source
from baseline import checker
import known_checks
from test_mixed import controls, rules
import affine_branch, native_case, partial_solver, check_partial
import information, check_information
from target_cache import TargetCache


def branch_for(controls, name, policy):
    original, _, prepared, _, collected = controls
    p, c = prepared[name], collected[name]
    cache = TargetCache(c.query_index, c['natural_records'], rules(), lambda v: None)
    meter = solver.Meter(original['fixture'])
    recipes = core.recipes(original, c, rules(), meter, lambda v: None)
    assert checker.recipes(original, rules(), recipes)
    arm = 'known' if name.startswith('known') else 'ap0'
    prefix = 0 if name.startswith('known') else rules()['sources']
    branch = affine_branch.build(p['cell'], c, rules(), recipes['policies'][policy],
        arm, prefix, policy, cache, lambda v: None)
    oracle = checker.GroupOracle(p['cell']['fixture'], c['target_generation']['targets'])
    assert checker.branch(p['cell'], c, rules(), recipes['policies'][policy], branch, cache, oracle)['checked']
    return p, c, branch, cache


@pytest.mark.parametrize('name', ['norm', 'hybrid', 'known32', 'known48'])
@pytest.mark.parametrize('policy', ['walk', 'hash_offset', 'general'])
def test_native_rows_partial_joint_and_full_joint_agree_with_public_targets(controls, name, policy):
    p, c, branch, cache = branch_for(controls, name, policy)
    scope = 'supplied' if name.startswith('known') else 'anchors'
    # Tiny199-order known48 produces far more relations per query than native
    # holdouts. Its positive control uses budget2; budget3 refusal is explicit.
    budget = 2 if name == 'known48' else 3
    meter = solver.Meter(p['cell']['fixture'])
    case = meter.stage('native_matrix_assembly', lambda: native_case.build(p, c, branch, cache, budget, scope, meter))
    assert json.loads(json.dumps(case)) == json.loads(json.dumps(native_case.expected(p, c, branch, cache, budget, scope)))
    fixture = p['cell']['fixture']
    partial = partial_solver.solve(case, p['known'], p['basis'], solver.Meter(fixture))
    joint = solver.solve(case, 'sparse_joint', solver.Meter(fixture))
    assert check_partial.check(case, p['known'], p['basis'], partial)['checked']
    assert known_checks.joint_case(case, joint)['checked']
    assert [(v['identifiable'], v['scalar']) for v in partial['recoveries']] == [
        (v['identifiable'], v['scalar']) for v in joint['recoveries']]
    for rec, target in zip(partial['recoveries'], case['targets'], strict=True):
        if rec['identifiable']:
            assert check_source.old.multiply(fixture['p'], 0, fixture['a'], rec['scalar'], tuple(fixture['P'])) == tuple(target['point'])
    # Helper-native columns are substituted; old signed unknown coordinates
    # retain the same order even when an owned cache supplies their values.
    assert partial['unknown_basis'] == p['basis']
    if name.startswith('known'):
        assert p['basis'] == [] and all(v['kind'] == 'supplied_native_unit' for v in case['source_origins'])
    assert all(row['source_scalar'] == 0 for record in cache.records for row in record['rows'])


def test_dense_tiny_known48_gate_retains_exact_materialized_failure_prefix(controls):
    p, c, branch, cache = branch_for(controls, 'known48', 'general')
    events = []
    meter = core.ProgressMeter(p['cell']['fixture'], events.append, dict(software_control=True))
    with pytest.raises(ValueError, match='matrix size gate') as error:
        meter.stage('native_matrix_assembly', lambda: native_case.build(p, c, branch, cache, 3, 'supplied', meter))
    partial = error.value.partial_case
    assert len(partial['source'])+len(partial['target']) == 4097
    assert meter.counters()['native_target_rows_assembled'] == len(partial['target'])
    assert events[0]['partial_case'] == partial
    assert meter.phases[-1]['status'] == 'failed'


@pytest.mark.parametrize('scope', ['relations', 'anchors'])
def test_old_coordinate_supplied_matches_stay_explicit_in_every_scope_and_budget(controls, scope):
    p, c, branch, cache = branch_for(controls, 'hybrid', 'general')
    for budget in (1, 2, 3):
        case = native_case.build(p, c, branch, cache, budget, scope, solver.Meter(p['cell']['fixture']))
        assert sum(v['kind'] == 'supplied_owned_cache_match' for v in case['source_origins']) == len(p['supplied'])
        assert len(case['source']) >= len(p['known'])+len(p['supplied'])
        assert json.loads(json.dumps(case)) == json.loads(json.dumps(native_case.expected(p, c, branch, cache, budget, scope)))
        if scope == 'relations':
            assert not any(v['kind'] == 'constructed_source_anchor' for v in case['source_origins'])
            assert all(v['kind'] == 'decomposition' for v in case['target'])


def test_branch_admission_refuses_before_target_work(controls):
    _, _, prepared, _, collected = controls
    p, c = prepared['norm'], collected['norm']
    cache = TargetCache(c.query_index, c['natural_records'], rules(), lambda v: None)
    events = []
    with pytest.raises(ValueError, match='admission'):
        affine_branch.build(p['cell'], c, dict(rules(), software_control=False), [],
                            'ap0', 16, 'walk', cache, events.append)
    assert events == []


@pytest.mark.parametrize('scope', ['relations', 'anchors'])
def test_matched_collected_native_information_has_dense_rank_and_old_kernel_checks(controls, scope):
    norm_p, norm_c, norm_branch, norm_cache = branch_for(controls, 'norm', 'general')
    hybrid_p, hybrid_c, hybrid_branch, hybrid_cache = branch_for(controls, 'hybrid', 'general')
    norm = native_case.build(norm_p, norm_c, norm_branch, norm_cache, 2, scope,
                             solver.Meter(norm_p['cell']['fixture']))
    hybrid = native_case.build(hybrid_p, hybrid_c, hybrid_branch, hybrid_cache, 2, scope,
                               solver.Meter(hybrid_p['cell']['fixture']))
    result = information.compare(norm, norm_p, hybrid, hybrid_p, solver.Meter(hybrid_p['cell']['fixture']))
    assert check_information.check(norm, norm_p, hybrid, hybrid_p, result)['checked']
    assert sum(result['increments'].values()) == result['delta_vs_old']
    assert [v['phase'] for v in result['phases']][-1] == 'outside_elimination_and_native_lifting'
