#!/usr/bin/env python3
"""Draw trials.svg from the four execution-receipt.json files this session wrote.

Values are read from the receipts (started_at/finished_at/status); nothing is
recomputed or modelled. Run from the repository root:

    python3 experiments/EXP-PEXT-212d5c/reports/run-20261115T0426Z/make_graph.py
"""
import datetime
import json
import pathlib

RUNS = ["RUN-PEXT-63ca6a", "RUN-PEXT-056770", "RUN-PEXT-708f11", "RUN-PEXT-3fd19f"]
LABELS = {
    "RUN-PEXT-63ca6a": "regression",
    "RUN-PEXT-056770": "construct",
    "RUN-PEXT-708f11": "char2",
    "RUN-PEXT-3fd19f": "census",
}
COLORS = {"output_validated": "#2f6f4f", "interrupted": "#b8860b"}
ROOT = pathlib.Path(__file__).resolve().parents[4]
W, H = 760, 430
LEFT, RIGHT, TOP, BOTTOM = 80, 730, 70, 350

rows = []
for run in RUNS:
    receipt = ROOT / "experiments/EXP-PEXT-212d5c/runs" / run / "execution-receipt.json"
    data = json.loads(receipt.read_text())
    start = datetime.datetime.fromisoformat(data["started_at"])
    finish = datetime.datetime.fromisoformat(data["finished_at"])
    rows.append((run, data["status"], (finish - start).total_seconds()))

peak = max(seconds for _, _, seconds in rows)
bar_w = 96
gap = (RIGHT - LEFT - bar_w * len(rows)) / (len(rows) + 1)
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
    '<text x="80" y="28" font-size="15" font-weight="bold" fill="#1b1b1b">'
    'EXP-PEXT-212d5c: wall time per run directory, 2026-11-15 session</text>',
    '<text x="80" y="46" font-size="11" fill="#5a5a5a">'
    'measured from each execution-receipt.json started_at/finished_at; census bar is the interrupted segment only</text>',
]
for tick in range(0, int(peak) + 1, 300):
    y = BOTTOM - (BOTTOM - TOP) * tick / peak
    parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{RIGHT}" y2="{y:.1f}" stroke="#e2e2e2"/>')
    parts.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" font-size="10" text-anchor="end" fill="#5a5a5a">{tick}</text>')
parts.append(f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{BOTTOM}" stroke="#333" stroke-width="1.2"/>')
parts.append(f'<line x1="{LEFT}" y1="{BOTTOM}" x2="{RIGHT}" y2="{BOTTOM}" stroke="#333" stroke-width="1.2"/>')
parts.append(f'<text x="18" y="{(TOP + BOTTOM) / 2:.0f}" font-size="11" fill="#333" '
             f'transform="rotate(-90 18 {(TOP + BOTTOM) / 2:.0f})" text-anchor="middle">wall seconds</text>')
for index, (run, status, seconds) in enumerate(rows):
    x = LEFT + gap + index * (bar_w + gap)
    height = (BOTTOM - TOP) * seconds / peak
    y = BOTTOM - height
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{height:.1f}" '
                 f'fill="{COLORS.get(status, "#888")}"/>')
    parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 6:.1f}" font-size="11" text-anchor="middle" fill="#1b1b1b">'
                 f'{seconds:.0f} s</text>')
    parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{BOTTOM + 16}" font-size="11" text-anchor="middle" fill="#1b1b1b">'
                 f'{LABELS[run]}</text>')
    parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{BOTTOM + 31}" font-size="9" text-anchor="middle" fill="#5a5a5a">'
                 f'{run}</text>')
    parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{BOTTOM + 45}" font-size="9" text-anchor="middle" fill="#5a5a5a">'
                 f'{status.replace("_", " ")}</text>')
parts.append('<text x="80" y="410" font-size="10" fill="#5a5a5a">'
             'lean (RUN-PEXT-2723eb) and analyze (RUN-PEXT-422517) were not launched; no bar exists for them.</text>')
parts.append("</svg>")
(pathlib.Path(__file__).resolve().parent / "trials.svg").write_text("\n".join(parts) + "\n")
for run, status, seconds in rows:
    print(run, status, f"{seconds:.0f}s")
