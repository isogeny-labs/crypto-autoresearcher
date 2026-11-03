"""Independent polynomial-basis replay of the fixed F27 rational-root set."""

import argparse
import json
from pathlib import Path

from check_compact_class_inputs import BasisField
from check_quotient_certificate import polynomial_value


def projective_image(field, matrix, point):
    a, b, c, d = matrix
    if point == field.size:
        return field.size if c == 0 else field.div(a, c)
    numerator = field.add(field.mul(a, point), b)
    denominator = field.add(field.mul(c, point), d)
    return field.size if denominator == 0 else field.div(numerator, denominator)


def rational_roots(field, form):
    roots = [x for x in range(field.size) if polynomial_value(field, form, x) == 0]
    if form[4] == 0:
        roots.append(field.size)
    return roots


def verify(certificate, joined):
    if certificate.get("schema") != "pext.rational-collision-software/v1":
        raise ValueError("rational collision schema")
    if certificate.get("fixture") != joined.get("fixture") or joined.get("fixture") != "f27-char3":
        raise ValueError("fixed fixture identity")
    field = BasisField(joined["field"])
    if (field.p, field.n, field.size) != (3, 3, 27):
        raise ValueError("field identity")
    if joined["total"] != 1638 or joined["start"] != 0 or joined["end"] != 1638:
        raise ValueError("join is not the complete fixed fixture")
    if len(joined.get("rows", [])) != 1638 or any(row.get("class_index") != 0 for row in joined["rows"]):
        raise ValueError("joined row cardinality or class")
    if certificate.get("structures") != joined["structures"] or joined["structures"] != 819:
        raise ValueError("structure count")
    if certificate.get("cocycle_entries") != 819 or certificate.get("rational_image_entries") != 3276:
        raise ValueError("index coverage")
    rows = certificate.get("rows")
    if not isinstance(rows, list) or len(joined["classes"]) != 1 or len(rows) != len(joined["classes"][0]["targets"]) or len(rows) != 2:
        raise ValueError("target count")
    results = []
    for coset_index, candidate in enumerate(rows):
        if candidate.get("coset_index") != coset_index:
            raise ValueError("target order")
        group = [row for row in joined["rows"] if row["coset_index"] == coset_index]
        if len(group) != 819 or sorted(row["structure_index"] for row in group) != list(range(819)):
            raise ValueError("joined structure coverage")
        form = group[0]["original_form"]
        if candidate.get("form") != form:
            raise ValueError("literal quotient form")
        roots = rational_roots(field, form)
        if candidate.get("rational_roots") != roots:
            raise ValueError("rational branch roots")
        direct = []
        for row in group:
            if row["original_form"] != form:
                raise ValueError("inconsistent target form")
            matrix = row["matrix"]
            if field.mul(matrix[0], matrix[3]) == field.mul(matrix[1], matrix[2]):
                raise ValueError("singular structure matrix")
            image = [projective_image(field, matrix, root) for root in roots]
            frobenius = {field.size if point == field.size else field.power(point, field.p)
                         for point in image}
            if any(point in frobenius for point in image):
                direct.append(row["structure_index"])
        supplied = candidate.get("structure_indices")
        if (not isinstance(supplied, list)
                or any(type(value) is not int or value < 0 or value >= 819 for value in supplied)
                or supplied != sorted(set(supplied)) or supplied != direct):
            raise ValueError("rational collision candidate set mismatch")
        results.append({"coset_index": coset_index, "rational_roots": len(roots),
                        "candidate_indices": len(direct)})
    return {"valid": True, "fixture": "f27-char3", "structures_per_T": 819,
            "targets": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("joined", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(json.loads(args.certificate.read_bytes()),
                                json.loads(args.joined.read_bytes())), sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
