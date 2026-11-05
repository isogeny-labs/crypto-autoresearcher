# SA-04 REPORT: Riemann–Roch norm presentation with graded smallness (Diem II over F_p)

(Saved by the main session verbatim from the resumed executor's final message; the harness refused the executor's own write.)

## Summary

**Verdict: KILL against the frozen criterion** ("Kill: equal reach and degree growing with B").

- **Reach is equal.** After α is eliminated, the norm system becomes a single relation F(e_1..e_m) = 0. Its weighted Newton polytope (weights w_k = k for e_k ≤ C(m,k)B^k) has JM-basic reach of exactly **1/6, 1/24 and 1/80 at m = 2, 3, 4** under the SA-06 centroid formula. These are the S_{m+1} single-polynomial values to within 4e-16. The first session's extrapolated determinant sums give the same result (0.16665, 0.04159, 0.01245). Planted LLL at m = 2 (96/128-bit p) shows the Vieta-conic lattice is no better than the S_3 lattice at any finite level, and slightly worse.
- **The degree grows with B at m = 3.** msolve F4 max degree for the un-eliminated norm system in the digit presentation is **5, 6, 7 at B = 4, 8, 16**, which is s + 3 with s = log2 B. With the vanishing-polynomial base it is **10, 18, 34 at B = 8, 16, 32**, which is B + 2. At m = 2 it is 3 + ⌊s/2⌋ for B = 4..128 (6 doublings) and B + 1 for B = 8..128.
- The prediction's secondary claim holds. The un-eliminated system has a lower solving degree than the eliminated S_{m+1}: by one at m = 2 (3+⌊s/2⌋ against 4+⌊s/2⌋), and with a slope three times smaller at m = 3 (s+3 against 3s+1). The degree is still not bounded, and at this scale the lower degree does not turn into a cheaper solve (Table 3).

## What was run

Two sessions. The first (Sonnet, interrupted) produced part (a) and the Macaulay-engine sweeps. The second (Opus 5.5) added the msolve part (b), the exact reach formula, known-answer checks and this report.

| script | purpose |
|---|---|
| `scripts/nsys.py`, `scripts/build.py` | Riemann–Roch norm system: f = h_{m+1} + Σ α_k h_k ∈ L((m+1)O − (−R)), N(f)/(X − x_R) gives e_k = Q_k(α) (quadratic in α). Planted instances with x_i ≤ B on random curves. Presentations: digit (x_i = Σ 2^j b_ij, b² = b), vanishing base (Π_{t=1..B}(x_i − t)), S_{m+1} baselines on the same kind of planted instance, and a curve-free null in which Q_k is replaced by a random quadratic in α. |
| `scripts/vieta_rel.py` | eliminates α exactly: kernel computation of F(e_1..e_m), total degree 2, 4, 8 at m = 2, 3, 4 → `out/vieta_support.json` |
| `scripts/jm.py`, `reach_run.py`, `reach_m4.py` | first session: JM determinant sums for k = 1..12 extrapolated in 1/k → `out/reach_results.json`, `out/reach_m4_k6.json` |
| `scripts/reach_formula.py` | new: exact JM-basic reach δ = 1/((n+1) Σ w_i g_i), g the centroid of Newt(F) (formula from SA-06) → `out/reach_formula.json` |
| `scripts/planted_lll.py` | first session: planted fpylll LLL at m = 2, S_3 against the Vieta conic → `out/lll_planted.jsonl` |
| `scripts/ms_sweep.py` | new: msolve 0.10.1 `-g 2 -v 2 -t 1`; degree = max "deg" in the F4 round table (same parse as SA-14) → `out/ms/*.jsonl` |
| `scripts/ms_check.py` | new: known-answer check; every element of msolve's reduced GB must vanish at the planted point → `out/ms/planted_gb_check.json` |
| `scripts/ms_summary.py` | tables, slopes, figure → `out/ms/msolve_table.md`, `out/ms/msolve_summary.json`, `out/ms/fig_msolve_degree.png` |
| `scripts/macaulay.py`, `sweep.py`, `summarize.py` | first session: hand-built dense Macaulay engine (full-Macaulay degree D_sol) → `out/dsol_tables.md`, `out/fig_dsol.png` |

