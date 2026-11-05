"""Bind separate algebra and character-genus replays to one source record."""

from independent_component_geometry import assess as assess_geometry
from independent_fixed_model_check import verify as verify_algebra


def verify(record, field_record, forms):
    if not isinstance(record, dict) or record.get("schema") != "pext.source-fixed-geometry/v1":
        raise ValueError("source fixed geometry record required")
    algebra = verify_algebra(record, field_record, forms)
    geometry = assess_geometry(field_record, forms)
    expected = {
        "geometric_component_count": geometry["geometric_component_count"],
        "geometric_component_degree": geometry["geometric_component_degree"],
        "geometric_component_genus": geometry["geometric_component_genus"],
        "connected_curve_genus": geometry["connected_curve_genus"],
        "geometrically_connected": geometry["geometric_component_count"] == 1,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ValueError(f"independent source geometry mismatch: {key}")
    replay = record.get("independent_relation_replay")
    if not isinstance(replay, dict) or any(
            replay.get(key) != geometry[key] for key in
            ("geometric_rank", "arithmetic_rank")):
        raise ValueError("independent source relation rank mismatch")
    branch = record.get("branch_geometry")
    if not isinstance(branch, dict) or branch.get("branch_points") != geometry["branch_points"]:
        raise ValueError("independent source branch count mismatch")
    return {"schema": "pext.independent-source-fixed-check/v1", "valid": True,
            "algebra": algebra, "geometry": geometry,
            "scope": "source generator, ambient and fixed algebra, geometric components and character genus"}
