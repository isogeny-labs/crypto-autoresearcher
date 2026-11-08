#!/usr/bin/env python3
"""Exact degree-0/1 joint top-syzygy screen for a named binary m=2 input."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from rank_binary_top_forms import field_mul, field_trace, binary_rank


def nullspace(rows, width):
    rows = rows[:]
    pivots = []
    pos = 0
    for col in range(width):
        found = next((i for i in range(pos, len(rows)) if rows[i] & (1 << col)), None)
        if found is None:
            continue
        rows[pos], rows[found] = rows[found], rows[pos]
        for i in range(len(rows)):
            if i != pos and rows[i] & (1 << col):
                rows[i] ^= rows[pos]
        pivots.append(col)
        pos += 1
        if pos == len(rows):
            break
    free = sorted(set(range(width)) - set(pivots))
    out = []
    for col in free:
        value = 1 << col
        for i, pivot in enumerate(pivots):
            if rows[i] & (1 << col):
                value |= 1 << pivot
        out.append(value)
    return out


def column_solver(columns):
    pivots = {}
    kernel = []
    for index, value in enumerate(columns):
        combination = 1 << index
        while value and value.bit_length() - 1 in pivots:
            reduced, source = pivots[value.bit_length() - 1]
            value ^= reduced
            combination ^= source
        if value:
            pivots[value.bit_length() - 1] = value, combination
        else:
            kernel.append(combination)

    def solve(value):
        source = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                raise ValueError("target is not in the linear image")
            reduced, combination = pivots[pivot]
            value ^= reduced
            source ^= combination
        return source

    return solve, kernel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    record = json.loads(raw)["record"]
    n = record["n"]
    modulus = int(record["modulus_hex"], 16)
    z = int(record["z_hex"], 16)
    basis = [int(value, 16) for value in record["V_basis_hex"]]
    k = len(basis)
    N = 2 * k
    if k != record["k"] or modulus.bit_length() != n + 1:
        raise ValueError("inconsistent plan record")

    def mul(a, b):
        return field_mul(a, b, n, modulus)

    def trace(a):
        return field_trace(a, n, modulus)

    z2 = mul(z, z)
    def sqrt(a):
        for _ in range(n - 1):
            a = mul(a, a)
        return a

    def T(gamma):
        y = mul(gamma, z2)
        return sqrt(y) ^ y

    solve_T, kernel_T = column_solver([T(1 << i) for i in range(n)])
    if len(kernel_T) != 1:
        raise ValueError("expected a one-dimensional trace-relation kernel")

    annihilator_rows = [sum(trace(mul(1 << t, v)) << t for t in range(n))
                        for v in basis]
    v_perp = nullspace(annihilator_rows, n)
    if len(v_perp) != n - k:
        raise ValueError("factor-base vectors are not independent")

    L = []
    pair_products = []
    for x in basis:
        row = []
        for y in basis:
            xy = mul(x, y)
            pair_products.append(xy)
            row.append(mul(xy, xy) ^ mul(z, xy))
        L.append(row)

    def s3_without_constant(x, c):
        y = x ^ c
        xy = mul(x, y)
        part = xy ^ mul(x, z) ^ mul(y, z)
        return mul(part, part) ^ mul(xy, z)

    for i, x in enumerate(basis):
        for j, c in enumerate(basis):
            direct = (s3_without_constant(x, c) ^ s3_without_constant(x, 0) ^
                      s3_without_constant(0, c) ^ s3_without_constant(0, 0))
            if direct != L[i][j]:
                raise ValueError("top coefficient disagrees with direct S3 descent")
    product_span_rank = binary_rank(pair_products)
    z_in_product_span = binary_rank(pair_products + [z]) == product_span_rank
    pairs = {item: i for i, item in enumerate(itertools.combinations(range(N), 2))}
    triples = {item: i for i, item in enumerate(itertools.combinations(range(N), 3))}
    edges = [[(i, k+j) for i in range(k) for j in range(k)
              if trace(mul(1 << t, L[i][j]))] for t in range(n)]
    q_rows = [sum(1 << pairs[edge] for edge in form) for form in edges]
    product_rows = [
        sum(1 << triples[tuple(sorted((a, b, variable)))]
            for a, b in form if variable not in (a, b))
        for form in edges for variable in range(N)
    ]
    q_rank = binary_rank(q_rows)
    if q_rank != product_span_rank - int(z_in_product_span):
        raise ValueError("quadratic rank disagrees with product-span formula")
    product_rank = binary_rank(product_rows)
    product_kernel_dim = n*N - product_rank

    def syzygy(coefficient_terms):
        vector = 0
        image = 0
        for gamma, variable in coefficient_terms:
            for t in range(n):
                if gamma & (1 << t):
                    vector ^= 1 << (t*N + variable)
                    image ^= product_rows[t*N + variable]
        if image:
            raise ValueError("claimed symbolic syzygy does not vanish")
        return vector

    trace_family = [syzygy([(kernel_T[0], variable)])
                    for variable in range(N)]
    x1_family = []
    x2_family = []
    for lam in v_perp:
        gammas = [solve_T(mul(lam, v)) for v in basis]
        x1_family.append(syzygy([(gamma, j) for j, gamma in enumerate(gammas)]))
        x2_family.append(syzygy([(gamma, j) for j, gamma in enumerate(gammas)] +
                                 [(gamma, k+j) for j, gamma in enumerate(gammas)]))
    exhibited = trace_family + x1_family + x2_family
    exhibited_rank = binary_rank(exhibited)
    if exhibited_rank > product_kernel_dim:
        raise AssertionError("exhibited kernel rank exceeds computed nullity")
    print(json.dumps({
        "schema": "semaev.binary-joint-top-syzygies/v1",
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "instance": record["name"],
        "variables": N,
        "equations": n,
        "quadratic_form_rank": q_rank,
        "product_span_rank": product_span_rank,
        "z_in_product_span": z_in_product_span,
        "direct_s3_top_coefficients_checked": k*k,
        "constant_syzygy_dimension": n - q_rank,
        "linear_multiplier_domain_dimension": n*N,
        "cubic_target_dimension": len(triples),
        "linear_multiplier_image_rank": product_rank,
        "linear_multiplier_kernel_dimension": product_kernel_dim,
        "exhibited_trace_multiples": len(trace_family),
        "exhibited_x1_v_perp": len(x1_family),
        "exhibited_x2_v_perp": len(x2_family),
        "exhibited_syzygy_rank": exhibited_rank,
        "exhibited_spans_kernel": exhibited_rank == product_kernel_dim,
        "claim": "Exact degree-zero and degree-one top-form syzygies for this named input only; no D5 full closure or LFD-six claim."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
