"""Canonical field-to-Boolean compilation and range-only proof completion.

Prime p is a caller premise. No solver, field census or assignment-specialized
construction is used. Generic descriptors bind caller arithmetic; compile_block
additionally binds the reviewed rationality builder. Authentication is separate
from witness evaluation. All costs are counts in named, separate phases.
"""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(None)
def load(path):
    spec = importlib.util.spec_from_file_location('_range_' + Path(path).stem, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapter():
    return load('research/prime_sat_prefix_adapter_20261030/adapter.py')


def authenticated():
    return load('research/prime_sat_rationality_authenticated_20261031/authenticated.py')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(x, minimum=0):
    require(type(x) is int and x >= minimum, 'canonical integer required')
    return x


def encoded(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(x):
    return hashlib.sha256(encoded(x)).hexdigest()


def same(a, b, counts):
    counts['nodes'] += 1
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k], counts) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y, counts) for x, y in zip(a, b))
    return a == b


def fields(x, keys):
    require(type(x) is dict and set(x) == set(keys), 'exact mapping schema required')


def poly(x, p, n):
    require(type(x) is dict, 'polynomial mapping required')
    out = {}
    for k, c in x.items():
        require(type(k) is str and re.fullmatch(r'0|[1-9][0-9]*', k), 'canonical mask string required')
        require(int(k).bit_length() <= n, 'mask outside ring')
        require(integer(c, 1) < p, 'canonical nonzero residue required')
        out[k] = c
    return out


def sparse(terms, p, counts):
    out = {}
    for m, c in terms:
        counts['coefficient_merges'] += 1
        if m in out:
            counts['colliding_masks'] += 1
        out[m] = (out.get(m, 0) + c) % p
    counts['cancelled_output_terms'] += sum(c == 0 for c in out.values())
    return {str(m): c for m, c in sorted(out.items()) if c}


def substitute_equations(equations, layout, p, n):
    """Strict low-level substitution; callers supply trusted field equations."""
    integer(p, 2); integer(n)
    require(type(layout) is dict and type(equations) is list, 'equations/layout types')
    used = set()
    for name, positions in layout.items():
        require(type(name) is str and name and type(positions) is list, 'named bit list')
        require(len(positions) == (p-1).bit_length(), 'field bit width')
        for pos in positions:
            require(integer(pos) < n and pos not in used, 'unique in-ring value position')
            used.add(pos)
    costs = Counter(); output = []; labels = []
    for eq in equations:
        fields(eq, ('label', 'terms'))
        label = eq['label']
        require(type(label) is str and bool(label) and label not in labels, 'nonempty unique equation label')
        labels.append(label)
        require(type(eq['terms']) is list, 'term list')
        seen = set(); terms = []; previous = None
        for term in eq['terms']:
            fields(term, ('coefficient', 'variables'))
            c, vs = term['coefficient'], term['variables']
            require(integer(c, 1) < p, 'canonical field coefficient')
            require(type(vs) is list and all(type(v) is str and v in layout for v in vs), 'known field variables')
            require(len(vs) <= 2 and vs == sorted(vs), 'canonical degree at most two')
            monomial = tuple(vs)
            require(monomial not in seen and (previous is None or previous < monomial), 'canonical ordered unique terms')
            seen.add(monomial); previous = monomial
            expansion = [(0, c)]
            for name in vs:
                next_terms = []
                for mask, coefficient in expansion:
                    for j, bit in enumerate(layout[name]):
                        costs['products'] += 1
                        next_terms.append((mask | (1 << bit), coefficient * (1 << j) % p))
                expansion = next_terms
            terms.extend(expansion)
            costs['source_terms'] += 1
        output.append(sparse(terms, p, costs))
    return output, labels, dict(costs)


