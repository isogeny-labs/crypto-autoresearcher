"""Plain public-group reconstruction of owned caches, recipes and collection."""
from hashlib import sha256
import json

from shared import check_source, batch_check
import known_checks
import check_base, check_construct, geometry
from check_query import Oracle


def closed_signs(f, records):
    known = {}
    for item in records:
        scalar, point = item['scalar'], item['point']
        if scalar in known and known[scalar]['point'] != point:
            raise ValueError('independent owned label conflict')
        expected = check_source.old.multiply(f['p'], 0, f['a'], scalar, tuple(f['P']))
        if point != (None if expected is None else list(expected)):
            raise ValueError('independent owned P equation')
        known.setdefault(scalar, dict(scalar=scalar, point=point, origin=item['origin']))
    for scalar, item in list(known.items()):
        if scalar and -scalar % f['r'] not in known:
            q = item['point']
            known[-scalar % f['r']] = dict(scalar=-scalar % f['r'], point=[q[0], -q[1] % f['p']],
                origin=dict(kind='owned_paid_sign', parent=item['origin'], scalar=scalar))
    return [known[s] for s in sorted(known) if s]


def schedules(original, rules, actual):
    f = original['fixture']
    r, uid = f['r'], f['ec1']['curve_uid']
    orders, ap, trace = {}, {}, []
    def h(*values):
        return int(sha256('|'.join(map(str, values)).encode()).hexdigest(), 16)
    for seed in rules['seeds']:
        for counter in range(rules['maximum_scalar_candidates']):
            a = 1+h(rules['domain'], 'ap-start', uid, seed, counter) % (r-1)
            d = 1+h(rules['domain'], 'ap-step', uid, seed, counter) % (r-1)
            values = [(a+i*d) % r for i in range(rules['sources'])]
            chosen = 0 not in values
            trace.append(dict(kind='ap_candidate', seed=seed, counter=counter, a=a, d=d,
                selected=chosen, reason='selected' if chosen else 'zero_in_horizon'))
            if chosen:
                orders['ap'+str(seed)] = values
                ap['ap'+str(seed)] = dict(a=a, d=d)
                break
        else:
            raise ValueError('independent AP candidate gate')
        values, used = [], set()
        for index in range(rules['sources']):
            for counter in range(rules['maximum_scalar_candidates']):
                scalar = 1+h(rules['domain'], 'hash', uid, seed, index, counter) % (r-1)
                chosen = scalar not in used
                trace.append(dict(kind='hash_candidate', seed=seed, index=index, counter=counter,
                                  scalar=scalar, selected=chosen))
                if chosen:
                    values.append(scalar)
                    used.add(scalar)
                    break
            else:
                raise ValueError('independent hash candidate gate')
        orders['hash'+str(seed)] = values
    if actual != dict(orders=orders, ap=ap, trace=trace):
        raise ValueError('independent source schedule trace')
    return True


