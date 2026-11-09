from pathlib import Path
from html import escape
p=Path(__file__).parent
rows=[('Odd diagonal: span(V V) equals the full field','The trace bilinear form rules out a nonzero product annihilator'),('Nonexceptional W2 has only the affine trace relation','Containing 1 excludes the rank-one exception automatically'),('Known two-point ideal needs 2k-1 affine generators','At least one is missing from W2: LFD is at least three'),('Fixed F8 control attains three','Rank-five lower witness; cap-three upper identities; no search')]
a=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="360"><rect width="820" height="360" fill="white"/>']
for i,(title,detail) in enumerate(rows):
 y=10+88*i;a.append(f'<rect x="15" y="{y}" width="790" height="65" rx="6" fill="#eef4f8" stroke="#536779"/><g font-family="sans-serif" fill="#172b4d"><text x="30" y="{y+25}" font-size="16">{escape(title)}</text><text x="30" y="{y+49}" font-size="13">{escape(detail)}</text></g>')
 if i<3:a.append(f'<path d="M410 {y+65}v18l-5 -5m5 5l5 -5" fill="none" stroke="#536779"/>')
a.append('</svg>');(p/'degree-two.svg').write_text(''.join(a))
