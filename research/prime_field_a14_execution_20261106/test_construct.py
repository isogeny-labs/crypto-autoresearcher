"""Public scalar program/cold-cache controls on the fixed tiny211 fixture."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import check_source
from test_geometry import control
import source_construct, check_construct, public_base


def rules():
    return dict(software_control=True, fields=[dict(p=211, base_size=2)], sources=16,
                domain='a14-source-constructor-software/v1', public_base_sizes=[16], maximum_base_candidates=256)


def initial(fixture, helper):
    if helper:
        value = public_base.build(dict(id='tiny-source', fixture=fixture), rules(), 16, lambda v: None)
        return [dict(point=v['point'], scalar=v['scalar'], origin='own_paid_helper16') for v in value['knowledge']]
    p, r, a, P = fixture['p'], fixture['r'], fixture['a'], tuple(fixture['P'])
    return [dict(point=list(check_source.old.multiply(p, 0, a, s, P)), scalar=s, origin='own_paid_software_seed') for s in (1, r-1)]


def program(fixture, kind):
    if kind == 'ap':
        ap = dict(a=3, d=5)
        return [(3+5*i) % fixture['r'] for i in range(16)], ap
    return [1+(13+7*i) % (fixture['r']-1) for i in range(16)], None


@pytest.mark.parametrize('kind', ['ap', 'hash'])
@pytest.mark.parametrize('helper', [False, True])
def test_full_horizon_source_prediction_and_plain_public_images(control, kind, helper):
    fixture = control[0]
    paid = initial(fixture, helper)
    values, ap = program(fixture, kind)
    actual = source_construct.build(fixture, rules(), paid, values, kind, ap, kind+'0', lambda v: None)
    assert check_construct.check(fixture, rules(), paid, values, kind, ap, json.loads(json.dumps(actual)))['checked']
    assert [v['scalar'] for v in actual['sources']] == values
    assert actual['selection']['full_horizon'] is True


@pytest.mark.parametrize('change', ['source_point', 'order', 'policy', 'future', 'missing', 'origin', 'counter'])
def test_independent_source_checker_refuses_future_cache_or_false_points(control, change):
    fixture = control[0]
    paid = initial(fixture, False)
    values, ap = program(fixture, 'ap')
    actual = source_construct.build(fixture, rules(), paid, values, 'ap', ap, 'ap0', lambda v: None)
    if change == 'source_point': actual['sources'][0]['point'][0] += 1
    elif change == 'order': actual['sources'][0]['scalar'] += 1
    elif change == 'policy': actual['selection']['window'] = (actual['selection']['window']+1) % 9
    elif change == 'future': next(v for v in actual['knowledge'] if v['prefix'])['prefix'] = 0
    elif change == 'missing': actual['knowledge'].pop()
    elif change == 'origin': next(v for v in actual['knowledge'] if not v['prefix'])['paid_origin'] = 'other_known48_arm'
    elif change == 'counter': actual['counters']['scalar_wrapper_add_calls'] += 1
    with pytest.raises(ValueError):
        check_construct.check(fixture, rules(), paid, values, 'ap', ap, actual)


def test_unadmitted_or_changed_source_program_refuses(control):
    fixture = control[0]
    values, ap = program(fixture, 'ap')
    with pytest.raises(ValueError, match='admission'):
        source_construct.build(fixture, dict(rules(), software_control=False), [], values, 'ap', ap, 'ap0', lambda v: None)
    with pytest.raises(ValueError, match='AP full-horizon'):
        source_construct.build(fixture, rules(), [], values, 'ap', dict(a=3, d=4), 'ap0', lambda v: None)
