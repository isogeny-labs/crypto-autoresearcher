"""Render the final checked-publication coverage record and static figure."""

import json
from pathlib import Path

import typst


study = Path('analysis/semaev-degree-five-quotient-lift')
source = study / 'validation/publication-coverage-20261101-final-001/publication-coverage.json'
out = study / 'reports/publication-coverage-final-20261101'
out.mkdir(parents=True, exist_ok=True)
record = json.loads(source.read_text())
assert record['mapped_public_locations'] == record['certified_lower_bound_certificates'] == 63
assert record['dual_location_count'] == 2
assert record['modes'] == {
    'separate_gzip_certificate': 51,
    'evidence_archive_with_verified_member': 6,
    'evidence_archive_with_certificate': 6,
}
assert len(record['rows']) == 63

report = '''# Public certificate coverage for the completed D4 panel

The [final panel audit](../../validation/panel-coverage-20261101-final-001/coverage.json) lists 63 named n=33–45 inputs with checked LFD lower bounds of at least five. This [publication audit](../../validation/publication-coverage-20261101-final-001/publication-coverage.json) maps all **63 certificates** to checked public locations: 51 separate gzip certificate assets, six evidence archives with a verified certificate member, and six evidence archives with a previously checked certificate. Two n=42 certificates also occur in the original worker bundle; both locations were checked and each input is counted once.

The audit rechecks the retained archive content, worker bundle, result hashes, and committed publication receipts. The receipts record earlier anonymous HTTPS download and hash checks; this audit did not repeat those downloads. Publication coverage establishes custody and availability of the finite-instance certificates. The mathematical bounds rest on their separate checker acceptances and exact solution counts in the panel records.
'''
(out / 'report.md').write_text(report + '\n![Certificate location modes](flow.svg)\n')

segments = [
    ('Separate gzip certificate', 51, '#286b9a'),
    ('Verified archive member', 6, '#399675'),
    ('Checked evidence archive', 6, '#9f6b31'),
]
x = 40
bars = []
legend = []
for index, (label, count, color) in enumerate(segments):
    width = 800 * count / 63
    bars.append(f'<rect x="{x:.2f}" y="85" width="{width:.2f}" height="48" fill="{color}"/>')
    legend.append(f'<rect x="40" y="{160+index*32}" width="18" height="18" fill="{color}"/><text x="68" y="{175+index*32}" font-family="sans-serif" font-size="16" fill="#17222f">{label}: {count}</text>')
    x += width
(out / 'flow.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="280" viewBox="0 0 900 280" role="img" aria-label="63 of 63 certified D4 results have checked public certificate locations">
<rect width="900" height="280" fill="white"/>
<text x="40" y="38" font-family="sans-serif" font-size="22" fill="#17222f">Public locations for 63 checked D4 certificates</text>
<text x="40" y="64" font-family="sans-serif" font-size="15" fill="#526273">140 frozen inputs: 63 certified lower bounds, all 63 mapped</text>
''' + '\n'.join(bars + legend) + '''
<text x="40" y="270" font-family="sans-serif" font-size="13" fill="#526273">Two n42 certificates also have verified worker-bundle locations; each is counted once.</text>
</svg>''')

typ = '''#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
= Public certificate coverage for the completed D4 panel
The final n=33–45 panel audit records 63 checked LFD-at-least-five certificates among 140 frozen inputs. The publication audit maps all 63 to checked public locations: 51 separate gzip certificates, six evidence archives with a verified certificate member, and six evidence archives with a previously checked certificate. Two n42 certificates also have verified locations in the original worker bundle and are counted once.

#image("flow.svg", width: 100%)

This audit checks retained archives, the worker bundle, result hashes, and committed publication receipts. It relies on the receipts' earlier anonymous HTTPS download checks and does not perform fresh downloads. The mathematical claims remain tied to the separate certificate checkers and exact counts in the panel records.
'''
(out / 'report.typ').write_text(typ)
typst.compile(str(out / 'report.typ'), output=str(out / 'report.pdf'))
