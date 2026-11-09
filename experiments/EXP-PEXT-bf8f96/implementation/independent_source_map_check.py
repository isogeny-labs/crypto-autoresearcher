"""Independent exact replay of one source-to-quartic map.

Uses only the polynomial-basis certificate arithmetic. This checks one named
source row and its coordinate maps; it proves no cohort coverage or descent.
"""

from check_quotient_certificate import Field, Curve, polynomial_mul, polynomial_remainder, trim


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Functions:
    """Fractions (a(x)+b(x)y)/d(x), with y²=the named nonsingular cubic."""

    def __init__(self, field, cubic):
        self.f, self.cubic = field, cubic

    def poly_add(self, a, b):
        f = self.f
        return trim([f.add(a[i] if i < len(a) else 0,
                           b[i] if i < len(b) else 0)
                     for i in range(max(len(a), len(b)))])

    def poly_neg(self, a):
        return [self.f.sub(0, c) for c in a]

    def poly_div(self, a, b):
        f = self.f
        a, b = trim(a), trim(b)
        need(bool(b), "zero polynomial divisor")
        answer = [0] * max(0, len(a)-len(b)+1)
        while len(a) >= len(b):
            shift, scale = len(a)-len(b), f.div(a[-1], b[-1])
            answer[shift] = scale
            for i, c in enumerate(b):
                a[shift+i] = f.sub(a[shift+i], f.mul(scale, c))
            a = trim(a)
        need(not a, "nonexact polynomial division")
        return trim(answer)

    def gcd(self, a, b):
        f = self.f
        a, b = trim(a), trim(b)
        while b:
            a, b = b, polynomial_remainder(f, a, b)
        need(bool(a), "zero polynomial gcd")
        return [f.div(c, a[-1]) for c in a]

    def value(self, a, b=None, d=None):
        f = self.f
        a, b, d = trim(a), trim(b or []), trim(d if d is not None else [1])
        need(bool(d), "zero function denominator")
        if not a and not b:
            return ((), (), (1,))
        common = self.gcd(self.gcd(a, b) if a and b else (a or b), d)
        a, b, d = self.poly_div(a, common), self.poly_div(b, common), self.poly_div(d, common)
        scale = f.div(1, d[-1])
        return (tuple(f.mul(c, scale) for c in a),
                tuple(f.mul(c, scale) for c in b),
                tuple(f.mul(c, scale) for c in d))

    def scalar(self, c):
        return self.value([self.f.element(c)])

    def add(self, u, v):
        m = lambda a, b: polynomial_mul(self.f, a, b)
        return self.value(self.poly_add(m(u[0], v[2]), m(v[0], u[2])),
                          self.poly_add(m(u[1], v[2]), m(v[1], u[2])), m(u[2], v[2]))

    def neg(self, u):
        return self.value(self.poly_neg(u[0]), self.poly_neg(u[1]), u[2])

    def sub(self, u, v):
        return self.add(u, self.neg(v))

    def mul(self, u, v):
        m = lambda a, b: polynomial_mul(self.f, a, b)
        return self.value(self.poly_add(m(u[0], v[0]), m(self.cubic, m(u[1], v[1]))),
                          self.poly_add(m(u[0], v[1]), m(u[1], v[0])), m(u[2], v[2]))

    def inv(self, u):
        need(bool(u[0] or u[1]), "zero function inverse")
        m = lambda a, b: polynomial_mul(self.f, a, b)
        norm = self.poly_add(m(u[0], u[0]), self.poly_neg(m(self.cubic, m(u[1], u[1]))))
        need(bool(norm), "zero function norm")
        return self.value(m(u[2], u[0]), self.poly_neg(m(u[2], u[1])), norm)

    def div(self, u, v):
        return self.mul(u, self.inv(v))

    def power2(self, u):
        return self.mul(u, u)

    def equal(self, u, v):
        return self.sub(u, v) == self.scalar(0)

    def read(self, row):
        need(type(row) is dict and set(row) ==
             {"numerator_constant", "numerator_y", "denominator"}, "stored function shape")
        parts = [row[k] for k in ("numerator_constant", "numerator_y", "denominator")]
        need(all(type(part) is list and len(part) <= 1025 for part in parts),
             "stored function polynomial shape")
        for part in parts:
            for c in part:
                self.f.element(c)
        return self.value(*parts)


