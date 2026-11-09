"""Prospective C6 same-source coordinate control with a twisted action.

A common K-projective change of the whole conjugate family preserves its
square classes. For M outside PGL2(F_q), conjugating only the moved f0 makes a
different family; its ordinary coefficient orbit is not the C6 comparison.
"""

import hashlib
import json

from candidate_binding import CandidateBinder
from check_quotient_certificate import Field
from check_structure_certificate import inverse, multiply, normalize, transform
from independent_component_geometry import assess
from independent_source_map_check import verify as verify_source_map
from independent_transversal import IndependentTransversal
from source_map_binding import certify, certify_bound


SEED = 20261102
DRAW_CAP = 4096
SLOTS = 16
GEOMETRY_KEYS = ("geometric_rank", "arithmetic_rank",
                 "geometric_component_count", "geometric_component_degree",
                 "geometric_component_genus", "connected_curve_genus",
                 "branch_points", "character_count")


def _need(condition, reason):
    if not condition:
        raise ValueError(reason)


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _orbit(field, form):
    result = [form]
    for _ in range(1, field.n):
        result.append([field.power(value, field.p) for value in result[-1]])
    _need([field.power(value, field.p) for value in result[-1]] == form,
          "source coefficient orbit does not close")
    return result


def _exact_inverse(field, matrix):
    a, b, c, d = matrix
    determinant = field.sub(field.mul(a, d), field.mul(b, c))
    _need(determinant != 0, "singular C6 matrix")
    result = [field.div(value, determinant) for value in inverse(field, matrix)]
    identity = [1, 0, 0, 1]
    _need(multiply(field, matrix, result) == identity
          and multiply(field, result, matrix) == identity,
          "C6 matrix inverse mismatch")
    return result


def seeded_matrix(field_record, binding, ordinal, slot, *, seed=SEED):
    """SHA256 counter stream; one fixed draw cap for each of 16 slots."""
    field = Field(field_record)
    _need(type(seed) is int and seed == SEED
          and type(slot) is int and 0 <= slot < SLOTS
          and type(ordinal) is int
          and 0 <= ordinal < binding["structures_per_T"],
          "C6 seed, slot or ordinal outside frozen plan")
    identity = {key: binding[key] for key in (
        "cohort", "class_index", "T_index", "join_plan_sha256",
        "input_sha256", "manifest_sha256", "structure_offset")}
    # Rejection preserves a uniform coefficient in F_{p^n}; modulo the full
    # 16-bit range would bias values when the field size does not divide 2^16.
    limit = 65536 - (65536 % field.size)
    for counter in range(DRAW_CAP):
        payload = json.dumps(["pext-c6-coordinate/v1", seed, identity, ordinal,
                              slot, counter], sort_keys=True,
                             separators=(",", ":")).encode()
        block = hashlib.sha256(payload).digest()
        words = [int.from_bytes(block[2*i:2*(i+1)], "little")
               for i in range(4)]
        if any(value >= limit for value in words):
            continue
        raw = [value % field.size for value in words]
        a, b, c, d = raw
        if field.mul(a, d) == field.mul(b, c) or c == 0:
            continue
        matrix = normalize(field, raw)
        if all(field.power(value, field.p) == value for value in matrix):
            continue
        return {"matrix": matrix, "draw_index": counter,
                "counter_sha256": block.hex(),
                "sha256_blocks": counter + 1,
                "sha256_bytes_generated": 32 * (counter + 1),
                "sample_bytes_examined": 8 * (counter + 1)}
    raise ValueError("C6 deterministic transport draw cap exhausted")


