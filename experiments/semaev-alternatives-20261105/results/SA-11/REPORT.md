# SA-11 report (saved by the main session verbatim in substance from the executor's hand-back; the executor could not write this file)

## Summary
**Verdict: KILL** against the frozen criterion, for the cavity / replica-symmetric predictor as stated.

## Deciding numbers
- Existing cells within ±1 of measured (25 cells: 15 digit, 10 tower): cavity/RS entropy predictor scores 11/25 (digits 8/15, towers 3/10) against the required 90%. On digits it equals the support-matched null (s + 3) by a short proof, which is the frozen kill condition.
- Tower d_F slope: predictor gives 1.0 per level; measured repo medians (t = 2..10) give 0.233, bootstrap 95% [0.16, 0.33]. About 4× too steep.
- Matched random-CSP null (own Macaulay-closure engine; Kummer towers, m = 2, random coefficients on the same 9-monomial support): d_F equals the real system at t = 2..6 (t = 6: 3/3 vs 3/3, both 5). One real draw at t = 7 also gave 5. The null already matches the real tower degree, so no predictor beats it. The t = 7 null was stopped for time.

## Key findings
- **Cavity degenerates.** The factor graph is one dense factor, so the cavity calculation reduces to a random-energy-model calculation whose only threshold is satisfiability at α = log2 p / n = 1. Sketch only; no 1RSB numerics.
- **α scan contradicts an α-only predictor.** 30 draws with α from 1.03 to 2.5 give constant first fall degree (5, 6, 6 at s = 3, 4, 5). The degree depends on s, not on α, p or the curve.
- **Side result (retrodiction, not counted as success).** ffd = D + (least annihilator degree of the leading form in the graded ring). Proved for unit f; agrees with the closure engine on 53/53 draws. It gives ffd = ⌊s/2⌋ + e/2 + 1 + (m − 1)e with e = 2^(m−1): exactly 4 + ⌊s/2⌋ for m = 2, s ≤ 8, and 13, 13, 14 for m = 3, s = 4..6. All 15 digit cells match. Found after seeing the data; ties the repository's block-factored null by construction. On towers it gives ffd = 4 flat (repository theorem D3 reproduced) and carries no d_F content; a constant 4 also scores 9/10 on tower cells, so the ±1 tolerance is vacuous there.
- **Engine validation.** The closure engine reproduces the repository integers: digits s = 2..5 (d_F = ffd on 33 draws; support null s + 3) and tower d_F = 4, 4, 4, 4, 5 at t = 2..6.
- **Unrun cells.** t = 14 cap 6: the repository's own fit gives d_F = 7, so cap 6 should not refute; the cavity predictor gives 16. The m = 4, N = 20 and m = 3, N = 21 cells are not predicted, because m ≥ 3 towers carry free unknowns the engine does not model.

## Limitations
- Raw tower rows are not in the repository; the prereg's quoted medians were used.
- The tower slope interval bootstraps 9 median points, not draws.
- p below 2^20 throughout.

## Suggested lead-atlas update
- Proposed LEAD-ICE-cavity-solving-degree-predictor: close as negative (11/25 cells; tower slope 1.0 vs 0.233).
- Add a narrow lemma: ffd = D + annihilator degree of the leading form. Not applicable to KN-OPEN-020, which concerns d_F.
- LEAD-ICP-pkm-tower-algebraic-oracle: no change.
