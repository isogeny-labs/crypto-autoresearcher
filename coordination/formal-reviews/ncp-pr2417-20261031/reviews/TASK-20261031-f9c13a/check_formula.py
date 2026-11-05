#!/usr/bin/env python3
"""Compare frozen blind enumeration with independently derived length formula."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "raw-minima.json").read_text())
observed = {(x["B"], x["e"], tuple(x["a"])): x for x in data}

def minimum(e, a):
    return sum(abs(x) for x in a) + (1 if e == -1 else (2 if any(x < 0 for x in a) else 0))

checks = []
for B in range(3):
    for a in itertools.product(range(-5, 6), repeat=B):
        if sum(abs(x) for x in a) > 5:
            continue
        for e in (-1, 1):
            predicted = minimum(e, a)
            seen = observed.get((B, e, a))
            actual = None if seen is None else seen["minimum_seen"]
            expected_in_window = predicted if predicted <= 5 else None
            checks.append({"B": B, "e": e, "a": list(a), "predicted": predicted,
                           "minimum_seen": actual, "matches": actual == expected_in_window})
assert all(x["matches"] for x in checks)
assert len(observed) == sum(x["predicted"] <= 5 for x in checks)
(ROOT / "formula-comparison.json").write_text(json.dumps(checks, indent=2) + "\n")
controls = []
for a, budgets in [((), (0, 1)), ((-1, 2), (4, 5)), ((2, -2), (4, 5))]:
    for e in (1, -1):
        seen = observed.get((len(a), e, a))
        for budget in budgets:
            controls.append({
                "B": len(a), "e": e, "a": list(a), "budget": budget,
                "derived_minimum": minimum(e, a),
                "enumerated_reachable_within_budget": seen is not None and seen["minimum_seen"] <= budget,
                "derived_reachable_within_budget": minimum(e, a) <= budget,
                "witness_within_length_5": None if seen is None else seen["witness"],
            })
assert all(x["enumerated_reachable_within_budget"] == x["derived_reachable_within_budget"] for x in controls)
(ROOT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
print(json.dumps({"checked_state_sign_pairs": len(checks), "mismatches": 0,
                  "observed_minima": len(observed), "outside_length_window": sum(x["predicted"] > 5 for x in checks),
                  "controls": len(controls)}, sort_keys=True))
