"""Chapter 2 red-team: finite fields / polynomials (2.10-2.16)."""
import math, random, itertools
from fractions import Fraction
from nt import isprime, factorint
random.seed(2)
def hdr(s): print("\n=== " + s)

# ---- polynomial arithmetic over F_p, coefficient lists low->high ----
def trim(a):
    while a and a[-1] == 0: a.pop()
    return a
def padd(a, b, p):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)])
def psub(a, b, p): return padd(a, [(-x) % p for x in b], p)
def pmul(a, b, p):
    if not a or not b: return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % p
    return trim(r)
def pdivmod(a, b, p):
    a = a[:]; q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], -1, p)
    while len(a) >= len(b) and a:
        c = a[-1] * inv % p; k = len(a) - len(b); q[k] = c
        for i, y in enumerate(b): a[i + k] = (a[i + k] - c * y) % p
        trim(a)
    return trim(q), a
def pmod(a, b, p): return pdivmod(a, b, p)[1]
def pgcd(a, b, p):
    while b: a, b = b, pmod(a, b, p)
    if a: inv = pow(a[-1], -1, p); a = [x * inv % p for x in a]
    return a
def ppowmod(a, e, f, p):
    r = [1]; a = pmod(a, f, p)
    while e:
        if e & 1: r = pmod(pmul(r, a, p), f, p)
        a = pmod(pmul(a, a, p), f, p); e >>= 1
    return r
