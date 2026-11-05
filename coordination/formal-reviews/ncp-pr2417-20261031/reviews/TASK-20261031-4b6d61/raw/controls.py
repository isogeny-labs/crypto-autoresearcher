#!/usr/bin/env python3
"""Exact finite arithmetic controls for TASK-20261031-4b6d61.

These stdlib computations model the stated operations. They do not invoke Lean,
elaborate a theorem, test a serialized curve parser, or measure performance.
"""
import itertools
import json
import math


def action(points, word, x, modulus=None):
    for letter in word:
        x = -x if letter == 'neg' else x + points[letter]
        if modulus is not None:
            x %= modulus
    return x


def shadow(word, size):
    sign = (-1) ** word.count('neg')
    counts = [0] * size
    for index, letter in enumerate(word):
        if letter != 'neg':
            counts[letter] += (-1) ** word[index + 1:].count('neg')
    return sign, counts


def order(p, modulus):
    return modulus // math.gcd(p, modulus)


result = {'scope': 'exact finite arithmetic source controls; not Lean replay'}
chronological = []
for word, expected in [([0, 'neg'], -1), (['neg', 0], 1), ([], 0)]:
    value = action([1], word, 0)
    sign, counts = shadow(word, 1)
    assert value == expected == sign * 0 + counts[0]
    chronological.append({'word': word, 'start': 0, 'point': 1,
                          'result': value, 'shadow_sign': sign,
                          'signed_counts': counts, 'expected': expected})
assert chronological[0]['result'] != chronological[1]['result']
result['chronological_order'] = chronological

panels = []
for ambient, p, n in [(2, 1, 2), (5, 1, 5), (6, 3, 2)]:
    assert order(p, ambient) == n
    encode = lambda x: (x * p) % ambient
    checks = 0
    for length in range(4):
        for word in itertools.product([0, 'neg'], repeat=length):
            sign, counts = shadow(word, 1)
            for s, x, y in itertools.product(range(n), repeat=3):
                scalar = action([s], word, x, n)
                point = action([encode(s)], word, encode(x), ambient)
                assert point == encode(scalar)
                assert scalar == (sign * x + counts[0] * s) % n
                assert (point == encode(y)) == (scalar == y)
                checks += 1
    panels.append({'ambient_ZMod': ambient, 'P': p, 'n': n,
                   'addOrderOf_P': order(p, ambient), 'B': 1,
                   'word_lengths': [0, 1, 2, 3],
                   'point_encode_normal_form_iff_checks': checks,
                   'passed': True})
result['positive_canonical_encoding'] = panels

ambient, p, n, x, y = 2, 0, 2, 0, 1
encode = lambda scalar: scalar * p % ambient
lhs = action([encode(1)], [], encode(x), ambient) == encode(y)
rhs = action([1], [], x, n) == y
assert (n * p) % ambient == 0
assert lhs is True and rhs is False
assert order(p, ambient) == 1 != n
result['omitted_order_false_case'] = {
    'ambient_ZMod': ambient, 'P': p, 'n': n, 's': [1], 'word': [],
    'x': x, 'y': y, 'n_smul_P_eq_zero': True,
    'addOrderOf_P': order(p, ambient), 'order_hypothesis_holds': False,
    'point_equality': lhs, 'scalar_equality': rhs,
    'iff_without_order_is_false': lhs != rhs,
    'failure_kind': 'exact arithmetic counterexample to omitted hypothesis; no Lean application attempted'}

# The second proves-too-much object assigned in the precommitted plan:
# in C2 x C2, t=(1,0), nu=(0,1) satisfy the presentation relators;
# their action on Z/2 sends t to flip and nu to identity.
elements = list(itertools.product(range(2), repeat=2))
identity, t, nu = (0, 0), (1, 0), (0, 1)
mul = lambda u, v: ((u[0] + v[0]) % 2, (u[1] + v[1]) % 2)
assert mul(t, t) == mul(nu, nu) == identity
assert mul(mul(nu, t), mul(nu, t)) == identity
assert nu != identity
images = {u: tuple((u[0] + ((-1) ** u[1]) * x) % 2 for x in range(2))
          for u in elements}
assert images[nu] == images[identity] and len(set(images.values())) == 2
result['order_two_full_kernel_control'] = {
    'n': 2, 'B': 1, 's': [1], 'abstract_group': 'C2 x C2',
    'presentation_relators_hold': True, 'nu_nonidentity_in_abstract_group': True,
    'nu_permutation_is_identity': True,
    'abstract_elements': [list(u) for u in elements],
    'permutation_images': [{'element': list(u), 'image': list(images[u])} for u in elements],
    'extra_action_kernel_element': list(nu),
    'scope': 'rejects extending historical full action-kernel presentation to n=2; no verdict on J2'}

result['all_assertions_passed'] = True
print(json.dumps(result, indent=2, sort_keys=True))
