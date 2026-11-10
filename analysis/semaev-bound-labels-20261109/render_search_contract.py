from pathlib import Path
from html import escape
p=Path(__file__).parent
rows=[('Exact normalized Semaev input','Full vector space; exact polynomial and input hashes'),('Choose finite degree D and quotient rank q','Preflight unknown, equation and term limits'),('Encode C, partial multiplication T, right inverse R','Unit separation + generator annihilation + full closure + rank'),('Future solver proposes a candidate','No solver executed in this packet'),('Independent certificate and bridge checks required','Kernel closure + UNSAT, solution bound or missing consequence'),('Growing family remains open','Finite feasibility is not an asymptotic theorem')]
s=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="540"><rect width="800" height="540" fill="white"/>']
for i,(title,detail) in enumerate(rows):
 y=10+88*i
 s.append(f'<rect x="20" y="{y}" width="760" height="65" rx="6" fill="#eef4f8" stroke="#536779"/><g font-family="sans-serif" fill="#172b4d"><text x="35" y="{y+25}" font-size="17">{escape(title)}</text><text x="35" y="{y+49}" font-size="14">{escape(detail)}</text></g>')
 if i<5:s.append(f'<path d="M400 {y+65}v18l-5 -5m5 5l5 -5" fill="none" stroke="#536779"/>')
s.append('</svg>');(p/'search-contract.svg').write_text(''.join(s))
