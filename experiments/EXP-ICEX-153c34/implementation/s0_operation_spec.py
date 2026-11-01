"""Independent operation-site contract for the ICEX S0 accounting gate.

This module deliberately contains no G1 arithmetic.  It is the reviewable,
separately maintained vocabulary against which both the producer trace and an
independent deterministic replay are checked.  Adding or moving a charged
operation therefore requires an explicit change here as well as in the G1
implementation.
"""

from __future__ import annotations


COMPONENTS = ("P", "S", "G", "X", "V")
RAW_FIELDS = ("mul", "inv", "probes", "point_add",
              "s_pairs", "reductions", "product_skips")
WEIGHTS = {"mul": 1, "inv": 10, "probes": 1, "point_add": 13,
           "s_pairs": 0, "reductions": 0, "product_skips": 0}


# site -> (operation, allowed components).  Generic polynomial primitives are
# intentionally allowed only in the stages in which the frozen algorithm uses
# them.  A trace containing an unregistered site, operation, or stage fails.
SITE_SPEC = {
    "Field.mul": ("mul", frozenset(("S", "X"))),
    "Field.inv": ("inv", frozenset(("S", "X"))),
    "poly_mul": ("mul", frozenset(("S",))),
    "poly_eval": ("mul", frozenset(("X",))),
    "d2_target.xR_square": ("mul", frozenset(("S",))),
    "d2_target.a_xR": ("mul", frozenset(("S",))),
    "d2_target.a_square": ("mul", frozenset(("S",))),
    "d2_target.b_xR": ("mul", frozenset(("S",))),
    "d2_specialise.scalar": ("mul", frozenset(("S",))),
    "d2_specialise.pair_product": ("mul", frozenset(("S",))),
    "d2_zero_target.coefficient": ("mul", frozenset(("S",))),
    "one_var_remainder": ("mul", frozenset(("P", "S"))),
    "setup.f5.pow_a.accumulate": ("mul", frozenset(("P",))),
    "setup.f5.pow_a.square": ("mul", frozenset(("P",))),
    "setup.f5.pow_b.accumulate": ("mul", frozenset(("P",))),
    "setup.f5.pow_b.square": ("mul", frozenset(("P",))),
    "setup.f5.coefficient_a": ("mul", frozenset(("P",))),
    "setup.f5.coefficient_b": ("mul", frozenset(("P",))),
    "setup.indicator_product": ("mul", frozenset(("P",))),
    "setup.indicator_reduce": ("mul", frozenset(("P",))),
    "setup.lift.x_square": ("mul", frozenset(("P",))),
    "setup.lift.x_cube": ("mul", frozenset(("P",))),
    "setup.lift.a_x": ("mul", frozenset(("P",))),
    "setup.sqrt.legendre.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.legendre.square": ("mul", frozenset(("P",))),
    "setup.sqrt.direct.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.direct.square": ("mul", frozenset(("P",))),
    "setup.sqrt.nonresidue.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.nonresidue.square": ("mul", frozenset(("P",))),
    "setup.sqrt.c.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.c.square": ("mul", frozenset(("P",))),
    "setup.sqrt.t.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.t.square": ("mul", frozenset(("P",))),
    "setup.sqrt.root.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.root.square": ("mul", frozenset(("P",))),
    "setup.sqrt.correction.accumulate": ("mul", frozenset(("P",))),
    "setup.sqrt.correction.square": ("mul", frozenset(("P",))),
    "setup.sqrt.t_square": ("mul", frozenset(("P",))),
    "setup.sqrt.square_loop": ("mul", frozenset(("P",))),
    "setup.sqrt.root_correction": ("mul", frozenset(("P",))),
    "setup.sqrt.correction_square": ("mul", frozenset(("P",))),
    "setup.sqrt.t_correction_square": ("mul", frozenset(("P",))),
    "fp_pow.accumulate": ("mul", frozenset(("X",))),
    "fp_pow.square": ("mul", frozenset(("X",))),
    "sparse_eval": ("mul", frozenset(("X",))),
    "SparsePoly.add.scale": ("mul", frozenset(("G",))),
    "SparsePoly.mul": ("mul", frozenset(("P",))),
    "SparsePoly.monic.inverse": ("inv", frozenset(("G",))),
    "SparsePoly.monic.scale": ("mul", frozenset(("G",))),
    "normal_form.inverse": ("inv", frozenset(("G",))),
    "normal_form.leading_scale": ("mul", frozenset(("G",))),
    "normal_form.reduction": ("reductions", frozenset(("G",))),
    "s_polynomial.f_inverse": ("inv", frozenset(("G",))),
    "s_polynomial.f_scale": ("mul", frozenset(("G",))),
    "s_polynomial.g_inverse": ("inv", frozenset(("G",))),
    "s_polynomial.g_scale": ("mul", frozenset(("G",))),
    "buchberger.product_criterion": ("product_skips", frozenset(("G",))),
    "buchberger.s_pair": ("s_pairs", frozenset(("G",))),
    "root_specialisation": ("mul", frozenset(("X",))),
    "signed_recovery.point_add": ("point_add", frozenset(("V",))),
}


def empty_raw():
    return {field: 0 for field in RAW_FIELDS}


def units(raw):
    return sum(raw[field] * WEIGHTS[field] for field in RAW_FIELDS)


def validate_event(event, expected_sequence=None):
    """Return a list of contract errors for one event."""
    errors = []
    if not isinstance(event, dict):
        return ["event is not an object"]
    if set(event) != {"sequence", "component", "operation", "count", "site"}:
        return ["event has an inexact field set"]
    if expected_sequence is not None and event["sequence"] != expected_sequence:
        errors.append("event has a nonconsecutive sequence")
    site = event["site"]
    if site not in SITE_SPEC:
        errors.append("event uses an unregistered operation site")
        return errors
    wanted_operation, allowed_components = SITE_SPEC[site]
    if event["operation"] != wanted_operation:
        errors.append("event operation disagrees with the site contract")
    if event["component"] not in allowed_components:
        errors.append("event component disagrees with the site contract")
    count = event["count"]
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        errors.append("event count is not a positive integer")
    return errors


def aggregate(events):
    """Validate and aggregate a complete ordered trace by component."""
    errors = []
    raw = {component: empty_raw() for component in COMPONENTS}
    last_component = 0
    for sequence, event in enumerate(events):
        event_errors = validate_event(event, sequence)
        errors.extend("event %d: %s" % (sequence, error) for error in event_errors)
        if event_errors:
            continue
        component_index = COMPONENTS.index(event["component"])
        if component_index < last_component:
            errors.append("event %d moves backward between components" % sequence)
        last_component = max(last_component, component_index)
        raw[event["component"]][event["operation"]] += event["count"]
    return raw, errors
