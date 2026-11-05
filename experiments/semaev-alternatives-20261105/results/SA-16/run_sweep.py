"""Sweep: family x solver x B=2^k.  usage: run_sweep.py FAMILY BITS TRIALS KMIN KMAX KSTEP OUT.json [seed]
Families: G (generic, a=0,b=7), Gp (generic, ~p-size a,b), C1 (degenerate conic, f(xr)=0), C2 (R=[2]P1, a=0,b=7),
C3 (anomalous curve y^2=x^3+b small b, generic planted R=P1+P2).
Success = some returned (x1,x2) passes verify_decomp (group-law check with x<=B).  Never uses the planted x1,x2 in a solver."""
import sys, json, time, random
from common import *
from solvers import *
from anomalous import anomalous_curve

fam, bits, trials, kmin, kmax, kstep, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
seed = int(sys.argv[8]) if len(sys.argv) > 8 else 1
rng = random.Random(seed * 1000003 + bits)

BIV = [('biv_m1s0', dict(m=1, s=0)), ('biv_m1s1', dict(m=1, s=1)), ('biv_m2s0', dict(m=2, s=0)), ('biv_m2s1', dict(m=2, s=1))]


def mk_biv(kw):
    return lambda inst: solve_cop_biv(inst, **kw)


SOLVERS = {
    'G': [('L3', solve_L3)] + [(n, mk_biv(kw)) for n, kw in BIV],
    'Gp': [('L3', solve_L3)] + [(n, mk_biv(kw)) for n, kw in BIV],
    'C3': [('L3', solve_L3)] + [(n, mk_biv(kw)) for n, kw in BIV],
    'C2': [('L3', solve_L3), ('L2diag', solve_L2diag), ('cop_uni_m4t4', lambda i: solve_cop_uni(i, 4, 4)),
           ('cop_uni_m2t2', lambda i: solve_cop_uni(i, 2, 2))] + [(n, mk_biv(kw)) for n, kw in BIV],
    'C1': [('L3', solve_L3), ('vieta_cvp', solve_vieta_cvp),
           ('biv_rad_m1s0', lambda i: solve_cop_biv_rad(i, 1, 0)), ('biv_rad_m2s0', lambda i: solve_cop_biv_rad(i, 2, 0)), ('biv_rad_m3s0', lambda i: solve_cop_biv_rad(i, 3, 0))]
          + [(n, mk_biv(kw)) for n, kw in BIV],
    'ENUM': [('enum', solve_enum)],
}

p = None
if fam == 'C3':
    p, a3, b3 = anomalous_curve(bits, rng)
elif fam in ('G', 'C2', 'ENUM'):
    p = nextprime_34(bits, rng)
else:
    p = nextprime_34(bits, rng)

import os, re
FILT = os.environ.get('SOLVER_FILTER')
rows = []
for k in range(kmin, kmax + 1, kstep):
    B = 2 ** k
    insts = []
    for t in range(trials):
        if fam == 'G': inst = plant_small_curve(p, B, rng=rng)
        elif fam in ('C2', 'ENUM'): inst = plant_small_curve(p, B, rng=rng, diag=True)
        elif fam == 'C1': inst = plant_degenerate_conic(p, B, rng=rng)
        elif fam == 'Gp': inst = plant_generic_largecoeff(p, B, rng=rng)
        elif fam == 'C3': inst = plant_small_curve(p, B, a=0, b=b3, rng=rng)
        insts.append(inst)
    for name, fn in SOLVERS[fam]:
        if FILT and not re.search(FILT, name): continue
        succ = 0; vanish = 0; times = []
        for inst in insts:
            ii = dict(inst)
            t0 = time.process_time()
            try:
                sols = fn(ii)
            except Exception as e:
                sols = []
            dt = time.process_time() - t0
            ok = any(verify_decomp(x1, x2, ii['xr'], ii['a'], ii['b'], p, B) for x1, x2 in sols)
            succ += ok
            times.append(dt)
            if '_polys' in ii:
                x1, x2 = inst['x1'], inst['x2']
                pl = ii['_polys'][:2]
                if len(pl) == 2 and all(sum(c * x1 ** i * x2 ** j for (i, j), c in h.items()) == 0 for h in pl):
                    vanish += 1
        rows.append(dict(fam=fam, bits=bits, k=k, B=B, delta=k / bits, solver=name, trials=trials, succ=succ, vanish=vanish, times=times))
        print(fam, bits, 'k=%d' % k, name, '%d/%d' % (succ, trials), 'vanish=%d' % vanish, 'mean_t=%.4f' % (sum(times) / len(times)), flush=True)
    json.dump(rows, open(out, 'w'))
