"""Public-only full-horizon source constructors using owned paid caches."""
from shared import core
from baseline import construct
from guards import require_fields
from crypto_autoresearcher.index_calculus.targets import FixedBaseMultiplier


def prediction(r, known, values, kind, ap, window):
    curve = construct.ScalarModel(r, known)
    table, initialized = None, False

    def mul(s):
        nonlocal table, initialized
        if s in curve.known:
            return s
        if not initialized:
            if window:
                table = FixedBaseMultiplier(curve, 1, r, window=window)
            initialized = True
        if s in curve.known:
            return s
        return construct.binary(curve, s, 1) if table is None else table.mul(s)

    if kind == 'ap':
        A, D = mul(ap['a']), mul(ap['d'])
        produced = []
        for i in range(len(values)):
            if i:
                A = curve.add(A, D)
            produced.append(A)
    else:
        produced = [mul(s) for s in values]
    if produced != values:
        raise ValueError('source-only public scalar prediction')
    return dict(window=window, uncached_ec_adds=curve.calls, wrapper_add_calls=curve.api_calls,
                table_entries=0 if table is None else table.entries, known_labels=len(curve.known))


class Stream(dict):
    """Serializable source facts plus a transient meter for subsequent queries."""
    meter = None


def build(fixture, rules, initial, values, kind, ap, schedule, event, capability=None):
    require_fields(rules, fixture, capability)
    r, count = fixture['r'], rules['sources']
    if not 0 < count <= 128 or len(values) != count or len(set(values)) != count:
        raise ValueError('source horizon/uniqueness gate')
    if any(type(s) is not int or not 0 < s < r for s in values) or kind not in ('ap', 'hash'):
        raise ValueError('source scalar encoding')
    if kind == 'ap' and (not ap or [((ap['a']+i*ap['d']) % r) for i in range(count)] != values):
        raise ValueError('AP full-horizon recipe')
    meter = core.ProgressMeter(fixture, event, dict(kind='source_construction', source_schedule=schedule))
    knowledge, sources = [], []
    prefix = 0
    known, origins = {0: None}, {}
    for item in initial:
        scalar = item['scalar']
        point = None if item['point'] is None else tuple(item['point'])
        if type(scalar) is not int or not 0 <= scalar < r:
            raise ValueError('paid source initial label')
        if scalar in known and known[scalar] != point:
            raise ValueError('inconsistent paid source cache')
        known[scalar] = point
        origins[scalar] = item.get('origin')

    def on_point(point, scalar, basis, origin):
        if point is None:
            return
        value = dict(point=list(point), scalar=scalar, prefix=prefix, origin=origin)
        if scalar in origins:
            value['paid_origin'] = origins[scalar]
        knowledge.append(value)
        event(dict(kind='source_constructor_point', source_schedule=schedule, record=value))

    curve = meter.stage('source_cache_hydration', lambda: construct.ScalarCurve(
        meter, fixture['p'], r, tuple(fixture['P']), known, on_point, 'P'))

    def choose():
        rows = [prediction(r, list(curve.known), values, kind, ap, window) for window in range(9)]
        best = min(rows, key=lambda row: (row['uncached_ec_adds'], row['window']))
        meter.other['constructor_policy_candidates'] += len(rows)
        meter.other['constructor_policy_simulated_ec_adds'] += sum(row['uncached_ec_adds'] for row in rows)
        meter.other['constructor_policy_simulated_wrapper_adds'] += sum(row['wrapper_add_calls'] for row in rows)
        return dict(window=best['window'], candidates=rows, full_horizon=True,
            objective='Uncached group-add calls over all source scalars/AP advances; ascending window on ties. Public scalar/cache labels only.')

    selection = meter.stage('source_constructor_policy', choose)
    constructor = construct.Constructor(curve, selection)
    prefix = count

    def produce():
        A = D = None
        if kind == 'ap':
            A, D = constructor.mul(ap['a']), constructor.mul(ap['d'])
        for i, scalar in enumerate(values):
            if kind == 'ap':
                if i:
                    A = curve.add(A, D)
                point = A
            else:
                point = constructor.mul(scalar)
            if point is None:
                raise ValueError('nonzero source scalar produced identity')
            item = dict(scalar=scalar, point=list(point), prefix=count)
            sources.append(item)
            event(dict(kind='source_constructed', source_schedule=schedule, record=item))

    meter.stage('source_public_point_construction', produce)
    result = Stream(selection=selection, sources=sources, knowledge=knowledge,
        initial_scalars=sorted(known), schedule=schedule, source_kind=kind,
        phases=list(meter.phases), counters=meter.counters(), complete=True)
    result.meter = meter
    return result
