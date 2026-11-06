"""Tiny public group controls for native/helper aliases and unchanged columns."""
from copy import deepcopy
from pathlib import Path
import sys
import json
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import core, solver, check_source
import geometry, partial_solver, check_partial


@pytest.fixture(scope='module')
def control():
    rules = dict(software_control=True, domain='a14-geometry-software-control/v1',
        fields=[dict(p=211, base_size=5)], a=1, curves_per_field=1,
        maximum_curve_candidates=128, sources=16, excluded_curves=[])
    fixture = core.generate(rules, lambda v: None)['cells'][0]['fixture']
    p, r, P = fixture['p'], fixture['r'], tuple(fixture['P'])
    multiples = {j: check_source.old.multiply(p, 0, fixture['a'], j, P) for j in (1, 2, 3, 6, r-2)}
    fixture = dict(fixture, factor_base=[dict(point=list(multiples[j])) for j in (1, 2, r-2, 3)])
    labels = {2: r-2, 3: 3}
    meter = solver.Meter(fixture)
    result = meter.stage('native_geometry', lambda: geometry.build(fixture, 2, labels, meter))
    return fixture, labels, result, multiples, meter


def test_duplicate_sign_class_queries_once_and_supplies_an_explicit_old_equation(control):
    fixture, labels, result, _, meter = control
    assert geometry.check(fixture, 2, labels, result)['geometric_atoms'] == 3
    assert result['native_width'] == 4 and result['native_indices'] == [0, 1, 3]
    assert result['maximum_pair_entries'] == 12
    assert result['aliases'][2] == dict(native_index=2, geometry_index=1, representative_native=1, sign=-1)
    assert result['supplied_norm_matches'][0]['vector'] == [0, 1, 0, 0]
    assert result['supplied_norm_matches'][0]['rhs'] == 2
    assert meter.counters()['geometry_alias_records'] == 4


def test_helper_overlap_keeps_old_coordinate_and_full_native_target_certificate(control):
    fixture, labels, geom, multiples, _ = control
    known = [(0, 1), *labels.items()]
    source = [([int(k == j) for k in range(4)], value) for j, value in known]
    source += [(row['vector'], row['rhs']) for row in geom['supplied_norm_matches']]
    case = dict(width=4, target_count=1, modulus=fixture['r'], source=source,
        target=[dict(vector=[1, 1, 0, 1], outside=[fixture['r']-1], rhs=0)],
        targets=[dict(index=0, point=list(multiples[6]))])
    result = partial_solver.solve(case, known, [(1, 1)], solver.Meter(fixture))
    assert check_partial.check(case, known, [(1, 1)], result)['checked']
    assert result['unknown_basis'] == [[1, 1]]
    assert result['recoveries'][0]['scalar'] == 6
    assert check_source.old.multiply(fixture['p'], 0, fixture['a'], 6, tuple(fixture['P'])) == tuple(case['targets'][0]['point'])


@pytest.mark.parametrize('change', ['alias', 'representative', 'point', 'equation', 'sign', 'pair_count', 'label'])
def test_plain_geometry_checker_refuses_corruption(control, change):
    fixture, labels, result, _, _ = control
    value, labels = deepcopy(result), dict(labels)
    if change == 'alias': value['aliases'][2]['geometry_index'] = 0
    elif change == 'representative': value['native_indices'][2] = 2
    elif change == 'point': value['points'][0][1] += 1
    elif change == 'equation': value['supplied_norm_matches'][0]['rhs'] += 1
    elif change == 'sign': value['supplied_norm_matches'][0]['witness']['sign'] *= -1
    elif change == 'pair_count': value['maximum_pair_entries'] = 24
    elif change == 'label': labels[2] = 2
    with pytest.raises(ValueError):
        geometry.check(fixture, 2, labels, value)


def test_missing_helper_label_refuses(control):
    fixture, labels, _, _, _ = control
    with pytest.raises(ValueError, match='every helper'):
        geometry.build(fixture, 2, {2: labels[2]}, solver.Meter(fixture))


def test_geometry_and_partial_certificates_survive_json_without_integer_key_assumptions(control):
    fixture, labels, result, _, _ = control
    encoded = json.loads(json.dumps(dict(geometry=result, helper_labels=list(labels.items()))))
    restored = {j: value for j, value in encoded['helper_labels']}
    assert geometry.check(fixture, 2, restored, encoded['geometry'])['checked']


def test_zero_helper_label_and_native_overflow_refuse(control):
    fixture, labels, _, _, _ = control
    with pytest.raises(ValueError, match='scalar encoding'):
        geometry.build(fixture, 2, dict(labels, **{}) | {2: 0}, solver.Meter(fixture))
    large = dict(fixture, factor_base=fixture['factor_base']*13)
    with pytest.raises(ValueError, match='size gate'):
        geometry.build(large, 2, {}, solver.Meter(large))
