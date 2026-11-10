#!/usr/bin/env python3
"""split_null.py -- null calibration of the pooled split-prime deficit statistic."""

PREREG = """\
PRE-REGISTRATION (frozen; this text and the source file are hashed before any sampling)
Claim under test: the pooled split-prime deficit of ten published prime-order curves
  (pooled z = -3.13 at B = 691; z in [-3.13, -1.79] at all 12 cutoffs) is exceptional.
  Not Galbraith-McKee Conjecture A; nothing about the density of prime-order curves.
Statistic: for a set of K = 10 curves, S_B = number of (curve, odd prime l <= B) with
  (Delta/l) = +1, Delta = t^2 - 4p; z_B = (S_B - sum E)/sqrt(sum Var) under the study's
  model: Frobenius mod l uniform on GL2(F_l) matrices of determinant p, trace class
  tau = p+1 removed, remainder renormalised.
P   primary  : z_691                      observed -3.13   tail P(z_691 <= -3.13)
S1  secondary: max over cutoffs of -z_B   observed  3.13   tail P(S1 >= 3.13)
S2  secondary: max over cutoffs of  z_B   observed -1.79   tail P(S2 <= -1.79)
Cutoffs (as published): 100 200 500 691 1000 2000 5000 10000 20000 50000 100000 200000.
Null: p fixed per size to the standard field prime (P-192, P-224, P-256). t uniform on
  the integers [-T, T], T = isqrt(4p), by bit-rejection. n = p + 1 - t. Accept iff
  gcd(n, product of primes < 2000) = 1 and n passes 40 Miller-Rabin rounds with bases
  from a separate deterministic stream; otherwise redraw t. No other screening.
Replicate: 10 accepted curves on one field; 10,000 replicates per size.
Seeds: SHA-256 counter streams keyed by (SEED, size, replicate, curve index).
Gate: model E and sd at B = 691 must print 59.7/5.51 (192), 60.1/5.53 (224),
  60.2/5.54 (256), the brief's values; otherwise abort before sampling.
Tails: exact counts k/N per size and pooled (N = 30,000); 95% Clopper-Pearson intervals.
Decision: p_adj = 3 x pooled tail of S1 (3 = min-of-three families). EXCEPTIONAL if the
  upper 95% limit of p_adj < 0.01; NOT EXCEPTIONAL if the lower limit > 0.01; otherwise
  UNRESOLVED at this N.
Declared in advance: under a t-uniform null the model mean is too high (the model
  weights trace classes by matrix count), so E[z] < 0 under the null. z is not
  recentred; predicted and empirical null means are printed.
"""

import argparse, hashlib, json, math, sys
from multiprocessing import Pool

# ---------------- registered constants ----------------
CUTOFFS = (100, 200, 500, 691, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000)
OBS_H = (271, 181, 298, 313, 198, 216, 245, 212, 226, 200, 187, 179)  # -z x 100 (brief)
I691 = CUTOFFS.index(691)
C_MAX, C_WEAK = max(OBS_H), min(OBS_H)          # 313 and 179
assert OBS_H[I691] == C_MAX == 313 and C_WEAK == 179
K, REPS, MR_ROUNDS, FAMILIES, ALPHA = 10, 10_000, 40, 3, 0.01
SEED = b"split-deficit-null/prereg-v1"
FIELDS = {192: 2**192 - 2**64 - 1,
          224: 2**224 - 2**96 + 1,
          256: 2**256 - 2**224 + 2**192 + 2**96 - 1}
GATE = {192: ("59.7", "5.51"), 224: ("60.1", "5.53"), 256: ("60.2", "5.54")}


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, math.isqrt(n) + 1):
        if s[i]:
            s[i * i::i] = bytes(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if s[i]]


