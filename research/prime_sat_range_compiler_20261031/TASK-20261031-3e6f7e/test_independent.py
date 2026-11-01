#!/usr/bin/env python3
"""Independent fixed checks. No solver, search, assignment census, or file writes.

Expectations come from the prospective contract, literal identities, and direct
coefficient evaluation. The runner retains stdout and this source per attempt.
"""
import copy
import hashlib
import importlib.util
import json
import math
import platform
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SOURCE = 'research/prime_sat_range_compiler_20261031/compiler.py'
spec = importlib.util.spec_from_file_location('independent_target', ROOT / SOURCE)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
RESULTS = []


def packed(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def equal(actual, expected):
    assert packed(actual) == packed(expected), {'actual': actual, 'expected': expected}


def rejects(fn, phrase=None):
    try:
        value = fn()
    except (ValueError, TypeError, KeyError, IndexError) as e:
        if phrase:
            assert phrase in str(e), str(e)
        return {'type': type(e).__name__, 'message': str(e)}
    raise AssertionError({'unexpected_acceptance': value})


def rejected_completion(result, phrase):
    assert result['checker_result'] is None
    assert phrase in result['failure']['message'], result
    return result


def evaluate(poly, bits, p):
    return sum(c for mask, c in poly.items() if int(mask) & bits == int(mask)) % p


def residuals(source, assignment):
    return [sum(t['coefficient'] * math.prod(assignment[v] for v in t['variables'])
                for t in e['terms']) % source['p'] for e in source['equations']]


def identity(polys, certificate, depth, prefix, p):
    """Independent expansion: fixed zero kills, fixed one erases variables."""
    total = {}
    for polynomial, multiplier in zip(polys, certificate):
        for key, coeff in polynomial.items():
            mask = int(key)
            if any(mask >> j & 1 and not prefix >> j & 1 for j in range(depth)):
                continue
            remaining = mask & ~((1 << depth) - 1)
            for other, scale in multiplier.items():
                m = remaining | int(other)
                total[m] = (total.get(m, 0) + coeff * scale) % p
    return {str(k): v for k, v in total.items() if v}


def domain(cnf, bits):
    return all(any(bool(bits >> (abs(x)-1) & 1) == (x > 0) for x in clause) for clause in cnf)


def descriptor(p=7, n=4, m=3, values=None, states=None, arithmetic=None):
    return {'p': p, 'n': n, 'projected_bits': m, 'arithmetic': arithmetic or [],
            'blocks': [{'name': 'X', 'value_bits': [0, 1, 2] if values is None else values,
                        'state_bits': [3] if states is None else states}]}


def public(p, kind, k=None, a=0, b=1):
    names = ['u'+str(i) for i in range(k)] if kind == 'nilpotent' else (
        ['b0'] if kind == 'constant' else ['A0', 'A1', 'A2', 'A3', 'b0', 'b1'])
    return {'p': p, 'curve': {'a': a, 'b': b}, 'kind': kind, 'k': k, 'projection': names}


D7 = descriptor()
P7 = [{'8': 1, '6': 6}, {'9': 1}]
PROOF7 = {'depth': 3, 'prefix': 7, 'clause': [-1, -2, -3],
          'certificate': [{'0': 6}, {'0': 1}]}
RAW7 = {'status': 'complete', 'models': [0, 1, 2, 3, 4, 5, 14], 'learned': []}


def literal_f7():
    doc = C.compile_range(D7)
    equal(doc['polynomials'], P7)
    equal(C.range_certificate(doc, 3, 7), PROOF7)
    equal(identity(P7, PROOF7['certificate'], 3, 7, 7), {'0': 1})
    output = C.complete_transcript(doc, D7, RAW7, 'range')
    assert output['failure'] is None
    equal(output['augmented']['learned'], [PROOF7])
    equal(output['checker_result']['projected_models'], [0, 1, 2, 3, 4, 5, 6])
    assert output['checker_result']['projected_model_set_complete']
    return {'input': RAW7, 'expected_polynomials': P7, 'expected_proof': PROOF7, 'output': output}


def literal_f7_negatives():
    answer = {**copy.deepcopy(RAW7), 'learned': [copy.deepcopy(PROOF7)]}
    verifier = C.adapter().verify_transcript
    checks = {}
    checks['missing_certificate'] = rejects(lambda: verifier(7, 4, 3, P7, [], RAW7), 'uncovered')
    bad = copy.deepcopy(answer); bad['models'].remove(14)
    checks['missing_model14'] = rejects(lambda: verifier(7, 4, 3, P7, [], bad), 'uncovered')
    bad = copy.deepcopy(answer); bad['learned'][0]['certificate'][0]['0'] = 1
    checks['wrong_sign'] = rejects(lambda: verifier(7, 4, 3, P7, [], bad), 'identity')
    bad = copy.deepcopy(answer); bad['models'][-1] = 6
    checks['wrong_model6'] = rejects(lambda: verifier(7, 4, 3, P7, [], bad), 'not a polynomial root')
    checks['direct_cnf'] = rejects(lambda: verifier(7, 4, 3, P7, [[-1, -2, -3]], answer), 'empty CNF')
    return checks


def direct_f5():
    d = descriptor(5, 3, 3, states=[]); doc = C.compile_range(d)
    equal(doc['polynomials'], [{'5': 1}, {'6': 1}])
    equal(doc['bootstrap_cnf'], [[-1, -3], [-2, -3]])
    proof = C.range_certificate(doc, 3, 6)
    equal(proof['certificate'], [{}, {'0': 1}])
    equal(identity(doc['polynomials'], proof['certificate'], 3, 6, 5), {'0': 1})
    result = C.adapter().verify_transcript(5, 3, 3, doc['polynomials'], [],
        {'status': 'censored', 'models': [], 'learned': [proof]})
    return {'descriptor': d, 'proof': proof, 'result': result}


def f7_fixed_states():
    doc = C.compile_range(D7); rows = []
    for prefix in (7, 15):
        proof = C.range_certificate(doc, 4, prefix)
        equal(proof['certificate'], PROOF7['certificate'])
        equal(identity(P7, proof['certificate'], 4, prefix, 7), {'0': 1})
        check = C.adapter().verify_transcript(7, 4, 3, P7, [],
            {'status': 'censored', 'models': [], 'learned': [proof]})
        rows.append({'prefix': prefix, 'proof': proof, 'check': check})
    return rows


def interleaving():
    d = {'p': 5, 'n': 6, 'projected_bits': 6, 'arithmetic': [], 'blocks': [
        {'name': 'A', 'value_bits': [0, 2, 4], 'state_bits': []},
        {'name': 'B', 'value_bits': [1, 3, 5], 'state_bits': []}]}
    doc = C.compile_range(d)
    equal(doc['polynomials'], [{'17': 1}, {'20': 1}, {'34': 1}, {'40': 1}])
    rows = []
    for prefix, index in ((21, 1), (42, 3), (63, 1)):
        proof = C.range_certificate(doc, 6, prefix)
        expected = [{} for _ in range(4)]; expected[index] = {'0': 1}
        equal(proof['certificate'], expected)
        equal(identity(doc['polynomials'], expected, 6, prefix, 5), {'0': 1})
        checked = C.adapter().verify_transcript(5, 6, 6, doc['polynomials'], [],
            {'status': 'censored', 'models': [], 'learned': [proof]})
        rows.append({'prefix': prefix, 'expected_generator': index, 'proof': proof, 'adapter_result': checked})
    return {'descriptor': d, 'rows': rows}


def cross_projection():
    d = descriptor(7, 6, 3, [0, 2, 4], [5]); doc = C.compile_range(d)
    equal(doc['polynomials'], [{'32': 1, '20': 6}, {'33': 1}])
    equal(C.encode_assignment(doc, {'X': 6}, d, 'range'), 52)
    equal(C.decode_assignment(doc, 52, d, 'range')['assignment'], {'X': 6})
    raw = {'status': 'complete', 'models': [0, 1, 2, 3, 52, 5, 6, 7], 'learned': []}
    output = C.complete_transcript(doc, d, raw, 'range')
    assert output['failure'] is None and output['checker_result']['projected_model_set_complete']
    proof = C.range_certificate(doc, 5, 21)
    equal(identity(doc['polynomials'], proof['certificate'], 5, 21, 7), {'0': 1})
    checked = C.adapter().verify_transcript(7, 6, 3, doc['polynomials'], [],
        {'status': 'censored', 'models': [], 'learned': [proof]})
    return {'descriptor': d, 'nonzero_auxiliary_witness': 52, 'proof': proof, 'adapter_result': checked, 'output': output}


def zero_projection():
    d = descriptor(m=0); doc = C.compile_range(d)
    valid = C.complete_transcript(doc, d, {'status': 'complete', 'models': [14], 'learned': []}, 'range')
    assert valid['checker_result']['projected_model_set_complete']
    equal(valid['checker_result']['projected_models'], [0])
    empty = C.complete_transcript(doc, d, {'status': 'complete', 'models': [], 'learned': []}, 'range')
    rejected_completion(empty, 'uncovered')
    equal(empty['gaps'], [{'depth': 0, 'prefix': 0, 'zero_suffix_value_domain_witness': 0, 'arithmetic_root_asserted': False}])
    return {'valid': valid, 'empty': empty}


def censored():
    doc = C.compile_range(D7); rows = []
    for models, expected_cover in ((RAW7['models'], True), ([0], False)):
        raw = {'status': 'censored', 'models': models, 'learned': []}
        output = C.complete_transcript(doc, D7, raw, 'range')
        check = output['checker_result']
        assert check['declared_status'] == 'censored' and not check['projected_model_set_complete']
        assert check['cover_complete'] is expected_cover
        equal(output['original'], raw); equal(output['augmented']['status'], 'censored')
        rows.append(output)
    return rows


def shadowed_bad_record():
    doc = C.compile_range(D7)
    bad = {'depth': 4, 'prefix': 0, 'clause': [1, 2, 3, 4], 'certificate': [{}, {}]}
    raw = {**copy.deepcopy(RAW7), 'learned': [bad]}
    output = C.complete_transcript(doc, D7, raw, 'range')
    rejected_completion(output, 'identity')
    equal(output['augmented']['learned'][0], bad)
    duplicate = copy.deepcopy(RAW7); duplicate['models'].append(0)
    duplicated = C.complete_transcript(doc, D7, duplicate, 'range')
    rejected_completion(duplicated, 'repeated model projection')
    malformed = []
    for key, value in (('depth', True), ('depth', 3.0), ('depth', -1), ('depth', 5), ('prefix', 8), ('prefix', -1)):
        item = copy.deepcopy(PROOF7); item[key] = value
        out = C.complete_transcript(doc, D7, {**copy.deepcopy(RAW7), 'learned': [item]}, 'range')
        assert out['failure'] is not None
        equal(out['augmented']['learned'][0], item)
        malformed.append({'input': item, 'failure': out['failure']})
    return {'shadowed': output, 'duplicate': duplicated, 'malformed': malformed}


def domain_gap():
    doc = C.compile_range(D7); rows = []
    for models in ([], [0, 1, 2, 3, 4, 5]):
        output = C.complete_transcript(doc, D7, {'status': 'complete', 'models': models, 'learned': []}, 'range')
        rejected_completion(output, 'uncovered')
        assert output['gaps'] and all(not g['arithmetic_root_asserted'] for g in output['gaps'])
        rows.append(output)
    assert C.range_certificate(doc, 4, 8) is None
    assert domain(doc['bootstrap_cnf'], 8)
    equal([evaluate(q, 8, 7) for q in P7], [1, 0])
    bad = C.complete_transcript(doc, D7, {'status': 'censored', 'models': [8], 'learned': []}, 'range')
    rejected_completion(bad, 'not a polynomial root')
    return {'gaps': rows, 'valid_value_wrong_state': {'bits': 8, 'range_certificate': None, 'output': bad}}


def bootstrap():
    rows = []
    cases = [
        (descriptor(), [[-1, -2, -3]], P7, [(0, True), (6, True), (7, False), (8, True), (14, True)]),
        (descriptor(11, 5, 4, [0, 1, 2, 3], [4]), [[-1, -2, -4], [-3, -4]],
         [{'16': 1, '10': 10}, {'17': 1}, {'12': 1}], [(10, True), (11, False), (12, False)]),
        (descriptor(17, 5, 5, [0, 1, 2, 3, 4], []), [[-1, -5], [-2, -5], [-3, -5], [-4, -5]],
         [{'17': 1}, {'18': 1}, {'20': 1}, {'24': 1}], [(0, True), (16, True), (17, False), (31, False)])]
    for d, clauses, polys, literals in cases:
        doc = C.compile_range(d); equal(doc['bootstrap_cnf'], clauses); equal(doc['polynomials'], polys)
        for bits, expected in literals:
            assert domain(clauses, bits) is expected
        rows.append({'descriptor': d, 'expected_clauses': clauses, 'expected_polynomials': polys, 'literal_checks': literals})
    return rows


def layout_mutations():
    cases = []
    for label, key, value in [('bool', 'value_bits', [False, 1, 2]), ('float', 'value_bits', [0.0, 1, 2]),
        ('negative', 'value_bits', [-1, 1, 2]), ('outside', 'value_bits', [0, 1, 4]),
        ('duplicate', 'value_bits', [0, 0, 2]), ('short', 'value_bits', [0, 1]),
        ('state_projection', 'state_bits', [2]), ('alias_collision', 'state_bits', [0]),
        ('state_missing', 'state_bits', []), ('state_count', 'state_bits', [3, 3])]:
        d = copy.deepcopy(D7); d['blocks'][0][key] = value
        cases.append({'label': label, 'descriptor': d, 'rejection': rejects(lambda: C.compile_range(d))})
    doc = C.compile_range(D7)
    for label, modify in [('weights', lambda d: d['blocks'][0].update(value_bits=[2, 1, 0])),
                           ('public_p', lambda d: d.update(p=5)), ('public_projection', lambda d: d.update(projected_bits=2))]:
        d = copy.deepcopy(D7); modify(d)
        cases.append({'label': label, 'descriptor': d, 'rejection': rejects(lambda: C.authenticate(doc, d, 'range'))})
    for bits in (True, 0.0, -1, 16):
        cases.append({'bits': bits, 'rejection': rejects(lambda: C.decode_assignment(doc, bits, D7, 'range'))})
    for assignment in ({}, {'X': True}, {'X': 1.0}, {'X': -1}, {'X': 7}, {'X': 0, 'Y': 0}):
        cases.append({'assignment': assignment, 'rejection': rejects(lambda: C.encode_assignment(doc, assignment, D7, 'range'))})
    for polynomial in ({'06': 1}, {'16': 1}, {'0': 0}, {'0': True}, {'0': 7}, {0: 1}):
        d = copy.deepcopy(D7); d['arithmetic'] = [polynomial]
        cases.append({'arithmetic': polynomial, 'rejection': rejects(lambda: C.compile_range(d))})
    return cases


def content_mutations():
    d = descriptor(arithmetic=[{'1': 1}]); doc = C.compile_range(d)
    mutations = [
        ('coefficient', lambda x: x['polynomials'][0].update({'1': 2})),
        ('omitted_equation', lambda x: x['polynomials'].pop(0)),
        ('omitted_recurrence', lambda x: x['polynomials'].pop(1)),
        ('reordered_ranges', lambda x: x['polynomials'].reverse()),
        ('generator_index', lambda x: x['generators'][0]['forbidden'][0].update(index=1)),
        ('omitted_cnf', lambda x: x.update(bootstrap_cnf=[])),
        ('reordered_cnf_literals', lambda x: x['bootstrap_cnf'][0].reverse()),
        ('state_cnf_literal', lambda x: x['bootstrap_cnf'][0].__setitem__(0, -4)),
        ('name', lambda x: x['blocks'][0].update(name='Y')),
        ('projection', lambda x: x.update(projected_bits=2)),
        ('bool_coefficient', lambda x: x['polynomials'][0].update({'1': True})),
        ('float_coefficient', lambda x: x['polynomials'][0].update({'1': 1.0})),
        ('cost_metadata', lambda x: x['construction_costs']['range'].update(blocks=True))]
    rows = []
    for label, mutate in mutations:
        bad = copy.deepcopy(doc); mutate(bad)
        rows.append({'label': label, 'mutated_document': bad, 'rejection': rejects(lambda: C.authenticate(bad, d, 'range'))})
    pd = public(5, 'nilpotent', 1); block = C.compile_block(pd)
    for label, mutate in [
        ('specialized_source', lambda x: x['source'].update(equations=[])),
        ('source_coefficient', lambda x: x['source']['equations'][0]['terms'][0].update(coefficient=2)),
        ('source_metadata', lambda x: x['source']['metadata'].update(extra=1)),
        ('projection_decoding', lambda x: x['projection_decoding'][0]['value_bits'].reverse()),
        ('source_hash', lambda x: x.update(source_sha256='0'*64)),
        ('source_projection_name', lambda x: x['source']['projection'].__setitem__(0, 'v'))]:
        bad = copy.deepcopy(block); mutate(bad)
        rows.append({'label': label, 'rejection': rejects(lambda: C.authenticate(bad, pd)), 'mutated_sha256': hashlib.sha256(packed(bad)).hexdigest()})
    for value in (True, 1.0, -1, 6):
        bad = copy.deepcopy(pd); bad['k'] = value
        rows.append({'public_descriptor': bad, 'rejection': rejects(lambda: C.compile_block(bad))})
    badcnf = C.compile_range(D7)
    rows.append({'label': 'actual_bootstrap_mutation', 'rejection': rejects(lambda: C.complete_transcript(badcnf, D7, RAW7, 'range', [[-1, -2, -4]]))})
    return rows


def bit_substitution():
    def term(c, vs): return {'coefficient': c, 'variables': vs}
    equations = [
        {'label': 'square', 'terms': [term(1, ['x', 'x'])]},
        {'label': 'product', 'terms': [term(1, ['x', 'y'])]},
        {'label': 'cancel', 'terms': [term(4, ['x']), term(1, ['x', 'x'])]},
        {'label': 'zero', 'terms': []}, {'label': 'constant', 'terms': [term(4, [])]}]
    expected = [{'1': 1, '2': 4, '3': 4, '4': 1, '5': 3, '6': 1},
                {'9': 1, '10': 2, '12': 4, '17': 2, '18': 4, '20': 3, '33': 4, '34': 3, '36': 1},
                {'2': 2, '3': 4, '4': 2, '5': 3, '6': 1}, {}, {'0': 4}]
    layout = {'x': [0, 1, 2], 'y': [3, 4, 5]}
    polys, labels, costs = C.substitute_equations(equations, layout, 5, 6)
    equal(polys, expected); equal(labels, ['square', 'product', 'cancel', 'zero', 'constant'])
    equal(costs['products'], 39)
    equal(costs['source_terms'], 5)
    equal(costs['coefficient_merges'], 31)
    equal(costs['cancelled_output_terms'], 1)
    invalid = []
    for terms in ([term(1, ['x', 'x', 'x'])], [term(0, ['x'])], [term(True, ['x'])],
                  [term(5, ['x'])], [term(1, ['y', 'x'])], [term(1, ['z'])],
                  [term(1, ['x']), term(2, ['x'])], [term(1, ['x', 'x']), term(1, ['x'])]):
        invalid.append({'terms': terms, 'rejection': rejects(lambda: C.substitute_equations([{'label': 'bad', 'terms': terms}], layout, 5, 6))})
    # Canonical source checker.py:82 requires a nonempty label. This helper
    # promises strict canonical source input; compile_block cannot reach this
    # malformed case because its trusted builder emits nonempty labels.
    malformed_equations = [{'label': '', 'terms': []}]
    try:
        rejects(lambda: C.substitute_equations(malformed_equations, {}, 5, 0))
    except AssertionError as error:
        raise AssertionError({'finding': 'F2', 'scope': 'low-level substitute_equations only',
            'input': {'equations': malformed_equations, 'layout': {}, 'p': 5, 'n': 0},
            'expected': 'reject noncanonical empty equation label', 'actual': str(error)}) from error
    return {'equations': equations, 'layout': layout, 'expected': expected, 'actual': polys, 'costs': costs, 'invalid': invalid}


def accepted_blocks():
    rows = []
    for p in (5, 7):
        for kind, k in [('nilpotent', 0), ('nilpotent', 1), ('nilpotent', 2), ('nilpotent', 3), ('nilpotent', 4), ('nilpotent', 5), ('guard', None), ('slack', None), ('constant', None)]:
            d = public(p, kind, k); doc = C.compile_block(d); source = doc['source']
            names = source['inputs'] + source['auxiliaries']; width = 3; states = int(p == 7)
            equal(doc['projected_bits'], len(source['inputs'])*width)
            equal(doc['n'], len(names)*(width+states))
            equal([b['name'] for b in doc['blocks']], names)
            equal(doc['arithmetic_labels'], [e['label'] for e in source['equations']])
            for i, block in enumerate(doc['blocks']):
                equal(block['value_bits'], [3*i, 3*i+1, 3*i+2])
                equal(block['state_bits'], [3*len(names)+i] if states else [])
            assert all(int(mask).bit_count() <= 2 for poly in doc['polynomials'] for mask in poly)
            equal(doc['source_sha256'], hashlib.sha256(packed(source)).hexdigest())
            C.authenticate(json.loads(packed(doc)), d)
            rows.append({'descriptor': d, 'n': doc['n'], 'm': doc['projected_bits'],
                         'equations': len(doc['polynomials']), 'source_sha256': doc['source_sha256'],
                         'document_sha256': hashlib.sha256(packed(doc)).hexdigest(), 'costs': doc['construction_costs']})
    return rows


def fixed_root_roundtrip():
    builders = C.authenticated().builders
    fixtures = json.loads((ROOT / 'coordination/prime_sat_rationality_authenticated_20261031/fixed-software-contract.json').read_text())
    rows = []
    cases = []
    for f in fixtures['nilpotent_fixtures']:
        d = public(f['p'], 'nilpotent', len(f['U'])-1, f['a'], f['b'])
        bundle = builders.nilpotent_square_block(d['k'], f['p'], f['a'], f['b'], f['U'], f['C'])
        cases.append((f['id'], d, bundle, f['valid']))
    for kind in ('guard', 'slack'):
        for beta in (1, 4):
            cases.append(('F1_'+kind+'_'+str(beta), public(5, kind),
                builders.linear_B_square_block(5, 0, 1, kind, [0, 4], [0, 1], beta), True))
    cases.append(('constant2', public(5, 'constant'), builders.constant_B_block({'p': 5, 'a': 0, 'b': 1}, [2]), True))
    for name, d, bundle, expected_root in cases:
        doc = C.compile_block(d); assignment = bundle['assignment']
        equal(doc['source'], bundle['circuit'])
        original = residuals(bundle['circuit'], assignment)
        bits = C.encode_assignment(doc, assignment, d)
        compiled = [evaluate(poly, bits, d['p']) for poly in doc['polynomials']]
        equal(compiled[:len(original)], original)
        assert all(value == 0 for value in compiled[len(original):])
        assert (not any(original)) is expected_root
        decoded = C.decode_assignment(doc, bits, d)
        equal(decoded['assignment'], assignment)
        # Source generation is symbolic: recompilation has the same content.
        equal(C.compile_block(d), doc)
        rows.append({'id': name, 'descriptor': d, 'assignment': assignment, 'bits': bits,
                     'expected_root': expected_root, 'source_residuals': original,
                     'bit_residuals': compiled, 'decoding_costs': decoded['costs']})
    # Strict reconstruction rejects the literal wrong F7 recurrence bit.
    doc7 = C.compile_range(D7)
    rows.append({'wrong_state6': rejects(lambda: C.decode_assignment(doc7, 6, D7, 'range'), 'recurrence')})
    return rows


def fidelity():
    doc = C.compile_range(D7); raw = copy.deepcopy(RAW7); original_bytes = packed(raw); document_bytes = packed(doc)
    raw['learned'] = [copy.deepcopy(PROOF7)]; original_bytes = packed(raw)
    calls = []; adapter = C.adapter(); original = adapter.verify_transcript
    def observed(*args, **kwargs):
        calls.append({'domain_cnf': copy.deepcopy(args[4]), 'aux_bound': kwargs.get('aux_bound'),
                      'polynomials': copy.deepcopy(args[3]), 'answer': copy.deepcopy(args[5])})
        return original(*args, **kwargs)
    adapter.verify_transcript = observed
    try:
        output = C.complete_transcript(doc, D7, raw, 'range')
    finally:
        adapter.verify_transcript = original
    assert packed(raw) == original_bytes and packed(doc) == document_bytes
    equal(output['augmented']['learned'][:len(raw['learned'])], raw['learned'])
    equal(output['original_sha256'], hashlib.sha256(original_bytes).hexdigest())
    equal(calls[0]['domain_cnf'], []); assert calls[0]['aux_bound'] is None
    raw['models'][0] = 99; doc['bootstrap_cnf'][0][0] = -4
    assert output['original']['models'][0] == 0 and output['bootstrap_cnf'] == [[-1, -2, -3]]
    return {'captured_verifier_calls': calls, 'retained_output': output}


def accounting():
    doc = C.compile_range(D7); output = C.complete_transcript(doc, D7, RAW7, 'range')
    expected = {'insertion_bit_visits': 21, 'trie_visits': 15, 'minimum_updates': 14,
                'emitted_certificates': 1, 'multiplier_vector_entries': 2, 'multiplier_nonzeros': 2,
                'certificate_serialization_bytes': len(packed(PROOF7))}
    equal(output['costs']['completion'], expected)
    final = output['costs']['final_verifier']
    equal(final['restriction'], {'term_visits': 3, 'coefficient_additions': 3})
    equal(final['identity_check'], {'coefficient_multiplications': 3, 'coefficient_additions': 3})
    equal(final['model_evaluation'], {'term_visits': 21, 'coefficient_additions': 2})
    equal(final['coverage'], {'prefixes': 8, 'prefix_depth_sum': 24, 'trie_nodes': 15})
    equal(final['domain_validation'], {})
    d = public(5, 'constant'); block = C.compile_block(d)
    bits = C.encode_assignment(block, {'b0': 2, 'z': 3}, d)
    auth = C.authenticated(); original = auth.canonical_circuit; calls = []
    def observed(descriptor):
        calls.append(copy.deepcopy(descriptor)); return original(descriptor)
    auth.canonical_circuit = observed
    try:
        decoded = C.decode_assignment(block, bits, d)
    finally:
        auth.canonical_circuit = original
    equal(len(calls), 2)
    missing = not any('authenticat' in key or 'construction' in key or 'comparison' in key
                      for key in decoded['costs'])
    assert not missing, {'finding': 'F1', 'scope': 'production decode_assignment cost report',
        'descriptor': d, 'bits': bits, 'canonical_builder_calls_observed': len(calls),
        'returned_costs': decoded['costs'],
        'expected': 'retain authentication, recompilation, and typed comparison phase costs in addition to bit decoding'}
    return {'literal_completion_expected': expected, 'literal_actual_costs': output['costs'],
            'decode_authentication_probe': {'descriptor': d, 'bits': bits, 'canonical_builder_calls_observed': len(calls),
                'returned_costs': decoded['costs'], 'missing_authentication_phase': 'authentication' not in decoded['costs']}}


GROUPS = [literal_f7, literal_f7_negatives, direct_f5, f7_fixed_states, interleaving,
          cross_projection, zero_projection, censored, shadowed_bad_record, domain_gap,
          bootstrap, layout_mutations, content_mutations, bit_substitution, accepted_blocks,
          fixed_root_roundtrip, fidelity, accounting]


def main():
    binding = json.loads((ROOT / '.resume/range-compiler-review-source-binding.json').read_text())
    before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in binding['source_sha256']}
    equal(before, binding['source_sha256'])
    for fn in GROUPS:
        try:
            output = fn()
            RESULTS.append({'group': fn.__name__, 'status': 'passed', 'details': output})
        except Exception as e:
            RESULTS.append({'group': fn.__name__, 'status': 'failed', 'error_type': type(e).__name__,
                            'error': str(e), 'traceback': traceback.format_exc()})
    after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in binding['source_sha256']}
    report = {'schema': 'independent-fixed-range-compiler-suite/v1', 'runtime': {
        'executable': sys.executable, 'python_version': sys.version, 'platform': platform.platform()},
        'source_hashes_before': before, 'source_hashes_after': after,
        'sources_unchanged': before == after, 'groups': RESULTS,
        'groups_passed': sum(x['status'] == 'passed' for x in RESULTS),
        'groups_failed': sum(x['status'] == 'failed' for x in RESULTS),
        'scientific_runs': 0, 'solver_instances': 0, 'remote_jobs': 0,
        'enumeration': 'Only explicit literal transcript/witness cases; no assignment, coefficient, field, or projected-model census.'}
    print(json.dumps(report, sort_keys=True, indent=2))
    return int(report['groups_failed'] != 0 or before != after)


if __name__ == '__main__':
    raise SystemExit(main())