def verify(source, expected_field, expected_model, expected_target, expected_matrix):
    """Replay stored maps and both inverses against external source inputs."""
    need(type(source) is dict and source.get("schema") == "pext.source-map-binding/v1",
         "source map schema")
    need(source.get("field") == expected_field and source.get("model") == expected_model
         and source.get("target") == expected_target and source.get("matrix") == expected_matrix,
         "source map external identity mismatch")
    f = Field(expected_field)
    curve = Curve(f, expected_model)
    target = curve.read_point(expected_target)
    need(type(expected_matrix) is list and len(expected_matrix) == 4, "matrix shape")
    a, b, c, d = [f.element(v) for v in expected_matrix]
    det = f.sub(f.mul(a, d), f.mul(b, c))
    need(det and source.get("determinant") == det, "source determinant mismatch")
    ring = Functions(f, curve.cubic)
    x, y = ring.value([0, 1]), ring.value([], [1])
    one = ring.scalar(1)
    if target is None:
        t, w = x, y
    else:
        u, v = target
        t = ring.div(ring.add(y, ring.scalar(v)), ring.sub(x, ring.scalar(u)))
        w = ring.sub(ring.add(ring.add(ring.mul(ring.scalar(2), x),
                                       ring.scalar(curve.a2)), ring.scalar(u)), ring.power2(t))
    form = curve.quotient_form(target)
    need(source.get("source_form") == form, "source quartic mismatch")
    moved = [0] * 5
    left, right = [f.sub(0, b), d], [a, f.sub(0, c)]
    for i, coefficient in enumerate(form):
        term = [coefficient]
        for factor in [left] * i + [right] * (4-i):
            term = polynomial_mul(f, term, factor)
        for j, value in enumerate(term):
            moved[j] = f.add(moved[j], value)
    need(source.get("moved_form") == moved, "moved quartic mismatch")
    denominator = ring.add(ring.mul(ring.scalar(c), t), ring.scalar(d))
    xnew = ring.div(ring.add(ring.mul(ring.scalar(a), t), ring.scalar(b)), denominator)
    ynew = ring.div(ring.mul(ring.scalar(f.mul(det, det)), w), ring.power2(denominator))
    need(ring.read(source.get("x_map")) == xnew, "stored x map mismatch")
    need(ring.read(source.get("y_map")) == ynew, "stored y map mismatch")
    def evaluate(coefficients, argument):
        value = ring.scalar(0)
        for coefficient in reversed(coefficients):
            value = ring.add(ring.mul(value, argument), ring.scalar(coefficient))
        return value
    need(ring.equal(ring.power2(w), evaluate(form, t)), "source quartic identity mismatch")
    need(ring.equal(ring.power2(ynew), evaluate(moved, xnew)),
         "moved quartic identity mismatch")
    # The inverse is checked in the original function field, including the
    # exceptional chart at the named T; equality is of rational functions.
    tback = ring.div(ring.sub(ring.mul(ring.scalar(d), xnew), ring.scalar(b)),
                     ring.sub(ring.scalar(a), ring.mul(ring.scalar(c), xnew)))
    wback = ring.div(ring.mul(ynew, ring.power2(ring.add(
        ring.mul(ring.scalar(c), tback), ring.scalar(d)))), ring.scalar(f.mul(det, det)))
    need(ring.equal(tback, t) and ring.equal(wback, w), "projective inverse mismatch")
    if target is None:
        xback, yback = tback, wback
    else:
        u, v = target
        xback = ring.div(ring.add(ring.sub(ring.power2(tback),
                         ring.add(ring.scalar(curve.a2), ring.scalar(u))), wback), ring.scalar(2))
        yback = ring.sub(ring.mul(tback, ring.sub(xback, ring.scalar(u))), ring.scalar(v))
    need(ring.equal(xback, x) and ring.equal(yback, y), "elliptic inverse mismatch")
    return {"schema": "pext.independent-source-map-check/v1", "valid": True,
            "scope": "one source identity, stored coordinate maps and rational inverses"}
