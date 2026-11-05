"""Deterministic C5 unit selection from a complete certified metadata table.

This prepares a blind review roster, not an independent scientific check. The
caller must validate the metadata certificates before exposing the roster to a
second implementation; producer genus and minimum values are never inputs.
"""

import hashlib
import json
import re


HEX = re.compile(r"[0-9a-f]{64}\Z")
STATUSES = {"certified_admissible", "certified_inadmissible", "mixed", "unresolved"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _ordinals(value, structures, label):
    if (not isinstance(value, list) or any(type(x) is not int or not 0 <= x < structures
                                           for x in value)
            or value != sorted(set(value))):
        raise ValueError(f"{label} must be sorted unique structure ordinals")


def select(plan, metadata):
    """Select canonical first/lower-middle/last unit in every occupied stratum.

    Metadata is ordered one-for-one with the published join plan. Each row
    carries only certified classification and witness identities; the caller
    verifies the referenced certificate digest against retained evidence.
    """
    if (not isinstance(plan, dict) or plan.get("schema") != "pext.join-plan/v1"
            or not isinstance(plan.get("classes"), list)
            or type(plan.get("structures_per_T")) is not int
            or plan["structures_per_T"] < 1
            or not isinstance(metadata, list)):
        raise ValueError("published join plan and metadata required")
    cohort, structures = plan.get("cohort"), plan["structures_per_T"]
    expected = [(class_index, t_index, len(curve["targets"]))
                for class_index, curve in enumerate(plan["classes"])
                for t_index in range(len(curve["targets"]))]
    if len(metadata) != len(expected):
        raise ValueError("C5 metadata does not cover every canonical unit")
    strata, special, curve_counterexample = {}, {}, {}
    for position, ((class_index, t_index, torsion), row) in enumerate(zip(expected, metadata)):
        if (not isinstance(row, dict) or set(row) != {
                "cohort", "class_index", "T_index", "torsion_count", "descent_status",
                "special_j", "unit_counterexample", "curve_counterexample",
                "counterexample_ordinals", "type2_hyperelliptic_ordinals",
                "certificate_sha256"}
                or (row["cohort"], row["class_index"], row["T_index"],
                    row["torsion_count"]) != (cohort, class_index, t_index, torsion)
                or not isinstance(row["descent_status"], str)
                or row["descent_status"] not in STATUSES
                or type(row["special_j"]) is not bool
                or type(row["unit_counterexample"]) is not bool
                or type(row["curve_counterexample"]) is not bool
                or not isinstance(row["certificate_sha256"], str)
                or not HEX.fullmatch(row["certificate_sha256"])):
            raise ValueError("C5 metadata identity or certificate malformed")
        _ordinals(row["counterexample_ordinals"], structures, "counterexample")
        _ordinals(row["type2_hyperelliptic_ordinals"], structures, "Type2 witness")
        previous = special.setdefault(class_index, row["special_j"])
        if previous != row["special_j"]:
            raise ValueError("special-j flag differs within actual curve")
        previous = curve_counterexample.setdefault(class_index, row["curve_counterexample"])
        if previous != row["curve_counterexample"]:
            raise ValueError("curve counterexample flag differs within actual curve")
        key = (cohort, torsion, t_index, row["descent_status"])
        strata.setdefault(key, []).append(position)
    selected = {}
    for key, positions in sorted(strata.items()):
        for label, position in (("first", positions[0]),
                                ("middle", positions[(len(positions)-1)//2]),
                                ("last", positions[-1])):
            selected.setdefault(position, set()).add(label + "_in_stratum")
    for position, row in enumerate(metadata):
        for flag, reason in ((row["special_j"], "special_j"),
                             (row["unit_counterexample"] or row["curve_counterexample"]
                              or bool(row["counterexample_ordinals"]), "counterexample"),
                             (bool(row["type2_hyperelliptic_ordinals"]), "type2_witness")):
            if flag:
                selected.setdefault(position, set()).add(reason)
    roster = []
    for position in sorted(selected):
        row = metadata[position]
        roster.append({"cohort": cohort, "class_index": row["class_index"],
                       "T_index": row["T_index"], "torsion_count": row["torsion_count"],
                       "descent_status": row["descent_status"],
                       "certificate_sha256": row["certificate_sha256"],
                       "reasons": sorted(selected[position]),
                       "unit_counterexample": row["unit_counterexample"],
                       "curve_counterexample": row["curve_counterexample"],
                       "counterexample_ordinals": row["counterexample_ordinals"],
                       "type2_hyperelliptic_ordinals": row[
                           "type2_hyperelliptic_ordinals"]})
    return {"schema": "pext.c5-selection/v1", "status": "prospective_blind_roster",
            "cohort": cohort, "join_plan_sha256": hashlib.sha256(canonical(plan)).hexdigest(),
            "metadata_sha256": hashlib.sha256(canonical(metadata)).hexdigest(),
            "unit_count": len(expected), "stratum_count": len(strata),
            "selected_count": len(roster), "selected_units": roster}
