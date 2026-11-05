"""Exact rank of an integer matrix over F_p (p < 2^15), vectorised Gaussian elimination in int64."""
import numpy as np
def rank_mod_p(A, p):
    M = np.array(A, dtype=np.int64) % p
    n, m = M.shape; r = 0
    for c in range(m):
        if r == n: break
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0: continue
        piv = r + nz[0]
        if piv != r: M[[r, piv]] = M[[piv, r]]
        M[r] = (M[r] * pow(int(M[r, c]), -1, p)) % p
        col = M[r+1:, c].copy()
        nzr = np.nonzero(col)[0]
        if nzr.size:
            M[r+1+nzr] = (M[r+1+nzr] - np.outer(col[nzr], M[r])) % p
        r += 1
    return r
