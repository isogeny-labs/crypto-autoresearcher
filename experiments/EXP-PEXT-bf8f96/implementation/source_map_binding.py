"""Exact source elliptic map to a projectively moved quotient quartic.

The map keeps the determinant-dependent ordinate scalar. It binds an actual
K-Weierstrass model, a canonical T and a checked projective structure. It
does not construct the fixed-field model of the radical Frobenius action.
"""

from candidate_binding import CandidateBinder
from check_quotient_certificate import require
from check_structure_certificate import normalize, transform
from independent_transversal import IndependentTransversal
from target_transport import FunctionField, coordinates, verified_field
import json


def _polynomial_at(ring, polynomial, argument):
    value = ring.integer(0)
    for coefficient in reversed(polynomial):
        value = value*argument + ring.scalar(coefficient)
    return value


def _encode(value):
    return {"numerator_constant": value.a,
            "numerator_y": value.b,
            "denominator": value.d}


def certify(field_record, model, target, matrix):
    """Check the forward equation and both rational inverse charts."""
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(",", ":")))
    ring = FunctionField(field, model)
    point = ring.curve.read_point(target)
    matrix = normalize(field, matrix)
    a, b, c, d = map(ring.scalar, matrix)
    determinant = field.sub(field.mul(matrix[0], matrix[3]),
                            field.mul(matrix[1], matrix[2]))
    require(determinant != 0, "singular source-map matrix")
    t, w = coordinates(ring, point, ring.x(), ring.y())
    form = ring.curve.quotient_form(point)
    require((w*w).equals_cross(_polynomial_at(ring, form, t)),
            "source quotient equation mismatch")
    denominator = c*t+d
    x_new = (a*t+b)/denominator
    y_new = ring.scalar(field.mul(determinant, determinant))*w/(denominator*denominator)
    moved = transform(field, form, matrix)
    require((y_new*y_new).equals_cross(_polynomial_at(ring, moved, x_new)),
            "weighted projective quartic identity mismatch")
    t_back = (d*x_new-b)/(a-c*x_new)
    w_back = y_new*(c*t_back+d)**2/ring.scalar(field.mul(determinant, determinant))
    require(t_back.equals_cross(t) and w_back.equals_cross(w),
            "projective inverse coordinate mismatch")
    if point is None:
        x_back, y_back = t_back, w_back
    else:
        u, v = map(ring.scalar, point)
        x_back = (t_back*t_back-ring.scalar(ring.curve.a2)-u+w_back)/ring.integer(2)
        y_back = t_back*(x_back-u)-v
    require(x_back.equals_cross(ring.x()) and y_back.equals_cross(ring.y()),
            "elliptic inverse coordinate mismatch")
    return {"schema": "pext.source-map-binding/v1", "field": field_record,
            "model": model, "target": target, "matrix": matrix,
            "source_form": form, "moved_form": moved,
            "determinant": determinant, "x_map": _encode(x_new),
            "y_map": _encode(y_new),
            "status": "source_to_moved_quartic_checked; descended_model_pending"}


def certify_bound(binder, class_index, t_index, ordinal, matrix):
    """Bind the exact identity to a published class/T and structure ordinal."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("checked published cohort binder required")
    binding = binder.bind(class_index, t_index)
    transversal = IndependentTransversal(binding["field"])
    if type(ordinal) is not int or not 0 <= ordinal < transversal.count:
        raise ValueError("structure ordinal outside published transversal")
    if matrix != transversal.matrix(ordinal):
        raise ValueError("structure matrix differs from independent ordinal")
    record = certify(binding["field"], binding["model"], binding["target"], matrix)
    if record["source_form"] != binding["quotient_form"]:
        raise ValueError("source map differs from canonical quotient form")
    record.update({"cohort": binding["cohort"], "class_index": class_index,
                   "T_index": t_index, "structure_ordinal": ordinal,
                   "join_plan_sha256": binding["join_plan_sha256"],
                   "structure_offset": binding["structure_offset"]})
    return record
