"""Chapter 2 red-team: Jacobi (2.4.x), square roots (2.9.x), Cornacchia, Hensel, exponentiation."""
import math, random
from nt import isprime, primerange, jacobi_symbol, sqrt_mod, factorint
random.seed(1)
def hdr(s): print("\n=== " + s)

def jac(a, n):  # reference via factorisation (Definition 2.4.1)
    r = 1
    for p, e in factorint(n).items():
        a_ = a % p
        if a_ == 0: return 0
        r *= (1 if pow(a_, (p - 1) // 2, p) == 1 else -1) ** e
    return r

hdr("Theorem 2.4.3, odd n in 1..199 (incl n=1), a in -50..50")
bad = []
for n in range(1, 200, 2):
    if jac(1, n) != 1: bad.append(("one", n))
    if jac(-1, n) != (-1) ** ((n - 1) // 2): bad.append(("-1", n))
    if jac(2, n) != (-1) ** ((n * n - 1) // 8): bad.append(("2", n))
    for a in range(-50, 51):
        if jac(a, n) != jac(a % n, n): bad.append(("mod", a, n))
        if isprime(n) and n > 2 and jac(a, n) % n != pow(a, (n - 1) // 2, n) % n: bad.append(("euler", a, n))
        for b in range(-7, 8):
            if jac(a * b, n) != jac(a, n) * jac(b, n): bad.append(("mult", a, b, n))
    for m in range(1, 200, 2):
        if math.gcd(m, n) == 1 and jac(n, m) != (-1) ** ((m - 1) * (n - 1) // 4) * jac(m, n): bad.append(("QR", n, m))
print("failures:", len(bad), bad[:5])
print("Def 2.4.1 literal overlap at p|a: x^2=0 mod 3 has solution x=0, so case '1' and case '0' both apply for a=0,p=3")
print("QR with m negative: (n/m) undefined for m<0 (Jacobi needs n in N); e.g. m=-3,n=5 not covered by definition")

hdr("Exercise 2.4.7 table, primes < 20000")
bad = 0; tot = 0
for p in primerange(3, 20000):
    tot += 1
    if p % 4 == 3 and jacobi_symbol(p - 1, p) != -1: bad += 1
    if p % 4 == 1 and p % 3 == 2 and jacobi_symbol(3, p) != -1: bad += 1
    if p % 4 == 1 and p % 8 != 1:
        i = sqrt_mod(p - 1, p)
        if jacobi_symbol(i, p) != -1: bad += 1
    if p % 8 == 1 and p % 16 != 1:
        i = sqrt_mod(p - 1, p); s2 = sqrt_mod(2, p)
        z = (1 + i) * pow(s2, -1, p) % p
        # must be a primitive 8th root of unity for some choice of sqrt(2): check both signs
        zs = [z, (1 + i) * pow(-s2 % p, -1, p) % p]
        if any(jacobi_symbol(zz, p) != -1 for zz in zs): bad += 1
print("primes", tot, "failures", bad)

hdr("Lemma 2.9.1, primes 3 mod 4 < 3000, all QR a")
bad = 0
for p in primerange(3, 3000):
    if p % 4 != 3: continue
    for a in range(1, p):
        if jacobi_symbol(a, p) == 1 and pow(a, (p + 1) // 4, p) ** 2 % p != a: bad += 1
print("failures", bad)

hdr("Lemma 2.9.2 edge cases")
p, a = 7, 0
print("p=7, a=0 (a square: 0=0^2): b = a^q =", pow(a, 3, p), "-> b=0 has no multiplicative order (statement needs p∤a)")
print("p=2: p-1=2^0*1, e=0, 'order dividing 2^(e-1)=1/2' meaningless (needs p odd)")

hdr("Algorithm 3 (Tonelli-Shanks) exactly as printed; primes < 2000, all QR a")
def ts(a, p):
    e, q = 0, p - 1
    while q % 2 == 0: q //= 2; e += 1
    while True:
        n = random.randrange(2, p)
        if jacobi_symbol(n, p) == -1: break
    y = pow(n, q, p); w = pow(a, (q + 1) // 2, p); b = pow(a, q, p)
    yy = y * y % p; j = 0; cur = 1
    while cur != b:            # brute-force j (Pohlig-Hellman would be faster)
        cur = cur * yy % p; j += 1
        assert j <= 2 ** e
    return w * pow(pow(y, j, p), -1, p) % p
bad = 0; tot = 0
for p in primerange(3, 2000):
    for a in range(1, p):
        if jacobi_symbol(a, p) == 1:
            tot += 1
            if ts(a, p) ** 2 % p != a: bad += 1
print("cases", tot, "failures", bad)

hdr("Exercise 2.9.9 Atkin, p=5 mod 8 < 5000")
bad = 0
for p in primerange(5, 5000):
    if p % 8 != 5: continue
    for a in range(1, p):
        if jacobi_symbol(a, p) != 1: continue
        z = pow(2 * a, (p - 5) // 8, p); i = 2 * a * z * z % p
        w = a * z * (i - 1) % p
        if i * i % p != p - 1 or w * w % p != a: bad += 1
print("failures", bad)

hdr("Exercise 2.9.10 Cipolla: hypothesis (a/p)=1 missing")
def cip(a, t, p):  # x^((p+1)/2) in F_p[x]/(x^2 - t x + a): elements (u,v)=u+v x, x^2 = t x - a
    def mul(A, B):
        u1, v1 = A; u2, v2 = B
        # (u1+v1x)(u2+v2x) = u1u2 + (u1v2+u2v1)x + v1v2 x^2
        return ((u1 * u2 - v1 * v2 * a) % p, (u1 * v2 + u2 * v1 + v1 * v2 * t) % p)
    r = (1, 0); base = (0, 1); k = (p + 1) // 2
    while k:
        if k & 1: r = mul(r, base)
        base = mul(base, base); k >>= 1
    return r
bad_qr = 0; nonres_ex = None
for p in primerange(3, 400):
    for a in range(1, p):
        for t in range(p):
            if jacobi_symbol(t * t - 4 * a, p) != -1: continue
            u, v = cip(a, t, p)
            if jacobi_symbol(a, p) == 1:
                if v != 0 or u * u % p != a: bad_qr += 1
            elif nonres_ex is None:
                nonres_ex = (p, a, t, (u, v))
print("QR a: failures", bad_qr, "; non-residue a example (p,a,t,x^((p+1)/2)=u+v*x):", nonres_ex,
      "-> v!=0 so not an element of F_p; no square root mod p exists")

hdr("Cornacchia as printed (Euclid on 2p and x0, stop at first r<sqrt p) vs the p-version")
def corn(p, d, mod):
    if jacobi_symbol(-d % p, p) == -1 and p > 2: return None
    x0 = sqrt_mod(-d % p, p)
    if x0 is None: return None
    if 2 * x0 < p: x0 = p - x0
    A, B = mod, x0
    lim = math.isqrt(p)
    while B > lim:  # first remainder r < sqrt(p) (r=lim with lim^2<p also < sqrt p)
        A, B = B, A % B
    while B * B >= p:
        A, B = B, A % B
    r = B; t = p - r * r
    if t % d: return None
    s = math.isqrt(t // d)
    return (r, s) if s * s == t // d else None
def brute(p, d):
    for y in range(1, math.isqrt(p // d) + 1):
        x2 = p - d * y * y
        x = math.isqrt(x2)
        if x * x == x2: return (x, y)
    return None
miss2p = []; missp = 0; tot = 0
for p in primerange(3, 3000):
    for d in range(1, 30):
        sol = brute(p, d)
        if sol is None: continue
        tot += 1
        if corn(p, d, 2 * p) is None: miss2p.append((p, d, sol))
        if corn(p, d, p) is None: missp += 1
print(f"solvable (p,d): {tot}; printed 2p-version misses {len(miss2p)} e.g. {miss2p[:3]}; p-version misses {missp}")

hdr("Example 2.13.2 / Exercise 2.13.4 (quadratic Hensel)")
print("13^2 mod 27 =", 13 * 13 % 27)
bad = 0
for p in [3, 5, 7, 11]:
    for c in range(1, p):
        F = lambda x: x ** 3 + 2 * x + c
        dF = lambda x: 3 * x * x + 2
        for x in range(p):
            if F(x) % p or dF(x) % p == 0: continue
            xk, k = x, 1
            for _ in range(4):
                M = p ** (2 * k)
                xk = (xk - F(xk) * pow(dF(xk), -1, M)) % M; k *= 2
                if F(xk) % p ** k: bad += 1
print("quadratic Hensel failures:", bad)

hdr("Algorithm 2 edge cases; Example 2.8.5")
def alg2(g, n, m):
    i = math.floor(math.log2(m)) - 1
    bits = bin(m)[2:]
    b = g
    while i >= 0:
        b = b * b % n
        if bits[len(bits) - 1 - i] == '1': b = b * g % n
        i -= 1
    return b
bad = sum(1 for n in range(2, 60) for g in range(0, 2 * n) for m in range(1, 300) if alg2(g, n, m) % n != pow(g, m, n))
print("Algorithm 2 congruence failures (m>=1):", bad, "; m=1,g=10,n=7 returns", alg2(10, 7, 1), "(not reduced); m=0: log2(0) undefined")
e = 1
for op in ['s', 's', 's', 's', 'm3', 's', 's', 's', 'm3']:
    e = 2 * e if op == 's' else e + 3
print("Example 2.8.5 exponent reached:", e, "== 0b10011011 =", 0b10011011)
