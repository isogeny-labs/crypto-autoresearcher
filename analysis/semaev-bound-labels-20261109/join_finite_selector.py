#!/usr/bin/env python3
"""Check exact retained binary m2 selector polynomials and label a safe LFD cap."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_bounds import Field, digest
from join_retained_weil import REQUIRED, decimal, polys, read

SCHEMA = 'semaev.finite-selector-parameters/v1'


def anf(values, bits):
    out = list(values)
    for i in range(bits):
        for mask in range(1 << bits):
            if mask & (1 << i):
                out[mask] ^= out[mask ^ (1 << i)]
    return out


def coordinate_rows(coefficients, n):
    return [[mask for mask, value in enumerate(coefficients) if value >> j & 1]
            for j in range(n)]


def check(parameters, artifact):
    if not isinstance(parameters, dict) or set(parameters) != {'schema', 'n', 'modulus', 'a6', 'z'} or parameters['schema'] != SCHEMA:
        raise ValueError('exact finite-selector parameter schema required')
    field = Field(parameters['n'], parameters['modulus'])
    n = field.n
    for key in ('a6', 'z'):
        if type(parameters[key]) is not int or not 0 <= parameters[key] < 1 << n:
            raise ValueError('noncanonical field parameter')
    if not parameters['a6']:
        raise ValueError('singular binary curve parameter')
    if not isinstance(artifact, dict) or set(artifact) != REQUIRED:
        raise ValueError('exact retained producer format required')
    if type(artifact['lifting_required']) is not bool or not artifact['lifting_required']:
        raise ValueError('lifting flag required')
    if (artifact['coefficient_field'], artifact['quotient'], artifact['monomial_order']) != ('F2', 'v_i^2+v_i', 'degrevlex'):
        raise ValueError('unsupported polynomial encoding')
    k = artifact['selector_bits_per_summand']
    if type(k) is not int or not 0 <= k <= 6:
        raise ValueError('selector bits outside [0,6]')
    nv = 2*k
    for key, value in [('n_vars', nv), ('field_degree', n)]:
        if type(artifact[key]) is not int or artifact[key] != value:
            raise ValueError('dimension mismatch')
    low = artifact['irreducible_low_terms']
    if not isinstance(low, list) or any(type(i) is not int or not 0 <= i < n for i in low) or len(set(low)) != len(low):
        raise ValueError('invalid modulus terms')
    if sorted(low) != [i for i in range(n) if parameters['modulus'] >> i & 1]:
        raise ValueError('modulus mismatch')
    if decimal(artifact['target_x']) != parameters['z']:
        raise ValueError('target mismatch')
    codes = artifact['selector_codes']
    if not isinstance(codes, list) or len(codes) != 1 << k:
        raise ValueError('selector table length mismatch')
    codes = [decimal(v) for v in codes]
    if any(v >= 1 << n for v in codes):
        raise ValueError('selector field value out of range')
    distinct = sorted(set(codes))
    if (len(distinct)-1).bit_length() != k or codes != [distinct[i % len(distinct)] for i in range(1 << k)]:
        raise ValueError('selector table differs from sorted cyclic producer policy')
    maps = artifact['coordinate_maps']
    if not isinstance(maps, list) or len(maps) != 2:
        raise ValueError('two coordinate maps required')
    coefficients = anf(codes, k)
    for side in range(2):
        expected = [[mask << (side*k) for mask in row] for row in coordinate_rows(coefficients, n)]
        if polys(maps[side], n, nv) != expected:
            raise ValueError('coordinate map mismatch')
    z = parameters['z']; z2 = field.mul(z, z)
    values = []
    for assignment in range(1 << nv):
        x = codes[assignment & ((1 << k)-1)]
        y = codes[assignment >> k]
        xy = field.mul(x, y)
        values.append(field.mul(xy, xy) ^ field.mul(z, xy) ^ field.mul(z2, field.mul(x ^ y, x ^ y)) ^ parameters['a6'])
    expected = coordinate_rows(anf(values, nv), n)
    if polys(artifact['equations'], n, nv) != expected:
        raise ValueError('literal equation mismatch')
    # A bound for the specified dense queue algorithm, not observed solver work.
    dimension = 1 << nv
    attempts = n + nv*dimension
    closure_cost = {
        'algorithm': 'immutable-degree-ordered-dense-boolean-closure/v1',
        'status': 'theorem_derived_upper_bound_not_executed',
        'degree_cap': nv+1, 'input_rows': n,
        'monomial_columns': dimension, 'eligible_pivot_bound': dimension,
        'candidate_insertion_bound': attempts,
        'whole_row_xor_bound': attempts*dimension,
        'coefficient_bit_xor_bound': attempts*dimension*dimension,
        'variable_product_column_visit_bound': nv*dimension*dimension,
        'dense_basis_coefficient_storage_bits_bound': dimension*dimension,
        'arithmetic_model': 'unit indexed bit access; coefficient XORs counted separately',
        'excluded_costs': ['input parsing and validation', 'field and ANF reconstruction',
                           'monomial indexing', 'queue and pivot metadata',
                           'solution extraction', 'proof provenance', 'I/O'],
        'native_instruction_count': None, 'wall_time_bound_seconds': None,
        'training_cost_eligible': False,
        'theorem': 'generic-strict-closure-operation-bound.md',
    }
    return {
        'schema': 'semaev.finite-selector-bound-join/v1',
        'parameters_sha256': digest(parameters), 'retained_artifact_sha256_canonical': digest(artifact),
        'closure_algorithm_cost_bound': closure_cost,
        'n_vars': nv, 'selector_table_entries': len(codes), 'distinct_selector_values': len(distinct),
        'last_fall_degree': {'lower_bound': None, 'upper_bound': nv+1, 'exact': None,
                             'reason': 'finite_boolean_ring_full_cap'},
        'first_fall_degree': None, 'solution_count': None,
        'original_dataset_equations_match': True, 'selector_domain_and_maps_match': True,
        'bound_labels_admission': True, 'dataset_admission': False,
        'point_domain_and_group_lifts_verified': False, 'producer_provenance_authenticated': False,
        'theorem': 'finite-selector-bounds-and-transfer.md', 'formal_kernel_certification': False,
        'scope': 'normalized Boolean polynomial system; no group lifts or authenticated production admission',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters', type=Path); parser.add_argument('retained_weil', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parameters, ph = read(args.parameters); artifact, ah = read(args.retained_weil)
    result = check(parameters, artifact)
    result.update(parameters_file_sha256=ph, retained_file_sha256=ah)
    result['source_hashes'] = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                              for name in ['join_finite_selector.py', 'join_retained_weil.py', 'inspect_bounds.py',
                                           'finite-selector-bounds-and-transfer.md', 'finite-selector-bounds-review.md',
                                           'generic-strict-closure-operation-bound.md', 'generic-strict-closure-operation-review.md']}
    with args.output.open('x') as out:
        json.dump(result, out, sort_keys=True, indent=2); out.write('\n')


if __name__ == '__main__':
    main()
