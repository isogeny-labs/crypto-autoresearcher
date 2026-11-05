"""Coefficient-aware square-class relation ledger for conjugate quartics.

Over an odd finite field, a rational-function square class is its projective
odd-valuation support plus the square class of its leading coefficient.
This computes those two coordinates for every subset of a verified Frobenius
orbit. A relation ledger alone is not a Frobenius descent/lift certificate.
"""

from generic_disjoint import classify, monic, symmetric_difference
from check_quotient_certificate import trim


IDENTITY = ((1,), False)


def coefficient_bit(field, coefficient):
    """Return 0 for a square, 1 for a nonsquare in the source field."""
    field.element(coefficient)
    if coefficient == 0 or field.p % 2 != 1:
        raise ValueError("odd-field nonzero coefficient required")
    symbol = field.power(coefficient, (field.size-1)//2)
    if symbol == 1:
        return 0
    if symbol == field.sub(0, 1):
        return 1
    raise ValueError("coefficient Euler character invalid")


def ledger(field, forms):
    """Enumerate exact geometric and arithmetic relations, n=3,5,7."""
    classification = classify(field, forms)
    n = len(forms)
    supports = []
    bits = []
    for form in forms:
        finite = trim(form)
        supports.append((monic(field, finite), len(finite) == 4))
        bits.append(coefficient_bit(field, finite[-1]))
    rows = []
    geometric_relations = arithmetic_relations = 0
    seen_geometric = set()
    seen_arithmetic = set()
    for mask in range(1 << n):
        support, bit = IDENTITY, 0
        indices = []
        for index in range(n):
            if mask & (1 << index):
                support = symmetric_difference(field, support, supports[index])
                bit ^= bits[index]
                indices.append(index)
        geometric = support == IDENTITY
        arithmetic = geometric and bit == 0
        geometric_relations += geometric
        arithmetic_relations += arithmetic
        seen_geometric.add(support)
        seen_arithmetic.add((support, bit))
        rows.append({"mask": mask, "indices": indices,
                     "projective_support": [list(support[0]), support[1]],
                     "constant_nonsquare": bool(bit),
                     "geometric_relation": geometric,
                     "arithmetic_relation": arithmetic})
    geometric_rank = len(seen_geometric).bit_length()-1
    arithmetic_rank = len(seen_arithmetic).bit_length()-1
    if (len(seen_geometric) != 1 << geometric_rank
            or len(seen_arithmetic) != 1 << arithmetic_rank
            or geometric_relations != 1 << (n-geometric_rank)
            or arithmetic_relations != 1 << (n-arithmetic_rank)
            or arithmetic_rank not in (geometric_rank, geometric_rank+1)):
        raise ValueError("square-class relation cardinality")
    # Frobenius rotates the inputs and preserves square/nonsquare constants.
    for row in rows:
        rotated = ((row["mask"] << 1) | (row["mask"] >> (n-1))) & ((1 << n)-1)
        other = rows[rotated]
        if (row["geometric_relation"] != other["geometric_relation"]
                or row["arithmetic_relation"] != other["arithmetic_relation"]):
            raise ValueError("Frobenius does not preserve relation kernel")
    return {"schema": "pext.squareclass-relations/v1", "degree": n,
            "classification": classification["classification"],
            "coefficient_nonsquare": [bool(bit) for bit in bits],
            "geometric_rank": geometric_rank,
            "arithmetic_rank": arithmetic_rank,
            "constant_nonsquare_relation": arithmetic_rank > geometric_rank,
            "relations": rows,
            "status": "relation_ledger_only; Frobenius_lift_and_descent_pending"}
