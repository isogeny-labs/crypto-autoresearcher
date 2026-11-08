#!/usr/bin/env python3
"""Independent exact Boolean D3 closure from a named m=2 plan record."""

import argparse
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

from rank_binary_top_forms import field_mul, field_trace


class Echelon:
    def __init__(self, low_columns):
        self.rows = {}
        self.low_columns = low_columns
        self.low_queue = deque()

    def add(self, row):
        while row:
            pivot = row.bit_length() - 1
            old = self.rows.get(pivot)
            if old is not None:
                row ^= old
            else:
                self.rows[pivot] = row
                if pivot < self.low_columns:
                    self.low_queue.append(row)
                return True
        return False

    def dimensions(self):
        return len(self.rows), sum(p < self.low_columns for p in self.rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--input-sys", type=Path)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    record = json.loads(raw)["record"]
    n = record["n"]
    modulus = int(record["modulus_hex"], 16)
    z = int(record["z_hex"], 16)
    a6 = int(record["a6_hex"], 16)
    basis = [int(value, 16) for value in record["V_basis_hex"]]
    k = len(basis)
    N = 2*k
    if k != record["k"] or modulus.bit_length() != n+1:
        raise ValueError("inconsistent plan record")

    def mul(a, b):
        return field_mul(a, b, n, modulus)

    def trace(a):
        return field_trace(a, n, modulus)

    z2 = mul(z, z)
    monomials = [sum(1 << i for i in choice)
                 for degree in range(4)
                 for choice in itertools.combinations(range(N), degree)]
    low_columns = 1 + N + N*(N-1)//2
    index = {mask: i for i, mask in enumerate(monomials)}
    multiply = [[index[mask | (1 << variable)]
                 for mask in monomials[:low_columns]]
                for variable in range(N)]

    def s3(a_mask, c_mask):
        x = 0
        c = 0
        for j, v in enumerate(basis):
            if a_mask & (1 << j): x ^= v
            if c_mask & (1 << j): c ^= v
        y = x ^ c
        xy = mul(x, y)
        part = xy ^ mul(x, z) ^ mul(y, z)
        return mul(part, part) ^ mul(xy, z) ^ a6

    coefficients = [0] * low_columns
    coefficients[0] = a6
    for j, v in enumerate(basis):
        v2 = mul(v, v)
        coefficients[index[1 << j]] = mul(v2, v2) ^ mul(z, v2)
        coefficients[index[1 << (k+j)]] = mul(z2, v2)
    for i, x in enumerate(basis):
        for j, c in enumerate(basis):
            xy = mul(x, c)
            coefficients[index[(1 << i) | (1 << (k+j))]] = mul(xy, xy) ^ mul(z, xy)

    # Reconstruct every degree-at-most-two coefficient independently by
    # Boolean interpolation of the original S3 formula.
    values = [s3(0, 0)]
    for variable in range(N):
        values.append(s3(1 << variable, 0) if variable < k
                      else s3(0, 1 << (variable-k)))
    if values[0] != coefficients[0]:
        raise ValueError("constant coefficient mismatch")
    for variable in range(N):
        if values[variable+1] ^ values[0] != coefficients[index[1 << variable]]:
            raise ValueError("linear coefficient mismatch")
    for i, j in itertools.combinations(range(N), 2):
        a_mask = ((1 << i) if i < k else 0) | ((1 << j) if j < k else 0)
        c_mask = ((1 << (i-k)) if i >= k else 0) | ((1 << (j-k)) if j >= k else 0)
        direct = s3(a_mask, c_mask) ^ values[i+1] ^ values[j+1] ^ values[0]
        if direct != coefficients[index[(1 << i) | (1 << j)]]:
            raise ValueError("quadratic coefficient mismatch")

    input_sha256 = None
    if args.input_sys is not None:
        source = args.input_sys.read_bytes()
        lines = source.decode("ascii").splitlines()
        if lines[0] != f"{N} {n}" or len(lines) != n+1:
            raise ValueError("input.sys dimensions disagree with plan")
        expected = [set() for _ in range(n)]
        original_terms = {0: a6}
        for j, v in enumerate(basis):
            linear = mul(z2, mul(v, v))
            original_terms[1 << j] = linear
            original_terms[1 << (k+j)] = linear
        for i, x in enumerate(basis):
            for j, y in enumerate(basis):
                xy = mul(x, y)
                original_terms[(1 << i) | (1 << (k+j))] = mul(xy, xy) ^ mul(z, xy)
        for mask, value in original_terms.items():
            for t in range(n):
                if value & (1 << t):
                    expected[t].add(mask)
        for t, line in enumerate(lines[1:]):
            fields = line.split()
            if int(fields[0]) != len(fields)-1:
                raise ValueError("input.sys term count disagrees with row")
            actual = {int(value, 16) for value in fields[1:]}
            if actual != expected[t] or len(actual) != len(fields)-1:
                raise ValueError(f"input.sys row {t} disagrees with direct descent")
        input_sha256 = hashlib.sha256(source).hexdigest()

    equations = [sum(trace(mul(1 << t, value)) << j
                     for j, value in enumerate(coefficients))
                 for t in range(n)]

    def times_variable(row, variable):
        out = 0
        while row:
            low_bit = row & -row
            column = low_bit.bit_length() - 1
            if column >= low_columns:
                raise ValueError("multiplying a cubic row exceeds D3")
            out ^= 1 << multiply[variable][column]
            row ^= low_bit
        return out

    macaulay = Echelon(low_columns)
    for equation in equations:
        macaulay.add(equation)
        for variable in range(N):
            macaulay.add(times_variable(equation, variable))

    closure = Echelon(low_columns)
    for equation in equations:
        closure.add(equation)
    equation_rank = len(closure.rows)
    multiplied_low_rows = 0
    while closure.low_queue:
        row = closure.low_queue.popleft()
        multiplied_low_rows += 1
        for variable in range(N):
            closure.add(times_variable(row, variable))

    m_dim, m_low = macaulay.dimensions()
    w_dim, w_low = closure.dimensions()
    print(json.dumps({
        "schema": "semaev.binary-d3-independent-replay/v1",
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "input_sys_sha256": input_sha256,
        "instance": record["name"],
        "variables": N,
        "equations": n,
        "equation_rank": equation_rank,
        "interpolated_coefficients_checked": low_columns,
        "d3_columns": len(monomials),
        "m3_dimension": m_dim,
        "m3_low_dimension": m_low,
        "degree_one_syzygy_fall_rank_mod_equations": m_low - equation_rank,
        "w3_dimension": w_dim,
        "w3_low_dimension": w_low,
        "new_low_dimension_from_iterated_closure": w_low - m_low,
        "w3_contains_one": 0 in closure.rows,
        "w3_low_rows_multiplied": multiplied_low_rows,
        "claim": "Exact independent D3 Boolean closure for the named input; no D4/D5 or LFD-six claim."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
