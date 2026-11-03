"""Lemma 2.3.5 (Dujella) and Theorem 2.3.6 (Pell) brute force; Lemma 2.1.20 n<=0 edge."""
import math
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 80
def hdr(s): print("\n=== " + s)

def cf_convergents(alpha, nterms):
    a = []; x = alpha
    for _ in range(nterms):
        ai = int(x // 1); a.append(ai); fr = x - ai
        if fr == 0: break
        x = 1 / fr
    h = [1, a[0]]; k = [0, 1]   # h_{-1}, h_0
    for ai in a[1:]:
        h.append(ai * h[-1] + h[-2]); k.append(ai * k[-1] + k[-2])
    return h, k  # index i <-> n=i-1

hdr("Lemma 2.3.5: |alpha - t/s| < c/s^2  =>  (t,s)=(u h_{n+1} +- v h_n, u k_{n+1} +- v k_n), n,u,v>=0, uv<2c")
alphas = {"sqrt2": Decimal(2).sqrt(), "phi": (1 + Decimal(5).sqrt()) / 2, "e": Decimal(1).exp(),
          "pi": Decimal("3.14159265358979323846264338327950288419716939937510582097494459"),
          "355/113": Decimal(355) / Decimal(113), "7/3": Decimal(7) / Decimal(3)}
for name, al in alphas.items():
    h, k = cf_convergents(al, 40)
    for c in [Decimal("0.5"), Decimal(1), Decimal(2), Decimal(3)]:
        fails = []; tested = 0; usedneg1 = 0
        S = 600
        for s in range(1, S + 1):
            lo = int((al - c / (s * s)) * s) - 1
            for t in range(max(lo, 1), lo + 2 * int(c) + 4):
                if abs(al - Decimal(t) / s) >= c / (s * s): continue
                tested += 1
                found = False; found_neg1 = False
                for i in range(len(h) - 1):     # n = i-1 >= -1; pair (n, n+1)
                    for sg in (1, -1):
                        hn1, hn, kn1, kn = h[i + 1], h[i], k[i + 1], k[i]
                        # solve t = u hn1 + sg v hn, s = u kn1 + sg v kn
                        det = hn1 * kn - hn * kn1
                        if det == 0: continue
                        u = Fraction(t * kn - s * hn, det); v = Fraction(sg * (s * hn1 - t * kn1), det)
                        if u.denominator == 1 and v.denominator == 1 and u >= 0 and v >= 0 and u * v < 2 * Fraction(str(c)):
                            if i >= 1: found = True
                            else: found_neg1 = True
                if not found:
                    if found_neg1: usedneg1 += 1
                    else: fails.append((t, s))
        print(f"{name} c={c}: tested {tested}, failures(n>=0) {len(fails)} {fails[:3]}; needed n=-1: {usedneg1}")

hdr("Theorem 2.3.6 Pell: all positive solutions with y<=3000 arise as (h_{nr-1},k_{nr-1}); d squarefree<=60")
def squarefree(d): return all(d % (p * p) for p in range(2, int(d ** 0.5) + 1))
bad = []
for d in range(2, 61):
    if not squarefree(d): continue
    r0 = math.isqrt(d)
    if r0 * r0 == d: continue
    # periodic CF of sqrt d
    m, dd, a = 0, 1, r0; a0 = a; period = [];
    while True:
        m = dd * a - m; dd = (d - m * m) // dd; a = (a0 + m) // dd; period.append(a)
        if a == 2 * a0: break
    r = len(period)
    h = [1, a0]; k = [0, 1]
    idx = 0
    while k[-1] < 10 ** 7:
        ai = period[idx % r]; idx += 1
        h.append(ai * h[-1] + h[-2]); k.append(ai * k[-1] + k[-2])
    conv = {(h[i + 1], k[i + 1]): i for i in range(len(h) - 1)}   # key -> n index
    for n in range(1, 6):
        i = n * r - 1
        if i + 1 < len(h) and h[i + 1] ** 2 - d * k[i + 1] ** 2 != (-1) ** (n * r): bad.append(("identity", d, n))
    for y in range(1, 3001):
        for sgn in (1, -1):
            x2 = d * y * y + sgn
            x = math.isqrt(x2)
            if x * x == x2:
                n_ok = any((x, y) == (h[n * r - 1 + 1], k[n * r - 1 + 1]) for n in range(1, 40) if n * r < len(h))
                if not n_ok: bad.append(("missing", d, x, y))
print("failures:", bad[:5], len(bad))
print("d=1 is square-free: sqrt(1)=1 has CF [1] (no period); x^2-y^2=+-1 has solutions (+-1,0),(0,+-1) only")
print("trivial solution (1,0) and negative solutions only arise 'up to sign' / with n=0 (h_{-1},k_{-1})=(1,0)")

hdr("Lemma 2.1.20: n = ceil(log(1/eps')/eps) for eps' >= 1")
for e1, e2 in [(0.5, 1.0), (0.5, 2.0), (0.1, 1e-6)]:
    print(f"eps={e1} eps'={e2}: n={math.ceil(math.log(1 / e2) / e1)}")
