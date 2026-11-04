"""Independent left-coset coverage and literal scalar-preserving form replay.

Coverage uses distinct cocycles N^-1 sigma(N) and the exact group index.
It certifies projective structures, not curve cohort coverage or descent.
"""
import argparse
import json
from pathlib import Path
from check_quotient_certificate import Field, integer, keys, load, require, polynomial_mul


def normalize(f, matrix):
    require(type(matrix) is list and len(matrix) == 4, "matrix shape")
    a, b, c, d = [f.element(v) for v in matrix]
    require(f.mul(a, d) != f.mul(b, c), "singular matrix")
    first = next(v for v in matrix if v)
    return [f.div(v, first) for v in matrix]


def multiply(f, a, b):
    return [f.add(f.mul(a[0], b[0]), f.mul(a[1], b[2])),
            f.add(f.mul(a[0], b[1]), f.mul(a[1], b[3])),
            f.add(f.mul(a[2], b[0]), f.mul(a[3], b[2])),
            f.add(f.mul(a[2], b[1]), f.mul(a[3], b[3]))]


def inverse(f, m):
    return [m[3], f.sub(0, m[1]), f.sub(0, m[2]), m[0]]


def cocycle(f, m):
    return normalize(f, multiply(f, inverse(f, m), [f.power(v, f.p) for v in m]))


def transform(f, form, matrix):
    """Independent homogeneous expansion, with all leading scalars retained."""
    a, b, c, d = matrix
    linear = [[f.sub(0, b), d], [a, f.sub(0, c)]]
    out = [0]*5
    for i, coefficient in enumerate(form):
        term = [coefficient]
        for factor in [linear[0]]*i+[linear[1]]*(4-i):
            term = polynomial_mul(f, term, factor)
        for j, value in enumerate(term):
            out[j] = f.add(out[j], value)
    return out


def verify(record, expected, field_limit=100000, structure_limit=100000):
    keys(record, "schema field forms count structures")
    require(record["schema"] == "pext.structure-certificate/v1", "structure schema")
    keys(expected, "field forms")
    keys(expected["field"], "prime degree modulus")
    f = Field(record["field"], field_limit)
    require(f.n in (1, 3, 5, 7), "unsupported transversal degree")
    integer(expected["field"]["prime"], 3, 13)
    integer(expected["field"]["degree"], 1, 7)
    require(type(expected["field"]["modulus"]) is list, "expected modulus")
    for value in expected["field"]["modulus"]:
        integer(value, 0, f.p-1)
    require(expected["field"] == {k: record["field"][k] for k in expected["field"]}, "expected field mismatch")
    require(type(expected["forms"]) is list and 1 <= len(expected["forms"]) <= 7, "expected form count")
    for form in expected["forms"]:
        require(type(form) is list and len(form) == 5, "expected form shape")
        for value in form:
            f.element(value)
        require(any(form), "zero expected form")
    require(type(record["forms"]) is list and record["forms"] == expected["forms"], "expected forms mismatch")
    for form in record["forms"]:
        for value in form:
            f.element(value)
    count = (f.size**3-f.size)//(f.p**3-f.p)
    require(count <= structure_limit, "structure limit exceeded")
    require(integer(record["count"], 1, structure_limit) == count, "group index mismatch")
    rows = record["structures"]
    require(type(rows) is list and len(rows) == count, "structure row count")
    seen = set()
    for row in rows:
        keys(row, "matrix cocycle transformed_forms")
        matrix = normalize(f, row["matrix"])
        require(matrix == row["matrix"], "noncanonical matrix")
        actual = cocycle(f, matrix)
        supplied = normalize(f, row["cocycle"])
        require(actual == supplied == row["cocycle"], "cocycle mismatch")
        identity = tuple(actual)
        require(identity not in seen, "duplicate left coset")
        seen.add(identity)
        product, current = [1, 0, 0, 1], actual
        for _ in range(f.n):
            product = multiply(f, product, current)
            current = [f.power(v, f.p) for v in current]
        require(normalize(f, product) == [1, 0, 0, 1], "cocycle norm failure")
        transformed = row["transformed_forms"]
        require(type(transformed) is list and len(transformed) == len(expected["forms"]), "transformed form count")
        for original, given in zip(expected["forms"], transformed):
            require(type(given) is list and len(given) == 5, "transformed form shape")
            for value in given:
                f.element(value)
            require(given == transform(f, original, matrix), "literal transform mismatch")
    return {"valid": True, "structures": count,
            "scope": "complete left projective cosets and supplied binary-form transforms; no curve cohort or descent certificate"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--expected-input", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(load(args.certificate), load(args.expected_input)), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