Instances: p = nextprime(8·B^m). 2–3 seeds per cell; every seed gave the same degree in every cell.

## Results

### Table 1. Part (a): asymptotic JM-basic reach, eliminated norm relation F(e) vs single polynomial S_{m+1}

| m | support of F (monomials) | max weighted degree Σ k·a_k | δ norm/Vieta (exact centroid) | δ norm (first session, extrapolated) | δ S_{m+1} box | difference |
|---|---|---|---|---|---|---|
| 2 | 6 | 4 | 0.166667 = 1/6 | 0.16665 | 1/6 | 0 |
| 3 | 35 | 12 | 0.041667 = 1/24 | 0.04159 | 1/24 | −1e-17 |
| 4 | 495 | 32 | 0.012500 = 1/80 | 0.01245 | 1/80 | −4e-16 |

Newt(F) is the full weighted simplex {Σ k·a_k ≤ m·2^{m−1}}. With weights 1..m its weighted centroid gives the same value as the box [0, 2^{m−1}]^m with unit weights, so graded smallness buys nothing over the single polynomial for this lattice family.

Planted check, m = 2 (`out/lll_planted.jsonl`, 12–16 trials per point), success S_3 / Vieta conic:

| level | δ (p bits) | success |
|---|---|---|
| k = 2 | 0.12 (96) | 13/16 vs 8/16 |
| k = 3 | 0.14 (96) | 5/16 vs 1/16 |
| k = 3 | 0.14 (128) | 3/16 vs 0/16 |
| k = 4 | 0.14 (128) | 12/12 vs 10/12 |

Both lattices fail at δ ≥ 0.15–0.16, below the 1/6 asymptote. The conic is never better.

### Table 2. Part (b): msolve F4 max degree (grevlex, 1 thread); s = log2 B

| system | B = 4 | 8 | 16 | 32 | 64 | 128 | closed form |
|---|---|---|---|---|---|---|---|
| m=2 norm (RR), digit | 4 | 4 | 5 | 5 | 6 | 6 (63 s) | 3 + ⌊s/2⌋ |
| m=2 norm digit, curve-free null | 4 | 4 | 5 | 5 | 6 | 6 | 3 + ⌊s/2⌋ |
| m=2 S_3, digit | 5 | 5 | 6 | 6 | 7 | 7 (101 s) | 4 + ⌊s/2⌋ (repository digit formula reproduced) |
| m=2 norm + vanishing | – | 9 | 17 | 33 | 65 | 129 | B + 1 |
| m=2 S_3 + vanishing | – | 10 | 18 | 34 | 66 | 130 | B + 2 |
| **m=3 norm (RR), digit** | **5** | **6** | **7** (124 s) | timeout 250 s | – | – | s + 3 |
| m=3 norm digit, curve-free null | 5 | 6 | 7 | – | – | – | s + 3 |
| m=3 S_4, digit | 7 | 10 | 13 (70 s) | timeout 200 s | – | – | 3s + 1 |
| **m=3 norm + vanishing** | – | **10** | **18** | **34** | timeout 120 s | – | B + 2 |
| m=3 S_4 + vanishing | – | 16 | 24 | 40 | timeout 120 s | – | B + 8 |

Least-squares slope of degree vs s: m = 2 norm digit 0.457 per bit (6 points); m = 3 norm digit 1.00 per bit (3 points); m = 3 S_4 digit 3.00 per bit (3 points). Figure: `out/ms/fig_msolve_degree.png`.

Known-answer checks: 12/12 instances passed (m = 2, 3; digit, S, V, SV and null), every reduced-GB element vanishing at the planted point. No GB was {1}.

### Table 3. Cost at m = 3, digit (largest F4 matrix rows × columns, time)

| B | norm (RR) | S_4 |
|---|---|---|
| 4 | 792 × 655, 0.03 s | 267 × 219, 0.01 s |
| 8 | 5155 × 5583, 0.5 s | 2592 × 2734, 0.2 s |
| 16 | 47521 × 47696, 124 s | 26698 × 27855, 70 s |

