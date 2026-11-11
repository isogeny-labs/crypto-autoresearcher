#!/usr/bin/env python3
"""Produce an explicit original-generator XOR witness for the n51 trace slice."""

import argparse
import hashlib
import json
from pathlib import Path

from verify_n50_poly03_d3_rank import multiply
from verify_retained_m2_w3_item import generators


EXPECTED_PLAN_SHA256 = 'd6ce88c49ea3f9ca75bf9ff4462643da73e56d75463592f5fce662b14923d2a1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def power(value, exponent, n, modulus):
    result = 1
    while exponent:
        if exponent & 1:
            result = multiply(result, value, n, modulus)
        value = multiply(value, value, n, modulus)
        exponent >>= 1
    return result


def trace(value, n, modulus):
    total = 0
    for _ in range(n):
        total ^= value
        value = multiply(value, value, n, modulus)
    if total not in (0, 1):
        raise ValueError('field trace is not a base-field bit')
    return total


def span_witness(polys, target):
    masks = sorted(set().union(*polys, target))
    columns = {mask: i for i, mask in enumerate(masks)}

    def vector(poly):
        result = 0
        for mask in poly:
            result ^= 1 << columns[mask]
        return result

    pivots = {}
    for i, poly in enumerate(polys):
        row, witness = vector(poly), 1 << i
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row, witness
                break
            row ^= pivots[lead][0]
            witness ^= pivots[lead][1]
    row, witness = vector(target), 0
    while row:
        lead = row.bit_length() - 1
        if lead not in pivots:
            raise ValueError('trace relation is outside original generator span')
        row ^= pivots[lead][0]
        witness ^= pivots[lead][1]
    indices = [i for i in range(len(polys)) if witness >> i & 1]
    checked = set()
    for i in indices:
        checked.symmetric_difference_update(polys[i])
    if checked != target:
        raise ValueError('constructed generator XOR differs from target')
    return indices


def run(plan_path, descent_source, system_path, witness_path):
    if sha(plan_path) != EXPECTED_PLAN_SHA256:
        raise ValueError('named plan changed')
    record = json.loads(plan_path.read_text())['record']
    if (record['name'], record['n'], record['k']) != ('fresh-n51-poly-00', 51, 26):
        raise ValueError('wrong named input')
    n, k = record['n'], record['k']
    modulus = int(record['modulus_hex'], 16)
    z = int(record['z_hex'], 16)
    a6 = int(record['a6_hex'], 16)
    basis = [int(value, 16) for value in record['V_basis_hex']]
    z_squared = multiply(z, z, n, modulus)
    alpha = multiply(a6, power(z_squared, (1 << n) - 2, n, modulus),
                     n, modulus)
    constant = trace(alpha, n, modulus)
    variables = [i for i, value in enumerate(basis) if trace(value, n, modulus)]
    variables += [k + i for i, value in enumerate(basis)
                  if trace(value, n, modulus)]
    if constant != 1 or variables != [0, k]:
        raise ValueError('named trace relation is not 1+a0+b0')
    target = {0, 1, 1 << k}
    polys = generators(record)
    indices = span_witness(polys, target)
    lines = [f'{2 * k} {len(polys)}']
    for poly in polys:
        terms = sorted(poly)
        lines.append(str(len(terms)) + ' ' + ' '.join(f'{mask:x}' for mask in terms))
    system = ('\n'.join(lines) + '\n').encode('ascii')
    with system_path.open('xb') as stream:
        stream.write(system)
    proof = {'schema': 'semaev.affine-span-witness/v1',
             'instance': record['name'],
             'input_sys_sha256': sha(system_path),
             'plan_sha256': sha(plan_path),
             'descent_source_sha256': sha(descent_source),
             'variables': 2 * k, 'generators': len(polys),
             'constant': constant,
             'relation_variable_indices': variables,
             'generator_indices_zero_based': indices,
             'claim': 'The XOR of these original generators is 1+a0+b0.'}
    with witness_path.open('x') as stream:
        json.dump(proof, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'schema': 'semaev.n51-poly00-affine-span-derived/v1',
                      'system_sha256': sha(system_path),
                      'witness_sha256': sha(witness_path),
                      'generator_terms': len(indices),
                      'relation_variable_indices': variables,
                      'constant': constant}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--descent-source', required=True, type=Path)
    parser.add_argument('--system-out', required=True, type=Path)
    parser.add_argument('--witness-out', required=True, type=Path)
    args = parser.parse_args()
    run(args.plan, args.descent_source, args.system_out, args.witness_out)
