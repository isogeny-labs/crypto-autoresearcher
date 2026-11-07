"""Native geometry with explicitly labelled or unlabelled auxiliary slots."""
from shared import check_source


def build(fixture, norm_size, helper_labels, meter):
    native = fixture['factor_base']
    if type(norm_size) is not int or not native or not 0 <= norm_size <= len(native) <= 48:
        raise ValueError('native geometry size gate')
    if any(type(j) is not int for j in helper_labels) or not set(helper_labels) <= set(range(norm_size, len(native))):
        raise ValueError('supplied auxiliary labels must name auxiliary slots')
    if any(type(value) is not int or not 0 < value < fixture['r'] for value in helper_labels.values()):
        raise ValueError('helper scalar encoding')
    classes, representatives, points, aliases = {}, [], [], []
    for j, atom in enumerate(native):
        point = tuple(atom['point'])
        if len(point) != 2:
            raise ValueError('finite point encoding')
        opposite = meter.neg(point)
        if point == opposite:
            raise ValueError('order-two atom outside odd prime-order base')
        meter.other['geometry_orientation_comparisons'] += 1
        canonical = min(point, opposite)
        meter.other['geometry_class_lookups'] += 1
        if canonical not in classes:
            classes[canonical] = len(representatives)
            representatives.append(j)
            points.append(list(point))
            meter.other['geometry_classes_stored'] += 1
        index = classes[canonical]
        sign = 1 if point == tuple(points[index]) else -1
        aliases.append(dict(native_index=j, geometry_index=index,
                            representative_native=representatives[index], sign=sign))
        meter.other['geometry_alias_records'] += 1
    matches = []
    for j, scalar in helper_labels.items():
        alias = aliases[j]
        representative = alias['representative_native']
        meter.other['helper_native_match_lookups'] += 1
        if representative >= norm_size:
            continue
        value = scalar if alias['sign'] == 1 else meter.ring.sub(0, scalar)
        vector = [0]*len(native)
        vector[representative] = 1
        matches.append(dict(vector=vector, rhs=value, kind='supplied_helper_match',
            witness=dict(helper_native=j, norm_native=representative, sign=alias['sign'], helper_scalar=scalar)))
        meter.other['supplied_helper_match_equations'] += 1
        meter.other['supplied_helper_match_coefficients_emitted'] += len(native)
    return dict(native_width=len(native), norm_size=norm_size, native_indices=representatives,
                points=points, aliases=aliases, supplied_norm_matches=matches,
                maximum_pair_entries=2*len(points)*(len(points)-1))


def check(fixture, norm_size, helper_labels, geometry):
    """Plain independent sign-class reconstruction and supplied-label checks."""
    p, r = fixture['p'], fixture['r']
    points = [tuple(v['point']) for v in fixture['factor_base']]
    canonical = []
    representatives, values, aliases = [], [], []
    for j, point in enumerate(points):
        if (point[1]**2-point[0]**3-fixture['a']*point[0]-fixture['b']) % p:
            raise ValueError('geometry non-curve atom')
        opposite = point[0], -point[1] % p
        if point == opposite:
            raise ValueError('geometry order-two atom')
        key = min(point, opposite)
        if key not in canonical:
            canonical.append(key)
            representatives.append(j)
            values.append(list(point))
        index = canonical.index(key)
        aliases.append(dict(native_index=j, geometry_index=index, representative_native=representatives[index],
                            sign=1 if point == tuple(values[index]) else -1))
    matches = []
    for j, scalar in helper_labels.items():
        if check_source.old.multiply(p, 0, fixture['a'], scalar, tuple(fixture['P'])) != points[j]:
            raise ValueError('geometry helper public scalar label')
        rep, sign = aliases[j]['representative_native'], aliases[j]['sign']
        if rep < norm_size:
            vector = [int(k == rep) for k in range(len(points))]
            matches.append(dict(vector=vector, rhs=sign*scalar % r, kind='supplied_helper_match',
                witness=dict(helper_native=j, norm_native=rep, sign=sign, helper_scalar=scalar)))
    expected = dict(native_width=len(points), norm_size=norm_size, native_indices=representatives,
                    points=values, aliases=aliases, supplied_norm_matches=matches,
                    maximum_pair_entries=2*len(values)*(len(values)-1))
    if geometry != expected:
        raise ValueError('geometry aliases/native slots or supplied equations differ')
    return dict(checked=True, native_width=len(points), geometric_atoms=len(values),
                supplied_norm_matches=len(matches), maximum_pair_entries=expected['maximum_pair_entries'])
