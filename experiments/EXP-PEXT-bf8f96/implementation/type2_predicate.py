"""Separate Chao Type2 orbit signature and trace-zero Mobius predicate.

Applies to a cubic extension K/k with prime k=F_p. The branch roots live in
the checked quadratic extension of K. This is an exact P4 instrument, not a
descent or hyperelliptic-model certificate.
"""

from check_all_degree_collision_certificate import validate_row
from check_structure_certificate import normalize, transform


def _add(extension, left, right):
    return extension.add(left, right)


def _scale(extension, value, scalar):
    return extension.mul(value, extension.constant(scalar))


def _projective_image(field, extension, matrix, root):
    a, b, c, d = matrix
    numerator = _add(extension, _scale(extension, root, a), extension.constant(b))
    denominator = _add(extension, _scale(extension, root, c), extension.constant(d))
    if denominator == extension.constant(0):
        raise ValueError("degree-six root sent to infinity")
    inverse = extension.power(denominator, field.size**extension.degree-2)
    return extension.mul(numerator, inverse)


def _orbit(extension, root, prime):
    values = [root]
    for _ in range(5):
        values.append(extension.power(values[-1], prime))
    if extension.power(values[-1], prime) != root or len(set(values)) != 6:
        return None
    return values


def _base_matrix_witness(field, extension, alpha):
    beta = extension.power(alpha, field.p**3)
    trace = _add(extension, alpha, beta)
    norm = extension.mul(alpha, beta)
    if any(trace[index] or norm[index] for index in range(1, extension.degree)):
        raise ValueError("quadratic conjugate trace or norm outside K")
    # Trace zero gives d=-a. Then b=c*alpha*beta-a*(alpha+beta).
    # Every a,c in F_p is exhausted; b is uniquely forced in K.
    for a in range(field.p):
        for c in range(field.p):
            b = field.sub(field.mul(c, norm[0]), field.mul(a, trace[0]))
            if b >= field.p:
                continue
            d = field.sub(0, a)
            determinant = field.sub(field.mul(a, d), field.mul(b, c))
            if determinant == 0:
                continue
            matrix = normalize(field, [a, b, c, d])
            left = _add(extension, _scale(extension, alpha, c), extension.constant(d))
            left = extension.mul(beta, left)
            right = _add(extension, _scale(extension, alpha, a), extension.constant(b))
            if left != right:
                raise ValueError("trace-zero matrix equation mismatch")
            return matrix
    return None


def inspect(field, unit, matrix):
    """Return independently checked Type2 signature and separate predicate."""
    if field.n != 3 or field.p % 2 != 1:
        raise ValueError("Type2 instrument requires odd cubic extension")
    factor = {"form": unit["form"], "pattern": unit["factor_pattern"],
              "infinity": unit["infinity"], "factors": unit["factors"],
              "extension_modulus": unit["extension_modulus"], "roots": unit["roots"]}
    extension, roots = validate_row(field, factor, unit["form"], unit["factor_pattern"])
    matrix = normalize(field, matrix)
    moved = transform(field, unit["form"], matrix)
    if unit["factor_pattern"] != [2, 2]:
        return {"schema": "pext.type2-predicate/v1", "signature": False,
                "hyperelliptic_predicate": None, "moved_form": moved,
                "status": "checked_non_type2_factor_pattern"}
    if extension.degree != 2 or len(roots) != 4:
        raise ValueError("Type2 quadratic roots incomplete")
    moved_roots = [_projective_image(field, extension, matrix, root) for root in roots]
    if len(set(moved_roots)) != 4 or any(extension.evaluate(moved, root) != extension.constant(0)
                                       for root in moved_roots):
        raise ValueError("moved Type2 branch roots invalid")
    ordered = sorted(moved_roots)
    choices = []
    for alpha in ordered:
        orbit = _orbit(extension, alpha, field.p)
        if orbit is not None and set(moved_roots) == {orbit[index] for index in (0, 1, 3, 4)}:
            choices.append(alpha)
    if not choices:
        return {"schema": "pext.type2-predicate/v1", "signature": False,
                "hyperelliptic_predicate": None, "moved_form": moved,
                "status": "checked_no_length_six_type2_orbit"}
    witnesses = [(alpha, _base_matrix_witness(field, extension, alpha)) for alpha in choices]
    accepted = next(((alpha, witness) for alpha, witness in witnesses if witness is not None), None)
    return {"schema": "pext.type2-predicate/v1", "signature": True,
            "hyperelliptic_predicate": accepted is not None,
            "moved_form": moved, "alpha": list((accepted or witnesses[0])[0]),
            "trace_zero_matrix": None if accepted is None else accepted[1],
            "alpha_choices_checked": len(choices),
            "base_matrix_pair_space_per_choice": field.p**2,
            "status": "checked_type2_signature_and_trace_zero_predicate"}
