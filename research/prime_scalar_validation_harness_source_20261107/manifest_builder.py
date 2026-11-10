"""Metadata-only builder; execution requires separate metadata admission.

Never imports candidate or oracle. The future runner DOES NOT import this file.
Typed trees preserve bool/int/float, dict order, list/tuple, and malformed inputs.
"""
import hashlib
import itertools
import json
from pathlib import Path

SPEC_SHA256 = '7f68929cedcf12965554d96eefe7b1aeddef82f0f1bb182e6e37113e16d5e9dc'


def typed(value):
    kind = type(value)
    if value is None:
        return ['none']
    if kind is bool:
        return ['bool', value]
    if kind is int:
        return ['int', str(value)]
    if kind is float:
        return ['float', value.hex()]
    if kind in (list, tuple):
        return ['list' if kind is list else 'tuple', [typed(v) for v in value]]
    if kind is dict:
        return ['dict', [[typed(k), typed(v)] for k, v in value.items()]]
    raise ValueError('unsupported metadata type')


def polynomial(code, p, n):
    pairs = []
    for mask in range(2 ** n):
        digit = code % p
        code //= p
        if digit:
            pairs.append([mask, digit])
    return pairs


def build(spec):
    """Return exact expanded call manifest, with no semantic evaluations."""
    cases, calls = [], []
    for family in spec['families']:
        for p in family['p']:
            for n in family['n']:
                codes = range(p ** (2 ** n))
                for combination in itertools.product(codes, repeat=family['generator_count']):
                    generators = [polynomial(code, p, n) for code in combination]
                    for assignment in range(2 ** n):
                        cases.append({'id': 'case-%04d' % len(cases),
                                      'family': family['id'], 'p': p, 'n': n,
                                      'assignment': assignment, 'generators': generators})
    for control in spec['controls']:
        cases.append(dict(control, id='control-' + control['id'], family='control'))
    for case in cases:
        for order in ('ascending', 'descending'):
            for container in ('list', 'tuple'):
                for repeat in (0, 1):
                    generators = [dict(sorted(poly, reverse=order == 'descending'))
                                  for poly in case['generators']]
                    if container == 'tuple':
                        generators = tuple(generators)
                    common = [case['p'], case['n'], case['assignment'], generators]
                    apis = [('extract_reference', None), ('extract_sweep', None)]
                    apis += [('restrict_reference', d) for d in range(case['n'] + 1)]
                    for api, depth in apis:
                        arguments = common + ([] if depth is None else [depth])
                        calls.append({'id': 'call-%05d' % len(calls), 'case_id': case['id'],
                                      'family': case['family'], 'order': order,
                                      'container': container, 'repeat': repeat, 'api': api,
                                      'depth': depth, 'malformed': False,
                                      'arguments': typed(arguments)})
    mutations = [('global', i, v) for i, v in enumerate(spec['malformed_global_mutations'])]
    mutations += [('depth', i, v) for i, v in enumerate(spec['malformed_depth_mutations'])]
    for kind, index, mutation in mutations:
        for repeat in (0, 1):
            apis = ('extract_reference', 'extract_sweep', 'restrict_reference') if kind == 'global' else ('restrict_reference',)
            for api in apis:
                arguments = [2, 1, 0, [{1: 1}]]
                depth = 0
                if kind == 'depth':
                    depth = mutation
                else:
                    field = mutation['field']
                    value = mutation.get('value')
                    if field in ('p', 'n', 'assignment'):
                        arguments[('p', 'n', 'assignment').index(field)] = value
                    elif field == 'generators':
                        arguments[3] = {} if 'typed_value' in mutation else value
                    elif field == 'generator0':
                        arguments[3][0] = [[1, 1]]
                    elif field == 'mask':
                        arguments[3][0] = {value: 1}
                    elif field == 'coefficient':
                        arguments[3][0] = {1: value}
                    else:
                        raise ValueError('unrecognized frozen mutation')
                if api == 'restrict_reference':
                    arguments.append(depth)
                calls.append({'id': 'call-%05d' % len(calls),
                              'case_id': 'malformed-%s-%02d' % (kind, index),
                              'family': 'malformed-' + kind, 'order': 'ascending',
                              'container': 'list', 'repeat': repeat, 'api': api,
                              'depth': typed(depth) if api == 'restrict_reference' else None,
                              'malformed': True, 'arguments': typed(arguments)})
    depth_queries = sum(case['n'] + 1 for case in cases)
    # Counts are metadata, not oracle execution. Each generator has one full
    # evaluation at every suffix for every depth; duplicated realizations cache it.
    full_evaluations = sum(len(c['generators']) * (2 ** (c['n'] + 1) - 1) for c in cases)
    counts = {'base_cases': len(cases), 'base_depth_queries': depth_queries,
              'valid_entry_calls': sum(not c['malformed'] for c in calls),
              'malformed_entry_calls': sum(c['malformed'] for c in calls),
              'total_entry_calls': len(calls), 'oracle_full_evaluations': full_evaluations}
    expected = {'base_cases': 649, 'base_depth_queries': 1680,
                'valid_entry_calls': 23824, 'malformed_entry_calls': 128,
                'total_entry_calls': 23952}
    if any(counts[k] != v for k, v in expected.items()):
        raise ValueError('frozen count drift')
    return {'schema': 'prime-scalar.typed-manifest/v1', 'spec_sha256': SPEC_SHA256,
            'counts': counts, 'cases': cases, 'calls': calls}


def materialize(spec_path, destination, metadata_admission):
    """Caller must bind this operation to a separately checked native task.

    The receipt argument is a required reference, not an approval validator;
    this builder is intentionally not an execution-admission surface.
    """
    if not metadata_admission:
        raise ValueError('separate metadata-generation admission required')
    data = Path(spec_path).read_bytes()
    if hashlib.sha256(data).hexdigest() != SPEC_SHA256:
        raise ValueError('case specification drift')
    manifest = build(json.loads(data))
    payload = (json.dumps(manifest, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    with Path(destination).open('xb') as output:
        output.write(payload)
        output.flush()
        import os
        os.fsync(output.fileno())
    return {'metadata_admission': metadata_admission,
            'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload),
            'counts': manifest['counts']}
