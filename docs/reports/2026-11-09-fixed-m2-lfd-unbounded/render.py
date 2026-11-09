from pathlib import Path
import json,math
p=Path(__file__).parent
rows={'R35a':{'N':36,'closure':[0,1,105,3885,61425]},'P45a':{'N':46,'closure':[0,1,224,8950,166705]}}
for r in rows.values():r['q']=[sum(math.comb(r['N'],i) for i in range(e+1))-r['closure'][e] for e in range(5)]
(p/'profiles.json').write_text(json.dumps({'source':'semaev-m2-last-fall-degree/results/verification.md','interpretation':'exact arithmetic from saved profiles; one instance per line; no new measurements', 'instances':rows},indent=2)+'\n')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="420" viewBox="0 0 760 420"><rect width="760" height="420" fill="white"/><g font-family="sans-serif" font-size="14" fill="#172b4d">','<text x="35" y="28" font-size="20">Saved degree-4 quotient filtration (not an asymptotic fit)</text>']
for j in range(5):
 y=330-65*j;s.append(f'<path d="M70 {y}H700" stroke="#ddd"/><text x="12" y="{y+5}">10^{j}</text>')
for e in range(5):s.append(f'<text x="{95+140*e}" y="355">{e}</text>')
for (name,r),color in zip(rows.items(),['#005ea8','#b54b00']):
 pts=' '.join(f'{100+140*e},{330-65*math.log10(q)}' for e,q in enumerate(r['q']));s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
 for e,q in enumerate(r['q']):s.append(f'<circle cx="{100+140*e}" cy="{330-65*math.log10(q)}" r="4" fill="{color}"/>')
s+=['<text x="290" y="382">Degree layer e (fixed closure cap D=4)</text>','<text x="80" y="405" fill="#005ea8">R35a: N=36, exact LFD=5</text><text x="390" y="405" fill="#b54b00">P45a: N=46, saved LFD≥5</text></g></svg>']
(p/'profiles.svg').write_text(''.join(s))
labels=[('Existing degree-4 certificates','Finite controls; no extrapolation'),('Exclude automatic amplification','Subfield UNSAT LFD ≤ 3; copies do not add'),('Construct a uniform vector quotient','Growing depth; rank at least D'),('Prove every generator and kernel identity','Actual field tensor; strict closure'),('Add UNSAT or SAT consequence bridge','Needed for a true LFD lower bound'),('Obtain D(n) → infinity','OPEN: no infinite construction yet')]
s=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="550"><rect width="760" height="550" fill="white"/><g font-family="sans-serif" fill="#172b4d">']
for i,(a,b) in enumerate(labels):
 y=15+i*88; fill='#edf6ee' if i<2 else '#fff4dc';s.append(f'<rect x="65" y="{y}" width="630" height="67" rx="7" fill="{fill}" stroke="#536779"/><text x="85" y="{y+26}" font-size="19">{a}</text><text x="85" y="{y+50}" font-size="15">{b}</text>')
 if i<5:s.append(f'<path d="M380 {y+67}v18l-5 -5m5 5l5 -5" stroke="#536779" fill="none"/>')
s.append('</g></svg>');(p/'proof-map.svg').write_text(''.join(s))
