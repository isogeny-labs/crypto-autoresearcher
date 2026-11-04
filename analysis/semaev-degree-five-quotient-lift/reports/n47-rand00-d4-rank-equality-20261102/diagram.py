#!/usr/bin/env python3
"""Draw the checked n47 random00 D4 dimension comparison as SVG."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
result = json.loads((HERE / "evidence/result.json").read_text())
ambient = result["observed"]["columns"]
w4 = result["observed"]["rank"]
u4 = ambient - 61196
assert (ambient, w4, u4) == (213053, 151857, 151857)
scale = 620 / ambient
bars = [("Boolean space B4", ambient, "#64748b", 80),
        ("independent W4", w4, "#2563eb", 150),
        ("accepted U4 kernel", u4, "#059669", 220)]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="355" viewBox="0 0 940 355">',
         '<rect width="940" height="355" fill="white"/>',
         '<text x="28" y="38" font-family="sans-serif" font-size="20" font-weight="bold">n=47 random00: exact degree-four dimensions</text>',
         '<text x="28" y="59" font-family="sans-serif" font-size="13" fill="#475569">One named Boolean presentation; units are GF(2) dimensions</text>']
for label, value, color, y in bars:
    parts += [f'<text x="28" y="{y+4}" font-family="sans-serif" font-size="14" fill="#0f172a">{label}</text>',
              f'<rect x="230" y="{y-18}" width="{value*scale:.3f}" height="29" rx="3" fill="{color}"/>',
              f'<text x="{240+value*scale:.3f}" y="{y+3}" font-family="sans-serif" font-size="15" font-weight="bold" fill="#0f172a">{value:,}</text>']
parts += ['<line x1="230" y1="270" x2="850" y2="270" stroke="#94a3b8"/>',
          '<text x="230" y="290" font-family="sans-serif" font-size="12">0</text>',
          '<text x="775" y="290" font-family="sans-serif" font-size="12">213,053</text>',
          '<text x="28" y="322" font-family="sans-serif" font-size="13" fill="#334155">W4 is contained in U4 by the original checker. Equal dimensions prove W4 = U4.</text>',
          '<text x="28" y="343" font-family="sans-serif" font-size="11" fill="#64748b">Source: n47-rand00-independent-d4-rank-002; accepted D4 quotient SHA-256 3bdad807…</text>',
          '</svg>']
(HERE / "dimension-bridge.svg").write_text("\n".join(parts) + "\n")
