"""Independent fixed F27 replay of one checked candidate unit.

The expected form and complete joined software fixture are external inputs.
Production review must bind the expected form to the frozen cohort/T plan.
"""

import argparse
import json
from pathlib import Path

from check_all_degree_collision_certificate import validate_row, root_degree, projective_kernel
from check_compact_class_inputs import BasisField
from check_join_certificate import verify_shards
from check_rational_collision_certificate import projective_image
from check_structure_certificate import cocycle, transform
from generic_disjoint import classify, exceptional_geometry


def verify(unit, joined, expected_form):
    if unit.get("schema") != "pext.checked-candidate-unit/v1" or unit.get("structure_order") != "left-pgl2-fq/v1":
        raise ValueError("candidate unit schema or order")
    verify_shards([joined], "f27-char3")
    field = BasisField(joined["field"])
    if unit.get("field") != joined["field"] or (field.p, field.n, field.size) != (3, 3, 27):
        raise ValueError("candidate field identity")
    if unit.get("form") != expected_form:
        raise ValueError("candidate expected form")
    if unit.get("structures") != 819 or unit.get("cocycle_entries") != [819] or unit.get("rational_image_entries") != 3276:
        raise ValueError("candidate index coverage")
    factor_row = {"form": unit["form"], "pattern": unit["factor_pattern"],
                  "infinity": unit["infinity"], "factors": unit["factors"],
                  "extension_modulus": unit["extension_modulus"], "roots": unit["roots"]}
    extension, roots = validate_row(field, factor_row, expected_form, unit["factor_pattern"])
    degrees = [root_degree(extension, root) for root in roots]
    rational_roots = [root[0] for root, degree in zip(roots, degrees) if degree == 1]
    if unit["infinity"]:
        rational_roots.append(field.size)
    matrices = [joined["rows"][ordinal]["matrix"] for ordinal in range(819)]
    cocycle_index = {tuple(cocycle(field, matrix)): ordinal for ordinal, matrix in enumerate(matrices)}
    if len(cocycle_index) != 819:
        raise ValueError("duplicate cocycle")
    rational, nonrational = set(), set()
    for ordinal, matrix in enumerate(matrices):
        image = [projective_image(field, matrix, root) for root in rational_roots]
        conjugate = {field.size if point == field.size else field.power(point, field.p)
                     for point in image}
        if any(point in conjugate for point in image):
            rational.add(ordinal)
    if extension.degree > 1:
        for alpha, alpha_degree in zip(roots, degrees):
            if alpha_degree == 1:
                continue
            for gamma, gamma_degree in zip(roots, degrees):
                if gamma_degree != alpha_degree:
                    continue
                beta = extension.power(gamma, field.p)
                for matrix in projective_kernel(field, extension, alpha, beta):
                    ordinal = cocycle_index.get(matrix)
                    if ordinal is not None:
                        nonrational.add(ordinal)
    expected = sorted(rational | nonrational)
    rows = unit.get("rows")
    if not isinstance(rows, list) or len(rows) != len(expected) or unit.get("exceptional") != len(expected):
        raise ValueError("candidate row cardinality")
    if [row[0] for row in rows if isinstance(row, list) and len(row) == 5] != expected:
        raise ValueError("candidate ordinal set mismatch")
    if unit.get("rational_count") != len(rational) or unit.get("nonrational_count") != len(nonrational):
        raise ValueError("candidate root-degree counts")
    if unit.get("duplicate_count") != len(rational & nonrational):
        raise ValueError("candidate overlap count")
    intervals = []
    cursor = 0
    for ordinal in expected:
        if cursor < ordinal:
            intervals.append([cursor, ordinal])
        cursor = ordinal+1
    if cursor < 819:
        intervals.append([cursor, 819])
    if unit.get("generic_intervals") != intervals or unit.get("generic") != 819-len(expected):
        raise ValueError("generic complement coverage")
    direct = set()
    for ordinal, matrix in enumerate(matrices):
        moved = transform(field, expected_form, matrix)
        orbit = [moved]
        for _ in range(1, field.n):
            orbit.append([field.power(value, field.p) for value in orbit[-1]])
        if classify(field, orbit)["classification"] == "exceptional":
            direct.add(ordinal)
    if direct != set(expected):
        raise ValueError("literal support candidate completeness")
    for row in rows:
        ordinal, matrix, rank, branches, genus = row
        if matrix != matrices[ordinal]:
            raise ValueError("candidate matrix ordinal mismatch")
        moved = transform(field, expected_form, matrix)
        orbit = [moved]
        for _ in range(1, field.n):
            orbit.append([field.power(value, field.p) for value in orbit[-1]])
        geometry = exceptional_geometry(field, orbit)
        if (rank, branches, genus) != (geometry["geometric_squareclass_rank"],
                                      geometry["branch_points"], geometry["geometric_genus"]):
            raise ValueError("candidate geometry mismatch")
    return {"valid": True, "fixture": "f27-char3", "form": expected_form,
            "structures": 819, "rational": len(rational), "nonrational": len(nonrational),
            "overlap": len(rational & nonrational), "exceptional": len(expected),
            "generic_intervals": len(intervals)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit", type=Path)
    parser.add_argument("joined", type=Path)
    parser.add_argument("--expected-form", required=True,
                        help="five comma-separated polynomial-basis coefficients from the bound T plan")
    args = parser.parse_args()
    try:
        form = [int(value) for value in args.expected_form.split(",")]
        print(json.dumps(verify(json.loads(args.unit.read_bytes()),
                                json.loads(args.joined.read_bytes()), form), sort_keys=True))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
