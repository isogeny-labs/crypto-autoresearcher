"""Exact Type2 cross-tab over a fully independently reviewed candidate unit.

The Type2 root orbit necessarily overlaps a Frobenius conjugate branch set.
The independent candidate checker certifies every exceptional ordinal and
the complete generic complement, so only exceptional rows need inspection.
"""

from type2_predicate import Type2Instrument


def scan(field, unit, review):
    """Retain each signature row and its separate trace-zero predicate."""
    if field.n != 3 or field.p % 2 != 1:
        raise ValueError("Type2 unit scan requires odd cubic extension")
    rows = unit.get("rows")
    independent = review.get("independent") if isinstance(review, dict) else None
    if not isinstance(rows, list) or not isinstance(independent, dict):
        raise ValueError("full independent candidate review required")
    ordinals = [row[0] for row in rows if isinstance(row, list) and len(row) == 5]
    if (len(ordinals) != len(rows)
            or independent.get("valid") is not True
            or independent.get("structures") != unit.get("structures")
            or independent.get("exceptional") != unit.get("exceptional")
            or independent.get("geometry_checked") != len(rows)
            or review.get("geometry_ordinals") != ordinals):
        raise ValueError("Type2 requires full independently checked exceptional geometry")
    instrument = Type2Instrument(field, unit)
    signatures = []
    if unit["factor_pattern"] == [2, 2]:
        for row in rows:
            result = instrument.inspect(row[1])
            if result["signature"]:
                signatures.append({"ordinal": row[0], "matrix": row[1],
                                   "hyperelliptic_predicate": result["hyperelliptic_predicate"],
                                   "alpha": result["alpha"],
                                   "trace_zero_matrix": result["trace_zero_matrix"],
                                   "alpha_choices_checked": result["alpha_choices_checked"]})
    return {"schema": "pext.type2-unit-scan/v1",
            "status": "complete_independent_exceptional_scan; cohort_decision_pending",
            "structures": unit["structures"], "exceptional_checked": len(rows),
            "generic_excluded_by_orbit_overlap": unit["generic"],
            "factor_pattern": unit["factor_pattern"],
            "type2_signature_count": len(signatures),
            "hyperelliptic_predicate_true_count": sum(
                row["hyperelliptic_predicate"] for row in signatures),
            "hyperelliptic_predicate_false_count": sum(
                not row["hyperelliptic_predicate"] for row in signatures),
            "signature_rows": signatures}
