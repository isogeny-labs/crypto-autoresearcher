"""Independent polynomial-basis replay of fixed F27 all-degree collisions.

Rebuilds branch factors, common-extension roots, K-linear projective kernels,
cocycle norm/Lang witnesses and literal support-gcd sets. Software fixture only.
"""

import argparse
from itertools import permutations
import json
from pathlib import Path

from check_compact_class_inputs import BasisField
from check_join_certificate import verify_shards
from check_quotient_certificate import polynomial_mul, polynomial_remainder, trim
from check_structure_certificate import cocycle, multiply, normalize, transform
from generic_disjoint import classify, support_gcd
from check_rational_collision_certificate import projective_image

PATTERNS = [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2], [4]]
FIXED_FORMS = [[0, 3, 2, 6, 1], [0, 2, 1, 2, 1], [0, 9, 2, 0, 1],
               [6, 0, 7, 0, 1], [2, 1, 0, 0, 1]]
LABELS = ["split-1111", "split-112", "split-13", "split-22",
          "irreducible-4", "actual-0", "actual-1"]


def difference(field, left, right):
    return trim([field.sub(left[i] if i < len(left) else 0,
                           right[i] if i < len(right) else 0)
                 for i in range(max(len(left), len(right)))])


def polynomial_power(field, base, exponent, modulus):
    result = [1]
    while exponent:
        if exponent & 1:
            result = polynomial_remainder(field, polynomial_mul(field, result, base), modulus)
        exponent >>= 1
        if exponent:
            base = polynomial_remainder(field, polynomial_mul(field, base, base), modulus)
    return trim(result)


def irreducible(field, factor):
    degree = len(factor)-1
    if degree == 1:
        return True
    if degree not in (2, 3, 4) or factor[-1] != 1:
        return False
    x = [0, 1]
    if polynomial_power(field, x, field.size**degree, factor) != x:
        return False
    proper = polynomial_power(field, x, field.size**(2 if degree == 4 else 1), factor)
    return len(support_gcd(field, factor, difference(field, proper, x))) == 1


class Extension:
    def __init__(self, field, modulus):
        self.field = field
        self.modulus = modulus
        self.degree = len(modulus)-1 if modulus is not None else 1

    def add(self, left, right):
        return tuple(self.field.add(a, b) for a, b in zip(left, right))

    def sub(self, left, right):
        return tuple(self.field.sub(a, b) for a, b in zip(left, right))

    def mul(self, left, right):
        field, degree = self.field, self.degree
        if degree == 1:
            return (field.mul(left[0], right[0]),)
        product = [0] * (2*degree-1)
        for i, a in enumerate(left):
            for j, b in enumerate(right):
                product[i+j] = field.add(product[i+j], field.mul(a, b))
        for i in range(len(product)-1, degree-1, -1):
            scale = product[i]
            for j in range(degree):
                product[i-degree+j] = field.sub(product[i-degree+j],
                                                field.mul(scale, self.modulus[j]))
        return tuple(product[:degree])

    def constant(self, value):
        return (value,) + (0,) * (self.degree-1)

    def power(self, base, exponent):
        result = self.constant(1)
        while exponent:
            if exponent & 1:
                result = self.mul(result, base)
            exponent >>= 1
            if exponent:
                base = self.mul(base, base)
        return result

    def evaluate(self, coefficients, root):
        result = self.constant(0)
        for coefficient in reversed(coefficients):
            result = self.add(self.mul(result, root), self.constant(coefficient))
        return result


def root_degree(extension, root):
    value = root
    for degree in range(1, extension.degree+1):
        value = extension.power(value, extension.field.size)
        if value == root:
            return degree
    raise ValueError("branch root orbit closure")


def cross_ratio_orbit(extension, roots):
    """All anharmonic values of four distinct finite branch roots."""
    if len(roots) != 4 or len(set(roots)) != 4:
        raise ValueError("cross-ratio requires four distinct finite roots")
    values = set()
    one = extension.constant(1)
    for a, b, c, d in permutations(roots):
        numerator = extension.mul(extension.sub(a, c), extension.sub(b, d))
        denominator = extension.mul(extension.sub(a, d), extension.sub(b, c))
        if denominator == extension.constant(0):
            raise ValueError("cross-ratio denominator zero")
        inverse = extension.power(denominator,
                                  extension.field.size**extension.degree - 2)
        if extension.mul(denominator, inverse) != one:
            raise ValueError("cross-ratio inverse invalid")
        value = extension.mul(numerator, inverse)
        if value in (extension.constant(0), one):
            raise ValueError("degenerate cross-ratio")
        values.add(value)
    if not 1 <= len(values) <= 6:
        raise ValueError("cross-ratio anharmonic orbit size")
    return [list(value) for value in sorted(values)]


