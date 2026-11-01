#!/usr/bin/env sage
"""Sage-only independent verifiers for EXP-ICEX-153c34 S0."""

import argparse
import hashlib
import importlib.util
import json
import resource
import sys
import time

from sage.all import EllipticCurve, GF, PolynomialRing


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def f3(a, b, u, v, w):
    return ((u - v) ** 2 * w ** 2
            - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + (u * v - a) ** 2 - 4 * b * (u + v))


def fixed_coefficients(poly, variable_index, degree, ring):
    """Low-to-high coefficients, retaining every formal zero slot."""
    variables = ring.gens()
    out = [ring.zero() for _ in range(degree + 1)]
    for monomial, coefficient in poly.dict().items():
        exponent = monomial[variable_index]
        if exponent > degree:
            raise ArithmeticError("formal resultant degree exceeded")
        powers = list(monomial)
        powers[variable_index] = 0
        term = ring(coefficient)
        for variable, power in zip(variables, powers):
            if power:
                term *= variable ** power
        out[exponent] += term
    return out


def sylvester(low_a, low_b, ring):
    degree_a, degree_b = len(low_a) - 1, len(low_b) - 1
    size = degree_a + degree_b
    matrix = [[ring.zero() for _ in range(size)] for _ in range(size)]
    for row in range(degree_b):
        for column, value in enumerate(low_a):
            matrix[row][row + column] = value
    for row in range(degree_a):
        for column, value in enumerate(low_b):
            matrix[degree_b + row][row + column] = value
    return matrix


def determinant_bareiss(source, ring):
    matrix = [list(row) for row in source]
    size = len(matrix)
    previous, sign = ring.one(), 1
    for pivot_column in range(size - 1):
        pivot_row = next((row for row in range(pivot_column, size)
                          if matrix[row][pivot_column] != 0), None)
        if pivot_row is None:
            return ring.zero()
        if pivot_row != pivot_column:
            matrix[pivot_column], matrix[pivot_row] = matrix[pivot_row], matrix[pivot_column]
            sign = -sign
        pivot = matrix[pivot_column][pivot_column]
        for row in range(pivot_column + 1, size):
            for column in range(pivot_column + 1, size):
                numerator = (pivot * matrix[row][column]
                             - matrix[row][pivot_column] * matrix[pivot_column][column])
                if pivot_column:
                    quotient, remainder = numerator.quo_rem(previous)
                    if remainder != 0:
                        raise ArithmeticError("Bareiss division was not exact")
                    numerator = quotient
                matrix[row][column] = numerator
            matrix[row][pivot_column] = ring.zero()
        previous = pivot
    return sign * matrix[-1][-1]


def determinant_subset_dp(matrix, ring):
    size = len(matrix)
    states = {0: ring.one()}
    for row in range(size):
        next_states = {}
        for mask, subtotal in states.items():
            for column in range(size):
                entry = matrix[row][column]
                if mask & (1 << column) or entry == 0:
                    continue
                sign = -1 if ((mask >> (column + 1)).bit_count() & 1) else 1
                key = mask | (1 << column)
                next_states[key] = next_states.get(key, ring.zero()) + sign * subtotal * entry
        states = next_states
    return states.get((1 << size) - 1, ring.zero())


def polynomial_sha256(poly):
    import hashlib
    digest = hashlib.sha256()
    for monomial, coefficient in sorted(poly.dict().items()):
        row = ",".join(str(int(x)) for x in monomial) + ":" + str(int(coefficient)) + "\n"
        digest.update(row.encode("ascii"))
    return digest.hexdigest()


def fixture_rows(v4_path, panel_path):
    with open(v4_path, "r") as handle:
        v4 = json.load(handle)["EXP-ICEX-aaccfc"]
    with open(panel_path, "r") as handle:
        panel = json.load(handle)["panel"]
    rows = []
    for fixture in v4:
        item = dict(fixture)
        item["fixture_id"] = "v4-b%d-s%d" % (item["bits"], item["seed"])
        rows.append(item)
    for fixture in panel:
        item = dict(fixture)
        item["fixture_id"] = "panel-b%d-s%d" % (item["bits"], item["seed"])
        rows.append(item)
    return rows


def inventory_polynomial(rows, variable_count, a, b, ring):
    """Specialise the pinned Z[a,b] coefficient inventory exactly in F_p."""
    terms = {}
    for row in rows:
        ea, eb = row[0], row[1]
        exponent = tuple(row[2:2 + variable_count]) + (0,) * (6 - variable_count)
        coefficient = ring.base_ring()(row[-1]) * a ** ea * b ** eb
        terms[exponent] = terms.get(exponent, ring.base_ring().zero()) + coefficient
    return ring(terms)


