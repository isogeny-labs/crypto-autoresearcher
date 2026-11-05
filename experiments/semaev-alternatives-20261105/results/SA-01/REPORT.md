# SA-01 REPORT: lattice ceilings for six presentations of the decomposition system

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary
**INCONCLUSIVE against the frozen criterion.** Success fails clearly. The kill condition cannot be stated as met: it needs every presentation within 0.005 of 1/6, 1/24 and 1/80. (iii) and (iv) were not certified asymptotically at m = 3 and m = 4, and (vi) certifies far *below* the single-polynomial value, not within 0.005 of it. No presentation exceeds the single-polynomial value in any cell computed; all results lean toward the kill direction.

Deciding numbers:
- Success line (m = 3): best certified value 0.0306 ((i), t = 6), extrapolating to 0.0416; success line 1/4. (iii) and (iv) certify 0 at m = 3 for t ≤ 3, where (i) already certifies 0.0215.
- Analytic asymptotes: weighted Newton-polytope (JM-basic) values are exactly 1/6, 1/24, 1/80 for both (i) and (ii) at m = 2, 3, 4. The Vieta graded box changes nothing.
- (v): SA-06 gives 1/6, 1/24, 1/80 for the u-variable 2-torsion symmetrisation, in all six special-j cells.
- m = 2 extrapolations: (i) 0.1664 (LOO 0.1663–0.1665); (iii) Gröbner generators 0.1652 (0.158–0.169); (iv) 0.1660 (identical to (i) at m = 2).
- (vi) integer lift is strictly worse: JM-basic asymptote 0; finite-t optimum 0.028 at t = 6, extrapolating to about 0.05.

Tooling is not what the prereg named: cuso, the sumset calculator, the Ehrhart check and the ePrint 2026/1027 LP were unavailable, replaced by an exact MILP shift-set optimiser and the analytic polytope formula (DEVIATIONS 2–4). Read "certified" with that substitution in mind.

## What was run
The run was interrupted and resumed; the first executor's outputs are reused unchanged (DEVIATIONS 1).
1. Polynomials and supports: semaev_polys.py (S_{m+1} by PARI resultants); vieta_support.py (S_{m+1} in e_1..e_m; 6/35/495 monomials, the full simplices sum g_k ≤ 2^{m-1}); pres_supports.py (supports of (iii) and (iv)).
2. Shift-set optimiser (coppersmith_lp.py, model.py, run_ceilings.py, run_model.py, run_list.py): lattices p^{t-|k|} x^s prod g_i^{k_i}, down-closed M, leading monomials chosen by weight vectors. Condition: sum_{y in M} cost(y) < sum level(y). Exact MILP gives a finite-t construction (lower bound); reach by bisection on delta. The LP relaxation is reported but is not a valid ceiling for non-box supports (DEVIATIONS 4).
3. Analytic asymptote (analytic_reach.py → analytic_reach.json): SA-06 formula generalised to graded bounds X_j = p^{c0_j + c1_j delta}: delta = (1 − (n+1) sum c0_j g_j) / ((n+1) sum c1_j g_j), g the centroid of the Newton polytope or its down-closure; the better of the two is reported.
4. Elimination checks: check_iii_m2.py (m = 2: Gröbner basis {alpha − L(e), Vieta conic}); check_iii_m3.py and check_iii_m3_elim.py (m = 3, mod 1000003): the lex Gröbner basis has exactly one e-only element, 35 terms (full Vieta S_4 support), vanishing at 20/20 genuine 3-decompositions and 0/20 random-e_3 controls. a_1 is eliminated linearly; a_2 survives to degree 3.
5. Planted recovery (plant_m2.py, lab.py): curve y^2 = x^3 + 3x + 5, planted R = P_1 + P_2 with x_i ≤ B = p^delta, MILP-optimal M at the certified delta for t = 3, fpylll LLL. Success = two reduced polynomials vanish at the root with a nonzero resultant.
6. Merge, fits and figure (finalize2.py): ceilings_table.csv, ceilings_summary.json, ceilings_m2_m3.png.

