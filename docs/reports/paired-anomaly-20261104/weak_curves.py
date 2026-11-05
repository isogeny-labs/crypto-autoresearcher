"""Curve search for the weak-class calibration: anomalous (#E = p), small embedding degree (k = ord_n(p) <= 6),
j = 0 (a = 0, p = 1 mod 3), and ordinary prime-order curves paired by p. Prime order n throughout."""
import numpy as np
def isprime(n): return n > 1 and all(n % d for d in range(2, int(n**.5) + 1))
def leg_table(p):
    t = -np.ones(p, dtype=np.int64); t[0] = 0; t[(np.arange(1, p)**2) % p] = 1; return t
def order(p, a, b, leg):
    X = np.arange(p, dtype=np.int64); return p + 1 + int(leg[(X**3 + a*X + b) % p].sum())
def emb_degree(p, n, kmax=6):
    for k in range(1, kmax + 1):
        if pow(p, k, n) == 1: return k
    return None
def find_curve(p, want, rng, leg, a_fixed=None, tries=200000):
    for _ in range(tries):
        a = a_fixed if a_fixed is not None else int(rng.integers(0, p)); b = int(rng.integers(1, p))
        if (4*a**3 + 27*b*b) % p == 0: continue
        n = order(p, a, b, leg)
        if want(n): return a, b, n
    return None
def primes_in(lo, hi): return [q for q in range(lo, hi) if isprime(q)]
def small_k_targets(p):
    """prime n in the Hasse interval with ord_n(p) <= 6 (n != p)."""
    r = int(2*p**.5) + 1
    return [n for n in range(p + 1 - r, p + 2 + r) if n != p and isprime(n) and emb_degree(p, n)]
