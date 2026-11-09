"""Independent replay of a serialized PEXT fixed radical algebra.

This checker imports only the older quotient certificate's finite-field and
polynomial arithmetic. It reconstructs the radical quotient and its coherent
relation witnesses, then checks every fixed vector, product and unit after
extension from k(x) to K(x). External field/forms are required inputs.
"""

import argparse
import json
from pathlib import Path

from check_quotient_certificate import (Field, Curve, polynomial_mul,
                                        polynomial_remainder, square_relations,
                                        trim)
from independent_source_map_check import verify as verify_source_map


def need(condition, message):
    if not condition:
        raise ValueError(message)


def _poly_add(f, a, b):
    return trim([f.add(a[i] if i < len(a) else 0,
                       b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def _poly_quotient(f, dividend, divisor):
    dividend, divisor = trim(dividend), trim(divisor)
    need(bool(divisor), "zero polynomial divisor")
    quotient = [0] * max(0, len(dividend) - len(divisor) + 1)
    while len(dividend) >= len(divisor):
        offset = len(dividend) - len(divisor)
        scale = f.div(dividend[-1], divisor[-1])
        quotient[offset] = scale
        for i, value in enumerate(divisor):
            dividend[offset+i] = f.sub(dividend[offset+i], f.mul(scale, value))
        dividend = trim(dividend)
    need(not dividend, "nonexact polynomial quotient")
    return trim(quotient)


def _gcd(f, left, right):
    left, right = trim(left), trim(right)
    while right:
        left, right = right, polynomial_remainder(f, left, right)
    need(bool(left), "zero polynomial gcd")
    inverse = f.div(1, left[-1])
    return trim([f.mul(inverse, c) for c in left])


def _fraction(f, numerator, denominator):
    numerator, denominator = trim(numerator), trim(denominator)
    need(bool(denominator), "zero rational denominator")
    if not numerator:
        return ((), (1,))
    common = _gcd(f, numerator, denominator)
    numerator = _poly_quotient(f, numerator, common)
    denominator = _poly_quotient(f, denominator, common)
    inverse = f.div(1, denominator[-1])
    return (tuple(f.mul(inverse, c) for c in numerator),
            tuple(f.mul(inverse, c) for c in denominator))


def _read_fraction(f, value, base=False):
    need(type(value) is dict and set(value) == {"numerator", "denominator"},
         "rational factor shape")
    numerator, denominator = value["numerator"], value["denominator"]
    need(type(numerator) is list and type(denominator) is list,
         "rational polynomial shape")
    for coefficient in numerator + denominator:
        f.element(coefficient)
        if base:
            need(coefficient < f.p, "fixed coefficient outside base field")
    return _fraction(f, numerator, denominator)


def _mul(f, a, b):
    return _fraction(f, polynomial_mul(f, a[0], b[0]),
                     polynomial_mul(f, a[1], b[1]))


def _add(f, a, b):
    return _fraction(f, _poly_add(f, polynomial_mul(f, a[0], b[1]),
                                   polynomial_mul(f, b[0], a[1])),
                     polynomial_mul(f, a[1], b[1]))


def _frobenius(f, a):
    return _fraction(f, [f.power(c, f.p) for c in a[0]],
                     [f.power(c, f.p) for c in a[1]])


def _mask_product(f, forms, mask):
    product = [1]
    for index, form in enumerate(forms):
        if mask & (1 << index):
            product = polynomial_mul(f, product, trim(form))
    return product


def _sqrt(f, polynomial):
    polynomial = trim(polynomial)
    coefficient = polynomial[-1]
    scalar = next((c for c in range(f.size) if f.mul(c, c) == coefficient), None)
    need(scalar is not None and (len(polynomial)-1) % 2 == 0,
         "arithmetic relation lacks polynomial square root")
    monic = [f.div(c, coefficient) for c in polynomial]
    degree = (len(monic)-1)//2
    root = [0]*degree+[1]
    for index in range(degree-1, -1, -1):
        known = 0
        for left in range(index+1, degree+1):
            right = degree+index-left
            if index < right <= degree:
                known = f.add(known, f.mul(root[left], root[right]))
        root[index] = f.div(f.sub(monic[degree+index], known), 2)
    result = [f.mul(scalar, c) for c in root]
    need(polynomial_mul(f, result, result) == polynomial,
         "relation polynomial square root mismatch")
    return result


def _ambient(f, forms, algebra):
    n = len(forms)
    relations = square_relations(f, forms)
    arithmetic = {mask for mask, is_square in relations if is_square}
    pivots, relation_basis = {}, []
    for mask in sorted(arithmetic):
        residual = mask
        for pivot in sorted(pivots, reverse=True):
            if residual & (1 << pivot):
                residual ^= pivots[pivot]
        if residual:
            pivots[residual.bit_length()-1] = residual
            relation_basis.append(mask)
    roots = {mask: _sqrt(f, _mask_product(f, forms, mask))
             for mask in relation_basis}
    witnesses = {0: [1]}
    for mask in sorted(arithmetic - {0}):
        chosen = next((subset for subset in range(1 << len(relation_basis))
                       if mask == _xor([relation_basis[i] for i in range(len(relation_basis))
                                        if subset & (1 << i)])), None)
        need(chosen is not None, "relation basis incomplete")
        current, witness = 0, [1]
        for index, basis_mask in enumerate(relation_basis):
            if chosen & (1 << index):
                numerator = polynomial_mul(f, witness, roots[basis_mask])
                witness = _poly_quotient(f, numerator,
                                         _mask_product(f, forms, current & basis_mask))
                current ^= basis_mask
        need(current == mask and polynomial_mul(f, witness, witness) ==
             _mask_product(f, forms, mask), "relation witness mismatch")
        witnesses[mask] = witness
    reductions = {}
    for mask in range(1 << n):
        representative = min(mask ^ relation for relation in arithmetic)
        relation = mask ^ representative
        factor = _fraction(f, witnesses[relation],
                           _mask_product(f, forms, representative & relation))
        need(_mul(f, factor, factor) == _fraction(
            f, _mask_product(f, forms, mask),
            _mask_product(f, forms, representative)), "radical reduction mismatch")
        reductions[mask] = (representative, factor)
    masks = sorted({representative for representative, _ in reductions.values()})
    need(type(algebra) is dict and algebra.get("basis_masks") == masks,
         "ambient basis masks mismatch")
    need(algebra.get("degree") == n and algebra.get("arithmetic_rank") ==
         len(masks).bit_length()-1 and len(masks) == 1 << algebra["arithmetic_rank"],
         "ambient rank or dimension mismatch")
    table = algebra.get("multiplication")
    need(type(table) is list and len(table) == len(masks), "ambient table rows")
    for i, left in enumerate(masks):
        need(type(table[i]) is list and len(table[i]) == len(masks),
             "ambient table columns")
        for j, right in enumerate(masks):
            target, factor = reductions[left ^ right]
            expected = _mul(f, _fraction(f, _mask_product(f, forms, left & right), [1]),
                            factor)
            entry = table[i][j]
            need(type(entry) is dict and entry.get("target") == target and
                 _read_fraction(f, entry.get("factor")) == expected,
                 "ambient multiplication mismatch")
    signs = algebra.get("generator_signs")
    need(type(signs) is list and len(signs) == n and
         all(type(sign) is int and sign in (0, 1) for sign in signs) and
         sum(signs) % 2 == 0, "generator signs or order mismatch")
    action = {}
    rows = algebra.get("frobenius_action")
    need(type(rows) is list and len(rows) == len(masks), "ambient action rows")
    for mask, row in zip(masks, rows):
        rotated = ((mask << 1) | (mask >> (n-1))) & ((1 << n)-1)
        target, factor = reductions[rotated]
        if sum(signs[i] for i in range(n) if mask & (1 << i)) % 2:
            factor = _mul(f, factor, _fraction(f, [f.sub(0, 1)], [1]))
        need(type(row) is dict and row.get("from") == mask and
             row.get("target") == target and
             _read_fraction(f, row.get("factor")) == factor,
             "ambient Frobenius action mismatch")
        action[mask] = (target, factor)
    for mask in masks:
        current, factor = mask, _fraction(f, [1], [1])
        for _ in range(n):
            target, multiplier = action[current]
            factor = _mul(f, _frobenius(f, factor), multiplier)
            current = target
        need(current == mask and factor == _fraction(f, [1], [1]),
             "ambient Frobenius order mismatch")
    indices = {mask: index for index, mask in enumerate(masks)}
    for i, left in enumerate(masks):
        for j, right in enumerate(masks):
            product = table[i][j]
            product_target, product_factor = action[product["target"]]
            image_left, left_factor = action[left]
            image_right, right_factor = action[right]
            image_product = table[indices[image_left]][indices[image_right]]
            left_side = _mul(f, _frobenius(f, _read_fraction(f, product["factor"])),
                             product_factor)
            right_side = _mul(f, _mul(f, left_factor, right_factor),
                              _read_fraction(f, image_product["factor"]))
            need(product_target == image_product["target"] and
                 left_side == right_side, "ambient Frobenius is not multiplicative")
    return masks, table, action


def _xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def _read_vector(f, record, masks):
    rows = record.get("coefficients")
    need(type(rows) is list, "fixed vector coefficients shape")
    vector = {}
    for row in rows:
        need(type(row) is dict and type(row.get("mask")) is int and
             row["mask"] in masks and row["mask"] not in vector,
             "fixed vector mask mismatch")
        vector[row["mask"]] = _read_fraction(f, row.get("factor"))
    return {mask: factor for mask, factor in vector.items() if factor[0]}


def _vector_add(f, a, b):
    result = dict(a)
    for mask, factor in b.items():
        result[mask] = _add(f, result.get(mask, ((), (1,))), factor)
        if not result[mask][0]:
            del result[mask]
    return result


def _apply(f, vector, action):
    result = {}
    for mask, factor in vector.items():
        target, multiplier = action[mask]
        result = _vector_add(f, result,
                             {target: _mul(f, _frobenius(f, factor), multiplier)})
    return result


def _fixed_basis(f, fixed, masks, action):
    basis = fixed.get("basis")
    need(type(basis) is dict and basis.get("degree") == f.n and
         basis.get("basis_dimension") == len(masks) and
         basis.get("moore_rank") == f.n, "fixed basis metadata mismatch")
    rows, orbits = basis.get("vectors"), basis.get("orbits")
    need(type(rows) is list and len(rows) == len(masks) and type(orbits) is list,
         "fixed basis rows mismatch")
    unseen, expected_orbits, expected_vectors = set(masks), [], []
    one = _fraction(f, [1], [1])
    while unseen:
        start = min(unseen)
        orbit, current = [start], action[start][0]
        while current != start:
            need(current in unseen and current not in orbit, "action orbit mismatch")
            orbit.append(current)
            current = action[current][0]
        need(len(orbit) in (1, f.n), "action orbit length mismatch")
        unseen.difference_update(orbit)
        expected_orbits.append(orbit)
        indices = range(f.n) if len(orbit) == f.n else range(f.n)
        for index in indices:
            seed = {start: _fraction(f, [f.p**index], [1])}
            trace, current_vector = {}, seed
            for _ in range(f.n):
                trace = _vector_add(f, trace, current_vector)
                current_vector = _apply(f, current_vector, action)
            need(current_vector == seed, "trace action did not close")
            if len(orbit) == f.n or trace:
                expected_vectors.append((start, index, trace))
                if len(orbit) == 1:
                    break
    need(orbits == expected_orbits and len(expected_vectors) == len(rows),
         "fixed basis orbit or dimension mismatch")
    vectors = []
    for row, (start, index, expected) in zip(rows, expected_vectors):
        need(type(row) is dict and row.get("orbit_start") == start and
             row.get("seed_basis_index") == index, "fixed basis seed mismatch")
        vector = _read_vector(f, row, masks)
        need(vector == expected and _apply(f, vector, action) == vector,
             "fixed basis vector mismatch")
        vectors.append(vector)
    return vectors


def _product(f, left, right, masks, table):
    indices = {mask: index for index, mask in enumerate(masks)}
    result = {}
    for left_mask, left_factor in left.items():
        for right_mask, right_factor in right.items():
            entry = table[indices[left_mask]][indices[right_mask]]
            factor = _mul(f, _mul(f, left_factor, right_factor),
                          _read_fraction(f, entry["factor"]))
            result = _vector_add(f, result, {entry["target"]: factor})
    return result


def _linear_combination(f, rows, vectors):
    need(type(rows) is list, "fixed multiplication coordinate shape")
    result, seen = {}, set()
    for row in rows:
        need(type(row) is dict and type(row.get("index")) is int and
             0 <= row["index"] < len(vectors) and row["index"] not in seen,
             "fixed coordinate index mismatch")
        seen.add(row["index"])
        factor = _read_fraction(f, row.get("factor"), base=True)
        need(bool(factor[0]), "zero fixed coordinate term")
        result = _vector_add(f, result, {mask: _mul(f, factor, coefficient)
                                         for mask, coefficient in vectors[row["index"]].items()})
    return result


def _check_source(f, forms, source):
    need(type(source) is dict and source.get("schema") ==
         "pext.source-radical-algebra/v1", "source algebra wrapper mismatch")
    radical = source.get("source")
    need(type(radical) is dict and radical.get("schema") ==
         "pext.source-radical-binding/v1" and radical.get("conjugate_forms") == forms and
         radical.get("source_generator_index") == 0 and
         radical.get("source_generator_square") == forms[0],
         "source radical generator mismatch")
    need(radical.get("radical_action", {}).get("generator_signs") ==
         source.get("algebra", {}).get("generator_signs"),
         "source radical action signs mismatch")
    source_map = radical.get("source_map")
    need(type(source_map) is dict and source_map.get("field", {}).get("prime") == f.p and
         source_map.get("field", {}).get("degree") == f.n and
         source_map.get("field", {}).get("modulus") == f.modulus and
         source_map.get("moved_form") == forms[0], "source form mismatch")
    model, target, matrix = (source_map.get(key) for key in ("model", "target", "matrix"))
    need(type(model) is list and type(matrix) is list and len(matrix) == 4,
         "source model or matrix shape")
    curve = Curve(f, model)
    point = curve.read_point(target)
    original = curve.quotient_form(point)
    need(source_map.get("source_form") == original, "source quotient form mismatch")
    for value in matrix:
        f.element(value)
    a, b, c, d = matrix
    need(f.sub(f.mul(a, d), f.mul(b, c)) != 0, "source matrix singular")
    linear = ([f.sub(0, b), d], [a, f.sub(0, c)])
    moved = [0]*5
    for i, coefficient in enumerate(original):
        term = [coefficient]
        for factor in [linear[0]]*i + [linear[1]]*(4-i):
            term = polynomial_mul(f, term, factor)
        for j, value in enumerate(term):
            moved[j] = f.add(moved[j], value)
    need(moved == forms[0], "source moved form mismatch")
    checked_map = verify_source_map(source_map, source_map["field"], model,
                                    target, matrix)
    need(checked_map["valid"] is True, "source coordinate map replay failed")


def verify(record, field_record, forms):
    """Return a scoped pass after independent exact replay of a serialized model."""
    f = Field(field_record)
    need(type(forms) is list and len(forms) == f.n and f.n in (3, 5, 7),
         "external conjugate forms mismatch")
    for i, form in enumerate(forms):
        need(type(form) is list and len(form) == 5 and
             all(type(c) is int and 0 <= c < f.size for c in form) and
             forms[(i+1) % f.n] == [f.power(c, f.p) for c in form],
             "external conjugate form mismatch")
    need(type(record) is dict, "fixed model record shape")
    if record.get("schema") == "pext.source-fixed-geometry/v1":
        source = record.get("source")
        fixed = record.get("fixed_model")
    elif record.get("schema") == "pext.source-fixed-field-model/v1":
        source = record.get("source")
        fixed = record.get("fixed")
    else:
        need(record.get("schema") == "pext.fixed-field-multiplication/v1",
             "fixed model schema mismatch")
        source, fixed = None, record
    need(type(fixed) is dict and fixed.get("schema") ==
         "pext.fixed-field-multiplication/v1" and fixed.get("degree") == f.n,
         "fixed multiplication record mismatch")
    basis = fixed.get("basis")
    need(type(basis) is dict and type(basis.get("algebra")) is dict,
         "ambient algebra missing")
    masks, ambient_table, action = _ambient(f, forms, basis["algebra"])
    vectors = _fixed_basis(f, fixed, masks, action)
    table = fixed.get("multiplication")
    need(type(table) is list and len(table) == len(vectors) and
         fixed.get("dimension") == len(vectors), "fixed multiplication rows")
    for i, left in enumerate(vectors):
        need(type(table[i]) is list and len(table[i]) == len(vectors),
             "fixed multiplication columns")
        for j, right in enumerate(vectors):
            actual = _product(f, left, right, masks, ambient_table)
            claimed = _linear_combination(f, table[i][j], vectors)
            need(actual == claimed, "fixed multiplication coefficient mismatch")
    unit = _linear_combination(f, fixed.get("unit"), vectors)
    need(unit == {0: _fraction(f, [1], [1])}, "fixed multiplication unit mismatch")
    if source is not None:
        _check_source(f, forms, source)
        need(source.get("algebra") == basis["algebra"],
             "source and fixed ambient algebra mismatch")
        need(1 in masks, "source generator missing from ambient basis")
        source_generator = _product(f, {1: _fraction(f, [1], [1])},
                                    {1: _fraction(f, [1], [1])}, masks, ambient_table)
        need(source_generator == {0: _fraction(f, forms[0], [1])},
             "source generator square mismatch")
    return {"schema": "pext.independent-fixed-model-check/v1", "valid": True,
            "dimension": len(vectors), "products_checked": len(vectors)**2,
            "source_generator_checked": source is not None,
            "scope": "external forms, ambient table, fixed basis, every product/unit, and source generator when bound"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _load(path):
    need(path.stat().st_size <= 256*1024*1024, "checker file limit exceeded")
    return json.loads(path.read_text(), object_pairs_hook=_unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--field", required=True, type=Path)
    parser.add_argument("--forms", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(_load(args.record), _load(args.field),
                                _load(args.forms)), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
