"""Cross-check source-bound fixed algebra against independent square relations.

The relation replay uses the quotient certificate checker's separate finite
field and polynomial implementation. Geometry is reported per geometric
component; a disconnected constant-field algebra has no connected-curve genus.
"""

from check_quotient_certificate import Field, square_relations
from fixed_field_multiplication import build_from_source as build_fixed
from generic_disjoint import classify, exceptional_geometry


def _rank(degree, relation_count):
    if relation_count < 1 or relation_count & (relation_count - 1):
        raise ValueError("independent relation count is not a power of two")
    return degree - (relation_count.bit_length() - 1)


def assess(field_record, forms, fixed):
    """Check rank and component geometry for a supplied exact fixed algebra."""
    field = Field(field_record)
    relations = square_relations(field, forms)
    degree = len(forms)
    geometric_rank = _rank(degree, len(relations))
    arithmetic_rank = _rank(degree, sum(is_square for _, is_square in relations))
    algebra = fixed["basis"]["algebra"]
    if (geometric_rank != algebra["geometric_rank"]
            or arithmetic_rank != algebra["arithmetic_rank"]
            or fixed["dimension"] != 1 << arithmetic_rank):
        raise ValueError("fixed algebra disagrees with independent relation replay")
    if arithmetic_rank not in (geometric_rank, geometric_rank + 1):
        raise ValueError("unexpected constant-field relation rank")
    classification = classify(field, forms)
    geometry = (classification if classification["classification"] == "generic-disjoint"
                else exceptional_geometry(field, forms))
    if geometry["geometric_squareclass_rank"] != geometric_rank:
        raise ValueError("branch geometry disagrees with independent relation replay")
    components = 1 << (arithmetic_rank - geometric_rank)
    return {
        "schema": "pext.source-fixed-geometry/v1",
        "fixed_model": fixed,
        "independent_relation_replay": {
            "geometric_relation_count": len(relations),
            "arithmetic_relation_count": sum(is_square for _, is_square in relations),
            "geometric_rank": geometric_rank,
            "arithmetic_rank": arithmetic_rank,
        },
        "geometric_component_count": components,
        "geometric_component_degree": 1 << geometric_rank,
        "geometric_component_genus": geometry["geometric_genus"],
        "geometrically_connected": components == 1,
        "connected_curve_genus": geometry["geometric_genus"] if components == 1 else None,
        "branch_geometry": geometry,
        "status": "fixed_algebra_and_component_geometry_cross_checked; independent_model_review_pending",
    }


def build_from_source(field_record, model, target, matrix, forms):
    """Bind checked component geometry to the named elliptic K-model and T."""
    checked = build_fixed(field_record, model, target, matrix, forms)
    result = assess(field_record, forms, checked["fixed"])
    result["schema"] = "pext.source-fixed-geometry/v1"
    result["source"] = checked["source"]
    result["status"] = "source_fixed_algebra_and_component_geometry_cross_checked; independent_model_review_pending"
    return result
