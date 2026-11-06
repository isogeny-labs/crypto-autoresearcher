"""Small public-group controls of actual owned collection and source-free arms."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import core, solver
import public_base, mixed_collection, check_mixed


def rules():
    return dict(software_control=True, domain='a14-mixed-collection-software/v1',
        fields=[dict(p=211, base_size=5)], a=1, curves_per_field=1,
        maximum_curve_candidates=128, sources=16, prerequisite=4, excluded_curves=[],
        seeds=[0], maximum_scalar_candidates=256, maximum_target_candidates=256,
        public_base_sizes=[16, 32, 48], maximum_base_candidates=256,
        max_pair_entries=8192, max_retained_rows=4096, targets=2,
        target_policies=['walk', 'hash_offset', 'general'], target_queries_per_point=3,
        target_prefixes=[1, 2, 3], max_affine_labels=4096)


@pytest.fixture(scope='module')
def controls():
    r = rules()
    original = core.generate(r, lambda v: None)['cells'][0]
    # Independently execute all three paid constructors before targets exist.
    built = {n: public_base.build(original, r, n, lambda v: None) for n in (16, 32, 48)}
    prepared = {name: mixed_collection.prepare(original, r, helper, lambda v: None)
                for name, helper in [('norm', None), ('hybrid', built[16])]}
    for n in (32, 48):
        prepared['known'+str(n)] = mixed_collection.prepare_known(built[n], r, lambda v: None)
    meter = solver.Meter(original['fixture'])
    targets = meter.stage('target_generation', lambda: core.old.targets(original, r, meter, lambda v: None))
    collected = {name: (mixed_collection.collect_known if name.startswith('known') else mixed_collection.collect)(
        value, targets, r, lambda v: None) for name, value in prepared.items()}
    return original, built, prepared, targets, collected


@pytest.mark.parametrize('name', ['norm', 'hybrid', 'known32', 'known48'])
def test_independent_owned_preparation_and_full_geometric_collection(controls, name):
    original, built, prepared, targets, collected = controls
    before = json.loads(json.dumps(original))
    p = json.loads(json.dumps(prepared[name]))
    c = json.loads(json.dumps(collected[name]))
    if name.startswith('known'):
        result = check_mixed.known_preparation(original, rules(), built[int(name[5:])], p)
    else:
        result = check_mixed.preparation(original, rules(), built[16] if name == 'hybrid' else None, p)
    checked, _ = check_mixed.collection(p, rules(), c)
    assert result['checked'] and checked['checked']
    assert checked['physical_query_endpoints'] == (2 if name.startswith('known') else 34)
    assert original == before
    assert c['target_generation'] == targets
    if name.startswith('known'):
        assert len(c['arms']) == 1 and c['arms']['known']['sources'] == []
    else:
        assert prepared['norm']['selection'] == p['selection']
        assert prepared['norm']['basis'] == p['basis']
        for arm in c['arms'].values():
            assert all(row['source_scalar'] == 0 for record in arm['query_records'] for row in record['rows'])


@pytest.mark.parametrize('change', ['prerequisite', 'borrowed', 'basis', 'schedule', 'helper_unit'])
def test_prelude_checker_refuses_false_paid_scope_or_changed_old_coordinates(controls, change):
    original, built, prepared, _, _ = controls
    actual = deepcopy(prepared['hybrid'])
    if change == 'prerequisite': actual['prerequisites'][0]['scalar'] += 1
    elif change == 'borrowed': actual['initial'][0]['origin'] = 'other_paid_known48'
    elif change == 'basis': actual['basis'].reverse(); actual['basis'].append([0, 1])
    elif change == 'schedule': actual['selection']['orders']['ap0'][0] += 1
    elif change == 'helper_unit': actual['known'][-1][1] += 1
    with pytest.raises(ValueError):
        check_mixed.preparation(original, rules(), built[16], actual)


@pytest.mark.parametrize('change', ['query', 'rhs', 'anchor', 'knowledge', 'natural', 'engine', 'counter'])
def test_collection_checker_refuses_false_geometry_or_future_cache(controls, change):
    _, _, prepared, _, collected = controls
    actual = deepcopy(collected['hybrid'])
    arm = actual['arms']['ap0']
    if change == 'query': arm['query_records'][0]['trace'][0]['bucket'] = [-1]
    elif change == 'rhs': arm['rows'][0]['source_scalar'] += 1
    elif change == 'anchor': arm['anchors'].pop()
    elif change == 'knowledge': arm['knowledge'][0]['origin'] = 'other_source_program'
    elif change == 'natural': actual['natural_records'].reverse()
    elif change == 'engine': actual['query_engine_records'].pop()
    elif change == 'counter': arm['counters']['owned_knowledge_base_lookups'] += 1
    with pytest.raises(ValueError):
        check_mixed.collection(prepared['hybrid'], rules(), actual)


def test_missing_admission_refuses_before_collection_or_paid_prerequisites(controls):
    original, built, prepared, targets, _ = controls
    native = dict(rules(), software_control=False)
    events = []
    with pytest.raises(ValueError, match='admission'):
        mixed_collection.prepare(original, native, built[16], events.append)
    with pytest.raises(ValueError, match='admission'):
        mixed_collection.collect(prepared['norm'], targets, native, events.append)
    assert events == []


def test_hybrid_cannot_accept_known32_as_a_free_helper_prefix(controls):
    original, built, _, _, _ = controls
    with pytest.raises(ValueError, match='separate paid helper16'):
        mixed_collection.prepare(original, rules(), built[32], lambda v: None)


def test_multiple_seed_query_order_survives_sorted_json_reload(controls):
    original = controls[0]
    value = dict(rules(), seeds=[0, 1])
    prepared = mixed_collection.prepare(original, value, None, lambda v: None)
    collected = mixed_collection.collect(prepared, controls[3], value, lambda v: None)
    checked, _ = check_mixed.collection(json.loads(json.dumps(prepared, sort_keys=True)), value,
                                        json.loads(json.dumps(collected, sort_keys=True)))
    assert checked['physical_query_endpoints'] == 66