def compile_range(descriptor):
    """Authenticate layout and bind exact caller-supplied arithmetic content."""
    d = deepcopy(descriptor)
    fields(d, ('p', 'n', 'projected_bits', 'arithmetic', 'blocks'))
    p, n, m = integer(d['p'], 2), integer(d['n']), integer(d['projected_bits'])
    require(m <= n, 'projection outside ring')
    require(type(d['arithmetic']) is list and type(d['blocks']) is list, 'descriptor lists')
    arithmetic = [poly(x, p, n) for x in d['arithmetic']]
    b = (p-1).bit_length(); ones = [j for j in reversed(range(b)) if (p-1) >> j & 1]
    used = set(); names = set(); polynomials = deepcopy(arithmetic); generators = []; cnf = []; labels = []
    costs = Counter()
    for block in d['blocks']:
        fields(block, ('name', 'value_bits', 'state_bits'))
        name, values, states = block['name'], block['value_bits'], block['state_bits']
        require(type(name) is str and name and name not in names, 'unique field name')
        names.add(name)
        require(type(values) is list and len(values) == b, 'value width')
        require(type(states) is list and len(states) == len(ones)-1, 'state width')
        for pos in values + states:
            require(integer(pos) < n and pos not in used, 'duplicate/out-of-ring bit')
            used.add(pos)
        require(all(pos >= m for pos in states), 'state inside projection')
        s = [values[ones[0]]] + states
        rec = []
        for r in range(1, len(ones)):
            rec.append(len(polynomials))
            polynomials.append(sparse([(1 << s[r], 1), ((1 << s[r-1]) | (1 << values[ones[r]]), p-1)], p, costs))
            labels.append(name + ':recurrence:' + str(ones[r]))
        forbidden = []
        for j in range(b):
            if (p-1) >> j & 1:
                continue
            higher = [q for q in ones if q > j]
            r = len(higher)-1
            index = len(polynomials)
            polynomials.append({str((1 << s[r]) | (1 << values[j])): 1})
            labels.append(name + ':forbidden:' + str(j))
            forbidden.append({'local_bit': j, 'index': index, 'recurrences': rec[:r]})
            cnf.append([-(values[j]+1)] + [-(values[q]+1) for q in sorted(higher)])
        generators.append({'name': name, 'recurrences': rec, 'forbidden': forbidden})
    costs.update(blocks=len(d['blocks']), generators=len(polynomials)-len(arithmetic), clauses=len(cnf), literals=sum(map(len, cnf)))
    return {'schema': 'prime-range-compiler/v1', 'kind': 'range', 'descriptor': d,
            'p': p, 'n': n, 'projected_bits': m, 'blocks': deepcopy(d['blocks']),
            'polynomials': polynomials, 'range_labels': labels, 'generators': generators,
            'bootstrap_cnf': cnf, 'construction_costs': {'range': dict(costs)}}


def compile_block(public_descriptor):
    source = authenticated().canonical_circuit(deepcopy(public_descriptor))
    p = source['p']; b = (p-1).bit_length(); h = (p-1).bit_count()-1
    names = source['projection'] + source['auxiliaries']
    require(source['projection'] == source['inputs'] and len(set(names)) == len(names), 'source variable layout')
    m = b * len(source['projection']); total_values = b * len(names)
    blocks = [{'name': name, 'value_bits': list(range(i*b, (i+1)*b)),
               'state_bits': list(range(total_values+i*h, total_values+(i+1)*h))} for i, name in enumerate(names)]
    n = total_values + h*len(names)
    arithmetic, labels, substitution = substitute_equations(source['equations'], {x['name']: x['value_bits'] for x in blocks}, p, n)
    doc = compile_range({'p': p, 'n': n, 'projected_bits': m, 'arithmetic': arithmetic, 'blocks': blocks})
    doc.update(kind='block', public_descriptor=deepcopy(public_descriptor), source=deepcopy(source),
               source_sha256=digest(source), arithmetic_labels=labels,
               projection_decoding=[deepcopy(x) for x in blocks[:len(source['projection'])]])
    doc['construction_costs']['substitution'] = substitution
    doc['construction_costs']['source_authentication'] = {'canonical_builder_calls': 1, 'equations': len(labels), 'source_bytes': len(encoded(source))}
    return doc


