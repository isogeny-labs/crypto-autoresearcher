"""Construct a checked fixed-vector basis for the radical Frobenius action.

Orbit traces use a polynomial basis of K/k and work when characteristic
divides the extension degree. Multiplication over k(x) is a later step.
"""

from check_quotient_certificate import polynomial_mul, trim
from radical_algebra_model import (build as build_algebra, equal_fractions,
                                   fraction, frobenius_fraction,
                                   multiply_fractions)


def add_fractions(field, left, right):
    first = polynomial_mul(field, left["numerator"], right["denominator"])
    second = polynomial_mul(field, right["numerator"], left["denominator"])
    size = max(len(first), len(second))
    numerator = trim([field.add(first[i] if i < len(first) else 0,
                                second[i] if i < len(second) else 0)
                      for i in range(size)])
    return fraction(field, numerator, polynomial_mul(
        field, left["denominator"], right["denominator"]))


def _zero(value):
    return not value["numerator"] or all(c == 0 for c in value["numerator"])


def _add_vectors(field, left, right):
    result = dict(left)
    for mask, coefficient in right.items():
        result[mask] = add_fractions(field, result[mask], coefficient) if mask in result else coefficient
        if _zero(result[mask]):
            del result[mask]
    return result


def _apply(field, vector, action):
    result = {}
    for mask, coefficient in vector.items():
        image = action[mask]
        target = image["target"]
        value = multiply_fractions(field, frobenius_fraction(field, coefficient),
                                   image["factor"])
        if target in result:
            result[target] = add_fractions(field, result[target], value)
        else:
            result[target] = value
    return {mask: value for mask, value in result.items() if not _zero(value)}


def _equal_vectors(field, left, right):
    if set(left) != set(right):
        return False
    return all(equal_fractions(field, left[mask], right[mask]) for mask in left)


def _field_basis_rank(field):
    """Rank of the Moore matrix for the polynomial k-basis of K."""
    degree = field.n
    values = [field.p**index for index in range(degree)]
    rows = [[field.power(value, field.p**row) for value in values]
            for row in range(degree)]
    rank = 0
    for column in range(degree):
        pivot = next((row for row in range(rank, degree) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = field.div(1, rows[rank][column])
        rows[rank] = [field.mul(inverse, value) for value in rows[rank]]
        for row in range(degree):
            if row != rank and rows[row][column]:
                scale = rows[row][column]
                rows[row] = [field.sub(value, field.mul(scale, pivot_value))
                             for value, pivot_value in zip(rows[row], rows[rank])]
        rank += 1
    if rank != degree:
        raise ValueError("polynomial-basis Moore matrix is singular")
    return rank


def build(field, forms):
    """Return exactly dim_K(A) invariant vectors spanning A over K(x)."""
    algebra = build_algebra(field, forms)
    masks = algebra["basis_masks"]
    action = {row["from"]: row for row in algebra["frobenius_action"]}
    if set(action) != set(masks) or _field_basis_rank(field) != field.n:
        raise ValueError("radical action or polynomial basis incomplete")
    unseen = set(masks)
    orbits, vectors = [], []
    one = fraction(field, [1], [1])
    while unseen:
        start = min(unseen)
        orbit = [start]
        current = action[start]["target"]
        while current != start:
            if current in orbit or current not in unseen:
                raise ValueError("radical Frobenius orbit is not a cycle")
            orbit.append(current)
            current = action[current]["target"]
        if len(orbit) not in (1, field.n):
            raise ValueError("unexpected radical Frobenius orbit length")
        unseen.difference_update(orbit)
        if len(orbit) == field.n:
            for index in range(field.n):
                seed = {start: fraction(field, [field.p**index], [1])}
                trace, current_vector = {}, seed
                for _ in range(field.n):
                    trace = _add_vectors(field, trace, current_vector)
                    current_vector = _apply(field, current_vector, action)
                if not _equal_vectors(field, current_vector, seed):
                    raise ValueError("radical orbit did not close after n actions")
                vectors.append({"orbit_start": start, "seed_basis_index": index,
                                "coefficients": trace})
        else:
            found = False
            for index in range(field.n):
                seed = {start: fraction(field, [field.p**index], [1])}
                trace, current_vector = {}, seed
                for _ in range(field.n):
                    trace = _add_vectors(field, trace, current_vector)
                    current_vector = _apply(field, current_vector, action)
                if trace:
                    vectors.append({"orbit_start": start, "seed_basis_index": index,
                                    "coefficients": trace})
                    found = True
                    break
            if not found:
                raise ValueError("fixed radical orbit has zero trace on field basis")
        orbits.append(orbit)
    if len(vectors) != len(masks):
        raise ValueError("fixed radical basis dimension mismatch")
    for vector in vectors:
        if not _equal_vectors(field, _apply(field, vector["coefficients"], action),
                              vector["coefficients"]):
            raise ValueError("constructed radical vector is not Frobenius fixed")
    return {"schema": "pext.fixed-radical-basis/v1", "degree": field.n,
            "algebra": algebra, "orbits": orbits, "vectors": [
                {"orbit_start": row["orbit_start"],
                 "seed_basis_index": row["seed_basis_index"],
                 "coefficients": [{"mask": mask, "factor": coefficient}
                                  for mask, coefficient in sorted(row["coefficients"].items())]}
                for row in vectors],
            "basis_dimension": len(vectors), "moore_rank": field.n,
            "status": "fixed_kx_basis_checked; base_multiplication_pending"}
