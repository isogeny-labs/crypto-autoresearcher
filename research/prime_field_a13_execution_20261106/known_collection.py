"""Source-free known-base collector with its own paid geometry index/cache."""
from collections import defaultdict
from itertools import combinations, product

from baseline import core, batch_query, require


def collect(built, target_generation, rules, event, capability=None):
    require(rules, capability, built['cell']['fixture'])
    cell = built['cell']
    f = cell['fixture']
    base = [tuple(v['point']) for v in f['factor_base']]
    n = len(base)
    meter = core.ProgressMeter(f, event, dict(kind='known_base_collection'))
    signed = meter.stage('known_base_signed_query_index',
                         lambda: {(j, s): q if s == 1 else meter.neg(q)
                                  for j, q in enumerate(base) for s in (1, -1)})
    engines = meter.stage('query_engine_index_setup',
                          lambda: batch_query.QueryEngines(f, base, signed, meter, event))
    pairs, table = [], defaultdict(list)

    def pair_table():
        for (j, k), signs in product(combinations(range(n), 2), product((1, -1), repeat=2)):
            point = meter.e.add(signed[j, signs[0]], signed[k, signs[1]])
            table[point].append(len(pairs))
            pairs.append(dict(indices=[j, k], signs=list(signs), point=None if point is None else list(point)))
            meter.other['pair_table_insertions'] += 1
            if len(pairs) > rules['max_pair_entries']:
                raise ValueError('known pair table size gate')

    meter.stage('pair_construction', pair_table)

    def natural_queries():
        rows, trace = [], []
        for target in target_generation['targets']:
            index, Q = target['index'], tuple(target['point'])
            wanted_points = engines.evaluate(Q, meter, dict(target=True, arm='known', index=index))
            for third, sign in product(range(n), (1, -1)):
                wanted = wanted_points[2 * third + (sign == -1)]
                bucket = table.get(wanted, [])
                accepted = []
                meter.other['target_queries'] += 1
                meter.other['table_lookups'] += 1
                for pi in bucket:
                    meter.other['bucket_entries_inspected'] += 1
                    pair = pairs[pi]
                    if pair['indices'][1] >= third:
                        continue
                    row = core.old.direct.make_row(f, 0, pair['indices'] + [third], pair['signs'] + [sign])
                    row.update(target_index=index, target_point=list(Q))
                    total = None
                    for j, s in zip(row['triple'], row['signs'], strict=True):
                        total = meter.e.add(total, signed[j, s])
                    if not meter.equal(total, Q):
                        raise ValueError('known natural row group certificate')
                    meter.other['target_certificates'] += 1
                    rows.append(row)
                    accepted.append(pi)
                    event(dict(kind='known_natural_relation', row=row))
                record = dict(index=index, third=third, sign=sign,
                              wanted=None if wanted is None else list(wanted), bucket=bucket, accepted=accepted)
                trace.append(record)
                event(dict(kind='known_natural_query', record=record))
                if len(rows) > rules['max_retained_rows']:
                    raise ValueError('known natural row size gate')
        return dict(rows=rows, trace=trace)

    natural = meter.stage('target_queries', natural_queries)

    def information():
        anchors = []
        for j, label in enumerate(built['signed_labels']):
            vector = [0] * n
            vector[j] = 1
            anchors.append(dict(coefficients=vector, source_scalar=label, prefix=0,
                                atom=j, kind='supplied_public_base_label'))
            meter.other['supplied_base_unit_rows_constructed'] += 1
            meter.other['supplied_base_unit_coefficients_emitted'] += n
        projection = dict(U=n, unknown_points=[list(v) for v in base],
                          native_to_projected=[['unknown', j, 1] for j in range(n)], public_derivations=[])
        return anchors, projection

    anchors, projection = meter.stage('supplied_public_base_information', information)
    collected = batch_query.Collected(complete=True, projection=projection,
        selection=dict(orders={'known': []}, ap={}, trace=[]),
        target_generation=target_generation, target_collection=natural, pairs=pairs,
        arms=dict(known=dict(rows=[], anchors=anchors, knowledge=built['knowledge'],
                             sources=[], phase_ids=[], budgets=[])),
        collection_phases=meter.phases, collection_counters=meter.counters(),
        query_engine_setup=engines.descriptor, query_engine_records=list(engines.records))
    collected.query_engines = engines
    return collected


def case_input(cell, collected, branch, cache, budget, meter):
    """Assemble native columns directly, avoiding identity-projection arithmetic."""
    f = cell['fixture']
    n = len(f['factor_base'])
    nt = len(collected['target_generation']['targets'])
    source = [(list(row['coefficients']), row['source_scalar'])
              for row in collected['arms']['known']['anchors']]
    meter.other['supplied_base_unit_rows_copied'] += len(source)
    meter.other['matrix_coefficients_copied'] += n * len(source)
    target = []
    for request in branch['requests']:
        if request['step'] > budget:
            continue
        for generic in cache.records[request['query_id']]['rows']:
            outside = [0] * nt
            outside[request['target_index']] = meter.ring.sub(0, request['beta'])
            target.append(dict(vector=list(generic['coefficients']), outside=outside,
                               rhs=request['alpha'], kind='decomposition', request=request))
            meter.other['matrix_coefficients_copied'] += n
    for row in branch['equations']:
        if row['budget'] > budget:
            continue
        target.append(dict(vector=list(row['coefficients']), outside=list(row['outside']),
                           rhs=row['rhs'], kind=row['kind'], witness=row['witness']))
        meter.other['matrix_coefficients_copied'] += n + nt
    meter.other['native_target_rows_assembled'] += len(target)
    return dict(width=n, target_count=nt, modulus=f['r'], source=source, target=target,
                targets=collected['target_generation']['targets'])