## Results
### Table 1. Asymptotic reach (analytic JM-basic Newton polytope)
| presentation | m=2 | m=3 | m=4 | source |
|---|---|---|---|---|
| (i) S_{m+1} in x, box [0,2^{m-1}]^m | 1/6 | 1/24 | 1/80 | analytic_reach.json |
| (ii) Vieta, graded bounds (B, B^2, ..., B^m) | 1/6 | 1/24 | 1/80 | analytic_reach.json |
| (iii) norm system, full-size alphas | ≡ (ii) (Gröbner, proved) | elimination ideal = (Vieta S_4) (checked); asymptote not computed | not computed | check_iii_* |
| (iv) chained S_3, full-size auxiliaries | ≡ (i) | finite t only | not computed | |
| (v) 2-torsion symmetrised, u-variables | 1/6 | 1/24 | 1/80 | SA-06 Table 1 |
| (v') naive product S(x,xR)S(x,xR+T), control | 1/12 | 1/48 | 1/160 | analytic_reach.json |
| (vi) integer lift S − p c | 0 | 0 | 0 | analytic_reach.json |

For (ii) the simplex has centroid g_k = 2^{m-1}/(m+1), so sum_k k g_k = m 2^{m-2} and delta = 2/(m(m+1)2^{m-1}), the box value exactly. The symmetric quotient cuts volume by m! and the graded bounds give it back exactly.

### Table 2. Exact finite-t certified delta (MILP; box supports LP = MILP); fit D − a/t − b/t^2 over t ≥ 2, LOO range in brackets
| pres | m | values (t: delta) | extrap. D | analytic |
|---|---|---|---|---|
| (i) | 2 | 2:.1000 3:.1189 4:.1294 6:.1408 8:.1470 12:.1531 16:.1564 | 0.1664 [0.1663, 0.1665] | 1/6 |
| (ii) | 2 | 3:.1308 8:.1512 10:.1536 12:.1540 (60 s MILP limit) | 0.159 [0.142, 0.163] | 1/6 |
| (iii) raw generators | 2 | t=2–4: 0 | – | – |
| (iii) Gröbner generators | 2 | 2:.1161 3:.1303 4:.1387 5:.1433 | 0.1652 [0.158, 0.169] | 1/6 |
| (iv) | 2 | identical to (i), t ≤ 6 | 0.1660 | 1/6 |
| (v') naive product | 2 | 6:.0670 | 0.0829 | 1/12 |
| (vi) | 2 | 2:.0040 4:.0187 6:.0281 (LP) | 0.051 [0.048, 0.057] | 0 (JM-basic) |
| (i) | 3 | 2:.0144 3:.0215 4:.0258 5:.0286 6:.0306 | 0.0416 [0.0413, 0.0421] | 1/24 |
| (iii) raw generators | 3 | t=1–3: 0 | – | – |
| (iv) | 3 | t=1–3: 0 (LP upper also 0) | – | – |
| (i) | 4 | t=1: 0 | – | 1/80 |

LP relaxations that overshoot (not ceilings): (ii) m=2 t=12: 0.2004; (iii) raw generators m=2 t=4: 0.304 (exact value 0); (iii) Gröbner generators t=5: 0.162.

Notes: (vi) extrapolates above its JM-basic asymptote 0 because optimal shift sets beat JM-basic for this support; it is still a third of the (i) value, and its finite values come from the LP, which could overshoot for this non-box support. (ii) and (iii)-Gröbner sit above (i) at equal t (t=3: 0.1308 vs 0.1189), with smaller lattices (dim 28 vs 49), and converge to the same 1/6.

### Table 3. Planted recovery, m=2, t=3 (successes/trials)
(i) x-coordinates, dim 49, finite-t cert 0.119:
| bits | 0.10/0.109 | 0.119/0.12 | 0.129/0.13 | 0.14 | 0.15 | 0.16 |
|---|---|---|---|---|---|---|
| 64 | 20/20 | 20/20 | | 13/20 | 0/20 | |
| 72 | | | 10/10 | 7/10 | 2/10 | 0/10 |
| 96 | 20/20 | 20/20 | | 5/20 | 0/20 | |
| 128 | 20/20 | 20/20 | 20/20 | 1/20 | 0/20 | |

(ii) Vieta (e1, e2), bounds (2B, B^2), dim 28, finite-t cert 0.1308:
| bits | 0.12/0.121 | 0.13/0.131 | 0.14/0.141 | 0.15 | 0.16–0.18 |
|---|---|---|---|---|---|
| 64 | 20/20 | 20/20 | 8/20 | 1/20 | |
| 72 | 10/10 | | 4/10 | 1/10 | 0/10, 0/10 |
| 96 | 20/20 | 20/20 | 1/20 | 0/20 | |
| 128 | 20/20 | 20/20 | 0/20 | 0/20 | |
Additional (ii) point: 120-bit, t=6, dim 91, delta 0.14: 6/6.

At the certificate the heuristic succeeds 20/20 at every bit size for both presentations. Above it, recovery collapses within about 0.01–0.02: at 128 bits (ii) goes 20/20 at cert to 0/20 at cert+0.01; (i) is 20/20 at cert+0.01 and 1/20 at cert+0.021. The heuristic matches the finite-t certificate to within about 0.01. Figure: ceilings_m2_m3.png; numbers in ceilings_table.csv.

## Verdict reasoning
Frozen criterion. Success: certified reach ≥ 1/4 at m=3 or ≥ 1/5 at m=4, confirmed by planted recovery. Kill: all certified bounds within 0.005 of 1/6, 1/24, 1/80.

Success fails: at m=3 the best certified value is 0.0306 (finite t), asymptote 1/24 for (i) and (ii); (iii) and (iv) give 0 where (i) gives 0.0215. At m=4, (i), (ii) and (v) are exactly 0.0125.

Kill holds for (i), (ii) and (v) at every m, and for (iii) and (iv) at m=2: (iii) is exactly (ii) by Gröbner, (iv) is exactly (i), and (iii)-Gröbner extrapolates to 0.1652 (its LOO spread ±0.006 just exceeds the tolerance).

Kill is not established in three places:
(a) (iii) and (iv) at m=3,4 have only t ≤ 3 data (all 0) and no asymptotic certificate. The m=3 Gröbner check (elimination ideal = Vieta S_4) supports the prereg's resultant mechanism but does not certify the lattice class with a full-size a_2 inside it.
(b) (vi) certifies far below the single-polynomial value (about 0.05 vs 1/6 at m=2; 0 under JM-basic), outside "within 0.005" in the downward direction.
(c) The certificates come from substitute tools, not cuso, the sumset calculator or the 2026 LP.

Reading "within 0.005" as "not above" would make this KILL; the prereg forbids that reinterpretation, so the verdict is INCONCLUSIVE. The direction is unambiguous: no presentation improves on the single-polynomial reach in any cell computed. The prediction holds for (i), (ii), (v), and for (iii), (iv) at m=2; it is false for (vi), which is strictly worse.

## Limitations
- Substitute tooling (DEVIATIONS 2–4). The MILP is exact only within its lattice class: single monomial order, product-of-powers shifts, down-closed M. Asymptotic values are JM-basic lower bounds on optimal-shift reach; the (vi) finite-t numbers show the gap can be real. The ceiling side rests on a loose LP relaxation for non-box supports and on the convergence of exact finite-t values to the analytic value.
- m=4 lattice computations reached t=1 only; m=4 numbers are analytic or cited from SA-06.
- (iii) and (iv) at m ≥ 3 are limited to t ≤ 3: full-size auxiliary unknowns make the grids large, and at small t they give 0.
- Planted tests are m=2 only, toy scale (64–128-bit p, dim ≤ 49 at t=3), LLL rather than flatter. Recovery is shown in principle (two independent vanishing polynomials); the root was not solved for.
- (ii) m=2 MILP values at t ≥ 8 hit the 60 s limit, so they are lower bounds. The analytic 1/6 and SA-02's continuum optimisation (cont_vieta2.py: 0.16667) fix the asymptote.
- No result here is a security claim about a deployed curve.

## Suggested lead-atlas update
LEAD-ICP-coppersmith-smallroot-semaev: keep "measured", adding the qualifier "proved for (i), (ii) and 2-torsion-symmetrised (v) under the JM-basic polytope formula". Do not promote to "proved for the automated-shift class": cuso, the sumset calculator and the 2026 LP were not run, and (iii)/(iv) at m ≥ 3 were not certified asymptotically. Record: the Vieta graded box gives exactly 1/6, 1/24, 1/80 (the m! volume saving is cancelled by the graded bounds); the norm system is the Vieta conic at m=2 and its elimination ideal is Vieta S_4 at m=3; chained S_3 and the norm system certify 0 at m=3 for t ≤ 3 (S_4 in x: 0.0215); the integer lift is strictly worse (about 0.05 vs 1/6 at m=2); planted LLL recovery matches the finite-t certificate within 0.01 at 64–128 bits. next_action: run cuso or a correct non-relaxed upper-bound LP on (iii) and (iv) at m=3 only if a new presentation mechanism is proposed; otherwise close the lead. Deciding number: best m=3 value 0.0306 vs success line 0.25.
