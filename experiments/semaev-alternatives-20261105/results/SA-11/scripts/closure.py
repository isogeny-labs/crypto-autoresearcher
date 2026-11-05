"""Mutant-closure (HKY) engine over F_p for monomial-basis quotient rings.
Basis = bitstrings of n bits, degree = popcount. Ring kinds:
  'bool'  : a_i^2 = a_i,  multiplication by variable i sets bit i
  'tower' : m Kummer towers of height t, variable (i,j) shifts exponent k_i by 2^j mod 2^t (degree = popcount, may fall)
V_{F,c}: smallest subspace of R_{<=c} containing f and x*g for every g in V_{F,c} of degree < c.
Returns d_F = least c with 1 in V_{F,c}, and ffd = least c with V_{F,c} meets R_{<=c-1} beyond V_{F,c-1}.
p < 2^20 so float64 BLAS matmul is exact (p^2 * N < 2^53)."""
import numpy as np
from scipy import sparse

class Ring:
    def __init__(self, kind, n, p, t=None, m=None, cmax=6):
        self.kind, self.n, self.p, self.t, self.m = kind, n, p, t, m
        N = 1 << n
        pc = np.array([bin(i).count('1') for i in range(N)], dtype=np.int16)
        keep = np.nonzero(pc <= cmax)[0]
        order = keep[np.argsort(-pc[keep], kind='stable')]  # degree descending: pivot = leading (highest degree)
        self.mons = order; self.deg = pc[order]
        self.idx = -np.ones(N, dtype=np.int64); self.idx[order] = np.arange(len(order))
        self.N = len(order)
        self.act = [self._action(v) for v in range(n)]
    def _var_map(self, v, b):
        if self.kind == 'bool': return b | (1 << v)
        t = self.t; K = 1 << t; i, j = divmod(v, t)
        k = (b >> (i*t)) & (K-1); k2 = (k + (1 << j)) % K
        return (b & ~((K-1) << (i*t))) | (k2 << (i*t))
    def _action(self, v):
        src = []; dst = []
        for ci, b in enumerate(self.mons):
            r = self._var_map(v, int(b))
            if self.idx[r] >= 0: src.append(ci); dst.append(self.idx[r])
        return sparse.csr_matrix((np.ones(len(src)), (src, dst)), shape=(self.N, self.N))

def closure_dF(R, f, cmax, p, maxrows=None, trace=False):
    """f: dict bitmask->coef. returns dict(dF, ffd, dims)"""
    N = R.N; deg = R.deg
    res = dict(dF=None, ffd=None, dims=[])
    prev_dim = 0
    one_col = R.idx[0]
    for c in range(1, cmax+1):
        cols_ok = np.nonzero(deg <= c)[0]       # columns with degree <= c are a suffix (degree descending order)
        lo = cols_ok[0]
        fvec = np.zeros(N);
        D = max(bin(m).count('1') for m in f)
        if D > c: res['dims'].append((c, 0)); continue
        for m_, co in f.items(): fvec[R.idx[m_]] = co
        B = np.zeros((0, N)); piv = np.zeros(0, dtype=np.int64)   # RREF basis
        queue = fvec[None, :]
        mult_done = 0
        while queue.shape[0]:
            # reduce queue against basis, then self-reduce -> new independent rows
            Qm = queue % p
            if B.shape[0]:
                Qm = (Qm - (Qm[:, piv] @ B) ) % p
            newrows = []; newpiv = []
            # eliminate within Qm
            Qm = np.array(Qm, dtype=np.int64)
            r = 0
            rows_idx = list(range(Qm.shape[0]))
            for col in range(lo, N):
                if r >= Qm.shape[0]: break
                nz = np.nonzero(Qm[r:, col])[0]
                if len(nz) == 0: continue
                pr = r + nz[0]
                if pr != r: Qm[[r, pr]] = Qm[[pr, r]]
                inv = pow(int(Qm[r, col]), p-2, p)
                Qm[r] = (Qm[r] * inv) % p
                others = np.nonzero(Qm[:, col])[0]; others = others[others != r]
                if len(others): Qm[others] = (Qm[others] - np.outer(Qm[others, col], Qm[r])) % p
                r += 1; newpiv.append(col)
            Qn = Qm[:r].astype(float)
            if r == 0: break
            newpiv = np.array(newpiv, dtype=np.int64)
            # back-substitute existing basis: B -= B[:,newpiv] @ Qn
            if B.shape[0]:
                B = (B - (B[:, newpiv] @ Qn)) % p
            B = np.vstack([B, Qn]); piv = np.concatenate([piv, newpiv])
            # mutants: new rows of degree < c times every variable
            low = deg[newpiv] < c
            src = Qn[low]
            if src.shape[0] == 0: break
            outs = []
            for A in R.act:
                outs.append(np.asarray((A.T @ src.T).T))
            queue = np.vstack(outs) % p
            # drop duplicates cheaply
            queue = queue[np.any(queue != 0, axis=1)]
            if maxrows and B.shape[0] > maxrows: res['dims'].append((c, 'censored')); return res
        dim = B.shape[0]
        # 1 in V?
        has_one = False
        if dim:
            j = np.nonzero(piv == one_col)[0]
            if len(j):
                row = B[j[0]]; has_one = (np.count_nonzero(row) == 1)
        n_low = int(np.sum(deg[piv] < c))   # dim(V_c ∩ R_{<=c-1})
        res['dims'].append((c, dim, n_low))
        if trace: print('c', c, 'dim', dim, 'low', n_low, 'one', has_one, flush=True)
        if res['ffd'] is None and c > 1 and n_low > prev_dim_low(res, c): res['ffd'] = c
        if has_one: res['dF'] = c; return res
    return res

def prev_dim_low(res, c):
    # dim V_{F,c-1}
    for ent in res['dims']:
        if ent[0] == c-1 and len(ent) == 3: return ent[1]
    return 0
