# SA-14: Extending Yokoyama et al. to compositional (tower) bases

## Summary

**Verdict: INCONCLUSIVE against the frozen criterion** ("theorem with explicit c, or a family with bounded degree"). No unconditional theorem with c > 0 for the F4/Gröbner solving degree was obtained, and no bounded-degree family was found. What was obtained: (i) a rigorous, numerically verified exact theorem for the *Macaulay (XL) degree* of Kummer-tower Semaev systems, slope c_XL = m(q-1) per level (2 for m = 2, q = 2), (ii) an independent msolve measurement of the *F4* degree, 4,4,4,4,4,5,5,5,5 for t = 1..9 (q = 2, m = 2), which reproduces the repository's pattern 4 + floor((t-2)/4) for t >= 2, but with a single step so it cannot separate c = 1/4 from c = 0.18 or from a bounded plateau, (iii) a clear statement of why (i) does not imply anything about (ii): Gröbner/F4 behaves like polynomial calculus, whose degree can be far below the Nullstellensatz/Macaulay degree, and the gap is exactly gap A4/H_T.

Deciding numbers: Macaulay degree 2t+4 exactly (q = 2, S nowhere zero, t = 1..8, 24/24 instances, DFT computation) versus F4 degree 4 -> 5 at t = 6, still 5 at t = 9 (msolve, 3 seeds each t <= 7).

I could not read the Yokoyama et al. full text (publisher returned 405; only the abstract was reachable), so the "extension" below is built from the abstract's statement (GB computation as an extension of the extended Euclidean algorithm, lower bound via linear algebra under statistical assumptions on S_m), not by re-running their proof. The repository file RESEARCH_ALGEBRAIC_IC_LOWER_BOUND.md was not available either, so the "slope bar (m-1)/2" is quoted from the prereg only; I add my own break-even computation below, clearly labelled.

## What was run

All in /home/user/semaev-runs/SA-14/. Family: Kummer tower, m = 2 summands (S_3 with fixed x_R), V_t = mu_{q^t} in F_p, my own encoding (DEVIATIONS.md item 1). Planted instances (x_R = x(P1+P2) with x(P_i) in V) and unplanted ones (S nowhere zero on V^2), random curves.

| script | what |
|---|---|
| `msolve_sd.py`, `run_msolve.py`, `run_msolve_b.py`, `fit_f4.py` | F4 solving degree = max round degree of `msolve -g 2 -v 2 -t 1` |
| `exact_unplanted.py` | exact Macaulay degree of the inconsistent system as 4 + delta(1/S), by 2D DFT over F_p (t <= 8, q = 2; t <= 4, q = 3) |
| `macaulay.py` | independent dense Macaulay-matrix computation (n <= 6 variables) |
| `kummer_sd.py`, `run_all.py`, `fit_fig.py` | Singular Buchberger with degBound sweep (a third, different quantity) incl. a random same-support null |
| `breakeven.py` | my own break-even slope calculation |

Raw outputs: `out/*.txt`, `out/*.json`. Figures: `fig_f4_degree.png`, `fig_slope.png`.

## Results

### F4 degree (msolve), q = 2, m = 2, p = 12289

| t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| F4 degree (planted, median of 3; t=8,9: 1 seed) | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 5 |
| F4 degree (no solution, 2 seeds; t=8: 1) | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | n/a |
| repo medians (lead YAML) | 3 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 5 |
| max matrix rows (planted) | 7 | 35 | 147 | 357 | 892 | 2803 | 6354 | 11138 | 23644 |

Seeds agree exactly (no variance seen). Planted and unplanted give the same degree, as the repository's null comparison also found. q = 3: 5,5,5,6,6 (t = 1..5 planted), 5,5,5,6 (no solution, t = 1..4). OLS slope over t = 1..9 (see `out/f4_summary.json`) is about 0.17 (q = 2) and 0.30 (q = 3), each from one step, so these are not estimates with a meaningful CI. Max matrix rows grow like t^5 (x31 from t = 4 to 8, 2^5 = 32), i.e. polynomial in t at fixed degree 5. t = 9 took 412 s and 23644 rows at degree 5 (rows x2.1 per level now).

### Macaulay (XL) degree: exact formula, rigorous

Let T be the tower ideal, A = F[x_i, w_ij]. Hypothesis (G): the generators w_j - L_j(w_{j-1}) have deg L_j = q_j >= 2.

