#!/usr/bin/env python3
"""Blind exhaustive word evaluation; no producer imports or formula."""
import csv
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = []
minima = {}
for B in range(3):
    alphabet = tuple(range(B)) + ("nu",)
    for length in range(6):
        for word in itertools.product(alphabet, repeat=length):
            right_nu = 0
            counts = [0] * B
            positive = [0] * B
            negative = [0] * B
            for letter in reversed(word):
                if letter == "nu":
                    right_nu += 1
                else:
                    sign = -1 if right_nu % 2 else 1
                    counts[letter] += sign
                    (positive if sign == 1 else negative)[letter] += 1
            e = -1 if right_nu % 2 else 1
            rendered = " ".join("nu" if x == "nu" else f"t{x}" for x in word)
            rows.append({
                "B": B, "length": length, "word": rendered,
                "nu_count": right_nu, "e": e,
                "a": json.dumps(counts, separators=(",", ":")),
                "positive_counts": json.dumps(positive, separators=(",", ":")),
                "negative_counts": json.dumps(negative, separators=(",", ":")),
            })
            key = (B, e, tuple(counts))
            if key not in minima:
                minima[key] = (length, rendered)

with (ROOT / "raw-words.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
minimum_rows = [
    {"B": B, "e": e, "a": list(a), "minimum_seen": val[0], "witness": val[1]}
    for (B, e, a), val in sorted(minima.items())
]
(ROOT / "raw-minima.json").write_text(json.dumps(minimum_rows, indent=2) + "\n")
summary = {
    "bounds": {"B_max": 2, "length_max": 5},
    "word_count": len(rows),
    "word_count_by_B": {str(B): sum(r["B"] == B for r in rows) for B in range(3)},
    "distinct_states_by_B": {str(B): sum(k[0] == B for k in minima) for B in range(3)},
    "evaluation": "direct right-to-left parity and integer coordinate accumulation",
}
(ROOT / "enumeration-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, sort_keys=True))
