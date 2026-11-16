#!/usr/bin/env python3
"""Exact full quadratic-multiplier top-map rank for one bounded binary S3 input.

This ranks A_2 tensor F_top -> A_4 in the square-zero associated graded
Boolean algebra. It does not compute W4, W5, a quotient certificate, or LFD.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

from rank_binary_top_forms import binary_rank, field_mul, field_trace


def rank_for_plan(plan_path):
    raw = plan_path.read_bytes()
    rec = json.loads(raw)["record"]
    n = rec["n"]
    modulus = int(rec["modulus_hex"], 16)
    z = int(rec["z_hex"], 16)
    basis = [int(value, 16) for value in rec["V_basis_hex"]]
    k = len(basis)
    N = 2*k
    pair_count = N*(N-1)//2
    quartic_count = N*(N-1)*(N-2)*(N-3)//24
    if (k != rec["k"] or not z or n < 3 or n > 47 or N > 48 or
            n*pair_count > 53016 or quartic_count > 194580):
        raise ValueError("outside frozen full-top-rank resource envelope")
    if binary_rank(basis) != k or modulus.bit_length() != n+1:
        raise ValueError("invalid named field or factor-base basis")

    def mul(a, b):
        return field_mul(a, b, n, modulus)

    def trace(a):
        return field_trace(a, n, modulus)

    product_values = [mul(x, y) for x in basis for y in basis]
    top_values = [mul(value, value) ^ mul(z, value)
                  for value in product_values]
    pairs = list(itertools.combinations(range(N), 2))
    quartics = {choice: index for index, choice in enumerate(
        itertools.combinations(range(N), 4))}
    edges = []
    q_rows = []
    pair_index = {choice: index for index, choice in enumerate(pairs)}
    for t in range(n):
        form = [(i, k+j) for i in range(k) for j in range(k)
                if trace(mul(1 << t, top_values[i*k+j]))]
        edges.append(form)
        q_rows.append(sum(1 << pair_index[edge] for edge in form))
    quadratic_rank = binary_rank(q_rows)
    product_rank = binary_rank(product_values)
    z_in_products = binary_rank(product_values + [z]) == product_rank
    if quadratic_rank != product_rank - int(z_in_products):
        raise ValueError("top-form rank disagrees with product-span identity")

    row_bytes = (quartic_count + 7)//8
    pivots = {}
    rank_by_equation = []
    for t, form in enumerate(edges):
        for u, v in pairs:
            row = bytearray(row_bytes)
            for a, b in form:
                if a == u or a == v or b == u or b == v:
                    continue
                column = quartics[tuple(sorted((a, b, u, v)))]
                row[column >> 3] ^= 1 << (column & 7)
            value = int.from_bytes(row, "little")
            while value:
                pivot = value.bit_length() - 1
                old = pivots.get(pivot)
                if old is None:
                    pivots[pivot] = value
                    break
                value ^= old
        rank_by_equation.append(len(pivots))
        print(f"equation {t+1}/{n}: rank {len(pivots)}", file=sys.stderr,
              flush=True)

    image_rank = len(pivots)
    return {
        "schema": "semaev.binary-full-quadratic-top-rank/v1",
        "instance": rec["name"],
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "n": n,
        "k": k,
        "variables": N,
        "product_span_rank": product_rank,
        "z_in_product_span": z_in_products,
        "quadratic_form_rank": quadratic_rank,
        "multiplier_domain_dimension": n*pair_count,
        "quartic_target_dimension": quartic_count,
        "image_rank": image_rank,
        "full_top_kernel_dimension": n*pair_count - image_rank,
        "rank_by_equation": rank_by_equation,
        "claim": "Exact full degree-two-multiplier top kernel for one named input; no bounded W4 closure, D5 certificate or LFD claim."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    print(json.dumps(rank_for_plan(args.plan), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
