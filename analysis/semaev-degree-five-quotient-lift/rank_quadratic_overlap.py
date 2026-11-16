#!/usr/bin/env python3
"""Exact small-matrix overlap test for named odd-degree binary S3 top syzygies.

This computes the intersection of the symmetric top-syzygy family and the
variable lifts of the explicit degree-one family. It does not compute the
full quadratic-multiplier kernel or a last-fall degree.
"""

import argparse
import hashlib
import json
from pathlib import Path

from joint_binary_top_syzygies import nullspace
from rank_binary_top_forms import binary_rank, field_mul, field_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    rec = json.loads(raw)["record"]
    n = rec["n"]
    basis = [int(value, 16) for value in rec["V_basis_hex"]]
    k = len(basis)
    if n % 2 != 1 or k < 2 or k != rec["k"] or n*k*k > 30000:
        raise ValueError("outside bounded odd-degree overlap screen")
    modulus = int(rec["modulus_hex"], 16)
    z = int(rec["z_hex"], 16)
    if not z or binary_rank(basis) != k:
        raise ValueError("invalid nonzero target or factor-base basis")

    def mul(a, b):
        return field_mul(a, b, n, modulus)

    def trace(a):
        return field_trace(a, n, modulus)

    def power(a, exponent):
        out = 1
        while exponent:
            if exponent & 1:
                out = mul(out, a)
            a = mul(a, a)
            exponent >>= 1
        return out

    inverse_z = power(z, (1 << n) - 2)
    if mul(z, inverse_z) != 1 or trace(1) != 1:
        raise ValueError("field inverse or odd-degree trace check failed")
    product_rank = binary_rank([mul(x, y) for x in basis for y in basis])
    if product_rank != n:
        raise ValueError("proof reduction requires full product span")

    projected = []
    for x in basis:
        for y in basis:
            value = mul(mul(x, y), inverse_z)
            projected.append(value ^ trace(value))
    squares = [projected[i*k+i] for i in range(k)]
    square_rank = binary_rank(squares)
    trace_row = sum(trace(1 << t) << t for t in range(n))
    square_rows = [sum(trace(mul(1 << t, value)) << t for t in range(n))
                   for value in squares]
    orthogonal = nullspace([trace_row, *square_rows], n)
    if len(orthogonal) != n-1-square_rank:
        raise ValueError("square orthogonal dimension mismatch")
    v_perp_rows = [sum(trace(mul(1 << t, value)) << t for t in range(n))
                   for value in basis]
    v_perp = nullspace(v_perp_rows, n)
    if len(v_perp) != n-k:
        raise ValueError("factor-base annihilator dimension mismatch")

    def flatten(values):
        return sum(value << (n*index) for index, value in enumerate(values))

    # F_A(x,s)=x*A(s)+s*A(x), with one basis value A(v_b)=lambda.
    annihilator_rows = []
    for b in range(k):
        for lam in v_perp:
            products = [mul(v, lam) for v in basis]
            values = [((products[i] if j == b else 0) ^
                       (products[j] if i == b else 0))
                      for i in range(k) for j in range(k)]
            if any(trace(value) for value in values):
                raise ValueError("annihilator image escaped K0")
            annihilator_rows.append(flatten(values))

    # Every self-adjoint L killing the projected-square subspace is a
    # symmetric tensor on the orthogonal complement. Rank-one and exchange
    # tensors form an exact basis of that space.
    evaluations = [[trace(mul(u, value)) for value in projected]
                   for u in orthogonal]
    symmetric_rows = []
    for i, u in enumerate(orthogonal):
        symmetric_rows.append(flatten([u if bit else 0 for bit in evaluations[i]]))
        for j in range(i+1, len(orthogonal)):
            v = orthogonal[j]
            symmetric_rows.append(flatten([
                (u if evaluations[j][cell] else 0) ^
                (v if evaluations[i][cell] else 0)
                for cell in range(k*k)
            ]))

    rank_a = binary_rank(annihilator_rows)
    rank_l = binary_rank(symmetric_rows)
    rank_union = binary_rank(annihilator_rows + symmetric_rows)
    expected_a = k*(n-k)
    expected_l = (n-1-square_rank)*(n-square_rank)//2
    if rank_a != expected_a or rank_l != expected_l:
        raise ValueError("one of the proof-basis rank checks failed")
    intersection = rank_a + rank_l - rank_union
    trace_lifts = (2*k)*(2*k-1)//2
    nontrace_lifts = 4*k*(n-k)
    independent_symmetric = (n-1)*n//2
    generated_rank = trace_lifts + nontrace_lifts + independent_symmetric - intersection
    print(json.dumps({
        "schema": "semaev.binary-quadratic-overlap/v1",
        "instance": rec["name"],
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "n": n,
        "k": k,
        "product_span_rank": product_rank,
        "projected_square_rank": square_rank,
        "square_orthogonal_dimension": len(orthogonal),
        "annihilator_basis_vectors": len(annihilator_rows),
        "annihilator_image_rank": rank_a,
        "symmetric_quotient_basis_vectors": len(symmetric_rows),
        "symmetric_quotient_rank": rank_l,
        "combined_image_rank": rank_union,
        "symmetric_linear_overlap_dimension": intersection,
        "generated_quadratic_syzygy_rank": generated_rank,
        "claim": "Exact overlap and resulting generated-subspace rank only; no full quadratic kernel, D4 closure, or LFD claim."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
