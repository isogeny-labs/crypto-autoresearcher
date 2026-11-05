"""Red-team: exact description of spec(M) for odd cyclic n (non-degenerate case).
Deleting vertex O from the symmetrised Cayley quotient: mu is an eigenvalue of M iff
  G(mu) = sum_{j in Z/n} 1/(lambda_j - mu) = 0      (lambda_j = lambda_{-j}; trace of resolvent)
and the eigenvector is the Green function v(P) = sum_{j in Z/n} chi_j(P)/(lambda_j - mu).
Checks both at the producer's five curves (same curve/FB selection rule)."""
import numpy as np, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/rt_rerun')
from rt_transfer import points, add, full_M, isprime

res = []
for p in [61, 101, 163, 211, 307]:
    for a in range(1, p):
        E = points(p, a, 1); n = len(E)
        if isprime(n) and n >= 5: break
    G = E[1]; log = {}; R = None
    for k in range(n): log[R] = k; R = add(R, G, p, a)
    Ex = sorted({P[0] for P in E[1:]}); B0 = max(3, int(p ** .5)); FB = [x for x in Ex if x <= B0 * 3][:B0]
    M = full_M(p, a, 1, FB)[np.ix_(Ex, Ex)].astype(float)
    mu, V = np.linalg.eigh(M)
    S = [log[P] for P in E[1:] if P[0] in set(FB)]
    lam = np.array([sum(np.cos(2 * np.pi * j * s / n) for s in S) for j in range(n)])  # all j in Z/n
    Gval = np.array([np.sum(1.0 / (lam - m)) for m in mu])
    # scale-free secular residual: |G(mu)| relative to sum |1/(lam-mu)|
    rel = np.abs(Gval) / np.array([np.sum(np.abs(1.0 / (lam - m))) for m in mu])
    # eigenvector check: Green function vs numerical eigenvector (cosine similarity)
    cs = []
    for i, m in enumerate(mu):
        g = np.zeros(len(Ex))
        for P in E[1:]:
            g[Ex.index(P[0])] = np.sum(np.cos(2 * np.pi * np.arange(n) * log[P] / n) / (lam - m))
        cs.append(abs(g @ V[:, i]) / (np.linalg.norm(g) * np.linalg.norm(V[:, i])))
    res.append(dict(p=p, a=a, n=n, FB=len(FB), max_rel_secular_residual=float(rel.max()),
                    min_cosine_green_vs_eigvec=float(min(cs))))
print(json.dumps(res, indent=1))
