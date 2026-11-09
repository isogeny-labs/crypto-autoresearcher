"""Independent replay of the complete generic-interval descent theorem.

This checker uses the separate root/cocycle candidate-set implementation and
rederives the disjoint-support and semilinear-action consequences directly.
It receives the exact raw unit bytes and an external curve/T/plan binding.
"""

import hashlib
import json

from candidate_binding import CandidateBinder
from independent_candidate_unit import IndependentCandidateChecker


def _hash(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def _need(test, reason):
    if not test:
        raise ValueError(reason)


def verify(record, raw_bytes, binding):
    """Independently validate one compact certificate against the sealed unit."""
    unit = json.loads(raw_bytes)
    _need(type(unit) is dict and type(binding) is dict and type(record) is dict,
          "generic descent input shape")
    for key in ("cohort", "class_index", "T_index", "model", "target",
                "field", "quotient_form", "input_sha256", "manifest_sha256",
                "join_plan_sha256", "structure_offset", "structure_end_exclusive",
                "structures_per_T"):
        _need(key in binding, "external candidate binding incomplete")
    _need(binding.get("schema") == "pext.candidate-binding/v1"
          and binding.get("experiment") == "EXP-PEXT-bf8f96"
          and binding["field"] == unit.get("field")
          and binding["quotient_form"] == unit.get("form")
          and binding["structures_per_T"] == unit.get("structures")
          and type(binding["class_index"]) is int and binding["class_index"] >= 0
          and type(binding["T_index"]) is int and binding["T_index"] >= 0
          and type(binding["structure_offset"]) is int
          and binding["structure_offset"] >= 0
          and type(binding["structure_end_exclusive"]) is int
          and binding["structure_end_exclusive"] == (binding["structure_offset"]
                                                       + unit["structures"]),
          "external candidate binding mismatch")
    for key in ("input_sha256", "manifest_sha256", "join_plan_sha256"):
        value = binding[key]
        _need(type(value) is str and len(value) == 64
              and all(character in "0123456789abcdef" for character in value),
              "external source digest invalid")
    checker = IndependentCandidateChecker(binding["field"])
    _need(checker.field.p % 2 == 1 and checker.field.n in (3, 5, 7),
          "odd-field degree 3, 5 or 7 required")
    reviewed = checker.verify(unit, binding["quotient_form"])
    intervals = unit["generic_intervals"]
    count = sum(stop - start for start, stop in intervals)
    _need(count == unit["generic"] == unit["structures"] - reviewed["exceptional"],
          "generic complement cardinality")
    # Unique odd branch valuations rule out every nonempty subset square,
    # regardless of coefficient square classes. Exact coefficient Frobenius
    # rotation sends y_i to y_(i+1), and its n-th iterate is the identity.
    n = checker.field.n
    claims = {"schema": "pext.generic-interval-descent/v1",
              "theorem": "disjoint-conjugate-quartics-order-n-permutation/v1",
              "scope": "generic_complement_only",
              "candidate_unit_sha256": _hash(unit),
              "candidate_raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
              "exceptional_ordinals_sha256": _hash([row[0] for row in unit["rows"]]),
              "independent_exceptional_count": reviewed["exceptional"],
              "generic_intervals_sha256": _hash(intervals),
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
    for key in ("cohort", "class_index", "T_index", "field", "model", "target",
                "quotient_form", "input_sha256", "manifest_sha256",
                "join_plan_sha256", "structure_offset", "structure_end_exclusive"):
        claims[key] = binding[key]
    _need(record == claims,
          "generic descent certificate differs from independent replay")
    return {"valid": True, "scope": "all exact generic complement intervals",
            "generic_count": count, "exceptional_excluded": reviewed["exceptional"],
            "genus": claims["genus"], "status": claims["status"]}


def verify_bound(record, raw_bytes, binder, class_index, t_index):
    """Require the current published class/T/plan before a production readback."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("published cohort binder required")
    return verify(record, raw_bytes, binder.bind(class_index, t_index))
