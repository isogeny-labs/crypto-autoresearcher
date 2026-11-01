#!/usr/bin/env python3
"""Render recorded relation ranks from eight immutable checkpoint manifests."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = []
for path in root.glob('000000000000000000*.json'):
    snap = json.loads(path.read_text())['snapshot']
    rows.append((snap['sequence'], snap['relation_rank']))
rows.sort()
if [sequence for sequence, _ in rows] != list(range(1, 10)):
    raise ValueError('checkpoint sequence changed')
width, height = 660, 310
left, top, chart_w, chart_h = 92, 40, 520, 205
maximum = 60000
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#1f2937} .grid{stroke:#d1d5db;stroke-width:1} .bar{fill:#2563eb}</style>',
         '<text x="92" y="24" font-size="16" font-weight="bold">n49 polynomial00: retained relation-checkpoint ranks</text>']
for value in (0, 15000, 30000, 45000, 60000):
    y = top + chart_h - value / maximum * chart_h
    parts.append(f'<line class="grid" x1="{left}" x2="{left+chart_w}" y1="{y:.1f}" y2="{y:.1f}"/>')
    parts.append(f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" font-size="12">{value:,}</text>')
for sequence, rank in rows:
    x = left + (sequence-1)*56 + 10
    bar_h = rank / maximum * chart_h
    y = top + chart_h - bar_h
    parts.append(f'<rect class="bar" x="{x}" y="{y:.1f}" width="38" height="{bar_h:.1f}"/>')
    parts.append(f'<text x="{x+19}" y="{top+chart_h+20}" text-anchor="middle" font-size="12">{sequence}</text>')
parts += [f'<text x="{left+chart_w/2}" y="{height-14}" text-anchor="middle" font-size="12">Checkpoint sequence</text>',
          '<text x="11" y="153" transform="rotate(-90 11 153)" text-anchor="middle" font-size="12">Recorded relation rank</text>',
          '</svg>']
(root/'checkpoint-rank.svg').write_text('\n'.join(parts)+'\n')
print(rows)
