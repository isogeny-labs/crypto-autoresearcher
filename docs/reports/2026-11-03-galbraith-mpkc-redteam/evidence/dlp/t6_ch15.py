"""Ch15 checks: Example 15.5.4, Example 15.5.20, L-notation numerics (Ex 15.2.12, NFS 2^87, Coppersmith 2^67),
Coppersmith constant optimisation, Lemma 15.1.6(4) numeric sanity, Theorem 15.8.2 (summation polynomials):
root property over F_p vs algebraic closure, symmetry/degree of Summ4, and Gaudry n=2 eliminant degree."""
import math, itertools
from sympy import symbols, resultant, Poly, GF, degree, expand, factor_list

print('== Example 15.5.4 ==')
p, g, h, r, g1 = 223, 15, 68, 37, 184
print('ord g =', next(k for k in range(1, p) if pow(g, k, p) == 1), ' ord g1 =', next(k for k in range(1, p) if pow(g1, k, p) == 1))
rels = [(1, 1), (33, 0), (8, 1), (7, 0)]
fb = [2, 3, 5, 7]
def fac(n):
    e = []
    for q in fb:
        c = 0
        while n % q == 0: n //= q; c += 1
        e.append(c)
    return e, n
rows = []
for z, i in rels:
    e, rem = fac(pow(g, z, p) * pow(g1, i, p) % p); rows.append(e); print(z, i, e, 'rem', rem)
e, rem = fac(h * pow(g, 7, p) * pow(g1, 2, p) % p); rows.append(e); print('h g^7 g1^2 ->', e, 'rem', rem)
v = [1, 36, 20, 17, 8]; z = [1, 33, 8, 7, 7]
print('v*A mod 37 =', [sum(v[i] * rows[i][j] for i in range(5)) % 37 for j in range(4)])
Z1 = sum(a * b for a, b in zip(v, z)) % 37; Z2 = 8
print('Z1 =', Z1, 'g^Z1 h^Z2 mod p =', pow(g, Z1, p) * pow(h, Z2, p) % p, ' log =', (-Z1 * pow(Z2, -1, 37)) % 37, ' check', pow(g, (-Z1 * pow(Z2, -1, 37)) % 37, p) == h)

print('\n== Example 15.5.20 (F_2^15, F=x^15+x+1) ==')
F = (1 << 15) | 0b11
def mul(a, b):
    res = 0
    while b:
        if b & 1: res ^= a
        b >>= 1; a <<= 1
        if a >> 15 & 1: a ^= F
    return res
def pw(a, e):
    res = 1
    while e:
        if e & 1: res = mul(res, a)
        a = mul(a, a); e >>= 1
    return res
P = lambda *exps: sum(1 << e for e in exps)
x = P(1); g_ = P(11, 7, 5, 2, 0); h_ = P(14, 11, 10, 9, 0)
print('ord x =', next(k for k in (1, 7, 31, 151, 217, 1057, 4681, 32767) if pw(x, k) == 1))
print('x^15 == x+1:', pw(x, 15) == P(1, 0), ' x^240 == x^2+x+1:', pw(x, 240) == P(2, 1, 0),
      ' x^1023 == x^3+x+1:', pw(x, 1023) == P(3, 1, 0), ' x^15345 == x^3+x^2+1:', pw(x, 15345) == P(3, 2, 0))
print('g == x^26040:', pw(x, 26040) == g_, ' h == x^9114:', pw(x, 9114) == h_, ' G=x^4+x+1 == x^3840:', pw(x, 3840) == P(4, 1, 0))
gg = pw(g_, 23) == h_; print('h == g^23:', gg, '; g has order 151:', pw(g_, 151) == 1)

print('\n== L-notation numerics ==')
L = lambda lnN, a, c: c * lnN ** a * math.log(lnN) ** (1 - a) / math.log(2)
ln = 1024 * math.log(2)
print(f'L(1/2,2)=2^{L(ln,.5,2):.2f}  L(1/2,1)=2^{L(ln,.5,1):.2f}  NFS L(1/3,1.923)=2^{L(ln,1/3,(64/9)**(1/3)):.2f}  '
      f'Coppersmith L(1/3,(32/9)^(1/3))=2^{L(ln,1/3,(32/9)**(1/3)):.2f} (book: 2^197, 2^98.5, 2^87, 2^67)')

print('\n== Coppersmith constant: f(c)=c ln2 + 2/(3 sqrt c) (relation stage), LA = 2c ln2, pair supply needs 2c ln2 - 2/(3sqrt c) >= c ln2 ==')
l2 = math.log(2)
f = lambda c: c * l2 + 2 / (3 * math.sqrt(c))
cs = [i / 10000 for i in range(1000, 40000)]
c_free = min(cs, key=f)
print(f'unconstrained argmin of relation stage: c={c_free:.4f}, c^1.5 ln2={c_free**1.5*l2:.4f} (book says optimum at 2/3)')
print(f'  -> constant max(f,2c ln2)/ln2^(1/3) at that c = {max(f(c_free), 2*c_free*l2)/l2**(1/3):.4f}  [would beat (32/9)^(1/3) if pairs sufficed]')
feas = [c for c in cs if 2 * c * l2 - 2 / (3 * math.sqrt(c)) >= c * l2 - 1e-12]
cb = min(feas, key=lambda c: max(f(c), 2 * c * l2))
print(f'with pair-supply constraint: c={cb:.4f}, c^1.5 ln2={cb**1.5*l2:.4f}, constant={max(f(cb),2*cb*l2)/l2**(1/3):.4f}, (32/9)^(1/3)={(32/9)**(1/3):.4f}')

