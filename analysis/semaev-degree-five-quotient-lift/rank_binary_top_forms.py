#!/usr/bin/env python3
"""Exact bilinear top-form ranks for a named binary m=2 plan record."""

import argparse
import hashlib
import json
from pathlib import Path


def field_mul(a, b, n, modulus):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= modulus
    return out


def field_trace(a, n, modulus):
    out = 0
    for _ in range(n):
        out ^= a
        a = field_mul(a, a, n, modulus)
    if out not in (0, 1):
        raise ValueError("modulus does not give the expected base-field trace")
    return out


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def rank_for_mu(mu, products, n, modulus):
    rows = [
        sum(field_trace(field_mul(mu, value, n, modulus), n, modulus) << j
            for j, value in enumerate(row))
        for row in products
    ]
    return binary_rank(rows)


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
    if len(basis) != record["k"] or modulus.bit_length() != n + 1:
        raise ValueError("inconsistent plan record")
    products = []
    for x in basis:
        row = []
        for y in basis:
            xy = field_mul(x, y, n, modulus)
            row.append(field_mul(xy, xy, n, modulus) ^
                       field_mul(z, xy, n, modulus))
        products.append(row)
    selected = {hex(mu): rank_for_mu(mu, products, n, modulus)
                for mu in (1, 2, 3, z)}
    coordinate_ranks = [rank_for_mu(1 << i, products, n, modulus)
                        for i in range(n)]
    print(json.dumps({
        "schema": "semaev.binary-top-form-rank-screen/v1",
        "claim": "Exact ranks for selected and basis trace functionals only; no joint syzygy or LFD claim.",
        "plan_sha256": hashlib.sha256(raw).hexdigest(),
        "instance": record["name"],
        "n": n,
        "k": record["k"],
        "selected_mu_ranks": selected,
        "coordinate_basis_rank_histogram": {
            str(rank): coordinate_ranks.count(rank)
            for rank in sorted(set(coordinate_ranks))
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
