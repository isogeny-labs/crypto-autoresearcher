"""replib.py -- replication engine for G31-001 successor 1 (2026-11-20).

Two INDEPENDENT ordered-m-tuple counting engines:

  (A) PRIMARY: discrete-log / cyclic-convolution engine.
      Enumerate G = <g> as g^0..g^(n-1); a point P = g^k gets index k.
      Ordered m-tuple sums become sums of indices mod n, so the ordered
      count vector is the cyclic m-fold self-convolution of the 0/1
      indicator of the base, done with FFTs:
          m=3:  c = irfft(rfft(a,n)**3, n)
          m=4:  c = irfft(rfft(a,n)**4, n)
      Only valid for cyclic groups of PRIME order (which is what we use:
      cofactor 1 and #E prime => G = E(F_p) is cyclic of prime order).
      Exactness is checked by the |c - round(c)| residual and by (B).

  (B) VERIFICATION ONLY: the pilot's group-law pair-sum table
      (pilot_run.Ctx / InvTable), i.e. affine point additions with a
      modular-inverse table and np.unique/searchsorted accumulation.
      Shares no code path with (A): (A) never touches the group law after
      building the log table.

Curve generation is deterministic from (bits, curve index, attempt) via
sha256.  Acceptance depends ONLY on #E's factorisation (prime order) and on
j-invariant novelty -- never on any decomposition statistic.
"""
from __future__ import annotations

import hashlib
import math
import random

import numpy as np
import sympy
from sympy.ntheory.residue_ntheory import sqrt_mod

from ec import EC

OKEY = 1 << 52          # sentinel for O in the pilot's int64 key space
MASTER = "g31-001-rep-v1"


# --------------------------------------------------------------- rng plumbing
def seed_int(*parts) -> int:
    return int(hashlib.sha256(("|".join(str(p) for p in parts)).encode()).hexdigest(), 16)


def rng_for(*parts) -> random.Random:
    return random.Random(seed_int(*parts))


# ------------------------------------------------------------ exact point order
def point_order(E: EC, P, nmax: int) -> int:
    """Exact order of P (P != O), assuming ord(P) <= nmax.  BSGS."""
    if P is None:
        return 1
    M = math.isqrt(nmax) + 1
    table = {}
    Q = None
    for j in range(M):                     # baby steps j*P, j = 0..M-1
        if Q not in table:
            table[Q] = j
        Q = E.add(Q, P)
    MP = E.mul(M, P)
    R = None
    for i in range(1, M + 2):              # giant steps i*(M*P)
        R = E.add(R, MP)
        j = table.get(R)
        if j is not None:
            m = i * M - j
            if m > 0 and E.mul(m, P) is None:
                return m
    raise RuntimeError("point_order: BSGS failed")


