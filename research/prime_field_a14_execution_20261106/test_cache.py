"""Tiny physical query aliases never import affine coefficient knowledge."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import solver
from test_geometry import control
from query_index import QueryIndex
from check_query import Oracle
from target_cache import TargetCache


def rules():
    return dict(software_control=True, fields=[dict(p=211, base_size=2)],
                max_pair_entries=128, max_retained_rows=4096, targets=1,
                target_policies=['walk'], target_queries_per_point=2)


def setup(control):
    fixture, labels, geom, multiples, _ = control
    meter = solver.Meter(fixture)
    index = QueryIndex(fixture, geom, rules(), meter, lambda v: None)
    natural = index.query(multiples[6], meter, dict(target=True, natural=True))
    cache = TargetCache(index, [natural], rules(), lambda v: None)
    return multiples, index, natural, cache, Oracle(fixture, geom)


def test_natural_and_cross_label_aliases_share_only_geometry(control):
    multiples, index, natural, cache, oracle = setup(control)
    assert cache.request(multiples[6], dict(target_index=0, alpha=0, beta=1)) == 0
    assert cache.request(multiples[6], dict(target_index=1, alpha=9, beta=3)) == 0
    assert len(index.engines.records) == 1
    assert len(cache.records) == 1 and cache.records[0]['rows'] == natural['rows']
    assert all(row['source_scalar'] == 0 for row in cache.records[0]['rows'])
    assert all('outside' not in row for row in cache.records[0]['rows'])
    assert oracle.check(cache.records[0], index.pairs)['checked']
    assert cache.meter.counters()['logical_target_requests'] == 2
    assert cache.meter.counters()['target_cache_hits'] == 2


def test_new_point_queries_once_then_reuses_checked_native_rows(control):
    multiples, index, natural, cache, oracle = setup(control)
    assert cache.request(multiples[1], dict(target_index=0, index=1)) == 1
    assert cache.request(multiples[1], dict(target_index=0, index=1)) == 1
    assert len(index.engines.records) == 2
    assert oracle.check(cache.records[1], index.pairs)['checked']
    assert cache.meter.counters()['target_cache_records_added'] == 1
    assert cache.meter.counters()['signed_point_queries'] == 6


def test_endpoint_cap_refuses_with_paid_lookup_without_an_extra_query(control):
    multiples, index, natural, cache, oracle = setup(control)
    cache.request(multiples[1], {})
    with pytest.raises(ValueError, match='cache size gate'):
        cache.request(None, {})
    assert len(cache.records) == 2 and len(index.engines.records) == 2
    assert cache.meter.counters()['logical_target_requests'] == 2


def test_seed_does_not_accept_duplicate_or_missing_targets(control):
    multiples, index, natural, cache, oracle = setup(control)
    with pytest.raises(ValueError, match='census'):
        TargetCache(index, [], rules(), lambda v: None)
    with pytest.raises(ValueError, match='duplicate natural'):
        TargetCache(index, [natural, natural], dict(rules(), targets=2), lambda v: None)
