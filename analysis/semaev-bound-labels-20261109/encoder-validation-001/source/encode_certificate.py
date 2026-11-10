#!/usr/bin/env python3
"""Encode bounded closed-kernel certificate feasibility; never run a solver.

Each equation is a canonical XOR of monomials in Boolean variable IDs.
An empty monomial [] is one; an empty equation [] is zero.
No global commutativity/idempotence constraints are added to the T matrices.
"""
import argparse
import hashlib
import itertools
import json
from math import comb
from pathlib import Path

from inspect_bounds import SCHEMA as INPUT_SCHEMA, digest, inspect

SCHEMA = 'semaev.closed-kernel-feasibility-request/v1'
MAX_INPUT_BYTES = 65536
DEFAULT_CAPS = {'variables': 10000, 'equations': 10000, 'terms': 100000}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_request(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError('input exceeds 64 KiB')
    return json.loads(raw, object_pairs_hook=unique_object), raw


def preflight(request, caps=None):
    """Compute combinatorial envelopes before descent or monomial allocation."""
    if type(request) is not dict or set(request) != {'schema', 'input', 'degree_cap', 'quotient_dimension'} or request['schema'] != SCHEMA:
        raise ValueError('exact feasibility request schema required')
    spec = request['input']
    required = {'schema', 'n', 'modulus', 'basis', 'a2', 'a6', 'z', 'require_rational_target'}
    if type(spec) is not dict or set(spec) != required or spec['schema'] != INPUT_SCHEMA:
        raise ValueError('exact normalized input schema required')
    n, basis = spec['n'], spec['basis']
    if type(n) is not int or not 3 <= n <= 64 or type(basis) is not list or not 1 <= len(basis) <= n:
        raise ValueError('invalid bounded n/basis shape')
    N, k = 2 * len(basis), len(basis)
    D, q = request['degree_cap'], request['quotient_dimension']
    if type(D) is not int or not 2 <= D <= N:
        raise ValueError('degree_cap must be an integer in [2,N]')
    if type(q) is not int or q < 1:
        raise ValueError('quotient_dimension must be a positive integer')
    caps = DEFAULT_CAPS.copy() if caps is None else dict(caps)
    if set(caps) != set(DEFAULT_CAPS):
        raise ValueError('exact variables/equations/terms caps required')
    for name, ceiling in DEFAULT_CAPS.items():
        if type(caps[name]) is not int or not 1 <= caps[name] <= ceiling:
            raise ValueError('caps may only lower the finite default: ' + name)
    # N<=128, so these arithmetic counts are bounded even on rejected inputs.
    M = sum(comb(N, d) for d in range(D + 1))
    L = M - comb(N, D)
    if q > M:
        raise ValueError('quotient_dimension exceeds monomial count')
    variables = 2 * M * q + N * q * q
    equations = q + n * q + N * L * q + q * q
    generator_support_bound = 1 + 2 * k + k * k
    terms_upper = (q + 1) + n * q * generator_support_bound + N * L * q * (q + 1) + q * q * M + q
    for name, value in [('variables', variables), ('equations', equations), ('terms', terms_upper)]:
        if value > caps[name]:
            raise ValueError('preflight ' + name + ' cap exceeded')
    return {'n': n, 'k': k, 'N': N, 'D': D, 'q': q, 'M': M, 'L': L,
            'variables': variables, 'equations': equations,
            'nonzero_terms_upper_bound': terms_upper, 'caps': caps}


def canonical_terms(terms):
    present = set()
    for term in terms:
        # Unknowns are Boolean, so repeated factors collapse; coefficients XOR.
        monomial = tuple(sorted(set(term)))
        if monomial in present:
            present.remove(monomial)
        else:
            present.add(monomial)
    return [list(term) for term in sorted(present, key=lambda item: (len(item), item))]


def encode(request, caps=None):
    counts = preflight(request, caps)
    # This bounded inspection performs exact reconstruction, with product enumeration disabled.
    inspected = inspect(request['input'], product_limit=0)
    binding = inspected['equation_binding']
    N, D, q, M, L = [counts[key] for key in ('N', 'D', 'q', 'M', 'L')]
    masks = []
    for degree in range(D + 1):
        masks.extend(sorted(sum(1 << i for i in indices) for indices in itertools.combinations(range(N), degree)))
    if len(masks) != M:
        raise RuntimeError('internal monomial count mismatch')
    positions = {mask: i for i, mask in enumerate(masks)}
    c_offset, t_offset, r_offset = 0, M * q, M * q + N * q * q
    c_id = lambda m, a: c_offset + positions[m] * q + a
    t_id = lambda i, a, b: t_offset + (i * q + a) * q + b
    r_id = lambda j, b: r_offset + j * q + b
    equations = []
    def emit(kind, indices, terms):
        equations.append({'kind': kind, 'indices': indices, 'terms': canonical_terms(terms)})
    for a in range(q):
        emit('unit', [a], [[c_id(0, a)]] + ([[]] if a == 0 else []))
    for j, equation in enumerate(binding['equations']):
        for a in range(q):
            emit('generator', [j, a], ([c_id(m, a)] for m in equation))
    for i in range(N):
        for m in masks[:L]:
            for a in range(q):
                terms = [[t_id(i, a, b), c_id(m, b)] for b in range(q)]
                terms.append([c_id(m | (1 << i), a)])
                emit('closure', [i, m, a], terms)
    for a in range(q):
        for b in range(q):
            terms = [[c_id(m, a), r_id(j, b)] for j, m in enumerate(masks)]
            if a == b:
                terms.append([])
            emit('right_inverse', [a, b], terms)
    terms = sum(len(e['terms']) for e in equations)
    if len(equations) != counts['equations'] or terms > counts['nonzero_terms_upper_bound']:
        raise RuntimeError('internal preflight envelope mismatch')
    layout = {
        'C': {'offset': c_offset, 'shape': [M, q], 'axes': ['monomial_index', 'quotient_coordinate']},
        'T': {'offset': t_offset, 'shape': [N, q, q], 'axes': ['input_variable', 'output_coordinate', 'input_coordinate']},
        'R': {'offset': r_offset, 'shape': [M, q], 'axes': ['monomial_index', 'right_inverse_column']},
        'flattening': 'row-major, zero-based IDs',
    }
    payload = {'variable_count': counts['variables'], 'variable_domain': 'Boolean GF(2)',
               'layout': layout, 'monomial_order': 'degree then numeric mask',
               'monomial_masks': masks, 'equations': equations}
    return {'schema': 'semaev.closed-kernel-feasibility-encoding/v1',
            'request_sha256': digest(request), 'input_sha256': inspected['input_sha256'],
            'equation_binding_sha256': inspected['equation_binding_sha256'], 'equation_binding': binding,
            'encoding_sha256': digest(payload), 'encoding': payload,
            'preflight': counts, 'actual_nonzero_terms': terms,
            'solver_executed': False, 'certificate_found': None, 'lfd_lower_bound': None,
            'exact_lfd': None, 'dataset_admission': False,
            'claim_scope': 'finite algebraic feasibility encoding only; no satisfiability or degree conclusion'}


def write_output(path, result):
    with Path(path).open('x', encoding='utf-8') as output:
        json.dump(result, output, sort_keys=True, indent=2)
        output.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    for name, default in DEFAULT_CAPS.items():
        parser.add_argument('--max-' + name, type=int, default=default)
    args = parser.parse_args()
    request, raw = read_request(args.input)
    caps = {name: getattr(args, 'max_' + name) for name in DEFAULT_CAPS}
    result = encode(request, caps)
    result['input_file_sha256'] = hashlib.sha256(raw).hexdigest()
    result['encoder_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['inspector_sha256'] = hashlib.sha256(Path(__file__).with_name('inspect_bounds.py').read_bytes()).hexdigest()
    write_output(args.output, result)

if __name__ == '__main__':
    main()
