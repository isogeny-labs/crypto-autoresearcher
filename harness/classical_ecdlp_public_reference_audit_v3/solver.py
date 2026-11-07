#!/usr/bin/env python3
"""Public-only finite certificate search: HAC 3.56, SEC1 2.2.1.

No candidate implementation, retained prediction, private scalar or cost model
is an input. Timers below enforce the process watchdog only.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def reject_number(value):
    raise ValueError('noninteger/nonfinite input token: ' + value)


def integer(value):
    return type(value) is int


def prime(n):
    if not integer(n) or not 2 <= n <= 1 << 20:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


def inverse(n, modulus):
    old_r, r, old_t, t = modulus, n % modulus, 0, 1
    while r:
        quotient = old_r // r
        old_r, r, old_t, t = r, old_r - quotient * r, t, old_t - quotient * t
    if old_r != 1:
        raise ValueError('inverse does not exist')
    return old_t % modulus


class Curve:
    def __init__(self, p, a, b, r, base):
        if not (prime(p) and p > 3 and prime(r)):
            raise ValueError('bounded prime field/order required')
        if not all(integer(v) and 0 <= v < p for v in (a, b)):
            raise ValueError('noncanonical curve coefficients')
        if (4 * a ** 3 + 27 * b ** 2) % p == 0:
            raise ValueError('singular curve')
        self.p, self.a, self.b, self.r = p, a, b, r
        self.base = self.point(base, allow_identity=False)
        if self.multiply(r, self.base) is not None:
            raise ValueError('base order does not divide the declared prime r')

    def point(self, value, allow_identity=True):
        if value is None:
            if allow_identity:
                return None
            raise ValueError('identity prohibited here')
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError('point must have two coordinates')
        x, y = value
        if not all(integer(v) and 0 <= v < self.p for v in (x, y)):
            raise ValueError('noncanonical point coordinates')
        if (y * y - x ** 3 - self.a * x - self.b) % self.p:
            raise ValueError('off-curve point')
        return x, y

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            slope = (3 * x1 * x1 + self.a) * inverse(2 * y1, self.p)
        else:
            slope = (y2 - y1) * inverse(x2 - x1, self.p)
        slope %= self.p
        x3 = (slope * slope - x1 - x2) % self.p
        return x3, (slope * (x1 - x3) - y1) % self.p

    def multiply(self, scalar, point):
        if not integer(scalar) or scalar < 0:
            raise ValueError('nonnegative integer scalar required')
        # Deliberately no reduction modulo r: order checks must not be tautologies.
        result, current, remaining = None, point, scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, current)
            current = self.add(current, current)
            remaining >>= 1
        return result


class BabyGiant:
    def __init__(self, curve):
        self.curve = curve
        self.width = math.isqrt(curve.r - 1) + 1
        self.babies = {}
        current = None
        for j in range(self.width):
            if current in self.babies:
                raise ValueError('unexpected repeated baby step')
            self.babies[current] = j
            current = curve.add(current, curve.base)
        self.stride = None if current is None else (current[0], -current[1] % curve.p)

    def solve(self, target):
        target = self.curve.point(target)
        if self.curve.multiply(self.curve.r, target) is not None:
            raise ValueError('target not killed by r')
        current = target
        for i in range(self.width):
            j = self.babies.get(current)
            if j is not None:
                scalar = i * self.width + j
                if scalar < self.curve.r and self.curve.multiply(scalar, self.curve.base) == target:
                    return scalar
            current = self.curve.add(current, self.stride)
        raise ValueError('no logarithm in the complete bounded search')


def required_rejection(function):
    try:
        function()
    except (ValueError, TypeError):
        return True
    raise ValueError('negative control was accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-input', required=True, type=Path)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    deadline = started + float(os.environ.get('REFERENCE_TIME_LIMIT', '1200'))
    raw = args.public_input.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != args.expected_sha256:
        raise ValueError('public input digest mismatch')
    document = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                          parse_float=reject_number, parse_constant=reject_number)
    if document.get('schema') != 'controlled-followup-v5.public-input/v1':
        raise ValueError('unexpected public input schema')
    public = document['public']
    groups = public['curves']
    if len(groups) != 48 or len({g['curve_id'] for g in groups}) != 48:
        raise ValueError('public domain inventory mismatch')
    records, controls = [], []
    target_total = target_curves = 0
    for group in groups:
        if time.monotonic() >= deadline:
            raise TimeoutError('original process watchdog reached')
        model = group['model']
        curve = Curve(*(model[k] for k in ('p', 'a', 'b', 'r')), group['base'])
        search = BabyGiant(curve)
        planted = []
        for scalar in (0, 1, curve.r - 1, curve.r // 2):
            point = curve.multiply(scalar, curve.base)
            found = search.solve(point)
            if found != scalar:
                raise ValueError('positive control logarithm mismatch')
            planted.append([scalar, point, found])
        off_curve = (0, 0) if curve.b else (0, 1)
        required_rejection(lambda: search.solve(off_curve))
        required_rejection(lambda: curve.point((curve.p, 0)))
        required_rejection(lambda: Curve(curve.p, curve.a, curve.b, 2 * curve.r, curve.base))
        controls.append({'curve_id': group['curve_id'], 'known_scalar_cases': planted,
                         'offcurve_rejected': True, 'noncanonical_point_rejected': True,
                         'composite_order_rejected': True})
        rows, seen = [], set()
        for target in group['targets']:
            tid = target['target_id']
            if tid in seen:
                raise ValueError('duplicate target id within a domain')
            seen.add(tid)
            point = curve.point(target['point'], allow_identity=False)
            scalar = search.solve(point)
            if curve.multiply(scalar, curve.base) != point:
                raise ValueError('direct certificate equation failed')
            rows.append([tid, scalar])
        target_total += len(rows)
        target_curves += bool(rows)
        records.append({'curve_id': group['curve_id'], 'scalars': rows})
    if target_total != 1536 or target_curves != 24:
        raise ValueError('public target inventory mismatch')
    toy = Curve(17, 2, 2, 19, (5, 1))
    if toy.multiply(2, toy.base) != (6, 3) or BabyGiant(toy).solve((6, 3)) != 2:
        raise ValueError('external known-point control failed')
    yzero = Curve(17, 1, 0, 2, (0, 0))
    if yzero.add(yzero.base, yzero.base) is not None or BabyGiant(yzero).solve(yzero.base) != 1:
        raise ValueError('y=0 control failed')
    result = {'schema': 'classical.ecdlp.public-reference-certificates/v1',
              'public_input_sha256': digest, 'public_input_bytes': len(raw),
              'method': 'HAC Algorithm 3.56; affine SEC1 group law; direct original equations',
              'curves': records, 'controls': controls,
              'fixed_controls': {'F17_2G': [6, 3], 'F17_log_2G': 2,
                                 'F17_yzero_doubles_to_identity': True},
              'scope': 'Exact finite certificates only; no performance metrics or new algorithm claim.'}
    encoded = (json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(encoded)
    print(json.dumps({'certificate_file_sha256': hashlib.sha256(encoded).hexdigest(),
                      'domains': len(records), 'target_curves': target_curves,
                      'targets': target_total, 'controls_passed': True}))


if __name__ == '__main__':
    main()
