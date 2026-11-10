"""Compact, prospective connected-component geometry for one sealed unit.

The exceptional square-class vector supplies component counts, not a checked
order-n descent action. C5 and admissible minima remain unresolved.
"""

import hashlib
import json
from collections import Counter


SCHEMA = "pext.prospective-unit-descent/v1"
STATUS = "prospective_component_geometry; exceptional_descent_reviewer_and_cohort_admission_pending"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def summarize(raw_bytes, binding, review):
    """Aggregate only a fully reviewed exact unit and its generic certificate."""
    if not isinstance(raw_bytes, bytes) or not isinstance(binding, dict) or not isinstance(review, dict):
        raise ValueError("prospective unit inputs missing")
    unit = json.loads(raw_bytes)
    if not isinstance(unit, dict):
        raise ValueError("sealed candidate unit must be an object")
    n = binding.get("field", {}).get("degree")
    if (binding.get("schema") != "pext.candidate-binding/v1"
            or binding.get("experiment") != "EXP-PEXT-bf8f96"
            or n not in (3, 5, 7)
            or unit.get("field") != binding["field"]
            or unit.get("form") != binding.get("quotient_form")
            or unit.get("structures") != binding.get("structures_per_T")):
        raise ValueError("prospective unit external binding mismatch")
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    rows = unit.get("rows")
    squareclasses = unit.get("exceptional_squareclasses")
    independent = review.get("independent")
    generic = review.get("generic_descent")
    if (not isinstance(rows, list) or not isinstance(squareclasses, list)
            or len(squareclasses) != len(rows)
            or not isinstance(independent, dict) or not isinstance(generic, dict)
            or review.get("raw_sha256") != raw_sha
            or review.get("geometry_ordinals") != [row[0] for row in rows]
            or independent.get("valid") is not True
            or independent.get("structures") != unit["structures"]
            or independent.get("exceptional") != len(rows)
            or len(rows) != unit.get("exceptional")
            or independent.get("geometry_checked") != len(rows)
            or independent.get("arithmetic_checked") != len(rows)
            or generic.get("candidate_raw_sha256") != raw_sha
            or generic.get("candidate_unit_sha256") != digest(unit)
            or generic.get("generic_count") != unit.get("generic")
            or generic.get("generic_interval_count") != len(unit.get("generic_intervals", []))
            or generic.get("genus") != 1 + (n - 1) * (1 << n)):
        raise ValueError("complete independent review or generic certificate absent")
    for key in ("cohort", "class_index", "T_index", "field", "model", "target",
                "quotient_form", "input_sha256", "manifest_sha256",
                "join_plan_sha256", "structure_offset", "structure_end_exclusive"):
        if key not in binding or key not in generic or generic[key] != binding[key]:
            raise ValueError("generic certificate external binding mismatch")
    generic_expected = {
        "schema": "pext.generic-interval-descent/v1",
        "theorem": "disjoint-conjugate-quartics-order-n-permutation/v1",
        "scope": "generic_complement_only",
        "candidate_raw_sha256": raw_sha,
        "candidate_unit_sha256": digest(unit),
        "exceptional_ordinals_sha256": digest([row[0] for row in rows]),
        "independent_exceptional_count": len(rows),
        "generic_intervals_sha256": digest(unit["generic_intervals"]),
        "generic_interval_count": len(unit["generic_intervals"]),
        "generic_count": unit["generic"],
        "geometric_rank": n, "arithmetic_rank": n,
        "geometrically_connected": True, "descends_to_base_field": True,
        "genus": 1 + (n - 1) * (1 << n),
        "status": "prospective_generic_theorem; collision_completeness_review_and_full_cohort_admission_pending",
        "premises": {
            "odd_characteristic": True, "squarefree_binary_quartic": True,
            "exact_coefficient_q_frobenius_orbit": True,
            "pairwise_disjoint_projective_support_on_complement": True,
            "all_nonempty_subset_geometric_and_arithmetic_square_relations_absent": True,
            "radical_action": "sigma(c)=c^q; sigma(x)=x; sigma(y_i)=y_(i+1 mod n)",
            "radical_action_order": n},
    }
    if (set(generic) != set(generic_expected) | {
            "cohort", "class_index", "T_index", "field", "model", "target",
            "quotient_form", "input_sha256", "manifest_sha256",
            "join_plan_sha256", "structure_offset", "structure_end_exclusive"}
            or any(generic.get(key) != value for key, value in generic_expected.items())):
        raise ValueError("checked generic certificate differs from sealed unit")
    if (unit["exceptional"] + unit["generic"] != unit["structures"]
            or sum(stop-start for start, stop in unit["generic_intervals"]) != unit["generic"]):
        raise ValueError("prospective unit coverage mismatch")
    rank_pairs = Counter()
    connected_genera = []
    for row, entry in zip(rows, squareclasses):
        if (not isinstance(row, list) or len(row) != 5
                or not isinstance(entry, list) or len(entry) != 2
                or type(row[2]) is not int or type(row[4]) is not int
                or type(entry[0]) is not int or type(entry[1]) is not bool
                or not 1 <= row[2] <= n or entry[0] not in (row[2], row[2] + 1)
                or entry[1] != (entry[0] > row[2])):
            raise ValueError("exceptional arithmetic vector malformed")
        rank_pairs[row[2], entry[0]] += 1
        if entry[0] == row[2]:
            connected_genera.append(row[4])
    if unit["generic"]:
        connected_genera.append(generic["genus"])
    connected_exceptional = sum(count for (geometric, arithmetic), count in rank_pairs.items()
                                if geometric == arithmetic)
    disconnected_exceptional = len(rows) - connected_exceptional
    return {"schema": SCHEMA, "status": STATUS, "descent_status": "unresolved",
            "cohort": binding["cohort"], "class_index": binding["class_index"],
            "T_index": binding["T_index"], "join_plan_sha256": binding["join_plan_sha256"],
            "candidate_raw_sha256": raw_sha,
            "independent_review_sha256": digest(review),
            "generic_certificate_sha256": digest(generic),
            "exceptional_squareclasses_sha256": digest(squareclasses),
            "structures": unit["structures"], "exceptional_count": len(rows),
            "generic_count": unit["generic"], "covered_count": len(rows) + unit["generic"],
            "exceptional_rank_pairs": [
                {"geometric_rank": geometric, "arithmetic_rank": arithmetic,
                 "count": rank_pairs[geometric, arithmetic]}
                for geometric, arithmetic in sorted(rank_pairs)],
            "connected_exceptional_count": connected_exceptional,
            "disconnected_exceptional_count": disconnected_exceptional,
            "connected_generic_count": unit["generic"],
            "prospective_connected_genus_minimum": (
                min(connected_genera) if connected_genera else None)}
