# SA-01b REPORT: certified ceilings, m = 3 norm/chained presentations and m = 4 lattices

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary
**INCONCLUSIVE against the frozen criterion, leaning KILL.** SUCCESS fails clearly. KILL cannot be declared in the frozen words: it needs a finite-t sequence with a leave-one-out range inside the band. (iii)-Groebner has three points, the last one a Vieta bound. (iv)-Groebner's three-parameter leave-one-out range reaches 0.0474, which is 0.0007 above the band.

Deciding numbers (m = 3, band = 1/24 ± 0.005 = [0.0367, 0.0467]):
- (iii)-Groebner: t=2,3 computed 0.0193, 0.0254; t=4 Vieta bound 0.0275. Fit D−a/t: 0.0361 (LOO 0.0341–0.0374). Only 3 points.
- (iv)-Groebner (chain ideal: S_4 plus a u-linear element): t=2,3 computed 0.0169, 0.0234; t=4..6 taken from (i). Fit D−a/t−b/t²: 0.0392 (LOO 0.0365–0.0474). Fit D−a/t: 0.0366 (0.0358–0.0373).
- (iv) raw chained S_3 (u full size): the LP ceiling is below 0.002 for t=1..4. The LP ratio at δ=0.002 is 0.15, 0.33, 0.46, 0.54 (feasible only above 1).
- (i) at m=4: t=1,2,3 give 0, 0.002455, 0.004804 (asymptote 1/80 = 0.0125). At t=2,3 this is 20% and 38% of the asymptote, against 34% and 52% at m=3.

## What was run
1. Tool attempt (protocol step 1): `pip install cuso` and `pip download cuso` found no distribution; artifacts.iacr.org/eurocrypt/2025/a13 answers HTTP 301; a fetch of the artifact page and a pip install from git were blocked by the session permission classifier and not worked around. Fallback per protocol: the SA-01 shift-set MILP/LP (model.py, coppersmith_lp.py) extended in t, on Groebner generators.
2. Groebner generators (sympy, lex, mod 1000003): `gb_iii_m3.py` repeats SA-01's m=3 norm system — 10 elements: one linear in a1, nine in (a2,e1,e2,e3) with a2 up to degree 3, and the 35-term Vieta S_4 as the only e-only element. `gb_iv_m3.py` does the chain {S_3(x1,x2,u), S_3(u,x3,xR)} — 8 elements: the two inputs, five u-linear elements of 223–315 terms, and the 125-term S_4(x).
3. (iii) m=3: `iiiG_m3.py` (a1 eliminated, a2 full size, e_k of size p^(kδ)). (ii) Vieta alone: `run_model.py`, `run_model2.py` for t=1..4. (iv): `ivG_m3.py`, `probe.py`. Fits and figure: `fits.py`, `fig.py`.
4. (i) m=4: `i_m4.py` (full LP, t=2) and `i_m4_sym.py` (S_4-orbit-reduced LP, t=2,3).
5. Planted recovery was not run (DEVIATIONS 8).

## Results
Certified δ at finite t (exact MILP, or box LP = MILP). Full table in round2_table.csv; figure ceilings_round2.png.

| presentation, m=3 | t=1 | t=2 | t=3 | t=4 | t=5 | t=6 |
|---|---|---|---|---|---|---|
| (i) S_4 in x (SA-01) | 0 | .01436 | .02153 | .02578 | .02856 | .03062 |
| (ii) Vieta, graded bounds | 0 | .01851 | .02491 | .02755 (LB) | | |
| (iii)-Groebner (a2 full size) | .00564 | .01932 | .02536 | .02755 (Vieta bound) | | |
| (iv)-Groebner (S_4 + u-linear element) | | .01691 | .02341 | .02578 ((i)) | .02856 ((i)) | .03062 ((i)) |
| (iv) raw chain, LP ceiling | 0 | 0 | 0 | 0 | | |

| (i), m=4 | t=1 | t=2 | t=3 |
|---|---|---|---|
| reach | 0 | .002455 | .004804 |

Extrapolations (SA-01 convention, leave-one-out range in brackets):

| series | D−a/t−b/t² | D−a/t | vs band [.0367,.0467] |
|---|---|---|---|
| (i) m=3, t=2..6 | .0416 [.0413,.0421] | .0382 [.0376,.0395] | inside |
| (ii) m=3, t=2..4 | 3 points, exact fit | .0368 [.0355,.0377] | partly below, none above |
| (iii)-G m=3, t=2..4 | 3 points | .0361 [.0341,.0374] | below or inside |
| (iv)-G m=3, t=2..6 | .0392 [.0365,.0474] | .0366 [.0358,.0373] | 3-parameter LOO upper end 0.0007 above |
| (i) m=4, t=2..3 | not fittable | | |

