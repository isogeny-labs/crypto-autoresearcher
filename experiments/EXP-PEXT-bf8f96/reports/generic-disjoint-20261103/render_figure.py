"""Draw the fixed-control generic/exceptional split from the software log."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
log = json.loads((HERE / "software-tests.json").read_text())
if log["exit_code"] != 0:
    raise SystemExit("software control did not pass")
counts = json.loads(log["stdout"].strip().splitlines()[-1])
generic, exceptional = counts["generic-disjoint"], counts["exceptional"]
total = generic + exceptional
if total != 1638:
    raise SystemExit("unexpected F27 fixed-control cardinality")
scale = 650 / total
generic_width = generic * scale
exceptional_width = exceptional * scale
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="330" viewBox="0 0 800 330">
<rect width="800" height="330" fill="#ffffff"/>
<text x="40" y="40" font-family="sans-serif" font-size="23" font-weight="bold" fill="#14213d">Exact branch-support split</text>
<text x="40" y="67" font-family="sans-serif" font-size="13" fill="#46546a">F27 fixed software control · 1,638 joined rows · no production cohort</text>
<rect x="40" y="93" width="225" height="46" rx="7" fill="#e9eef8" stroke="#8591a5"/>
<text x="53" y="121" font-family="sans-serif" font-size="14" fill="#14213d">Squarefree conjugate quartics</text>
<path d="M265 116 H296" stroke="#52627b" stroke-width="2" marker-end="url(#arrow)"/>
<rect x="298" y="93" width="198" height="46" rx="7" fill="#e9eef8" stroke="#8591a5"/>
<text x="312" y="121" font-family="sans-serif" font-size="14" fill="#14213d">Projective support gcds</text>
<path d="M496 116 H526" stroke="#52627b" stroke-width="2" marker-end="url(#arrow)"/>
<rect x="528" y="93" width="230" height="46" rx="7" fill="#e9eef8" stroke="#8591a5"/>
<text x="542" y="121" font-family="sans-serif" font-size="14" fill="#14213d">Exact generic or exception</text>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#52627b"/></marker></defs>
<text x="40" y="186" font-family="sans-serif" font-size="15" font-weight="bold" fill="#14213d">Full fixed-control classification</text>
<rect x="40" y="207" width="{generic_width:.3f}" height="42" fill="#168b72"/>
<rect x="{40+generic_width:.3f}" y="207" width="{exceptional_width:.3f}" height="42" fill="#d68832"/>
<text x="40" y="279" font-family="sans-serif" font-size="14" fill="#168b72">Generic disjoint: {generic:,} ({generic/total:.1%})</text>
<text x="384" y="279" font-family="sans-serif" font-size="14" fill="#a76118">Exceptional overlap: {exceptional:,} ({exceptional/total:.1%})</text>
<text x="40" y="309" font-family="sans-serif" font-size="12" fill="#46546a">Generic rows: exact rank 3, 12 distinct branch points, genus 17; exceptional rows require full analysis.</text>
</svg>'''
(HERE / "figure.svg").write_text(svg)
