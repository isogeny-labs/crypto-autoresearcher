from pathlib import Path
from html import escape
p=Path(__file__).parent
rows=[('Original normalized input + quotient columns C','No T/R matrices or solver verdict trusted'),('Separate evaluation reconstruction of S3','Check generator annihilation, quotient rank and C(1)'),('Entire low-degree kernel basis','Check every permitted variable product of every relation'),('Scoped result and explicit refusal states','Nonmembership + codimension lower bound; LFD remains unknown')]
a=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="360"><rect width="800" height="360" fill="white"/>']
for i,(title,detail) in enumerate(rows):
 y=10+88*i;a.append(f'<rect x="20" y="{y}" width="760" height="65" rx="6" fill="#eef4f8" stroke="#536779"/><g font-family="sans-serif" fill="#172b4d"><text x="35" y="{y+25}" font-size="17">{escape(title)}</text><text x="35" y="{y+49}" font-size="14">{escape(detail)}</text></g>')
 if i<3:a.append(f'<path d="M400 {y+65}v18l-5 -5m5 5l5 -5" fill="none" stroke="#536779"/>')
a.append('</svg>');(p/'direct-check.svg').write_text(''.join(a))
