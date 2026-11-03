"""Independent polynomial-basis replay of one standard-structure certificate.

No producer arithmetic is imported. A valid unit is not a cohort-completeness
or Frobenius-descent certificate. An external expected field/model is required.
"""
import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper):
    require(type(value) is int and lower <= value <= upper, "integer/range violation")
    return value


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected.split()), "object keys mismatch")


def trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def prime_remainder(a, b, p):
    a, b = trim([v % p for v in a]), trim([v % p for v in b])
    require(bool(b), "zero polynomial divisor")
    while len(a) >= len(b):
        d, c = len(a)-len(b), a[-1]*pow(b[-1], -1, p) % p
        for i, v in enumerate(b):
            a[d+i] = (a[d+i]-c*v) % p
        a = trim(a)
    return a


class Field:
    def __init__(self, record, limit=100000):
        keys(record, "prime degree modulus primitive_polynomial_index logarithm_to_polynomial_index")
        self.p = integer(record["prime"], 3, 13)
        require(self.p in (3, 5, 7, 11, 13), "unsupported characteristic")
        self.n = integer(record["degree"], 1, 7)
        self.size = self.p**self.n
        require(self.size <= limit, "checker field limit exceeded")
        m = record["modulus"]
        require(type(m) is list and len(m) == self.n+1, "modulus length")
        self.modulus = [integer(v, 0, self.p-1) for v in m]
        require(m[-1] == 1, "nonmonic modulus")
        x = self.p if self.n > 1 else (-m[0]) % self.p
        require(self.power(x, self.size) == x, "modulus fails Frobenius irreducibility test")
        for divisor in range(2, self.n+1):
            if self.n % divisor or any(divisor % j == 0 for j in range(2, divisor)):
                continue
            a, b = m, self.digits(self.sub(self.power(x, self.p**(self.n//divisor)), x))
            while trim(b):
                a, b = b, prime_remainder(a, b, self.p)
            require(len(trim(a)) == 1, "reducible modulus")
        table = record["logarithm_to_polynomial_index"]
        require(type(table) is list and len(table) == self.size, "encoding table length")
        for value in table:
            self.element(value)
        require(set(table) == set(range(self.size)) and table[:2] == [0, 1], "encoding bijection")
        primitive = self.element(record["primitive_polynomial_index"])
        require(primitive != 0, "zero primitive element")
        current = 1
        for encoded in range(1, self.size):
            require(table[encoded] == current, "primitive/log table inconsistency")
            current = self.mul(current, primitive)
        require(current == 1, "primitive cycle")
        self.log = {value: i for i, value in enumerate(table)}

    def element(self, value):
        return integer(value, 0, self.size-1)

    def digits(self, a):
        result = []
        for _ in range(self.n):
            result.append(a % self.p)
            a //= self.p
        return result

    def encode(self, digits):
        return sum((v % self.p)*self.p**i for i, v in enumerate(digits))

    def add(self, a, b):
        return self.encode([x+y for x, y in zip(self.digits(a), self.digits(b))])

    def sub(self, a, b):
        return self.encode([x-y for x, y in zip(self.digits(a), self.digits(b))])

    def mul(self, a, b):
        product = [0]*(2*self.n-1)
        for i, x in enumerate(self.digits(a)):
            for j, y in enumerate(self.digits(b)):
                product[i+j] += x*y
        return self.encode(prime_remainder(product, self.modulus, self.p))

    def power(self, a, exponent):
        result = 1
        while exponent:
            if exponent & 1:
                result = self.mul(result, a)
            a = self.mul(a, a)
            exponent >>= 1
        return result

    def div(self, a, b):
        require(b != 0, "zero division")
        return self.mul(a, self.power(b, self.size-2))


def polynomial_mul(f, a, b):
    if not a or not b:
        return []
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = f.add(out[i+j], f.mul(x, y))
    return trim(out)


def polynomial_remainder(f, a, b):
    a, b = trim(a), trim(b)
    require(bool(b), "zero polynomial divisor")
    while len(a) >= len(b):
        d, c = len(a)-len(b), f.div(a[-1], b[-1])
        for i, v in enumerate(b):
            a[d+i] = f.sub(a[d+i], f.mul(c, v))
        a = trim(a)
    return a


def polynomial_value(f, a, x):
    result = 0
    for c in reversed(a):
        result = f.add(f.mul(result, x), c)
    return result


def monic_square(f, product):
    """Extract a monic polynomial square root, independently of support XOR."""
    degree = len(product)-1
    if degree % 2:
        return False
    normalized = [f.div(c, product[-1]) for c in product]
    d = degree//2
    root = [0]*d+[1]
    for k in range(d-1, -1, -1):
        known = 0
        for i in range(k+1, d+1):
            j = d+k-i
            if k < j <= d:
                known = f.add(known, f.mul(root[i], root[j]))
        root[k] = f.div(f.sub(normalized[d+k], known), 2)
    return polynomial_mul(f, root, root) == normalized


def square_relations(f, forms):
    require(len(forms) <= 7, "relation dimension limit")
    relations = []
    for polynomial in forms:
        require(type(polynomial) is list and len(polynomial) == 5, "binary quartic shape")
        for c in polynomial:
            f.element(c)
        a = trim(polynomial)
        require(4 <= len(a) <= 5, "projective branch multiplicity at infinity")
        b = trim([f.mul(i % f.p, a[i]) for i in range(1, len(a))])
        while b:
            a, b = b, polynomial_remainder(f, a, b)
        require(len(a) == 1, "repeated branch root")
    for mask in range(1 << len(forms)):
        product = [1]
        infinity_parity = 0
        for i, polynomial in enumerate(forms):
            if mask & (1 << i):
                polynomial = trim(polynomial)
                infinity_parity ^= (len(polynomial)-1) % 2
                product = polynomial_mul(f, product, polynomial)
        if not infinity_parity and monic_square(f, product):
            relations.append([mask, f.power(product[-1], (f.size-1)//2) == 1])
    return relations


class Curve:
    def __init__(self, f, coefficients):
        require(type(coefficients) is list and len(coefficients) == 3, "curve coefficient shape")
        self.f = f
        self.a2, self.a4, self.a6 = [f.element(v) for v in coefficients]
        self.cubic = [self.a6, self.a4, self.a2, 1]
        derivative = [self.a4, f.mul(2, self.a2), 3 % f.p]
        a, b = self.cubic, trim(derivative)
        while b:
            a, b = b, polynomial_remainder(f, a, b)
        require(len(a) == 1, "singular curve")
        self.roots = {}
        for y in range(f.size):
            self.roots.setdefault(f.mul(y, y), []).append(y)
        self.points = {None}
        for x in range(f.size):
            for y in self.roots.get(polynomial_value(f, self.cubic, x), []):
                self.points.add((x, y))

    def read_point(self, value):
        if value is None:
            return None
        require(type(value) is list and len(value) == 2, "point shape")
        p = tuple(self.f.element(v) for v in value)
        require(p in self.points, "point off expected curve")
        return p

    def key(self, p):
        return (0,) if p is None else (1, self.f.log[p[0]], self.f.log[p[1]])

    def add(self, p, q):
        if p is None:
            return q
        if q is None:
            return p
        f = self.f
        x, y = p
        u, v = q
        if x == u and f.add(y, v) == 0:
            return None
        if x == u:
            numerator = f.add(f.add(f.mul(3 % f.p, f.mul(x, x)), f.mul(2, f.mul(self.a2, x))), self.a4)
            slope = f.div(numerator, f.mul(2, y))
        else:
            slope = f.div(f.sub(v, y), f.sub(u, x))
        nx = f.sub(f.sub(f.sub(f.mul(slope, slope), self.a2), x), u)
        return nx, f.sub(f.mul(slope, f.sub(x, nx)), y)

    def quotient_form(self, target):
        if target is None:
            return self.cubic+[0]
        f = self.f
        u, v = target
        c0 = f.sub(f.sub(f.sub(f.mul(self.a2, self.a2), f.mul(2, f.mul(self.a2, u))), f.mul(3 % f.p, f.mul(u, u))), f.mul(4 % f.p, self.a4))
        return [c0, f.sub(0, f.mul(8 % f.p, v)), f.sub(0, f.mul(2, f.add(self.a2, f.mul(3 % f.p, u)))), 0, 1]

    def check_images(self, target, rows, form):
        require(type(rows) is list and len(rows) == len(self.points), "chart coverage length")
        f = self.f
        u, v = target
        seen, images = set(), set()
        expected_images = {("infinity", 1), ("infinity", -1)}
        for t in range(f.size):
            expected_images.update(("affine", t, w) for w in self.roots.get(polynomial_value(f, form, t), []))
        for row in rows:
            keys(row, "point image")
            p = self.read_point(row["point"])
            require(p not in seen, "duplicate chart point")
            seen.add(p)
            image = row["image"]
            require(type(image) is dict, "chart image shape")
            if set(image) == {"infinity"}:
                sign = integer(image["infinity"], -1, 1)
                require(sign in (-1, 1), "invalid infinity branch")
                decoded = None if sign == 1 else target
                ident = ("infinity", sign)
            else:
                keys(image, "affine")
                pair = image["affine"]
                require(type(pair) is list and len(pair) == 2, "quartic coordinate shape")
                t, w = [f.element(a) for a in pair]
                require(f.mul(w, w) == polynomial_value(f, form, t), "point off quartic")
                x = f.div(f.add(f.sub(f.sub(f.mul(t, t), self.a2), u), w), 2)
                decoded = x, f.sub(f.mul(t, f.sub(x, u)), v)
                ident = ("affine", t, w)
                opposite_x = f.div(f.sub(f.sub(f.sub(f.mul(t, t), self.a2), u), w), 2)
                opposite = opposite_x, f.sub(f.mul(t, f.sub(opposite_x, u)), v)
                require(p is not None and opposite == self.add(target, (p[0], f.sub(0, p[1]))), "quotient involution mismatch")
            require(decoded == p and ident not in images, "inverse or injectivity failure")
            images.add(ident)
        require(seen == self.points and images == expected_images, "complete chart bijection failure")


def verify(record, expected, field_limit=100000):
    keys(record, "schema scope field curve points cosets quotients")
    require(record["schema"] == "pext.quotient-certificate/v1" and record["scope"] == "one-curve-standard-structure", "certificate scope/schema")
    keys(expected, "field curve")
    keys(expected["field"], "prime degree modulus")
    require(type(record["field"]) is dict, "field object shape")
    integer(expected["field"]["prime"], 3, 13)
    integer(expected["field"]["degree"], 1, 7)
    require(type(expected["field"]["modulus"]) is list and type(expected["curve"]) is list, "expected input arrays")
    for v in expected["field"]["modulus"] + expected["curve"]:
        integer(v, 0, field_limit-1)
    require({k: record["field"].get(k) for k in expected["field"]} == expected["field"] and record["curve"] == expected["curve"], "external expected-input mismatch")
    f = Field(record["field"], field_limit)
    curve = Curve(f, record["curve"])
    require(type(record["points"]) is list, "point list shape")
    supplied = [curve.read_point(p) for p in record["points"]]
    require(supplied == sorted(curve.points, key=curve.key), "complete canonical point list mismatch")
    doubles = {curve.add(p, p) for p in curve.points}
    cosets = record["cosets"]
    require(type(cosets) is list and 1 <= len(cosets) <= 4, "coset list shape")
    uncovered = set(curve.points)
    representatives = []
    for coset in cosets:
        keys(coset, "representative members")
        rep = curve.read_point(coset["representative"])
        require(uncovered and rep == min(uncovered, key=curve.key), "noncanonical or duplicate coset")
        expected_members = {curve.add(rep, d) for d in doubles}
        require(type(coset["members"]) is list and len(coset["members"]) == len(doubles), "coset witness count")
        members = set()
        for row in coset["members"]:
            keys(row, "point half")
            p, half = curve.read_point(row["point"]), curve.read_point(row["half"])
            require(p not in members and curve.add(rep, curve.add(half, half)) == p, "coset witness failure")
            members.add(p)
        require(members == expected_members and members <= uncovered, "coset coverage/overlap")
        uncovered -= members
        representatives.append(rep)
    require(not uncovered and len(cosets) == sum(curve.add(p, p) is None for p in curve.points), "quotient completeness/kernel cardinality")
    quotients = record["quotients"]
    require(type(quotients) is list and len(quotients) == len(representatives), "quotient list coverage")
    for target, quotient in zip(representatives, quotients):
        keys(quotient, "target chart_kind conjugates relations geometric_rank arithmetic_rank contains_nonsquare_constant images")
        require(curve.read_point(quotient["target"]) == target, "target identity/order")
        form = curve.quotient_form(target)
        conjugates, current = [], form
        for _ in range(f.n):
            conjugates.append(current)
            current = [f.power(c, f.p) for c in current]
        require(type(quotient["conjugates"]) is list and len(quotient["conjugates"]) == f.n, "conjugate count")
        for given in quotient["conjugates"]:
            require(type(given) is list and len(given) == 5, "form shape")
            for c in given:
                f.element(c)
        require(quotient["conjugates"] == conjugates, "ordered conjugate binding")
        relations = square_relations(f, conjugates)
        require(type(quotient["relations"]) is list, "relation list")
        for row in quotient["relations"]:
            require(type(row) is list and len(row) == 2 and type(row[1]) is bool, "relation shape")
            integer(row[0], 0, (1 << f.n)-1)
        require(quotient["relations"] == relations, "complete square relation mismatch")
        geometric = f.n-(len(relations).bit_length()-1)
        arithmetic = f.n-(sum(square for _, square in relations).bit_length()-1)
        require(integer(quotient["geometric_rank"], 0, f.n) == geometric and integer(quotient["arithmetic_rank"], 0, f.n) == arithmetic, "rank mismatch")
        flag = quotient["contains_nonsquare_constant"]
        require(type(flag) is bool and flag == any(not s for _, s in relations), "constant flag mismatch")
        if target is None:
            require(quotient["chart_kind"] == "baseline-cubic" and quotient["images"] is None, "baseline chart mismatch")
        else:
            require(quotient["chart_kind"] == "quartic", "nonzero target chart kind")
            curve.check_images(target, quotient["images"], form)
    return {"schema": "pext.quotient-check/v1", "valid": True, "points": len(curve.points), "cosets": len(cosets), "scope": "expected single curve, all rational quotient representatives, standard structure; no descent or cohort certificate"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    require(path.stat().st_size <= 16*1024*1024, "checker file limit exceeded")
    return json.loads(path.read_text(), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--expected-input", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(load(args.certificate), load(args.expected_input)), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, "INVALID: " + str(error) + "\n")