def preparation(original, rules, helper, actual):
    prior, f = original['fixture'], actual['cell']['fixture']
    n = len(prior['factor_base'])
    if helper is None:
        expected_cell = original
    else:
        check_base.check(original, rules, 16, helper)
        expected = {key: prior[key] for key in ('p', 'a', 'b', 'r', 'P')}
        expected['factor_base'] = prior['factor_base']+helper['cell']['fixture']['factor_base']
        uid = sha256(json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        expected_cell = dict(id=original['id'], fixture=dict(expected, uid=uid, ec1=prior['ec1']))
    if actual['cell'] != expected_cell or actual['norm_size'] != n:
        raise ValueError('native norm/helper identity')
    projection = check_source.old.public_projection(prior, list(range(1, rules['prerequisite']+1)))
    if actual['projection'] != projection:
        raise ValueError('original norm projection changed')
    known, basis = [], [None]*projection['U']
    for j, entry in enumerate(projection['native_to_projected']):
        if entry[0] == 'known': known.append([j, entry[1]])
        else:
            if basis[entry[1]] is not None: raise ValueError('duplicate original norm unknown')
            basis[entry[1]] = [j, entry[2]]
    labels = {} if helper is None else {n+j: value for j, value in enumerate(helper['signed_labels'])}
    known += [[j, value] for j, value in labels.items()]
    if actual['known'] != known or actual['basis'] != basis:
        raise ValueError('old unknown order or declared known units changed')
    prerequisites = [dict(scalar=s, point=list(check_source.old.multiply(f['p'], 0, f['a'], s, tuple(f['P']))))
                     for s in range(1, rules['prerequisite']+1)]
    if actual['prerequisites'] != prerequisites:
        raise ValueError('independent fixed prerequisite walk')
    initial = [dict(v, origin='own_fixed_prerequisite') for v in prerequisites]
    if helper is not None:
        initial += [dict(scalar=v['scalar'], point=v['point'], origin='own_paid_helper16') for v in helper['knowledge']]
    if actual['initial'] != closed_signs(f, initial):
        raise ValueError('borrowed/missing paid helper cache')
    available = {tuple(item['point']): item for item in actual['initial']}
    supplied = []
    for j, sign in basis:
        item = available.get(tuple(f['factor_base'][j]['point']))
        if item is not None:
            supplied.append(dict(vector=[int(k == j) for k in range(len(f['factor_base']))],
                rhs=item['scalar'], kind='supplied_owned_cache_match', witness=dict(native_index=j, paid_label=item)))
    if actual['supplied'] != supplied:
        raise ValueError('supplied cache matches changed or hidden as collected rank')
    geometry.check(f, n, labels, actual['geometry'])
    schedules(original, rules, actual['selection'])
    counts = known_checks.phase_counts(actual)
    if counts.get('prerequisite_group_adds', 0) != rules['prerequisite']-1:
        raise ValueError('fixed prerequisite work missing')
    return dict(checked=True, native_width=len(f['factor_base']), original_unknowns=len(basis),
                supplied_columns=len(known), owned_initial_labels=len(actual['initial']))


def known_preparation(original, rules, built, actual):
    n = built['public_base_size']
    check_base.check(original, rules, n, built)
    f = built['cell']['fixture']
    expected_initial = closed_signs(f, [dict(scalar=v['scalar'], point=v['point'], origin='own_paid_known'+str(n))
                                      for v in built['knowledge']])
    expected = dict(cell=built['cell'], norm_size=0, projection=None,
        known=[[j, value] for j, value in enumerate(built['signed_labels'])], basis=[],
        prerequisites=[], initial=expected_initial, supplied=[], selection=dict(orders={}, ap={}, trace=[]))
    if any(actual[key] != value for key, value in expected.items()):
        raise ValueError('source-free control borrowed cache or source work')
    geometry.check(f, 0, dict(enumerate(built['signed_labels'])), actual['geometry'])
    known_checks.phase_counts(actual)
    return dict(checked=True, native_width=n, original_unknowns=0, supplied_columns=n)


def collection(prepared, rules, actual):
    f = prepared['cell']['fixture']
    if actual['projection'] != prepared['projection'] or actual['selection'] != prepared['selection']:
        raise ValueError('collection changed frozen norm preparation')
    expected_schedules = set(prepared['selection']['orders']) or {'known'}
    if set(actual['arms']) != expected_schedules:
        raise ValueError('source schedule census')
    oracle = Oracle(f, prepared['geometry'])
    endpoints, results = [], []
    for schedule, values in prepared['selection']['orders'].items():
        arm = actual['arms'][schedule]
        ap = prepared['selection']['ap'].get(schedule)
        check_construct.check(f, rules, prepared['initial'], values, 'ap' if ap else 'hash', ap, arm['construction'])
        if arm['sources'] != arm['construction']['sources'] or len(arm['query_records']) != len(values):
            raise ValueError('source query count/order')
        rows = []
        for source, query in zip(arm['sources'], arm['query_records'], strict=True):
            if query['point'] != source['point']:
                raise ValueError('source query borrowed another endpoint')
            oracle.check(query, actual['pairs'])
            endpoints.append(source['point'])
            rows.extend(dict(row, source_scalar=source['scalar']) for row in query['rows'])
        if rows != arm['rows']:
            raise ValueError('native source row RHS/trace mismatch')
        construction = arm['construction']['knowledge']
        expected = closed_signs(f, [dict(v, origin=dict(kind='source_owned', source_schedule=schedule,
            prefix=v['prefix'], constructor_origin=v['origin'], paid_origin=v.get('paid_origin'))) for v in construction])
        prefix = {v['scalar']: v['prefix'] for v in construction}
        for item in expected:
            item['prefix'] = min(prefix.get(item['scalar'], rules['sources']), prefix.get(-item['scalar'] % f['r'], rules['sources']))
        if arm['knowledge'] != expected:
            raise ValueError('source borrowed/future signed knowledge')
        anchors = []
        for item in expected:
            for j, atom in enumerate(f['factor_base']):
                if atom['point'] == item['point']:
                    anchors.append(dict(coefficients=[int(k == j) for k in range(len(f['factor_base']))],
                        source_scalar=item['scalar'], prefix=item['prefix'], atom=j, kind='owned_public_scalar_anchor'))
        if anchors != arm['anchors']:
            raise ValueError('explicit owned anchor completeness')
        known_checks.phase_counts(arm)
        results.append(dict(schedule=schedule, source_queries=len(values), rows=len(rows), anchors=len(anchors)))
    if not prepared['selection']['orders']:
        expected = dict(rows=[], anchors=[], sources=[], knowledge=[dict(v, prefix=0) for v in prepared['initial']], phases=[], counters={})
        if actual['arms']['known'] != expected:
            raise ValueError('source-free control gained source knowledge')
    targets = actual['target_generation']['targets']
    if len(targets) != rules['targets'] or len(actual['natural_records']) != len(targets):
        raise ValueError('natural target census')
    for target, query in zip(targets, actual['natural_records'], strict=True):
        if target['point'] != query['point']:
            raise ValueError('natural target query identity')
        oracle.check(query, actual['pairs'])
        endpoints.append(target['point'])
    geometric = dict(f, factor_base=[f['factor_base'][j] for j in prepared['geometry']['native_indices']])
    batch_check.records(dict(fixture=geometric), actual['query_engine_records'], endpoints)
    known_checks.phase_counts(dict(phases=actual['collection_phases'], counters=actual['collection_counters']))
    return dict(checked=True, schedules=results, natural_targets=len(targets),
                physical_query_endpoints=len(endpoints), geometric_atoms=len(prepared['geometry']['points'])), oracle
