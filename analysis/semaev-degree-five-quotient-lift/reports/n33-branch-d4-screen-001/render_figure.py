#!/usr/bin/env python3
"""Render the exact D4 branch-result chart from evidence.json."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
evidence = json.loads((here / "evidence.json").read_text())
assert evidence["status"] == "independently_reproduced_exact_lfd5"
for branch in (0, 1):
    native = next(r for r in evidence["rows"] if r["arm"] == f"a0-{branch}")
    independent = next(r for r in evidence["rows"] if r["arm"] == f"full-independent-{branch}")
    assert native["dims"] == independent["dims"] == [1, 34, 562, 6018, 46938]

# The original value is a certified lower bound, not a measured exact codimension.
bars = [("Original D4", 4888, "#315d9d"),
        ("a0 = 0, D4", 0, "#23835b"),
        ("a0 = 1, D4", 0, "#23835b")]
lines = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="390" viewBox="0 0 800 390">',
    '<rect width="800" height="390" fill="white"/>',
    '<text x="28" y="38" font-family="sans-serif" font-size="21" font-weight="bold">Degree-four quotient dimension</text>',
    '<text x="28" y="64" font-family="sans-serif" font-size="14">fresh-n33-tr0-01; original is a checked lower bound, branches are exact full-closure results</text>',
]
for i, (label, value, color) in enumerate(bars):
    y = 105 + i * 83
    width = 530 * value / 5000
    lines.append(f'<text x="28" y="{y+24}" font-family="sans-serif" font-size="16">{label}</text>')
    lines.append(f'<rect x="190" y="{y}" width="530" height="34" fill="#edf0f3"/>')
    if value:
        lines.append(f'<rect x="190" y="{y}" width="{width:.1f}" height="34" fill="{color}"/>')
    lines.append(f'<text x="{max(202, 200+width):.1f}" y="{y+24}" font-family="sans-serif" font-size="16" fill="#18212b">{value:,}</text>')
lines.append('<text x="28" y="365" font-family="sans-serif" font-size="13">Unit: F₂ dimension. Both branches: 1 ∈ W₄, so codimension 0. Original: 1 ∉ W₄.</text>')
lines.append('</svg>')
(here / "figure.svg").write_text("\n".join(lines) + "\n")
