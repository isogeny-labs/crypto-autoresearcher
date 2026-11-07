"""End-to-end check (integer side): when the coprime criterion holds, resultant + root finding returns exactly the planted (x1,x2)."""
import sys; sys.path.insert(0,'.')
from lat_e2e import *
import random, sympy, itertools
rng = random.Random(11); random.seed(11)
X, Y = pari('x'), pari('y')
for (q, n, s, t, S) in [(3, 32, 4, 2, 8), (3, 40, 4, 2, 9), (5, 24, 2, 1, 6), (7, 24, 4, 2, 6), (3, 48, 6, 3, 12)]:
    p = int(sympy.nextprime(q**n)); crit = 0; rec = 0
    for _ in range(10):
        r = z_trial(q, n, p, S, s, t, rng)
        if not r['success']: continue
        crit += 1; found = False
        P0 = [sum(pari(int(c))*X**a*Y**b for (a, b), c in g.items()) for _, g in r['rows']]
        P = [sum(random.randint(-5, 5)*P0[k] for k in range(len(P0))) for _ in range(4)]   # random integer combinations of all vanishing rows
        for i, j in itertools.combinations(range(len(P)), 2):
            R = pari.polresultant(P[i], P[j], 'y')
            if R == 0: continue
            for r1 in pari.nfroots(None, R):
                if int(r1) == r['x1']:
                    G = pari.gcd(pari.subst(P[i], 'x', r1), pari.subst(P[j], 'x', r1))
                    if pari.poldegree(G) >= 1 and any(int(z) == r['x2'] for z in pari.nfroots(None, G)): found = True
            if found: break
        rec += found
    print(q, n, s, t, S, 'criterion holds', crit, 'planted (x1,x2) recovered', rec, flush=True)
