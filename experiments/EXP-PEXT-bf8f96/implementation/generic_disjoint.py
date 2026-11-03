"""Exact generic branch-support certificate for a conjugate quartic family.

Pairwise disjoint squarefree supports imply independent geometric square
classes, connectedness, and genus (n-1)*2**n+1. An overlap is returned as an
exceptional case requiring the full rank/genus/descent calculation.
"""

from check_quotient_certificate import polynomial_mul, polynomial_remainder, trim


def gcd_degree(field, left, right):
    left, right = trim(left), trim(right)
    while right:
        left, right = right, polynomial_remainder(field, left, right)
    return len(left)-1


def monic(field, polynomial):
    polynomial = trim(polynomial)
    if not polynomial:
        raise ValueError("zero branch polynomial")
    return tuple(field.div(value, polynomial[-1]) for value in polynomial)


def exact_quotient(field, dividend, divisor):
    dividend, divisor = list(dividend), list(divisor)
    quotient = [0] * (len(dividend) - len(divisor) + 1)
    while dividend and len(dividend) >= len(divisor):
        offset = len(dividend) - len(divisor)
        scalar = field.div(dividend[-1], divisor[-1])
        quotient[offset] = scalar
        for i, value in enumerate(divisor):
            dividend[offset+i] = field.sub(dividend[offset+i], field.mul(scalar, value))
        dividend = trim(dividend)
    if dividend:
        raise ValueError("nonexact support division")
    return tuple(trim(quotient))


def support_gcd(field, left, right):
    left, right = list(left), list(right)
    while right:
        left, right = right, polynomial_remainder(field, left, right)
    return monic(field, left)


def symmetric_difference(field, left, right):
    """XOR of two squarefree projective branch supports."""
    gcd = support_gcd(field, left[0], right[0])
    a = exact_quotient(field, left[0], gcd)
    b = exact_quotient(field, right[0], gcd)
    return (monic(field, polynomial_mul(field, a, b)), left[1] ^ right[1])


def exceptional_geometry(field, forms):
    """Exact geometric rank/genus of a verified overlapping conjugate family.

    This counts branch parity over the algebraic closure. It deliberately does
    not decide coefficient square classes, descent or admissible minima.
    """
    outcome = classify(field, forms)
    if outcome["classification"] != "exceptional":
        raise ValueError("exceptional geometry requires an overlap")
    supports = [(monic(field, trim(form)), form[4] == 0) for form in forms]
    identity = ((1,), False)
    span = {identity}
    for support in supports:
        span |= {symmetric_difference(field, member, support) for member in span}
    if len(span) & (len(span)-1):
        raise ValueError("support span cardinality")
    rank = len(span).bit_length()-1
    union = (1,)
    for polynomial, _ in supports:
        gcd = support_gcd(field, union, polynomial)
        union = monic(field, polynomial_mul(field, union,
                                            exact_quotient(field, polynomial, gcd)))
    branch_points = len(union)-1 + int(any(infinity for _, infinity in supports))
    if rank == 1:
        genus = (branch_points-2)//2
    else:
        genus = 1+(1 << (rank-2))*(branch_points-4)
    character_sum = sum((len(polynomial)-1+int(infinity)-2)//2
                        for polynomial, infinity in span if (polynomial, infinity) != identity)
    if genus != character_sum:
        raise ValueError("exceptional genus character-sum mismatch")
    if rank < 1 or branch_points < 4 or genus < 0:
        raise ValueError("invalid exceptional genus")
    return {"classification": "exceptional", "overlaps": outcome["overlaps"],
            "geometric_squareclass_rank": rank, "branch_points": branch_points,
            "connected": True, "geometric_genus": genus}


def squarefree(field, form):
    if type(form) is not list or len(form) != 5:
        raise ValueError("binary quartic shape")
    for value in form:
        field.element(value)
    finite = trim(form)
    if len(finite) not in (4, 5):
        raise ValueError("multiple branch at infinity or invalid degree")
    derivative = trim([field.mul(i % field.p, finite[i]) for i in range(1, len(finite))])
    if gcd_degree(field, finite, derivative) != 0:
        raise ValueError("repeated finite branch root")
    return finite


def classify(field, forms):
    if type(forms) is not list or len(forms) not in (3, 5, 7) or len(forms) != field.n:
        raise ValueError("requires degree-n conjugate quartics, n=3,5,7")
    finite = [squarefree(field, form) for form in forms]
    for i, form in enumerate(forms):
        expected = [field.power(value, field.p) for value in form]
        if forms[(i+1) % len(forms)] != expected:
            raise ValueError("Frobenius conjugate sequence mismatch")
    overlaps = []
    for i in range(len(forms)):
        for j in range(i+1, len(forms)):
            infinity = forms[i][4] == 0 and forms[j][4] == 0
            finite_degree = gcd_degree(field, finite[i], finite[j])
            if infinity or finite_degree:
                overlaps.append({"left": i, "right": j,
                                 "finite_gcd_degree": finite_degree,
                                 "shared_infinity": infinity})
    if overlaps:
        return {"classification": "exceptional", "overlaps": overlaps}
    n = len(forms)
    return {"classification": "generic-disjoint", "overlaps": [],
            "geometric_squareclass_rank": n, "arithmetic_squareclass_rank": n,
            "branch_points": 4*n, "connected": True,
            "geometric_genus": (n-1)*2**n+1}
