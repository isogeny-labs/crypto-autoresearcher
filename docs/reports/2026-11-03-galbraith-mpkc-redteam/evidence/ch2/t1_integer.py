"""Chapter 2 red-team: integer / modular rows (2.2.2, 2.3.x, 2.5.x, CRT, 2.6.4)."""
import math, itertools
from fractions import Fraction
log = math.log

def hdr(s): print("\n=== " + s)

# ---------- Lemma 2.5.1(4) / Lemma 2.2.2(4): bound sign ----------
hdr("Lemma 2.5.1(4): g(a,n)=log n (log a - log n + 1)")
for a, n in [(1, 100), (5, 1000), (10**3, 10**6), (0, 7), (-5, 7), (1, 1)]:
    try:
        v = log(n) * (log(a) - log(n) + 1)
    except ValueError:
        v = "undefined (log of %d)" % a
    print(f"a={a} n={n} g={v}")
print("Def 2.1.2 requires g: N^m -> R>0 and bound for ALL (a,n) with a>=N1,n>=N2;"
      " (a, n=a^2) with a large gives g<0:", log(a := 10**6) and log(a*a) * (log(a) - log(a*a) + 1))
hdr("Lemma 2.5.1(1),(2) at n=1: log(1)=0 so the bound is 0 (Def 2.1.2 needs g>0)")
print(log(1))
hdr("Lemma 2.5.1(3): a^-1 mod n for non-units")
print("a=0,n=6 -> pow(0,-1,6):", end=" ")
try: pow(0, -1, 6)
except ValueError as e: print("ValueError", e)
print("a=2,n=6:", end=" ")
try: pow(2, -1, 6)
except ValueError as e: print("ValueError", e)
hdr("Lemma 2.2.2(4): |a|>|b| allows b=0 (a=5,b=0): no q,r with 0<=r<0")

