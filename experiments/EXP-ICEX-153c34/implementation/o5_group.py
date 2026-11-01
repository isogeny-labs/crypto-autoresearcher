"""Independent verifier-only affine group arithmetic for ICEX S0.

This module is deliberately separate from ``g1_s0``. The exact O5 oracle and
fixture construction import it, while a Sage gate cross-checks its formulas
against Sage's elliptic-curve implementation.
"""


def point_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        numerator, denominator = (3 * x1 * x1 + a) % p, (2 * y1) % p
    else:
        numerator, denominator = (y2 - y1) % p, (x2 - x1) % p
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def sqrt(value, p):
    """Deterministic Tonelli-Shanks square root over an odd prime field."""
    value %= p
    if value == 0:
        return 0
    if pow(value, (p - 1) // 2, p) != 1:
        raise ValueError("not a square")
    if p % 4 == 3:
        return pow(value, (p + 1) // 4, p)
    odd, power = p - 1, 0
    while odd % 2 == 0:
        odd //= 2
        power += 1
    nonresidue = 2
    while pow(nonresidue, (p - 1) // 2, p) != p - 1:
        nonresidue += 1
    m = power
    c = pow(nonresidue, odd, p)
    t = pow(value, odd, p)
    root = pow(value, (odd + 1) // 2, p)
    while t != 1:
        index, square = 1, t * t % p
        while square != 1:
            square = square * square % p
            index += 1
        correction = pow(c, 1 << (m - index - 1), p)
        root = root * correction % p
        t = t * correction * correction % p
        c = correction * correction % p
        m = index
    return root


def canonical_point(p, a, b, x):
    rhs = (x**3 + a * x + b) % p
    if rhs == 0:
        return x, 0
    if pow(rhs, (p - 1) // 2, p) != 1:
        return None
    y = sqrt(rhs, p)
    return x, min(y, p - y)
