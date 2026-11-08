# SA-20 report: Coppersmith ladder on the twisted-Edwards summation polynomial

## Summary
**INCONCLUSIVE** against the frozen criteria. Asymptotic reach is unchanged (the KILL asymptotic half holds), but the planted crossings at fixed shift depth t beat the Weierstrass control by 0.015-0.022 (> 0.01), so the KILL planted half fails; SUCCESS fails because no asymptotic or extrapolated reach exceeds 1/6 + 0.01.

Deciding numbers:
- Newton polytope of Edwards S_3 in (y1,y2): hull = full box [0,2]^2 (5 monomials, parity lattice a = b mod 2, index 2); S_4 in (y1,y2,y3): full box [0,4]^3 (35 of 125 monomials, parity lattice index 4). Centroid sum 2 and 6, so reach 1/6 and 1/24, identical to Weierstrass. cuso 0.4.0 (independent): delta* = 1/6 exactly (m=2, k_pre 1,2) and 1/24 exactly (m=3, k_pre 1).
- Certified finite-t reach, m=2 (exact MILP, parity-coset lattices), Edwards vs Weierstrass: t=2 .1152/.0996, t=3 .1265/.1187, t=4 .1338/.1294, t=6 .1431/.1406, t=8 .1479/.1470, t=12 .1538/.1531. Gap .0156, .0078, .0044, .0025, .0009, .0007: decays to 0. Fit D - a/t - b/t^2: Edwards 0.1657 (LOO 0.1655-0.1662), Weierstrass 0.1662 (0.1660-0.1664).
- m=3 certified: Edwards t=2 .0158, t=3 .0223 (Weierstrass SA-01: .0144, .0215); t=4 not certified (MILP time limit).
- Planted 50% crossings (20 trials/delta, step 0.005): t=2: Edwards .1506 (64 b), .1475 (96 b) vs Weierstrass .1281, .1256 (gap +.022). t=3: Edwards .1567, .1532 vs .1410, .1385 (gap +.016, +.015).

## What was run
1. step1_polytope.py: S_3, S_4 (PARI resultant, y4 or x4 = 7) supports, hull, centroid, delta = 1/((n+1) sum g), parity sublattice index (Smith form).
2. model2.py / run_m2.py / run_m2_ed_hi.py / run_m3.py: MILP certifier with exact support and per-coset lattices; fit.py.
3. cuso_ed.py: cuso asymptotic bounds on the integer Edwards S_3 and S_4.
4. plant20.py: planted fpylll (LLL 0.99) recovery on the SA-19 Edwards curve (v^2 = u^3+6u^2+u, y=(u-1)/(u+1), y_i in [2,B+1]) and y^2=x^3+3x+5 (control), 64 and 96 bits, t = 2, 3, shift set from the MILP optimum.

## Results
Asymptotics: the odd-degree cancellation halves the monomial lattice, but halves both determinant and gain; centroid ratio unchanged. The z = y^2 view (bilinear in z, bounds p^{2 delta}) gives 2 delta = 1/3, again 1/6. Frozen prediction (ceiling 1/6; finite-t within 0.01 of Weierstrass) holds for the ceiling; the finite-t part holds only for t >= 4 (gap at t=2,3 is .016, .008 certified).
Planted recovery exceeds the certified delta for both lattices (by ~0.03 for Weierstrass), as in SA-01. The Edwards lattice has half the dimension at equal t (13/25 vs 25/49), roughly Weierstrass at 2t; the advantage is a finite-depth, boundary effect and shrinks as t grows. Raw: results/*.json, results/plant.jsonl, results/plant_*.log; figure fig_sa20.png.

## Verdict reasoning
SUCCESS needs asymptotic/extrapolated > 1/6 + 0.01 (m=2) or > 1/24 + 0.005 (m=3): found 1/6, 0.1657, 1/24. KILL needs also planted crossings within 0.01 of the control at the same t: they differ by 0.015-0.022. Hence INCONCLUSIVE by the frozen letter. What would decide: planted crossings at t >= 5 (dimension Weierstrass 121, Edwards 61), where the certified gap is < 0.003; I expect it to fall inside 0.01, which would convert to KILL, but that was not run.

## Limitations
Toy sizes; crossings by linear interpolation of 20-trial rates, no CIs; Edwards t=16,20 and m=3 t=4 MILP not certified; planted tests only m=2, t = 2, 3; one curve per model with small constants; cuso only on the box polytope.

## Suggested lead-atlas update
LEAD (lattice lens / Coppersmith ladder on Edwards S_3): ceiling unchanged, 1/6 (m=2) and 1/24 (m=3) by centroid, MILP fit (0.1657) and cuso; Edwards parity structure yields only a finite-depth gain (certified +0.016 at t=2 decaying to +0.0007 at t=12; planted +0.015-0.022 at t=2,3). Disposition: killed up to a constant; next_action none, optional planted check at t=5.
