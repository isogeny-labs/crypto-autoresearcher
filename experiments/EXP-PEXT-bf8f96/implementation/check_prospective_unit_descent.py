"""Independent full-row replay of one prospective unit descent summary."""

import hashlib
import json
from collections import Counter

from check_generic_interval_descent import verify as verify_generic


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def verify(record, raw_bytes, binding, review):
    """Recompute every exceptional square class and the entire compact summary."""
    if (not isinstance(record, dict) or not isinstance(raw_bytes, bytes)
            or not isinstance(binding, dict) or not isinstance(review, dict)):
        raise ValueError("prospective unit check input shape")
    unit = json.loads(raw_bytes)
    if not isinstance(unit, dict) or not isinstance(review.get("generic_descent"), dict):
        raise ValueError("prospective unit or generic certificate missing")
    checked = verify_generic(review["generic_descent"], raw_bytes, binding,
                             full_geometry=True,
                             generic_ordinals=review.get("generic_ordinals", ()))
    rows = unit["rows"]
    squareclasses = unit["exceptional_squareclasses"]
    if (review.get("raw_sha256") != hashlib.sha256(raw_bytes).hexdigest()
            or review.get("independent") != checked["independent"]
            or review.get("geometry_ordinals") != [row[0] for row in rows]
            or len(squareclasses) != len(rows)
            or checked["geometry_checked"] != len(rows)
            or checked["arithmetic_checked"] != len(rows)):
        raise ValueError("prospective full independent review differs from sealed unit")
    ranks = Counter((row[2], entry[0]) for row, entry in zip(rows, squareclasses))
    connected_exceptional = sum(count for (geometric, arithmetic), count in ranks.items()
                                if geometric == arithmetic)
    connected_genera = [row[4] for row, entry in zip(rows, squareclasses)
                        if row[2] == entry[0]]
    if unit["generic"]:
        connected_genera.append(checked["genus"])
    if (unit["exceptional"] + unit["generic"] != unit["structures"]
            or checked["generic_count"] != unit["generic"]
            or checked["exceptional_excluded"] != unit["exceptional"]):
        raise ValueError("prospective unit coverage differs from independent replay")
    expected = {
        "schema": "pext.prospective-unit-descent/v1",
        "status": "prospective_component_geometry; exceptional_descent_reviewer_and_cohort_admission_pending",
        "descent_status": "unresolved",
        "cohort": binding["cohort"], "class_index": binding["class_index"],
        "T_index": binding["T_index"],
        "join_plan_sha256": binding["join_plan_sha256"],
        "candidate_raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "independent_review_sha256": _hash(review),
        "generic_certificate_sha256": _hash(review["generic_descent"]),
        "exceptional_squareclasses_sha256": _hash(squareclasses),
        "structures": unit["structures"], "exceptional_count": len(rows),
        "generic_count": unit["generic"],
        "covered_count": len(rows) + unit["generic"],
        "exceptional_rank_pairs": [
            {"geometric_rank": geometric, "arithmetic_rank": arithmetic,
             "count": ranks[geometric, arithmetic]}
            for geometric, arithmetic in sorted(ranks)],
        "connected_exceptional_count": connected_exceptional,
        "disconnected_exceptional_count": len(rows) - connected_exceptional,
        "connected_generic_count": unit["generic"],
        "prospective_connected_genus_minimum": (
            min(connected_genera) if connected_genera else None),
    }
    if record != expected:
        raise ValueError("prospective unit descent summary differs from independent replay")
    return {"valid": True, "scope": "sealed unit, full exceptional square classes and generic complement",
            "covered_count": expected["covered_count"],
            "prospective_connected_genus_minimum": expected[
                "prospective_connected_genus_minimum"],
            "status": expected["status"]}
