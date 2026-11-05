"""Exact monomial-basis model of a conjugate quartic radical algebra.

Arithmetic square relations choose a canonical F2 quotient basis. Rational
function factors give multiplication and the order-n semilinear Frobenius
action. Computing an explicit invariant fixed-field basis comes next.
"""

import json

from check_quotient_certificate import polynomial_mul
from radical_frobenius import (candidate_lift, derive_witnesses, parity,
                               product_for_mask)
from source_radical_binding import certify as certify_source_radical
from squareclass_relations import ledger
from target_transport import verified_field


def fraction(field, numerator, denominator):
    if not denominator or all(value == 0 for value in denominator):
        raise ValueError("zero rational denominator")
    return {"numerator": list(numerator), "denominator": list(denominator)}


def multiply_fractions(field, left, right):
    return fraction(field, polynomial_mul(field, left["numerator"], right["numerator"]),
                    polynomial_mul(field, left["denominator"], right["denominator"]))


def equal_fractions(field, left, right):
    return (polynomial_mul(field, left["numerator"], right["denominator"])
            == polynomial_mul(field, right["numerator"], left["denominator"]))


def frobenius_fraction(field, value):
    return fraction(field,
                    [field.power(c, field.p) for c in value["numerator"]],
                    [field.power(c, field.p) for c in value["denominator"]])


def _rotate(mask, degree):
    return ((mask << 1) | (mask >> (degree - 1))) & ((1 << degree) - 1)


def _negative(field, value):
    return fraction(field, [field.sub(0, c) for c in value["numerator"]],
                    value["denominator"])


def build(field, forms):
    """Return exact K(x)-basis, multiplication table and Frobenius table."""
    relation = ledger(field, forms)
    lift = candidate_lift(field, forms)
    if lift["status"] != "order_n_radical_lift_checked; source_map_and_model_pending":
        raise ValueError("order-n radical action unavailable")
    degree = len(forms)
    relation_masks = [row["mask"] for row in relation["relations"]
                      if row["arithmetic_relation"]]
    _, witnesses = derive_witnesses(field, forms, relation["relations"])
    if set(witnesses) != set(relation_masks):
        raise ValueError("arithmetic relation witness coverage")
    quotient = {mask: min(mask ^ r for r in relation_masks)
                for mask in range(1 << degree)}
    basis = sorted(set(quotient.values()))
    if len(basis) != 1 << relation["arithmetic_rank"] or basis[0] != 0:
        raise ValueError("radical quotient basis dimension mismatch")
    reductions = {}
    for mask, representative in quotient.items():
        relation_mask = mask ^ representative
        common = representative & relation_mask
        factor = fraction(field, witnesses[relation_mask],
                          product_for_mask(field, forms, common))
        # Y_mask = factor * Y_representative; verify by squaring in K(x).
        left = polynomial_mul(field,
                              polynomial_mul(field, factor["numerator"],
                                             factor["numerator"]),
                              product_for_mask(field, forms, representative))
        right = polynomial_mul(field, product_for_mask(field, forms, mask),
                               polynomial_mul(field, factor["denominator"],
                                              factor["denominator"]))
        if left != right:
            raise ValueError("radical quotient reduction square identity")
        reductions[mask] = (representative, factor)
    multiplication = []
    for left in basis:
        row = []
        for right in basis:
            target, factor = reductions[left ^ right]
            common = product_for_mask(field, forms, left & right)
            row.append({"target": target,
                        "factor": multiply_fractions(
                            field, fraction(field, common, [1]), factor)})
        multiplication.append(row)
    sign_mask = sum(value << index for index, value in enumerate(lift["generator_signs"]))
    action = []
    for mask in basis:
        target, factor = reductions[_rotate(mask, degree)]
        if parity(sign_mask & mask):
            factor = _negative(field, factor)
        action.append({"from": mask, "target": target, "factor": factor})
    indices = {mask: index for index, mask in enumerate(basis)}
    for left_index in range(len(basis)):
        for right_index in range(len(basis)):
            product = multiplication[left_index][right_index]
            image = action[indices[product["target"]]]
            image_factor = multiply_fractions(
                field, frobenius_fraction(field, product["factor"]), image["factor"])
            left_image, right_image = action[left_index], action[right_index]
            target_product = multiplication[indices[left_image["target"]]][
                indices[right_image["target"]]]
            factors = multiply_fractions(
                field, multiply_fractions(field, left_image["factor"],
                                          right_image["factor"]),
                target_product["factor"])
            if (image["target"] != target_product["target"]
                    or not equal_fractions(field, image_factor, factors)):
                raise ValueError("Frobenius does not preserve radical multiplication")
    identity = fraction(field, [1], [1])
    for mask in basis:
        target, factor = mask, identity
        for _ in range(degree):
            image = action[indices[target]]
            factor = multiply_fractions(
                field, frobenius_fraction(field, factor), image["factor"])
            target = image["target"]
        if target != mask or not equal_fractions(field, factor, identity):
            raise ValueError("Frobenius action does not have order n on basis")
    return {"schema": "pext.radical-algebra-model/v1", "degree": degree,
            "basis_masks": basis, "arithmetic_rank": relation["arithmetic_rank"],
            "geometric_rank": relation["geometric_rank"],
            "constant_nonsquare_relation": relation["constant_nonsquare_relation"],
            "multiplication": multiplication, "frobenius_action": action,
            "generator_signs": lift["generator_signs"],
            "status": "explicit_Kx_algebra_and_order_n_action; fixed_invariants_pending"}


def build_from_source(field_record, model, target, matrix, forms):
    """Attach the algebra table to the exact named elliptic source map."""
    source = certify_source_radical(field_record, model, target, matrix, forms)
    if source["status"] != "source_generator_and_order_n_action_checked; fixed_field_model_pending":
        raise ValueError("source radical action unavailable")
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(",", ":")))
    algebra = build(field, forms)
    if algebra["generator_signs"] != source["radical_action"]["generator_signs"]:
        raise ValueError("source and algebra Frobenius signs differ")
    return {"schema": "pext.source-radical-algebra/v1", "source": source,
            "algebra": algebra,
            "status": "source_and_explicit_Kx_algebra_checked; fixed_invariants_pending"}
