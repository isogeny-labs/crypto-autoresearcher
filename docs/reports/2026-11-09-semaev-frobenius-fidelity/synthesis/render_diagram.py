#!/usr/bin/env python3
"""Render the reviewed evidence joints and the unproved downstream bridge."""
from pathlib import Path
from html import escape

out = Path(__file__).with_name('evidence-map.svg')
boxes = [
    (20, 32, 290, 90, '#e8f3e8', 'J1 · algebra', 'Blind derivation and finite controls'),
    (330, 32, 290, 90, '#e8f0fa', 'J2 · fidelity', 'Pinned source, target and Lean type'),
    (640, 32, 290, 90, '#f4ecfa', 'J3 · machine', 'Hosted receipt, hashes and audit'),
    (230, 195, 490, 100, '#e7f4ee', 'Lemma 1 · verified', 'g^q ≡ g^φ mod (Xᵢ^q − Xᵢ), q=p^e'),
    (230, 370, 490, 100, '#fff2df', 'Next bridge · open', 'Concrete descent and degree interpretation'),
]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="950" height="510" viewBox="0 0 950 510">',
         '<rect width="950" height="510" fill="#fff"/>',
         '<text x="20" y="20" font-family="sans-serif" font-size="15" fill="#222">THM-SEMAEV-FALL1-LEMMA-1 · three independently sealed review joints</text>']
for x,y,w,h,fill,title,subtitle in boxes:
    parts += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="#455"/>',
              f'<text x="{x+14}" y="{y+34}" font-family="sans-serif" font-size="19" font-weight="bold">{escape(title)}</text>',
              f'<text x="{x+14}" y="{y+62}" font-family="sans-serif" font-size="14">{escape(subtitle)}</text>']
for x in (165,475,785):
    parts += [f'<path d="M {x} 122 L 475 195" fill="none" stroke="#566" stroke-width="2"/>']
parts += ['<path d="M 475 295 L 475 370" fill="none" stroke="#aa7830" stroke-width="2" stroke-dasharray="8 6"/>',
          '<text x="500" y="338" font-family="sans-serif" font-size="13" fill="#87551b">requires a separate theorem</text>',
          '<text x="20" y="496" font-family="sans-serif" font-size="12" fill="#555">Evidence: sealed J1/J2/J3 packets; hosted run 42665763089. Dashed edge marks an unproved implication.</text>', '</svg>']
out.write_text('\n'.join(parts)+'\n')
print(out)
