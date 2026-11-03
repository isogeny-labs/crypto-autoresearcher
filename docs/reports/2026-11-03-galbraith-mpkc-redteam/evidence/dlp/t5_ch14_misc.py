"""Ch14 misc: Example 14.2.6 replay; proof of Theorem p292-1 assumes b_{i+lh}-b_i constant on the cycle
(true for the additive walk, false for the original squaring walk); Example 14.9.3; Theorem 14.7.5 constant
by exact lattice sum; Certicom ratios (14.4.3); Kuhn-Struik sqrt(2kN) vs Poisson-limit sqrt(2N)Gamma(k+1/2)/Gamma(k);
Example 14.4.8 constant."""
import math, random
import numpy as np

print('== Example 14.2.6 replay ==')
p, r, g, h = 809, 101, 89, 799
gs = {1: (37, 34), 2: (71, 69), 3: (76, 18)}
G = {j: pow(g, u, p) * pow(h, v, p) % p for j, (u, v) in gs.items()}
print('g_j =', G)
x, a, b = g, 1, 0; seq = []
for i in range(1, 14):
    seq.append((x, a, b, x % 4))
    s = x % 4
    if s == 0: x, a, b = x * x % p, 2 * a % r, 2 * b % r
    else: x, a, b = x * G[s] % p, (a + gs[s][0]) % r, (b + gs[s][1]) % r
for i, t in enumerate(seq[:7], 1): print(i, t)
xs = [t[0] for t in seq]
first = next(j for j in range(len(xs)) if xs[j] in xs[:j]); lt = xs.index(xs[first]) + 1; lh = first + 1 - lt
ep = next(i for i in range(1, 7) if xs[2 * i - 1] == xs[i - 1])
x1, a1, b1 = seq[ep - 1][:3]; x2, a2, b2 = seq[2 * ep - 1][:3]
lg = (a2 - a1) * pow(b1 - b2, -1, r) % r
print(f'lt={lt} lh={lh} epact={ep}; DLP={lg}; check {pow(g, lg, p) == h}')

print('\n== proof of Thm p292-1: is b_{i+lh} - b_i constant along the cycle? ==')
random.seed(1)
def run(walk_type, p=2027, r=1013, trials=200, nS=4):
    # subgroup of order r=1013 in F_2027^*
    g = pow(2, (p - 1) // r, p); h = pow(g, 123, p); nonconst = 0; n = 0
    for _ in range(trials):
        uv = [(random.randrange(r), random.randrange(r)) for _ in range(nS)]
        Gj = [pow(g, u, p) * pow(h, v, p) % p for u, v in uv]
        salt = random.randrange(1 << 30)
        S = lambda x: hash((x, salt)) % nS
        x, a, b = g, 1, 0; pos = {}; hist = []
        while x not in pos:
            pos[x] = len(hist); hist.append((x, a, b))
            s = S(x)
            if walk_type == 'orig' and s == 0: x, a, b = x * x % p, 2 * a % r, 2 * b % r
            else: x, a, b = x * Gj[s] % p, (a + uv[s][0]) % r, (b + uv[s][1]) % r
        lt = pos[x]; lh = len(hist) - lt
        if lh < 2: continue
        # extend one more lap to compare b_{i+lh} - b_i for each i on the cycle
        ext = list(hist) + [(x, a, b)]
        for _ in range(lh):
            s = S(x)
            if walk_type == 'orig' and s == 0: x, a, b = x * x % p, 2 * a % r, 2 * b % r
            else: x, a, b = x * Gj[s] % p, (a + uv[s][0]) % r, (b + uv[s][1]) % r
            ext.append((x, a, b))
        diffs = {(ext[i + lh][2] - ext[i][2]) % r for i in range(lt, lt + lh)}
        n += 1; nonconst += len(diffs) > 1
    return nonconst, n
for wt in ('additive', 'orig'):
    nc, n = run(wt)
    print(f'{wt:8s} walk: cycles where b_(i+lh)-b_i is NOT constant along the cycle: {nc}/{n}')

print('\n== Example 14.9.3 ==')
N = 144493; f = lambda x: (x * x + 1) % N
xs = [2]
for _ in range(20): xs.append(f(xs[-1]))
print('N =', N, '=', 131, '*', N // 131, '; x_i mod 131:', [x % 131 for x in xs[:12]], '; gcd(x14-x7,N)=', math.gcd(xs[13] - xs[6], N))

print('\n== Theorem 14.7.5 constant: exact lattice sum (#T/#A)*sqrt(pi #A) averaged over all (a1,a2) ==')
for N in (100, 400, 1600):
    tot = 0.0
    xs_ = np.arange(N)
    for a1 in range(N):
        ov1 = np.clip(np.minimum(N, a1 + N // 2) - np.maximum(0, a1 - N // 2), 0, None)
        ov2 = np.clip(np.minimum(N, xs_ + N // 2) - np.maximum(0, xs_ - N // 2), 0, None)
        A = ov1 * ov2
        tot += np.sum(N * N / A * np.sqrt(np.pi * A))
    print(f'N={N}: average/N = {tot / N**2 / N:.5f}  (claim sqrt(pi)(2(2-sqrt2))^2 = {math.sqrt(math.pi)*(2*(2-math.sqrt(2)))**2:.5f})')

print('\n== 14.4.3 Certicom ratios ==')
r = 1.5 * 2 ** 108; print('ECCp-109 2002: found/expected =', 68228567 / (2 ** -29 * math.sqrt(math.pi * r / 2)))
print('ECC2-109 2004: found/expected =', 16531676 / (2 ** -30 * math.sqrt(math.pi * 2 ** 108 / 2)))
p112 = (2 ** 128 - 3) / 76439; print('BKM p ~ 2^%.3f ; 8.5e16/sqrt(pi p/2)=%.3f ; ops*2^-24=%.3g' % (math.log2(p112), 8.5e16 / math.sqrt(math.pi * p112 / 2), 8.5e16 * 2 ** -24))

print('\n== Kuhn-Struik: E[samples to k collisions] ~ sqrt(2kN) (book) vs sqrt(2N)Gamma(k+1/2)/Gamma(k) ==')
for k in (1, 2, 3, 5, 10, 50):
    exact = math.sqrt(2) * math.exp(math.lgamma(k + 0.5) - math.lgamma(k))
    print(f'k={k:2d}: Poisson-limit/sqrtN={exact:.4f}  book sqrt(2k)={math.sqrt(2*k):.4f}  ratio book/limit={math.sqrt(2*k)/exact:.4f}')
rng = np.random.default_rng(42); Nn = 10 ** 5; T = 4000
for k in (2, 3):
    vals = []
    for _ in range(T):
        seen = set(); c = 0; n = 0
        while c < k:
            v = int(rng.integers(Nn)); n += 1
            if v in seen: c += 1
            else: seen.add(v)
        vals.append(n / math.sqrt(Nn))
    v = np.array(vals); print(f'MC N=1e5 k={k}: {v.mean():.4f} +- {1.96*v.std(ddof=1)/math.sqrt(T):.4f}')

print('\n== Example 14.4.8: sqrt(pi 2^m/(4m)) vs sqrt(pi r/(4m)), #E = h r ==')
for hcof in (2, 4): print(f'h={hcof}: book/correct = sqrt(2^m/r) = sqrt(h) = {math.sqrt(hcof):.4f}')
