#!/usr/bin/env python3
"""Render the typed-certificate evidence and remaining wire bridge."""
from pathlib import Path
from html import escape
out = Path(__file__).with_name('evidence-boundary.svg')
boxes = [
    (20,30,280,85,'#e8f3e8','J1 · blind algebra','F5 model and false controls'),
    (335,30,280,85,'#e8f0fa','J2 · source fidelity','Pinned type and source comparison'),
    (650,30,280,85,'#f4ecfa','J3 · hosted Lean','Named receipt and input closure'),
    (205,188,540,100,'#e7f4ee','Typed pair certificate · validated','Equation + declared span + group sum'),
    (205,365,540,100,'#fff2df','Serialized record · open','B1–B6: decoding, binding and execution'),
]
p=['<svg xmlns="http://www.w3.org/2000/svg" width="950" height="505" viewBox="0 0 950 505">','<rect width="950" height="505" fill="white"/>','<text x="20" y="20" font-family="sans-serif" font-size="15">THM-SEMAEV-FALL1-LEMMA-3-RAW-COORDINATES · evidence boundary</text>']
for x,y,w,h,c,title,sub in boxes:
 p += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{c}" stroke="#455"/>',f'<text x="{x+13}" y="{y+33}" font-family="sans-serif" font-size="18" font-weight="bold">{escape(title)}</text>',f'<text x="{x+13}" y="{y+60}" font-family="sans-serif" font-size="13">{escape(sub)}</text>']
for x in (160,475,790): p.append(f'<path d="M{x} 115 L475 188" fill="none" stroke="#566" stroke-width="2"/>')
p += ['<path d="M475 288 L475 365" fill="none" stroke="#a72" stroke-width="2" stroke-dasharray="8 6"/>','<text x="500" y="335" font-family="sans-serif" font-size="13" fill="#87551b">not supplied by the iff theorem</text>','<text x="20" y="492" font-family="sans-serif" font-size="12" fill="#555">Evidence: J1/J2/J3 sealed reviews, hosted run 42666660822. Dashed edge is an open proof and execution bridge.</text>','</svg>']
out.write_text('\n'.join(p)+'\n')
print(out)
