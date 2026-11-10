#!/usr/bin/env python3
"""Size-matched conditional null for the split-prime deficit.

Ten published curves, their actual field primes fixed. For each replicate draw a
trace t uniform in the Hasse interval with n = p+1-t prime, compute the split
count over the published cutoffs, and pool the ten curves with the study's
conditioned model. Reports the null distribution of z_691 and of the
max-over-cutoffs statistic.

    python3 split_null_curvewise.py --reps 10000 --procs 8
"""
import argparse
import hashlib
import math
import random
from multiprocessing import Pool

# published field primes, in the study's table order
P = [
    6277101735386680763835789423207666416083908700390324961279,   # prime192v1
    6277101735386680763835789423207666416083908700390324961279,   # prime192v2
    6277101735386680763835789423207666416083908700390324961279,   # prime192v3
    26959946667150639794667015087019630673557916260026308143510066298881,  # P-224
    883423532389192164791648750360308885314476597252960362792450860609699839,  # prime239v1
    883423532389192164791648750360308885314476597252960362792450860609699839,  # prime239v2
    883423532389192164791648750360308885314476597252960362792450860609699839,  # prime239v3
    115792089210356248762697446949407573530086143415290314195533631308867097853951,  # P-256
    39402006196394479212279040100143613805079739270465446667948293404245721771496870329047266088258938001861606973112319,  # P-384
    6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151,  # P-521
]
CUTOFFS = (100, 200, 500, 691, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000)
OBS_COUNTS_691 = (60, 58, 57, 50, 42, 57, 57, 57, 54, 52)
OBS_Z = (2.71, 1.81, 2.98, 3.13, 1.98, 2.16, 2.45, 2.12, 2.26, 2.00, 1.87, 1.79)
I691 = CUTOFFS.index(691)
OBS_691 = OBS_Z[I691]
OBS_MAX = max(OBS_Z)
MR_ROUNDS = 16
SEED = b"split-curvewise-null/v1"


def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, math.isqrt(n) + 1):
        if s[i]:
            s[i * i::i] = bytes(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if s[i]]


ALL = primes_upto(CUTOFFS[-1])
ODD = ALL[1:]
SEGS, lo = [], 0
for B in CUTOFFS:
    SEGS.append([(l, (l - 1) // 2) for l in ODD if lo < l <= B])
    lo = B
PRIMORIAL = math.prod(q for q in ALL if q < 2000)


def legendre(a, l):
    e = pow(a, (l - 1) // 2, l)
    if e == 1:
        return 1
    if e == l - 1:
        return -1
    if e == 0:
        return 0
    raise ArithmeticError("Euler criterion")


def model_prob(l, p):
    r = p % l
    if r == 1:
        m = (l - 3) // 2
        return m * (l + 1), l * l - l - 1
    m = (l - 4 - legendre(r, l)) // 2
    return m, l - 2


def model_tables(p):
    E, V = [], []
    e = v = 0.0
    for seg in SEGS:
        for l, _ in seg:
            a, b = model_prob(l, p)
            e += a / b
            v += a * (b - a) / (b * b)
        E.append(e)
        V.append(v)
    return E, V


def is_prime(n, rng):
    if n < 2 or n & 1 == 0:
        return False
    if math.gcd(n, PRIMORIAL) != 1:
        return False
    d, s = n - 1, 0
    while d & 1 == 0:
        d >>= 1
        s += 1
    for _ in range(MR_ROUNDS):
        a = rng.randrange(2, n - 1)
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


def split_counts(t, p):
    D = t * t - 4 * p
    out, cum = [], 0
    for seg in SEGS:
        for l, h in seg:
            a = D % l
            if a:
                e = pow(a, h, l)
                if e == 1:
                    cum += 1
        out.append(cum)
    return out


def replicate(rep):
    rng = random.Random(int.from_bytes(hashlib.sha256(SEED + b"|" + str(rep).encode()).digest()[:16], "big"))
    S = [0] * len(CUTOFFS)
    for p in P:
        T = math.isqrt(4 * p)
        while True:
            t = rng.randint(-T, T)
            if (p + 1 - t) & 1 == 0:
                continue
            if is_prime(p + 1 - t, rng):
                break
        c = split_counts(t, p)
        S = [a + b for a, b in zip(S, c)]
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10000)
    ap.add_argument("--procs", type=int, default=8)
    a = ap.parse_args()
    print("PRE-REGISTRATION: primary z_691 <= -3.13; secondary max_B -z_B >= 3.13;")
    print("ten published p fixed; t uniform in the Hasse interval with n prime; 16 MR rounds;")
    print("model: GL2 conditioned baseline of the study. reps =", a.reps, "seed =", SEED.decode())
    E = [0.0] * len(CUTOFFS)
    V = [0.0] * len(CUTOFFS)
    for p in P:
        e, v = model_tables(p)
        E = [x + y for x, y in zip(E, e)]
        V = [x + y for x, y in zip(V, v)]
    # sanity: simulated observed pooled z from the study's counts at 691
    obs_s = sum(OBS_COUNTS_691)
    print(f"observed at 691: S={obs_s}, E={E[I691]:.1f}, sd={math.sqrt(V[I691]):.2f}, "
          f"z={(obs_s - E[I691]) / math.sqrt(V[I691]):.2f} (study -3.13)")
    hits1 = hits2 = hits3 = 0
    zmeans = 0.0
    with Pool(a.procs) as pool:
        for i, S in enumerate(pool.imap_unordered(replicate, range(a.reps), chunksize=8), 1):
            z = [(S[b] - E[b]) / math.sqrt(V[b]) for b in range(len(CUTOFFS))]
            zmeans += z[I691]
            if z[I691] <= -OBS_691:
                hits1 += 1
            if max(-x for x in z) >= OBS_MAX:
                hits2 += 1
            if z[I691] <= -OBS_691 and max(-x for x in z) >= OBS_MAX:
                hits3 += 1
            if i % 500 == 0:
                print(f"  {i}/{a.reps}", flush=True)
    n = a.reps
    print(f"\nnull mean z_691 = {zmeans / n:.3f}")
    print(f"P(z_691 <= -{OBS_691}) = {hits1}/{n} = {hits1 / n:.5f}")
    print(f"P(max_B -z_B >= {OBS_MAX}) = {hits2}/{n} = {hits2 / n:.5f}")
    print(f"P(both) = {hits3}/{n} = {hits3 / n:.5f}")


if __name__ == "__main__":
    main()