print('\n== Theorem 15.8.2: Summ_n roots over F_p vs points in E(F_p) ==')
x1, x2, x3, x4, X = symbols('x1 x2 x3 x4 X')
def summ3(a, b, c, A, B):
    return (a - b) ** 2 * c ** 2 - 2 * ((a + b) * (a * b + A) + 2 * B) * c + ((a * b - A) ** 2 - 4 * B * (a + b))
pp, A, B = 31, 2, 3
pts = [(xx, yy) for xx in range(pp) for yy in range(pp) if (yy * yy - xx ** 3 - A * xx - B) % pp == 0]
def add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    (a, b), (c, d) = P1, P2
    if a == c and (b + d) % pp == 0: return None
    lam = (3 * a * a + A) * pow(2 * b, -1, pp) if P1 == P2 else (d - b) * pow(c - a, -1, pp)
    lam %= pp; e = (lam * lam - a - c) % pp; return (e, (lam * (a - e) - b) % pp)
good = set()
for P1 in pts:
    for P2 in pts:
        S = add(P1, P2)
        if S is not None: good.add((P1[0], P2[0], S[0]))   # P1+P2+(-S)=O
S3 = lambda a, b, c: summ3(a, b, c, A, B) % pp
roots = {(a, b, c) for a in range(pp) for b in range(pp) for c in range(pp) if S3(a, b, c) == 0}
print(f'p={pp}, E: y^2=x^3+{A}x+{B}, #E(F_p)={len(pts)+1}; #F_p-roots of Summ3 = {len(roots)}, of which from E(F_p)-points: {len(roots & good)}; extra roots: {len(roots - good)}')
ex = sorted(roots - good)[0]
nonsq = [ (t ** 3 + A * t + B) % pp for t in ex ]
print('example extra root', ex, ' x^3+Ax+B values', nonsq, ' QR?', [pow(v, (pp - 1) // 2, pp) for v in nonsq])
print('  (no y in F_p for these x: the points live on the quadratic twist / over F_p^2; statement holds only over the algebraic closure)')
print('Summ2 = x1-x2: root (x0,x0) with x0^3+Ax+B a non-square, e.g. x0 =', next(t for t in range(pp) if pow((t**3+A*t+B) % pp, (pp-1)//2, pp) == pp-1))

S4 = resultant(summ3(x1, x2, X, A, B), summ3(x3, x4, X, A, B), X)
P4 = Poly(S4, x1, x2, x3, x4, modulus=pp)
print('\nSumm4 degrees in x1..x4 (mod 31):', [P4.degree(v) for v in (x1, x2, x3, x4)], '(claim 2^(n-2)=4)')
sw = Poly(S4.subs({x2: x3, x3: x2}, simultaneous=True), x1, x2, x3, x4, modulus=pp)
ratio_ok = any((P4 * c - sw).is_zero for c in range(1, pp))
print('Summ4 symmetric under x2<->x3 (up to scalar):', ratio_ok)

print('\n== Gaudry n=2 over F_{p^2}: eliminant degree vs book bound 2^(n(n-1))=4 ==')
# F_{p^2} = F_p[t]/(t^2 - d), d non-residue; curve coefficients and x_R random in F_{p^2}
pp = 101; d = next(t for t in range(2, pp) if pow(t, (pp - 1) // 2, pp) == pp - 1)
import random; random.seed(7)
t = symbols('t')
degs = []
for trial in range(5):
    A2 = random.randrange(pp) + random.randrange(pp) * t; B2 = random.randrange(pp) + random.randrange(pp) * t
    xR = random.randrange(pp) + random.randrange(pp) * t
    E3 = expand(summ3(x1, x2, xR, A2, B2))
    PE = Poly(E3, t, x1, x2)
    # reduce t^2 -> d
    red = 0
    for (et, e1, e2), c in PE.terms():
        red += c * (d ** (et // 2)) * t ** (et % 2) * x1 ** e1 * x2 ** e2
    red = expand(red)
    G0 = Poly(red, t).coeff_monomial(1); G1 = Poly(red, t).coeff_monomial(t)
    Rx = Poly(resultant(G0, G1, x1), x2, modulus=pp)
    degs.append(Rx.degree())
print('degree in x2 of Res_x1(G1,G2) for 5 random instances:', degs, '; multihomogeneous Bezout n!*2^(n(n-1)) = 8')
