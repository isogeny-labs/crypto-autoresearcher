"""End-to-end check for the budget-8 Edwards-y form lattice: recover the reduced vector, solve for (y1 y2, y1^2+y2^2),
then y1, y2, lift to points and verify P1 + P2 = R in the group.  96 bits, delta = 0.11, 20 trials."""
import sys, random, json, math
sys.path.insert(0, '/home/user/semaev-runs/SA-19')
from lattice19 import *
import sympy as sp
rng = random.Random(777); bits = 96; p = rand_prime(bits, rng)
cs = EdwardsY(); cs.setup(p, rng); cs.T, cs.degs = echelon_T(cs.co); cs.Tinv = mat_inv_mod(cs.T, p)
print('integer twisted-Edwards summation polynomial (A=6, a=8, d=4):', cs.S)
print('coefficient polynomials c0,c1,c2:', cs.co); print('echelon T:', cs.T, 'degrees', cs.degs)
Y1, Y2, lam = sp.symbols('Y1 Y2 lam')
cpol = [sum(v * Y1**k[0] * Y2**k[1] for k, v in q.items()) for q in cs.co]
vpol = [sum(cs.T[i][j] * cpol[j] for j in range(3)) for i in range(3)]
ok_all = 0; out = []
for trial in range(20):
    delta = 0.11; B = int(round(2 ** (delta * bits)))
    y1, y2, yR = cs.plant(B, rng)
    c = [peval_int(q, (y1, y2)) for q in cs.co]; v = [sum(cs.T[i][j] * c[j] for j in range(3)) for i in range(3)]
    mu = [pow(yR, l, p) for l in range(3)]; mu2 = [sum(mu[j] * cs.Tinv[j][i] for j in range(3)) % p for i in range(3)]
    ok, best = form_lattice_recover([mu2], v, cs.degs, B, p)
    if not ok: out.append(dict(trial=trial, lattice=False)); continue
    # solve vpol(Y1,Y2) = lam * best  for Y1, Y2 (symmetric): use s = Y1+Y2? equations are in P=Y1Y2 and S2=Y1^2+Y2^2
    sols = sp.solve([sp.expand(vpol[i] - lam * best[i]) for i in range(3)], [Y1, Y2, lam], dict=True)
    cands = set()
    for s in sols:
        a1, a2 = s.get(Y1), s.get(Y2)
        if a1 is None or a2 is None or not (a1.is_integer and a2.is_integer): continue
        cands.add((int(a1), int(a2)))
    found = (y1, y2) in cands or (y2, y1) in cands
    # verify in the group: lift, add, compare y-coordinate of R
    E = cs.E; verified = False
    for (a1, a2) in cands:
        try:
            u1 = (1 + a1) * pow(1 - a1, -1, p) % p; u2 = (1 + a2) * pow(1 - a2, -1, p) % p
        except ValueError: continue
        P1, P2 = E.lift_x(u1), E.lift_x(u2)
        if P1 is None or P2 is None: continue
        for s1 in (P1, E.neg(P1)):
            R = E.add(s1, P2)
            if R and (R[0] - 1) * pow(R[0] + 1, -1, p) % p == yR: verified = True
    ok_all += verified
    out.append(dict(trial=trial, lattice=True, candidates=sorted(cands), planted=[y1, y2], found=found, verified=verified))
print('verified in group: %d / 20' % ok_all)
json.dump(dict(p=str(p), bits=bits, delta=0.11, verified=ok_all, rows=out), open('/home/user/semaev-runs/SA-19/results/e2e_edwards.json', 'w'), indent=1)
