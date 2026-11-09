"""Independent deterministic draw replay for a retained prospective C7 row.

The draw stream and rejection accounting are reconstructed here rather than
calling the producer sampler. This module performs no sampling on import.
"""

import hashlib
import json

from check_quotient_certificate import Field, trim
from c7_matched_random import (COEFFICIENT_BLOCK_CAP, DRAW_CAP, PATTERNS, SAMPLES_PER_STRATUM,
                               SEED, check_form, factor_pattern)
from generic_disjoint import squarefree
from squareclass_relations import coefficient_bit


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def _draw(field, label, attempt, position):
    limit = (1 << 32) - ((1 << 32) % field.size)
    if limit == 0:
        raise ValueError("C7 field exceeds counter word range")
    for block in range(COEFFICIENT_BLOCK_CAP):
        message = _json(["pext-c7-sha256-counter/v1", SEED, label,
                         attempt, position, block])
        word = int.from_bytes(hashlib.sha256(message).digest()[0:4], "little")
        if word < limit:
            return word % field.size
    raise ValueError("C7 coefficient rejection block cap exhausted")


def replay(field_record, record):
    """Recreate every attempted draw and require exact record equality."""
    if type(record) is not dict or record.get("schema") != "pext.c7-matched-random/v1":
        raise ValueError("C7 record schema mismatch")
    field = Field(field_record)
    pattern = record.get("pattern")
    scalar_class = record.get("scalar_class")
    count = record.get("requested")
    if (type(pattern) is not list or tuple(pattern) not in PATTERNS
            or type(scalar_class) is not int or scalar_class not in (0, 1)
            or type(count) is not int or not 1 <= count <= SAMPLES_PER_STRATUM):
        raise ValueError("C7 stratum or requested count invalid")
    field_hash = hashlib.sha256(_json(field_record)).hexdigest()
    label = [field_hash, pattern, scalar_class]
    nonsquare = next(value for value in range(1, field.size)
                     if coefficient_bit(field, value) == 1)
    selected, seen = [], set()
    attempted = invalid = wrong = flips = duplicates = 0
    for attempt in range(DRAW_CAP):
        if len(selected) == count:
            break
        attempted += 1
        form = [_draw(field, label, attempt, position) for position in range(5)]
        try:
            squarefree(field, form)
        except ValueError:
            invalid += 1
            continue
        if coefficient_bit(field, trim(form)[-1]) != scalar_class:
            form = [field.mul(coefficient, nonsquare) for coefficient in form]
            flips += 1
        if factor_pattern(field, form) != tuple(pattern):
            wrong += 1
            continue
        if tuple(form) in seen:
            duplicates += 1
            continue
        seen.add(tuple(form))
        selected.append({"draw": attempt, "form": form,
                         "check": check_form(field, form)})
    expected = {"schema": "pext.c7-matched-random/v1", "seed": SEED,
                "field_sha256": field_hash, "pattern": pattern,
                "scalar_class": scalar_class, "draw_cap": DRAW_CAP,
                "requested": count, "attempted": attempted,
                "invalid_squarefree": invalid, "wrong_pattern": wrong,
                "scalar_flips": flips, "duplicate": duplicates,
                "selected": selected,
                "status": ("control_complete" if len(selected) == count
                           else "inconclusive_draw_cap_exhausted")}
    if record != expected:
        raise ValueError("C7 retained record differs from independent seed replay")
    return {"valid": True, "field_sha256": field_hash,
            "record_sha256": hashlib.sha256(_json(record)).hexdigest(),
            "selected": len(selected), "attempted": attempted}
