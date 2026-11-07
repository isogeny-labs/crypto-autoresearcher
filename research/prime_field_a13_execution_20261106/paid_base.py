"""An explicitly charged, hash-labelled public-scalar factor base.

Hash draws use public curve identity only.  The base is fixed before targets
are examined.  Constructor intermediates are available only to this base arm.
Labels are supplied knowledge; they are never reported as learned relations.
"""
from hashlib import sha256
import json

from baseline import core, construct, require


def hashed(*values):
    return sha256('|'.join(map(str, values)).encode()).hexdigest()


def draw_labels(fixture, rules, meter, event):
    r = fixture['r']
    size = len(fixture['factor_base'])
    if not 0 < size <= 32 or size > (r - 1) // 2:
        raise ValueError('public-labelled base size gate')
    labels, used, trace = [], set(), []
    for index in range(size):
        for counter in range(rules['maximum_base_candidates']):
            scalar = int(hashed(rules['domain'], 'known-base',
                                fixture['ec1']['curve_uid'], index, counter), 16) % r
            meter.other['base_label_hashes'] += 1
            key = min(scalar, -scalar % r)
            meter.other['base_scalar_class_lookups'] += 1
            reason = 'identity' if not scalar else 'duplicate_sign_class' if key in used else 'selected'
            rec = dict(index=index, counter=counter, scalar=scalar, selected=reason == 'selected', reason=reason)
            trace.append(rec)
            event(dict(kind='known_base_label_candidate', record=rec))
            if reason == 'selected':
                labels.append(scalar)
                used.add(key)
                break
        else:
            raise ValueError('finite public-labelled base candidate gate exhausted')
    return labels, trace


def build(cell, rules, event, capability=None):
    require(rules, capability, cell['fixture'])
    original = cell['fixture']
    meter = core.ProgressMeter(original, event, dict(kind='known_base_construction'))
    P, r = tuple(original['P']), original['r']
    labels, trace = meter.stage('known_base_public_label_draws',
                                lambda: draw_labels(original, rules, meter, event))
    points = []

    def on_point(point, scalar, basis, origin):
        if point is None:
            return
        rec = dict(point=list(point), scalar=scalar, origin=origin, prefix=0)
        points.append(rec)
        event(dict(kind='known_base_constructor_point', record=rec))

    def setup():
        opposite = meter.neg(P)
        return construct.ScalarCurve(meter, original['p'], r, P,
                                     {1: P, r - 1: opposite}, on_point, 'P')

    curve = meter.stage('known_base_cache_setup', setup)

    def choose():
        selection = construct.select(r, list(curve.known), labels)
        meter.other['constructor_policy_candidates'] += len(selection['candidates'])
        meter.other['constructor_policy_simulated_ec_adds'] += sum(v['uncached_ec_adds'] for v in selection['candidates'])
        meter.other['constructor_policy_simulated_wrapper_adds'] += sum(v['wrapper_add_calls'] for v in selection['candidates'])
        return selection

    selection = meter.stage('known_base_constructor_selection', choose)
    constructor = construct.Constructor(curve, selection)
    base, signed_labels = [], []

    def materialize():
        for index, scalar in enumerate(labels):
            point = constructor.mul(scalar)
            if point is None:
                raise ValueError('nonzero public label constructed identity')
            opposite = meter.neg(point)
            meter.other['base_orientation_comparisons'] += 1
            if point > opposite:
                point, scalar = opposite, meter.ring.sub(0, scalar)
            base.append(dict(point=list(point)))
            signed_labels.append(scalar)
            event(dict(kind='known_base_atom', index=index, scalar=scalar, point=list(point)))
        if len({tuple(v['point']) for v in base}) != len(base):
            raise ValueError('duplicate canonical base point')
        # The scalar-only selection model does not inspect y orientation.
        # Hydrate these signs after the entire fixed constructor workload so
        # they cannot change the predicted construction cache midway through.
        for atom, scalar in zip(base, signed_labels, strict=True):
            curve.remember(tuple(atom['point']), scalar, 'canonical_base_orientation')

    meter.stage('known_base_materialization_and_signs', materialize)

    def validate():
        for atom, scalar in zip(base, signed_labels, strict=True):
            point = tuple(atom['point'])
            if not meter.e.on(point) or not meter.equal(meter.e.mul(scalar, P), point):
                raise ValueError('public base scalar certificate')
            meter.other['public_base_certificates_verified'] += 1

    meter.stage('known_base_public_scalar_verification', validate)
    fixture = {key: original[key] for key in ('p', 'a', 'b', 'r', 'P')}
    fixture['factor_base'] = base
    # Historical fixture IDs include the base; EC1 curve identity does not.
    fixture['uid'] = sha256(json.dumps(fixture, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    fixture['ec1'] = original['ec1']
    return dict(cell=dict(id=cell['id'], fixture=fixture), raw_labels=labels,
                signed_labels=signed_labels, draw_trace=trace, selection=selection,
                knowledge=points, phases=meter.phases, counters=meter.counters(), complete=True)


def unit_rows(labels):
    rows = []
    for j, scalar in enumerate(labels):
        vector = [0] * len(labels)
        vector[j] = 1
        rows.append((vector, scalar))
    return rows
