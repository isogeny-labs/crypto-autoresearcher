"""Exact construction check for a degree-two quotient of an elliptic curve.

For E: y^2 = x^3 + a2*x^2 + a4*x + a6 and a nonidentity point
T=(u,v), t=(y+v)/(x-u) gives the quartic below. Coefficients are in
ascending order. The function uses ring operations and applies in any odd
characteristic. The inverse map requires division by 2.

This is an algebraic construction component, not a census launcher. It does
not enumerate E(K)/2E(K), settle exceptional projective charts, classify
K-isomorphisms, test descent, or produce experiment measurements.

Chart specification for a future implementation: when v != 0, the removable
point -T has t=-(3*u^2+2*a2*u+a4)/(2*v). O and T are the two poles;
on the monic quartic they correspond to w/t^2 approaching +1 and -1.
For v=0, T=-T is a pole, so the removable-point formula must not be used.
"""


def quartic_coefficients(a2, a4, u, v):
    """Return coefficients of w^2=D(t), retaining the input curve's model."""
    return (
        a2 * a2 - 2 * a2 * u - 3 * u * u - 4 * a4,
        -8 * v,
        -2 * (a2 + 3 * u),
        0,
        1,
    )


def check_symbolic_identity():
    """Check identities over Z; no experiment instances are sampled."""
    import sympy as s

    x, u, v, t, a2, a4, a6, w = s.symbols("x u v t a2 a4 a6 w")
    cubic = x**3 + a2*x**2 + a4*x + a6
    residual = (x**2 + (a2+u-t**2)*x
                + u**2 + a2*u + a4 + u*t**2 + 2*v*t)
    factor_identity = s.expand(
        cubic - (t*(x-u)-v)**2 - (x-u)*residual
    ).subs(a6, v**2-u**3-a2*u**2-a4*u)
    quartic = sum(c*t**i for i, c in enumerate(
        quartic_coefficients(a2, a4, u, v)))
    checks = {
        "residual_factor": s.expand(factor_identity) == 0,
        "quartic_discriminant": s.expand(s.discriminant(residual, x)-quartic) == 0,
        "inverse_quadratic": s.expand(
            4*residual.subs(x, (t**2-a2-u+w)/2) - (w**2-quartic)
        ) == 0,
        "removable_point_equation": s.expand(
            residual.subs(x, u) - (3*u**2+2*a2*u+a4+2*v*t)
        ) == 0,
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return {"schema": "pext.degree2.symbolic-check/v1", "checks": checks,
            "sympy_version": s.__version__,
            "scope": "polynomial identities only; inverse requires odd characteristic"}


if __name__ == "__main__":
    import json
    print(json.dumps(check_symbolic_identity(), sort_keys=True))
