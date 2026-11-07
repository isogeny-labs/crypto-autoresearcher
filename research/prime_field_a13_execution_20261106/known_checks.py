"""Plain group and dense linear-algebra controls, separate from producers."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json

from baseline import checker, check_source, check_solver


def public_base(original_cell, rules, actual):
    original = original_cell['fixture']
    f = actual['cell']['fixture']
    r, p, a, P = original['r'], original['p'], original['a'], tuple(original['P'])
    size = len(original['factor_base'])
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
    counts = phase_counts(actual)
    if counts.get('scalar_uncached_ec_adds', 0) != integer.calls or counts.get('scalar_wrapper_add_calls', 0) != integer.api:
        raise ValueError('known-base physical constructor prediction')
    if counts.get('public_base_certificates_verified', 0) != size or counts.get('base_label_hashes', 0) != len(trace):
        raise ValueError('known-base certificate or draw counts')
    return dict(checked=True, base_size=size, draw_records=len(trace), constructor_points=len(knowledge), supplied_equations=size)


def phase_counts(actual):
    totals = Counter()
    for phase in actual['phases']:
        if phase['status'] != 'complete' or phase['wall_valid'] is not False:
            raise ValueError('phase validity')
        if any(type(v) is not int or v < 0 for v in phase['counters'].values()):
            raise ValueError('counter encoding')
        totals.update(phase['counters'])
    if dict(totals) != actual['counters']:
        raise ValueError('phase conservation')
    return totals


def known_case(case, labels, actual, fixture=None):
    w, nt, r = case['width'], case['target_count'], case['modulus']
    if len(labels) != w or len(case['source']) != w:
        raise ValueError('known-case supplied information')
    for j, (vector, rhs) in enumerate(case['source']):
        if vector != [int(k == j) for k in range(w)] or rhs != labels[j]:
            raise ValueError('known-case unit equation')
    B = [v['vector'] for v in case['target']]
    U = [v['outside'] for v in case['target']]
    rhs = [v['rhs'] for v in case['target']]
    reduced = [(b - sum(a * s for a, s in zip(v, labels, strict=True))) % r for v, b in zip(B, rhs, strict=True)]
    if actual['arm'] != 'known_direct' or actual['reduced_rhs'] != reduced or actual['system']['columns'] != nt:
        raise ValueError('known-case substitution')
    check_source.system(actual['system'], U, reduced, r)
    M = [v for v, b in case['source']]
    full = [v + [0] * nt for v in M] + [v + u for v, u in zip(B, U, strict=True)]
    values = list(labels) + rhs
    rr = check_source.rank(full, r)
    if rr != w + check_source.rank(U, r) or len(actual['recoveries']) != nt:
        raise ValueError('known-case full system rank')
    for t, rec in enumerate(actual['recoveries']):
        unit = [int(k == t) for k in range(nt)]
        if rec['target_index'] != t:
            raise ValueError('target order')
        check_solver.member(rec, unit, U, reduced, actual['system'], r)
        if rec['scalar'] != rec['value']:
            raise ValueError('known-case scalar offset')
        if rec['identifiable']:
            weights = rec['original_row_weights']
            query = [0] * w + unit
            if len(weights) != len(full) or check_solver.combine(weights, full, values, w + nt, r) != (query, rec['scalar']):
                raise ValueError('known-case original row certificate')
            if fixture and check_source.old.multiply(fixture['p'], 0, fixture['a'], rec['scalar'], tuple(fixture['P'])) != tuple(case['targets'][t]['point']):
                raise ValueError('known-case public target certificate')
        elif rec['original_row_weights'] is not None:
            raise ValueError('fabricated unresolved original weights')
    phase_counts(actual)
    names = ['known_label_substitution', 'elimination', 'identification', 'certificate_lifting', 'original_row_certificate_verification']
    if fixture:
        names.append('public_target_verification')
    if [v['phase'] for v in actual['phases']] != names:
        raise ValueError('known-case phase sequence')
    return dict(checked=True, supplied_rank=w, outside_rank=rr-w,
                identified=sum(v['identifiable'] for v in actual['recoveries']))


def collection(built, target_generation, actual):
    f = built['cell']['fixture']
    n, p, r = len(f['factor_base']), f['p'], f['r']
    base = [tuple(v['point']) for v in f['factor_base']]
    if actual['target_generation'] != target_generation:
        raise ValueError('known arm target substitution')
    if actual['projection'] != dict(U=n, unknown_points=[list(v) for v in base],
            native_to_projected=[['unknown', j, 1] for j in range(n)], public_derivations=[]):
        raise ValueError('known native projection')
    known = actual['arms'].get('known')
    if set(actual['arms']) != {'known'} or actual['selection'] != dict(orders={'known': []}, ap={}, trace=[]):
        raise ValueError('known arm source-free selection')
    if known['rows'] or known['sources'] or known['knowledge'] != built['knowledge']:
        raise ValueError('known arm borrowed source knowledge')
    anchors = []
    for j, label in enumerate(built['signed_labels']):
        vector = [int(k == j) for k in range(n)]
        anchors.append(dict(coefficients=vector, source_scalar=label, prefix=0, atom=j, kind='supplied_public_base_label'))
    if known['anchors'] != anchors:
        raise ValueError('known supplied equations')
    add = lambda a, b: check_source.old.add(p, 0, f['a'], a, b)
    signed = {(j, s): q if s == 1 else (q[0], -q[1] % p) for j, q in enumerate(base) for s in (1, -1)}
    pairs, table = [], defaultdict(list)
    for (j, k), signs in product(combinations(range(n), 2), product((1, -1), repeat=2)):
        q = add(signed[j, signs[0]], signed[k, signs[1]])
        table[q].append(len(pairs))
        pairs.append(dict(indices=[j, k], signs=list(signs), point=None if q is None else list(q)))
    if pairs != actual['pairs']:
        raise ValueError('known pair table completeness')
    triples = defaultdict(list)
    for indices, signs in product(combinations(range(n), 3), product((1, -1), repeat=3)):
        q = None
        for j, s in zip(indices, signs, strict=True):
            q = add(q, signed[j, s])
        triples[q].append((indices, signs))
    trace = []
    rows = actual['target_collection']['rows']
    for target in target_generation['targets']:
        index, Q = target['index'], tuple(target['point'])
        chosen = [row for row in rows if row['target_index'] == index]
        if sorted((tuple(v['triple']), tuple(v['signs'])) for v in chosen) != sorted(triples[Q]):
            raise ValueError('known natural full triple oracle')
        for row in chosen:
            vector = [0] * n
            for j, s in zip(row['triple'], row['signs'], strict=True):
                vector[j] = (vector[j] + s) % r
            if row['coefficients'] != vector or row['curve_uid'] != f['uid'] or row['source_scalar'] != 0 or row['target_point'] != target['point']:
                raise ValueError('known natural row encoding')
        for third, sign in product(range(n), (1, -1)):
            q = signed[third, sign]
            wanted = add(Q, (q[0], -q[1] % p))
            bucket = table.get(wanted, [])
            trace.append(dict(index=index, third=third, sign=sign, wanted=None if wanted is None else list(wanted),
                              bucket=bucket, accepted=[i for i in bucket if pairs[i]['indices'][1] < third]))
    if trace != actual['target_collection']['trace']:
        raise ValueError('known natural query or miss trace')
    totals = Counter()
    for phase in actual['collection_phases']:
        if phase['status'] != 'complete':
            raise ValueError('known partial collection phase')
        totals.update(phase['counters'])
    if dict(totals) != actual['collection_counters'] or totals.get('source_queries', 0):
        raise ValueError('known source-free physical conservation')
    return dict(checked=True, signed_triple_oracle=sum(map(len, triples.values())), source_queries=0,
                supplied_base_equations=n), dict(triples)


def joint_case(case, actual, fixture=None):
    w, nt, r = case['width'], case['target_count'], case['modulus']
    rows = [v + [0] * nt for v, b in case['source']] + [v['vector'] + v['outside'] for v in case['target']]
    values = [b for v, b in case['source']] + [v['rhs'] for v in case['target']]
    M = [v for v, b in case['source']]
    U = [v['outside'] for v in case['target']]
    rr, mr, ur = check_source.rank(rows, r), check_source.rank(M, r), check_source.rank(U, r)
    if actual['arm'] != 'sparse_joint' or actual['system']['columns'] != w + nt:
        raise ValueError('joint arm or width')
    check_source.system(actual['system'], rows, values, r)
    if len(actual['recoveries']) != nt:
        raise ValueError('joint target coverage')
    for t, rec in enumerate(actual['recoveries']):
        unit = [0] * (w + nt)
        unit[w + t] = 1
        if rec['target_index'] != t:
            raise ValueError('joint target order')
        check_solver.member(rec, unit, rows, values, actual['system'], r)
        if rec['scalar'] != rec['value']:
            raise ValueError('joint scalar offset')
        if rec['identifiable']:
            weights = rec['original_row_weights']
            if len(weights) != len(rows) or check_solver.combine(weights, rows, values, w + nt, r) != (unit, rec['scalar']):
                raise ValueError('joint original row certificate')
            if fixture and check_source.old.multiply(fixture['p'], 0, fixture['a'], rec['scalar'], tuple(fixture['P'])) != tuple(case['targets'][t]['point']):
                raise ValueError('joint public target certificate')
        elif rec['original_row_weights'] is not None:
            raise ValueError('joint fabricated unresolved certificate')
    phase_counts(actual)
    names = ['joint_matrix_construction', 'elimination', 'identification', 'certificate_lifting', 'original_row_certificate_verification']
    if fixture:
        names.append('public_target_verification')
    if [v['phase'] for v in actual['phases']] != names:
        raise ValueError('joint phase sequence')
    return dict(checked=True, joint_rank=rr, source_rank=mr, outside_rank=ur,
                delta=rr-ur-mr, base_rank_after_cancellation=rr-ur,
                identified=sum(v['identifiable'] for v in actual['recoveries']))
