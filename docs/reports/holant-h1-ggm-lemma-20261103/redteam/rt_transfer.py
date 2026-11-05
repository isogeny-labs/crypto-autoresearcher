"""Red-team re-derivation of the transfer-matrix claim. Independent of the producer's code:
M is built from S_3 over the full F_p alphabet; the Cayley quotient B is built from the group
law on orbits {O},{+-P} (no discrete logs). Checks:
  E1  M restricted to X(E) == B with the O orbit deleted (entrywise, integers)
  E2  O coupling in D^{1/2} B D^{-1/2} is sqrt2 * 1_FB
  E3  bordered matrix spectrum == spectrum of B (all even-character eigenvalues, any abelian group)
  E4  Cauchy interlacing of spec(M_E) inside spec(B)
  E5  exact residual identity  M c - lam c = -f(O) 1_FB  for every eigenvector f of B (cyclic odd n)
  E6  twist-side / mixed FB: block structure of M over F_p
Usage: python3 rt_transfer.py   (toy primes only, seconds)"""
import numpy as np, json, sys

def legendre(v, p):
    v %= p
    if v == 0: return 0
    return 1 if pow(v, (p - 1) // 2, p) == 1 else -1

def points(p, a, b):
    sq = {}
    for y in range(p): sq.setdefault(y * y % p, []).append(y)
    P = [None]
    for x in range(p):
        for y in sq.get((x ** 3 + a * x + b) % p, []): P.append((x, y))
    return P

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    if P == Q: l = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else: l = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x = (l * l - P[0] - Q[0]) % p
    return (x, (l * (P[0] - x) - P[1]) % p)

def neg(P, p): return None if P is None else (P[0], (-P[1]) % p)

def S3(x1, x2, x3, p, a, b):
    return ((x1 - x2) ** 2 * x3 * x3 - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + (x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p

def full_M(p, a, b, FB):
    """M[y,z] = #{x in FB : S3(x,y,z)=0} over the full alphabet F_p (vectorised)."""
    Y = np.arange(p, dtype=np.int64)[:, None]; Z = np.arange(p, dtype=np.int64)[None, :]
    M = np.zeros((p, p), dtype=np.int64)
    for x in FB:
        d = (x - Y) % p
        t1 = (d * d % p) * (Z * Z % p) % p
        t2 = 2 * (((x + Y) % p) * ((x * Y + a) % p) % p + 2 * b) % p * Z % p
        t3 = ((x * Y - a) % p) ** 2 % p
        t4 = 4 * b * ((x + Y) % p) % p
        M += ((t1 - t2 + t3 - t4) % p == 0)
    return M

def cayley_quotient(E, FBset, p, a):
    """B[o,o'] = #{s in S : P_o + s in o'} on orbits {O},{+-P}; S = {+-F : x(F) in FBset}."""
    xs = sorted({P[0] for P in E[1:]})
    idx = {None: 0}
    for i, x in enumerate(xs): idx[x] = i + 1
    rep = {x: P for P in E[1:] for x in [P[0]]}
    S = [P for P in E[1:] if P[0] in FBset]          # both +-F listed (one if 2-torsion)
    size = np.array([1] + [2 if rep[x][1] != 0 else 1 for x in xs], float)
    k = len(xs) + 1
    B = np.zeros((k, k))
    reps = [None] + [rep[x] for x in xs]
    for i, P in enumerate(reps):
        for s in S:
            R = add(P, s, p, a)
            B[i, idx[None if R is None else R[0]]] += 1
    return B, size, xs

def check_curve(p, a, b, FB_E=None, FB_T=None, label=""):
    E = points(p, a, b); n = len(E)
    XE = sorted({P[0] for P in E[1:]})
    XT = [x for x in range(p) if legendre(x ** 3 + a * x + b, p) == -1]
    FB_E = FB_E if FB_E is not None else []
    FB_T = FB_T if FB_T is not None else []
    FB = sorted(set(FB_E) | set(FB_T))
    M = full_M(p, a, b, FB)
    out = dict(label=label, p=p, a=a, b=b, n=n, n_twist=2 * p + 2 - n,
               FB_E=len(FB_E), FB_T=len(FB_T),
               two_torsion_E=sum(1 for P in E[1:] if P[1] == 0))
    out['cross_mass'] = int(M[np.ix_(XE, XT)].sum() + M[np.ix_(XT, XE)].sum())
    out['ME_mass'] = int(M[np.ix_(XE, XE)].sum()); out['MT_mass'] = int(M[np.ix_(XT, XT)].sum())
    # E side
    if FB_E or not FB_T:
        B, size, xs = cayley_quotient(E, set(FB_E), p, a)
        ME = M[np.ix_(xs, xs)].astype(float)
        out['E1_M_eq_B_minus_O'] = bool(np.array_equal(ME, B[1:, 1:]))
        out['E1_max_entry_diff'] = float(np.max(np.abs(ME - B[1:, 1:])))
        Dh = np.sqrt(size); Bs = (Dh[:, None] * B) / Dh[None, :]
        out['B_sym_is_symmetric'] = bool(np.allclose(Bs, Bs.T))
        fbv = np.array([1.0 if x in set(FB_E) else 0.0 for x in xs])
        out['E2_coupling_sqrt2'] = bool(np.allclose(Bs[0, 1:], np.sqrt(2) * fbv) and np.allclose(Bs[1:, 0], np.sqrt(2) * fbv))
        lamB = np.sort(np.linalg.eigvals(B).real)
        bord = np.zeros_like(Bs); bord[1:, 1:] = ME
        bord[0, 1:] = bord[1:, 0] = np.sqrt(2) * fbv
        evb = np.sort(np.linalg.eigvalsh(bord))
        out['E3_bordered_eq_specB'] = bool(np.allclose(evb, lamB, atol=1e-8))
        out['E3_max_err'] = float(np.max(np.abs(evb - lamB)))
        mu = np.sort(np.linalg.eigvalsh(ME))
        out['E4_interlaces'] = bool(all(lamB[i] - 1e-8 <= mu[i] <= lamB[i + 1] + 1e-8 for i in range(len(mu))))
        # exact coincidences of M eigenvalues with B eigenvalues
        out['E4_M_eigs_equal_to_some_lambda'] = int(sum(np.min(np.abs(lamB - m)) < 1e-8 for m in mu))
        # E5: for each eigenvector f of B (unsymmetrised), residual of f|_{nonO} under M is -f(O)*B[o,O]
        w, V = np.linalg.eig(B)
        res = []
        for j in range(len(w)):
            f = V[:, j].real if np.allclose(V[:, j].imag, 0) else None
            if f is None or abs(w[j].imag) > 1e-9: continue
            r = ME @ f[1:] - w[j].real * f[1:] + f[0] * B[1:, 0]
            res.append(float(np.max(np.abs(r))))
        out['E5_max_resid_identity'] = max(res) if res else None
        out['E5_B_col_O_equals_1FB'] = bool(np.allclose(B[1:, 0], fbv))
    # twist side: build E' (X = d x) and compare twist block with its Cayley quotient
    if FB_T:
        d = next(t for t in range(2, p) if legendre(t, p) == -1)
        a2, b2 = a * d * d % p, b * d ** 3 % p
        Et = points(p, a2, b2)
        dinv = pow(d, -1, p)
        FBt_scaled = {x * d % p for x in FB_T}
        Bt, sizet, xst = cayley_quotient(Et, FBt_scaled, p, a2)
        xs_orig = [X * dinv % p for X in xst]              # twist x's in E's coordinate
        MT = M[np.ix_(xs_orig, xs_orig)].astype(float)
        out['twist_order_check'] = len(Et) == 2 * p + 2 - n
        out['T1_MT_eq_Bt_minus_O'] = bool(np.array_equal(MT, Bt[1:, 1:]))
        out['T1_max_entry_diff'] = float(np.max(np.abs(MT - Bt[1:, 1:])))
        mu = np.sort(np.linalg.eigvalsh(MT)); lamT = np.sort(np.linalg.eigvals(Bt).real)
        out['T_interlaces'] = bool(all(lamT[i] - 1e-8 <= mu[i] <= lamT[i + 1] + 1e-8 for i in range(len(mu))))
    return out

def isprime(n): return n > 1 and all(n % q for q in range(2, int(n ** .5) + 1))

if __name__ == "__main__":
    res = []
    # (1) several b per prime, prime n (producer's regime but other curves)
    for p in [61, 101, 211]:
        cnt = 0
        for b in range(2, p):
            for a in range(1, p):
                if (4 * a ** 3 + 27 * b * b) % p == 0: continue
                E = points(p, a, b)
                if not isprime(len(E)): continue
                XE = sorted({P[0] for P in E[1:]}); B0 = max(3, int(p ** .5))
                res.append(check_curve(p, a, b, FB_E=XE[:B0], label="primeN_otherb")); cnt += 1
                break
            if cnt >= 2: break
    # (2) odd composite n (cyclic or not), (3) even n with 2-torsion, (4) twist-side and mixed FB
    want = {"odd_composite": 0, "even_n": 0}
    for p in [67, 73, 79, 97, 103, 109]:
        for a in range(1, p):
            b = 3
            if (4 * a ** 3 + 27 * b * b) % p == 0: continue
            E = points(p, a, b); n = len(E)
            XE = sorted({P[0] for P in E[1:]}); B0 = max(3, int(p ** .5))
            XT = [x for x in range(p) if legendre(x ** 3 + a * x + b, p) == -1]
            if n % 2 == 1 and not isprime(n) and want["odd_composite"] < 3:
                res.append(check_curve(p, a, b, FB_E=XE[:B0], label="odd_composite_n")); want["odd_composite"] += 1
            elif n % 2 == 0 and want["even_n"] < 3:
                # exclude 2-torsion x from FB first, then include it
                tors = {P[0] for P in E[1:] if P[1] == 0}
                fb = [x for x in XE if x not in tors][:B0]
                res.append(check_curve(p, a, b, FB_E=fb, label="even_n_FB_without_2tors"))
                fb2 = sorted(set(fb[:-1]) | tors)
                res.append(check_curve(p, a, b, FB_E=fb2, label="even_n_FB_with_2tors"))
                want["even_n"] += 1
        # twist-side and mixed FB on the first prime-n curve at this p
        for a in range(1, p):
            E = points(p, a, 1); n = len(E)
            if isprime(n) and (4 * a ** 3 + 27) % p:
                XE = sorted({P[0] for P in E[1:]})
                XT = [x for x in range(p) if legendre(x ** 3 + a * x + 1, p) == -1]
                B0 = max(3, int(p ** .5))
                res.append(check_curve(p, a, 1, FB_T=XT[:B0], label="twist_side_FB"))
                res.append(check_curve(p, a, 1, FB_E=XE[:B0 // 2], FB_T=XT[:B0 // 2], label="mixed_FB"))
                break
    print(json.dumps(res, indent=1))
