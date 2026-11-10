"""Independent answer verification for run 39882571652 (reader's own GF(2^83) arithmetic).
Curve (from the rT raw record): y^2 + xy = x^3 + a x^2 + b over GF(2)[x]/(f), f = x^83 + sum x^i for
i in field_modulus_low_terms; points are polynomial-basis integers (decimal strings).
Checks: f irreducible (Rabin test), G and every Q on the curve, l*h == #E from the ICV1 curve id,
l prime (Miller-Rabin, 40 fixed bases), [l]G == O, and [k]G == Q for every arm's recovered scalar k.
Proves-too-much: [k+1]G != Q for every point (the checker can fail).
Usage: python3 -I verify_answers.py decoded_runs.json"""
import json, sys

rows = json.load(open(sys.argv[1]))
rt = [x['decoded'] for x in rows if x['decoded']['arm'] == 'rT']
rec0 = rt[0]['records'][0]
M = int(rec0['n'])
F = (1 << M) | sum(1 << i for i in rec0['field_modulus_low_terms'])
A, B = int(rec0['a']), int(rec0['b'])
ELL = int(rec0['subgroup_order']); H = int(rec0['cofactor'])
order_from_id = int(rec0['curve_id'].split(':')[3])
trace_from_id = int(rec0['curve_id'].split(':')[2])

def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1; a <<= 1
        if a >> M & 1:
            a ^= F
    return r

def ppow(a, e):
    r = 1
    while e:
        if e & 1:
            r = pmul(r, a)
        a = pmul(a, a); e >>= 1
    return r

def inv(a):
    return ppow(a, (1 << M) - 2)

def pmod(a, m):
    dm = m.bit_length()
    while a and a.bit_length() >= dm:
        a ^= m << (a.bit_length() - dm)
    return a

def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a

def irreducible(f):
    # Rabin: x^(2^m) == x mod f, and gcd(x^(2^(m/p)) - x, f) == 1 for prime p | m (m = 83 is prime)
    m = f.bit_length() - 1
    x = 2; t = x
    for _ in range(m):
        t = pmod(_sq(t), f)
    if t != x:
        return False
    # m = 83 is prime, so the only divisor test is p = m: gcd(x^(2^1) - x, f) == 1
    assert all(m % p for p in range(2, int(m ** 0.5) + 1)), 'this test assumes prime m'
    return pgcd(f, pmod(_sq(x), f) ^ x) == 1

def _sq(a):
    r = 0; i = 0
    while a:
        if a & 1:
            r |= 1 << (2 * i)
        a >>= 1; i += 1
    return r

def on_curve(P):
    if P is None:
        return True
    x, y = P
    return pmul(y, y) ^ pmul(x, y) == pmul(pmul(x, x), x) ^ pmul(A, pmul(x, x)) ^ B

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 ^ y2 == x2:  # Q == -P (negation (x, x+y))
            return None
        if x1 == 0: return None
        lam = x1 ^ pmul(y1, inv(x1))
        x3 = pmul(lam, lam) ^ lam ^ A
        y3 = pmul(x1, x1) ^ pmul(lam ^ 1, x3)
        return (x3, y3)
    lam = pmul(y1 ^ y2, inv(x1 ^ x2))
    x3 = pmul(lam, lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = pmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)

def smul(k, P):
    R = None
    while k:
        if k & 1:
            R = add(R, P)
        P = add(P, P); k >>= 1
    return R

def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

out = {'m': M, 'field_poly_low_terms': rec0['field_modulus_low_terms'], 'a': A, 'b': B,
       'field_poly_irreducible': irreducible(F),
       'ell_times_h_equals_order_in_curve_id': ELL * H == order_from_id,
       'order_equals_2^m+1-t': order_from_id == (1 << M) + 1 - trace_from_id,
       'ell_prime_MR40': is_prime(ELL)}
G = tuple(int(v) for v in rec0['generator'])
out['G_on_curve'] = on_curve(G)
out['ell_G_is_identity'] = smul(ELL, G) is None
res = {'checked': 0, 'ok': 0, 'fail': [], 'k_plus_1_rejected': 0}
for x in rows:
    d = x['decoded']
    g = tuple(int(v) for v in d['records'][0]['generator'])
    Q = tuple(int(v) for v in d['point'])
    k = int(d['records'][0]['recovered_scalar'])
    assert g == G
    res['checked'] += 1
    good = on_curve(Q) and smul(k, G) == Q
    res['ok'] += int(good)
    if not good:
        res['fail'].append((d['arm'], d['panel']))
    res['k_plus_1_rejected'] += int(smul(k + 1, G) != Q)
out['answers'] = res
print(json.dumps(out, indent=1))
