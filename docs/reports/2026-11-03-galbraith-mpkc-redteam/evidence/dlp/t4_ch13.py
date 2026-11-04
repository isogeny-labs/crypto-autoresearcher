"""Chapter 13 checks: Algorithm 13 (Pohlig-Hellman as printed), Example 13.2.3, Ex 13.2.7 inequality,
Algorithm 14 (BSGS as printed) termination, Lemma 13.4.4 small exhaustive, Lemma 13.5.6 counterexample
illustration, Lemma 13.6.6 / 13.6.7 / Thm 13.6.9 exhaustive checks, 'WLOG w even' counterexample."""
import math, itertools
from fractions import Fraction
from math import comb
from sympy import factorint, primitive_root, isprime

def alg13(g, h, N, fac, mod):
    """Algorithm 13 exactly as printed (group = <g> in F_mod^*)."""
    res = []
    for l, e in fac.items():
        ai = 0
        for j in range(1, e + 1):
            g0 = pow(g, N // l ** j, mod); h0 = pow(h, N // l ** j, mod)
            u = pow(g0, -ai, mod); h0 = h0 * u % mod
            if h0 != 1:
                g0 = pow(g, N // l, mod); b = 1; T = g0
                while h0 != T:
                    b += 1; T = T * g0 % mod
                ai += b * l ** (j - 1)
        res.append((ai, l ** e))
    a, M = 0, 1
    for r, m in res:  # CRT
        a = a + M * ((r - a) * pow(M, -1, m) % m); M *= m
    return a % M

print('== Algorithm 13 exhaustive on F_p^* (all h) ==')
cnt = 0
for p in [19, 31, 73, 97, 109, 163, 257, 433, 577, 769]:
    g = primitive_root(p); N = p - 1; fac = factorint(N)
    for a in range(N):
        assert alg13(g, pow(g, a, p), N, fac, p) == a
        cnt += 1
print('all correct,', cnt, 'instances; Example 13.2.3 (p=19,g=2,h=5) ->', alg13(2, 5, 18, {2: 1, 3: 2}, 19))

print('\n== Ex 13.2.7: sum x_i <= B log N / log B for 2<=x_i<=B, B>3 ==')
# max of sum x_i / log(prod x_i) = max_x x/log x over [2,B]
for B in range(3, 60):
    worst = max(x / math.log(x) for x in range(2, B + 1))
    ok = worst <= B / math.log(B) + 1e-12
    if not ok or B in (3, 4, 5):
        print(f'B={B}: max x/log x = {worst:.4f}, B/log B = {B/math.log(B):.4f}, holds={ok}')
print('(tight at B=4: 2/ln2 = 4/ln4)')

print('\n== Algorithm 14 as printed, h not in <g> ==')
p = 23; g = 2  # order 11
r = 11; m = math.isqrt(r - 1) + 1
L = {pow(g, i, p): i for i in range(m + 1)}
u = pow(g, -m, p); y = 5; j = 0  # 5 is not in <2> mod 23 (2 is a QR, 5 is a non-residue)
while y not in L and j < 10 ** 5:
    y = y * u % p; j += 1
print(f'giant-step loop still running after j={j} iterations (no bound in line 10); line 16 "return ⊥" unreachable')

print('\n== Lemma 13.4.4 (Schwartz-Zippel) exhaustive, r=5, k=2, total degree <=2 ==')
r = 5; mons = [(i, j) for i in range(3) for j in range(3) if i + j <= 2]
worst = 0
for coeffs in itertools.product(range(r), repeat=len(mons)):
    if not any(coeffs): continue
    d = max(i + j for (i, j), c in zip(mons, coeffs) if c)
    if d == 0: continue  # nonzero constant: no zeros
    z = sum(1 for x in range(r) for y in range(r) if sum(c * x ** i * y ** j for (i, j), c in zip(mons, coeffs)) % r == 0)
    worst = max(worst, Fraction(z, r * r) / Fraction(d, r))
print('max Pr[F=0]/(d/r) =', worst, '(<=1 required)')

print('\n== Lemma 13.5.6 counterexample (l=2, S1=S2=Z/rZ): BSGS with a1=0 ==')
for p in [2003, 20011, 200003, 2000003]:
    # find prime r | p-1 large
    r = max(factorint(p - 1)); g = pow(primitive_root(p), (p - 1) // r, p)
    g1, g2 = g, pow(g, 7, p); a = (r * 3) // 5; h = pow(g, a, p)
    m = math.isqrt(r - 1) + 1; L = {}; x = 1; ops = 0
    for i in range(m): L[x] = i; x = x * g2 % p; ops += 1
    u = pow(g2, -m, p); y = h; jj = 0
    while y not in L: y = y * u % p; jj += 1; ops += 1
    a2 = (L[y] + m * jj) % r
    assert pow(g1, 0, p) * pow(g2, a2, p) % p == h
    print(f'r={r}: representation h=g1^0 g2^{a2} found with {ops} group ops; #S1^(l/2) = r = {r}; ratio ops/r={ops/r:.4f}')

print('\n== Lemma 13.6.6 splitting system (cyclic B_i, i<n/2), exhaustive ==')
for n in range(2, 19, 2):
    for w in range(0, n + 1, 2):
        Bs = [frozenset((i + j) % n for j in range(n // 2)) for i in range(n // 2)]
        for Y in itertools.combinations(range(n), w):
            Ys = set(Y)
            assert any(len(Ys & B) == w // 2 for B in Bs), (n, w, Y)
print('holds for all even n<=18, even w<=n')

print('\n== Lemma 13.6.7 formula, exhaustive n<=14 ==')
for n in range(2, 15, 2):
    for w in range(0, n + 1, 2):
        Y = set(range(w)); good = sum(1 for B in itertools.combinations(range(n), n // 2) if len(Y & set(B)) == w // 2)
        assert Fraction(good, comb(n, n // 2)) == Fraction(comb(w, w // 2) * comb(n - w, (n - w) // 2), comb(n, n // 2))
print('formula exact for all even n<=14, even w')

print('\n== Thm 13.6.9 proof inequalities: 2^k/sqrt(2k) <= C(k,k/2) <= 2^k sqrt(2/(pi k)), even k ==')
lc = lambda k: math.lgamma(k + 1) - 2 * math.lgamma(k // 2 + 1)
viol = [k for k in range(2, 4001, 2) if not (k * math.log(2) - 0.5 * math.log(2 * k) <= lc(k) <= k * math.log(2) + 0.5 * math.log(2 / (math.pi * k)))]
print('violations for even k in [2,4000]:', viol[:10])
mx = 0; arg = None
for n in range(2, 401, 2):
    for w in range(2, n, 2):
        v = math.exp(lc(n) - lc(w) - lc(n - w)) / math.sqrt(w)
        if v > mx: mx, arg = v, (n, w)
print(f'max (1/p_YB)/sqrt(w) over even 2<=w<n<=400: {mx:.4f} at {arg}; sqrt(8/pi)={math.sqrt(8/math.pi):.4f}')

print('\n== "WLOG n,w even (add one)": Algorithm 15 searches weight exactly w/2 per half ==')
n0, w0 = 6, 3; n, w = 6, 4
a = 0b000111  # weight 3 = w0
found = False
for B in itertools.combinations(range(n), n // 2):
    I_B = [i for i in range(n) if i not in B]
    for Y1 in itertools.combinations(B, w // 2):
        for Y2 in itertools.combinations(I_B, w // 2):
            if sum(2 ** j for j in Y1 + Y2) == a: found = True
print(f'a={a} (weight {w0}) found by Algorithm 15 with w:=4 over ALL B? {found}')
