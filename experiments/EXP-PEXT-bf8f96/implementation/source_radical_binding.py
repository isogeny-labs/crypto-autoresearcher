"""Bind an actual elliptic quotient to generator zero of a radical algebra.

This checks the named source model, T and projective map, then checks the
coherent conjugate radicals and an order-n semilinear action. A fixed-field
model and descended admissible genus still require separate certificates.
"""

import json

from candidate_binding import CandidateBinder
from radical_frobenius import candidate_lift
from source_map_binding import certify as certify_source
from source_map_binding import certify_bound as certify_bound_source
from target_transport import verified_field


def _bind(source, forms):
    field_record = source["field"]
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(",", ":")))
    if (field.n not in (3, 5, 7) or field.p % 2 != 1
            or not isinstance(forms, list) or len(forms) != field.n):
        raise ValueError("source radical requires an odd n=3/5/7 conjugate orbit")
    current = source["moved_form"]
    for index, form in enumerate(forms):
        if (not isinstance(form, list) or len(form) != 5
                or any(type(value) is not int or not 0 <= value < field.size for value in form)
                or form != current):
            raise ValueError(f"source radical conjugate {index} differs from exact source map")
        current = [field.power(value, field.p) for value in current]
    if current != source["moved_form"]:
        raise ValueError("source radical coefficient orbit does not close")
    lift = candidate_lift(field, forms)
    if (lift.get("status") != "order_n_radical_lift_checked; source_map_and_model_pending"
            or lift.get("degree") != field.n or lift.get("order_n_check") is not True
            or len(lift.get("generator_signs", [])) != field.n):
        raise ValueError("source radical action absent, degree or order mismatch")
    return {"schema": "pext.source-radical-binding/v1", "source_map": source,
            "conjugate_forms": forms, "radical_action": lift,
            "source_generator_index": 0,
            "source_generator_square": source["moved_form"],
            "action_on_generators": [
                {"from": index, "to": (index+1) % field.n,
                 "sign": lift["generator_signs"][index]}
                for index in range(field.n)],
            "status": "source_generator_and_order_n_action_checked; fixed_field_model_pending"}


def certify(field_record, model, target, matrix, forms):
    """Check source E/T/map, coefficient orbit and coherent radical action."""
    return _bind(certify_source(field_record, model, target, matrix), forms)


def certify_bound(binder, class_index, t_index, ordinal, matrix, forms):
    """Also bind to the published curve/T and independent structure ordinal."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("published source radical binder required")
    return _bind(certify_bound_source(binder, class_index, t_index, ordinal,
                                      matrix), forms)
