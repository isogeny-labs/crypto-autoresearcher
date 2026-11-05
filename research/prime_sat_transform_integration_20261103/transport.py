"""UNVALIDATED exact assignment and range-state transport; original signed checks."""
from collections import Counter
from copy import deepcopy
from contextlib import nullcontext
from .transform import authenticate_transform, composition, require


def _scope(attempt, name, counters=None):
    return attempt.phase(name, counters) if attempt else nullcontext()


def _auth(document, trusted_descriptor, mode):
    auth = authenticate_transform(document, trusted_descriptor, mode)
    require(auth['status'] == 'applicable', 'requested transform not applicable')
    return auth


def reconstruct_original_assignment(document, assignment, trusted_descriptor, mode, *, attempt=None):
    with _scope(attempt, 'transport.authentication'):
        auth = _auth(document, trusted_descriptor, mode)
    counts = Counter()
    with _scope(attempt, 'transport.inverse', lambda: dict(counts)):
        require(type(assignment) is dict and set(assignment) == set(document['variable_orders']['transformed']),
                'complete transformed assignment required')
        p = trusted_descriptor['p']; original = deepcopy(assignment)
        for name, value in assignment.items():
            counts['canonical_field_checks'] += 1
            require(type(value) is int and 0 <= value < p, 'canonical transformed value: '+name)
        if mode != 'identity':
            a, b = trusted_descriptor['target']
            original['chart.A0'] = (b - a*assignment['chart.A1']) % p
            counts.update(field_multiplications=1, field_subtractions=1, modular_reductions=1)
        require(set(original) == set(document['variable_orders']['original']), 'inverse variable bijection')
    return {'assignment': original, 'costs': {'authentication': auth, 'inverse': dict(counts)}}


def project_original_coefficients(document, assignment, trusted_descriptor, mode, *, attempt=None):
    result = reconstruct_original_assignment(document, assignment, trusted_descriptor, mode, attempt=attempt)
    names = document['projections']['original']
    return {'names': names[:], 'values': [result['assignment'][name] for name in names],
            'costs': result['costs']}


def encode_transformed_assignment(document, original_assignment, trusted_descriptor, mode, *, attempt=None):
    c = composition()
    with _scope(attempt, 'encode.transform_authentication'):
        auth = _auth(document, trusted_descriptor, mode)
    with _scope(attempt, 'encode.original_residuals'):
        checked = c.check_chart_assignment(document['original'], original_assignment, trusted_descriptor)
        require(checked['status'] == 'valid', 'supplied original assignment must satisfy every original row')
    reduced = {name: original_assignment[name] for name in document['variable_orders']['transformed']}
    inverse = reconstruct_original_assignment(document, reduced, trusted_descriptor, mode, attempt=attempt)
    comparison = Counter()
    with _scope(attempt, 'encode.inverse_comparison', lambda: dict(comparison)):
        require(c.compiler().same(inverse['assignment'], original_assignment, comparison), 'inverse must recover all original values')
    rd = document['range_document']
    with _scope(attempt, 'encode.transformed_range'):
        result = c.compiler().encode_assignment_counted(rd, reduced, rd['descriptor'], 'range')
    with _scope(attempt, 'encode.original_range'):
        original_bits = c.encode_chart_counted(document['original'], original_assignment, trusted_descriptor)
    return {'bits': result['bits'], 'assignment': reduced, 'original_bits': original_bits['bits'],
            'costs': {'authentication': auth, 'original_residuals': checked,
                      'inverse': inverse['costs'], 'inverse_comparison': dict(comparison), 'transformed_encoding': result['costs'],
                      'original_encoding': original_bits['costs']}}


def decode_and_check_original(document, bits, trusted_descriptor, mode, *, attempt=None):
    c = composition()
    with _scope(attempt, 'decode.transform_authentication'):
        auth = _auth(document, trusted_descriptor, mode)
    rd = document['range_document']
    with _scope(attempt, 'decode.transformed_range'):
        decoded = c.compiler().decode_assignment(rd, bits, rd['descriptor'], 'range')
    with _scope(attempt, 'decode.transformed_residuals'):
        residuals = c._evaluate(document['source'], decoded['assignment'])
        require(residuals['status'] == 'valid', 'transformed model is not a root')
    inverse = reconstruct_original_assignment(document, decoded['assignment'], trusted_descriptor, mode, attempt=attempt)
    with _scope(attempt, 'decode.original_encoding'):
        encoded = c.encode_chart_counted(document['original'], inverse['assignment'], trusted_descriptor)
    # Unchanged aggregate, recovery and independent signed checker, including
    # exact multiplicities and all common-root beta branches.
    with _scope(attempt, 'decode.original_signed_check', lambda: dict(c.q.EVENTS)):
        original = c.decode_chart_counted(document['original'], encoded['bits'], trusted_descriptor)
    comparison = Counter()
    with _scope(attempt, 'decode.original_comparison', lambda: dict(comparison)):
        require(c.compiler().same(original['assignment'], inverse['assignment'], comparison), 'original roundtrip mismatch')
    with _scope(attempt, 'decode.reencode_range'):
        back = c.compiler().encode_assignment_counted(rd, decoded['assignment'], rd['descriptor'], 'range')
        require(type(bits) is int and back['bits'] == bits, 'canonical transformed range-state fiber mismatch')
    return {'assignment': original['assignment'], 'transformed_assignment': decoded['assignment'],
            'original_bits': encoded['bits'], 'transformed_bits': bits,
            'projection': original['projection'], 'chart': original['chart'], 'recovered': original['recovered'],
            'costs': {'authentication': auth, 'range_decoding': decoded['costs'],
                      'transformed_residuals': residuals['costs'], 'inverse': inverse['costs'],
                      'original_encoding': encoded['costs'], 'original_comparison': dict(comparison), 'original_checks': original['costs'],
                      'range_reencoding': back['costs']}}
