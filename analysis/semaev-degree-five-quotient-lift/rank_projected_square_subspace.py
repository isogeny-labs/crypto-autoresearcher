#!/usr/bin/env python3
"""Exact rank of pi(V^[2]/z) for a frozen odd-degree binary Semaev plan."""

import argparse
import hashlib
import json
from pathlib import Path

from rank_binary_top_forms import binary_rank, field_mul, field_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    rec = json.loads(raw)["record"]
    n = rec["n"]
    modulus = int(rec["modulus_hex"], 16)
    z = int(rec["z_hex"], 16)
    basis = [int(value, 16) for value in rec["V_basis_hex"]]
    if n % 2 != 1 or not z or len(basis) != rec["k"]:
        raise ValueError("expected a nonzero target and odd-degree named input")

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
    squares = [mul(v, v) for v in basis]
    projected = []
    for value in squares:
        scaled = mul(value, inverse_z)
        projected.append(scaled ^ trace(scaled))
    if any(trace(value) for value in projected):
        raise ValueError("projection did not land in the trace-zero space")
    rank_basis = binary_rank(basis)
    rank_squares = binary_rank(squares)
    if rank_basis != len(basis) or rank_squares != len(basis):
        raise ValueError("factor-base basis or Frobenius image lost rank")

    print(json.dumps({
        "schema": "semaev.projected-square-rank/v1",
        "instance": rec["name"],
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "n": n,
        "k": len(basis),
        "trace_one": trace(1),
        "basis_rank": rank_basis,
        "square_rank": rank_squares,
        "projected_square_rank": binary_rank(projected),
        "z_in_square_subspace": binary_rank(squares + [z]) == len(basis),
        "claim": "Exact rank of pi(V^[2]/z) for this named input; no full syzygy-kernel or LFD claim."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
