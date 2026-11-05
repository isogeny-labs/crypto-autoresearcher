"""Exact special-j stratum flag for a named odd-characteristic K-model.

The model is y^2 = x^3 + a2*x^2 + a4*x + a6. The returned invariant only
classifies j=0 or j=1728; it never replaces the actual K-isomorphism identity.
"""

from check_quotient_certificate import Field


def special_j(field, model):
    if not isinstance(field, Field) or not isinstance(model, list) or len(model) != 3:
        raise ValueError("named field and three-coefficient model required")
    a2, a4, a6 = (field.element(value) for value in model)
    f = field
    const = lambda value: value % f.p
    b2 = f.mul(const(4), a2)
    b4 = f.mul(const(2), a4)
    b6 = f.mul(const(4), a6)
    b8 = f.sub(f.mul(const(4), f.mul(a2, a6)), f.mul(a4, a4))
    c4 = f.sub(f.mul(b2, b2), f.mul(const(24), b4))
    delta = f.sub(0, f.mul(f.mul(b2, b2), b8))
    delta = f.sub(delta, f.mul(const(8), f.power(b4, 3)))
    delta = f.sub(delta, f.mul(const(27), f.mul(b6, b6)))
    delta = f.add(delta, f.mul(const(9), f.mul(f.mul(b2, b4), b6)))
    if delta == 0:
        raise ValueError("singular named curve")
    j = f.div(f.power(c4, 3), delta)
    return j in {0, const(1728)}
