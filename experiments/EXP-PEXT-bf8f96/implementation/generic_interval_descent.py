"""Prospective descent theorem for the exact generic complement of one T unit.

The checked exceptional-set complement supplies the universal disjoint-support
premise. No structure in an interval is materialized as a fixed-field model.
The certificate records a theorem application, not a cohort observation.
"""

import hashlib
import json

from candidate_binding import CandidateBinder
from independent_candidate_unit import IndependentCandidateChecker


SCHEMA = "pext.generic-interval-descent/v1"
THEOREM = "disjoint-conjugate-quartics-order-n-permutation/v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _check_binding(unit, binding, checker):
    if (binding.get("schema") != "pext.candidate-binding/v1"
            or binding.get("experiment") != "EXP-PEXT-bf8f96"
            or binding.get("field") != unit.get("field")
            or binding.get("quotient_form") != unit.get("form")
            or binding.get("structures_per_T") != unit.get("structures")
            or checker.field_record != binding["field"]):
        raise ValueError("external candidate binding mismatch")
    for key in ("cohort", "class_index", "T_index", "model", "target",
                "input_sha256", "manifest_sha256", "join_plan_sha256",
                "structure_offset", "structure_end_exclusive"):
        if key not in binding:
            raise ValueError("incomplete external candidate binding")
    if (type(binding["class_index"]) is not int or type(binding["T_index"]) is not int
            or binding["class_index"] < 0 or binding["T_index"] < 0
            or type(binding["structure_offset"]) is not int
            or type(binding["structure_end_exclusive"]) is not int
            or binding["structure_offset"] < 0):
        raise ValueError("external candidate identity invalid")
    for key in ("input_sha256", "manifest_sha256", "join_plan_sha256"):
        value = binding[key]
        if (not isinstance(value, str) or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)):
            raise ValueError("external source digest invalid")
    if binding["structure_end_exclusive"] != (binding["structure_offset"]
                                               + unit["structures"]):
        raise ValueError("published structure offset mismatch")
    if checker.field.p % 2 != 1 or checker.field.n not in (3, 5, 7):
        raise ValueError("odd-field degree 3, 5 or 7 required")


def checked_complement(unit, binding, checker):
    """Recompute the complete exceptional set from externally bound inputs."""
    _check_binding(unit, binding, checker)
    independent = checker.verify(unit, binding["quotient_form"])
    if not independent["valid"] or independent["structures"] != unit["structures"]:
        raise ValueError("independent exceptional coverage unavailable")
    return independent


def _certificate(unit, binding, checker, independent, raw_sha256):
    """Format the theorem after the exact independent checker has returned."""
    if (not independent.get("valid") or independent.get("structures") != unit["structures"]
            or independent.get("exceptional") != unit["exceptional"]
            or independent.get("generic_intervals") != len(unit["generic_intervals"])):
        raise ValueError("independent exceptional coverage unavailable")
    intervals = unit["generic_intervals"]
    count = sum(end - start for start, end in intervals)
    if count != unit["generic"] or count != unit["structures"] - independent["exceptional"]:
        raise ValueError("generic interval cardinality mismatch")
    n = checker.field.n
    return {"schema": SCHEMA, "theorem": THEOREM,
            "scope": "generic_complement_only",
            "cohort": binding["cohort"], "class_index": binding["class_index"],
            "T_index": binding["T_index"], "field": binding["field"],
            "model": binding["model"], "target": binding["target"],
            "quotient_form": binding["quotient_form"],
            "input_sha256": binding["input_sha256"],
            "manifest_sha256": binding["manifest_sha256"],
            "join_plan_sha256": binding["join_plan_sha256"],
            "structure_offset": binding["structure_offset"],
            "structure_end_exclusive": binding["structure_end_exclusive"],
            "candidate_unit_sha256": digest(unit),
            "candidate_raw_sha256": raw_sha256,
            "exceptional_ordinals_sha256": digest([row[0] for row in unit["rows"]]),
            "independent_exceptional_count": independent["exceptional"],
            "generic_intervals_sha256": digest(intervals),
            "generic_interval_count": len(intervals), "generic_count": count,
            "premises": {
                "odd_characteristic": True,
                "squarefree_binary_quartic": True,
                "exact_coefficient_q_frobenius_orbit": True,
                "pairwise_disjoint_projective_support_on_complement": True,
                "all_nonempty_subset_geometric_and_arithmetic_square_relations_absent": True,
                "radical_action": "sigma(c)=c^q; sigma(x)=x; sigma(y_i)=y_(i+1 mod n)",
                "radical_action_order": n},
            "geometric_rank": n, "arithmetic_rank": n,
            "geometrically_connected": True, "descends_to_base_field": True,
            "genus": 1 + (n - 1) * (1 << n),
            "status": "prospective_generic_theorem; collision_completeness_review_and_full_cohort_admission_pending"}


def certify(unit, binding, checker, raw_bytes):
    """Apply the generic theorem to every half-open complement interval."""
    if json.loads(raw_bytes) != unit:
        raise ValueError("candidate raw bytes differ from supplied unit")
    independent = checked_complement(unit, binding, checker)
    return _certificate(unit, binding, checker, independent,
                        hashlib.sha256(raw_bytes).hexdigest())


def certify_from_checked_review(unit, binding, checker, independent, raw_sha256):
    """Use only immediately after this checker's exact verify in a review path."""
    _check_binding(unit, binding, checker)
    if (not isinstance(raw_sha256, str) or len(raw_sha256) != 64
            or any(char not in "0123456789abcdef" for char in raw_sha256)):
        raise ValueError("candidate raw digest invalid")
    return _certificate(unit, binding, checker, independent, raw_sha256)


def certify_bound(unit, raw_bytes, binder, class_index, t_index):
    """Production entry point requires an exact published join-plan binding."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("published cohort binder required")
    binding = binder.bind(class_index, t_index)
    return certify(unit, binding, IndependentCandidateChecker(binding["field"]), raw_bytes)