def check_transport(binder, class_index, t_index, ordinal, matrix, *,
                    slot=None, draw_index=None, counter_sha256=None,
                    sha256_blocks=None, sha256_bytes_generated=None,
                    sample_bytes_examined=None):
    """Check one published source/T and one common K-coordinate change."""
    _need(isinstance(binder, CandidateBinder) and binder.plan_path is not None,
          "published checked CandidateBinder required")
    binding = binder.bind(class_index, t_index)
    field = Field(binding["field"])
    _need(type(ordinal) is int, "C6 structure ordinal required")
    base_matrix = IndependentTransversal(binding["field"]).matrix(ordinal)
    _need(type(matrix) is list and matrix == normalize(field, matrix),
          "C6 transport matrix must be canonical")
    inverse_matrix = _exact_inverse(field, matrix)
    source = certify_bound(binder, class_index, t_index, ordinal, base_matrix)
    checked_source = verify_source_map(source, binding["field"],
                                       binding["model"], binding["target"],
                                       base_matrix)
    _need(checked_source["valid"] is True, "base source-map replay failed")
    base_forms = _orbit(field, source["moved_form"])
    base_geometry = assess(binding["field"], base_forms)

    common_forms = [transform(field, form, matrix) for form in base_forms]
    raw_composite = multiply(field, matrix, base_matrix)
    _need(common_forms[0] == transform(field, binding["quotient_form"],
                                       raw_composite),
          "literal C6 composition loses binary-form scalar")
    scalar = next(value for value in raw_composite if value)
    normalized_composite = normalize(field, raw_composite)
    quartic_factor = field.power(scalar, 4)
    ordinate_factor = field.power(scalar, 2)
    normalized_form = [field.div(value, quartic_factor)
                       for value in common_forms[0]]
    transported_source = certify(binding["field"], binding["model"],
                                 binding["target"], normalized_composite)
    checked_transported = verify_source_map(
        transported_source, binding["field"], binding["model"],
        binding["target"], normalized_composite)
    _need(checked_transported["valid"] is True
          and transported_source["moved_form"] == normalized_form,
          "transported source map or scalar mismatch")

    sigma_matrix = [field.power(value, field.p) for value in matrix]
    twist = multiply(field, sigma_matrix, inverse_matrix)
    common_geometry = assess(binding["field"], common_forms,
                             twisted_frobenius_matrix=twist)
    base_invariants = {key: base_geometry[key] for key in GEOMETRY_KEYS}
    common_invariants = {key: common_geometry[key] for key in GEOMETRY_KEYS}
    _need(base_invariants == common_invariants,
          "C6 common-coordinate geometry changed")
    result = {"schema": "pext.c6-coordinate-control/v1",
              "status": "prospective_source_only_control; cohort_admission_pending",
              "cohort": binding["cohort"], "class_index": class_index,
              "T_index": t_index, "structure_ordinal": ordinal,
              "join_plan_sha256": binding["join_plan_sha256"],
              "binding_sha256": _hash(binding),
              "base_matrix": base_matrix, "transport_matrix": matrix,
              "inverse_transport_matrix": inverse_matrix,
              "raw_composite_matrix": raw_composite,
              "normalized_composite_matrix": normalized_composite,
              "binary_form_scalar_factor": quartic_factor,
              "ordinate_scalar_factor": ordinate_factor,
              "twisted_frobenius_matrix": twist,
              "base_source_map_sha256": _hash(source),
              "transported_source_map_sha256": _hash(transported_source),
              "base_invariants": base_invariants,
              "common_transport_invariants": common_invariants,
              "invariant_equality": True}
    if slot is not None:
        result.update({"seed": SEED, "slot": slot,
                       "draw_index": draw_index,
                       "counter_sha256": counter_sha256,
                       "sha256_blocks": sha256_blocks,
                       "sha256_bytes_generated": sha256_bytes_generated,
                       "sample_bytes_examined": sample_bytes_examined})
    return result


def check_seeded(binder, class_index, t_index, ordinal, slot):
    """Check one predeclared C6 slot without sampling observed results."""
    binding = binder.bind(class_index, t_index)
    draw = seeded_matrix(binding["field"], binding, ordinal, slot)
    return check_transport(binder, class_index, t_index, ordinal,
                           draw["matrix"], slot=slot,
                           draw_index=draw["draw_index"],
                           counter_sha256=draw["counter_sha256"],
                           sha256_blocks=draw["sha256_blocks"],
                           sha256_bytes_generated=draw[
                               "sha256_bytes_generated"],
                           sample_bytes_examined=draw[
                               "sample_bytes_examined"])


def check_all_slots(binder, class_index, t_index, ordinal):
    """Retain all 16 predeclared transports for one selected C6 unit."""
    results = [check_seeded(binder, class_index, t_index, ordinal, slot)
               for slot in range(SLOTS)]
    matrices = [tuple(row["transport_matrix"]) for row in results]
    # A duplicate makes this fixed control inconclusive. Do not replace it by
    # an adaptive seventeenth slot or change the predeclared draw stream.
    _need(len(set(matrices)) == SLOTS,
          "C6 control inconclusive: duplicate frozen seeded transports")
    _need(all(row["invariant_equality"] is True for row in results),
          "C6 invariant equality incomplete")
    return {"schema": "pext.c6-coordinate-control-batch/v1",
            "status": "prospective_source_only_control; cohort_admission_pending",
            "cohort": results[0]["cohort"],
            "class_index": class_index, "T_index": t_index,
            "structure_ordinal": ordinal,
            "join_plan_sha256": results[0]["join_plan_sha256"],
            "seed": SEED, "draw_cap": DRAW_CAP,
            "slot_count": SLOTS, "rows": results}
