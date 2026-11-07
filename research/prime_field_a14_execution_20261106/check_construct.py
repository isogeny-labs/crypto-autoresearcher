"""Separate integer-program and plain group checks of paid source construction."""
from collections import Counter
from shared import check_source
from baseline import checker


def simulate(r, initial, values, kind, ap, window):
    model = checker.IntegerConstructor(r, initial, window)
    if kind == 'ap':
        A, D = model.mul(ap['a']), model.mul(ap['d'])
        result = []
        for i in range(len(values)):
            if i:
                A = model.add(A, D)
            result.append(A)
    else:
        result = [model.mul(value) for value in values]
    if result != values:
        raise ValueError('independent complete source recipe')
    return model


def check(fixture, rules, initial, values, kind, ap, actual):
    r = fixture['r']
    known = {0: None}
    origins = {}
    for item in initial:
        scalar, point = item['scalar'], item['point']
        point = None if point is None else tuple(point)
        if scalar in known and known[scalar] != point:
            raise ValueError('independent initial source collision')
        if check_source.old.multiply(fixture['p'], 0, fixture['a'], scalar, tuple(fixture['P'])) != point:
            raise ValueError('false paid initial public scalar')
        known[scalar] = point
        origins[scalar] = item.get('origin')
    if actual['initial_scalars'] != sorted(known) or actual['source_kind'] != kind:
        raise ValueError('source borrowed or missing paid cache')
    models = [simulate(r, known, values, kind, ap, window) for window in range(9)]
    candidates = [value.summary() for value in models]
    chosen = min(candidates, key=lambda v: (v['uncached_ec_adds'], v['window']))
    if actual['selection']['candidates'] != candidates or actual['selection']['window'] != chosen['window']:
        raise ValueError('source complete-horizon constructor policy')
    produced = actual['sources']
    if [v['scalar'] for v in produced] != values or any(v['prefix'] != rules['sources'] for v in produced):
        raise ValueError('source scalar/budget completeness')
    selected = models[chosen['window']]
    expected = selected.known-{0}
    labels = actual['knowledge']
    if len(labels) != len({v['scalar'] for v in labels}) or {v['scalar'] for v in labels} != expected:
        raise ValueError('source missing/future knowledge')
    for item in produced+labels:
        if tuple(item['point']) != check_source.old.multiply(fixture['p'], 0, fixture['a'], item['scalar'], tuple(fixture['P'])):
            raise ValueError('source point public equation')
    for item in labels:
        if item['prefix'] != (0 if item['scalar'] in known else rules['sources']):
            raise ValueError('source future label availability')
        if item['scalar'] in known:
            if item['origin'] != 'initial_paid_cache' or item.get('paid_origin') != origins[item['scalar']]:
                raise ValueError('source initial paid provenance')
        elif item['origin'] != 'scalar_constructor_intermediate':
            raise ValueError('source constructed point provenance')
    counts = Counter()
    for phase in actual['phases']:
        if phase['status'] != 'complete' or phase['wall_valid'] is not False or any(type(v) is not int or v < 0 for v in phase['counters'].values()):
            raise ValueError('source incomplete phase')
        counts.update(phase['counters'])
    if [v['phase'] for v in actual['phases']] != ['source_cache_hydration', 'source_constructor_policy', 'source_public_point_construction']:
        raise ValueError('source constructor phase order')
    if dict(counts) != actual['counters'] or counts.get('scalar_uncached_ec_adds', 0) != selected.calls or counts.get('scalar_wrapper_add_calls', 0) != selected.api:
        raise ValueError('source physical constructor prediction/conservation')
    return dict(checked=True, sources=len(produced), labelled_points=len(labels),
                uncached_group_adds=selected.calls, wrapper_adds=selected.api)
