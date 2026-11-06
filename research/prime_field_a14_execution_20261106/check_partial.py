"""Dense native/reduced membership and original certificate controls."""
from collections import Counter
from shared import check_source, check_solver


def check(case, known, basis, result, fixture=None):
    w, nt, r = case['width'], case['target_count'], case['modulus']
    if result['known_columns'] != [list(v) for v in known] or result['unknown_basis'] != [list(v) for v in basis]:
        raise ValueError('partial basis/knowledge witness')
    for i, (j, scalar) in enumerate(known):
        if case['source'][i][0] != [int(k == j) for k in range(w)] or case['source'][i][1] != scalar:
            raise ValueError('independent supplied-unit mismatch')
    remaining = set(range(w))-{j for j, value in known}
    if len(remaining) != len(basis) or {j for j, s in basis} != remaining or any(s not in (1, -1) for j, s in basis):
        raise ValueError('independent unknown basis')

    def project(v, b):
        return [v[j]*s % r for j, s in basis], (b-sum(v[j]*value for j, value in known)) % r

    M = [v for v, b in case['source']]
    native = [v+[0]*nt for v in M] + [v['vector']+v['outside'] for v in case['target']]
    values = [b for v, b in case['source']]+[v['rhs'] for v in case['target']]
    reduced, rhs = [], []
    for v, b in case['source'][len(known):]:
        row, value = project(v, b)
        reduced.append(row+[0]*nt)
        rhs.append(value)
    for item in case['target']:
        row, value = project(item['vector'], item['rhs'])
        reduced.append(row+item['outside'])
        rhs.append(value)
    if result['system']['columns'] != len(basis)+nt or result['arm'] != 'partial_joint':
        raise ValueError('partial system width/arm')
    rr = check_source.system(result['system'], reduced, rhs, r)
    native_rank = check_source.rank(native, r)
    if native_rank != rr+len(known) or check_source.rank([v+[b] for v, b in zip(native, values, strict=True)], r) != native_rank:
        raise ValueError('partial/native affine span mismatch')
    if len(result['recoveries']) != nt:
        raise ValueError('partial target coverage')
    for t, rec in enumerate(result['recoveries']):
        unit = [0]*(len(basis)+nt)
        unit[len(basis)+t] = 1
        check_solver.member(rec, unit, reduced, rhs, result['system'], r)
        original_unit = [0]*(w+nt)
        original_unit[w+t] = 1
        yes = check_source.rank(native+[original_unit], r) == native_rank
        if rec['target_index'] != t or rec['identifiable'] is not yes or rec['scalar'] != rec['value']:
            raise ValueError('partial native target membership/scalar')
        if yes:
            weights = rec['original_row_weights']
            if len(weights) != len(native) or check_solver.combine(weights, native, values, w+nt, r) != (original_unit, rec['scalar']):
                raise ValueError('partial original-unit row certificate')
            if fixture and check_source.old.multiply(fixture['p'], 0, fixture['a'], rec['scalar'], tuple(fixture['P'])) != tuple(case['targets'][t]['point']):
                raise ValueError('partial public group equation')
        elif rec['original_row_weights'] is not None:
            raise ValueError('partial fabricated unresolved weights')
    totals = Counter()
    for phase in result['phases']:
        if phase['status'] != 'complete' or phase['wall_valid'] is not False or any(type(v) is not int or v < 0 for v in phase['counters'].values()):
            raise ValueError('partial phase validity')
        totals.update(phase['counters'])
    if dict(totals) != result['counters']:
        raise ValueError('partial phase conservation')
    names = ['partial_known_substitution', 'joint_elimination', 'identification',
             'known_unit_certificate_lifting', 'original_row_certificate_verification']
    if fixture:
        names.append('public_target_verification')
    if [v['phase'] for v in result['phases']] != names:
        raise ValueError('partial phase order')
    outside_rank, source_rank = check_source.rank([v['outside'] for v in case['target']], r), check_source.rank(M, r)
    projected_source_rank = check_source.rank([project(v, b)[0] for v, b in case['source'][len(known):]], r)
    if projected_source_rank+len(known) != source_rank:
        raise ValueError('partial/native source span mismatch')
    return dict(checked=True, native_joint_rank=native_rank, supplied_columns=len(known),
                reduced_joint_rank=rr, native_source_rank=source_rank,
                source_rank=projected_source_rank, original_unknown_columns=len(basis), outside_rank=outside_rank,
                base_rank_after_cancellation=native_rank-outside_rank-len(known),
                delta=native_rank-outside_rank-source_rank,
                identified=sum(v['identifiable'] for v in result['recoveries']))
