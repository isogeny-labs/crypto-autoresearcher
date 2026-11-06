"""Dense rank identity, old-kernel action and native cancellation certificates."""
from shared import check_source, check_solver
import known_checks


def project(case, prepared):
    r = case['modulus']
    def row(v, b):
        return [v[j]*sign % r for j, sign in prepared['basis']], (b-sum(v[j]*s for j, s in prepared['known'])) % r
    return ([row(v, b) for v, b in case['source'][len(prepared['known']):]],
            [(*row(v['vector'], v['rhs']), v['outside']) for v in case['target']])


def kernel(rows, width, r):
    """Independent dense RREF kernel, diagnostic work outside production solver."""
    values, pivots, i = [list(v) for v in rows], [], 0
    for j in range(width):
        k = next((k for k in range(i, len(values)) if values[k][j] % r), None)
        if k is None:
            continue
        values[i], values[k] = values[k], values[i]
        inverse = pow(values[i][j] % r, -1, r)
        values[i] = [v*inverse % r for v in values[i]]
        for k in range(len(values)):
            if k != i:
                scale = values[k][j]
                values[k] = [(a-scale*b) % r for a, b in zip(values[k], values[i], strict=True)]
        pivots.append(j)
        i += 1
    result = []
    for free in sorted(set(range(width))-set(pivots)):
        vector = [0]*width
        vector[free] = 1
        for j, row in zip(pivots, values, strict=False):
            vector[j] = -row[free] % r
        result.append(vector)
    return result


def check(norm, norm_prepared, hybrid, hybrid_prepared, actual):
    r, width, nt = norm['modulus'], len(norm_prepared['basis']), norm['target_count']
    old, _ = project(norm, norm_prepared)
    new, targets = project(hybrid, hybrid_prepared)
    M, bM = [v for v, b in old], [b for v, b in old]
    check_source.system(actual['reference'], M, bM, r)
    origins = hybrid['source_origins'][len(hybrid_prepared['known']):]
    expected_groups = dict(supplied=[], collected=[])
    for index, ((v, b), origin) in enumerate(zip(new, origins, strict=True)):
        if origin['kind'] == 'supplied_owned_cache_match': name = 'supplied'
        elif origin['kind'] in ('collected_source', 'constructed_source_anchor'): name = 'collected'
        else: raise ValueError('independent information provenance')
        expected_groups[name].append(dict(vector=v, rhs=b, reduced_source_index=index))
    rows, rhs, ranks = list(M), list(bM), dict(reference=check_source.rank(M, r))
    N = kernel(M, width, r)
    if len(N)+ranks['reference'] != width or check_source.rank(N, r) != len(N):
        raise ValueError('old dense kernel dimension')
    syndromes = {}
    for name, expected in expected_groups.items():
        got = actual['groups'][name]
        if [{k: v for k, v in item.items() if k != 'old_rowspace'} for item in got] != expected:
            raise ValueError('supplied/collected attribution rows changed')
        for item in got:
            check_solver.member(item['old_rowspace'], item['vector'], M, bM, actual['reference'], r)
        rows += [v['vector'] for v in expected]
        rhs += [v['rhs'] for v in expected]
        ranks[name] = check_source.rank(rows, r)
        syndromes[name] = [[sum(a*b for a, b in zip(item['vector'], n, strict=True)) % r for n in N] for item in expected]
    U, B, bB = [u for v, b, u in targets], [v for v, b, u in targets], [b for v, b, u in targets]
    ur = check_source.system(actual['outside'], U, [0]*len(U), r)
    C, d, previous = [], [], -1
    for item in actual['cancellations']:
        weights = [0]*len(U)
        indices = []
        for j, value in item['original_target_weights']:
            if type(j) is not int or not 0 <= j < len(U) or type(value) is not int or not 0 < value < r:
                raise ValueError('information cancellation weight encoding')
            indices.append(j)
            weights[j] = value
        if indices != sorted(set(indices)) or not indices or indices[-1] <= previous or weights[indices[-1]] != 1:
            raise ValueError('information cancellation repeated weight')
        previous = indices[-1]
        if check_solver.combine(weights, U, [0]*len(U), nt, r)[0] != [0]*nt:
            raise ValueError('information outside coefficients did not cancel')
        if check_solver.combine(weights, B, bB, width, r) != (item['vector'], item['rhs']):
            raise ValueError('information cancellation vector/RHS')
        native_rows = [v for v, b in hybrid['source'][:len(hybrid_prepared['known'])]] + [v['vector']+v['outside'] for v in hybrid['target']]
        native_rows[:len(hybrid_prepared['known'])] = [v+[0]*nt for v in native_rows[:len(hybrid_prepared['known'])]]
        native_rhs = [b for v, b in hybrid['source'][:len(hybrid_prepared['known'])]] + [v['rhs'] for v in hybrid['target']]
        lifted = item['supplied_unit_weights']+weights
        query = [0]*(hybrid['width']+nt)
        for value, (j, sign) in zip(item['vector'], hybrid_prepared['basis'], strict=True):
            query[j] = sign*value % r
        if check_solver.combine(lifted, native_rows, native_rhs, len(query), r) != (query, item['rhs']):
            raise ValueError('information original native cancellation certificate')
        check_solver.member(item['old_rowspace'], item['vector'], M, bM, actual['reference'], r)
        C.append(item['vector'])
        d.append(item['rhs'])
    if len(C) != len(U)-ur:
        raise ValueError('incomplete outside cancellation basis')
    before = len(rows)
    rows += C
    rhs += d
    ranks['targets_after_cancellation'] = check_source.system(actual['final'], rows, rhs, r)
    block = [v+[0]*nt for v in rows[:before]]+[v+u for v, u in zip(B, U, strict=True)]
    delta = check_source.rank(block, r)-ur-ranks['reference']
    increments = dict(supplied=ranks['supplied']-ranks['reference'],
        collected_after_supplied=ranks['collected']-ranks['supplied'],
        targets_after_cancellation=ranks['targets_after_cancellation']-ranks['collected'])
    if actual['ranks'] != ranks or actual['increments'] != increments or actual['delta_vs_old'] != delta:
        raise ValueError('outside-corrected rank identity or attribution mismatch')
    if actual['attribution_order'] != ['reference', 'supplied', 'collected', 'targets_after_cancellation']:
        raise ValueError('information attribution order changed')
    syndromes['targets_after_cancellation'] = [[sum(a*b for a, b in zip(v, n, strict=True)) % r for n in N] for v in C]
    if check_source.rank(sum(syndromes.values(), []), r) != delta:
        raise ValueError('old-kernel action and corrected rank disagree')
    known_checks.phase_counts(actual)
    return dict(checked=True, old_kernel=N, old_kernel_syndromes=syndromes,
                outside_rank=ur, delta_vs_old=delta, ranks=ranks, increments=increments)
