#!/usr/bin/env sage
"""Independent byte reproducer for EXP-ICEX-153c34 gate G0-1.

This verifier intentionally imports no code from ``panel_fixtures.py``.  It
implements the frozen generation rule a second time and emits the same
canonical JSON byte stream on success.
"""

import hashlib
import json
import sys

from sage.all import EllipticCurve, GF, Integer, is_prime, next_prime


DOMAIN = "EXP-ICEX-153c34/v1"
WINDOWS = {
    16: (32769, 59049), 18: (161052, 248832), 20: (537825, 759375),
    22: (2476100, 3200000), 24: (9765626, 11881376),
}
B_BY_BITS = {16: 9, 18: 12, 20: 15, 22: 20, 24: 26}
L_BY_BITS = {16: 5, 18: 6, 20: 8, 22: 10, 24: 13}


def label_integer(bits, seed, counter):
    label = "%s|curve|%d|%d|%d" % (DOMAIN, bits, seed, counter)
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def curve_order_or_rejection(p, a, b):
    if a % p == 0 or b % p == 0:
        return None, "j in {0,1728}"
    if (4 * a**3 + 27 * b**2) % p == 0:
        return None, "singular"
    order = Integer(EllipticCurve(GF(p), [a, b]).cardinality())
    if not is_prime(order):
        return order, "order not prime"
    if order == p:
        return order, "anomalous"
    if order == p + 1:
        return order, "supersingular"
    for degree in range(1, 21):
        if pow(p, degree, order) == 1:
            return order, "embedding degree %d" % degree
    return order, None


def canonical_base_point(p, a, b):
    field = GF(p)
    for x in range(p):
        rhs = field(x) ** 3 + field(a) * field(x) + field(b)
        if rhs.is_square():
            y = int(rhs.sqrt())
            return [x, min(y, p - y)]
    raise RuntimeError("no affine base point")


def has_nonzero_lift(p, a, b, x):
    rhs = (x**3 + a * x + b) % p
    return rhs != 0 and pow(rhs, (p - 1) // 2, p) == 1


def reproduce_one(bits, seed):
    wanted_b, wanted_l = B_BY_BITS[bits], L_BY_BITS[bits]
    low, high = WINDOWS[bits]
    rejected = []
    for counter in range(1_000_000):
        digest = label_integer(bits, seed, counter)
        p = int(next_prime(Integer(2 ** (bits - 1) + digest % 2 ** (bits - 1))))
        if p.bit_length() != bits:
            rejected.append({"counter": counter, "reason": "wrong bit length", "p": p})
            continue
        if p < low or p > high:
            rejected.append({"counter": counter, "reason": "outside p window", "p": p})
            continue
        a, b = (digest >> 64) % p, (digest >> 128) % p
        order, reason = curve_order_or_rejection(p, a, b)
        if reason is not None:
            rejected.append({"counter": counter, "reason": reason, "p": p})
            continue
        actual_l = sum(has_nonzero_lift(p, a, b, x) for x in range(wanted_b))
        if actual_l != wanted_l:
            rejected.append({"counter": counter,
                             "reason": "L=%d (wanted %d)" % (actual_l, wanted_l),
                             "p": p})
            continue
        return {
            "bits": bits, "seed": seed, "counter": counter, "p": p,
            "a": int(a), "b": int(b), "N": int(order), "B_star": wanted_b,
            "L_star": wanted_l, "G": canonical_base_point(p, a, b),
            "rejected_counters": rejected,
        }
    raise RuntimeError("panel fixture search exhausted for %s/%s" % (bits, seed))


def main():
    document = {
        "experiment_id": "EXP-ICEX-153c34",
        "namespace": DOMAIN,
        "generation_rule": "specification.yaml panel_fixtures.generation_rule",
        "panel": [reproduce_one(bits, seed)
                  for bits in (16, 18, 20, 22, 24)
                  for seed in (1, 2, 3, 4)],
    }
    json.dump(document, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