def projective_kernel(field, extension, alpha, beta):
    product = extension.mul(alpha, beta)
    columns = [beta, extension.constant(1),
               tuple(field.sub(0, v) for v in product),
               tuple(field.sub(0, v) for v in alpha)]
    rows = [[columns[column][row] for column in range(4)]
            for row in range(extension.degree)]
    pivots = []
    for column in range(4):
        pivot = next((row for row in range(len(pivots), len(rows))
                      if rows[row][column]), None)
        if pivot is None:
            continue
        rows[len(pivots)], rows[pivot] = rows[pivot], rows[len(pivots)]
        lead = field.div(1, rows[len(pivots)][column])
        rows[len(pivots)] = [field.mul(lead, value) for value in rows[len(pivots)]]
        for row in range(len(rows)):
            if row != len(pivots):
                scale = rows[row][column]
                rows[row] = [field.sub(value, field.mul(scale, rows[len(pivots)][j]))
                             for j, value in enumerate(rows[row])]
        pivots.append(column)
    free = [column for column in range(4) if column not in pivots]
    if len(free) > 2:
        raise ValueError("unexpected root kernel dimension")
    if len(free) == 1:
        assignments = [(1,)]
    elif len(free) == 2:
        assignments = [(1, value) for value in range(field.size)] + [(0, 1)]
    else:
        assignments = []
    maps = set()
    for assignment in assignments:
        vector = [0] * 4
        for column, value in zip(free, assignment):
            vector[column] = value
        for row, column in enumerate(pivots):
            vector[column] = field.sub(0, sum_field(field,
                [field.mul(rows[row][j], vector[j]) for j in free]))
        if field.mul(vector[0], vector[3]) == field.mul(vector[1], vector[2]):
            continue
        first = next(value for value in vector if value)
        vector = tuple(field.div(value, first) for value in vector)
        maps.add(vector)
    return maps


def sum_field(field, values):
    result = 0
    for value in values:
        result = field.add(result, value)
    return result


def validate_row(field, row, expected_form, expected_pattern):
    if row.get("form") != expected_form or row.get("pattern") != expected_pattern:
        raise ValueError("fixed form or factor-pattern mismatch")
    form = row["form"]
    if not isinstance(form, list) or len(form) != 5 or any(type(v) is not int or not 0 <= v < field.size for v in form):
        raise ValueError("form encoding")
    finite = trim(form)
    if len(finite) not in (4, 5) or finite[-1] != 1:
        raise ValueError("finite quartic normalization")
    if row.get("infinity") is not (len(finite) == 4):
        raise ValueError("infinity flag")
    factors = row.get("factors")
    if not isinstance(factors, list) or not factors:
        raise ValueError("factor list")
    product = [1]
    for factor in factors:
        if not isinstance(factor, list) or not 2 <= len(factor) <= 5 or any(type(v) is not int or not 0 <= v < field.size for v in factor):
            raise ValueError("factor encoding")
        if not irreducible(field, factor):
            raise ValueError("reducible or nonmonic factor")
        product = polynomial_mul(field, product, factor)
    if product != finite or sorted([len(factor)-1 for factor in factors] +
                                   ([1] if row["infinity"] else [])) != expected_pattern:
        raise ValueError("branch factor product or degree pattern")
    modulus = row.get("extension_modulus")
    high = [factor for factor in factors if len(factor) > 2]
    if (modulus is None) != (not high) or (high and modulus not in high):
        raise ValueError("common extension modulus")
    extension = Extension(field, modulus)
    roots = row.get("roots")
    if not isinstance(roots, list) or len(roots) != 4-int(row["infinity"]):
        raise ValueError("root count")
    roots = [tuple(root) for root in roots]
    if any(len(root) != extension.degree or any(type(v) is not int or not 0 <= v < field.size for v in root)
           for root in roots) or len(set(roots)) != len(roots):
        raise ValueError("root basis or distinctness")
    if any(extension.evaluate(form, root) != extension.constant(0) for root in roots):
        raise ValueError("root off quartic")
    for factor in factors:
        members = {root for root in roots if extension.evaluate(factor, root) == extension.constant(0)}
        if len(members) != len(factor)-1 or any(extension.power(root, field.size) not in members
                                              for root in members):
            raise ValueError("incomplete factor root orbit")
    return extension, roots