Observations:
- Adding the a2 equations to Vieta helps at small t, and the gain shrinks: +4.4% over (ii) at t=2 (0.01932 vs 0.01851, via generators 7 or 8 with Vieta) and +1.8% at t=3 (0.02536 vs 0.02491). Generators 1–6 add nothing at t=2.
- Adding the u-linear chain element to S_4 raises (iv) from 0.0144 to 0.0169 at t=2 and from 0.0215 to 0.0234 at t=3. Both stay below (ii).
- Raw chained S_3 with a full-size u certifies 0 while S_4(x) gives .0144 at t=2. S_4 and the u-rational elements are in the ideal, but the raw generators do not expose them at low t.
- Sanity checks: the symmetrised and full LP agree to 8 digits at m=4, t=2 (ratio 0.39283533). The symmetrised LP at m=3, t=3 gives .02162 against SA-01's .02153.

## Verdict reasoning
- SUCCESS: no. The maxima are 0.0306 and 0.0048 against 0.0467 and 0.0145, so planted confirmation is moot.
- KILL needs both (iii) and (iv) at m=3 to have an extrapolation within 0.005 of 1/24 or below, with the leave-one-out range inside the band. (iii): the extrapolation 0.0361 is in the band, but it rests on 3 points and a 2-parameter fit, and the third point is a bound from (ii). (iv): the 2-parameter fit is inside the band; the 3-parameter fit that SA-01 used has an LOO maximum of 0.0474, outside by 0.0007.
- Every computed value is below the single-polynomial limit. No presentation is above the (i)/(ii) curves by more than 4.4%, and the gain shrinks with t.

What would decide it:
- KILL proper: compute (iii)-Groebner and (iv)-Groebner (not bound them) to t=5 or 6 at m=3. That needs an LP that fits in 1.5 GB at dimension about 3e4–1e5 (a structure-reduced LP, or cuso/the sumset calculator). Alternatively, prove that the a2 and u elements cannot raise the Newton-polytope value above the Vieta / S_4 value. A sketch exists (they only add constraints inconsistent with the cost vector (1, kδ)); it is not proved.
- m=4: (i) to t≥4 with a leaner orbit builder, then (ii)/(iii) at t≥3.

## Limitations
- Substitute tooling, one leading-monomial choice, product-of-powers shifts. This is not a theorem about all Coppersmith-style lattices.
- (iii) t=4 and (iv) t=4..6 are lower bounds from sub-presentations, not runs of those presentations. (iii)-G used generator subsets {8,9} at t=3. The full basis ran only to t=2 and was OOM-killed at t=3.
- (ii) t=4 is a 60 s MILP lower bound (LP upper 0.0314).
- (iv) raw: the ceiling below 0.002 holds at t≤4 only. At t=5 the LP did not finish in 480 s. "Stays 0" is a fit of the ratios (limit about 0.8), not a bound.
- m=4: two points, no extrapolation. The t=4 build ran out of memory.
- No planted recovery this round. m=3 deltas below 0.031 give roots of 2–3 bits at 64/96-bit p, and the t=2,3 lattices have dimension 2.7k–10.8k.
- Memory: several failed attempts exceeded the 1.5 GB guideline (ulimit 2.5–3 GB, one OOM kill). Successful runs stayed under 1 GB.
- No security claim about any deployed curve.

## Suggested lead-atlas update
LEAD-ICP-coppersmith-smallroot-semaev: keep "measured". At m=3 the Groebner-form norm system and the chain ideal certify only 1.8–4.4% above the Vieta / S_4 value at t=2,3 (0.0254 vs 0.0249; 0.0234 vs 0.0215); the gain shrinks in t, and the extrapolated limit is 0.036–0.039 against 1/24 = 0.0417. Raw chained S_3 certifies 0 (LP ceiling < 0.002, t≤4). (i) at m=4 reaches 0.0048 at t=3 against 1/80. Do not upgrade to KILL for (iii)/(iv): they are 3-point series. next_action: close the lead unless cuso or a reduced LP is available; if one is, compute the (iii)/(iv) Groebner series to t=5–6 at m=3 and (i) at m=4 to t=4–5. Deciding number: best m=3 value 0.0306 (t=6) against success line 0.0467.
