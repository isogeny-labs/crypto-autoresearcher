from pathlib import Path
p=Path(__file__).parent
rows=[('General normalized binary m=2, dim(V)=k','Set s=X+Y; every fibre is affine in X'),('Quartic homogeneous map, leading coefficient 1','At most four solutions; at most two free bits per fibre'),('Selector/free-bit normal forms','Degree at most k+2; multiplication reduces at cap k+3'),('All ideal consequences controlled','LFD ≤ k+3 for SAT and UNSAT'),('Structured subfamily: V=H, [K:H]=2, z outside H','At most four total points; stronger LFD ≤ 3')]
s=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="450"><rect width="760" height="450" fill="white"/><g font-family="sans-serif" fill="#172b4d">']
for i,(a,b) in enumerate(rows):
 y=10+i*88;s.append(f'<rect x="35" y="{y}" width="690" height="66" rx="7" fill="#eaf3fb" stroke="#526778"/><text x="52" y="{y+25}" font-size="18">{a}</text><text x="52" y="{y+49}" font-size="16">{b}</text>')
 if i<4:s.append(f'<path d="M380 {y+66}v19l-5 -5m5 5l5 -5" stroke="#526778" fill="none"/>')
s.append('</g></svg>');(p/'bounds.svg').write_text(''.join(s))
