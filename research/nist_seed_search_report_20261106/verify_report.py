"""Validate the report and its embedded evidence; launches no scientific programs."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

import pdfplumber
from pypdf import PdfReader

B = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pdf', type=Path, default=B / 'output/pdf/nist-seed-selection-search-comprehensive-report.pdf')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
r = PdfReader(str(args.pdf))
assert len(r.pages) == 61
assert set(r.attachments) == {'source-manifest.json', 'cohort.json', 'source-report-bundle.zip', 'retained-fit-catalog.json'}
manifest = json.loads(r.attachments['source-manifest.json'][0])
assert manifest == json.loads((B / 'source-manifest.json').read_text())
cohort = json.loads(r.attachments['cohort.json'][0])
assert len(cohort) == 21
assert sum(c['label'] == 'omitted' for c in cohort) == 11
with zipfile.ZipFile(io.BytesIO(r.attachments['source-report-bundle.zip'][0])) as z:
    for source in manifest['sources']:
        assert hashlib.sha256(z.read(source['path'])).hexdigest() == source['sha256']
    assert json.loads(z.read('cohort.json')) == cohort
    assert json.loads(z.read('source-manifest.json')) == manifest
from fit_catalog import load_catalog
catalog = load_catalog(B)
assert json.loads(r.attachments['retained-fit-catalog.json'][0]) == catalog
with zipfile.ZipFile(io.BytesIO(r.attachments['source-report-bundle.zip'][0])) as z:
    for name, digest in json.loads((B / 'inputs/build-inputs.json').read_text())['retained_fit_inputs'].items():
        assert hashlib.sha256(z.read('inputs/' + name)).hexdigest() == digest
text = '\n'.join(page.extract_text() or '' for page in r.pages)
flat = re.sub(r'\s+', '', text)
for row in cohort:
    assert row['seed_hex'] in flat and row['curve_uid'] in flat
    for key in ('p', 'b', 'c', 'n'):
        assert format(int(row[key]), 'x') in flat
assert 'Historical criterion: UNRESOLVED' in text
assert 'C199 <= 32 and D199 <= 2048' in text
assert 'ramified' in text and 'post-observation' in text
appendix = '\n'.join(p.extract_text() or '' for p in r.pages[43:])
appendix_flat = re.sub(r'\s+', '', appendix)
for pair in catalog['pairs']:
    assert pair['id'] in appendix
    assert not pair['historical_use_verified']
    for table in pair['truth_tables']:
        assert table['id'] in appendix
    for alias in pair['a_aliases'] + pair['b_aliases']:
        assert alias['name'] in appendix_flat
assert catalog['pair_count'] == 16 and catalog['truth_table_instances'] == 19
assert catalog['unique_alias_count'] == 54 and not catalog['new_search_performed']
assert '\u25a0' not in text and '\ufffd' not in text
with pdfplumber.open(args.pdf) as pdf:
    for number, page in enumerate(pdf.pages, 1):
        outside = [c for c in page.chars if c['x0'] < 40 or c['x1'] > page.width-40 or c['top'] < 15 or c['bottom'] > page.height-15]
        assert not outside, ('out-of-bounds text', number)
result = {
    'status': 'PASS', 'pages': len(r.pages), 'sources_verified': len(manifest['sources']),
    'cohort_rows': len(cohort), 'all_exact_uids_and_parameters_present': True,
    'embedded_evidence_hashes': 'PASS', 'page_boundaries': 'PASS',
    'historical_criterion': 'UNRESOLVED', 'prime_199_fit_discussion_present': True,
    'retained_pairs_verified': 16, 'table_instances_verified': 19, 'unique_aliases_present': 54,
    'new_predicate_search': False, 'new_scientific_trials': 0, 'pdf_sha256': hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
}
if args.output:
    args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
