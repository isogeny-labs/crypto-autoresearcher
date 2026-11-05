"""Shared utilities for SA-16: curves, S_3, planting of control families, verification."""
import random, math, time
import sympy as sp
import cypari2
pari = cypari2.Pari()
pari.allocatemem(200 * 10**6, silent=True)


def nextprime_34(bits, rng):
    """random-ish prime ~2^bits with p = 3 mod 4 (fast sqrt)."""
    p = sp.nextprime(2**bits + rng.randrange(2**(bits - 2)))
    while p % 4 != 3:
        p = sp.nextprime(p)
    return int(p)


def sqrt_mod(n, p):
    n %= p
    if n == 0:
        return 0
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
        return r if r * r % p == n else None
    r = sp.sqrt_mod(n, p)
    return None if r is None else int(r)


def is_qr(n, p):
    n %= p
    return n == 0 or pow(n, (p - 1) // 2, p) == 1


def f_of(x, a, b, p):
    return (x * x * x + a * x + b) % p


def point(x, a, b, p, sign=1):
    y = sqrt_mod(f_of(x, a, b, p), p)
    if y is None:
        return None
    return (x % p, (sign * y) % p)


def add(P, Q, a, p):
    """affine addition, None = infinity."""
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def mul(k, P, a, p):
    R = None
    Q = P
    while k:
        if k & 1: R = add(R, Q, a, p)
        Q = add(Q, Q, a, p)
        k >>= 1
    return R


def S3_coeffs_in_X(x1, x2, a, b):
    """S_3(x1,x2,X) = c2 X^2 + c1 X + c0 over Z."""
    c2 = (x1 - x2) ** 2
    c1 = -2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
    c0 = (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)
    return c0, c1, c2


def S3_eval(x1, x2, X, a, b):
    c0, c1, c2 = S3_coeffs_in_X(x1, x2, a, b)
    return c0 + c1 * X + c2 * X * X


def S3_bivariate(X, a, b, p):
    """S_3(x1,x2,X) mod p as dict {(i,j): coeff} in x1^i x2^j."""
    d = {(2, 0): X * X, (0, 2): X * X, (1, 1): -2 * X * X - 2 * a,
         (2, 1): -2 * X, (1, 2): -2 * X, (1, 0): -2 * a * X - 4 * b, (0, 1): -2 * a * X - 4 * b,
         (0, 0): -4 * b * X + a * a, (2, 2): 1}
    return {k: v % p for k, v in d.items()}


def verify_decomp(x1, x2, xr, a, b, p, B=None):
    """True iff x1,x2 in [1,B] (if B), both are x-coords of F_p-points, and some signs give
    x(+-P1 +- P2) == xr (group-law check, not just S_3 vanishing)."""
    if x1 < 1 or x2 < 1: return False
    if B is not None and (x1 > B or x2 > B): return False
    P1 = point(x1, a, b, p); P2 = point(x2, a, b, p)
    if P1 is None or P2 is None: return False
    for Q2 in (P2, neg(P2, p)):
        S = add(P1, Q2, a, p)
        if S is not None and S[0] == xr % p:
            return True
        if S is None and False:
            pass
    return False


def int_cubic_roots(A, C):
    """integer roots of e^3 + A e + C = 0 (A, C Python ints, possibly huge)."""
    import numpy as np
    roots = set()
    cand = []
    try:
        rr = np.roots([1.0, 0.0, float(A), float(C)])
        for r in rr:
            if abs(r.imag) < 1e-6 * max(1.0, abs(r.real)):
                cand.append(int(round(r.real)))
    except Exception:
        pass
    for c in cand:
        for d in range(-3, 4):
            e = c + d
            if e ** 3 + A * e + C == 0:
                roots.add(e)
    return roots


def isqrt_exact(n):
    if n < 0: return None
    r = math.isqrt(n)
    return r if r * r == n else None


def recover_from_form(c0, c1, c2, a, b):
    """given integer (c0,c1,c2) == coefficients of S_3(x1,x2,T), recover candidate (x1,x2) list."""
    out = []
    for s in (1, -1):
        C0, C1, C2 = s * c0, s * c1, s * c2
        d = isqrt_exact(C2)
        if d is None: continue
        for e1 in int_cubic_roots(4 * a - C2, 8 * b + 2 * C1):
            if e1 <= 0: continue
            num = e1 * e1 - C2
            if num % 4: continue
            e2 = num // 4
            if (e1 + d) % 2: continue
            x1 = (e1 + d) // 2; x2 = (e1 - d) // 2
            if x2 >= 1 and x1 * x2 == e2 and S3_coeffs_in_X(x1, x2, a, b) == (C0, C1, C2):
                out.append((x1, x2))
    return out


def plant_small_curve(p, B, a=0, b=7, rng=random, diag=False, tries=100000):
    """R = P1+P2 with x1,x2 uniform in [1,B] on y^2=x^3+ax+b. diag => P2=P1 (R=[2]P1)."""
    for _ in range(tries):
        x1 = rng.randrange(1, B + 1)
        x2 = x1 if diag else rng.randrange(1, B + 1)
        if not diag and x1 == x2: continue
        P1 = point(x1, a, b, p); P2 = point(x2, a, b, p, sign=rng.choice((1, -1)))
        if P1 is None or P2 is None: continue
        R = add(P1, P2, a, p)
        if R is None: continue
        return dict(p=p, a=a, b=b, B=B, x1=x1, x2=x2, xr=R[0])
    raise RuntimeError('plant failed')


def plant_degenerate_conic(p, B, rng=random, tries=100000):
    """Control (i): R=(xr,0) a rational 2-torsion point, R=P1+P2 with x1,x2<=B small.
    Construction: pick small x1,x2 and random xr, set a = x1 x2 - xr(x1+x2) - 2 xr^2, b = -xr^3 - a xr, so that
    f(xr)=0 and (x1-xr)(x2-xr)=f'(xr) (equivalent to S_3(x1,x2,xr)=0 when f(xr)=0). a,b are ~p (not small)."""
    for _ in range(tries):
        x1 = rng.randrange(1, B + 1); x2 = rng.randrange(1, B + 1)
        if x1 == x2: continue
        xr = rng.randrange(2, p)
        a = (x1 * x2 - xr * (x1 + x2) - 2 * xr * xr) % p
        b = (-xr ** 3 - a * xr) % p
        if 4 * a ** 3 % p == (-27 * b * b) % p: continue
        if verify_decomp(x1, x2, xr, a, b, p) and f_of(xr, a, b, p) == 0:
            return dict(p=p, a=a, b=b, B=B, x1=x1, x2=x2, xr=xr)
    raise RuntimeError('plant failed')


def plant_generic_largecoeff(p, B, rng=random, tries=100000):
    """Null for (i): random curve with ~p-size a,b, random small x1!=x2, R=P1+P2 (generic fibre)."""
    for _ in range(tries):
        a = rng.randrange(p); b = rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0: continue
        x1 = rng.randrange(1, B + 1); x2 = rng.randrange(1, B + 1)
        if x1 == x2: continue
        P1 = point(x1, a, b, p); P2 = point(x2, a, b, p)
        if P1 is None or P2 is None: continue
        R = add(P1, P2, a, p)
        if R is None or R[1] == 0: continue
        return dict(p=p, a=a, b=b, B=B, x1=x1, x2=x2, xr=R[0])
    raise RuntimeError('plant failed')


def boot_ci(vals_by_cell, stat, nboot=2000, rng=None):
    rng = rng or random.Random(1)
    res = []
    for _ in range(nboot):
        samp = [[rng.choice(c) for _ in c] for c in vals_by_cell]
        res.append(stat(samp))
    res.sort()
    return res[int(0.025 * nboot)], res[int(0.975 * nboot)]
