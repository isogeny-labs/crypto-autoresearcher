"""Exact quotient-coordinate transport in K(x)[y]/(y^2-f(x)).

Constructs and verifies algebraic certificates; it does not run cover/genus
measurements. Verification shares this rational-function engine with synthesis.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from check_quotient_certificate import integer, keys, load, require, polynomial_mul, polynomial_value, trim
from check_compact_class_inputs import BasisField
from check_curve_class_certificate import read_model
from check_structure_certificate import normalize, inverse, transform


@lru_cache(maxsize=8)
def verified_field(canonical_identity):
    return BasisField(json.loads(canonical_identity))


class AlgebraCurve:
    """Exact group law without materializing E(K) for every transport witness."""
    def __init__(self, f, model):
        self.f = f
        self.a2, self.a4, self.a6 = read_model(f, model)
        self.cubic = [self.a6, self.a4, self.a2, 1]

    def read_point(self, value):
        if value is None: return None
        require(type(value) is list and len(value) == 2, 'point shape')
        x, y = [self.f.element(v) for v in value]
        require(self.f.mul(y, y) == polynomial_value(self.f, self.cubic, x), 'point off curve')
        return x, y

    def add(self, p, q):
        if p is None: return q
        if q is None: return p
        f = self.f; x, y = p; u, v = q
        if x == u and f.add(y, v) == 0: return None
        if x == u:
            slope = f.div(f.add(f.add(f.mul(3 % f.p, f.mul(x, x)), f.mul(2, f.mul(self.a2, x))), self.a4), f.mul(2, y))
        else:
            slope = f.div(f.sub(v, y), f.sub(u, x))
        nx = f.sub(f.sub(f.sub(f.mul(slope, slope), self.a2), x), u)
        return nx, f.sub(f.mul(slope, f.sub(x, nx)), y)

    def quotient_form(self, target):
        if target is None: return self.cubic+[0]
        f = self.f; u, v = target
        c0 = f.sub(f.sub(f.sub(f.mul(self.a2, self.a2), f.mul(2, f.mul(self.a2, u))), f.mul(3 % f.p, f.mul(u, u))), f.mul(4 % f.p, self.a4))
        return [c0, f.sub(0, f.mul(8 % f.p, v)), f.sub(0, f.mul(2, f.add(self.a2, f.mul(3 % f.p, u)))), 0, 1]


class FunctionField:
    def __init__(self, field, model):
        self.f = field
        self.curve = AlgebraCurve(field, model)
        self.cubic = self.curve.cubic

    def add_poly(self, a, b):
        return trim([self.f.add(a[i] if i < len(a) else 0, b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))])

    def neg_poly(self, a): return [self.f.sub(0, c) for c in a]
    def sub_poly(self, a, b): return self.add_poly(a, self.neg_poly(b))
    def mul_poly(self, a, b):
        require(len(a)+len(b) <= 1026, 'function polynomial degree cap')
        return trim(polynomial_mul(self.f, a, b))

    def divmod_poly(self, a, b):
        a, b = trim(a), trim(b); require(bool(b), 'zero polynomial divisor')
        quotient = [0]*max(0, len(a)-len(b)+1)
        while len(a) >= len(b):
            degree = len(a)-len(b); coefficient = self.f.div(a[-1], b[-1]); quotient[degree] = coefficient
            for i, value in enumerate(b): a[degree+i] = self.f.sub(a[degree+i], self.f.mul(coefficient, value))
            a = trim(a)
        return trim(quotient), a

    def gcd(self, a, b):
        while b: a, b = b, self.divmod_poly(a, b)[1]
        return [self.f.div(c, a[-1]) for c in a] if a else []

    def exact_div(self, a, b):
        q, r = self.divmod_poly(a, b); require(not r, 'inexact polynomial division'); return q

    def value(self, a=(), b=(), denominator=(1,)): return Function(self, a, b, denominator)
    def scalar(self, value): return self.value([self.f.element(value)])
    def integer(self, value): return self.scalar(value % self.f.p)
    def x(self): return self.value([0, 1])
    def y(self): return self.value([], [1])


class Function:
    def __init__(self, ring, a, b, denominator):
        self.ring = ring
        for part in (a, b, denominator):
            require(len(part) <= 1025, 'function polynomial degree cap')
            for value in part: ring.f.element(value)
        a, b, denominator = trim(a), trim(b), trim(denominator)
        require(bool(denominator), 'zero function denominator')
        g = ring.gcd(ring.gcd(a, b), denominator)
        a, b, denominator = (ring.exact_div(part, g) for part in (a, b, denominator))
        leading = denominator[-1]
        self.a, self.b, self.d = ([ring.f.div(c, leading) for c in part] for part in (a, b, denominator))

    def same_ring(self, other): require(isinstance(other, Function) and other.ring is self.ring, 'mixed function fields')
    def __neg__(self): return self.ring.value(self.ring.neg_poly(self.a), self.ring.neg_poly(self.b), self.d)
    def __add__(self, other):
        self.same_ring(other); r = self.ring
        # LCM denominators avoid artificial degree growth in repeated additions.
        g = r.gcd(self.d, other.d); left = r.exact_div(other.d, g); right = r.exact_div(self.d, g)
        return r.value(r.add_poly(r.mul_poly(self.a, left), r.mul_poly(other.a, right)),
                       r.add_poly(r.mul_poly(self.b, left), r.mul_poly(other.b, right)), r.mul_poly(self.d, left))
    def __sub__(self, other): return self + (-other)
    def __mul__(self, other):
        self.same_ring(other); r = self.ring
        return r.value(r.add_poly(r.mul_poly(self.a, other.a), r.mul_poly(r.cubic, r.mul_poly(self.b, other.b))),
                       r.add_poly(r.mul_poly(self.a, other.b), r.mul_poly(self.b, other.a)), r.mul_poly(self.d, other.d))
    def reciprocal(self):
        r = self.ring
        norm = r.sub_poly(r.mul_poly(self.a, self.a), r.mul_poly(r.cubic, r.mul_poly(self.b, self.b)))
        return r.value(r.mul_poly(self.a, self.d), r.neg_poly(r.mul_poly(self.b, self.d)), norm)
    def __truediv__(self, other): return self * other.reciprocal()
    def __pow__(self, exponent):
        integer(exponent, 0, 16); result = self.ring.integer(1)
        for _ in range(exponent): result = result*self
        return result
    def __eq__(self, other):
        return isinstance(other, Function) and self.ring is other.ring and (self.a, self.b, self.d) == (other.a, other.b, other.d)
    def equals_cross(self, other):
        self.same_ring(other); r = self.ring
        return (not r.sub_poly(r.mul_poly(self.a, other.d), r.mul_poly(other.a, self.d))
                and not r.sub_poly(r.mul_poly(self.b, other.d), r.mul_poly(other.b, self.d)))
    def constant(self):
        require(not self.b and self.d == [1] and len(self.a) <= 1, 'transport multiplier is not constant')
        return self.a[0] if self.a else 0


def coordinates(ring, target, x, y):
    if target is None: return x, y
    u, v = map(ring.scalar, target)
    t = (y+v)/(x-u)
    return t, ring.integer(2)*x+ring.scalar(ring.curve.a2)+u-t*t


def translation(ring, point):
    x, y = ring.x(), ring.y()
    if point is None: return x, y
    h, k = map(ring.scalar, point)
    slope = (y-k)/(x-h)
    nx = slope*slope-ring.scalar(ring.curve.a2)-x-h
    return nx, slope*(x-nx)-y


def one_dimensional_kernel(ring, columns):
    denominator = [1]
    for column in columns:
        denominator = ring.mul_poly(denominator, ring.exact_div(column.d, ring.gcd(denominator, column.d)))
    expanded = [(ring.mul_poly(c.a, ring.exact_div(denominator, c.d)), ring.mul_poly(c.b, ring.exact_div(denominator, c.d))) for c in columns]
    rows = []
    for component in range(2):
        for degree in range(max(len(c[component]) for c in expanded)):
            row = [c[component][degree] if degree < len(c[component]) else 0 for c in expanded]
            if any(row): rows.append(row)
    f = ring.f; pivots = []; rank = 0
    for column in range(4):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None: continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]; rows[rank] = [f.div(c, scale) for c in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                factor = rows[i][column]
                rows[i] = [f.sub(c, f.mul(factor, p)) for c, p in zip(rows[i], rows[rank])]
        pivots.append(column); rank += 1
    require(rank == 3, 'Mobius relation does not have unique projective kernel')
    free = next(i for i in range(4) if i not in pivots); vector = [0]*4; vector[free] = 1
    for row, pivot in zip(rows, pivots): vector[pivot] = f.sub(0, row[free])
    return normalize(f, vector)


def context(field_record, model, source, half):
    field = verified_field(json.dumps(field_record, sort_keys=True, separators=(',', ':')))
    ring = FunctionField(field, model)
    source = ring.curve.read_point(source); half = ring.curve.read_point(half)
    target = ring.curve.add(source, ring.curve.add(half, half))
    t, w = coordinates(ring, source, ring.x(), ring.y())
    xp, yp = translation(ring, half); tp, wp = coordinates(ring, target, xp, yp)
    return ring, target, t, w, tp, wp


def synthesize(field_record, model, source, half):
    source = list(source) if source is not None else None
    half = list(half) if half is not None else None
    ring, target, t, w, tp, wp = context(field_record, model, source, half)
    matrix = one_dimensional_kernel(ring, [-t, -ring.integer(1), t*tp, tp])
    a, b, c, d = map(ring.scalar, matrix)
    kappa = (wp*(c*t+d)**2/w).constant(); require(kappa != 0, 'zero transport scale')
    record = {'schema': 'pext.target-transport/v1', 'field': field_record, 'curve': model,
              'source_target': source, 'half': half, 'target': list(target) if target is not None else None,
              'matrix': matrix, 'kappa': kappa,
              'source_form': ring.curve.quotient_form(ring.curve.read_point(source)),
              'target_form': ring.curve.quotient_form(target)}
    verify(record, {'field': field_record, 'curve': model, 'source_target': source, 'half': half})
    return record


def verify(record, expected):
    keys(record, 'schema field curve source_target half target matrix kappa source_form target_form')
    keys(expected, 'field curve source_target half')
    require(record['schema'] == 'pext.target-transport/v1', 'transport schema')
    require(json.dumps({k: record[k] for k in expected}, sort_keys=True) == json.dumps(expected, sort_keys=True), 'external transport input mismatch')
    ring, target, t, w, tp, wp = context(record['field'], record['curve'], record['source_target'], record['half'])
    f = ring.f
    require(ring.curve.read_point(record['target']) == target, 'target translation mismatch')
    matrix = normalize(f, record['matrix']); require(matrix == record['matrix'], 'noncanonical transport matrix')
    kappa = f.element(record['kappa']); require(kappa != 0, 'zero transport scale')
    a, b, c, d = map(ring.scalar, matrix)
    require((tp*(c*t+d)).equals_cross(a*t+b), 'quotient coordinate identity failure')
    require((wp*(c*t+d)**2).equals_cross(ring.scalar(kappa)*w), 'weighted ordinate identity failure')
    source_form = ring.curve.quotient_form(ring.curve.read_point(record['source_target']))
    target_form = ring.curve.quotient_form(target)
    for key, wanted in [('source_form', source_form), ('target_form', target_form)]:
        require(type(record[key]) is list and len(record[key]) == 5, 'form shape')
        for value in record[key]: f.element(value)
        require(record[key] == wanted, 'quotient form mismatch')
    # adj(adj(A))=A exactly, so this is F_target(A(X,Z)), with no determinant divisor.
    require(transform(f, target_form, inverse(f, matrix)) == [f.mul(f.mul(kappa, kappa), x) for x in source_form], 'literal quartic transport identity failure')
    return {'valid': True, 'scope': 'exact rational coordinate and weighted-ordinate identities plus literal binary quartic identity'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--expected-input', required=True, type=Path)
    args = parser.parse_args()
    try: print(json.dumps(verify(load(args.certificate), load(args.expected_input)), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error: parser.exit(2, 'INVALID: '+str(error)+'\n')
