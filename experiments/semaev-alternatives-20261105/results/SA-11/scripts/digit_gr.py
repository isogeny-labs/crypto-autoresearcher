"""SA-11 (a)-(c) digits: first fall degree via the graded-annihilator identity ffd = D + a(f_top),
for real (unsat, selected), support-matched null Usupp and block-factored null Ublock, m=2, s=2..S.
Also m=3 top form (Q1 Q2 Q3, degree-4 blocks) at s=4,5."""
import sys, random, json, math, itertools, numpy as np
import lib
from lib import *

def zeta_values(f, n, p):
    arr = np.zeros(1<<n, dtype=np.int64)
    for m,c in f.items(): arr[m] = c
    for i in range(n):
        step = 1<<i
        a = arr.reshape(-1, 2*step)
        a[:, step:] = (a[:, step:] + a[:, :step]) % p
    return arr  # value at assignment x = sum over subsets of x's support of coefficient

def is_unit(f, n, p): return bool(np.all(zeta_values(f,n,p) != 0))

def blk_support(s, shift, deg):
    out = []
    for d in range(deg+1):
        for c in itertools.combinations(range(s), d):
            out.append(sum(1<<(shift+i) for i in c))
    return out

def draw_real(rng, s, p):
    for _ in range(20000):
        a, b, xR = rng.randrange(p), rng.randrange(p), rng.randrange(p)
        if (4*a**3+27*b*b) % p == 0: continue
        M = s3_matrix(a, b, xR, p)
        f = digit_f(M, s, p)
        if is_unit(f, 2*s, p): return f, (a,b,xR)
    return None, None

def draw_usupp(rng, s, p):
    sup = [m1|m2 for m1 in blk_support(s,0,2) for m2 in blk_support(s,s,2)]
    for _ in range(2000):
        f = {m: rng.randrange(1,p) for m in sup}
        if is_unit(f, 2*s, p): return f
    return None

def draw_ublock(rng, s, p):
    for _ in range(2000):
        q = []
        for k in range(2):
            q.append({m: rng.randrange(0,p) for m in blk_support(s, k*s, 2)})
        f = pmul(q[0], q[1], p)
        if f and is_unit(f, 2*s, p): return f
    return None

def run(S, ndraw, seed=11):
    rng = random.Random(seed); rows = []
    for s in range(2, S+1):
        n = 2*s
        for arm in ('real','usupp','ublock'):
            for d in range(ndraw if s <= 6 else max(2, ndraw//2)):
                b = 2*s+1
                p = rand_prime(rng, 2**b, 2**(b+1))
                if arm == 'real': f, par = draw_real(rng, s, p)
                elif arm == 'usupp': f = draw_usupp(rng, s, p)
                else: f = draw_ublock(rng, s, p)
                if f is None: rows.append(dict(m=2,s=s,arm=arm,p=p,status='no-unit-draw')); continue
                D, ft = top_form(f)
                j = ann_degree(GrBool(n), ft, D, p)
                rows.append(dict(m=2, s=s, arm=arm, p=p, D=D, ann=j, ffd=D+j, status='ok'))
                print(rows[-1], flush=True)
    return rows

if __name__ == '__main__':
    S = int(sys.argv[1]); nd = int(sys.argv[2])
    rows = run(S, nd)
    json.dump(rows, open('/home/user/semaev-runs/SA-11/out/digit_gr_rows.json','w'))
