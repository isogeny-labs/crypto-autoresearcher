"""Explicit paid16/32/48 constructor controls on the tiny211 test curve only."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_geometry import control
import public_base, check_base


def rules():
    return dict(software_control=True, domain='a14-paid-base-software-control/v1',
        fields=[dict(p=211, base_size=2)], public_base_sizes=[16, 32, 48],
        maximum_base_candidates=256)


@pytest.fixture(scope='module')
def built_controls(control):
    fixture = control[0]
    cell = dict(id='p211-software', fixture=fixture)
    values = {size: public_base.build(cell, rules(), size, lambda v: None) for size in (16, 32, 48)}
    return cell, values


def test_each_size_executes_its_own_constructor_and_public_certificates(built_controls):
    cell, values = built_controls
    for size, value in values.items():
        restored = json.loads(json.dumps(value))
        checked = check_base.check(cell, rules(), size, restored)
        assert checked['base_size'] == size and checked['supplied_equations'] == size
        assert value['counters']['public_base_certificates_verified'] == size
        assert len(value['cell']['fixture']['factor_base']) == size
        assert value['selection']['full_horizon'] is True
    assert values[16]['raw_labels'] == values[32]['raw_labels'][:16] == values[48]['raw_labels'][:16]
    assert values[32]['raw_labels'] == values[48]['raw_labels'][:32]
    assert values[16]['knowledge'] is not values[32]['knowledge'] and values[32]['knowledge'] is not values[48]['knowledge']


def test_small_constructor_selection_is_not_a_slice_of_future_work(built_controls):
    cell, values = built_controls
    # This equality checks the independently replayed16-label workload, not an
    # assumption that constructor windows or intermediate sets must differ.
    assert check_base.check(cell, rules(), 16, values[16])['checked']
    assert values[16]['counters']['public_base_certificates_verified'] == 16
    assert values[48]['counters']['public_base_certificates_verified'] == 48
    assert len(values[16]['draw_trace']) <= len(values[48]['draw_trace'])


@pytest.mark.parametrize('change', ['size', 'sign', 'future', 'policy', 'counter'])
def test_explicit_size_checker_rejects_false_prefix_and_provenance(built_controls, change):
    cell, values = built_controls
    value = deepcopy(values[16])
    if change == 'size': value['public_base_size'] = 48
    elif change == 'sign': value['signed_labels'][0] = -value['signed_labels'][0] % cell['fixture']['r']
    elif change == 'future': value['knowledge'] = deepcopy(values[48]['knowledge'])
    elif change == 'policy': value['selection']['window'] = (value['selection']['window']+1) % 9
    elif change == 'counter': value['counters']['public_base_certificates_verified'] = 48
    with pytest.raises(ValueError):
        check_base.check(cell, rules(), 16, value)


def test_undeclared_size_and_native_input_refuse_before_builder_work(control):
    cell = dict(id='p211-software', fixture=control[0])
    events = []
    with pytest.raises(ValueError, match='declared control'):
        public_base.build(cell, rules(), 49, events.append)
    with pytest.raises(ValueError, match='admission'):
        public_base.build(cell, dict(rules(), software_control=False), 48, events.append)
    assert events == []


def test_full_native48_geometry_oracle_and_lifted_target_control(built_controls):
    from shared import solver, batch_check
    import geometry, partial_solver, check_partial
    from query_index import QueryIndex
    from check_query import Oracle
    built = built_controls[1][48]
    fixture = built['cell']['fixture']
    labels = dict(enumerate(built['signed_labels']))
    meter = solver.Meter(fixture)
    geom = geometry.build(fixture, 0, labels, meter)
    assert geometry.check(fixture, 0, labels, geom)['geometric_atoms'] == 48
    index = QueryIndex(fixture, geom, dict(rules(), max_pair_entries=8192, max_retained_rows=4096), meter, lambda v: None)
    assert len(index.pairs) == 4512
    Q = tuple(fixture['factor_base'][0]['point'])
    record = index.query(Q, meter, dict(software_control=True, known48=True))
    assert Oracle(fixture, geom).check(record, index.pairs)['checked']
    assert batch_check.records(dict(fixture=fixture), index.engines.records, [list(Q)])['checked']
    case = dict(width=48, target_count=1, modulus=fixture['r'],
        source=public_base.unit_rows(built['signed_labels']), targets=[dict(index=0, point=list(Q))],
        target=[dict(vector=row['coefficients'], outside=[fixture['r']-1], rhs=0) for row in record['rows']])
    result = partial_solver.solve(case, list(labels.items()), [], solver.Meter(fixture))
    assert check_partial.check(case, list(labels.items()), [], result)['checked']
    assert result['recoveries'][0]['scalar'] == built['signed_labels'][0]
