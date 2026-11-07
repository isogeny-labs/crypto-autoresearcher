"""Tiny signed-triple/miss, alias, vector and retained-failure controls."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import solver, batch_check
from test_geometry import control
from query_index import QueryIndex
from check_query import Oracle


def rules():
    return dict(software_control=True, fields=[dict(p=211, base_size=2)],
                max_pair_entries=128, max_retained_rows=4096)


def setup(control, event=lambda value: None):
    fixture, labels, geom, multiples, _ = control
    meter = solver.Meter(fixture)
    index = QueryIndex(fixture, geom, rules(), meter, event)
    return fixture, geom, multiples, meter, index, Oracle(fixture, geom)


def test_distinct_geometry_emits_native_width_and_checks_every_miss(control):
    fixture, geom, multiples, meter, index, oracle = setup(control)
    endpoints = [multiples[6], multiples[1], None]
    for i, Q in enumerate(endpoints):
        record = meter.stage('query'+str(i), lambda: index.query(Q, meter, dict(software_control=True, index=i)))
        checked = oracle.check(record, index.pairs)
        assert checked['native_width'] == 4 and checked['geometric_atoms'] == 3
        assert checked['signed_queries'] == 6
        assert all(len(row['coefficients']) == 4 and row['coefficients'][2] == 0 for row in record['rows'])
        if i == 0:
            assert len(record['rows']) == 1 and record['rows'][0]['triple'] == [0, 1, 3]
        if i == 1:
            assert record['rows'] == []
    # This old checker consumes a geometric point array, not native coefficient
    # metadata.  The temporary view is not a published replacement fixture UID.
    geometric_view = dict(fixture, factor_base=[fixture['factor_base'][j] for j in geom['native_indices']])
    assert batch_check.records(dict(fixture=geometric_view), index.engines.records,
                               [None if Q is None else list(Q) for Q in endpoints])['checked']
    assert meter.counters()['signed_point_queries'] == 18
    assert len(index.pairs) == 12


@pytest.mark.parametrize('change', ['pair', 'mapping', 'row', 'duplicate_alias', 'alias_equivalent', 'miss', 'accepted'])
def test_independent_oracle_refuses_mapping_equation_and_miss_corruptions(control, change):
    fixture, geom, multiples, meter, index, oracle = setup(control)
    record = index.query(multiples[6], meter, {})
    if change == 'pair': index.pairs.pop()
    elif change == 'mapping': index.pairs[0]['native_indices'][0] = 2
    elif change == 'row': record['rows'][0]['coefficients'][0] += 1
    elif change == 'duplicate_alias': record['rows'][0]['triple'][1] = 2
    elif change == 'alias_equivalent':
        # This is a valid group equation using the other native encoding of
        # the same geometric atom.  It must not create another witness.
        record['rows'][0].update(triple=[0, 2, 3], signs=[1, -1, 1],
                                coefficients=[1, 0, fixture['r']-1, 1])
    elif change == 'miss': record['trace'][0]['wanted'] = [1, 1]
    elif change == 'accepted': record['trace'][-2]['accepted'] = []
    with pytest.raises(ValueError):
        oracle.check(record, index.pairs)


def test_native_query_needs_admission_before_index_work(control):
    fixture, _, geom, _, _ = control
    fixture = dict(fixture, p=8191)
    r = dict(rules(), software_control=False, fields=[dict(p=8191, base_size=2)])
    meter, events = solver.Meter(fixture), []
    with pytest.raises(ValueError, match='admission'):
        QueryIndex(fixture, geom, r, meter, events.append)
    assert not meter.phases and not events


def test_pair_guard_retains_paid_prefix_and_refuses_without_truncation(control):
    fixture, _, geom, _, _ = control
    meter, events = solver.Meter(fixture), []
    with pytest.raises(ValueError, match='pair size gate'):
        QueryIndex(fixture, geom, dict(rules(), max_pair_entries=8), meter, events.append)
    assert meter.phases[-1]['status'] == 'failed'
    assert len([v for v in events if v['kind'] == 'geometric_pair']) == 9
    assert meter.counters()['pair_table_insertions'] == 9


def test_query_failure_retains_vector_work_and_accepted_native_prefix(control):
    fixture, _, geom, multiples, _ = control
    events = []
    def event(value):
        events.append(value)
        if value['kind'] == 'geometric_relation':
            raise RuntimeError('injected after native accepted row')
    meter = solver.Meter(fixture)
    index = QueryIndex(fixture, geom, rules(), meter, event)
    with pytest.raises(RuntimeError, match='injected'):
        meter.stage('query_failure', lambda: index.query(multiples[6], meter, {}))
    assert meter.phases[-1]['status'] == 'failed'
    assert meter.counters()['geometric_relation_certificates'] == 1
    assert any(v['kind'] == 'geometric_query_failed' and v['partial_rows'] for v in events)
    assert index.engines.records[0]['equal'] is True
