"""Bind one exceptional candidate row to its independently checked source model.

This is a pure prospective adapter. The supervised stage must decide which
rows to retain, enforce its deadline, and write the resulting certificate.
"""

from candidate_binding import CandidateBinder
from fixed_model_geometry import build_from_source as build_model
from independent_source_fixed_check import verify as verify_model
from independent_source_map_check import verify as verify_source_map
from independent_transversal import IndependentTransversal
from source_map_binding import certify_bound as certify_source_bound
from target_transport import verified_field
import json


def assess(binder, class_index, t_index, row):
    """Verify one sealed exceptional row against the published curve/T/ordinal."""
    if not isinstance(binder, CandidateBinder) or binder.plan_path is None:
        raise ValueError("published cohort binder required")
    if (not isinstance(row, list) or len(row) != 5
            or type(row[0]) is not int or type(row[1]) is not list
            or len(row[1]) != 4 or any(type(x) is not int for x in row[1])
            or any(type(x) is not int for x in row[2:])):
        raise ValueError("exceptional row shape")
    ordinal, matrix, expected_rank, expected_branches, expected_genus = row
    binding = binder.bind(class_index, t_index)
    source_map = certify_source_bound(binder, class_index, t_index, ordinal, matrix)
    field_record = binding["field"]
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(",", ":")))
    forms = [source_map["moved_form"]]
    for _ in range(field.n - 1):
        forms.append([field.power(value, field.p) for value in forms[-1]])
    model = build_model(field_record, binding["model"], binding["target"], matrix, forms)
    embedded_source = model["source"]["source"]["source_map"]
    if any(embedded_source.get(key) != source_map[key] for key in
           ("field", "model", "target", "matrix", "source_form", "moved_form",
            "determinant", "x_map", "y_map")):
        raise ValueError("source model differs from published ordinal binding")
    if (source_map.get("cohort") != binder.cohort
            or source_map.get("class_index") != class_index
            or source_map.get("T_index") != t_index
            or source_map.get("structure_ordinal") != ordinal
            or source_map.get("join_plan_sha256") != binder.plan_sha256
            or source_map.get("structure_offset") != binding["structure_offset"]
            or matrix != IndependentTransversal(field_record).matrix(ordinal)):
        raise ValueError("independent published class/T/ordinal binding mismatch")
    source_check = verify_source_map(embedded_source, field_record,
                                     binding["model"], binding["target"], matrix)
    if embedded_source.get("source_form") != binding["quotient_form"]:
        raise ValueError("independent published quotient form mismatch")
    independent = verify_model(model, field_record, forms)
    geometry = independent["geometry"]
    if model["branch_geometry"]["classification"] != "exceptional":
        raise ValueError("source-fixed unit requires an exceptional row")
    if (geometry["geometric_rank"] != expected_rank
            or geometry["branch_points"] != expected_branches
            or geometry["geometric_component_genus"] != expected_genus):
        raise ValueError("exceptional row differs from independent component geometry")
    return {"schema": "pext.source-fixed-unit/v1", "cohort": binder.cohort,
            "class_index": class_index, "T_index": t_index,
            "structure_ordinal": ordinal, "matrix": matrix,
            "join_plan_sha256": binder.plan_sha256,
            "source_fixed_model": model, "independent_check": independent,
            "independent_source_map_check": source_check,
            "geometrically_connected": geometry["geometric_component_count"] == 1,
            "connected_curve_genus": geometry["connected_curve_genus"],
            "status": "one_exceptional_source_fixed_row_checked; full_descent_and_minimum_pending"}