def group_order(E: EC, rng: random.Random) -> tuple[int, str]:
    """Exact #E via Hasse window + lcm of point orders (BSGS).

    ord(P) | #E always; the Hasse window has width 4*sqrt(p) < #E for
    p > 64, so the unique multiple of lcm(ord(P_i)) inside the window is
    #E, provided the lcm exceeds half the window width.
    """
    p = E.p
    h = 2 * math.isqrt(p) + 1
    lo, hi = p + 1 - h, p + 1 + h
    if p < 10000:
        return E.order_naive(), "naive"
    L = 1
    for _ in range(8):
        P = random_point(E, rng)
        o = point_order(E, P, hi)
        L = L * o // math.gcd(L, o)
        if L > 2 * h:
            break
    cands = [k * L for k in range(max(1, lo // L), hi // L + 2) if lo <= k * L <= hi]
    assert len(cands) == 1, ("ambiguous order", cands, lo, hi)
    N = cands[0]
    for _ in range(4):                      # certification: N kills random points
        assert E.mul(N, random_point(E, rng)) is None
    return N, "bsgs"


def random_point(E: EC, rng: random.Random):
    p = E.p
    for _ in range(500):
        x = rng.randrange(p)
        P = E.lift_x(x)
        if P is not None:
            return P
    raise RuntimeError("random_point failed")


# --------------------------------------------------------------- curve search
def j_invariant(E: EC) -> int:
    p, a, b = E.p, E.a, E.b
    num = (1728 * 4 * pow(a, 3, p)) % p
    den = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if den == 0:
        return None                        # j = infinity (never happens here)
    return num * pow(den, -1, p) % p


def curve_bits(bits: int, idx: int) -> dict:
    """Deterministic (p,a,b) attempt for curve slot idx of size class `bits`.
    p is fixed per slot; attempts vary (a,b) only."""
    width = 1 << (bits - 6)
    p0 = (1 << bits) + seed_int(MASTER, bits, idx, "p") % width
    p = int(sympy.nextprime(p0))
    return p


def make_curve(bits: int, idx: int, max_attempts: int = 4000,
               require_prime_order: bool = True) -> dict:
    """Search (a,b) over attempts for a curve with #E = c*n, n prime, c=1."""
    p = curve_bits(bits, idx)
    rng = random.Random(seed_int(MASTER, bits, idx, "curve-rng"))
    for t in range(1, max_attempts + 1):
        a = seed_int(MASTER, bits, idx, t, "a") % p
        b = seed_int(MASTER, bits, idx, t, "b") % p
        if (4 * a * a * a + 27 * b * b) % p == 0:
            continue
        E = EC(p, a, b)
        nE, method = group_order(E, rng)
        if nE < (1 << (bits - 3)):
            continue
        fac = sympy.factorint(nE)
        cof = 1
        n = nE
        if not sympy.isprime(nE):
            if require_prime_order:
                continue
            # fallback: largest prime factor, cofactor <= 4
            primes = sorted(fac)
            n = max(primes)
            cof = nE // n
            if cof > 4 or not sympy.isprime(n):
                continue
        # generator of the order-n subgroup
        g = None
        for k in range(1, 200):
            P = E.mul(cof, random_point(E, rng))
            if P is not None and E.mul(n, P) is None:
                g = P
                break
        if g is None:
            continue
        exact = E.order_naive()
        assert exact == nE, ("point count mismatch", bits, idx, t, exact, nE)
        return dict(bits=bits, idx=idx, attempt=t, p=p, a=a, b=b, nE=nE,
                    cofactor=cof, n=n, g=g, j=j_invariant(E),
                    order_method=method + "+naive-verified", E=E)
    raise RuntimeError(f"no prime-order curve in {max_attempts} attempts for bits={bits} idx={idx}")


# ------------------------------------------------------------- group geometry
def log_table(E: EC, n: int, g) -> dict:
    """point -> k with g^k = point, k = 0..n-1 (requires ord(g) = n)."""
    tab = {}
    Q = None
    for k in range(n):
        if Q not in tab:
            tab[Q] = k
        Q = E.add(Q, g)
    assert Q is None and len(tab) == n, "log table incomplete"
    return tab


def window_points(E: EC, N: int) -> list:
    """{P in E(F_p) : 0 <= x(P) < N} (both y signs)."""
    return [P for P in E.points_x_window(N) if P is not None]


def null_logs(n: int, b: int, kind: str, rng: random.Random) -> list:
    """Logs of a random base of size b.

    kind='uniform'  : b distinct uniform logs.
    kind='symmetric': negation-closed set, i.e. b/2 distinct logs together
                      with their negatives mod n (b must be even -- and
                      |B_G| of an x-window base is provably even, see
                      RESULTS.md).  Uniform over negation-closed b-sets.
    """
    if kind == "uniform":
        ks = set()
        while len(ks) < b:
            ks.add(rng.randrange(1, n))
        return sorted(ks)
    assert kind == "symmetric"
    assert b % 2 == 0, "negation-closed subset of odd-order group is even"
    half = b // 2
    ks = set()
    while len(ks) < half:
        k = rng.randrange(1, n)
        if k == n - k:           # k = n/2 impossible (n odd), kept as guard
            continue
        ks.add(k)
    return sorted(ks | {(-k) % n for k in ks})


# ------------------------------------------------------------------- counting
def counts(logs, n: int, m: int, a=None) -> tuple[np.ndarray, float]:
    """Ordered m-tuple count vector over Z/n (cyclic convolution)."""
    if a is None:
        a = np.zeros(n, dtype=np.float64)
        a[np.asarray(logs, dtype=np.int64)] = 1.0
    A = np.fft.rfft(a, n)
    if m == 2:
        R = np.fft.irfft(A ** 2, n)
    elif m == 3:
        R = np.fft.irfft(A ** 3, n)
    elif m == 4:
        R = np.fft.irfft((A ** 2) ** 2, n)
    else:
        raise ValueError(m)
    resid = float(np.max(np.abs(R - np.rint(R))))
    return np.rint(R).astype(np.int64), resid


def indicator(logs, n: int) -> np.ndarray:
    a = np.zeros(n, dtype=np.float64)
    a[np.asarray(logs, dtype=np.int64)] = 1.0
    return a


def evaluate(cvec: np.ndarray, tlogs) -> dict:
    v = cvec[np.asarray(tlogs, dtype=np.int64)]
    return dict(dec=int(np.count_nonzero(v)), nT=int(len(tlogs)),
                r_tot=int(v.sum()), frac=float(np.count_nonzero(v) / len(tlogs)),
                mean_r=float(v.mean()), r_max=int(v.max()))


def sumset_size(logs, n: int) -> int:
    """|B+B| (distinct unordered pair sums incl. repetitions)."""
    c, _ = counts(logs, n, 2)
    return int(np.count_nonzero(c))


# ------------------------------------------------------------------- metadata
def cm_info(p: int, nE: int) -> dict:
    """disc(t^2 - 4p) = D_K * f^2 with D_K the fundamental discriminant.
    Every curve over F_p has CM by an order in Q(sqrt(t^2-4p)); what varies
    is |D_K|.  |D_K| small <=> near-CM-special (j = 0, 1728 territory).
    Non-supersingularity is guaranteed here because #E is prime (t != 0)."""
    t = p + 1 - nE
    F = 4 * p - t * t
    assert F > 0, "supersingular (t^2 = 4p)"
    u, s = F, 1
    q = 2
    while q * q <= u:
        while u % (q * q) == 0:
            u //= q * q
            s *= q
        q += 1 if q == 2 else 2
    assert u * s * s == F
    D = -u if u % 4 == 3 else -4 * u
    return dict(t=int(t), four_p_minus_t2=int(F), squarefree_part=int(u),
                conductor=int(s), D=int(D), absD=int(-D),
                is_special=bool(-D in (3, 4)))
