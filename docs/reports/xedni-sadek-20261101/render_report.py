"""Render existing audit statements only; performs no scientific computation."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab import rl_config

# Keep compressed PDF streams binary rather than ASCII85-wrapped text.
rl_config.useA85 = 0

ROOT = Path(__file__).resolve().parent
BOXES = [
    (30, 30, 'Supplied rational data', 'E/Q, full basis, P and Gamma'),
    (30, 115, 'Coefficient bound', 'Nonzero n: prime ell divides n; |n| <= C'),
    (30, 200, 'Invalid step', 'ell <= sqrt(C): fails at n = ell = C = 3'),
    (30, 285, 'Conditional repair', 'ell <= B and k <= K imply degree <= M_star'),
    (30, 370, 'Open proof bridge', 'Admissible k, fields, zero/unit cases, full cutoff'),
]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="470" viewBox="0 0 640 470">',
       '<rect width="640" height="470" fill="white"/>']
for x,y,title,detail in BOXES:
    color = '#ffe8e3' if title == 'Invalid step' else '#edf3fa'
    svg += [f'<rect x="{x}" y="{y}" width="580" height="60" rx="7" fill="{color}" stroke="#274c77"/>',
            f'<text x="{x+16}" y="{y+23}" font-family="sans-serif" font-size="16" font-weight="bold">{title}</text>',
            f'<text x="{x+16}" y="{y+46}" font-family="sans-serif" font-size="13">{detail.replace("&", "&amp;").replace("<", "&lt;")}</text>']
    if y < 370:
        svg.append(f'<path d="M320 {y+60} v19 m-4 -5 l4 5 l4 -5" fill="none" stroke="#274c77"/>')
svg.append('<text x="30" y="454" font-family="sans-serif" font-size="12">Producer audit; independent full-proof review pending. H-XEDN-292264.</text></svg>')
(ROOT/'diagram.svg').write_text('\n'.join(svg)+'\n')

c = canvas.Canvas(str(ROOT/'report.pdf'), pagesize=(612,792))
c.setTitle('Xedni dependency-bound audit - 2026-11-01')

def text(x,y,line,size=10,bold=False):
    c.setFillColor(HexColor('#172c44'))
    c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
    c.drawString(x,y,line)

text(42,750,'Xedni: dependency-bound audit',21,True)
text(42,726,'2026-11-01 | TASK-20261101-fbd859 | H-XEDN-292264 (proposed)',9)
text(42,695,'Component progress',13,True)
for i,line in enumerate([
    'The square-root prime-divisor inference fails. A conditional integer majorant',
    'is derived separately; the complete repaired local-test theorem remains open.',
    'Historical diagnostic: 20 prime-divisor pairs, 10 square-root violations.',
    'Imported conversation evidence, not a harness RUN or independent replay.',
]): text(42,675-i*16,line)
for x,y,title,detail in BOXES:
    px,py=42,570-y*.89
    c.setFillColor(HexColor('#ffe8e3' if title=='Invalid step' else '#edf3fa'))
    c.roundRect(px,py,528,55,5,fill=1,stroke=0)
    text(px+12,py+34,title,12,True)
    text(px+12,py+14,detail,10)
    if y<370:
        c.setStrokeColor(HexColor('#274c77'))
        c.line(306,py,306,py-20)
text(42,165,'No reverse lift construction is supplied by this reduction-based test.',10)
text(42,143,'Source: Sadek, arXiv:1605.02961v1, 2016-05-10, Theorem 4.4 proof.',9)
text(42,128,'Published: C. R. Math. Rep. Acad. Sci. Canada 38(2) (2016), 75-84.',9)
text(42,113,'https://arxiv.org/pdf/1605.02961 | https://mathreports.ca/download/1173/',9)
text(42,70,'1 / 2 - Producer derivation; no official scientific status change.',9)
c.showPage()
text(42,750,'Repair hypothesis and next obligations',19,True)
lines=[
 ('Conditional arithmetic lemma',True),
 ('For integers 2 <= ell <= B, 1 <= k <= K and r >= 1:',False),
 ('(ell^2-1)(ell^2-ell) ell^(2(k+1)r+4k)',False),
 ('    <= (B^2-1)(B^2-B) B^(2(K+1)r+4K) = M_star.',False),
 ('Proof: positive monotone factors, base >= 2, increasing exponent.',False),
 ('This does not prove that an admissible uniform integer K exists.',False),
 ('',False),
 ('H-XEDN-292264: proposed full repair',True),
 ('Reconstruct a valid cutoff with certified B, admissible K and M_star.',False),
 ('Retain all Galois, GRH, full-basis and exceptional-j hypotheses.',False),
 ('Independently audit Kummer fields, integer rounding and zero/unit cases.',False),
 ('The reported gap is not a disproof of the local-to-global principle.',False),
 ('',False),
 ('Next bounded check - not launched',True),
 ('B=2..64, r=1..4, K=1..8; all prime ell<=B and integer k=1..K.',False),
 ('Exact integer comparisons; equality and invalid-domain controls.',False),
 ('Retain every tuple, values, exceptions and full resource measurements.',False),
 ('Freeze protocol and pass checkpoint/run admission before a science sweep.',False),
 ('',False),
 ('Acceptance and cost accounting',True),
 ('Local success is a filter result, not an exact rational relation certificate.',False),
 ('Charge lift search, failures, basis/height work, local tests, coefficient',False),
 ('discovery, exact verification, recovery, memory and reusable setup.',False),
 ('Unique scalar recovery from aP+bQ=O needs gcd(b,N)=1.',False),
 ('',False),
 ('Historical V2 comparison (not rerun)',True),
 ('68 doubling checks: one residue per prime. 1,944 rational fits / 24 pairs;',False),
 ('20 pairs had finite-field coefficients in [-8,8]; zero certified rational',False),
 ('dependencies in that bound. This audit does not change those results.',False),
 ('',False),
 ('Tracking and evidence',True),
 ('README.md: sources, scope, costs and obligation table.',False),
 ('prior-command.txt / prior-output.txt: actual earlier invocation/output.',False),
 ('test_bounds.py: software controls; VALIDATION.md: observed checks.',False),
 ('problems/xedni-sadek-explicit-cutoff.md: unresolved proof requirements.',False),
]
for i,(line,bold) in enumerate(lines): text(42,716-i*17,line,10,bold)
text(42,70,'2 / 2 - Independent review pending; no new lift or speedup claimed.',9)
c.save()
