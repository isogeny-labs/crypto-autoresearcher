"""Independent plain-group/public-scalar constructor control at explicit sizes."""
from hashlib import sha256
import json
from shared import check_source
from baseline import checker
import known_checks as parent


def check(original_cell, rules, size, actual):
    original = original_cell['fixture']
    f = actual['cell']['fixture']
    r, p, a, P = original['r'], original['p'], original['a'], tuple(original['P'])
    if actual['public_base_size'] != size:
        raise ValueError('public base control size')
    labels, used, trace = [], set(), []
    for index in range(size):
        for counter in range(rules['maximum_base_candidates']):
            text = '|'.join(map(str, (rules['domain'], 'known-base', original['ec1']['curve_uid'], index, counter)))
            scalar = int(sha256(text.encode()).hexdigest(), 16) % r
            key = min(scalar, -scalar % r)
            reason = 'identity' if not scalar else 'duplicate_sign_class' if key in used else 'selected'
            trace.append(dict(index=index, counter=counter, scalar=scalar, selected=reason == 'selected', reason=reason))
            if reason == 'selected':
                labels.append(scalar)
                used.add(key)
                break
        else:
            raise ValueError('independent known-base draw gate')
    if labels != actual['raw_labels'] or trace != actual['draw_trace']:
        raise ValueError('known-base draw trace')
    candidates, window = checker.expected_selection(r, {0, 1, r - 1}, labels)
    if actual['selection']['candidates'] != candidates or actual['selection']['window'] != window:
        raise ValueError('known-base constructor selection')
    integer = checker.IntegerConstructor(r, {0, 1, r - 1}, window)
    for scalar in labels:
        integer.mul(scalar)
    expected_base, signed = [], []
    for scalar in labels:
        point = check_source.old.multiply(p, 0, a, scalar, P)
        if point is None:
            raise ValueError('identity public base point')
        opposite = (point[0], -point[1] % p)
        if point > opposite:
            point, scalar = opposite, -scalar % r
        expected_base.append(dict(point=list(point)))
        signed.append(scalar)
    if f['factor_base'] != expected_base or actual['signed_labels'] != signed:
        raise ValueError('known-base canonical point/sign')
    expected_fixture = {key: original[key] for key in ('p', 'a', 'b', 'r', 'P')}
    expected_fixture['factor_base'] = expected_base
    uid = sha256(json.dumps(expected_fixture, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if f != dict(expected_fixture, uid=uid, ec1=original['ec1']) or actual['cell']['id'] != original_cell['id']:
        raise ValueError('known-base curve or fixture identity')
    knowledge = actual['knowledge']
    expected_known = integer.known | set(signed)
    if len(knowledge) != len({v['scalar'] for v in knowledge}) or {v['scalar'] for v in knowledge} != expected_known - {0}:
        raise ValueError('known-base constructor knowledge completeness')
    for item in knowledge:
        if item['prefix'] != 0 or tuple(item['point']) != check_source.old.multiply(p, 0, a, item['scalar'], P):
            raise ValueError('known-base false public knowledge')
    counts = parent.phase_counts(actual)
    if counts.get('scalar_uncached_ec_adds', 0) != integer.calls or counts.get('scalar_wrapper_add_calls', 0) != integer.api:
        raise ValueError('known-base physical constructor prediction')
    if counts.get('public_base_certificates_verified', 0) != size or counts.get('base_label_hashes', 0) != len(trace):
        raise ValueError('known-base certificate or draw counts')
    return dict(checked=True, base_size=size, draw_records=len(trace), constructor_points=len(knowledge), supplied_equations=size)
