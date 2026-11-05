# SA-01 deviations

1. **Interrupted and resumed by a different model.** The first executor was cut off by an API usage limit after about one hour (last output 05:32). A second executor (Claude Opus 5.5) resumed on 2026-11-05 from the saved files under /home/user/semaev-runs/RESUME_BRIEF.md. It reused every finished output (`ceil_*`, `ceilL_*`, `M_*`, `plant_*` at 64/72/96 bits) without rerunning it, and added: `analytic_reach.py`, `check_iii_m3_elim.py`, `cert_t3_m2.log`, `M_iv_m3*`, `M_iii_m3*`, `plant_*128*`, `finalize2.py`, the table, the figure and this report. The first executor left no notes, so its intentions were reconstructed from its code.

2. **No cuso, sumset calculator, Ehrhart check or ePrint 2026/1027 LP.** None of these tools was installed. The first executor downloaded `flatter-0.0.3.tar.gz` (1.7 kB, a stub, never built). It wrote its own shift-set optimiser in their place:
   - `coppersmith_lp.py` and `model.py`: an exact MILP over down-closed monomial sets M with optimal per-monomial shift levels, for lattices spanned by p^{t-|k|} x^s prod g_i^{k_i}. It also has an LP relaxation of the same problem.
   - `analytic_reach.py` (new): the weighted Newton-polytope formula from SA-06, delta = 1/((n+1) sum_j w_j g_j).

   These are substitutes. They are not the named 2023-2026 tools. The "certificate" here therefore means two things: an exact MILP optimum at finite t for this lattice class, and the JM-basic asymptotic formula. It does not mean a cuso or sumset certificate. LLL is fpylll, not flatter.

3. **Ehrhart cross-check replaced.** Instead of the Ehrhart quasi-polynomial check, the finite-t exact values are compared with the analytic asymptote. The fit is D - a/t - b/t^2 with leave-one-out spread.

4. **The LP relaxation is not a valid ceiling.** For non-box supports it overshoots the true optimum. Examples: (ii) m=2 t=12 gives LP 0.2004 against MILP 0.1540, and (iii) raw m=2 gives LP 0.30 against MILP 0. The cause is fractional double counting when closures of different levels are not nested (see the `model.py` docstring). Only MILP values and box-support LP values are reported as certified. For box supports, LP = MILP was checked (`M_i_m3`).

5. **Presentation (v).** The prereg's 2-torsion-symmetrised presentation in invariant u-variables was done in SA-06 and is cited from there (1/6, 1/24, 1/80 in all cells). Here (v) is computed only as the naive product S(x,xR)·S(x,xR+T) in x, with per-variable degree 2d. It is a control, not the prereg presentation.

6. **Scale reached.** Exact MILP runs reached these levels:
   - m=2: up to t=16 for (i), 12 for (ii), 5 for (iii), 6 for (iv)-(vi).
   - m=3: t ≤ 6 for (i) and t ≤ 3 for (iii) and (iv).
   - m=4: t=1 only, for (i).

   (iii) at m=4 and (iv) at m=4 were not run because the grid sizes are too large for the time budget. (ii) m=3,4 and (vi) m=3,4 have the analytic value only.

7. **Planted runs cover m=2 only.** They used (i) and (ii) at t=3 with 64, 96 and 128-bit p, 20 trials per delta. At m=3 and m=4 the certified finite-t delta is at most 0.03. That puts the root bound at 2^2-2^4 at these sizes, so a planted test there is meaningless. 72-bit runs used 10 trials. A later rerun at 72 bits crashed ("monomial outside M") and was discarded; the earlier 72-bit JSON is kept. The 64/96-bit grids used deltas {0.10..0.15}, not exactly cert ± 0.01. The 128-bit runs use exactly cert-0.01, cert and cert+0.01.

8. **Planted success test.** Success means that at least two LLL output polynomials vanish over Z at the planted root and have a nonzero resultant. That is recovery in principle. The root was not extracted by solving the resultant.

9. The Write tool refused REPORT.md for this resumed executor. Per RESUME_BRIEF, the full report text was returned in the final message for the main session to save as REPORT.md; it was not worked around.
