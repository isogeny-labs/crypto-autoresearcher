"""Signed binary weight (Schirokauer's weight) and instance provenance."""
from __future__ import annotations

import pytest

from harness.toycurve import (
    generate_instance,
    instance_metadata,
    signed_binary_weight,
)


def _dp_min_weight(limit: int) -> list[int]:
    """Brute-force minimal signed-binary weight by dynamic programming.

    f(0) = 0 and f(n) = min over d in {-1,0,1}, (n-d) even, of
    f((n-d)/2) + [d != 0]. This is the definition, evaluated bottom-up;
    it is independent of the non-adjacent-form recurrence under test.
    """
    f = [0] * (limit + 1)
    for n in range(1, limit + 1):
        best = 1 << 30
        for d in (-1, 0, 1):
            if (n - d) % 2:
                continue
            nxt = (n - d) // 2
            if nxt < 0 or nxt >= n:
                continue
            best = min(best, f[nxt] + (1 if d else 0))
        assert best < (1 << 30), n
        f[n] = best
    return f


def test_known_weights():
    assert signed_binary_weight(1) == 1
    assert signed_binary_weight(2) == 1
    assert signed_binary_weight(3) == 2      # 4 - 1
    assert signed_binary_weight(4) == 1
    assert signed_binary_weight(5) == 2      # 4 + 1
    assert signed_binary_weight(7) == 2      # 8 - 1
    assert signed_binary_weight(15) == 2     # 16 - 1
    assert signed_binary_weight(255) == 2
    assert signed_binary_weight(2 ** 31 - 1) == 2


def test_matches_dp_minimum_up_to_5000():
    f = _dp_min_weight(5000)
    for n in range(1, 5001):
        assert signed_binary_weight(n) == f[n], n


def test_rejects_non_positive():
    for n in (0, -1, -8):
        with pytest.raises(ValueError):
            signed_binary_weight(n)


def test_instance_metadata_freezes_weight_and_curve():
    inst = generate_instance(seed=7, field_bits=8)
    block = instance_metadata(inst)
    assert block["p"] == inst.p
    assert block["a"] == inst.a
    assert block["b"] == inst.b
    assert block["field_bits"] == 8
    assert block["n"] == inst.n
    assert block["signed_binary_weight"] == signed_binary_weight(inst.p)
    assert inst.p_weight == block["signed_binary_weight"]