def load_module(path):
    spec = importlib.util.spec_from_file_location("icex_o5_group", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent O5 group module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sage_tuple(point):
    if point.is_zero():
        return None
    return int(point[0]), int(point[1])


def o5_group_crosscheck(module, p, av, bv):
    """Cross-check the retained independent O5 affine law against Sage."""
    field = GF(p)
    curve = EllipticCurve(field, [field(av), field(bv)])
    points = []
    x = 0
    while len(points) < 6 and x < p:
        candidate = module.canonical_point(p, av, bv, x)
        if candidate is not None:
            # Curve construction also verifies the independent square root.
            sage_point = curve((field(candidate[0]), field(candidate[1])))
            if sage_tuple(sage_point) != candidate:
                return {"pass": False, "cases": 0,
                        "reason": "canonical lift disagrees with Sage", "x": x}
            points.append(candidate)
        x += 1
    if len(points) < 2:
        return {"pass": False, "cases": 0, "reason": "insufficient curve points"}

    cases = [(None, None)]
    for point in points:
        cases.extend(((None, point), (point, None),
                      (point, (point[0], (-point[1]) % p)), (point, point)))
    cases.extend((points[left], points[right])
                 for left in range(len(points)) for right in range(left + 1, len(points)))
    failures = []
    for index, (left, right) in enumerate(cases):
        sage_left = (curve(0) if left is None
                     else curve((field(left[0]), field(left[1]))))
        sage_right = (curve(0) if right is None
                      else curve((field(right[0]), field(right[1]))))
        expected = sage_tuple(sage_left + sage_right)
        observed = module.point_add(left, right, p, av)
        if observed != expected:
            failures.append({"case": index, "left": left, "right": right,
                             "observed": observed, "sage": expected})
    return {"pass": not failures, "cases": len(cases), "points": len(points),
            "failures": failures}


def gate_g02(v4_path, panel_path, inventory_path, o5_group_path):
    started = time.time()
    with open(inventory_path, "r") as handle:
        inventory = json.load(handle)
    o5_module = load_module(o5_group_path)
    evidence = []
    for fixture in fixture_rows(v4_path, panel_path):
        item_started = time.time()
        p, av, bv = int(fixture["p"]), int(fixture["a"]), int(fixture["b"])
        field = GF(p)
        ring = PolynomialRing(field, "x1,x2,x3,x4,x5,z", order="lex")
        x1, x2, x3, x4, x5, z = ring.gens()
        a, b = field(av), field(bv)

        left4 = f3(a, b, x1, x2, z)
        right4 = f3(a, b, x3, x4, z)
        matrix4 = sylvester(fixed_coefficients(left4, 5, 2, ring),
                            fixed_coefficients(right4, 5, 2, ring), ring)
        f4_bareiss = determinant_bareiss(matrix4, ring)
        f4_subset = determinant_subset_dp(matrix4, ring)
        f4_equal = f4_bareiss == f4_subset
        f4_inventory = inventory_polynomial(inventory["S4"], 4, a, b, ring)
        f4_inventory_equal = (f4_bareiss == f4_inventory
                              and f4_subset == f4_inventory)

        left5_bareiss = f4_bareiss.subs({x4: z})
        left5_subset = f4_subset.subs({x4: z})
        right5 = f3(a, b, x4, x5, z)
        right5_coeff = fixed_coefficients(right5, 5, 2, ring)
        f5_bareiss = determinant_bareiss(
            sylvester(fixed_coefficients(left5_bareiss, 5, 4, ring), right5_coeff, ring), ring)
        f5_subset = determinant_subset_dp(
            sylvester(fixed_coefficients(left5_subset, 5, 4, ring), right5_coeff, ring), ring)
        f5_equal = f5_bareiss == f5_subset
        f5_inventory = inventory_polynomial(inventory["S5"], 5, a, b, ring)
        f5_inventory_equal = (f5_bareiss == f5_inventory
                              and f5_subset == f5_inventory)
        group_check = o5_group_crosscheck(o5_module, p, av, bv)
        evidence.append({
            "fixture_id": fixture["fixture_id"], "p": p,
            "f4_equal": bool(f4_equal), "f5_equal": bool(f5_equal),
            "f4_inventory_equal": bool(f4_inventory_equal),
            "f5_inventory_equal": bool(f5_inventory_equal),
            "f4_terms": len(f4_bareiss.dict()), "f5_terms": len(f5_bareiss.dict()),
            "f4_sha256": polynomial_sha256(f4_bareiss),
            "f5_sha256": polynomial_sha256(f5_bareiss),
            "f4_inventory_sha256": polynomial_sha256(f4_inventory),
            "f5_inventory_sha256": polynomial_sha256(f5_inventory),
            "o5_group_sage_crosscheck": group_check,
            "seconds": round(time.time() - item_started, 6),
        })
    return {
        "gate": "G0-2", "pass": (len(evidence) == 26
                                      and all(row["f4_equal"] and row["f5_equal"]
                                              and row["f4_inventory_equal"]
                                              and row["f5_inventory_equal"]
                                              and row["o5_group_sage_crosscheck"]["pass"]
                                              for row in evidence)),
        "fixtures_checked": len(evidence),
        "method_a": "fraction-free Bareiss with exact divisions and first-nonzero row pivots",
        "method_b": "division-free subset-DP determinant expansion",
        "method_c": "exact specialization of pinned semaev_polys.json coefficient inventory",
        "inventory_sha256": hashlib.sha256(open(inventory_path, "rb").read()).hexdigest(),
        "o5_group_sha256": hashlib.sha256(open(o5_group_path, "rb").read()).hexdigest(),
        "o5_group_checked_by": "Sage EllipticCurve group law",
        "full_formal_slots_retained": True, "fixtures": evidence,
        "seconds": round(time.time() - started, 6), "peak_rss_bytes": peak_rss_bytes(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=("G0-2",), required=True)
    parser.add_argument("--v4", required=True)
    parser.add_argument("--panel", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--o5-group", required=True)
    args = parser.parse_args()
    result = gate_g02(args.v4, args.panel, args.inventory, args.o5_group)
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
