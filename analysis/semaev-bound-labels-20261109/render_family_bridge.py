from pathlib import Path
from html import escape
p=Path(__file__).parent
rows=[('Exactly two solutions: every odd n >= 3','Some dim-(n+1)/2 subspace containing 1; basis selection existential'),('UNSAT with nonzero restricted trace: infinitely many odd n','Avoids the single constant trace contradiction; other easy proofs may remain'),('Checked quotient rank q exceeds valid solution capacity U','Direct closure check + count dimension argument implies LFD >= D+1'),('Growing LFD remains a separate obligation','Order-four target; no prime-order-target or efficient-basis theorem')]
a=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="360"><rect width="820" height="360" fill="white"/>']
for i,(title,detail) in enumerate(rows):
 y=10+88*i;a.append(f'<rect x="15" y="{y}" width="790" height="65" rx="6" fill="#eef4f8" stroke="#536779"/><g font-family="sans-serif" fill="#172b4d"><text x="30" y="{y+25}" font-size="16">{escape(title)}</text><text x="30" y="{y+49}" font-size="13">{escape(detail)}</text></g>')
a.append('</svg>');(p/'family-bridge.svg').write_text(''.join(a))
