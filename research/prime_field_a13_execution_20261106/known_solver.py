"""Execute substitution of supplied base labels, then solve arbitrary U rows.

Original certificates include every supplied unit equation z_j = label_j.
Cross-target equations are solved together; symbolic multiples of Q never
become public scalar knowledge through their construction alone.
"""
from baseline import solver


def validate_labels(case, labels):
    solver.validate(case)
    r, w = case['modulus'], case['width']
    if len(labels) != w or any(type(v) is not int or not 0 <= v < r for v in labels):
        raise ValueError('public base labels encoding')
    if len(case['source']) != w:
        raise ValueError('known-label solver requires exact supplied unit equations')
    for j, (vector, rhs) in enumerate(case['source']):
        unit = [0] * w
        unit[j] = 1
        if vector != unit or rhs != labels[j]:
            raise ValueError('supplied unit equation does not match public labels')


def product(a, b, meter):
    """Count actual unit shortcuts, avoiding a gratuitous multiplication."""
    f = meter.ring
    if a == 1:
        meter.other['known_unit_product_shortcuts'] += 1
        return b
    if a == f.p - 1:
        meter.other['known_negative_unit_product_shortcuts'] += 1
        return f.sub(0, b)
    return f.mul(a, b)


def solve(case, labels, meter):
    validate_labels(case, labels)
    nt, w = case['target_count'], case['width']
    f = meter.ring
    start = len(meter.phases)

    def substitute():
        values = []
        for row in case['target']:
            value = row['rhs']
            meter.other['known_base_coefficients_scanned'] += w
            for coefficient, label in zip(row['vector'], labels, strict=True):
                if coefficient:
                    value = f.sub(value, product(coefficient, label, meter))
                    meter.other['known_base_substitution_support'] += 1
            values.append(value)
        return values

    values = meter.stage('known_label_substitution', substitute)
    system = solver.KernelFreeSystem(nt, meter)

    def eliminate():
        for row, value in zip(case['target'], values, strict=True):
            system.add(row['outside'], value)

    meter.stage('elimination', eliminate)

    def identify():
        records = []
        for t in range(nt):
            unit = [0] * nt
            unit[t] = 1
            found = system.identify(unit)
            records.append(dict(target_index=t, **found, scalar=found['value']))
        return records

    records = meter.stage('identification', identify)

    def lift():
        for rec in records:
            if not rec['identifiable']:
                rec['original_row_weights'] = None
                continue
            base_weights = [0] * w
            for a, row in zip(rec['row_weights'], case['target'], strict=True):
                meter.other['known_lift_row_weights_scanned'] += 1
                if not a:
                    continue
                for j, coefficient in enumerate(row['vector']):
                    meter.other['known_lift_base_coefficients_scanned'] += 1
                    if coefficient:
                        base_weights[j] = f.sub(base_weights[j], product(a, coefficient, meter))
                        meter.other['known_lift_support_visits'] += 1
            rec['original_row_weights'] = base_weights + rec['row_weights']
            meter.other['original_row_weight_coefficients_emitted'] += len(rec['original_row_weights'])

    meter.stage('certificate_lifting', lift)
    meter.stage('original_row_certificate_verification', lambda: solver.verify_original(case, records, meter))
    phases = meter.phases[start:]
    return dict(arm='known_direct', system=system.summary(), reduced_rhs=values,
                recoveries=records, phases=phases, counters=solver.counters(phases))