def authenticate(document, trusted_descriptor, kind='block'):
    require(type(kind) is str and kind in ('block', 'range'), 'authentication kind')
    expected = compile_block(trusted_descriptor) if kind == 'block' else compile_range(trusted_descriptor)
    costs = Counter()
    require(same(document, expected, costs), 'canonical document content mismatch')
    return {'typed_comparison': dict(costs), 'construction': expected['construction_costs']}


def _encode_authenticated(document, assignment):
    """Private reconstruction core; the public caller authenticates first."""
    require(type(assignment) is dict and set(assignment) == {b['name'] for b in document['blocks']}, 'complete assignment required')
    counts = Counter()
    bits = 0; p = document['p']
    ones = [j for j in reversed(range((p-1).bit_length())) if (p-1) >> j & 1]
    counts['threshold_bit_visits'] = (p-1).bit_length()
    for block in document['blocks']:
        value = integer(assignment[block['name']]); require(value < p, 'noncanonical field assignment')
        counts['canonical_value_checks'] += 1
        for j, pos in enumerate(block['value_bits']):
            bits |= ((value >> j) & 1) << pos
            counts['value_bit_writes'] += 1
        state = (value >> ones[0]) & 1
        counts['initial_state_bit_reads'] += 1
        for j, pos in zip(ones[1:], block['state_bits']):
            state &= (value >> j) & 1
            bits |= state << pos
            counts['recurrence_products'] += 1
            counts['state_bit_writes'] += 1
    return {'bits': bits, 'costs': dict(counts)}


def encode_assignment_counted(document, assignment, trusted_descriptor, kind='block'):
    """Return canonical bits and separate successful-operation phase counts."""
    authentication = authenticate(document, trusted_descriptor, kind)
    result = _encode_authenticated(document, assignment)
    return {'bits': result['bits'], 'costs': {'authentication': authentication,
                                           'reconstruction': result['costs']}}


def encode_assignment(document, assignment, trusted_descriptor, kind='block'):
    """Integer-only compatibility API; measured callers use the counted API."""
    return encode_assignment_counted(document, assignment, trusted_descriptor, kind)['bits']


def decode_assignment(document, bits, trusted_descriptor, kind='block'):
    authentication = authenticate(document, trusted_descriptor, kind)
    require(integer(bits).bit_length() <= document['n'], 'assignment outside ring')
    result = {}; costs = Counter()
    for block in document['blocks']:
        result[block['name']] = sum(((bits >> pos) & 1) << j for j, pos in enumerate(block['value_bits']))
        costs['value_bit_reads'] += len(block['value_bits'])
    reconstructed = _encode_authenticated(document, result)
    state_mask = sum(1 << pos for block in document['blocks'] for pos in block['state_bits'])
    require((reconstructed['bits'] ^ bits) & state_mask == 0, 'noncanonical recurrence states')
    costs['state_bit_checks'] = state_mask.bit_count()
    return {'assignment': result, 'costs': {'authentication': authentication,
            'decoding': dict(costs), 'reconstruction': reconstructed['costs']}}


def range_certificate(document, depth, prefix):
    n, p = document['n'], document['p']
    require(integer(depth) <= n and integer(prefix).bit_length() <= depth, 'prefix outside ring')
    for block, gen in zip(document['blocks'], document['generators']):
        minimum = sum(((prefix >> pos) & 1) << j for j, pos in enumerate(block['value_bits']) if pos < depth)
        if minimum < p:
            continue
        j = (minimum ^ (p-1)).bit_length()-1
        info = next(x for x in gen['forbidden'] if x['local_bit'] == j)
        multipliers = [{} for _ in document['polynomials']]
        multipliers[info['index']] = {'0': 1}
        for index in info['recurrences']:
            multipliers[index] = {'0': p-1}
        return {'depth': depth, 'prefix': prefix, 'clause': adapter()._block(prefix, depth), 'certificate': multipliers}
    return None


