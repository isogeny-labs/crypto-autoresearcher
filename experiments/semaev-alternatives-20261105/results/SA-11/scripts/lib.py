"""Shared tools for SA-11: polynomials in Boolean / tower quotient rings over F_p,
modular rank, graded annihilator degree, and a Macaulay-closure engine (HKY convention)."""
import numpy as np, itertools, random, math
from math import comb
from scipy import sparse

def is_prime(n):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, r = n-1, 0
    while d % 2 == 0: d//=2; r+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(r-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True

def rand_prime(rng, lo, hi, cong=None):
    while True:
        p = rng.randrange(lo, hi)
        if cong: p = p - (p-1) % cong
        if lo <= p < hi and is_prime(p): return p

# ---------- Semaev S3 coefficients: S3 = sum_{ij} M[i][j] x1^i x2^j  (i,j in 0..2), x3 = xR
def s3_matrix(a, b, xR, p):
    # S3 = xR^2 (e1^2-4e2) - 2 xR (e1 e2 + a e1 + 2b) + e2^2 - 2a e2 + a^2 - 4b e1
    M = [[0]*3 for _ in range(3)]
    def add(i,j,c): M[i][j] = (M[i][j] + c) % p
    X = xR % p
    # e1^2-4e2 = x1^2 -2x1x2 + x2^2
    add(2,0,X*X); add(1,1,-2*X*X); add(0,2,X*X)
    # -2X(e1 e2 + a e1 + 2b), e1e2 = x1^2x2 + x1x2^2
    add(2,1,-2*X); add(1,2,-2*X); add(1,0,-2*X*a); add(0,1,-2*X*a); add(0,0,-4*X*b)
    # e2^2 -2a e2 + a^2 - 4b e1
    add(2,2,1); add(1,1,-2*a); add(0,0,a*a); add(1,0,-4*b); add(0,1,-4*b)
    return M

def s3_eval_ok(M,p):
    return M

# ---------- Boolean polynomial helpers (dict mask->coef mod p)
def pmul(A,B,p):
    out = {}
    for ma,ca in A.items():
        for mb,cb in B.items():
            m = ma|mb
            out[m] = (out.get(m,0)+ca*cb) % p
    return {m:c for m,c in out.items() if c}
def padd(A,B,p,s=1):
    out = dict(A)
    for m,c in B.items(): out[m] = (out.get(m,0)+s*c) % p
    return {m:c for m,c in out.items() if c}
def pscale(A,k,p): return {m:(c*k)%p for m,c in A.items() if (c*k)%p}

def digit_f(M, s, p):
    """S3(l1,l2,xR) reduced in B = F_p[a]/(a^2-a); block1 = bits 0..s-1, block2 = bits s..2s-1."""
    L1 = {1<<i: pow(2,i,p) for i in range(s)}
    L2 = {1<<(s+i): pow(2,i,p) for i in range(s)}
    A = [{0:1}, L1, pmul(L1,L1,p)]
    B = [{0:1}, L2, pmul(L2,L2,p)]
    f = {}
    for i in range(3):
        for j in range(3):
            if M[i][j]%p: f = padd(f, pscale(pmul(A[i],B[j],p), M[i][j], p), p)
    return f

def f_degree(f): return max(bin(m).count('1') for m in f)
def top_form(f):
    D = f_degree(f); return D, {m:c for m,c in f.items() if bin(m).count('1')==D}

def digit_eval_zero(f_M, s, p):
    """does S3(u,v,xR) vanish for some u,v in [0,2^s)? M gives coefficients."""
    u = np.arange(2**s, dtype=np.int64)
    pw = [np.ones_like(u), u%p, (u*u)%p]
    for v in range(2**s):
        vp = [1, v%p, (v*v)%p]
        val = np.zeros_like(u)
        for i in range(3):
            for j in range(3):
                val = (val + M[i][j]*vp[j] % p * pw[i]) % p
        if (val==0).any(): return True
    return False

# ---------- modular rank (int64 numpy elimination)
def rank_mod_p(A, p):
    A = np.array(A, dtype=np.int64) % p
    r = 0; rows, cols = A.shape
    if rows > cols: A = A.T.copy(); rows, cols = cols, rows
    for c in range(cols):
        if r >= rows: break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0: continue
        piv = r + nz[0]
        if piv != r: A[[r,piv]] = A[[piv,r]]
        inv = pow(int(A[r,c]), p-2, p)
        A[r] = (A[r]*inv) % p
        below = np.nonzero(A[r+1:, c])[0] + r+1
        if len(below):
            A[below] = (A[below] - np.outer(A[below, c], A[r])) % p
        r += 1
    return r

# ---------- graded annihilator degree of a top form
class GrBool:
    """gr R for the Boolean ring: squarefree monomials, product = union if disjoint else 0."""
    def __init__(self, n): self.n = n
    def mul(self, m, b):
        return None if (m & b) else (m | b)
    def monos(self, j):
        for comb_ in itertools.combinations(range(self.n), j):
            yield sum(1<<i for i in comb_)
class GrTower:
    """gr R for product of t-level Kummer towers (m summands): exponent k_i in Z/K, degree popcount; product is zero in gr
    when popcount drops (carry)."""
    def __init__(self, m, t): self.m, self.t, self.n = m, t, m*t; self.K = 1<<t
    def mul(self, x, y):
        K, t = self.K, self.t; out = 0; 
        for i in range(self.m):
            a = (x >> (i*t)) & (K-1); b = (y >> (i*t)) & (K-1)
            if bin((a+b) % K).count('1') != bin(a).count('1')+bin(b).count('1'): return None
            out |= ((a+b) % K) << (i*t)
        return out
    def monos(self, j):
        for comb_ in itertools.combinations(range(self.n), j):
            yield sum(1<<i for i in comb_)

def ann_degree(gr, ftop, D, p, jmax=None, want_dims=False):
    """smallest j with a nonzero h in gr_j with h*ftop=0 in gr; returns j (or None)."""
    n = gr.n; jmax = jmax if jmax is not None else n
    for j in range(0, jmax+1):
        src = list(gr.monos(j))
        tgt = {}; ents = []
        for si, m in enumerate(src):
            for b,c in ftop.items():
                r = gr.mul(m,b)
                if r is None: continue
                ti = tgt.setdefault(r, len(tgt)); ents.append((si,ti,c))
        if not ents: return j
        A = np.zeros((len(src), len(tgt)), dtype=np.int64)
        for si,ti,c in ents: A[si,ti] = (A[si,ti]+c) % p
        if rank_mod_p(A,p) < len(src): return j
    return None
