#!/usr/bin/env python3
"""Audit public locations for the completed 140-input D4 panel.

The artifact root holds retained public archives and the historical worker
bundle. Repository publication receipts are checked byte-for-byte against it.
This reuses historical full-download receipts; it does not redownload assets.
"""

import argparse
import collections
import datetime
import json
from pathlib import Path

import audit_publication_coverage as base


STUDY = Path('analysis/semaev-degree-five-quotient-lift')
COVERAGE = STUDY / 'validation/panel-coverage-20261101-final-001/coverage.json'
DEFAULT_OUT = STUDY / 'validation/publication-coverage-20261101-final-001'
RECEIPT_DIRS = [
    Path('analysis/semaev-m2-last-fall-degree/submission-20261029/archive'),
    STUDY / 'panel-archive',
    STUDY / 'panel-local-archive-001',
]
BUNDLE_RELATIVE = STUDY / 'runtime/semaev-panel-worker-20261029.tar.gz'
BUNDLE_RECEIPT = STUDY / 'runtime/panel-publication.json'


def canonical_receipt(location, artifact_root):
    """Replace host-specific paths only after matching committed receipt bytes."""
    path = Path(location['receipt_path'])
    relative = path.relative_to(artifact_root)
    assert relative in RECEIPT_DIRS or relative == BUNDLE_RECEIPT or any(
        relative.parent == directory for directory in RECEIPT_DIRS
    ), relative
    committed = Path(relative)
    assert committed.is_file(), relative
    assert base.digest(committed)[1] == location['receipt_sha256'], relative
    return {**location, 'receipt_path': str(relative)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact_root = args.artifact_root.resolve()
    assert not args.out.exists(), 'output is write-once'

    coverage = json.loads(COVERAGE.read_text())
    assert (coverage['planned'], coverage['terminal'],
            coverage['certified_lfd_at_least5'], coverage['pending']) == (140, 140, 63, 0)
    expected = {}
    for row in coverage['rows']:
        if row['last_fall_degree_lower_bound'] != 5:
            continue
        result_path = Path(row['result_path'])
        assert base.digest(result_path)[1] == row['result_sha256'], row['id']
        expected[row['id']] = json.loads(result_path.read_text())['certificate_sha256']
    assert len(expected) == 63

    base.RECEIPT_ROOTS = [artifact_root / path for path in RECEIPT_DIRS]
    base.BUNDLE = artifact_root / BUNDLE_RELATIVE
    base.BUNDLE_PUBLICATION = artifact_root / BUNDLE_RECEIPT
    receipts = base.checked_receipts(set(expected.values()))
    embedded = base.bundle_evidence(expected)
    rows = []
    for name, certificate in sorted(expected.items()):
        hits = receipts.get(certificate, [])
        assert len(hits) <= 1, (name, hits)
        assert hits or name in embedded, name
        location = canonical_receipt(hits[0] if hits else embedded[name], artifact_root)
        if name in embedded and hits:
            location['also_in_worker_bundle'] = canonical_receipt(embedded[name], artifact_root)
        rows.append({'id': name, 'certificate_sha256': certificate, **location})
    assert len(rows) == 63

    modes = dict(collections.Counter(row['mode'] for row in rows))
    record = {
        'schema': 'semaev.publication-coverage/v2',
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Receipt and retained-archive audit of 63 checked public locations. Historical anonymous GET receipts are reused; assets are not freshly downloaded.',
        'panel_coverage_path': str(COVERAGE),
        'panel_coverage_sha256': base.digest(COVERAGE)[1],
        'bundle_path': str(BUNDLE_RELATIVE),
        'bundle_sha256': base.digest(base.BUNDLE)[1],
        'certified_lower_bound_certificates': 63,
        'mapped_public_locations': len(rows),
        'dual_location_count': sum('also_in_worker_bundle' in row for row in rows),
        'modes': modes,
        'rows': rows,
    }
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'publication-coverage.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in
                      ('mapped_public_locations', 'dual_location_count', 'modes')}))


if __name__ == '__main__':
    main()
