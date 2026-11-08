"""Deterministic checks; imports neither candidate nor manifest builder."""


class Mismatch(Exception):
    def __init__(self, reason, expected=None, actual=None):
        super().__init__(reason)
        self.reason, self.expected, self.actual = reason, expected, actual


def require(condition, reason, expected=None, actual=None):
    if not condition:
        raise Mismatch(reason, expected, actual)


def snapshot(value):
    kind = type(value)
    if value is None:
        return ['none']
    if kind is bool:
        return ['bool', value]
    if kind is int:
        return ['int', str(value)]
    if kind is float:
        return ['float', value.hex()]
    if kind is str:
        return ['str', value]
    if kind in (list, tuple):
        return ['list' if kind is list else 'tuple', [snapshot(v) for v in value]]
    if kind is dict:
        return ['dict', [[snapshot(k), snapshot(v)] for k, v in value.items()]]
    raise Mismatch('unsupported returned/snapshot type', 'built-in tree', kind.__name__)


def decode(tree):
    require(type(tree) is list and len(tree) >= 1, 'typed tree required')
    tag = tree[0]
    if tag == 'none':
        require(len(tree) == 1, 'null arity')
        return None
    require(len(tree) == 2, 'typed node arity')
    value = tree[1]
    if tag == 'bool':
        require(type(value) is bool, 'boolean payload')
        return value
    if tag == 'int':
        require(type(value) is str, 'integer string payload')
        result = int(value)
        require(str(result) == value, 'canonical integer string')
        return result
    if tag == 'float':
        require(type(value) is str, 'float hex payload')
        result = float.fromhex(value)
        require(result.hex() == value, 'canonical float hex')
        return result
    if tag == 'str':
        require(type(value) is str, 'string payload')
        return value
    require(type(value) is list, 'container payload')
    if tag in ('list', 'tuple'):
        values = [decode(item) for item in value]
        return values if tag == 'list' else tuple(values)
    require(tag == 'dict', 'unknown type tag')
    result = {}
    for pair in value:
        require(type(pair) is list and len(pair) == 2, 'dictionary pair')
        key, item = decode(pair[0]), decode(pair[1])
        require(key not in result, 'duplicate dictionary key')
        result[key] = item
    return result


def manifest_check(manifest):
    """Validate frozen manifest coverage/order, never regenerate case values."""
    require(manifest['schema'] == 'prime-scalar.typed-manifest/v1', 'manifest schema')
    cases, calls = manifest['cases'], manifest['calls']
    require(type(cases) is list and type(calls) is list, 'manifest containers')
    require(len(cases) == 649 and len(calls) == 23952, 'manifest length')
    case_ids = [case['id'] for case in cases]
    require(len(set(case_ids)) == 649, 'unique base case IDs')
    family_counts = {name: sum(c['family'] == name for c in cases)
                     for name in ('single', 'ordered-pair', 'empty-list', 'control')}
    require(family_counts == {'single': 419, 'ordered-pair': 207, 'empty-list': 14, 'control': 9},
            'family counts', actual=family_counts)
    require(sum(c['n'] + 1 for c in cases) == 1680, 'depth query count')
    require([c['id'] for c in calls] == ['call-%05d' % i for i in range(23952)], 'call IDs/order')
    position = 0
    for case in cases:
        require(type(case['p']) is int and type(case['n']) is int and type(case['assignment']) is int,
                'canonical case integers')
        require(2 <= case['p'] <= 4 and 0 <= case['n'] <= 3 and 0 <= case['assignment'] < 2 ** case['n'],
                'bounded case parameters')
        require(type(case['generators']) is list and len(case['generators']) <= 2, 'case generator count')
        for poly in case['generators']:
            require(type(poly) is list, 'polynomial pair list')
            masks = []
            for pair in poly:
                require(type(pair) is list and len(pair) == 2, 'polynomial pair')
                mask, coefficient = pair
                require(type(mask) is int and 0 <= mask < 2 ** case['n'], 'canonical original mask')
                require(type(coefficient) is int and 0 < coefficient < case['p'], 'canonical original coefficient')
                masks.append(mask)
            require(masks == sorted(set(masks)), 'canonical case pair order')
        for order in ('ascending', 'descending'):
            for container in ('list', 'tuple'):
                for repeat in (0, 1):
                    for api, depth in [('extract_reference', None), ('extract_sweep', None)] + [
                            ('restrict_reference', d) for d in range(case['n'] + 1)]:
                        row = calls[position]
                        position += 1
                        require(row['malformed'] is False and
                                (row['case_id'], row['family'], row['order'], row['container'], row['repeat'], row['api'], row['depth']) ==
                                (case['id'], case['family'], order, container, repeat, api, depth), 'valid call schedule')
                        args = decode(row['arguments'])
                        require(type(args) is list and len(args) == (5 if depth is not None else 4), 'argument arity')
                        require(all(type(v) is int for v in args[:3]) and args[:3] == [case['p'], case['n'], case['assignment']], 'case argument binding')
                        require(type(args[3]) is (list if container == 'list' else tuple), 'container realization')
                        require(len(args[3]) == len(case['generators']), 'generator realization count')
                        for actual, original in zip(args[3], case['generators']):
                            require(type(actual) is dict and list(actual.items()) ==
                                    [tuple(pair) for pair in sorted(original, reverse=order == 'descending')], 'insertion realization')
                        if depth is not None:
                            require(type(args[4]) is int and args[4] == depth, 'depth realization')
    require(position == 23824, 'valid call count')
    for kind, amount in (('global', 20), ('depth', 4)):
        for index in range(amount):
            for repeat in (0, 1):
                apis = ('extract_reference', 'extract_sweep', 'restrict_reference') if kind == 'global' else ('restrict_reference',)
                for api in apis:
                    row = calls[position]
                    position += 1
                    require(row['malformed'] is True and
                            (row['case_id'], row['family'], row['repeat'], row['api']) ==
                            ('malformed-%s-%02d' % (kind, index), 'malformed-' + kind, repeat, api), 'malformed schedule')
                    args = decode(row['arguments'])
                    require(type(args) is list and len(args) == (5 if api == 'restrict_reference' else 4), 'malformed argument arity')
                    require(snapshot(args) == row['arguments'], 'malformed typed round trip')
    expected_counts = {'base_cases': 649, 'base_depth_queries': 1680, 'valid_entry_calls': 23824,
                       'malformed_entry_calls': 128, 'total_entry_calls': 23952,
                       'oracle_full_evaluations': sum(len(c['generators']) * (2 ** (c['n'] + 1) - 1) for c in cases)}
    require(manifest['counts'] == expected_counts, 'manifest metadata counts', expected_counts, manifest['counts'])


