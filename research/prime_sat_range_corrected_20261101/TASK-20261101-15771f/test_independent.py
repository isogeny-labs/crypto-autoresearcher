"""Source-aware independent fixed review. No solver, census, search or benchmark.

All expectations below follow the prospective equations and explicit inputs.
This program prints records; the external custodian retains gate/attempt logs.
"""
import copy
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[3]
SOURCE = 'research/prime_sat_range_corrected_20261101/compiler.py'
SPEC = importlib.util.spec_from_file_location('independent_review_target', ROOT / SOURCE)
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)
GROUPS = []
CURRENT = None


def encoded(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(x):
    return hashlib.sha256(encoded(x)).hexdigest()


def eq(actual, expected, label, inputs=None):
    # JSON's equality distinguishes bool/int, unlike Python's equality.
    good = encoded(actual) == encoded(expected)
    CURRENT['checks'].append({'label': label, 'input': inputs, 'expected': expected,
                              'actual': actual, 'passed': good})
    if not good:
        raise AssertionError(label)


def reject(call, label, inputs):
    try:
        value = call()
    except ValueError as e:
        CURRENT['checks'].append({'label': label, 'input': inputs, 'expected': 'ValueError',
                                  'actual': {'type': 'ValueError', 'message': str(e)}, 'passed': True})
        return
    CURRENT['checks'].append({'label': label, 'input': inputs, 'expected': 'ValueError',
                              'actual': value, 'passed': False})
    raise AssertionError(label + ': unexpectedly accepted')


def group(name, fn):
    global CURRENT
    CURRENT = {'id': name, 'checks': [], 'passed': False}
    GROUPS.append(CURRENT)
    try:
        fn()
        CURRENT['passed'] = True
    except Exception as e:
        CURRENT['error'] = {'type': type(e).__name__, 'message': str(e),
                            'traceback': traceback.format_exc()}


def desc(p=7, n=4, m=3, values=None, states=None, arithmetic=None):
    return {'p': p, 'n': n, 'projected_bits': m, 'arithmetic': arithmetic or [],
            'blocks': [{'name': 'x', 'value_bits': [0, 1, 2] if values is None else values,
                        'state_bits': ([3] if p == 7 else []) if states is None else states}]}


D7 = desc()
P7 = [{'6': 6, '8': 1}, {'9': 1}]
CERT7 = {'depth': 3, 'prefix': 7, 'clause': [-1, -2, -3],
         'certificate': [{'0': 6}, {'0': 1}]}
MODELS7 = [0, 1, 2, 3, 4, 5, 14]
RAW7 = {'status': 'complete', 'models': MODELS7, 'learned': []}
COMPLETE7 = {'status': 'complete', 'models': MODELS7, 'learned': [CERT7]}


def answer(models=(), learned=(), status='censored'):
    return {'status': status, 'models': list(models), 'learned': copy.deepcopy(list(learned))}


def verify(d, a, cnf=None):
    return C.adapter().verify_transcript(d['p'], d['n'], d['projected_bits'],
                                         d['polynomials'], [] if cnf is None else cnf, a, aux_bound=None)


def field_residuals(source, assignment):
    p = source['p']
    return [sum(t['coefficient'] * math.prod(assignment[v] for v in t['variables'])
                for t in e['terms']) % p for e in source['equations']]


def bit_residuals(polys, bits, p):
    return [sum(c for m, c in poly.items() if int(m) & bits == int(m)) % p for poly in polys]


def independent_identity(polys, proof, p):
    total = {}
    fixed = (1 << proof['depth']) - 1
    for poly, multiplier in zip(polys, proof['certificate']):
        for m, c in poly.items():
            m = int(m)
            if m & fixed & ~proof['prefix']:
                continue
            for u, a in multiplier.items():
                mask = (m & ~fixed) | int(u)
                total[mask] = (total.get(mask, 0) + c * a) % p
    return {str(m): c for m, c in total.items() if c}


def literal_f7():
    d = C.compile_range(D7)
    eq(d['polynomials'], P7, 'hand expanded F7 generators', D7)
    eq(d['bootstrap_cnf'], [[-1, -2, -3]], 'value-only F7 clause')
    r = C.complete_transcript(d, D7, RAW7, 'range')
    eq(r['augmented'], COMPLETE7, 'append exact telescoping record', RAW7)
    eq(r['failure'], None, 'adapter accepts exact full-cube completion')
    eq(r['checker_result']['projected_models'], [0, 1, 2, 3, 4, 5, 6], 'projection set')
    eq(r['checker_result']['projected_model_set_complete'], True, 'declared completeness')
    eq(independent_identity(P7, CERT7, 7), {'0': 1}, 'independent restricted identity', CERT7)


def literal_negatives():
    d = C.compile_range(D7)
    cases = [('missing_certificate', RAW7),
             ('missing_model14', answer(MODELS7[:-1], [CERT7], 'complete')),
             ('wrong_state_model6', answer([0, 1, 2, 3, 4, 5, 6], [CERT7], 'complete'))]
    wrong = copy.deepcopy(CERT7); wrong['certificate'][0] = {'0': 1}
    cases.append(('wrong_certificate_sign', answer(MODELS7, [wrong], 'complete')))
    for name, a in cases:
        reject(lambda a=a: verify(d, a), name, a)
    reject(lambda: verify(d, COMPLETE7, [[-1, -2, -3]]),
           'nonempty_CNF_is_not_full_cube_proof', {'answer': COMPLETE7, 'domain_cnf': [[-1, -2, -3]]})


def direct_f5():
    de = desc(5, 3, 3)
    d = C.compile_range(de)
    eq(d['polynomials'], [{'5': 1}, {'6': 1}], 'F5 forbidden equations increasing local zero bit', de)
    proof = {'depth': 3, 'prefix': 6, 'clause': [1, -2, -3], 'certificate': [{}, {'0': 1}]}
    eq(C.range_certificate(d, 3, 6), proof, 'r1 direct multiplier', {'depth': 3, 'prefix': 6})
    eq(independent_identity(d['polynomials'], proof, 5), {'0': 1}, 'direct identity')
    eq(verify(d, answer(learned=[proof]))['valid'], True, 'unchanged adapter direct certificate')


def fixed_states():
    d = C.compile_range(D7)
    for prefix, clause in [(7, [-1, -2, -3, 4]), (15, [-1, -2, -3, -4])]:
        proof = {'depth': 4, 'prefix': prefix, 'clause': clause, 'certificate': [{'0': 6}, {'0': 1}]}
        eq(C.range_certificate(d, 4, prefix), proof, 'fixed state telescoping', proof)
        eq(independent_identity(P7, proof, 7), {'0': 1}, 'independent identity with fixed state')
        eq(verify(d, answer(learned=[proof]))['valid'], True, 'adapter fixed state certificate')


def interleaving():
    de = {'p': 5, 'n': 6, 'projected_bits': 6, 'arithmetic': [],
          'blocks': [{'name': 'a', 'value_bits': [0, 2, 4], 'state_bits': []},
                     {'name': 'b', 'value_bits': [1, 3, 5], 'state_bits': []}]}
    d = C.compile_range(de)
    eq(d['polynomials'], [{'17': 1}, {'20': 1}, {'34': 1}, {'40': 1}], 'interleaved generators', de)
    for prefix, index in [(20, 1), (40, 3), (60, 1)]:
        vector = [{} for _ in (0, 1, 2, 3)]; vector[index] = {'0': 1}
        proof = C.range_certificate(d, 6, prefix)
        eq(proof['certificate'], vector, 'first invalid block declaration order', {'prefix': prefix})
        eq(independent_identity(d['polynomials'], proof, 5), {'0': 1}, 'interleaved identity')
        eq(verify(d, answer(learned=[proof]))['valid'], True, 'interleaved adapter identity')


def crossing():
    de = desc(7, 6, 3, [0, 2, 4], [5]); d = C.compile_range(de)
    eq(d['polynomials'], [{'20': 6, '32': 1}, {'33': 1}], 'cross-projection generators', de)
    eq(C.encode_assignment(d, {'x': 6}, de, 'range'), 52, 'nonzero suffix witness', {'x': 6})
    eq(bit_residuals(d['polynomials'], 52, 7), [0, 0], 'witness root')
    eq(verify(d, answer([52]))['projected_models'], [4], 'existential projected witness')
    eq(verify(d, answer([4]))['valid'], True, 'range-only lower witness shares projection', {'bits': 4})
    proof = C.range_certificate(d, 5, 21)
    eq(proof, {'depth': 5, 'prefix': 21, 'clause': [-1, 2, -3, 4, -5],
               'certificate': [{'0': 6}, {'0': 1}]}, 'crossing invalid prefix certificate')
    eq(verify(d, answer(learned=[proof]))['valid'], True, 'crossing certificate accepted')
    forced = desc(7, 6, 3, [0, 2, 4], [5], [{'16': 1, '0': 6}])
    fd = C.compile_range(forced)
    eq(verify(fd, answer([52]))['valid'], True, 'arithmetic forces nonzero auxiliary suffix', forced)
    reject(lambda: verify(fd, answer([4])), 'zero suffix fails forced arithmetic', {'descriptor': forced, 'bits': 4})


def zero_projection():
    de = desc(7, 4, 0); d = C.compile_range(de)
    for a, complete in [(answer([14], status='complete'), True), (answer(), False)]:
        r = C.complete_transcript(d, de, a, 'range')
        eq(r['checker_result']['cover_complete'], complete, 'zero projection existential coverage', a)
        eq(bool(r['gaps']), not complete, 'zero projection gaps')
    r = C.complete_transcript(d, de, answer(status='complete'), 'range')
    eq(r['failure']['type'], 'ValueError', 'empty false complete rejects')


def censored():
    d = C.compile_range(D7)
    for models, incidental in [(MODELS7, True), ([0], False)]:
        a = answer(models)
        r = C.complete_transcript(d, D7, a, 'range')
        eq(r['augmented']['status'], 'censored', 'raw censoring preserved', a)
        eq(r['checker_result']['cover_complete'], incidental, 'incidental coverage')
        eq(r['checker_result']['projected_model_set_complete'], False, 'never promote censored status')


def shadowed():
    d = C.compile_range(D7)
    bad = {'depth': 4, 'prefix': 0, 'clause': [1, 2, 3, 4], 'certificate': [{}, {}]}
    a = answer([0], [bad]); r = C.complete_transcript(d, D7, a, 'range')
    eq(r['original'], a, 'malformed original retained', a)
    eq(r['augmented']['learned'][0], bad, 'shadowed bad certificate still present')
    eq(r['failure']['message'], 'certificate identity is not one', 'final checker rejects shadowed record')
    a = answer([0, 0]); r = C.complete_transcript(d, D7, a, 'range')
    eq(r['failure']['message'], 'repeated model projection', 'duplicate projected model rejected', a)


def gaps():
    d = C.compile_range(D7)
    for a in [answer(), answer(MODELS7[:-1], status='complete')]:
        r = C.complete_transcript(d, D7, a, 'range')
        eq(bool(r['gaps']), True, 'missing canonical domain branch remains open', a)
        eq([g['arithmetic_root_asserted'] for g in r['gaps']], [False] * len(r['gaps']), 'gap is not asserted root')
    eq(C.range_certificate(d, 4, 8), None, 'value0/state1 has no range certificate', {'depth': 4, 'prefix': 8})
    r = C.complete_transcript(d, D7, answer([8]), 'range')
    eq(r['failure']['message'], 'model is not a polynomial root', 'wrong state does not become model')
    for depth, prefix in [(True, 0), (1.0, 0), (-1, 0), (5, 0), (3, 8), (3, True), (3, -1)]:
        a = answer(learned=[{'depth': depth, 'prefix': prefix, 'clause': [], 'certificate': []}])
        r = C.complete_transcript(d, D7, a, 'range')
        eq(r['failure']['type'], 'ValueError', 'bounded prefix validation before trie', a)


def bootstrap():
    cases = [(desc(5, 3, 3), [[-1, -3], [-2, -3]], [{'5': 1}, {'6': 1}]),
             (D7, [[-1, -2, -3]], P7),
             (desc(11, 5, 4, [0, 1, 2, 3], [4]), [[-1, -2, -4], [-3, -4]],
              [{'16': 1, '10': 10}, {'17': 1}, {'12': 1}]),
             (desc(17, 5, 5, [0, 1, 2, 3, 4], []),
              [[-1, -5], [-2, -5], [-3, -5], [-4, -5]],
              [{'17': 1}, {'18': 1}, {'20': 1}, {'24': 1}])]
    for de, cnf, polys in cases:
        d = C.compile_range(de)
        eq(d['bootstrap_cnf'], cnf, 'threshold comparison CNF', de)
        eq(d['polynomials'], polys, 'compressed alias and generators')
        state_positions = {pos for b in de['blocks'] for pos in b['state_bits']}
        eq(any(abs(x)-1 in state_positions for cl in cnf for x in cl), False, 'no state literal in CNF')
    d = C.compile_range(D7)
    eq(all(any(not ((8 >> (abs(x)-1)) & 1) if x < 0 else bool(8 >> (x-1) & 1)
               for x in cl) for cl in d['bootstrap_cnf']), True, 'domain allows value0/state1')
    eq(bit_residuals(P7, 8, 7), [1, 0], 'recurrence rejects same assignment')


def setpath(obj, path, value):
    out = copy.deepcopy(obj); p = out
    for k in path[:-1]:
        p = p[k]
    p[path[-1]] = value
    return out


def layout_mutations():
    mutations = [(('blocks', 0, 'value_bits', 0), v) for v in [True, 0.0, -1, 4, 1]]
    mutations += [(('blocks', 0, 'state_bits'), v) for v in [[2], [4], [], [3, 4], [True]]]
    mutations += [(('blocks', 0, 'value_bits'), [0, 1]), (('blocks', 0, 'name'), ''),
                  (('projected_bits',), 5), (('projected_bits',), True), (('n',), 4.0), (('p',), True)]
    for path, value in mutations:
        de = setpath(D7, path, value)
        reject(lambda de=de: C.compile_range(de), 'malformed layout', de)
    de = copy.deepcopy(D7); de['blocks'].append(copy.deepcopy(de['blocks'][0]))
    reject(lambda: C.compile_range(de), 'duplicate name and positions', de)
    for ar in [[{'01': 1}], [{'16': 1}], [{'0': 0}], [{'0': 7}], [{'0': True}], [{0: 1}]]:
        de = setpath(D7, ('arithmetic',), ar)
        reject(lambda de=de: C.compile_range(de), 'strict arithmetic polynomial', de)
    d = C.compile_range(D7)
    for de in [setpath(D7, ('p',), 5), setpath(D7, ('projected_bits',), 2),
               setpath(D7, ('blocks', 0, 'value_bits'), [2, 1, 0])]:
        reject(lambda de=de: C.authenticate(d, de, 'range'), 'trusted p projection or local weights changed', de)


def pub(p=5, kind='constant', k=None, a=0, b=1):
    names = ['u'+str(i) for i in range(k)] if kind == 'nilpotent' else (
        ['b0'] if kind == 'constant' else ['A0', 'A1', 'A2', 'A3', 'b0', 'b1'])
    return {'p': p, 'curve': {'a': a, 'b': b}, 'kind': kind, 'k': k, 'projection': names}


def content_mutations():
    de = pub(); d = C.compile_block(de)
    changes = [(('polynomials', 0), {}), (('polynomials', 0, '0'), 3),
               (('generators', 0, 'forbidden', 0, 'index'), 0), (('range_labels',), list(reversed(d['range_labels']))),
               (('bootstrap_cnf',), d['bootstrap_cnf'][:-1]), (('bootstrap_cnf',), list(reversed(d['bootstrap_cnf']))),
               (('source', 'equations', 0, 'terms'), []), (('source', 'equations'), []),
               (('source', 'projection'), []), (('source', 'inputs', 0), 'changed'),
               (('source', 'metadata', 'blocks'), []), (('source', 'curve', 'b'), True),
               (('projection_decoding',), []), (('construction_costs', 'source_authentication', 'canonical_builder_calls'), True),
               (('polynomials',), d['polynomials'][:-1]),
               (('polynomials',), [d['polynomials'][0]]+list(reversed(d['polynomials'][1:])))]
    for path, value in changes:
        mutated = setpath(d, path, value)
        reject(lambda mutated=mutated: C.authenticate(mutated, de), 'typed content mutation', {'path': path, 'replacement': value})
    d7 = C.compile_range(D7)
    bad = setpath(d7, ('bootstrap_cnf', 0, 0), -4)
    reject(lambda: C.authenticate(bad, D7, 'range'), 'state literal substituted in comparator', {'path': ['bootstrap_cnf', 0, 0], 'value': -4})


def term(coef, *variables):
    return {'coefficient': coef, 'variables': list(variables)}


def bit_substitution():
    es = [{'label': 'square', 'terms': [term(1, 'x', 'x')]},
          {'label': 'product', 'terms': [term(1, 'x', 'y')]},
          {'label': 'square_minus_x', 'terms': [term(4, 'x'), term(1, 'x', 'x')]},
          {'label': 'zero', 'terms': []}, {'label': 'constant', 'terms': [term(3)]}]
    layout = {'x': [0, 1, 2], 'y': [3, 4, 5]}
    want = [{'1': 1, '2': 4, '4': 1, '3': 4, '5': 3, '6': 1},
            {'9': 1, '17': 2, '33': 4, '10': 2, '18': 4, '34': 3, '12': 4, '20': 3, '36': 1},
            {'2': 2, '4': 2, '3': 4, '5': 3, '6': 1}, {}, {'0': 3}]
    polys, labels, counts = C.substitute_equations(es, layout, 5, 6)
    eq(polys, want, 'literal symbolic expansions', {'equations': es, 'layout': layout, 'p': 5, 'n': 6})
    eq(labels, ['square', 'product', 'square_minus_x', 'zero', 'constant'], 'label order')
    eq(counts, {'products': 39, 'source_terms': 5, 'coefficient_merges': 31,
                'colliding_masks': 9, 'cancelled_output_terms': 1}, 'independent expansion event counts')


def nodes(x):
    return 1 + (sum(nodes(v) for v in x.values()) if type(x) is dict else
                sum(nodes(v) for v in x) if type(x) is list else 0)


def reference_expansion(source, layout):
    p = source['p']; b = (p-1).bit_length()
    counts = {'cancelled_output_terms': 0}; output = []
    for e in source['equations']:
        sums = {}; events = 0
        for t in e['terms']:
            arity = len(t['variables'])
            counts['source_terms'] = counts.get('source_terms', 0)+1
            if arity:
                counts['products'] = counts.get('products', 0)+sum(b**j for j in range(1, arity+1))
            # Cartesian product of bit positions within one degree<=2 term,
            # never of assignments or field values.
            for indices in itertools.product(range(b), repeat=arity):
                mask = 0; weight = t['coefficient']
                for v, j in zip(t['variables'], indices):
                    mask |= 1 << layout[v][j]; weight *= 1 << j
                sums[mask] = sums.get(mask, 0)+weight; events += 1
        if events:
            counts['coefficient_merges'] = counts.get('coefficient_merges', 0)+events
        collisions = events-len(sums)
        if collisions:
            counts['colliding_masks'] = counts.get('colliding_masks', 0)+collisions
        counts['cancelled_output_terms'] += sum(v % p == 0 for v in sums.values())
        output.append({str(m): v % p for m, v in sums.items() if v % p})
    if not source['equations']:
        counts = {}
    return output, counts


def accepted_blocks():
    # Exactly the named 18 descriptor cohort; this is not a parameter search.
    descriptors = [pub(p, 'nilpotent', k) for p in (5, 7) for k in (0, 1, 2, 3, 4, 5)]
    descriptors += [pub(p, kind) for p in (5, 7) for kind in ('guard', 'slack', 'constant')]
    for de in descriptors:
        d = C.compile_block(de); source = d['source']; p = de['p']; b = 3; h = int(p == 7)
        names = de['projection']+source['auxiliaries']; count = len(names)
        blocks = [{'name': name, 'value_bits': [3*i, 3*i+1, 3*i+2],
                   'state_bits': [3*count+i] if h else []} for i, name in enumerate(names)]
        eq(d['blocks'], blocks, 'canonical complete layout', de)
        eq([d['n'], d['projected_bits']], [(3+h)*count, 3*len(de['projection'])], 'ring and projection size')
        eq(d['projection_decoding'], blocks[:len(de['projection'])], 'projected bit blocks')
        ar, cost = reference_expansion(source, {b['name']: b['value_bits'] for b in blocks})
        eq(d['polynomials'][:len(ar)], ar, 'independent full symbolic substitution')
        eq(d['construction_costs']['substitution'], cost, 'full substitution operation counts')
        eq(d['arithmetic_labels'], [e['label'] for e in source['equations']], 'source equation order')
        eq(max((int(m).bit_count() for poly in d['polynomials'] for m in poly), default=0) <= 2,
           True, 'compiled Boolean degree at most two')
        eq(d['source_sha256'], sha(source), 'canonical source hash')


def own_nilpotent(p, a, b, U, Cvalues):
    """Independent ordinary coefficient arithmetic supplies all fixed auxiliaries."""
    k = len(U)-1; c = list(Cvalues)+[0]*(k-len(Cvalues))
    v = {'u'+str(i): U[i] for i in range(k)}
    v.update({'C'+str(i): c[i] for i in range(k)})
    if not k:
        return v
    if k == 1:
        v.update(v=U[0]**2 % p, F=(-U[0]**3-a*U[0]+b) % p)
        return v
    def reduce(coeffs):
        w = coeffs[:]+[0]*max(0, k-len(coeffs)); quotient = [0]*max(0, len(w)-k)
        for j in range(len(w)-1, k-1, -1):
            factor = w[j] % p; quotient[j-k] = factor
            for i in range(k+1):
                w[j-k+i] = (w[j-k+i]-factor*U[i]) % p
        return quotient, w[:k]
    def product(left, right, label, final=False):
        full = [0]*(2*k-1)
        for i, x in enumerate(left):
            for j, y in enumerate(right):
                full[i+j] += x*y
        qu, re = reduce(full)
        v.update({label+'.Q'+str(i): qu[i] for i in range(k-1)})
        if not final:
            v.update({label+'.P'+str(i): re[i] for i in range(k)})
        return re
    _, F = reduce([b, a, 0, 1])
    if k == 2:
        v.update({'f.q': -U[1] % p, 'f.F0': F[0], 'f.F1': F[1]})
    W = product(c, c, 'C2'); D = [(x-y) % p for x, y in zip(W, F)]
    if k == 2:
        product(D, D, 'D2zero', True)
    else:
        S = product(D, D, 'D2')
        if k == 3:
            product(S, D, 'D3zero', True)
        elif k == 4:
            product(S, S, 'D4zero', True)
        else:
            T = product(S, S, 'D4'); product(T, D, 'D5zero', True)
    return v


def own_linear(p, mode, A, B, beta):
    av = A+[0]*(4-len(A)); z = pow(B[1], -1, p); alpha = -B[0]*z % p
    q1 = (av[3]*alpha+av[2]) % p; q2 = (q1*alpha+av[1]) % p
    c = (q2*alpha+av[0]) % p; F = (alpha**3+1) % p
    v = {**{'A'+str(i): x for i, x in enumerate(av)}, 'b0': B[0], 'b1': B[1],
         'z': z, 'alpha': alpha, 'q1': q1, 'q2': q2, 'c': c, 'v': alpha**2 % p, 'F': F}
    if mode == 'guard':
        v.update(e=int(c == 0), u=pow(c, -1, p) if c else 0, beta=0 if c else beta)
    else:
        v.update(beta=beta, u=(beta*beta-F)*pow(c, -1, p) % p if c else 0)
    return v


def check_witness(de, assignment, expected_root, tag):
    d = C.compile_block(de); before = sha(d)
    field = field_residuals(d['source'], assignment)
    eq(all(x == 0 for x in field), expected_root, tag+' original residual validity',
       {'descriptor': de, 'assignment': assignment})
    bits = C.encode_assignment_counted(d, assignment, de)['bits']
    decoded = C.decode_assignment(d, bits, de)['assignment']
    eq(decoded, assignment, tag+' full field assignment roundtrip')
    residuals = bit_residuals(d['polynomials'], bits, de['p'])
    eq(residuals[:len(field)], field, tag+' source vs bit residuals')
    eq(residuals[len(field):], [0]*(len(residuals)-len(field)), tag+' unique canonical range states')
    eq(sha(d), before, tag+' assignment never specializes document')
    CURRENT['checks'].append({'label': tag+' exact encoded witness', 'input': assignment,
                              'expected': 'retained value, not performance evidence', 'actual': bits, 'passed': True})


def roundtrips():
    for p in (5, 7):
        for k in (0, 1, 2, 3, 4, 5):
            U = [0]*k+[1]; c = [1] if k else []
            check_witness(pub(p, 'nilpotent', k), own_nilpotent(p, 0, 1, U, c), True, 'X^k fixed witness')
        for mode in ('guard', 'slack'):
            for beta in (1, p-1):
                check_witness(pub(p, mode), own_linear(p, mode, [0], [0, 1], beta), True, 'common root both beta signs')
            check_witness(pub(p, mode), own_linear(p, mode, [2], [0, 1], 0), True, 'coprime fixed linear witness')
        check_witness(pub(p), {'b0': 2, 'z': pow(2, -1, p)}, True, 'constant inverse')
    fixed = json.loads((ROOT/'coordination/prime_sat_rationality_authenticated_20261031/fixed-software-contract.json').read_text())
    for f in fixed['nilpotent_fixtures']:
        check_witness(pub(f['p'], 'nilpotent', len(f['U'])-1, f['a'], f['b']),
                      own_nilpotent(f['p'], f['a'], f['b'], f['U'], f['C']), f['valid'], f['id'])
    # Explicit roots alpha=4,0,3 on y^2=x^3+1 yield F=0,1,3 respectively.
    # These are the eight frozen guard inputs, including their invalid auxiliaries.
    for f in fixed['guard_fixtures']:
        alpha = {0: 4, 1: 0, 3: 3}[f['F']]
        assignment = own_linear(5, 'guard', [f['c']], [(-alpha) % 5, 1], f['beta'])
        assignment.update({key: f[key] for key in ('e', 'u', 'beta')})
        check_witness(pub(5, 'guard'), assignment, f['valid'], f['id'])
    de = pub(); d = C.compile_block(de)
    for a in [{'b0': 2}, {'b0': 2, 'z': 3, 'extra': 0}, {'b0': True, 'z': 3},
              {'b0': 2.0, 'z': 3}, {'b0': 5, 'z': 3}, {'b0': 2, 'z': -1}]:
        reject(lambda a=a: C.encode_assignment_counted(d, a, de), 'malformed complete field assignment', a)
    check_witness(de, {'b0': 2, 'z': 2}, False, 'canonical invalid arithmetic witness')


def fidelity():
    d = C.compile_range(D7); frozen = copy.deepcopy(d); raw = copy.deepcopy(RAW7)
    adapter = C.adapter(); original = adapter.verify_transcript; calls = []
    def intercept(*args, **kwargs):
        calls.append({'p': args[0], 'n': args[1], 'm': args[2], 'polynomials': copy.deepcopy(args[3]),
                      'domain_cnf': copy.deepcopy(args[4]), 'answer': copy.deepcopy(args[5]), 'kwargs': kwargs})
        return original(*args, **kwargs)
    adapter.verify_transcript = intercept
    try:
        result = C.complete_transcript(d, D7, raw, 'range')
    finally:
        adapter.verify_transcript = original
    eq(calls, [{'p': 7, 'n': 4, 'm': 3, 'polynomials': P7, 'domain_cnf': [],
                'answer': COMPLETE7, 'kwargs': {'aux_bound': None}}], 'final adapter exact arguments')
    eq(raw, RAW7, 'raw unchanged'); eq(d, frozen, 'document unchanged')
    eq(result['original_sha256'], sha(RAW7), 'raw digest'); eq(result['document_sha256'], sha(d), 'document digest')
    raw2 = answer(MODELS7, [CERT7], 'complete'); r2 = C.complete_transcript(d, D7, raw2, 'range')
    eq(r2['augmented']['learned'][:len(raw2['learned'])], raw2['learned'], 'original learned list unchanged prefix')
    result['original']['models'].append(99); result['bootstrap_cnf'][0][0] = 99
    eq(raw, RAW7, 'returned raw deep copy'); eq(d, frozen, 'returned bootstrap deep copy')


def accounting():
    d = C.compile_range(D7); r = C.complete_transcript(d, D7, RAW7, 'range')
    eq(d['construction_costs'], {'range': {'coefficient_merges': 2, 'cancelled_output_terms': 0,
        'blocks': 1, 'generators': 2, 'clauses': 1, 'literals': 3}}, 'F7 exact construction units')
    want = {'authentication': {'typed_comparison': {'nodes': nodes(d)}, 'construction': d['construction_costs']},
            'bootstrap_comparison': {'nodes': 5},
            'completion': {'insertion_bit_visits': 21, 'trie_visits': 15, 'minimum_updates': 14,
                           'emitted_certificates': 1, 'multiplier_vector_entries': 2, 'multiplier_nonzeros': 2,
                           'certificate_serialization_bytes': len(encoded(CERT7))},
            'serialization': {'raw_bytes': len(encoded(RAW7)), 'augmented_bytes': len(encoded(COMPLETE7)),
                              'bootstrap_bytes': len(encoded([[-1, -2, -3]]))},
            'final_verifier': {'parsing': {'polynomial_entries': 5, 'learned_entries': 1, 'prefix_literals': 3, 'models': 7},
                               'domain_validation': {}, 'restriction': {'term_visits': 3, 'coefficient_additions': 3},
                               'identity_check': {'coefficient_multiplications': 3, 'coefficient_additions': 3},
                               'model_evaluation': {'term_visits': 21, 'coefficient_additions': 2},
                               'coverage': {'prefixes': 8, 'prefix_depth_sum': 24, 'trie_nodes': 15}}}
    eq(r['costs'], want, 'complete independent F7 receipt', {'descriptor': D7, 'answer': RAW7})


def labels():
    reject(lambda: C.substitute_equations([{'label': '', 'terms': []}], {}, 5, 0),
           'retained F2 empty label counterexample rejects', {'equations': [{'label': '', 'terms': []}], 'layout': {}, 'p': 5, 'n': 0})
    eq(C.substitute_equations([{'label': 'zero', 'terms': []}], {}, 5, 0),
       [[{}], ['zero'], {'cancelled_output_terms': 0}], 'nonempty zero polynomial accepted')
    es = [{'label': 'zero', 'terms': []}, {'label': 'zero', 'terms': []}]
    reject(lambda: C.substitute_equations(es, {}, 5, 0), 'duplicate nonempty labels reject', es)
    bad_terms = [[term(0, 'x')], [term(5, 'x')], [term(True, 'x')], [term(1, 'unknown')],
                 [term(1, 'x', 'x', 'x')], [term(1, 'y', 'x')], [term(1, 'x'), term(1)],
                 [term(1, 'x'), term(2, 'x')]]
    for terms in bad_terms:
        es = [{'label': 'bad', 'terms': terms}]
        reject(lambda es=es: C.substitute_equations(es, {'x': [0, 1, 2], 'y': [3, 4, 5]}, 5, 6),
               'canonical source rejection', es)


RECON5 = {'threshold_bit_visits': 3, 'canonical_value_checks': 2,
          'value_bit_writes': 6, 'initial_state_bit_reads': 2}


def reference_auth5(doc):
    # Literal original circuit b0*z-1, independently specified below.
    source = {'schema': 'prime-rationality-field-circuit/v1', 'p': 5, 'curve': {'a': 0, 'b': 1},
              'kind': 'constant', 'k': None, 'inputs': ['b0'], 'auxiliaries': ['z'], 'projection': ['b0'],
              'equations': [{'label': 'constant.inverse', 'terms': [term(4), term(1, 'b0', 'z')]}],
              'metadata': {'blocks': [{'name': 'constant', 'auxiliaries': ['z'], 'equations': ['constant.inverse']}]}}
    eq(doc['source'], source, 'literal trusted constant source')
    construction = {'range': {'blocks': 2, 'generators': 4, 'clauses': 4, 'literals': 8},
                    'substitution': {'source_terms': 2, 'products': 12, 'coefficient_merges': 10, 'cancelled_output_terms': 0},
                    'source_authentication': {'canonical_builder_calls': 1, 'equations': 1, 'source_bytes': len(encoded(source))}}
    eq(doc['construction_costs'], construction, 'independently derived F5 construction receipt')
    return {'typed_comparison': {'nodes': nodes(doc)}, 'construction': construction}


def counted_call(call, de):
    module = C.authenticated(); original = module.canonical_circuit; calls = []
    def wrapper(public):
        calls.append(copy.deepcopy(public))
        return original(public)
    module.canonical_circuit = wrapper
    try:
        value = call()
    finally:
        module.canonical_circuit = original
    eq(calls, [de], 'exactly one canonical source build per public call')
    return value


def counted_encode():
    de = pub(); doc = C.compile_block(de); auth = reference_auth5(doc)
    value = counted_call(lambda: C.encode_assignment_counted(doc, {'b0': 2, 'z': 3}, de), de)
    eq(value, {'bits': 26, 'costs': {'authentication': auth, 'reconstruction': RECON5}},
       'complete successful encode receipt', {'descriptor': de, 'assignment': {'b0': 2, 'z': 3}})
    eq(C.authenticate(doc, de), auth, 'independent authentication oracle matches public authenticate')


def counted_decode():
    de = pub(); doc = C.compile_block(de); auth = reference_auth5(doc)
    value = counted_call(lambda: C.decode_assignment(doc, 26, de), de)
    eq(value, {'assignment': {'b0': 2, 'z': 3}, 'costs': {'authentication': auth,
              'decoding': {'value_bit_reads': 6, 'state_bit_checks': 0}, 'reconstruction': RECON5}},
       'complete successful decode receipt', {'descriptor': de, 'bits': 26})


def nonzero_recurrence():
    de = desc(7, 6, 3, [0, 2, 4], [5]); doc = C.compile_range(de)
    rc = {'threshold_bit_visits': 3, 'canonical_value_checks': 1, 'value_bit_writes': 3,
          'initial_state_bit_reads': 1, 'recurrence_products': 1, 'state_bit_writes': 1}
    construction = {'range': {'coefficient_merges': 2, 'cancelled_output_terms': 0,
                             'blocks': 1, 'generators': 2, 'clauses': 1, 'literals': 3}}
    auth = {'typed_comparison': {'nodes': nodes(doc)}, 'construction': construction}
    enc = C.encode_assignment_counted(doc, {'x': 6}, de, 'range')
    eq(enc, {'bits': 52, 'costs': {'authentication': auth, 'reconstruction': rc}},
       'nonzero recurrence encode costs', {'descriptor': de, 'assignment': {'x': 6}})
    dec = C.decode_assignment(doc, 52, de, 'range')
    eq(dec, {'assignment': {'x': 6}, 'costs': {'authentication': auth, 'reconstruction': rc,
              'decoding': {'value_bit_reads': 3, 'state_bit_checks': 1}}}, 'nonzero recurrence decode costs')
    for bits in (20, 53, True, 52.0, -1, 64):
        reject(lambda bits=bits: C.decode_assignment(doc, bits, de, 'range'), 'malformed value or state rejects', {'bits': bits})


def canonical_binding():
    de = pub(); doc = C.compile_block(de)
    cases = [(setpath(doc, ('source_sha256',), '0'*64), de),
             (setpath(doc, ('arithmetic_labels', 0), 'stale'), de),
             (setpath(doc, ('projected_bits',), True), de),
             (setpath(doc, ('source', 'curve', 'a'), False), de),
             (doc, setpath(de, ('p',), 7)), (doc, setpath(de, ('curve', 'b'), True)),
             (doc, setpath(de, ('projection',), [])), (doc, setpath(de, ('kind',), 'guard')),
             (doc, setpath(de, ('k',), False)), (doc, setpath(de, ('curve', 'a'), 1))]
    for changed, trusted in cases:
        for operation in ('encode', 'decode'):
            reject(lambda changed=changed, trusted=trusted, operation=operation:
                   C.encode_assignment_counted(changed, {'b0': 2, 'z': 3}, trusted) if operation == 'encode' else
                   C.decode_assignment(changed, 26, trusted), 'counted API binding '+operation,
                   {'document_sha256': sha(changed), 'trusted_descriptor': trusted})
    eq(C._encode_authenticated.__name__.startswith('_'), True, 'reconstruction helper is explicitly private')
    eq('auth' in C._encode_authenticated.__doc__, True, 'private core documents caller authentication')


def receipt_isolation():
    de = pub(); doc = C.compile_block(de); original_doc = copy.deepcopy(doc)
    a = {'b0': 2, 'z': 3}
    r = C.encode_assignment_counted(doc, a, de); expected = copy.deepcopy(r)
    r['costs']['authentication']['construction']['range']['blocks'] = 999
    r['costs']['reconstruction']['value_bit_writes'] = 999
    eq(doc, original_doc, 'receipt mutation leaves document intact')
    eq(C.encode_assignment_counted(doc, a, de), expected, 'receipt mutation leaves later encode intact')
    dec = C.decode_assignment(doc, 26, de); preserved = copy.deepcopy(dec)
    dec['costs']['authentication']['typed_comparison']['nodes'] = -1
    dec['costs']['decoding']['value_bit_reads'] = -1
    dec['costs']['reconstruction']['threshold_bit_visits'] = -1
    dec['assignment']['b0'] = -1
    eq(C.decode_assignment(doc, 26, de), preserved, 'all decode phases and assignment isolated')
    eq(C.encode_assignment(doc, a, de), expected['bits'], 'integer compatibility result')
    eq(type(C.encode_assignment(doc, a, de)).__name__, 'int', 'compatibility encoder is not receipt')
    eq(sorted(expected['costs']), ['authentication', 'reconstruction'], 'separate encode phases no total')
    eq(sorted(preserved['costs']), ['authentication', 'decoding', 'reconstruction'], 'separate decode phases no total')


TESTS = [('literal_f7', literal_f7), ('literal_f7_negatives', literal_negatives), ('direct_f5', direct_f5),
         ('f7_fixed_states', fixed_states), ('interleaving', interleaving), ('cross_projection', crossing),
         ('zero_projection', zero_projection), ('censored', censored), ('shadowed_bad_record', shadowed),
         ('domain_gap', gaps), ('bootstrap', bootstrap), ('layout_mutations', layout_mutations),
         ('content_mutations', content_mutations), ('bit_substitution', bit_substitution),
         ('accepted_blocks', accepted_blocks), ('fixed_root_roundtrip', roundtrips), ('fidelity', fidelity),
         ('accounting', accounting), ('nonempty_labels', labels), ('counted_encode', counted_encode),
         ('single_decode_authentication', counted_decode), ('nonzero_recurrence', nonzero_recurrence),
         ('canonical_binding', canonical_binding), ('cost_receipt_isolation', receipt_isolation)]


if __name__ == '__main__':
    for name, fn in TESTS:
        group(name, fn)
    result = {'schema': 'independent-fixed-range-review-suite/v1', 'groups': GROUPS,
              'summary': {'groups': len(GROUPS), 'passed': sum(g['passed'] for g in GROUPS),
                          'failed': sum(not g['passed'] for g in GROUPS),
                          'checks': sum(len(g['checks']) for g in GROUPS)},
              'scope': {'solver_instances': 0, 'census': False, 'benchmark': False, 'remote_jobs': 0},
              'runtime': {'python': sys.version, 'executable': sys.executable}}
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if all(g['passed'] for g in GROUPS) else 1)