def complete_transcript(document, trusted_descriptor, answer, kind='block', bootstrap_cnf=None):
    """Append domain proofs, retain invalid original records, never promote status.

Missing trie subtrees with a domain-valid minimum are reported as gaps without
exploring their Boolean cubes. Final acceptance belongs to the frozen adapter.
"""
    authentication = authenticate(document, trusted_descriptor, kind)
    raw = deepcopy(answer); augmented = deepcopy(answer)
    actual_cnf = deepcopy(document['bootstrap_cnf'] if bootstrap_cnf is None else bootstrap_cnf)
    counts = Counter(); comparison = Counter()
    require(same(actual_cnf, document['bootstrap_cnf'], comparison), 'bootstrap CNF content mismatch')
    output = {'original': raw, 'augmented': augmented, 'bootstrap_cnf': actual_cnf,
              'original_sha256': digest(raw), 'document_sha256': digest(document),
              'gaps': [], 'checker_result': None, 'failure': None,
              'costs': {'authentication': authentication, 'bootstrap_comparison': dict(comparison)}}
    try:
        require(type(raw) is dict and all(k in raw for k in ('status', 'models', 'learned')), 'answer fields')
        require(type(raw['models']) is list and type(raw['learned']) is list, 'answer lists')
        n, m, p = document['n'], document['projected_bits'], document['p']
        trie = {}; terminal = 'terminal'
        def insert(depth, prefix):
            require(integer(depth) <= n and integer(prefix).bit_length() <= depth, 'bounded prefix required')
            node = trie
            for i in range(depth):
                counts['insertion_bit_visits'] += 1
                node = node.setdefault((prefix >> i) & 1, {})
            node[terminal] = True
        for model in raw['models']:
            require(integer(model).bit_length() <= n, 'model outside ring')
            insert(m, model & ((1 << m)-1))
        for item in raw['learned']:
            require(type(item) is dict and 'depth' in item and 'prefix' in item, 'learned prefix fields')
            insert(item['depth'], item['prefix'])
        # Explicit enter/leave stack: one minima array and O(depth) undo state.
        positions = {pos: (i, 1 << j) for i, block in enumerate(document['blocks']) for j, pos in enumerate(block['value_bits'])}
        minima = [0] * len(document['blocks']); invalid = 0
        stack = [('visit', 0, 0, trie)]
        while stack:
            operation, depth, prefix, node = stack.pop()
            if operation in ('add', 'undo'):
                if depth in positions:
                    i, weight = positions[depth]; before = minima[i] >= p
                    minima[i] += weight if operation == 'add' else -weight
                    invalid += int(minima[i] >= p) - int(before)
                    counts['minimum_updates'] += 1
                continue
            counts['trie_visits'] += 1
            if terminal in node:
                continue
            if invalid:
                proof = range_certificate(document, depth, prefix)
                require(proof is not None, 'range certificate construction')
                augmented['learned'].append(proof)
                counts['emitted_certificates'] += 1
                counts['multiplier_vector_entries'] += len(proof['certificate'])
                counts['multiplier_nonzeros'] += sum(bool(x) for x in proof['certificate'])
                counts['certificate_serialization_bytes'] += len(encoded(proof))
                continue
            if not node or depth == n:
                output['gaps'].append({'depth': depth, 'prefix': prefix, 'zero_suffix_value_domain_witness': prefix,
                                       'arithmetic_root_asserted': False})
                continue
            stack.extend([('undo', depth, 0, None), ('visit', depth+1, prefix | (1 << depth), node.get(1, {})),
                          ('add', depth, 0, None), ('visit', depth+1, prefix, node.get(0, {}))])
        output['checker_result'] = adapter().verify_transcript(p, n, m, document['polynomials'], [], augmented, aux_bound=None)
        output['costs']['final_verifier'] = output['checker_result']['costs']
    except (ValueError, KeyError, TypeError, IndexError) as error:
        output['failure'] = {'type': type(error).__name__, 'message': str(error)}
    output['costs']['completion'] = dict(counts)
    output['costs']['serialization'] = {'raw_bytes': len(encoded(raw)), 'augmented_bytes': len(encoded(augmented)), 'bootstrap_bytes': len(encoded(actual_cnf))}
    return output