def verify(certificate, joined):
    if certificate.get("schema") != "pext.all-degree-collision-software/v1" or certificate.get("fixture") != "f27-char3":
        raise ValueError("all-degree certificate identity")
    verify_shards([joined], "f27-char3")
    field = BasisField(joined["field"])
    if (field.p, field.n, field.size) != (3, 3, 27) or certificate.get("structures") != 819:
        raise ValueError("fixed field or structure count")
    if certificate.get("cocycle_entries") != 819 or certificate.get("rational_image_entries") != 3276:
        raise ValueError("index coverage")
    rows = certificate.get("rows")
    if not isinstance(rows, list) or len(rows) != 7 or [row.get("label") for row in rows] != LABELS:
        raise ValueError("seven fixed factor-pattern rows")
    matrices = [joined["rows"][i]["matrix"] for i in range(819)]
    cocycle_index = {}
    for ordinal, matrix in enumerate(matrices):
        value = tuple(cocycle(field, matrix))
        if value in cocycle_index:
            raise ValueError("duplicate projective cocycle")
        cocycle_index[value] = ordinal
        product, current = [1, 0, 0, 1], list(value)
        for _ in range(field.n):
            product = multiply(field, product, current)
            current = [field.power(v, field.p) for v in current]
        if normalize(field, product) != [1, 0, 0, 1]:
            raise ValueError("cocycle norm witness")
    if len(cocycle_index) != 819:
        raise ValueError("incomplete cocycle index")
    outcomes = []
    for index, row in enumerate(rows):
        form = (FIXED_FORMS[index] if index < 5 else
                joined["rows"][(index-5)*819]["original_form"])
        pattern = PATTERNS[index] if index < 5 else row.get("pattern")
        extension, roots = validate_row(field, row, form, pattern)
        if index < 5 and row.get("cross_ratio_orbit") != cross_ratio_orbit(extension, roots):
            raise ValueError("fixed cross-ratio orbit certificate mismatch")
        if index >= 5 and row["form"] != joined["rows"][(index-5)*819]["original_form"]:
            raise ValueError("actual quotient form")
        degrees = [root_degree(extension, root) for root in roots]
        rational_roots = [root[0] for root, degree in zip(roots, degrees) if degree == 1]
        if row["infinity"]:
            rational_roots.append(field.size)
        rational = set()
        nonrational = set()
        direct = set()
        for ordinal, matrix in enumerate(matrices):
            image = [projective_image(field, matrix, root) for root in rational_roots]
            conjugate = {field.size if point == field.size else field.power(point, field.p)
                         for point in image}
            if any(point in conjugate for point in image):
                rational.add(ordinal)
            moved = transform(field, form, matrix)
            orbit = [moved]
            for _ in range(1, field.n):
                orbit.append([field.power(value, field.p) for value in orbit[-1]])
            if classify(field, orbit)["classification"] == "exceptional":
                direct.add(ordinal)
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
                            # The joined N matrix is the explicit Lang witness.
                            if tuple(cocycle(field, matrices[ordinal])) != matrix:
                                raise ValueError("Lang witness mismatch")
                            nonrational.add(ordinal)
        def checked(name, expected):
            supplied = row.get(name)
            if (not isinstance(supplied, list) or any(type(v) is not int or not 0 <= v < 819 for v in supplied)
                    or supplied != sorted(set(supplied)) or supplied != sorted(expected)):
                raise ValueError(name + " candidate set mismatch")
        checked("rational_indices", rational)
        checked("nonrational_indices", nonrational)
        checked("union_indices", rational | nonrational)
        if rational | nonrational != direct:
            raise ValueError("all-degree candidate completeness mismatch")
        outcomes.append({"label": row["label"], "pattern": pattern,
                         "rational": len(rational), "nonrational": len(nonrational),
                         "overlap": len(rational & nonrational), "exceptional": len(direct)})
    return {"valid": True, "fixture": "f27-char3", "structures": 819, "targets": outcomes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("joined", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(json.loads(args.certificate.read_bytes()),
                                json.loads(args.joined.read_bytes())), sort_keys=True))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
