"""Assemble a complete prospective C5 table from checked geometric rows.

The output deliberately leaves descent unresolved and does not decide a
control-valid scientific counterexample. It cannot satisfy C5 on its own.
"""

import hashlib
import re

from candidate_batch import expected_units
from c5_selection import canonical
from check_quotient_certificate import Field
from curve_special_j import special_j


HEX = re.compile(r"[0-9a-f]{64}\Z")


def _hash(value, label):
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"{label} SHA-256 missing or malformed")
    return value


def assemble(plan, curves):
    """Bind every class/T unit to its retained geometric and Type2 identities."""
    if (not isinstance(plan, dict) or plan.get("schema") != "pext.join-plan/v1"
            or not isinstance(curves, list)
            or not isinstance(plan.get("classes"), list)
            or len(curves) != len(plan["classes"]) or not plan["classes"]):
        raise ValueError("complete join plan and geometric curve rows required")
    field = Field(plan["field"])
    units = expected_units(plan)
    structures = plan["structures_per_T"]
    cohort = plan["cohort"]
    rows, position = [], 0
    type2_digest = None
    for class_index, (expected_curve, curve) in enumerate(zip(plan["classes"], curves)):
        targets = expected_curve["targets"]
        if (not isinstance(curve, dict) or curve.get("cohort") != cohort
                or curve.get("class_index") != class_index
                or curve.get("model") != expected_curve["model"]
                or curve.get("T_count") != len(targets)
                or not isinstance(curve.get("units"), list)
                or len(curve["units"]) != len(targets)):
            raise ValueError("geometric curve differs from canonical join plan")
        is_special = special_j(field, expected_curve["model"])
        for t_index, unit in enumerate(curve["units"]):
            expected_unit = units[position]
            position += 1
            if (not isinstance(unit, dict) or unit.get("T_index") != t_index
                    or unit.get("unit_name") != expected_unit["name"]
                    or unit.get("structures") != structures):
                raise ValueError("geometric unit differs from canonical slot")
            raw_sha = _hash(unit.get("candidate_unit_sha256"), "candidate unit")
            witnesses = unit.get("type2_hyperelliptic_ordinals")
            if (not isinstance(witnesses, list)
                    or any(type(value) is not int or not 0 <= value < structures
                           for value in witnesses)
                    or witnesses != sorted(set(witnesses))):
                raise ValueError("retained Type2 witness ordinal list invalid")
            if field.n == 3:
                digest = _hash(unit.get("type2_check_sha256"), "Type2 check")
                if type2_digest is None:
                    type2_digest = digest
                elif digest != type2_digest:
                    raise ValueError("Type2 batch hash differs within cohort")
                if (type(unit.get("hyperelliptic_predicate_true_count")) is not int
                        or len(witnesses) != unit["hyperelliptic_predicate_true_count"]):
                    raise ValueError("retained Type2 witness count differs")
            elif witnesses or "type2_check_sha256" in unit:
                raise ValueError("Type2 witnesses on noncubic cohort")
            mismatch = unit.get("branch_type_mismatch_count")
            spectrum = unit.get("geometric_spectrum_violation_count")
            if (type(mismatch) is not int or mismatch not in (0, 1)
                    or spectrum is not None and (type(spectrum) is not int or spectrum < 0)):
                raise ValueError("geometric discrepancy counts invalid")
            rows.append({"cohort": cohort, "class_index": class_index,
                         "T_index": t_index, "torsion_count": len(targets),
                         "descent_status": "unresolved", "special_j": is_special,
                         "unit_counterexample": bool(mismatch or spectrum),
                         "curve_counterexample": False,
                         "counterexample_ordinals": [],
                         "type2_hyperelliptic_ordinals": witnesses,
                         "candidate_unit_sha256": raw_sha})
    if position != len(units):
        raise ValueError("C5 preview omitted canonical units")
    return {"schema": "pext.c5-metadata-preview/v1",
            "status": "complete_geometric_identity; descent_and_controls_unresolved",
            "cohort": cohort, "join_plan_sha256": hashlib.sha256(canonical(plan)).hexdigest(),
            "geometric_rows_sha256": hashlib.sha256(canonical(curves)).hexdigest(),
            "unit_count": len(rows), "rows": rows}
