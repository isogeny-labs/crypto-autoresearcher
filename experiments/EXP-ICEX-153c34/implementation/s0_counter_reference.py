#!/usr/bin/env python3
"""Standalone arithmetic/counting reference for ICEX gate G0-6.

This module intentionally imports neither ``g1_s0`` nor
``s0_operation_spec``.  It independently implements the fixed smoke-input
derivation, charged P_setup, D-2 specialisation, deterministic Buchberger
path, recursive root extraction, and signed recovery.  Its primitive totals
and arithmetic outputs are the expected values used by the counter checker.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path


SMOKE = "smoke|EXP-ICEX-153c34/v1"
FIELDS = ("mul", "inv", "probes", "point_add", "s_pairs",
          "reductions", "product_skips")
COMPONENTS = ("S", "G", "X", "V")


@dataclass
class PrimitiveCount:
    mul: int = 0
    inv: int = 0
    probes: int = 0
    point_add: int = 0
    s_pairs: int = 0
    reductions: int = 0
    product_skips: int = 0

    def add(self, field_name, count=1):
        if field_name not in FIELDS:
            raise ValueError("unknown reference primitive")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError("reference primitive count must be positive")
        setattr(self, field_name, getattr(self, field_name) + count)

    def raw(self):
        return {name: getattr(self, name) for name in FIELDS}

    def units(self):
        return self.mul + 10 * self.inv + self.probes + 13 * self.point_add

    def receipt(self):
        return self.raw() | {"units": self.units()}


class RefField:
    def __init__(self, p, count):
        self.p = int(p)
        self.count = count

    def mul(self, left, right):
        self.count.add("mul")
        return left * right % self.p

    def inv(self, value):
        if value % self.p == 0:
            raise ZeroDivisionError("reference inverse of zero")
        self.count.add("inv")
        return pow(value, self.p - 2, self.p)


def trim(poly):
    out = list(poly)
    while out and out[-1] == 0:
        out.pop()
    return out


def uadd(field, left, right):
    size = max(len(left), len(right))
    return trim([((left[i] if i < len(left) else 0)
                  + (right[i] if i < len(right) else 0)) % field.p
                 for i in range(size)])


def usub(left, right, p):
    size = max(len(left), len(right))
    return trim([((left[i] if i < len(left) else 0)
                  - (right[i] if i < len(right) else 0)) % p
                 for i in range(size)])


def uscale(field, poly, scalar):
    scalar %= field.p
    if scalar == 1:
        return trim(poly)
    if scalar == field.p - 1:
        return trim([(-value) % field.p for value in poly])
    return trim([field.mul(value, scalar) for value in poly])


def umul(field, left, right):
    if not left or not right:
        return []
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = (out[i + j] + field.mul(x, y)) % field.p
    return trim(out)


def ueval(field, poly, value):
    out = 0
    for coefficient in reversed(poly):
        out = (field.mul(out, value) + coefficient) % field.p
    return out


def udivmod(field, numerator, denominator):
    remainder = trim(numerator)
    denominator = trim(denominator)
    if not denominator:
        raise ZeroDivisionError("reference polynomial division by zero")
    if len(remainder) < len(denominator):
        return [], remainder
    quotient = [0] * (len(remainder) - len(denominator) + 1)
    inverse_lead = 1 if denominator[-1] == 1 else field.inv(denominator[-1])
    while remainder and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        factor = (remainder[-1] if inverse_lead == 1
                  else field.mul(remainder[-1], inverse_lead))
        quotient[shift] = factor
        for index, value in enumerate(denominator):
            remainder[index + shift] = (
                remainder[index + shift] - field.mul(factor, value)) % field.p
        remainder = trim(remainder)
    return trim(quotient), remainder


def ugcd(field, left, right):
    left, right = trim(left), trim(right)
    while right:
        _quotient, remainder = udivmod(field, left, right)
        left, right = right, remainder
    if not left:
        return []
    return uscale(field, left, field.inv(left[-1]))


def fp_pow(value, exponent, p, count):
    result, base = 1, value % p
    while exponent:
        if exponent & 1:
            count.add("mul")
            result = result * base % p
        exponent >>= 1
        if exponent:
            count.add("mul")
            base = base * base % p
    return result


def counted_mul(left, right, p, count):
    count.add("mul")
    return left * right % p


@dataclass
class RefSparse:
    nvars: int
    terms: dict = field(default_factory=dict)

    def clean(self, p):
        self.terms = {tuple(exp): value % p for exp, value in self.terms.items()
                      if value % p}
        return self

    def copy(self):
        return RefSparse(self.nvars, dict(self.terms))

    def add(self, other, p, scale=1, count=None):
        out = dict(self.terms)
        reduced = scale % p
        for exponent, coefficient in other.terms.items():
            if reduced == 1:
                value = coefficient
            elif reduced == p - 1:
                value = -coefficient
            else:
                if count is not None:
                    count.add("mul")
                value = reduced * coefficient
            out[exponent] = (out.get(exponent, 0) + value) % p
        return RefSparse(self.nvars, out).clean(p)

    def mul(self, other, p, count=None):
        out = {}
        for left_exp, left_value in self.terms.items():
            for right_exp, right_value in other.terms.items():
                if count is not None:
                    count.add("mul")
                exponent = tuple(a + b for a, b in zip(left_exp, right_exp))
                out[exponent] = (out.get(exponent, 0)
                                 + left_value * right_value) % p
        return RefSparse(self.nvars, out).clean(p)

    def lead(self):
        return max(self.terms) if self.terms else None

    def monic(self, p, count=None):
        if not self.terms:
            return self.copy()
        leading = self.terms[self.lead()]
        if leading == 1:
            return self.copy()
        if count is not None:
            count.add("inv")
            count.add("mul", len(self.terms))
        inverse = pow(leading, p - 2, p)
        return RefSparse(self.nvars, {
            exp: value * inverse % p for exp, value in self.terms.items()
        })


def load_terms(path):
    document = json.loads(Path(path).read_text())
    return document["S5"], document["degrees"]["S5"]


def indicator(values, p, count=None):
    coefficients = [1]
    for value in sorted(values):
        out = [0] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            if count is not None:
                count.add("mul")
            out[degree] = (out[degree] - coefficient * value) % p
            out[degree + 1] = (out[degree + 1] + coefficient) % p
        coefficients = out
    return coefficients


def indicator_sparse(coefficients, variable, nvars):
    terms = {}
    for degree, coefficient in enumerate(coefficients):
        if coefficient:
            exponent = [0] * nvars
            exponent[variable] = degree
            terms[tuple(exponent)] = coefficient
    return RefSparse(nvars, terms)


def one_var_remainder(p, coefficients, modulus, count=None):
    out = list(coefficients)
    while len(out) >= len(modulus):
        factor = out[-1] % p
        shift = len(out) - len(modulus)
        if factor:
            for index, value in enumerate(modulus):
                if count is not None:
                    count.add("mul")
                out[index + shift] = (out[index + shift] - factor * value) % p
        out.pop()
    return trim(out)


def reduce_indicator(poly, values, p, count=None):
    modulus = indicator(values, p, count)
    cache = {}
    out = RefSparse(poly.nvars, {})
    for exponent, coefficient in poly.terms.items():
        pieces = {tuple([0] * poly.nvars): coefficient % p}
        for variable, power in enumerate(exponent):
            key = (variable, power)
            if key not in cache:
                monomial = [0] * (power + 1)
                monomial[power] = 1
                cache[key] = one_var_remainder(p, monomial, modulus, count)
            next_pieces = {}
            for base, base_coefficient in pieces.items():
                for degree, degree_coefficient in enumerate(cache[key]):
                    new_exp = list(base)
                    new_exp[variable] = degree
                    new_exp = tuple(new_exp)
                    if count is not None:
                        count.add("mul")
                    next_pieces[new_exp] = (next_pieces.get(new_exp, 0)
                                            + base_coefficient * degree_coefficient) % p
            pieces = next_pieces
        out = out.add(RefSparse(poly.nvars, pieces), p)
    return out.clean(p)


def counted_sqrt(value, p, count):
    value %= p
    if value == 0:
        return 0
    if fp_pow(value, (p - 1) // 2, p, count) != 1:
        raise ValueError("reference non-residue factor-base lift")
    if p % 4 == 3:
        return fp_pow(value, (p + 1) // 4, p, count)
    odd, twos = p - 1, 0
    while odd % 2 == 0:
        odd //= 2
        twos += 1
    nonresidue = 2
    while fp_pow(nonresidue, (p - 1) // 2, p, count) != p - 1:
        nonresidue += 1
    m = twos
    c = fp_pow(nonresidue, odd, p, count)
    t = fp_pow(value, odd, p, count)
    root = fp_pow(value, (odd + 1) // 2, p, count)
    while t != 1:
        index = 1
        square = counted_mul(t, t, p, count)
        while square != 1:
            square = counted_mul(square, square, p, count)
            index += 1
        correction = fp_pow(c, 1 << (m - index - 1), p, count)
        root = counted_mul(root, correction, p, count)
        correction_square = counted_mul(correction, correction, p, count)
        t = counted_mul(t, correction_square, p, count)
        c, m = correction_square, index
    return root


def build_setup(p, a, b, values, terms_path, count):
    terms, degrees = load_terms(terms_path)
    coefficients = [RefSparse(4, {}) for _ in range(degrees[-1] + 1)]
    for term in terms:
        exponent_a, exponent_b = term[0], term[1]
        exponents = tuple(term[2:7])
        a_power = fp_pow(a, exponent_a, p, count)
        b_power = fp_pow(b, exponent_b, p, count)
        coefficient = counted_mul(term[7] % p, a_power, p, count)
        coefficient = counted_mul(coefficient, b_power, p, count)
        prefix = exponents[:4]
        coefficients[exponents[4]].terms[prefix] = (
            coefficients[exponents[4]].terms.get(prefix, 0) + coefficient) % p
    coefficients = [reduce_indicator(poly, values, p, count)
                    for poly in coefficients]
    pair_products = {}
    for left in range(9):
        for right in range(left, 9):
            product = coefficients[left].mul(coefficients[right], p, count)
            pair_products[left, right] = reduce_indicator(product, values, p, count)
    ordered = tuple(sorted(values))
    indicator_coefficients = indicator(ordered, p, count)
    points = {}
    for x in ordered:
        x_square = counted_mul(x, x, p, count)
        x_cube = counted_mul(x_square, x, p, count)
        a_x = counted_mul(a, x, p, count)
        y = counted_sqrt((x_cube + a_x + b) % p, p, count)
        points[x] = (x, min(y, p - y))
    return {
        "p": int(p), "a": int(a), "b": int(b), "V": ordered,
        "coeffs": coefficients, "pair_products": pair_products,
        "indicator": indicator_coefficients,
        "indicator_generators": tuple(
            indicator_sparse(indicator_coefficients, variable, 5)
            for variable in range(5)),
        "points": points,
    }


def setup_fingerprint(setup):
    def sparse(poly):
        return [[list(exponent), value]
                for exponent, value in sorted(poly.terms.items())]
    document = {
        "p": setup["p"], "a": setup["a"], "b": setup["b"],
        "V": list(setup["V"]), "indicator": list(setup["indicator"]),
        "coeffs": [sparse(poly) for poly in setup["coeffs"]],
        "pair_products": [
            {"pair": [left, right], "terms": sparse(setup["pair_products"][left, right])}
            for left in range(9) for right in range(left, 9)
        ],
        "points": [[x, list(setup["points"][x])] for x in sorted(setup["points"])],
    }
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def upow(field, base, exponent):
    out, current = [1], list(base)
    while exponent:
        if exponent & 1:
            out = umul(field, out, current)
        exponent >>= 1
        if exponent:
            current = umul(field, current, current)
    return out


def pseudo_basis(p, a, b, target_x, count):
    field = RefField(p, count)
    target_square = counted_mul(target_x, target_x, p, count)
    a_target = counted_mul(a, target_x, p, count)
    a_square = counted_mul(a, a, p, count)
    b_target = counted_mul(b, target_x, p, count)
    twice_b = (b + b) % p
    twice_target = (target_x + target_x) % p
    twice_a_target = (a_target + a_target) % p
    four_b = (twice_b + twice_b) % p
    four_b_target = (b_target + b_target + b_target + b_target) % p
    leading = [target_square, -twice_target % p, 1]
    linear = [-(a_target + twice_b + a_target + twice_b) % p,
              -(a + target_square + a + target_square) % p,
              -twice_target % p]
    constant = [(a_square - four_b_target) % p,
                (-twice_a_target - four_b) % p, target_square]
    alpha = [[0], [1]]
    beta = [[1], [0]]
    for _degree in range(2, 9):
        alpha.append(usub(umul(field, leading, beta[-1]),
                          umul(field, linear, alpha[-1]), p))
        beta.append(uscale(field, umul(field, constant, alpha[-2]), -1 % p))
    leading_powers = {power: upow(field, leading, power) for power in range(8)}
    scaled_alpha, scaled_beta = [], []
    for degree in range(9):
        if degree == 0:
            scaled_alpha.append([])
            scaled_beta.append(leading_powers[7])
        else:
            scale = leading_powers[8 - degree]
            scaled_alpha.append(umul(field, alpha[degree], scale))
            scaled_beta.append(umul(field, beta[degree], scale))
    return leading, linear, constant, scaled_alpha, scaled_beta, leading_powers[7]


def pair_weights(p, a, b, target_x, count):
    field = RefField(p, count)
    leading, linear, constant, alpha, beta, divisor = pseudo_basis(
        p, a, b, target_x, count)
    weights = {}
    for left in range(9):
        for right in range(left, 9):
            if left == right:
                numerator = usub(
                    uadd(field,
                         umul(field, constant, umul(field, alpha[left], alpha[left])),
                         umul(field, leading, umul(field, beta[left], beta[left]))),
                    umul(field, linear, umul(field, alpha[left], beta[left])), p)
            else:
                aa = uscale(field, umul(
                    field, constant, umul(field, alpha[left], alpha[right])), 2)
                bb = uscale(field, umul(
                    field, leading, umul(field, beta[left], beta[right])), 2)
                cross = uadd(field, umul(field, alpha[left], beta[right]),
                             umul(field, alpha[right], beta[left]))
                numerator = usub(uadd(field, aa, bb),
                                  umul(field, linear, cross), p)
            quotient, remainder = udivmod(field, numerator, divisor)
            if remainder:
                raise ArithmeticError("reference D-2 exact division failed")
            weights[left, right] = quotient
    return weights


def specialise(setup, target_x, count):
    p = setup["p"]
    weights = pair_weights(p, setup["a"], setup["b"], int(target_x), count)
    remainders, out = {}, {}
    for pair, pair_poly in setup["pair_products"].items():
        for degree, value in enumerate(weights[pair]):
            if not value:
                continue
            if degree not in remainders:
                monomial = [0] * (degree + 1)
                monomial[degree] = 1
                remainders[degree] = one_var_remainder(
                    p, monomial, setup["indicator"], count)
            for x5_degree, reduced in enumerate(remainders[degree]):
                if not reduced:
                    continue
                scalar = counted_mul(value, reduced, p, count)
                for exponent4, coefficient4 in pair_poly.terms.items():
                    exponent = tuple(exponent4) + (x5_degree,)
                    out[exponent] = (out.get(exponent, 0)
                                     + counted_mul(scalar, coefficient4, p, count)) % p
    return RefSparse(5, out).clean(p)


def zero_target(setup, count):
    p, out = setup["p"], {}
    for degree, coefficient_poly in enumerate(setup["coeffs"]):
        monomial = [0] * (degree + 1)
        monomial[degree] = 1
        remainder = one_var_remainder(p, monomial, setup["indicator"], count)
        for reduced_degree, scalar in enumerate(remainder):
            if not scalar:
                continue
            for exponent4, coefficient in coefficient_poly.terms.items():
                count.add("mul")
                exponent = tuple(exponent4) + (reduced_degree,)
                out[exponent] = (out.get(exponent, 0) + scalar * coefficient) % p
    return RefSparse(5, out).clean(p)


def poly_key(poly):
    return poly.lead(), tuple(sorted(poly.terms.items(), reverse=True))


def normal_form(poly, basis, p, count):
    work = poly.copy().clean(p)
    remainder = RefSparse(work.nvars, {})
    while work.terms:
        leading_exp = work.lead()
        reduced = False
        for divisor_poly in basis:
            divisor_exp = divisor_poly.lead()
            if divisor_exp and all(a >= b for a, b in zip(leading_exp, divisor_exp)):
                shift = tuple(a - b for a, b in zip(leading_exp, divisor_exp))
                divisor = divisor_poly.terms[divisor_exp]
                if divisor == 1:
                    coefficient = work.terms[leading_exp]
                else:
                    count.add("inv")
                    count.add("mul")
                    coefficient = (work.terms[leading_exp]
                                   * pow(divisor, p - 2, p)) % p
                shifted = RefSparse(work.nvars, {
                    tuple(a + b for a, b in zip(exp, shift)): value
                    for exp, value in divisor_poly.terms.items()
                })
                work = work.add(shifted, p, scale=-coefficient, count=count)
                count.add("reductions")
                reduced = True
                break
        if not reduced:
            remainder.terms[leading_exp] = work.terms.pop(leading_exp)
    return remainder.clean(p)


def s_polynomial(left, right, p, count):
    left_exp, right_exp = left.lead(), right.lead()
    lcm = tuple(max(a, b) for a, b in zip(left_exp, right_exp))
    left_shift = tuple(a - b for a, b in zip(lcm, left_exp))
    right_shift = tuple(a - b for a, b in zip(lcm, right_exp))
    left_coefficient, right_coefficient = left.terms[left_exp], right.terms[right_exp]
    left_inverse = 1 if left_coefficient == 1 else pow(left_coefficient, p - 2, p)
    right_inverse = 1 if right_coefficient == 1 else pow(right_coefficient, p - 2, p)
    if left_coefficient != 1:
        count.add("inv")
        count.add("mul", len(left.terms))
    if right_coefficient != 1:
        count.add("inv")
        count.add("mul", len(right.terms))
    scaled_left = RefSparse(left.nvars, {
        tuple(a + b for a, b in zip(exp, left_shift)):
            (value if left_inverse == 1 else value * left_inverse % p)
        for exp, value in left.terms.items()
    })
    scaled_right = RefSparse(right.nvars, {
        tuple(a + b for a, b in zip(exp, right_shift)):
            (value if right_inverse == 1 else value * right_inverse % p)
        for exp, value in right.terms.items()
    })
    return scaled_left.add(scaled_right, p, scale=-1, count=count)


def product_criterion(left, right):
    return all(min(a, b) == 0 for a, b in zip(left.lead(), right.lead()))


def pair_key(pair, basis):
    left, right = pair
    lcm = tuple(max(a, b) for a, b in zip(basis[left].lead(), basis[right].lead()))
    return sum(lcm), lcm, left, right


def interreduce(basis, p, count):
    work = sorted((poly.monic(p, count) for poly in basis if poly.terms),
                  key=poly_key, reverse=True)
    changed = True
    while changed:
        changed = False
        kept = []
        for index, poly in enumerate(work):
            leading = poly.lead()
            redundant = any(
                other_index != index
                and all(a >= b for a, b in zip(leading, other.lead()))
                and (leading != other.lead() or other_index < index)
                for other_index, other in enumerate(work))
            if redundant:
                changed = True
            else:
                kept.append(poly)
        work = kept
        reduced = []
        for index, poly in enumerate(work):
            others = work[:index] + work[index + 1:]
            result = normal_form(poly, others, p, count).monic(p, count)
            if not result.terms:
                changed = True
                continue
            if result.terms != poly.terms:
                changed = True
            reduced.append(result)
        work = sorted(reduced, key=poly_key, reverse=True)
    return work


def buchberger(generators, p, count):
    basis = sorted((poly.monic(p, count) for poly in generators if poly.terms),
                   key=poly_key, reverse=True)
    pairs = [(left, right) for left in range(len(basis)) for right in range(left)]
    while pairs:
        pairs.sort(key=lambda pair: pair_key(pair, basis))
        left, right = pairs.pop(0)
        if product_criterion(basis[left], basis[right]):
            count.add("product_skips")
            continue
        count.add("s_pairs")
        candidate = s_polynomial(basis[left], basis[right], p, count)
        reduced = normal_form(candidate, sorted(basis, key=poly_key, reverse=True), p, count)
        if reduced.terms:
            reduced = reduced.monic(p, count)
            new_index = len(basis)
            basis.append(reduced)
            pairs.extend((new_index, old) for old in range(new_index))
    return interreduce(basis, p, count)


def specialise_univariate(poly, current, trailing, p, count):
    specialised = {}
    for exponent, coefficient in poly.terms.items():
        value = coefficient
        for variable, fixed in trailing.items():
            power = fp_pow(fixed, exponent[variable], p, count)
            count.add("mul")
            value = value * power % p
        remaining = tuple(exponent[variable] for variable in range(current + 1))
        specialised[remaining] = (specialised.get(remaining, 0) + value) % p
    specialised = {exp: value for exp, value in specialised.items() if value}
    if any(any(exp[variable] for variable in range(current)) for exp in specialised):
        return None
    coefficients = {}
    for exponent, value in specialised.items():
        degree = exponent[current]
        coefficients[degree] = (coefficients.get(degree, 0) + value) % p
    if not coefficients:
        return []
    out = [0] * (max(coefficients) + 1)
    for degree, value in coefficients.items():
        out[degree] = value
    return trim(out)


def sparse_eval(poly, values, p, count):
    total = 0
    for exponent, coefficient in poly.terms.items():
        value = coefficient
        for coordinate, power in zip(values, exponent):
            powered = fp_pow(coordinate, power, p, count)
            count.add("mul")
            value = value * powered % p
        total = (total + value) % p
    return total


def extract_roots(basis, generators, values, p, indicator_coefficients, count):
    roots = sorted(set(int(value) % p for value in values))
    field = RefField(p, count)
    assignments = []

    def visit(current, trailing):
        common = list(indicator_coefficients)
        found = False
        for poly in basis:
            univariate = specialise_univariate(poly, current, trailing, p, count)
            if univariate is None or not univariate:
                continue
            found = True
            if len(univariate) == 1:
                return
            common = ugcd(field, common, univariate)
            if len(common) <= 1:
                return
        if not found:
            common = list(indicator_coefficients)
        candidates = [value for value in roots if ueval(field, common, value) == 0]
        for value in candidates:
            extended = dict(trailing)
            extended[current] = value
            if current:
                visit(current - 1, extended)
            else:
                xs = tuple(extended[index] for index in range(5))
                if all(sparse_eval(poly, xs, p, count) == 0 for poly in generators):
                    assignments.append(xs)

    visit(4, {})
    return sorted(set(tuple(sorted(values)) for values in assignments))


def counted_point_add(left, right, p, a, count):
    if left is None:
        return right
    if right is None:
        return left
    count.add("point_add")
    x1, y1 = left
    x2, y2 = right
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


def recover(fixture, candidates, target, points, count):
    p, a = int(fixture["p"]), int(fixture["a"])
    target = None if target is None else (int(target[0]), int(target[1]))
    negative = None if target is None else (target[0], (-target[1]) % p)
    decompositions = []
    for xs in candidates:
        for signs in itertools.product((-1, 1), repeat=5):
            total = None
            for x, sign in zip(xs, signs):
                point = points[x]
                if sign < 0:
                    point = (point[0], (-point[1]) % p)
                total = counted_point_add(total, point, p, a, count)
            if total == target or (target is not None and total == negative):
                decompositions.append({"xs": list(xs), "signs": list(signs),
                                       "target_sign": 1 if total == target else -1})
    return decompositions


def membership(fixture, target, setup):
    p = int(fixture["p"])
    counts = {component: PrimitiveCount() for component in COMPONENTS}
    target_x = None if target is None else int(target[0])
    polynomial = (zero_target(setup, counts["S"]) if target_x is None
                  else specialise(setup, target_x, counts["S"]))
    generators = [polynomial, *setup["indicator_generators"]]
    basis = buchberger(generators, p, counts["G"])
    candidates = extract_roots(
        basis, generators, setup["V"], p, setup["indicator"], counts["X"])
    decompositions = recover(fixture, candidates, target, setup["points"], counts["V"])
    return {
        "status": "ok", "member": bool(decompositions),
        "candidate_xs": [list(values) for values in candidates],
        "decompositions": decompositions, "basis_size": len(basis),
        "f6_terms": len(polynomial.terms),
        "components": {name: count.receipt() for name, count in counts.items()},
    }


def digest_label(*parts):
    label = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def is_prime(value):
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def next_prime(value):
    candidate = value + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def plain_sqrt(value, p):
    value %= p
    if value == 0:
        return 0
    if pow(value, (p - 1) // 2, p) != 1:
        raise ValueError("plain non-residue")
    if p % 4 == 3:
        return pow(value, (p + 1) // 4, p)
    odd, twos = p - 1, 0
    while odd % 2 == 0:
        odd //= 2
        twos += 1
    nonresidue = 2
    while pow(nonresidue, (p - 1) // 2, p) != p - 1:
        nonresidue += 1
    m, c = twos, pow(nonresidue, odd, p)
    t, root = pow(value, odd, p), pow(value, (odd + 1) // 2, p)
    while t != 1:
        index, square = 1, t * t % p
        while square != 1:
            square = square * square % p
            index += 1
        correction = pow(c, 1 << (m - index - 1), p)
        root, t, c, m = (root * correction % p,
                         t * correction * correction % p,
                         correction * correction % p, index)
    return root


def plain_point(p, a, b, x):
    rhs = (x**3 + a * x + b) % p
    if rhs == 0:
        return x, 0
    if pow(rhs, (p - 1) // 2, p) != 1:
        return None
    y = plain_sqrt(rhs, p)
    return x, min(y, p - y)


def plain_add(left, right, p, a):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
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


def plain_mul(scalar, point, p, a):
    out, addend = None, point
    while scalar:
        if scalar & 1:
            out = plain_add(out, addend, p, a)
        addend = plain_add(addend, addend, p, a)
        scalar >>= 1
    return out


def smoke_fixture(bits=7, wanted_l=2):
    for counter in range(1_000_000):
        value = digest_label(SMOKE, "curve", bits, wanted_l, counter)
        p = next_prime(2 ** (bits - 1) + value % 2 ** (bits - 1))
        if p.bit_length() != bits:
            continue
        a, b = (value >> 64) % p, (value >> 128) % p
        if a == 0 or b == 0 or (4 * a**3 + 27 * b**2) % p == 0:
            continue
        deck, base, bound = [], None, None
        for x in range(p):
            point = plain_point(p, a, b, x)
            if base is None and point is not None:
                base = point
            if point is not None and len(deck) < wanted_l:
                deck.append(point)
                if len(deck) == wanted_l:
                    bound = x + 1
                    break
        if len(deck) == wanted_l and base is not None:
            return {
                "fixture_id": "smoke-b%d-L%d" % (bits, wanted_l),
                "namespace": SMOKE, "bits": bits, "L": wanted_l, "B": bound,
                "counter": counter, "p": p, "a": a, "b": b,
                "target_scalar_modulus": p,
                "G": list(base), "V": [point[0] for point in deck],
            }
    raise RuntimeError("reference smoke fixture search exhausted")


def uniform(parts, modulus):
    limit = (1 << 256) // modulus * modulus
    for counter in range(1_000_000):
        value = digest_label(*parts, counter)
        if value < limit:
            return value % modulus
    raise RuntimeError("reference uniform rejection exhausted")


def target_for(fixture, attempt):
    scalar = uniform((SMOKE, "attempt", fixture["bits"], fixture["L"], attempt),
                     fixture["target_scalar_modulus"])
    target = plain_mul(scalar, tuple(fixture["G"]), fixture["p"], fixture["a"])
    return scalar, target


def expected_document(terms_path, terms_sha256):
    terms_path = Path(terms_path)
    if hashlib.sha256(terms_path.read_bytes()).hexdigest() != terms_sha256:
        raise RuntimeError("reference Semaev inventory hash mismatch")
    fixture = smoke_fixture()
    setup_count = PrimitiveCount()
    setup = build_setup(fixture["p"], fixture["a"], fixture["b"], fixture["V"],
                        terms_path, setup_count)
    queries = []
    for attempt in range(20):
        scalar, target = target_for(fixture, attempt)
        result = membership(fixture, target, setup)
        queries.append({
            "attempt": attempt, "scalar": scalar,
            "target": None if target is None else list(target),
            "result": {key: result[key] for key in (
                "status", "member", "candidate_xs", "decompositions",
                "basis_size", "f6_terms")},
            "components": result["components"],
        })
    return {
        "fixture": fixture, "terms_sha256": terms_sha256,
        "setup": {"fingerprint_sha256": setup_fingerprint(setup),
                  **setup_count.receipt()},
        "queries_completed": 20, "queries": queries,
    }


def reference_pseudo_basis(p, a, b, target_x):
    """Small offline regression hook returning arithmetic output and totals."""
    count = PrimitiveCount()
    output = pseudo_basis(p, a, b, target_x, count)
    return output, count.receipt()