# ---------- Lemma 2.5.3 Montgomery reduction: exhaustive ----------
hdr("Lemma 2.5.3 exhaustive (odd n<200, R=2^s>n, s<=10, all 0<=a<n) + Montgomery mult w<2n")
bad = 0; cnt = 0; badm = 0
for n in range(1, 200, 2):
    for s in range(1, 11):
        R = 1 << s
        if R <= n: continue
        npr = (-pow(n, -1, R)) % R
        assert 1 <= npr < R
        Rinv = pow(R, -1, n) if n > 1 else 0
        for a in range(n):
            u = (a * npr) % R
            wp = a + u * n
            cnt += 1
            if wp % R or not (0 <= wp // R < n) or (wp // R - a * Rinv) % n:
                bad += 1
        for a in range(0, n, max(1, n // 13)):
            for b in range(0, n, max(1, n // 11)):
                x = a * b; u = (x * npr) % R; w = (x + n * u) // R
                if (x + n * u) % R or not (0 <= w < 2 * n) or (w - a * b * Rinv) % n:
                    badm += 1
print("cases", cnt, "failures", bad, "mont-mult failures", badm)

# ---------- Faster modular reduction (p.53) ----------
hdr("p.53 Faster Modular Reduction: literal q=floor(n/a) from 1/a, vs corrected floor(a*b/2^e), b=floor(2^e/n)")
print("literal: a=n^2-1 (a=O(n^2)), n=1000 -> floor(n/a)=", 1000 // (1000**2 - 1),
      " r=a-n*q =", (1000**2 - 1) - 1000 * (1000 // (1000**2 - 1)), "(not a mod n =", (1000**2 - 1) % 1000, ")")
fails = 0; tot = 0; maxerr = 0; ex = None
for n in range(3, 400):
    e = 2 * n.bit_length()
    b = (1 << e) // n          # best e-bit-precision truncation of 1/n
    for a in range(0, n * n):
        tot += 1
        q = (a * b) >> e
        if q != a // n:
            fails += 1; maxerr = max(maxerr, a // n - q)
            if ex is None: ex = (a, n, e, b, q, a // n)
print(f"corrected reading, e=2*len(n): {fails}/{tot} cases with floor(ab/2^e) != floor(a/n); max deficit {maxerr}; first {ex}")

# ---------- CRT formula p.53 ----------
hdr("CRT p.53: x = c1 + (c2-c1)(m1^-1 mod m2) m1")
out = 0; tot = 0; ex = []
for m1 in range(2, 40):
    for m2 in range(2, 40):
        if math.gcd(m1, m2) != 1: continue
        inv = pow(m1, -1, m2)
        for c1 in range(m1):
            for c2 in range(m2):
                x = c1 + (c2 - c1) * inv * m1
                assert x % m1 == c1 and x % m2 == c2
                tot += 1
                if not 0 <= x < m1 * m2:
                    out += 1
                    if len(ex) < 2: ex.append((m1, m2, c1, c2, x))
print(f"congruences always hold; x outside [0,m1m2) in {out}/{tot} cases, e.g. {ex}")

# ---------- Algorithm 1 (XGCD, symmetric remainders) ----------
hdr("Algorithm 1 as printed (-|r_{i-1}|/2 < r_i <= |r_{i-1}|/2)")
def alg1(a, b):
    r = [a, b]; s = [1, 0]; t = [0, 1]
    while r[-1] != 0:
        A, B = r[-2], r[-1]
        m = abs(B)
        rr = A % m                       # 0..m-1
        if 2 * rr > m: rr -= m           # now -m/2 < rr <= m/2
        q = (A - rr) // B
        r.append(rr); s.append(s[-2] - q * s[-1]); t.append(t[-2] - q * t[-1])
    return r[-2], s[-2], t[-2]
neg = []; badid = 0
for a in range(-30, 31):
    for b in range(-30, 31):
        d, s, t = alg1(a, b)
        if d != s * a + t * b: badid += 1
        if d != math.gcd(a, b): neg.append((a, b, d))
print("identity failures", badid, "; output != gcd in", len(neg), "pairs; e.g.",
      [x for x in neg if x[0] > 0 and x[1] > 0][:3], [x for x in neg if x[0] == 0][:2])

# ---------- Theorem 2.3.1 proof step: 1+log|r_i| <= log|r_{i-1}| ----------
hdr("Thm 2.3.1 proof: '2|r_i|<=|r_{i-1}| so 1+log(r_i)<=log(r_{i-1})' (log = natural)")
print("r_{i-2}=12, r_{i-1}=5, r_i=2 (12=2*5+2, 2<=5/2): 1+ln2 =", 1 + log(2), "> ln5 =", log(5))
print("also last iteration has r_i=0: log(0) undefined; b=1 gives bound log(a)log(1)=0")

# ---------- Lemma 2.3.3 (positive remainders) ----------
hdr("Lemma 2.3.3 items 1-8, a,b in 1..150, positive remainders")
def euclid_pos(a, b):
    r = [a, b]; s = [1, 0]; t = [0, 1]; q = [None, None]
    while r[-1] != 0:
        qq = r[-2] // r[-1]
        r.append(r[-2] - qq * r[-1]); s.append(s[-2] - qq * s[-1]); t.append(t[-2] - qq * t[-1]); q.append(qq)
    return r, s, t   # index k <-> i=k-1
fail = {k: [] for k in range(1, 9)}
N = 150
for a in range(1, N + 1):
    for b in range(1, N + 1):
        r, s, t = euclid_pos(a, b)
        L = len(r)  # i from -1 .. L-2
        I = lambda i: i + 1
        for i in range(1, L - 2):   # need s_{i+1}
            if not (abs(s[I(i)]) < abs(s[I(i + 1)]) and abs(t[I(i)]) < abs(t[I(i + 1)])):
                fail[1].append((a, b, i)); break
        for i in range(1, L - 1):
            ok = (t[I(i)] > 0) if i % 2 == 0 else (t[I(i)] < 0)
            ok2 = (s[I(i)] < 0) if i % 2 == 0 else (s[I(i)] > 0)
            if not (ok and ok2): fail[2].append((a, b, i, s[I(i)], t[I(i)])); break
        for i in range(-1, L - 2):
            if t[I(i + 1)] * s[I(i)] - t[I(i)] * s[I(i + 1)] != (-1) ** (i + 1): fail[3].append((a, b, i)); break
        for i in range(0, L - 1):
            if r[I(i)] * s[I(i - 1)] - r[I(i - 1)] * s[I(i)] != (-1) ** i * b or \
               r[I(i)] * t[I(i - 1)] - r[I(i - 1)] * t[I(i)] != (-1) ** (i - 1) * a:
                fail[4].append((a, b, i)); break
        for i in range(1, L - 2):
            if abs(Fraction(a, b) + Fraction(t[I(i)], s[I(i)])) > Fraction(1, abs(s[I(i)] * s[I(i + 1)])):
                fail[5].append((a, b, i)); break
        for i in range(0, L - 2):
            if not (abs(r[I(i)] * s[I(i)]) < abs(r[I(i)] * s[I(i + 1)]) <= b and
                    abs(r[I(i)] * t[I(i)]) < abs(r[I(i)] * t[I(i + 1)]) <= a):
                fail[6].append((a, b, i)); break
for k in range(1, 7):
    print(f"item {k}: {len(fail[k])} failing (a,b); first {fail[k][:2]}")
# item 7 / 8 targeted
def is_pair(a, b, s, t):
    r, S, T = euclid_pos(a, b)
    return any((s, t) in [(S[k], T[k]), (-S[k], -T[k])] for k in range(len(S)))
def is_triple(a, b, rr, s, t):
    r, S, T = euclid_pos(a, b)
    return any((rr, s, t) in [(r[k], S[k], T[k]), (-r[k], -S[k], -T[k])] for k in range(len(S)))
c7 = []
for a in range(1, 40):
    for b in range(1, 40):
        for s in range(1, 40):
            for t in range(-80, 1):
                if abs(Fraction(a, b) + Fraction(t, s)) < Fraction(1, 2 * s * s) and not is_pair(a, b, s, t):
                    c7.append((a, b, s, t))
print("item 7 counterexamples:", len(c7), c7[:3], " (non-coprime (s,t))")
c8 = []
for a in range(1, 30):
    for b in range(1, 30):
        for s in range(-30, 31):
            for t in range(-30, 31):
                rr = a * s + b * t
                if 2 * abs(rr * s) < b and not is_triple(a, b, rr, s, t):
                    c8.append((a, b, rr, s, t))
print("item 8 counterexamples:", len(c8), "e.g.", [x for x in c8 if x[3] == 0][:2], [x for x in c8 if x[3] != 0][:2])

# ---------- Exercise 2.6.4 ----------
hdr("Exercise 2.6.4: '2z not in Z' and existence of x with |x|<N/2")
ms = [3, 5, 7]; N = 105
cs = [0, 0, 0]
z = sum(Fraction(c * pow(N // m, -1, m), m) for c, m in zip(cs, ms))
print("m=(3,5,7), c=(0,0,0): z =", z, " 2z in Z:", (2 * z).denominator == 1)
ms = [2, 3]; N = 6; cs = [1, 0]   # x = 3 mod 6
z = sum(Fraction(c * pow(N // m, -1, m), m) for c, m in zip(cs, ms))
print("m=(2,3), c=(1,0): class 3 mod 6 has no |x|<3; z =", z, "2z in Z:", (2 * z).denominator == 1)