def irreducible(f, p):
    d = len(f) - 1
    xp = [0, 1]
    for k in range(1, d // 2 + 1):
        xp = ppowmod(xp, p, f, p)
        if len(pgcd(f, psub(xp, [0, 1], p), p)) > 1: return False
    return True
def find_irred(p, m):
    for c in itertools.product(range(p), repeat=m):
        f = list(c) + [1]
        if f[0] and irreducible(f, p): return f
class GF:
    def __init__(s, p, m):
        s.p, s.m, s.f = p, m, find_irred(p, m)
        s.q = p ** m
    def el(s, i):
        c = []
        for _ in range(s.m): c.append(i % s.p); i //= s.p
        return trim(c)
    def mul(s, a, b): return pmod(pmul(a, b, s.p), s.f, s.p)
    def pow(s, a, e):
        r = [1]
        while e:
            if e & 1: r = s.mul(r, a)
            a = s.mul(a, a); e >>= 1
        return r
    def add(s, a, b): return padd(a, b, s.p)
    def inv(s, a): return s.pow(a, s.q - 2)
    def vec(s, a): return [(a[i] if i < len(a) else 0) for i in range(s.m)]
def rank_mod_p(rows, p):
    rows = [r[:] for r in rows]; rk = 0; ncol = len(rows[0])
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c] % p), None)
        if piv is None: continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][c], -1, p)
        rows[rk] = [x * inv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c] % p:
                t = rows[i][c]; rows[i] = [(x - t * y) % p for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk

hdr("Lemma 2.11.2: g^-1 = N(g)^-1 prod_{i=1}^{m-1} g^{q^i}  (q=p prime, small fields)")
bad = 0; tot = 0
for p, m in [(2, 2), (2, 3), (2, 5), (3, 2), (3, 3), (5, 2), (7, 3)]:
    K = GF(p, m)
    for i in range(1, K.q):
        g = K.el(i); prod = [1]
        for k in range(1, m): prod = K.mul(prod, K.pow(g, p ** k))
        N = K.mul(g, prod)
        assert len(N) <= 1
        lhs = K.inv(g); rhs = K.mul([pow(N[0], -1, p)], prod)
        tot += 1; bad += (lhs != rhs)
print("cases", tot, "failures", bad)

hdr("Lemma 2.14.8 half trace (m odd): is x^2+x = alpha for every alpha?")
for m in [3, 5, 7]:
    K = GF(2, m); fails = 0; trace1 = 0
    for i in range(K.q):
        a = K.el(i); x = []
        for k in range((m - 1) // 2 + 1): x = K.add(x, K.pow(a, 2 ** (2 * k)))
        tr = []
        for k in range(m): tr = K.add(tr, K.pow(a, 2 ** k))
        ok = K.add(K.mul(x, x), x) == a
        if not ok: fails += 1
        if tr == [1]: trace1 += 1
        assert ok == (tr == [])
    print(f"m={m}: fails for {fails}/{K.q} alpha; #Tr(alpha)=1 is {trace1} (fails exactly when Tr=1)")

hdr("Itoh-Tsujii identity 2^{m-1}-1 = (2^{2^{k-1}}-1)2^{2^{k-1}} + (2^{2^{k-1}}-1), m=2^k+1")
print(all(2 ** (2 ** k) - 1 == (2 ** (2 ** (k - 1)) - 1) * 2 ** (2 ** (k - 1)) + 2 ** (2 ** (k - 1)) - 1 for k in range(1, 8)))

hdr("Exercise 2.14.5 sqrt formula in F_2^m (m odd), with typo x_{m-1} read as a_{m-1}")
for m in [3, 5, 7]:
    K = GF(2, m); sx = K.pow([0, 1], 2 ** (m - 1)); bad = 0
    for i in range(K.q):
        g = K.el(i); a = K.vec(g)
        ev = trim([a[2 * j] for j in range((m + 1) // 2)])
        od = trim([a[2 * j + 1] for j in range((m - 1) // 2)])
        r = K.add(ev, K.mul(sx, od))
        bad += K.mul(r, r) != g
    print(f"m={m}: failures {bad}")

hdr("Theorem 2.14.2: 'there are q - m(m-1) elements u in F_q with G(u) normal' (exact count?)")
for p, m in [(5, 2), (7, 2), (11, 2), (13, 2), (7, 3), (11, 3), (13, 3)]:
    K = GF(p, m); F = K.f
    # alpha = x (class of x) is a root of F
    alpha = [0, 1]
    # synthetic division F(X)/(X - alpha) in K[X]
    coeffs = [[c] if c else [] for c in F]        # elements of K
    n = len(coeffs) - 1; Q = [None] * n; carry = []
    for k in range(n, 0, -1):
        carry = K.add(coeffs[k], K.mul(carry, alpha)) if k < n else coeffs[k]
        Q[k - 1] = carry
    dF = []
    for k in range(1, n + 1):
        if coeffs[k]: dF = K.add(dF, K.mul([k * coeffs[k][0] % p], K.pow(alpha, k - 1)))
    dinv = K.inv(dF)
    cnt = 0
    for u in range(p):
        val = []
        for k in range(n - 1, -1, -1): val = K.add(K.mul(val, [u] if u else []), Q[k])
        th = K.mul(val, dinv)
        rows = [K.vec(K.pow(th, p ** i)) for i in range(m)]
        cnt += rank_mod_p(rows, p) == m
    print(f"q={p} m={m}: #normal G(u) = {cnt}, q-m(m-1) = {p - m * (m - 1)}")

hdr("Exercise 2.12.9: F not square-free -> R_2 can have degree-1 factors")
p = 5; F = pmul([0, 1], [0, 1], p)            # x^2
R1 = pgcd(F, psub(ppowmod([0, 1], p, F, p), [0, 1], p), p)
F1 = pdivmod(F, R1, p)[0]
R2 = pgcd(F1, psub(ppowmod([0, 1], p * p, F1, p), [0, 1], p), p) if len(F1) > 1 else F1
print("F=x^2 over F_5: R1 =", R1, " F/R1 =", F1, " R2 =", R2, "(degree 1, not 2)")

hdr("Normal-basis probability (2.14.1 cites >=1/34 if m<q^4, >=1/(16 log_q m) if m>=q^4)")
def ordmod(q, d):
    if d == 1: return 1
    k, x = 1, q % d
    while x != 1: x = x * q % d; k += 1
    return k
def phi(n):
    r = n
    for l in factorint(n): r = r // l * (l - 1)
    return r
worst = {}
viol = []
for q in [2, 3, 4, 5, 7, 8, 9]:
    pchar = min(factorint(q))
    for m in range(1, 3001):
        mp = m
        while mp % pchar == 0: mp //= pchar
        pr = 1.0
        for d in range(1, mp + 1):
            if mp % d == 0:
                o = ordmod(q, d); pr *= (1 - q ** (-o)) ** (phi(d) // o)
        bound = 1 / 34 if m < q ** 4 else 1 / (16 * math.log(m, q))
        if pr < bound: viol.append((q, m, pr, bound))
        worst[q] = min(worst.get(q, 1), pr / bound)
print("violations:", viol[:5], "; min ratio prob/bound per q:", {k: round(v, 3) for k, v in worst.items()})

hdr("Lemma A.5.1 / 2.14.1: #monic irreducibles N_{m,q} >= q^m/(2m)")
def mobius(n):
    f = factorint(n)
    return 0 if any(e > 1 for e in f.values()) else (-1) ** len(f)
viol = []
for q in [2, 3, 4, 5, 7, 8, 9, 16, 25]:
    for m in range(1, 41):
        N = sum(mobius(d) * q ** (m // d) for d in range(1, m + 1) if m % d == 0) // m
        if 2 * m * N < q ** m: viol.append((q, m, N))
print("violations:", viol)

hdr("2.15.3: phi(q-1)/(q-1) >= 1/(6 log log q) for prime powers q <= 2*10^5")
viol = []
for q in range(3, 200001):
    f = factorint(q)
    if len(f) != 1: continue
    lhs = phi(q - 1) / (q - 1); rhs = 1 / (6 * math.log(math.log(q)))
    if lhs < rhs: viol.append((q, round(lhs, 3), round(rhs, 3)))
print("violations:", viol)

hdr("2.15 intro: 'smallest 0<=f<=e_i with g^{(q-1)/l_i^f}=1'")
q = 13; g = 3   # order 3
for l, e in factorint(q - 1).items():
    fs = [f for f in range(e + 1) if pow(g, (q - 1) // l ** f, q) == 1]
    print(f"l={l}: f with g^((q-1)/l^f)=1: {fs}; smallest = {min(fs)} always 0; largest gives v_l(ord)=e-f")

hdr("Algorithm 5: expected while-loop iterations (proof claims <= 2)")
def exp_iters(ls):
    E = 0.0
    for n in range(0, 200):
        E += 1 - math.prod(1 - l ** (-n) for l in ls)
    return E
for ls in [[2], [2, 3], [2, 3, 5], [2, 3, 5, 7, 11, 13]]:
    print(ls, "E[iterations] =", round(exp_iters(ls), 4))
# simulation q = 31 (q-1 = 2*3*5)
q = 31; fac = factorint(q - 1); runs = 20000; tot = 0
for _ in range(runs):
    S = set(fac); it = 0
    while S:
        it += 1; g = random.randrange(1, q)
        for l in list(S):
            gi = pow(g, (q - 1) // l ** fac[l], q)
            if pow(gi, l ** (fac[l] - 1), q) != 1: S.discard(l)
    tot += it
print("simulated q=31:", tot / runs)

hdr("Lemma 2.15.4 + Algorithm 4 (square-and-multiply cost) vs bound 2*ceil(log2 m)*log(N), log natural")
def S_lj(k, l, j): return set(range((j - 1) * 2 ** (k - l) + 1, j * 2 ** (k - l) + 1))
ok = True
for k in range(1, 7):
    S = set(range(1, 2 ** k + 1))
    for l in range(1, k + 1):
        if set().union(*[S_lj(k, l, j) for j in range(1, 2 ** l + 1)]) != S: ok = False
        for j in range(1, 2 ** l + 1):
            if len(S_lj(k, l, j)) != 2 ** (k - l): ok = False
            if l >= 2 and j <= 2 ** (l - 1) and S_lj(k, l - 1, j) != S_lj(k, l, 2 * j - 1) | S_lj(k, l, 2 * j): ok = False
    if any(S_lj(k, k, j) != {j} for j in range(1, 2 ** k + 1)): ok = False
print("Lemma 2.15.4 all items:", ok)
P = 2 ** 127 - 1
def sqmul_cost(e): return 0 if e <= 1 else (e.bit_length() - 1) + (bin(e).count('1') - 1)
def alg4(Ns, g, mod):
    m = len(Ns); k = math.ceil(math.log2(m)); Ns = Ns + [1] * (2 ** k - m); cost = 0
    def E(idx): return math.prod(Ns[i - 1] for i in idx)
    h = {}
    e1 = E(range(2 ** (k - 1) + 1, 2 ** k + 1)); e2 = E(range(1, 2 ** (k - 1) + 1))
    h[(1, 1)] = pow(g, e1, mod); h[(1, 2)] = pow(g, e2, mod); cost += sqmul_cost(e1) + sqmul_cost(e2)
    for l in range(2, k + 1):
        for j in range(1, 2 ** l + 1):
            j1 = (j + 1) // 2; e = E(S_lj(k, l - 1, j1) - S_lj(k, l, j))
            h[(l, j)] = pow(h[(l - 1, j1)], e, mod); cost += sqmul_cost(e)
    return [h[(k, j)] for j in range(1, m + 1)], cost
for Ns in [[2 ** 10 - 1, 2 ** 10 - 3], [2 ** 20 - 1] * 2, [2 ** 13 - 1, 2 ** 17 - 1, 2 ** 19 - 1, 2 ** 31 - 1], [random.getrandbits(40) | 1 for _ in range(16)]]:
    out, cost = alg4(Ns, 3, P); N = math.prod(Ns)
    correct = out == [pow(3, N // x, P) for x in Ns]
    k = math.ceil(math.log2(len(Ns)))
    print(f"m={len(Ns)} correct={correct} cost={cost} bound 2k ln N={2 * k * math.log(N):.1f} bound 2k log2 N={2 * k * math.log2(N):.1f}")
print("m=1: k=ceil(log2 1)=0, line 2 uses N_{2^{-1}+1}, returns h_{0,1}: undefined")
# recursive F ordering
def Frec(g, Ns, mod):
    m = len(Ns)
    if m == 1: return [g]
    l = m // 2
    h1 = pow(g, math.prod(Ns[:l]), mod); h2 = pow(g, math.prod(Ns[l:]), mod)
    return Frec(h1, Ns[l:], mod) + Frec(h2, Ns[:l], mod)
Ns = [3, 5, 7]; N = 105
print("recursive F as printed:", Frec(2, Ns, 10 ** 9 + 7), " target order g^{N/N_i}, i=1..m:", [pow(2, N // x, 10 ** 9 + 7) for x in Ns])

hdr("Addition chains: 'every m has a chain of length log2 m + log2 wt(m)' (book's length l counts m1=1)")
def l_star_free(n, maxlen=12):
    # minimal number of additions via iterative-deepening DFS over ascending chains
    if n == 1: return 0
    for L in range(1, maxlen + 1):
        chain = [1]
        def dfs():
            last = chain[-1]
            if last == n: return True
            if len(chain) - 1 == L: return False
            if last << (L - (len(chain) - 1)) < n: return False
            seen = set()
            for i in range(len(chain) - 1, -1, -1):
                for j in range(i, -1, -1):
                    s = chain[i] + chain[j]
                    if s <= last or s > n or s in seen: continue
                    seen.add(s); chain.append(s)
                    if dfs(): return True
                    chain.pop()
            return False
        if dfs(): return L
for m in [2, 8, 127, 191]:
    L = l_star_free(m)
    wt = bin(m).count('1')
    print(f"m={m}: min #additions={L} (book length l={L + 1}); log2 m + log2 wt = {math.log2(m) + math.log2(wt):.3f}")

hdr("Theorem 2.16.1 multipoint evaluation as sketched (with G_{t,1} for G_{t,0}); F_p, p=10007")
p = 10007; bad = 0
for n in [1, 2, 3, 5, 8, 13]:
    F = [random.randrange(p) for _ in range(n)] + [random.randrange(1, p)]
    xs = [random.randrange(p) for _ in range(n)]
    t = math.ceil(math.log2(n)) if n > 1 else 0
    X = xs + [0] * (2 ** t - n)
    G = {(0, j): [(-X[j - 1]) % p, 1] for j in range(1, 2 ** t + 1)}
    for i in range(1, t + 1):
        for j in range(1, 2 ** (t - i) + 1): G[(i, j)] = pmul(G[(i - 1, 2 * j - 1)], G[(i - 1, 2 * j)], p)
    Fij = {(t, 1): pmod(F, G[(t, 1)], p)}
    for i in range(t - 1, -1, -1):
        for j in range(1, 2 ** (t - i) + 1): Fij[(i, j)] = pmod(Fij[(i + 1, (j + 1) // 2)], G[(i, j)], p)
    got = [(Fij[(0, j)] or [0])[0] for j in range(1, n + 1)]
    ref = [sum(c * pow(x, k, p) for k, c in enumerate(F)) % p for x in xs]
    bad += got != ref
print("failures:", bad)

hdr("Horner as printed: ((F_d a)a + F_{d-1})a + ... vs F(a), d=2")
F0, F1, F2, a = 1, 2, 3, 5
print("printed:", ((F2 * a) * a + F1) * a + F0, " true F(a):", F2 * a * a + F1 * a + F0)

hdr("Toom-Cook exponent log_{k+1}(2k+1) (p.45)")
for k in [1, 2, 3]: print(k, round(math.log(2 * k + 1, k + 1), 4))

hdr("Simultaneous inversion multiplication count 3(m-1)")
def siminv(a, n):
    c = [a[0]]; mults = 0
    for x in a[1:]: c.append(c[-1] * x % n); mults += 1
    u = pow(c[-1], -1, n); out = [0] * len(a)
    for i in range(len(a) - 1, 0, -1):
        out[i] = u * c[i - 1] % n; u = u * a[i] % n; mults += 2
    out[0] = u
    return out, mults
o, mu = siminv([3, 5, 7, 11, 13], 10007)
print(o == [pow(x, -1, 10007) for x in [3, 5, 7, 11, 13]], mu, "== 3(m-1) =", 12)
