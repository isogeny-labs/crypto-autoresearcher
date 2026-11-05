"""UNVALIDATED source: descriptor-rooted, append-only k2 presentation transport.

No field equations are inserted into the Boolean source. Prime p>3 remains the
original public premise. Importing this module does not construct an instance.
"""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODES = ('identity', 'k2_raw_A0', 'k2_addrow_A0')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def source_identity():
    """Behavior-affecting package bytes; full snapshot custody is external."""
    names = ('transform.py', 'transport.py', 'chart_solver.py', 'engine_counted.py',
             'bridge_counted.py', 'attempt_receipt.py', 'census_v2.py', 'software_controls.py',
             'source-provenance.json', 'software-contract.json')
    return {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}


def verify_baselines():
    """Check frozen dependencies before any lazy baseline import; no candidates run."""
    provenance = json.loads((HERE / 'source-provenance.json').read_text())
    checked = {}
    for path, expected in provenance['baseline_sha256'].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(actual == expected, 'frozen baseline changed: ' + path)
        checked[path] = actual
    return checked


@lru_cache(None)
def composition():
    verify_baselines()
    path = ROOT / 'research/prime_sat_full_chart_composition_20261101/composition.py'
    spec = importlib.util.spec_from_file_location('_transform_original_composition', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = {'rat': 'prime_sat_rationality_software_20261031/rationality.py',
                'ir': 'prime_sat_rationality_software_20261031/circuits.py',
                'q': 'prime_sat_shared_signed_chart_20261030/quotient.py',
                'charts': 'prime_sat_shared_signed_chart_20261030/charts.py',
                'projectors': 'prime_sat_shared_signed_chart_20261030/projectors.py',
                'signed_recovery': 'prime_sat_shared_signed_chart_20261030/signed_recovery.py',
                'check_chart': 'prime_sat_shared_signed_chart_20261030/check_chart.py'}
    for attr, relative in expected.items():
        require(Path(getattr(module, attr).__file__).resolve() == ROOT/'research'/relative,
                'unexpected imported baseline module: '+attr)
    return module


def _sum(p, counts, *polys):
    result = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            counts['field_additions'] += 1
            result[monomial] = (result.get(monomial, 0) + coefficient) % p
    return {m: c for m, c in result.items() if c}


def _scale(poly, coefficient, p, counts):
    result = {}
    for m, c in poly.items():
        counts['field_multiplications'] += 1
        value = c * coefficient % p
        if value:
            result[m] = value
    return result


def _mul(left, right, p, counts):
    result = {}
    for m, c in left.items():
        for n, d in right.items():
            key = tuple(sorted(m + n))
            counts['field_multiplications'] += 1
            counts['field_additions'] += 1
            result[key] = (result.get(key, 0) + c * d) % p
    return {m: c for m, c in result.items() if c}


def _terms(poly):
    return [{'coefficient': c, 'variables': list(m)} for m, c in sorted(poly.items())]


def _poly(row):
    return {tuple(t['variables']): t['coefficient'] for t in row['terms']}


def _compile(source, d):
    C = composition().compiler()
    p = d['p']; w = (p - 1).bit_length(); h = (p - 1).bit_count() - 1
    names = source['projection'] + source['auxiliaries']
    value_count = w * len(names); n = value_count + h * len(names)
    blocks = [{'name': name, 'value_bits': list(range(i*w, (i+1)*w)),
               'state_bits': list(range(value_count+i*h, value_count+(i+1)*h))}
              for i, name in enumerate(names)]
    arithmetic, labels, costs = C.substitute_equations(
        source['equations'], {b['name']: b['value_bits'] for b in blocks}, p, n)
    rd = C.compile_range({'p': p, 'n': n, 'projected_bits': w*len(source['projection']),
                          'arithmetic': arithmetic, 'blocks': blocks})
    return rd, labels, costs


def build_transform(trusted_descriptor, mode):
    require(type(mode) is str and mode in MODES, 'unknown transform operation')
    c = composition(); d = c.descriptor(trusted_descriptor)
    original = c.compile_chart(d)
    original_auth = c.authenticate_chart(original, d)
    source = deepcopy(original['source']); p = d['p']; counts = Counter()
    baseline = verify_baselines()
    common = {'schema': 'prime-chart-transform/v1', 'operation': mode,
              'descriptor': d, 'original': original,
              'original_sha256': digest(original),
              'original_source_sha256': digest(original['source']),
              'original_range_sha256': digest(original['range_document']),
              'baseline_sha256': baseline,
              'field_augmentation': {'present_in_export': False,
                   'mathematical_convention': 'all original field variables x^p-x; theorem only'},
              'representation': 'canonical Boolean range compiler, not polynomial field augmentation'}
    if mode != 'identity' and not (d['k'] == 2 and d['target'] is not None and
                                  d['stratum'] == 'constant'):
        return {**common, 'status': 'not_applicable',
                'reason': 'requires finite arity 2 constant B stratum',
                'construction_costs': {'original': original['construction_costs'],
                                       'original_authentication': original_auth}}
    old_names = source['inputs'] + source['auxiliaries']
    old_rows = deepcopy(source['equations']); certificate = None; substitution = None
    if mode != 'identity':
        a, b = d['target']; alpha, beta = d['a'], d['b']
        require(source['inputs'] == source['projection'] == ['chart.A0', 'chart.A1'],
                'exact ordered A0,q projection')
        A0, q, u0, u1 = ('chart.A0', 'chart.A1', 'support.u0', 'support.u1')
        expected = {
            'norm.coefficient0': {(A0, A0): 1, (u0,): -a % p, (): -beta % p},
            'norm.coefficient1': {(A0, q): 2, (u0,): 1, (u1,): -a % p, (): -alpha % p},
            'norm.coefficient2': {(q, q): 1, (u1,): 1, (): -a % p},
            'norm.coefficient3': {},
            'sign.target': {(A0,): 1, (q,): a, (): -b % p}}
        by_label = {row['label']: (i, row) for i, row in enumerate(old_rows)}
        for label, terms in expected.items():
            require(label in by_label and _poly(by_label[label][1]) ==
                    {m: v for m, v in terms.items() if v}, 'literal k2 row binding: ' + label)
        for row in old_rows:
            if row['label'] not in expected:
                require(all(A0 not in t['variables'] and q not in t['variables']
                            for t in row['terms']), 'auxiliary row depends on pivot coefficients')
        if mode == 'k2_addrow_A0':
            i1, row1 = by_label['norm.coefficient1']; i2, row2 = by_label['norm.coefficient2']
            added = _sum(p, counts, _poly(row1), _scale(_poly(row2), 2*a, p, counts))
            certificate = {'schema': 'ordinary-row-combination/v1',
                'output_index': len(old_rows), 'label': 'transform.N1_plus_2aN2',
                'summands': [{'index': i1, 'label': row1['label'], 'coefficient': 1},
                             {'index': i2, 'label': row2['label'], 'coefficient': 2*a % p}],
                'terms': _terms(added), 'scope': 'ordinary polynomial identity before substitution'}
            old_rows.append({'label': certificate['label'], 'terms': _terms(added)})
        substitution = {(): b, (q,): -a % p}
        substitution = {m: v for m, v in substitution.items() if v}
        source['inputs'] = source['projection'] = [q]
    row_map = []; retained = []
    for i, row in enumerate(old_rows):
        poly = _poly(row)
        if mode != 'identity':
            expanded = {}
            for monomial, coefficient in poly.items():
                term = {(): coefficient}
                for name in monomial:
                    term = _mul(term, substitution if name == 'chart.A0' else {(name,): 1}, p, counts)
                expanded = _sum(p, counts, expanded, term)
            poly = expanded
        # Identity means byte-identical original source, including literal zero rows.
        keep = mode == 'identity' or bool(poly)
        row_map.append({'original_index': i if i < len(original['source']['equations']) else None,
                        'appended_index': i if i >= len(original['source']['equations']) else None,
                        'label': row['label'], 'transformed_index': len(retained) if keep else None,
                        'identically_zero': not bool(poly), 'retained': keep})
        if keep:
            retained.append({'label': row['label'], 'terms': _terms(poly)})
    if mode == 'identity':
        rd = deepcopy(original['range_document']); labels = original['arithmetic_labels'][:]
        substitution_cost = {}; transformed_source = deepcopy(original['source'])
    else:
        source['schema'] = 'prime-full-chart-transformed-field/v1'
        source['equations'] = retained
        source['metadata']['blocks'] = [
            {'name': name, 'equations': [r['label'] for r in retained if r['label'].split('.')[0] == name]}
            for name in dict.fromkeys(r['label'].split('.')[0] for r in retained)]
        source['construction_counts'] = dict(counts)
        transformed_source = source
        rd, labels, substitution_cost = _compile(source, d)
    forward = [{'original': name, 'transformed': name} for name in old_names
               if mode == 'identity' or name != 'chart.A0']
    return {**common, 'status': 'applicable', 'source': transformed_source,
        'source_sha256': digest(transformed_source), 'range_document': rd,
        'range_sha256': digest(rd), 'arithmetic_labels': labels,
        'variable_orders': {'original': old_names,
                            'transformed': transformed_source['inputs'] + transformed_source['auxiliaries']},
        'projections': {'original': original['source']['projection'][:],
                        'transformed': transformed_source['projection'][:]},
        'forward_map': forward,
        'inverse_pivot': None if mode == 'identity' else
            {'name': 'chart.A0', 'terms': _terms(substitution), 'modulus': p},
        'row_map': row_map, 'appended_row_certificate': certificate,
        'construction_costs': {'original': original['construction_costs'],
             'original_authentication': original_auth, 'transform': dict(counts),
             'substitution': substitution_cost,
             'range': {} if mode == 'identity' else deepcopy(rd['construction_costs'])}}


def authenticate_transform(document, trusted_descriptor, mode):
    """Rebuild every byte from the trust root. Hash equality alone is insufficient."""
    expected = build_transform(trusted_descriptor, mode)
    counts = Counter()
    require(composition().compiler().same(document, expected, counts),
            'descriptor-rooted transform content mismatch')
    return {'status': expected['status'], 'typed_comparison': dict(counts),
            'construction': deepcopy(expected['construction_costs'])}