ALL = primes_upto(CUTOFFS[-1])
ODD = ALL[1:]
SEGS, _lo = [], 0                       # odd primes in (previous cutoff, cutoff]
for _B in CUTOFFS:
    SEGS.append([(l, (l - 1) // 2) for l in ODD if _lo < l <= _B])
    _lo = _B
PRIMORIAL = math.prod(q for q in ALL if q < 2000)


# ---------------- deterministic randomness ----------------
class Stream:
    """SHA-256 in counter mode; platform- and version-independent."""
    def __init__(self, label):
        self.key = hashlib.sha256(SEED + b"|" + label).digest()
        self.ctr = self.buf = self.nbits = 0

    def bits(self, k):
        while self.nbits < k:
            blk = hashlib.sha256(self.key + self.ctr.to_bytes(8, "big")).digest()
            self.ctr += 1
            self.buf = (self.buf << 256) | int.from_bytes(blk, "big")
            self.nbits += 256
        self.nbits -= k
        out = self.buf >> self.nbits
        self.buf &= (1 << self.nbits) - 1
        return out

    def below(self, n):                 # uniform on [0, n), rejection, no modulo bias
        k = (n - 1).bit_length()
        while True:
            r = self.bits(k)
            if r < n:
                return r


def is_probable_prime(n, mr):
    if n & 1 == 0 or math.gcd(n, PRIMORIAL) != 1:   # n > 2^190 here, so gcd > 1 => composite
        return False
    d = n - 1
    s = (d & -d).bit_length() - 1
    d >>= s
    for _ in range(MR_ROUNDS):
        a = 2 + mr.below(n - 3)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------------- exact Legendre symbol and baseline model ----------------
def legendre(a, l):                     # a not divisible by l; Euler's criterion, exact
    e = pow(a, (l - 1) // 2, l)
    if e == 1:
        return 1
    if e == l - 1:
        return -1
    raise ArithmeticError("Euler criterion returned neither 1 nor -1")


def model_prob(l, p):
    """Return (a, b, m): conditioned-model P(split) = a/b exactly;
    m = number of split trace classes other than tau = p+1."""
    r = p % l
    assert r != 0
    if r == 1:                          # removed class tau = 2 is ramified (l^2 matrices)
        m = (l - 3) // 2
        return m * (l + 1), l * l - l - 1, m
    m = (l - 4 - legendre(r, l)) // 2   # removed class is split (l(l+1) matrices)
    return m, l - 2, m


def add(x, y):
    return x[0] * y[1] + y[0] * x[1], x[1] * y[1]


def tree_sum(pairs):                    # exact sum of fractions, unreduced
    pairs = list(pairs)
    if not pairs:
        return 0, 1
    while len(pairs) > 1:
        nxt = [add(pairs[i], pairs[i + 1]) for i in range(0, len(pairs) - 1, 2)]
        if len(pairs) % 2:
            nxt.append(pairs[-1])
        pairs = nxt
    return pairs[0]


def model_tables(p):
    """Per cutoff: exact cumulative mean and variance (num, den) for ONE curve, and the
    float (display-only) excess of the model mean over the t-uniform mean m/(l-1)."""
    E, V, U = [], [], []
    accE, accV, shift = (0, 1), (0, 1), 0.0
    for seg in SEGS:
        pr = [model_prob(l, p) for l, _ in seg]
        accE = add(accE, tree_sum((a, b) for a, b, _ in pr))
        accV = add(accV, tree_sum((a * (b - a), b * b) for a, b, _ in pr))
        shift += math.fsum(a / b - m / (l - 1) for (a, b, m), (l, _) in zip(pr, seg))
        E.append(accE); V.append(accV); U.append(shift)
    return E, V, U


def threshold(E, V, c_h):
    """Largest integer S with (S - K*E)/sqrt(K*V) <= -c_h/100, certified exactly."""
    (Ea, Eb), (Va, Vb) = E, V
    rhs = c_h * c_h * K * Va * Eb * Eb
    scale = Vb * 10000

    def ok(S):
        d = K * Ea - S * Eb
        return d >= 0 and d * d * scale >= rhs

    S = math.floor(K * (Ea / Eb) - (c_h / 100) * math.sqrt(K * (Va / Vb)))  # float guess
    while ok(S + 1):
        S += 1
    while not ok(S):
        S -= 1
    return S


# ---------------- one replicate = K curves on one field ----------------
def replicate(task):
    bits, rep = task
    p = FIELDS[bits]
    T = math.isqrt(4 * p)
    tot = [0] * len(CUTOFFS)
    tried = 0
    for j in range(K):
        st = Stream(b"t/%d/%d/%d" % (bits, rep, j))
        mr = Stream(b"mr/%d/%d/%d" % (bits, rep, j))
        while True:
            t = st.below(2 * T + 1) - T
            tried += 1
            if is_probable_prime(p + 1 - t, mr):
                break
        D = t * t - 4 * p               # exact integer discriminant, negative
        cum = 0
        for i, seg in enumerate(SEGS):
            for l, h in seg:
                a = D % l               # exact residue of the exact integer D
                if a:
                    e = pow(a, h, l)
                    if e == 1:
                        cum += 1
                    elif e != l - 1:
                        raise ArithmeticError("Euler criterion failed")
            tot[i] += cum
    return bits, rep, tot, tried


# ---------------- self-tests (run before sampling) ----------------
def selftest():
    assert sum(map(len, SEGS[:I691 + 1])) == 124 and sum(map(len, SEGS)) == 17983
    for l in ODD[:94]:                  # Euler criterion vs explicit squares, all l < 500
        sq = {x * x % l for x in range(1, l)}
        assert all((legendre(x, l) == 1) == (x in sq) for x in range(1, l))
    for l in (3, 5, 7, 11, 13):         # closed form vs brute-force matrix count
        sq = {x * x % l for x in range(1, l)}
        cnt = {d: [0, 0] for d in range(1, l)}
        for a in range(l):
            for b in range(l):
                for c in range(l):
                    for e in range(l):
                        d, tr = (a * e - b * c) % l, (a + e) % l
                        if d and tr != (d + 1) % l:
                            cnt[d][1] += 1
                            cnt[d][0] += ((tr * tr - 4 * d) % l) in sq
        for d in range(1, l):
            x, y, _ = model_prob(l, d)
            assert cnt[d][0] * y == x * cnt[d][1], (l, d)


# ---------------- interval estimate (floating point; display only) ----------------
def binom_cdf(k, n, p):
    if k < 0:
        return 0.0
    if k >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lp, lq, lg = math.log(p), math.log1p(-p), math.lgamma
    return min(1.0, math.fsum(
        math.exp(lg(n + 1) - lg(i + 1) - lg(n - i + 1) + i * lp + (n - i) * lq)
        for i in range(k + 1)))


def clopper_pearson(k, n, conf=0.95):
    a = (1 - conf) / 2

    def bisect(pred):                   # pred monotone False -> True in p
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if pred(mid):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else bisect(lambda q: 1 - binom_cdf(k - 1, n, q) >= a)
    upper = 1.0 if k == n else bisect(lambda q: binom_cdf(k, n, q) <= a)
    return lower, upper


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--procs", type=int, default=None)
    ap.add_argument("--out", default="null_result.json")
    args = ap.parse_args()
    nc = len(CUTOFFS)

    # ---- everything below up to "SAMPLING" is fixed before any random draw ----
    src_hash = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    pre_hash = hashlib.sha256(PREREG.encode()).hexdigest()
    print(PREREG)
    print("sha256(source) =", src_hash)
    print("sha256(prereg) =", pre_hash)
    if args.reps != REPS:
        print("*** reps differs from the registered 10,000: THIS IS NOT THE REGISTERED RUN ***")
    selftest()
    tab = {}
    for bits, p in FIELDS.items():
        E, V, U = model_tables(p)
        Ef, Vf = E[I691][0] / E[I691][1], V[I691][0] / V[I691][1]
        got = (f"{Ef:.1f}", f"{math.sqrt(Vf):.2f}")
        print(f"gate {bits}: E = {Ef:.4f}, sd = {math.sqrt(Vf):.4f} at B = 691 "
              f"(brief: {GATE[bits][0]}, {GATE[bits][1]})")
        if got != GATE[bits]:
            sys.exit("CALIBRATION GATE FAILED: baseline differs from the study's; "
                     "the source comment of tools/splitcount.rs is needed. Nothing sampled.")
        thr = {c: [threshold(E[i], V[i], c) for i in range(nc)] for c in (C_MAX, C_WEAK)}
        own = [threshold(E[i], V[i], OBS_H[i]) for i in range(nc)]
        tab[bits] = (E, V, U, thr, own)

    # ---- SAMPLING ----
    tasks = [(bits, rep) for bits in FIELDS for rep in range(args.reps)]
    res = {bits: [None] * args.reps for bits in FIELDS}
    tried = dict.fromkeys(FIELDS, 0)
    with Pool(args.procs) as pool:
        for done, (bits, rep, tot, nt) in enumerate(
                pool.imap_unordered(replicate, tasks, chunksize=8), 1):
            res[bits][rep] = tot
            tried[bits] += nt
            if done % 500 == 0:
                print(f"  {done}/{len(tasks)} replicates", file=sys.stderr)

    # ---- ANALYSIS (integer comparisons against certified thresholds) ----
    def line(name, k, n):
        lo, hi = clopper_pearson(k, n)
        print(f"  {name:<30} {k:>6}/{n:<6} = {k / n:.5f}   95% CP [{lo:.5f}, {hi:.5f}]")
        return lo, hi

    out = {"sha256_source": src_hash, "sha256_prereg": pre_hash, "reps": args.reps,
           "registered_run": args.reps == REPS, "sizes": {}}
    pooled = {"P": 0, "S1": 0, "S2": 0, "cut": [0] * nc}
    for bits in FIELDS:
        E, V, U, thr, own = tab[bits]
        R, n = res[bits], args.reps
        kP = sum(r[I691] <= thr[C_MAX][I691] for r in R)
        kS1 = sum(any(r[i] <= thr[C_MAX][i] for i in range(nc)) for r in R)
        kS2 = sum(all(r[i] <= thr[C_WEAK][i] for i in range(nc)) for r in R)
        kcut = [sum(r[i] <= own[i] for r in R) for i in range(nc)]
        Ef, Vf = E[I691][0] / E[I691][1], V[I691][0] / V[I691][1]
        zs = [(r[I691] - K * Ef) / math.sqrt(K * Vf) for r in R]
        mean = math.fsum(zs) / n
        sd = math.sqrt(math.fsum((z - mean) ** 2 for z in zs) / max(n - 1, 1))
        pred = -K * U[I691] / math.sqrt(K * Vf)
        print(f"\nsize {bits}: {K * n} curves from {tried[bits]} draws of t "
              f"(accept {K * n / tried[bits]:.5f}; 1/ln p = {1 / math.log(FIELDS[bits]):.5f})")
        print(f"  null z_691: mean {mean:+.3f} (predicted for t-uniform {pred:+.3f}), sd {sd:.3f}")
        line("P   P(z_691 <= -3.13)", kP, n)
        line("S1  P(max_B -z_B >= 3.13)", kS1, n)
        line("S2  P(max_B z_B <= -1.79)", kS2, n)
        print("  per-cutoff counts of z_B <= observed z_B:", kcut)
        pooled["P"] += kP; pooled["S1"] += kS1; pooled["S2"] += kS2
        pooled["cut"] = [x + y for x, y in zip(pooled["cut"], kcut)]
        out["sizes"][bits] = {"P": kP, "S1": kS1, "S2": kS2, "per_cutoff": kcut,
                              "thr_313": thr[C_MAX], "thr_179": thr[C_WEAK], "thr_own": own,
                              "draws": tried[bits], "null_mean_z691": mean,
                              "null_sd_z691": sd, "pred_mean_z691": pred, "S_totals": R}
    N = len(FIELDS) * args.reps
    print(f"\npooled over sizes (N = {N} replicates)")
    line("P   P(z_691 <= -3.13)", pooled["P"], N)
    lo, hi = line("S1  P(max_B -z_B >= 3.13)", pooled["S1"], N)
    line("S2  P(max_B z_B <= -1.79)", pooled["S2"], N)
    print("  per-cutoff counts of z_B <= observed z_B:", pooled["cut"])
    alo, ahi = min(1.0, FAMILIES * lo), min(1.0, FAMILIES * hi)
    verdict = ("EXCEPTIONAL under this null" if ahi < ALPHA else
               "NOT EXCEPTIONAL under this null" if alo > ALPHA else
               "UNRESOLVED at this N")
    print(f"\np_adj = {FAMILIES} x S1 tail: 95% limits [{alo:.5f}, {ahi:.5f}] vs {ALPHA}: {verdict}")
    out["pooled"] = dict(pooled, N=N, p_adj_limits=[alo, ahi], verdict=verdict)
    with open(args.out, "w") as f:
        json.dump(out, f)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
