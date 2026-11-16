# SA-13c: the two open proof steps for the modulus-p^2 lattice-query bound

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write. Full proofs are in step_a.md, step_b.md and step_volume.md.)

## Summary
**Verdict: INCONCLUSIVE.** (b) and the 1/15 volume inequality are PROVED; (a)'s classification is PROVED but its coverage bound is FALSE without H-sep (short-lift squares, coverage ~12 ω^{3/10}); the repair (factor-base success + p-independent polynomial schemes) makes H-sep automatic, and Theorem L2 gives Ω(p^{13/15}) completely.

| item | status | number |
|---|---|---|
| (b) branch k* = 1, general q | PROVED: cov_b/cost ≤ K_b (O(1) per unit cost) | measured sup cov_b/Π_J = 3e-4 |
| volume c2 ≤ C_2 ω^{1/15} | PROVED: C_2 = 5·2^{3/5} + 4^{1/15} < 8.7, plus M(1+ln M); LP dual shows 1/15 exact | measured sup 0.52 |
| (a) Case B (u ≡ 0 mod p) without H-sep | PROVED: ≤ 21384·max(1, ω/p²) + 19 (good reduction) | measured sup 60 Π_J at p = 31 |
| (a) Case A, ω ≥ p⁴ | PROVED trivial (cov ≤ p²/2 ≤ cost/2) | — |
| (a) Case A, ω < p⁴ | FALSE without H-sep: short-lift squares | 25 covered pairs at ω = p^{2.5} vs structural 0, heuristic 0.004 |
| repair | PROVED: H-sep holds on [1,B]² when C_S·H·B^{d+8} < p/2 (p-independent digit polynomials of degree d, height H; includes B ≤ p^{1/15}, d ≤ 6) | — |

## 1. What was run
- exp_b_branch_coverage.py: exact cov_b, 540 boxes, A_j ≤ 5003, three curves, x2 ≤ 300.
- exp_a_caseB.py: Bezout multiplicity at p = 101, 211, 401; exact Case-B coverage at p = 31, 40 boxes.
- exp_a_caseA.py: exact Λ_x-meets-box enumeration for all 1431 pairs at p = 103, 12 boxes, every vector classified (structural / short-lift square / other A / B-wrap).
- exp_vol_level2.py: exact c2 on tight boxes from 1.9M pairs x1x2 ≤ 3e5.
- fig.py → fig_sa13c.png. Proofs in step_b.md, step_volume.md, step_a.md.

## 2. Results
### 2.1 (b)
Lemma B1: a nonzero q(T)S(T) has two nonzero extreme coefficients q(0)G0 and lead(q)G2 at distinct indices, so two box coordinates are ≥ p and cost ≥ Π_J. Lemma B2 (Gelfond, K_G = 16√5) bounds the middle |G_k| ≤ 36 Π_J. With SA-13b's level-1 volume lemma: cov_b ≤ 6C·K_G^{2/9}(ω/p²)^{2/3} + const for ω ≥ p², const otherwise; degenerate cases finite or ≤ 2 Π_J^{5/6}. SA-13b's Mahler argument lost p^{1/3} by charging one coordinate; B1 charges two. Numbers: max cov_b = 156 at Π_J = 3e18; sup cov_b/Π_J^{2/3} = 0.0045.

### 2.2 Volume (Theorem V2)
c2(W) ≤ (5·2^{3/5} + 4^{1/15}) ω^{1/15} + M(1+ln M), via six inequalities from the five box conditions, a weighted geometric mean with weights (4,4,0,4,2,1)/15, and X1^{1/5} ≤ W2^{1/30}; an LP dual shows 1/15 is exact. Measured: (0,7) sup 0.517 at c = 21, sup over c ≥ 200 0.465, balanced B = 4..32: 0.25, 0.375, 0.398, 0.400; (2,5) 0.469; (−3,11) 0.490.