- **Prop 1 (proved).** Leading terms in grevlex are the pure powers w_{j-1}^{q_j}, pairwise coprime, so T is a Gröbner basis (Buchberger's first criterion). A/T has a basis of standard monomials of top degree m·Sum(q_j - 1) (= m t (q-1) for Kummer). When the roots are distinct and in F_p, A/T = Functions(V^m), and for Kummer the standard monomial prod w_j^{e_j} is the character x^k with k = Sum e_j q^j, so degree = q-ary digit sum of k: Fun(V) = F_p[Z/q^t] filtered by digit sum. Reductions mod T never raise degree.
- **Prop 2 (proved).** Macaulay degree D_Mac(T+S) <= m·Sum(q_j-1) + deg S. Proof: write f = t + S h, reduce h mod T, and use that T cap A_{<=D} is spanned by multiples of the generators (GB property).
- **Prop 3 (proved).** If S has no zero on V^m, then D_Mac = deg S + delta(1/S), where delta is the filtration (digit-sum) degree of the function 1/S on V^m. Proof: A is a domain so deg(hS) = deg h + deg S, and deg NF(h) <= deg h gives the lower bound; the NF representative gives the upper bound.
- **Prop 4 (proved under hypothesis R, "S|V^m is a uniformly random function with values in F_p^*").** delta(1/S) = top degree except with probability <= 1/(p-1) (1/S lies in a proper hyperplane of Fun(V^m)). Hence D_Mac = deg S + m·Sum(q_j-1) w.h.p., so **c_XL = m·mean(q_j - 1) >= m for every tower with all q_j >= 2**. For consistent systems with z zeros the same union-bound argument (sketched, not written out) gives D_Mac >= deg S + top - r where r is the number of top-degree layers containing fewer than z+1 monomials in total.
- R is false as a statement (S has degree 4 in x), so Prop 4 is a heuristic transfer. For the real S the claim "top coefficient of 1/S is nonzero" is an arithmetic non-vanishing in F_p; I checked it **exactly** (not statistically) for 24 instances, all with delta = top (`out/exact_unplanted.json`, `out/exact_log.txt`): q = 2, t = 1..8, 3 seeds each, D = 2t+4; q = 3, t = 1..4, D = 4t+4. Independent Macaulay-matrix computation (`macaulay.py`) gave 6 and 8 for t = 1, 2 unplanted (matches), and planted t = 1,2,3 gave 5, 7, 9 (planted is 1 below the formula, consistent with the z = 2 correction of Prop 4's sketch).
- Remark (proved, trivial): R genuinely needs a hypothesis, since S = x1^{N-1} x2^{N-1} (a unit with inverse x1 x2) has delta(1/S) = 2, so a bounded Macaulay degree exists for an abstract S. This does not occur for Semaev S_3, but shows what a proof would have to exclude.

### Why this does not decide F4

D_F4 <= D_Mac always (F4 matrices are submatrices of the Macaulay matrix), and strictly less is possible because F4 multiplies *derived* low-degree polynomials (degree falls), which is polynomial calculus, not Nullstellensatz. The data show it: Macaulay 2t+4 (6..20) against F4 4..5. So Props 2-4 prove c_XL = 2 and say nothing for c_F4. The Yokoyama picture (GB = extended Euclid) is exactly an argument that F4 can do better than Macaulay by elimination in stages, and a lower bound for F4 on towers would have to be a polynomial-calculus degree lower bound for the tower + S system. I do not have one. Singular's Buchberger-with-degBound gave an inflated 5,8,9,11,15,18 (slope about 2.5) which is a sugar-degree artefact and not the F4 degree; it is reported in `out/sd_rows.json` only as a cross-check of the Macaulay slope.

### Break-even slope (my own computation, `breakeven.py`)

Model: dense F4 cost C(n+D, D)^omega with n = m t variables, D = c t, against rho = sqrt(p) = q^{m t/2}. Largest c for which the tower still wins: m = 2: 0.082 (q=2, omega=2), 0.066 (omega=2.37), 0.152 / 0.121 (q = 3); m = 3: 0.123 / 0.099 (q=2), 0.228 / 0.181 (q=3); m = 4: 0.165 / 0.132 (q=2), 0.304 / 0.242 (q=3). So under this crude model a slope of 1/4 loses to rho for q = 2 at m <= 4 and for q = 3 at m <= 3, and wins only at (m = 4, q = 3, omega = 2) where c* = 0.304 > 0.25. Caveats: dense model, ignores sparsity, ignores the cost of getting many relations, and the tower with q^{mt} ~ p points. This is not the repository's bar and is not validated.

## Verdict reasoning

Frozen criterion: theorem with explicit c, or bounded-degree family. Neither was reached for the quantity that matters (F4). The theorem that was reached is about the Macaulay degree and conditional on a randomness/nonvanishing hypothesis that I verified only instance by instance. The prediction "c = 1/4 for Kummer towers" is neither confirmed nor refuted: F4 degrees reproduce the repository's pattern through t = 8 (plateau of 4, step to 5 at t = 6, 5 through t = 9), but with one step. A bounded family is also not excluded by anything here. Therefore INCONCLUSIVE, scale reached t = 9 (q = 2, m = 2) and t = 5 (q = 3).

## Limitations

- Own encoding (DEVIATIONS 1); m = 2 only; one seed at t = 8, 9; t = 10 not run. The next discriminating cell is t = 10 (predicted 6 by 4 + floor((t-2)/4); a plateau at 5 would be evidence for a slower slope or bounded degree).
- No unconditional lower bound on F4/PC degree. Yokoyama et al. full text not read. The repository's A4/H_T document not read.
- Random S hypothesis not proved; the exact check covers only the inconsistent case with fixed small p.
- The break-even calculation is a model, not a measurement.

## Suggested lead-atlas update

LEAD-ICP-pkm-tower-algebraic-oracle (gap A4/H_T): keep disposition open_blocked, but record that (a) the F4 degree pattern 4,4,4,4,4,5,5,5,5 for t = 1..9 is reproduced independently with msolve on my Kummer encoding, matrix rows scale like t^5 at degree 5, so the cost question hinges entirely on whether the degree stays at 5-6; (b) an exact, proved identity D_Mac = deg S + delta(1/S) and, under a verified-per-instance nonvanishing condition, D_Mac = m t (q-1) + deg S, slope 2 for m = 2, q = 2, so XL-type solvers are excluded for towers (c_XL >= m) and only polynomial-calculus-type degree falls could rescue them; (c) next_action: run msolve at t = 10 (q = 2, m = 2; the 11 GiB-scale cells in the repository are not needed for this single cell) and t = 6..7 for q = 3; the deciding number is whether the t = 10 degree equals 6 (slope-1/4 consistent) or 5 (plateau). A PC-degree lower bound, not an XL bound, is the missing theorem.
