from pathlib import Path
p=Path(__file__).parent
rows=[('Bind exact input presentation','Field basis, row operations, normalization, field equations'),('Classify homogeneous fibres','s ≠ 0: dimension 2 iff z=u v, u≠v, u+v=s'),('Product-excluded target control','z outside distinct products ⇒ all-instance LFD ≤ k+2'),('Keep FFD observables separate','Nonzero fall / top syzygy / new closure class'),('Finite presentation counterexample','Same F16 Semaev ideal: PQ FFD and LFD 2 → 1')]
a=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="450"><rect width="760" height="450" fill="white"/><g font-family="sans-serif" fill="#172b4d">']
for i,(s,t) in enumerate(rows):
 y=10+88*i;a.append(f'<rect x="30" y="{y}" width="700" height="66" rx="6" fill="#edf4f8" stroke="#536779"/><text x="45" y="{y+25}" font-size="18">{s}</text><text x="45" y="{y+49}" font-size="15">{t}</text>')
 if i<4:a.append(f'<path d="M380 {y+66}v18l-5 -5m5 5l5 -5" stroke="#536779" fill="none"/>')
a.append('</g></svg>');(p/'labels.svg').write_text(''.join(a))
