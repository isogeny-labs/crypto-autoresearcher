"""Red-team edge cases for the transfer-matrix claim.
(i)  even n: locate the entries where M != B[1:,1:] and test the 2-torsion correction.
(ii) j=0 (a=0, p=1 mod 3, prime n) with a zeta-stable FB: count M eigenvalues that equal a
     character sum exactly, and test whether character differences are exact eigenvectors of M.
Toy primes only."""
import numpy as np, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/rt_rerun')
from rt_transfer import points, add, full_M, cayley_quotient, isprime, legendre

out = {"even_n": [], "j0": []}
# (i) even n
for (p, a, b) in [(67, 2, 3), (67, 3, 3), (67, 5, 3)]:
    E = points(p, a, b); n = len(E)
    XE = sorted({P[0] for P in E[1:]}); tors = {P[0] for P in E[1:] if P[1] == 0}
    fb = [x for x in XE if x not in tors][:8]
    M = full_M(p, a, b, fb)
    B, size, xs = cayley_quotient(E, set(fb), p, a)
    ME = M[np.ix_(xs, xs)].astype(float); D = B[1:, 1:] - ME
    bad = [(xs[i], xs[j]) for i, j in zip(*np.nonzero(D))]
    rows_bad = {u for u, _ in bad}
    # correction: B_sym restricted with 2-torsion <-> non-2-torsion couplings divided by sqrt2
    Dh = np.sqrt(size); Bs = (Dh[:, None] * B) / Dh[None, :]
    C = Bs[1:, 1:].copy()
    t = np.array([x in tors for x in xs])
    C[np.ix_(t, ~t)] /= np.sqrt(2); C[np.ix_(~t, t)] /= np.sqrt(2)
    lamB = np.sort(np.linalg.eigvals(B).real); mu = np.sort(np.linalg.eigvalsh(ME))
    viol = [i for i in range(len(mu)) if not (lamB[i] - 1e-8 <= mu[i] <= lamB[i + 1] + 1e-8)]
    out["even_n"].append(dict(p=p, a=a, b=b, n=n, two_torsion_x=sorted(tors),
        n_bad_entries=len(bad), bad_rows_subset_of_2torsion=rows_bad <= tors,
        B_over_M_on_bad=sorted({float(B[1:, 1:][xs.index(u), xs.index(v)] / ME[xs.index(u), xs.index(v)]) for u, v in bad if ME[xs.index(u), xs.index(v)]}),
        corrected_C_equals_M=bool(np.allclose(C, ME)),
        interlacing_violations=len(viol),
        first_violation=(None if not viol else dict(i=viol[0], lam_i=float(lamB[viol[0]]), mu_i=float(mu[viol[0]]), lam_ip1=float(lamB[viol[0] + 1])))))

# (ii) j = 0
for p in [67, 73, 79, 97, 103, 109, 127, 139, 151, 157, 163, 181, 193, 199]:
    if p % 3 != 1: continue
    z = next(g for g in range(2, p) if pow(g, (p - 1) // 3, p) != 1)
    zeta = pow(z, (p - 1) // 3, p)
    for b in range(1, p):
        E = points(p, 0, b); n = len(E)
        if not isprime(n): continue
        XE = sorted({P[0] for P in E[1:]})
        orbits = []
        seen = set()
        for x in XE:
            if x in seen or x == 0: continue
            o = {x, x * zeta % p, x * zeta * zeta % p}; seen |= o; orbits.append(sorted(o))
        k = max(1, int(p ** .5) // 3)
        fb = sorted(set().union(*orbits[:k]))
        M = full_M(p, 0, b, fb)
        B, size, xs = cayley_quotient(E, set(fb), p, 0)
        ME = M[np.ix_(xs, xs)].astype(float)
        lamB = np.sort(np.linalg.eigvals(B).real); mu = np.sort(np.linalg.eigvalsh(ME))
        # multiplicities of B eigenvalues
        uniq = []
        for l in lamB:
            if not uniq or abs(l - uniq[-1][0]) > 1e-8: uniq.append([l, 1])
            else: uniq[-1][1] += 1
        mult = sorted({m for _, m in uniq})
        exact = int(sum(np.min(np.abs(lamB - m)) < 1e-8 for m in mu))
        # explicit character-difference eigenvector: need cyclic log
        G = E[1]; log = {}; R = None
        for kk in range(n): log[R] = kk; R = add(R, G, p, 0)
        idx = {x: i for i, x in enumerate(xs)}
        S = [log[P] for P in E[1:] if P[0] in set(fb)]
        lam = lambda j: sum(np.cos(2 * np.pi * j * s / n) for s in S)
        mu3 = next(m for m in range(2, n) if (m * m + m + 1) % n == 0)
        j1 = 1; j2 = mu3 * j1 % n
        c = np.zeros(len(xs))
        for P in E[1:]:
            c[idx[P[0]]] = np.cos(2 * np.pi * j1 * log[P] / n) - np.cos(2 * np.pi * j2 * log[P] / n)
        res_diff = float(np.linalg.norm(ME @ c - lam(j1) * c) / np.linalg.norm(c))
        c1 = np.zeros(len(xs))
        for P in E[1:]: c1[idx[P[0]]] = np.cos(2 * np.pi * j1 * log[P] / n)
        res_single = float(np.linalg.norm(ME @ c1 - lam(j1) * c1) / np.linalg.norm(c1))
        out["j0"].append(dict(p=p, a=0, b=b, n=n, FB=len(fb), M_dim=len(mu),
            lambda_multiplicities=mult, M_eigs_exactly_equal_to_char_sums=exact,
            lam_j1_minus_lam_jmu=float(abs(lam(j1) - lam(j2))),
            resid_char_difference=res_diff, resid_single_char=res_single))
        break
print(json.dumps(out, indent=1))
