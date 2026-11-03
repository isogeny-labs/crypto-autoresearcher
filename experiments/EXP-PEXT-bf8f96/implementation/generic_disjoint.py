"""Exact generic branch-support certificate for a conjugate quartic family.

Pairwise disjoint squarefree supports imply independent geometric square
classes, connectedness, and genus (n-1)*2**n+1. An overlap is returned as an
exceptional case requiring the full rank/genus/descent calculation.
"""

from check_quotient_certificate import polynomial_remainder, trim


def gcd_degree(field, left, right):
    left, right = trim(left), trim(right)
    while right:
        left, right = right, polynomial_remainder(field, left, right)
    return len(left)-1


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