### 2.3 (a)
- A1 (proved): Λ_x = {u : p² | u(τ_i), p | u'(τ_i)}, determinant p⁶, depending on (τ1, τ2) mod p only.
- A2 (proved): Case B via S_x | v and Bezout (≤ 12 per monic quadratic, measured ≤ 4 at good primes).
- A3 (proved): ω ≥ p⁴ trivial.
- A4 (proved and measured): for any short lift m′ of S_x mod p, coef(m′²) ∈ Λ_x; about ω^{3/10} such m′ exist, each covering ≤ 12 arbitrary residue pairs. In literal CE2 this gives success 48 p^{−2/5} per unit cost, and the same mechanism voids the level-1 bound without H-int. The covered pairs are R = (R+Q)/2 + (R−Q)/2 with arbitrary Q: index-calculus-useless, so the success criterion of CE/CE2 is the defect (as in SA-13 §1).

Case-A table (p = 103, all 1431 pairs; covered / short-lift squares / other A / B-wrap / random heuristic):

| box W | log_p ω | covered | short-lift sq. | other A | B-wrap | heuristic |
|---|---|---|---|---|---|---|
| (50,20,5,3,2) | 2.22 | 3 | 3 | 0 | 0 | 0.001 |
| (2,2,30,30,30) | 2.50 | 25 | 25 | 0 | 0 | 0.004 |
| (200,100,10,5,3) | 3.22 | 6 | 6 | 0 | 0 | 0.12 |
| (1000,300,15,6,4) | 3.99 | 30 | 23 | 7 | 0 | 4.1 |
| (256,128,64,32,16) | 4.49 | 204 | 175 | 52 | 0 | 41 |
| (5000,1000,20,8,5) | 4.77 | 133 | 36 | 100 | 0 | 153 |
| (5000,5000,25,10,6) | 5.25 | 606 | 54 | 570 | 0 | 1438 |
| (4096,1024,256,64,16) | 5.98 | 1431 | 815 | 1431 | 343 | 42166 |

Structural coverage is 0 in every box.

**Repair (proved).** Digit uniqueness needs only the lowest nonzero digit < p/2; for p-independent digit polynomials (degree d, height H), H-sep holds on the factor base [1,B]² when C_S·H·B^{d+8} < p/2. **Theorem L2:** in CE2-na with polynomial schemes and factor-base success, Pr[success] ≤ 4(C_2 ω^{1/15} + M(1+ln M) + K_b·cost)/N, hence Ω(p^{13/15}) per relation — complete.

## 3. Verdict reasoning
Prediction "(b) exponent ≥ 1/15": met (O(1) per unit cost). Prediction "Ω(p^{13/15}) conditional on (a)": met with (a) replaced by the automatically satisfied hypothesis, which is proved necessary. SUCCESS not claimed (literal (a) disproved; no sub-B¹ search). KILL not claimed (a repair exists; the covered pairs are not factor-base decompositions). Decided by a model ruling: if the repaired class is accepted, the level-2 bound is a finished theorem; otherwise the short-lift squares cap any bound in the literal model at p^{2/5}.

## 4. Limitations
Crude constants; the Bezout lemma needs good reduction and distinct roots ((2,5) at p = 101 is bad reduction); enumeration only at p = 31 and 103 (mechanism proved for all p); the repaired class keeps SA-13b's restrictions (m = 2, D ≤ 2 monomial, n = 5, per-target non-adaptive, all-list oracle); the 13th Case-A box did not finish; toy scale, no deployed-curve statement.

## 5. Suggested lead-atlas update
LEAD-EXO-lattice-query-lower-bound → `theorem_restricted_model_level2_complete` for the repaired class; record "H-sep not removable (short-lift squares); success must be restricted to factor-base decompositions"; next_action: model ruling, then the dual form and m ≥ 3. Deciding numbers: volume sup 0.52 vs proved 8.7; cov_b/Π_J sup 3e-4; short-lift squares 25 covered pairs vs heuristic 0.004.
