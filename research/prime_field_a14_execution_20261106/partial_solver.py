"""Substitute supplied base units and lift target certificates to native rows.

Native base variables remain explicit in the input.  A signed, ordered basis
for the remaining variables preserves the original norm projection.  Supplied
helper labels disappear through paid substitution, not by inventing unknowns
or counting their unit equations as newly collected information.
"""
from shared import solver, known_solver


def validate(case, known, basis):
    solver.validate(case)
    w, r = case['width'], case['modulus']
    indices = []
    for pair in known:
        if len(pair) != 2:
            raise ValueError('known column encoding')
        j, value = pair
        if type(j) is not int or not 0 <= j < w or type(value) is not int or not 0 <= value < r:
            raise ValueError('known column encoding')
        indices.append(j)
    if len(indices) != len(set(indices)) or len(case['source']) < len(known):
        raise ValueError('duplicate or missing supplied columns')
    for i, (j, value) in enumerate(known):
        unit = [int(k == j) for k in range(w)]
        vector, rhs = case['source'][i]
        if vector != unit or rhs != value:
            raise ValueError('supplied unit equation mismatch')
    unknown = []
    for pair in basis:
        if len(pair) != 2:
            raise ValueError('unknown signed basis encoding')
        j, sign = pair
        if type(j) is not int or not 0 <= j < w or type(sign) is not int or sign not in (1, -1):
            raise ValueError('unknown signed basis encoding')
        unknown.append(j)
    if len(unknown) != len(set(unknown)) or set(unknown) != set(range(w))-set(indices):
        raise ValueError('unknown basis must cover exactly remaining native columns')


def reduce_case(case, known, basis, meter):
    f = meter.ring

    def row(vector, rhs):
        meter.other['known_base_coefficients_scanned'] += len(known)
        for j, value in known:
            coefficient = vector[j]
            if coefficient:
                rhs = f.sub(rhs, known_solver.product(coefficient, value, meter))
                meter.other['known_base_substitution_support'] += 1
        reduced = []
        for j, sign in basis:
            value = vector[j]
            meter.other['unknown_basis_coefficients_copied'] += 1
            reduced.append(value if sign == 1 or not value else f.sub(0, value))
        return reduced, rhs

    source = [row(v, b) for v, b in case['source'][len(known):]]
    target = []
    for item in case['target']:
        vector, rhs = row(item['vector'], item['rhs'])
        target.append(dict(vector=vector, outside=list(item['outside']), rhs=rhs))
        meter.other['outside_coefficients_copied'] += case['target_count']
    return dict(width=len(basis), target_count=case['target_count'], modulus=case['modulus'],
                source=source, target=target, targets=case['targets'])


def solve(case, known, basis, meter):
    validate(case, known, basis)
    start = len(meter.phases)
    reduced = meter.stage('partial_known_substitution', lambda: reduce_case(case, known, basis, meter))
    rows, values = solver.joint_rows(reduced)
    system = solver.KernelFreeSystem(reduced['width']+case['target_count'], meter)

    def eliminate():
        for vector, rhs in zip(rows, values, strict=True):
            system.add(vector, rhs)

    meter.stage('joint_elimination', eliminate)

    def identify():
        records = []
        for t in range(case['target_count']):
            unit = [0]*system.width
            unit[reduced['width']+t] = 1
            value = system.identify(unit)
            records.append(dict(target_index=t, **value, scalar=value['value']))
        return records

    records = meter.stage('identification', identify)

    def lift():
        native_rows = [v for v, b in case['source'][len(known):]] + [v['vector'] for v in case['target']]
        for rec in records:
            if not rec['identifiable']:
                rec['original_row_weights'] = None
                continue
            coefficients = [0]*len(known)
            for weight, vector in zip(rec['row_weights'], native_rows, strict=True):
                meter.other['known_lift_row_weights_scanned'] += 1
                if not weight:
                    continue
                for k, (j, value) in enumerate(known):
                    meter.other['known_lift_base_coefficients_scanned'] += 1
                    if vector[j]:
                        coefficients[k] = meter.ring.sub(coefficients[k], known_solver.product(weight, vector[j], meter))
                        meter.other['known_lift_support_visits'] += 1
            rec['original_row_weights'] = coefficients+rec['row_weights']
            meter.other['original_row_weight_coefficients_emitted'] += len(rec['original_row_weights'])

    meter.stage('known_unit_certificate_lifting', lift)
    meter.stage('original_row_certificate_verification', lambda: solver.verify_original(case, records, meter))
    phases = meter.phases[start:]
    return dict(arm='partial_joint', known_columns=[list(v) for v in known],
                unknown_basis=[list(v) for v in basis], system=system.summary(),
                recoveries=records, phases=phases, counters=solver.counters(phases))
