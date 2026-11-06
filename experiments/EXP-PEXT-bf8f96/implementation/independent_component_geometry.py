"""Independent character-sum geometry for conjugate quartic square classes.

This uses the quotient certificate checker's separate field arithmetic and
does not import the producer's support-span or genus implementation.
"""

from check_quotient_certificate import (Field, polynomial_mul,
                                        polynomial_remainder, square_relations,
                                        trim)


IDENTITY = ((1,), False)


def monic(field, values):
    values = trim(values)
    if not values:
        raise ValueError("zero branch support")
    inverse = field.div(1, values[-1])
    return tuple(field.mul(value, inverse) for value in values)


def gcd(field, left, right):
    left, right = list(left), list(right)
    while right:
        left, right = right, polynomial_remainder(field, left, right)
    return monic(field, left)


def quotient(field, dividend, divisor):
    dividend, divisor = trim(dividend), trim(divisor)
    answer = [0] * (len(dividend) - len(divisor) + 1)
    while len(dividend) >= len(divisor):
        index = len(dividend) - len(divisor)
        factor = field.div(dividend[-1], divisor[-1])
        answer[index] = factor
        for position, value in enumerate(divisor):
            dividend[index + position] = field.sub(
                dividend[index + position], field.mul(factor, value))
        dividend = trim(dividend)
    if dividend:
        raise ValueError("support quotient is not exact")
    return trim(answer)


def xor_support(field, left, right):
    common = gcd(field, left[0], right[0])
    finite = polynomial_mul(field, quotient(field, left[0], common),
                            quotient(field, right[0], common))
    return monic(field, finite), left[1] ^ right[1]


def rank(cardinality):
    if cardinality < 1 or cardinality & (cardinality - 1):
        raise ValueError("square-class span cardinality")
    return cardinality.bit_length() - 1


def assess(field_record, forms):
    """Return independent geometric components and character-sum genus."""
    field = Field(field_record)
    if not isinstance(forms, list) or len(forms) != field.n or field.n not in (3, 5, 7):
        raise ValueError("degree-n conjugate quartics required")
    # Independent certificate checker validates coefficient shape and squarefreeness.
    checker_relations = square_relations(field, forms)
    supports = []
    bits = []
    for index, form in enumerate(forms):
        if forms[(index + 1) % field.n] != [field.power(value, field.p) for value in form]:
            raise ValueError("nonconjugate quartic family")
        finite = trim(form)
        supports.append((monic(field, finite), len(finite) == 4))
        bits.append(field.power(finite[-1], (field.size - 1) // 2) != 1)
    geometric_span = set()
    arithmetic_span = set()
    replay_relations = []
    for mask in range(1 << field.n):
        support, bit = IDENTITY, False
        for index in range(field.n):
            if mask & (1 << index):
                support = xor_support(field, support, supports[index])
                bit ^= bits[index]
        geometric_span.add(support)
        arithmetic_span.add((support, bit))
        if support == IDENTITY:
            replay_relations.append((mask, not bit))
    if replay_relations != [tuple(row) for row in checker_relations]:
        raise ValueError("independent square-relation check disagrees")
    geometric_rank, arithmetic_rank = rank(len(geometric_span)), rank(len(arithmetic_span))
    if arithmetic_rank not in (geometric_rank, geometric_rank + 1):
        raise ValueError("unexpected constant-field rank")
    character_genera = []
    for finite, infinity in sorted(geometric_span):
        if (finite, infinity) == IDENTITY:
            continue
        branches = len(finite) - 1 + int(infinity)
        if branches < 2 or branches % 2:
            raise ValueError("quadratic character branch count")
        character_genera.append((branches - 2) // 2)
    genus = sum(character_genera)
    union = IDENTITY
    for support in supports:
        common = gcd(field, union[0], support[0])
        finite = polynomial_mul(field, union[0], quotient(field, support[0], common))
        union = (monic(field, finite), union[1] or support[1])
    branch_points = len(union[0]) - 1 + int(union[1])
    r_h = ((branch_points - 2) // 2 if geometric_rank == 1 else
           1 + (1 << (geometric_rank - 2)) * (branch_points - 4))
    if genus != r_h or genus < 0:
        raise ValueError("character genus and Riemann-Hurwitz disagree")
    components = 1 << (arithmetic_rank - geometric_rank)
    return {"schema": "pext.independent-component-geometry/v1",
            "geometric_rank": geometric_rank, "arithmetic_rank": arithmetic_rank,
            "geometric_component_count": components,
            "geometric_component_degree": 1 << geometric_rank,
            "geometric_component_genus": genus,
            "connected_curve_genus": genus if components == 1 else None,
            "branch_points": branch_points,
            "character_count": len(character_genera),
            "status": "independent_character_sum_and_RH_geometry_checked"}