def unpack(api, result, layouts):
    """Layout MUST be selected by a future reviewed public-interface binding."""
    if api == 'restrict_reference':
        layout = layouts['restriction']
        if layout == 'tuple_pair_v1':
            require(type(result) is tuple and len(result) == 2, 'restriction tuple layout')
            return result[0], result[1]
        if layout == 'mapping_v1':
            require(type(result) is dict and set(result) == {'residuals', 'counters'}, 'restriction mapping layout')
            return result['residuals'], result['counters']
        raise Mismatch('unbound restriction layout')
    require(layouts['extraction'] == 'mapping_v1', 'unbound extraction layout')
    require(type(result) is dict, 'extraction mapping required')
    keys = {'status', 'method', 'depth', 'prefix', 'generator_index', 'constant', 'counters'}
    require(set(result) == keys, 'extraction fields', sorted(keys), sorted(result))
    return result, result['counters']


def valid_output(row, case, expected, result, layouts, counter_names, evaluate):
    payload, counters = unpack(row['api'], result, layouts)
    require(type(counters) is dict and set(counters) == set(counter_names), 'counter schema')
    require(all(type(v) is int and v >= 0 for v in counters.values()), 'nonnegative integer counters')
    require(counters['inverse_calls'] == counters['multiplier_entries'] == 0, 'no certificate work')
    if row['api'] == 'restrict_reference':
        depth, n, p = row['depth'], case['n'], case['p']
        require(type(payload) is list and len(payload) == len(case['generators']), 'residual shape')
        normalized = []
        for index, residual in enumerate(payload):
            require(type(residual) is dict, 'residual dictionary')
            for mask, coefficient in residual.items():
                require(type(mask) is int and 0 <= mask < 2 ** n and mask % (2 ** depth) == 0, 'residual canonical mask')
                require(type(coefficient) is int and 0 < coefficient < p, 'residual canonical coefficient')
            require(residual == expected['residuals'][depth][index], 'residual coefficients',
                    snapshot(expected['residuals'][depth][index]), snapshot(residual))
            for suffix in range(2 ** (n - depth)):
                point = [0] * depth + [(suffix // (2 ** i)) % 2 for i in range(n - depth)]
                actual = evaluate(list(residual.items()), point, p, n)
                require(actual == expected['tables'][depth][index][suffix], 'residual evaluation',
                        expected['tables'][depth][index][suffix], actual)
            normalized.append(sorted(residual.items()))
        if case['id'] == 'control-insertion-sensitive-deletion' and depth == 2:
            wanted = 0 if row['order'] == 'ascending' else 1
            require(counters['dictionary_deletes'] == wanted, 'registered deletion control', wanted, counters['dictionary_deletes'])
        return normalized
    wanted_method = 'reference_binary' if row['api'] == 'extract_reference' else 'incidence_sweep'
    require(payload['method'] == wanted_method, 'method identity')
    witness = [payload[key] for key in ('depth', 'prefix', 'generator_index', 'constant')]
    if expected['witness'] is None:
        require(payload['status'] == 'no_scalar_witness' and all(v is None for v in witness), 'no-witness fields', None, witness)
    else:
        require(payload['status'] == 'found' and all(type(v) is int for v in witness), 'found witness types')
        require(witness == expected['witness'], 'least-depth/least-index witness', expected['witness'], witness)
    if row['api'] == 'extract_sweep':
        incidences = sum(mask.bit_count() for poly in case['generators'] for mask, _ in poly)
        require(counters['incidences_built'] == incidences, 'original incidence count', incidences, counters['incidences_built'])
        live = counters['live_incidence_visits']
        require(counters['dictionary_subtractions'] == live, 'subtraction identity')
        require(counters['dictionary_adds'] <= live, 'addition upper bound')
        require(counters['touched_set_adds'] == live, 'touched insertion identity')
        depth = case['n'] if expected['witness'] is None else expected['witness'][0]
        require(counters['variable_batches'] == depth, 'complete batch count', depth, counters['variable_batches'])
    return [payload['status'], witness]
