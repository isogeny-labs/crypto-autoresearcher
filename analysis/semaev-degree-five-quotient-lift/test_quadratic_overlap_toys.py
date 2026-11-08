#!/usr/bin/env python3
"""Cross-check the reduced overlap against a different small full-map build."""

import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
CASES = [
    (3, 0xB, [1, 2], 1, 1, 16, 17),
    (5, 0x25, [1, 2, 4], 1, 0, 49, 60),
]


def full_quadratic_kernel(n, modulus, basis, z):
    def mul(a, b):
        out = 0
        while b:
            if b & 1:
                out ^= a
            b >>= 1
            a <<= 1
            if a >> n:
                a ^= modulus
        return out

    def trace(value):
        out = 0
        for _ in range(n):
            out ^= value
            value = mul(value, value)
        if out not in (0, 1):
            raise ValueError("toy modulus failed the field-trace check")
        return out

    k = len(basis)
    variables = 2*k
    quartics = {subset: index for index, subset in enumerate(
        itertools.combinations(range(variables), 4))}
    pivots = {}
    for t in range(n):
        edges = []
        for i, x in enumerate(basis):
            for j, y in enumerate(basis):
                xy = mul(x, y)
                coefficient = mul(xy, xy) ^ mul(z, xy)
                if trace(mul(1 << t, coefficient)):
                    edges.append((i, k+j))
        for u, v in itertools.combinations(range(variables), 2):
            row = 0
            for a, b in edges:
                if len({a, b, u, v}) == 4:
                    row ^= 1 << quartics[tuple(sorted((a, b, u, v)))]
            while row:
                pivot = row.bit_length() - 1
                if pivot in pivots:
                    row ^= pivots[pivot]
                else:
                    pivots[pivot] = row
                    break
    return n*(variables*(variables-1)//2) - len(pivots)


def run_json(script, plan, *flags):
    output = subprocess.check_output(
        [sys.executable, str(HERE / script), str(plan), *flags],
        text=True, timeout=30)
    return json.loads(output)


def main():
    with tempfile.TemporaryDirectory(prefix="semaev-overlap-toys-") as temp:
        for n, modulus, basis, z, expected_overlap, expected_generated, expected_full in CASES:
            plan = Path(temp) / f"n{n}.json"
            plan.write_text(json.dumps({"record": {
                "n": n, "modulus_hex": format(modulus, "x"),
                "z_hex": format(z, "x"), "V_basis_hex": [format(v, "x") for v in basis],
                "k": len(basis), "name": f"toy-n{n}-k{len(basis)}"
            }}) + "\n")
            reduced = run_json("rank_quadratic_overlap.py", plan)
            generated = run_json("joint_binary_top_syzygies.py", plan,
                                 "--quadratic-generated")
            full = full_quadratic_kernel(n, modulus, basis, z)
            if (reduced["symmetric_linear_overlap_dimension"] != expected_overlap or
                    reduced["generated_quadratic_syzygy_rank"] != expected_generated or
                    generated["quadratic_generated"]["combined_generated_rank"] != expected_generated or
                    full != expected_full):
                raise AssertionError(f"toy n={n} disagrees across constructions")
            print(f"n={n}: overlap={expected_overlap}, generated={expected_generated}, "
                  f"full_kernel={expected_full}")


if __name__ == "__main__":
    main()