The norm system has a lower degree but larger matrices and runs slower at every B reached, because it has m − 1 more variables. The ratio narrows from about 3× to about 1.8× in matrix area, not enough to call a crossover.

### Secondary: full-Macaulay degree D_sol (first session, `out/dsol_tables.md`)

| system | values | form |
|---|---|---|
| m=2 norm digit | 4, 6, 8, 10 at B = 2..16 | 2s + 2 |
| m=2 S_3 digit | 3, 7, 9, 11, 13 at B = 2..32 | — |
| m=2 norm V | 2B | — |
| m=2 S_3 V | 2B + 1 | — |
| m=3 norm digit | 10 at B = 4 | — |
| m=3 S_4 digit | 11, 17 at B = 4, 8 | — |
| m=3 S_4 V | 3B + 8 | — |

Same ordering as msolve. This is a different, larger quantity than the F4 degree and is not mixed into the verdict.

## Verdict reasoning

Neither success route holds.
1. Certified reach above the single-polynomial value: the weighted-polytope reach of the eliminated system equals 1/6, 1/24, 1/80 exactly; planted LLL at m = 2 agrees (conic equal or worse).
2. Solving degree bounded in B at m = 3: the F4 degree increases at every doubling measured (5 → 6 → 7 digit; 10 → 18 → 34 vanishing base).

The curve-free null gives exactly the same degrees at m = 2 and m = 3, so the degree behaviour is generic to "m quadratic-in-α equations + digit-coded symmetric functions" and owes nothing to the curve. Both halves of the kill condition hold: equal reach and degree growing with B. Verdict: KILL.

The prediction is confirmed in both halves: reach equals S_{m+1}'s (elimination is a resultant and does not shrink the polytope), and the un-eliminated system's degree is lower than the S_{m+1} digit presentation (3 + ⌊s/2⌋ vs 4 + ⌊s/2⌋ at m = 2; s + 3 vs 3s + 1 at m = 3), a constant-or-slope improvement that does not bound the degree. At toy scale the extra full-size α variables make the F4 run slower.

## Limitations

- Small scale at m = 3: the digit cell reached B = 16 (3 points), the vanishing cell B = 32. B = 32 digit and B = 64 vanishing timed out or would have exceeded the ~700 MB rule. The m = 3 slope is an exact fit to 3 points, not a CI over 4 doublings; growth is a strictly increasing integer sequence, identical on every seed and on the null.
- The vanishing-polynomial base forces degree ≥ B for any solver; only the digit cell is informative about "bounded in B", and there the degree grows like log B.
- Part (a) is the JM-basic (automated convex-shift) bound, not a strategy-independent certificate. The lattice keeping full-size α as unknowns was argued, not computed, to be no better (deviation 3).
- Comparison with the PKM tower's d_F is indirect (tower parametrised by level t; SA-14 measured 4,4,4,4,4,5,5,5,5 for t = 1..9 with the same msolve binary).
- Small primes (p ≈ 8B^m) keep planted instances near-unique. Toy-scale measurements on the shared campaign host; no security claim.

## Suggested lead-atlas update

On LEAD-ICP-shared-coefficient-membership (cross-reference LEAD-ICP-coppersmith-smallroot-semaev): the Riemann–Roch norm presentation with graded smallness has the same JM-basic lattice reach as S_{m+1} (exactly 1/6, 1/24, 1/80 at m = 2, 3, 4); its un-eliminated msolve F4 degree is lower than the Semaev digit presentation (m = 3: s + 3 vs 3s + 1; m = 2: 3 + ⌊s/2⌋ vs 4 + ⌊s/2⌋) but still grows with B (m = 3: 5, 6, 7 at B = 4, 8, 16). Disposition: killed as an exponent-changing route under the frozen criterion. Keep one solver-engineering next_action: test whether the lower slope (1 vs 3 per bit at m = 3) gives a matrix-size crossover against S_4 at B ≥ 32; matrices are still 1.8× larger at B = 16.
