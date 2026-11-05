"""Exact multiplication of fixed radical vectors over k(x).

Every product is computed in the checked K(x) radical algebra, decomposed in
the Frobenius-fixed basis, and reconstructed exactly. Norm rationalization
proves each structure coefficient belongs to the base rational-function field.
"""

import json

from check_quotient_certificate import polynomial_mul, trim
from fixed_invariant_basis import (_add_vectors, _apply, _equal_vectors,
                                   add_fractions, build as build_basis)
from generic_disjoint import exact_quotient, support_gcd
from radical_algebra_model import (equal_fractions, fraction,
                                   frobenius_fraction, multiply_fractions,
                                   build_from_source as build_source_algebra)
from target_transport import verified_field


def _normalize(field, value):
    numerator, denominator = trim(value["numerator"]), trim(value["denominator"])
    if not numerator:
        return fraction(field, [], [1])
    common = support_gcd(field, numerator, denominator)
    numerator = list(exact_quotient(field, numerator, common))
    denominator = list(exact_quotient(field, denominator, common))
    scale = field.div(1, denominator[-1])
    return fraction(field, [field.mul(scale, c) for c in numerator],
                    [field.mul(scale, c) for c in denominator])


def _mul(field, left, right):
    return _normalize(field, multiply_fractions(field, left, right))


def _add(field, left, right):
    return _normalize(field, add_fractions(field, left, right))


def _div(field, left, right):
    if not trim(right["numerator"]):
        raise ValueError("zero fixed-basis coefficient")
    return _mul(field, left, fraction(field, right["denominator"],
                                      right["numerator"]))


def _zero(field):
    return fraction(field, [], [1])


def _rationalize(field, value):
    """Expand a K(x) scalar in the polynomial K/k basis over k(x)."""
    value = _normalize(field, value)
    denominator = value["denominator"]
    conjugate = denominator
    complement = [1]
    for _ in range(1, field.n):
        conjugate = [field.power(c, field.p) for c in conjugate]
        complement = polynomial_mul(field, complement, conjugate)
    numerator = polynomial_mul(field, value["numerator"], complement)
    norm = polynomial_mul(field, denominator, complement)
    if any(c >= field.p for c in norm):
        raise ValueError("rationalized denominator is not over base field")
    coordinates = []
    for index in range(field.n):
        digits = trim([(c // field.p**index) % field.p for c in numerator])
        coordinates.append(fraction(field, digits, norm))
    reconstructed = _zero(field)
    for index, coordinate in enumerate(coordinates):
        scalar = fraction(field, [field.p**index], [1])
        reconstructed = _add(field, reconstructed, _mul(field, scalar, coordinate))
    if not equal_fractions(field, reconstructed, value):
        raise ValueError("K/k rational coordinate reconstruction mismatch")
    return coordinates


def _vector(record):
    return {row["mask"]: row["factor"] for row in record["coefficients"]}


def _product(field, left, right, algebra):
    masks = algebra["basis_masks"]
    indices = {mask: index for index, mask in enumerate(masks)}
    table = algebra["multiplication"]
    result = {}
    for left_mask, left_factor in left.items():
        for right_mask, right_factor in right.items():
            entry = table[indices[left_mask]][indices[right_mask]]
            value = _mul(field, _mul(field, left_factor, right_factor), entry["factor"])
            target = entry["target"]
            result[target] = _add(field, result.get(target, _zero(field)), value)
    return {mask: value for mask, value in result.items() if trim(value["numerator"])}


def _coordinates(field, value, basis):
    vectors = [_vector(row) for row in basis["vectors"]]
    orbits = basis["orbits"]
    slots = {}
    for index, row in enumerate(basis["vectors"]):
        slots.setdefault(row["orbit_start"], index)
    coefficients = [_zero(field) for _ in vectors]
    for orbit in orbits:
        start = orbit[0]
        scalar = value.get(start, _zero(field))
        if len(orbit) == field.n:
            expanded = _rationalize(field, scalar)
            first = slots[start]
            if [row["seed_basis_index"] for row in basis["vectors"][first:first+field.n]] != list(range(field.n)):
                raise ValueError("fixed orbit polynomial-basis vector order")
            coefficients[first:first+field.n] = expanded
        else:
            first = slots[start]
            generator = vectors[first][start]
            expanded = _rationalize(field, _div(field, scalar, generator))
            if any(trim(item["numerator"]) for item in expanded[1:]):
                raise ValueError("fixed orbit coefficient is not in base field")
            coefficients[first] = expanded[0]
    reconstructed = {}
    for coefficient, vector in zip(coefficients, vectors):
        if not trim(coefficient["numerator"]):
            continue
        scaled = {mask: _mul(field, coefficient, factor)
                  for mask, factor in vector.items()}
        reconstructed = _add_vectors(field, reconstructed, scaled)
    if not _equal_vectors(field, reconstructed, value):
        raise ValueError("fixed-vector product reconstruction mismatch")
    return coefficients


def build(field, forms):
    """Return multiplication and unit over k(x) in a checked invariant basis."""
    basis = build_basis(field, forms)
    algebra = basis["algebra"]
    vectors = [_vector(row) for row in basis["vectors"]]
    action = {row["from"]: row for row in algebra["frobenius_action"]}
    products = []
    for left in vectors:
        row = []
        for right in vectors:
            product = _product(field, left, right, algebra)
            if not _equal_vectors(field, _apply(field, product, action), product):
                raise ValueError("fixed-vector product is not Frobenius fixed")
            coordinates = _coordinates(field, product, basis)
            row.append([{"index": index, "factor": factor}
                        for index, factor in enumerate(coordinates)
                        if trim(factor["numerator"])])
        products.append(row)
    unit = _coordinates(field, {0: fraction(field, [1], [1])}, basis)
    one, zero = fraction(field, [1], [1]), _zero(field)
    for right_index in range(len(vectors)):
        result = [zero for _ in vectors]
        for unit_index, unit_factor in enumerate(unit):
            if not trim(unit_factor["numerator"]):
                continue
            for term in products[unit_index][right_index]:
                index = term["index"]
                result[index] = _add(field, result[index],
                                     _mul(field, unit_factor, term["factor"]))
        if any(not equal_fractions(field, value, one if index == right_index else zero)
               for index, value in enumerate(result)):
            raise ValueError("fixed-field multiplication unit identity mismatch")
    return {"schema": "pext.fixed-field-multiplication/v1", "degree": field.n,
            "basis": basis, "multiplication": products,
            "unit": [{"index": index, "factor": factor}
                     for index, factor in enumerate(unit) if trim(factor["numerator"])],
            "dimension": len(vectors),
            "status": "fixed_field_multiplication_checked; independent_descent_review_pending"}


def build_from_source(field_record, model, target, matrix, forms):
    """Bind the exact fixed algebra to a named elliptic source model and T."""
    source = build_source_algebra(field_record, model, target, matrix, forms)
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(",", ":")))
    fixed = build(field, forms)
    if fixed["basis"]["algebra"]["generator_signs"] != source["algebra"]["generator_signs"]:
        raise ValueError("source and fixed algebra action differ")
    return {"schema": "pext.source-fixed-field-model/v1", "source": source,
            "fixed": fixed,
            "status": "source_fixed_field_multiplication_checked; independent_geometry_review_pending"}
