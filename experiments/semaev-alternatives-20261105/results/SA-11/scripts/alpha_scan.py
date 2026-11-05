"""Does the first fall degree depend on the constraint density alpha = log2(p)/n?  Vary p (hence alpha) at fixed s, and s at ~fixed alpha.
Real digit system m=2; units only (f must have no grid zero) -> alpha >~ 1. Uses graded annihilator (exact identity) + closure engine for s<=4."""
import random, json, math
import lib, closure
from digit_gr import draw_real
rng = random.Random(77); rows=[]
for s in (3,4,5):
    n = 2*s
    for b in range(2*s, 2*s+9, 2):
        for rep in range(3):
            p = lib.rand_prime(rng, 2**b, 2**(b+1))
            f, par = draw_real(rng, s, p)
            if f is None: rows.append(dict(s=s,b=b,p=p,status='no-unit')); continue
            D, ft = lib.top_form(f); j = lib.ann_degree(lib.GrBool(n), ft, D, p)
            row = dict(s=s, b=b, alpha=round(math.log2(p)/n,2), ffd_gr=D+j)
            if s <= 4 and p < 2**20:
                R = closure.Ring('bool', n, p, cmax=s+4); r = closure.closure_dF(R, f, s+4, p)
                row.update(ffd=r['ffd'], dF=r['dF'])
            rows.append(row); print(row, flush=True)
json.dump(rows, open('/home/user/semaev-runs/SA-11/out/alpha_scan.json','w'))
