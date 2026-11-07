"""Assemble original native rows, preserving supplied/collected provenance."""
from shared import solver


def build(prepared, collected, branch, cache, budget, scope, meter):
    f = prepared['cell']['fixture']
    w, nt = len(f['factor_base']), len(collected['target_generation']['targets'])
    if not 0 < w <= 48 or not 0 < nt <= 8 or w+nt > 64:
        raise ValueError('native matrix width gate')
    context = branch['context']
    arm, prefix = context['source_schedule'], context['source_prefix']
    if scope not in ('relations', 'anchors', 'supplied'):
        raise ValueError('unknown native information scope')
    if not 0 < budget <= max(v['target_prefix'] for v in branch['budgets']):
        raise ValueError('native target budget gate')
    if scope == 'supplied' and arm != 'known' or arm == 'known' and scope != 'supplied':
        raise ValueError('source-free scope differs')
    records = collected['arms'][arm]
    source, origins, target = [], [], []

    def guard():
        if len(source)+len(target) > 4096:
            partial = dict(width=w, target_count=nt, modulus=f['r'], source=source,
                           source_origins=origins, target=target, targets=collected['target_generation']['targets'])
            if hasattr(meter, 'event'):
                meter.event(dict(kind='native_matrix_size_failure', partial_case=partial))
            error = ValueError('matrix size gate')
            error.partial_case = partial
            raise error
    for j, value in prepared['known']:
        vector = [0]*w
        vector[j] = 1
        source.append((vector, value))
        origins.append(dict(kind='supplied_native_unit', native_index=j))
        meter.other['supplied_native_unit_rows_copied'] += 1
        meter.other['matrix_coefficients_copied'] += w
        guard()
    for index, row in enumerate(prepared['supplied']):
        source.append((list(row['vector']), row['rhs']))
        origins.append(dict(kind='supplied_owned_cache_match', index=index))
        meter.other['supplied_old_coordinate_rows_copied'] += 1
        meter.other['matrix_coefficients_copied'] += w
        guard()
    order = set(collected['selection']['orders'].get(arm, [])[:prefix])
    for index, row in enumerate(records['rows']):
        if row['source_scalar'] in order:
            source.append((list(row['coefficients']), row['source_scalar']))
            origins.append(dict(kind='collected_source', index=index))
            meter.other['collected_source_rows_copied'] += 1
            meter.other['matrix_coefficients_copied'] += w
            guard()
    if scope == 'anchors':
        for index, row in enumerate(records['anchors']):
            if 0 < row['prefix'] <= prefix:
                source.append((list(row['coefficients']), row['source_scalar']))
                origins.append(dict(kind='constructed_source_anchor', index=index))
                meter.other['constructed_source_anchor_rows_copied'] += 1
                meter.other['matrix_coefficients_copied'] += w
                guard()
    for request in branch['requests']:
        if request['step'] > budget:
            continue
        for generic in cache.records[request['query_id']]['rows']:
            outside = [0]*nt
            outside[request['target_index']] = meter.ring.sub(0, request['beta'])
            target.append(dict(vector=list(generic['coefficients']), outside=outside,
                               rhs=request['alpha'], kind='decomposition', request=request))
            meter.other['matrix_coefficients_copied'] += w
            meter.other['native_target_rows_assembled'] += 1
            guard()
    if scope in ('anchors', 'supplied'):
        for row in branch['equations']:
            if row['budget'] <= budget:
                target.append(dict(vector=list(row['coefficients']), outside=list(row['outside']),
                                   rhs=row['rhs'], kind=row['kind'], witness=row['witness']))
                meter.other['matrix_coefficients_copied'] += w+nt
                meter.other['native_target_rows_assembled'] += 1
                guard()
    case = dict(width=w, target_count=nt, modulus=f['r'], source=source, target=target,
        targets=collected['target_generation']['targets'], source_origins=origins)
    solver.validate(case)
    return case


def expected(prepared, collected, branch, cache, budget, scope):
    """Independent plain native row reconstruction, without producer arithmetic."""
    f = prepared['cell']['fixture']
    w, nt = len(f['factor_base']), len(collected['target_generation']['targets'])
    context = branch['context']
    arm, prefix = context['source_schedule'], context['source_prefix']
    records = collected['arms'][arm]
    source = [([int(k == j) for k in range(w)], value) for j, value in prepared['known']]
    origins = [dict(kind='supplied_native_unit', native_index=j) for j, value in prepared['known']]
    for index, row in enumerate(prepared['supplied']):
        source.append((row['vector'], row['rhs']))
        origins.append(dict(kind='supplied_owned_cache_match', index=index))
    for index, row in enumerate(records['rows']):
        if row['source_scalar'] in collected['selection']['orders'].get(arm, [])[:prefix]:
            source.append((row['coefficients'], row['source_scalar']))
            origins.append(dict(kind='collected_source', index=index))
    if scope == 'anchors':
        for index, row in enumerate(records['anchors']):
            if 0 < row['prefix'] <= prefix:
                source.append((row['coefficients'], row['source_scalar']))
                origins.append(dict(kind='constructed_source_anchor', index=index))
    target = []
    for request in branch['requests']:
        if request['step'] <= budget:
            for generic in cache.records[request['query_id']]['rows']:
                outside = [(-request['beta'] % f['r']) if k == request['target_index'] else 0 for k in range(nt)]
                target.append(dict(vector=generic['coefficients'], outside=outside, rhs=request['alpha'],
                                   kind='decomposition', request=request))
    if scope in ('anchors', 'supplied'):
        target += [dict(vector=row['coefficients'], outside=row['outside'], rhs=row['rhs'],
                        kind=row['kind'], witness=row['witness'])
                   for row in branch['equations'] if row['budget'] <= budget]
    return dict(width=w, target_count=nt, modulus=f['r'], source=source, target=target,
                targets=collected['target_generation']['targets'], source_origins=origins)
