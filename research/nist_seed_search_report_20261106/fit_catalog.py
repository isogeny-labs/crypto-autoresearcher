"""Describe and validate only the 16 previously recorded fits; no search code."""
import hashlib
import json
from pathlib import Path
import zipfile


def load_catalog(base):
    base = Path(base)
    meta = json.loads((base / 'inputs/build-inputs.json').read_text())
    for name, digest in meta['retained_fit_inputs'].items():
        if hashlib.sha256((base / 'inputs' / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Retained fit input hash mismatch: ' + name)
    fits = json.loads((base / 'inputs/retained-fits.json').read_text())
    signatures = json.loads((base / 'inputs/retained-fit-signatures.json').read_text())
    provenance = json.loads((base / 'inputs/retained-fit-provenance.json').read_text())
    with zipfile.ZipFile(base / 'inputs/source-inputs.zip') as archive:
        raw = archive.read('research/nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/prior-rows.json')
    assert hashlib.sha256(raw).hexdigest() == provenance['cohort_file_sha256']
    rows = json.loads(raw)
    by_id = {s['id']: s for s in signatures}
    assert len(rows) == 21 and len(fits) == 16 and len(by_id) == 21
    assert sum(len(s['aliases']) for s in signatures) == 54
    full = (1 << len(rows)) - 1
    for s in signatures:
        assert s['unknown'] == 0
        assert s['true'] & s['false'] == 0 and s['true'] | s['false'] == full
    result = []
    truth_number = 0
    for number, fit in enumerate(fits, 1):
        a, b = by_id[fit['a']], by_id[fit['b']]
        assert a['aliases'] == fit['a_aliases'] and b['aliases'] == fit['b_aliases']
        assert fit['robust_functions'] == fit['possible_functions']
        bins = [{'inputs': f'{i//2}{i%2}', 'published': 0, 'omitted': 0} for i in range(4)]
        for i, row in enumerate(rows):
            bin_id = 2 * ((a['true'] >> i) & 1) + ((b['true'] >> i) & 1)
            bins[bin_id][row['label']] += 1
        truths = []
        for mask in fit['robust_functions']:
            assert mask in (1, 9)
            outputs = [(mask >> i) & 1 for i in range(4)]
            for i, counts in enumerate(bins):
                assert counts['published'] == 0 or outputs[i] == 1
                assert counts['omitted'] == 0 or outputs[i] == 0
            truth_number += 1
            truths.append({'id': f'T{truth_number:02d}', 'mask': mask, 'outputs': outputs,
                           'expression': 'NOT A AND NOT B' if mask == 1 else 'A equals B (XNOR)'})
        has_rank = any('_rank_' in alias['name'] for side in ('a_aliases', 'b_aliases') for alias in fit[side])
        support = 'No retrieved source establishes historical use of this exact pair, threshold choices, or truth table.'
        if number in (3, 6):
            support += ' Same-prime-199 relationship: linked to the retained lead, but the documented resource-policy follow-ups did not authenticate a historical gate.'
        elif number in range(4, 15):
            support += ' Includes an explicit level-199 feature with another retained feature; no original caller or fixed policy is identified.'
        else:
            support += ' This is another in-sample fit, not an independently supported selection mechanism.'
        if has_rank:
            support += ' Some aliases use the position of the correct eigenvalue candidate; that retrospective rank is not an observed historical timeout.'
        if number == 16:
            support += ' The cumulative budget through 293 includes level 199; it is not an independent test excluding that level.'
        result.append({'id': f'F{number:02d}', 'a_id': fit['a'], 'b_id': fit['b'],
                       'a_aliases': fit['a_aliases'], 'b_aliases': fit['b_aliases'],
                       'bins': bins, 'truth_tables': truths, 'historical_support': support,
                       'historical_use_verified': False})
    assert truth_number == 19
    assert {t['mask'] for f in result for t in f['truth_tables']} == {1, 9}
    empty_11 = [f['id'] for f in result if sum(f['bins'][3][k] for k in ('published', 'omitted')) == 0]
    assert empty_11 == ['F03', 'F04', 'F16']
    return {'pair_count': 16, 'truth_table_instances': 19, 'distinct_truth_masks': [1, 9],
            'signature_count': 21, 'unique_alias_count': 54, 'pair_alias_references': 69,
            'truth_encoding': 'bit (2*A+B) of mask; outputs ordered 00,01,10,11; 1=published,0=omitted',
            'empty_11_pairs': empty_11, 'historical_criterion': 'UNRESOLVED',
            'new_search_performed': False, 'validation_scope': 'Validate only 19 retained tables on retained signatures; no new thresholds, features, pairs, or truth functions.',
            'source_provenance': provenance, 'pairs': result}
