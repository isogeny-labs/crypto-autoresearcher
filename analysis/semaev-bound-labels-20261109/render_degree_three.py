from pathlib import Path
from html import escape
p=Path(__file__).parent
rows=[('Two-point Semaev family splits into unique-zero branches','If h is the branch LFD, h <= original LFD <= h+1'),('Full W3 requires repeated low-degree feedback','A one-pass cubic matrix does not certify saturation'),('W2 dimensions alone cannot force growth','A non-Semaev family shares the profile and always has LFD3'),('SAT export and supplied witness checked','1770 variables; 5610 clauses; direct lower-bound bridge gives 3')]
a=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="360"><rect width="820" height="360" fill="white"/>']
for i,(title,detail) in enumerate(rows):
 y=10+88*i;a.append(f'<rect x="15" y="{y}" width="790" height="65" rx="6" fill="#eef4f8" stroke="#536779"/><g font-family="sans-serif" fill="#172b4d"><text x="30" y="{y+25}" font-size="16">{escape(title)}</text><text x="30" y="{y+49}" font-size="13">{escape(detail)}</text></g>')
 if i<3:a.append(f'<path d="M410 {y+65}v18l-5 -5m5 5l5 -5" fill="none" stroke="#536779"/>')
a.append('</svg>');(p/'degree-three.svg').write_text(''.join(a))
