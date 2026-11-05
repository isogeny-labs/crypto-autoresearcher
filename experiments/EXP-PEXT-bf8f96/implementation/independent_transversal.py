"""Independent unranking of the frozen left PGL2(Fq) coset transversal.

Arithmetic is polynomial-basis Python arithmetic. The published log-to-basis
table is used only to reproduce the producer's numeric ordering of points.
"""

from check_compact_class_inputs import BasisField
from check_structure_certificate import normalize


class LogLabels:
    def __init__(self, record):
        self.basis = BasisField(record)
        self.table = record["logarithm_to_polynomial_index"]
        self.inverse = {basis: label for label, basis in enumerate(self.table)}
        self.p, self.n, self.size = self.basis.p, self.basis.n, self.basis.size

    def add(self, a, b):
        return self.inverse[self.basis.add(self.table[a], self.table[b])]

    def sub(self, a, b):
        return self.inverse[self.basis.sub(self.table[a], self.table[b])]

    def mul(self, a, b):
        return self.inverse[self.basis.mul(self.table[a], self.table[b])]

    def div(self, a, b):
        return self.inverse[self.basis.div(self.table[a], self.table[b])]

    def neg(self, a):
        return self.sub(0, a)

    def element(self, value):
        if type(value) is not int or not 0 <= value < self.size:
            raise ValueError("field label out of range")
        return value

    def in_fq(self, a):
        value = self.table[a]
        return self.basis.power(value, self.p) == value


def image(f, matrix, point):
    infinity = f.size
    a, b, c, d = matrix
    if point == infinity:
        return infinity if c == 0 else f.div(a, c)
    numerator, denominator = f.add(f.mul(a, point), b), f.add(f.mul(c, point), d)
    return infinity if denominator == 0 else f.div(numerator, denominator)


def from_triple(f, a, b, c):
    infinity = f.size
    if a == infinity:
        raw = [f.sub(c, b), b, 0, 1]
    elif b == infinity:
        raw = [a, f.sub(c, a), 1, 0]
    elif c == infinity:
        raw = [a, f.neg(b), 1, f.neg(1)]
    else:
        raw = [f.mul(a, f.sub(c, b)), f.mul(b, f.sub(a, c)),
               f.sub(c, b), f.sub(a, c)]
    return normalize(f, raw)


def orbit_representatives(domain, actions):
    remaining, representatives = set(domain), []
    while remaining:
        representative = min(remaining)
        orbit = {action(representative) for action in actions}
        if len(orbit) != len(actions) or not orbit <= remaining:
            raise ValueError("transversal action is not free or orbits overlap")
        representatives.append(representative)
        remaining -= orbit
    return representatives


class IndependentTransversal:
    def __init__(self, field_record):
        f = self.f = LogLabels(field_record)
        if f.n not in (3, 5, 7):
            raise ValueError("unsupported transversal degree")
        fq = [value for value in range(f.size) if f.in_fq(value)]
        if len(fq) != f.p:
            raise ValueError("base-field point count mismatch")
        fq_set = set(fq)
        non = [value for value in range(f.size) if value not in fq_set]
        pgl = ([normalize(f, [1, b, c, d]) for b in fq for c in fq for d in fq
                if d != f.mul(b, c)]
               + [normalize(f, [0, 1, c, d]) for c in fq if c != 0 for d in fq])
        if len(pgl) != f.p**3 - f.p:
            raise ValueError("base PGL2 cardinality mismatch")
        self.rep_b = orbit_representatives(non,
            [lambda point, matrix=matrix: image(f, matrix, point) for matrix in pgl])
        self.rep_a2 = orbit_representatives(non,
            [lambda point, u=u, v=v: f.add(f.mul(u, point), v)
             for u in fq if u != 0 for v in fq])
        self.rep_a1 = orbit_representatives(range(1, f.size),
            [lambda point, u=u: f.mul(u, point) for u in fq if u != 0])
        q = f.size
        self.count = (len(self.rep_a1) + len(self.rep_a2)*(q-1)
                      + len(self.rep_b)*q*(q-1))
        expected, remainder = divmod(q**3-q, f.p**3-f.p)
        if remainder or self.count != expected:
            raise ValueError("transversal structure count mismatch")

    def matrix(self, ordinal):
        f = self.f
        if type(ordinal) is not int or not 0 <= ordinal < self.count:
            raise ValueError("structure ordinal out of range")
        q = f.size
        first = len(self.rep_a1)
        second = len(self.rep_a2)*(q-1)
        omit_one = lambda rank, excluded: rank + (rank >= excluded)
        if ordinal < first:
            a, b, c = q, 0, self.rep_a1[ordinal]
        elif ordinal < first + second:
            offset = ordinal-first
            b = self.rep_a2[offset // (q-1)]
            a, c = q, omit_one(offset % (q-1), b)
        else:
            offset = ordinal-first-second
            a = self.rep_b[offset // (q*(q-1))]
            tail = offset % (q*(q-1))
            b = omit_one(tail // (q-1), a)
            c = tail % (q-1)
            for excluded in sorted((a, b)):
                c += c >= excluded
        return [f.table[value] for value in from_triple(f, a, b, c)]
