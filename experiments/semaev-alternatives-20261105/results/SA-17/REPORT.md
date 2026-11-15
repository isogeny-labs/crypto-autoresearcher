# SA-17 report: function-field mirror of polynomial-lattice small roots

(Saved by the main session verbatim from the resumed executor's final message; the harness refused the executor's own write.)

## Summary

**KILL.** In F_q[t]/(π) the function-field reach of the polynomial-lattice small-root method is far below the existence threshold 1/m. The prereg kill rule is: "the run is killed if the function-field reach is also below 1/m."

- For m = 2 (target 1/2), the measured FF threshold is δ_FF = 0.12–0.17 at every cell tested (q = 3,5,7, n = 24..64, box shift sets up to dim 49). Extrapolated to large n it is 0.112–0.126.
- The exact mechanism lattice gives δ_FF → 0.1128 [95% CI 0.1110, 0.1144], which matches 1/9.
- For m = 3 (target 1/3), δ_FF → 0.0215 [0.0208, 0.0220], which matches 1/50.

The carry is **not** the quantity the archimedean case loses. The FF-minus-F_p gap is a pure finite-size term of about 0.6/n. Extrapolated to large n it is 0.0011 [−0.0021, 0.0039] for m = 2 and 0.0005 [−0.0012, 0.0026] for m = 3. Both twins hit the same wall, and the wall comes from the lattice construction, not from the arithmetic. (A carry-loss law within 0.01 does exist, δ_Z ≈ δ_FF − 0.61/n, but it is trivial, and the kill rule takes precedence.)

## What was run

All runs are toy scale on the shared campaign host, single-threaded, under `nice`.

1. **Box-shift Coppersmith lattices for S3, m = 2.** Done by the predecessor (`lat.py`, `run_cell.py`), with the cells listed in DEVIATIONS item 5 added on resume.
   - Plant R = P1 + P2 with deg x_i < D_i (FF) or x_i ≤ q^{D_i} (F_p, p = nextprime(q^n)). Every planted relation was checked independently.
   - Build the same box monomial set [0,s]² with the same shifts f^k π^{t−k} (respectively p^{t−k}) in both twins.
   - Reduce with weak Popov form (Mulders–Storjohann, exact) over F_q[t] and with fpylll LLL (δ = 0.99) over Z.
   - Success: the vanishing reduced rows have trivial gcd, so the planted root is isolated.
   - Scan S = D1 + D2, with δ = S/(2n). The threshold is the interpolated 50% crossing.
   - Trials: 5 per S (FF) and 12 per S (F_p). 689 v2 scan rows plus 1066 v1 rows.
2. **Mechanism lattices (added on resume).** S_{m+1} is linear in the coefficient vector of its expansion in x_R:
   - m = 2: S3 = A·X² + B·X + C, with deg(A, B, C) = (2, 3, 4) in the small unknowns. The 3-dim lattice {(α, β, γ) : αX² + βX + γ ≡ 0} has the planted vector as its unique shortest vector iff (2+3+4)δ < 1, that is δ < **1/9**. In FF this holds exactly, because successive minima sum to the determinant degree. In Z it is the Gaussian heuristic.
   - m = 3: S4 = Σ_{l=0}^{4} c_l X^l with deg c_l = 12 − l. The 5-dim lattice gives δ < 1/Σ(12 − l) = **1/50**.
   - Scripts `form3.py` (q = 3,5,7, n = 24..192, 30 trials per S) and `form5.py` (q = 3,7, odd n = 97..385, 20 trials per S). Success means the first reduced vector is proportional to the planted vector.

## Results

### m = 2 box lattices, v2 criterion (`results/v2_thresholds.json`, `fig_threshold_v2.png`)

| (s,t) | dim | Coppersmith asym. | mean δ_FF | mean δ_Z | mean loss | δ_FF(n→∞) [95% CI] | δ_Z(n→∞) [95% CI] |
|---|---|---|---|---|---|---|---|
| (2,1) | 9 | 0.056 | 0.132 | 0.119 | 0.014 | 0.116 [0.112, 0.121] | 0.110 [0.105, 0.115] |
| (4,2) | 25 | 0.100 | 0.145 | 0.127 | 0.018 | 0.112 [0.105, 0.118] | 0.113 [0.107, 0.118] |
| (6,3) | 49 | 0.119 | 0.156 | 0.136 | 0.020 | 0.126 [0.122, 0.129]* | 0.131 [0.109, 0.144]* |

\* (6,3) has six cells with n = 32..64 only. The v1 criterion gives the same picture: (2,1) 0.115 / 0.111, (3,1) 0.116 / 0.107, (4,2) 0.113 / 0.112.

The maximum single-cell FF threshold anywhere is 0.170 (q=3, n=24, (4,2)). **No cell comes within a factor of 2.9 of 1/2.**

### Mechanism (form) lattices (`results/form3_thresholds.json`, `results/form5_thresholds.json`, `fig_mechanism.png`)

| m | theory | δ_FF(∞) [CI] | δ_Z(∞) [CI] | loss(∞) [CI] | loss slope (×1/n) | cells |
|---|---|---|---|---|---|---|
| 2 | 1/9 = 0.1111 | 0.1128 [0.1110, 0.1144] | 0.1118 [0.1102, 0.1138] | 0.0011 [−0.0021, 0.0039] | 0.68 | 24 FF / 23 Z |
| 3 | 1/50 = 0.0200 | 0.0215 [0.0208, 0.0220] | 0.0213 [0.0189, 0.0236] | 0.0005 [−0.0012, 0.0026] | 0.34 | 9 FF / 7 Z |

At m = 2 with matched (q, n), the box lattices at s ≤ 4 land within about 0.01 of the form lattice for n ≥ 48, and both converge to 1/9. This is the same 1/9 crossing that SA-13 found by weighting the (1, B, B²) columns: the box lattices are rediscovering that 3-dim form lattice.

The FF excess n·(δ_FF − theory) stays at 0.6–1.1 across n = 97..385, about one digit, consistent with the degree convention (deg x < D gives size q^{D−1}, while x ≤ q^D gives size q^D). This is a parametrisation offset, not an arithmetic loss.

### Carry-loss law fits (v2 box data, `results/v2_law.json`)

| law for loss = δ_FF − δ_Z | coefficient [CI] | in-sample within 0.01 | leave-one-lattice-out within 0.01 (max error) |
|---|---|---|---|
| constant | 0.0166 [0.0145, 0.0187] | 0.89 | 0.86 (0.015) |
| c/n ("one-digit ball") | 0.614 [0.551, 0.680] | 0.97 | 0.89 (0.013) |
| c/n + LLL-slack term | 0.862, −1.50 | 1.00 | 0.97 (0.010) |

The c/n law predicts δ_Z from δ_FF within 0.01 in 89–97% of cells, and its limit is zero.

## Verdict reasoning

- The frozen kill rule is "function-field reach also below 1/m". At m = 2 every measured FF threshold is at most 0.17, and every extrapolation is 0.112–0.126, against 0.5. At m = 3 it is 0.0215 against 0.333.
- Larger shift sets do not change the conclusion. Growing (s,t) from (2,1) to (6,3) moved the finite-n FF threshold by about +0.02. The asymptotic ceiling of bivariate Coppersmith box lattices is 1/6 (SA-08, SA-18), still below 1/2.
- The kill is met by a wide margin and is robust to the toy scale.
- The prereg prediction ("FF reach = existence threshold; F_p reach = Jochemsz–May; the difference is a carry term") is refuted on both halves: FF reach is not 1/m, and the twins differ only by an O(1/n) parametrisation term that vanishes as n grows. Exact polynomial-lattice reduction with no carries buys nothing asymptotically. At the shift sets tested, F_p reach is below the Jochemsz–May value (1/6 for m = 2, 1/24 for m = 3).
- The carry-loss law passes the 0.01 success test, but trivially: its limit is zero, so it names no term for a future proposal to remove. The kill rule governs the verdict.

## Limitations

- Toy scale: box lattices use n ≤ 64 (bits ≤ 180) and dim ≤ 49; box-lattice extrapolations span fewer than 4 doublings. The form lattices reach n = 192 (m = 2) and 385 (m = 3).
- q = 2 and m = 4 were not run. The m = 3 test uses only the form lattice, not a box/shift lattice. Two m = 3 F_p cells timed out. pari.sqrt stalls for n ≥ 96, so m = 3 planting used odd n only.
- The FF box success criterion is a specialisation gcd test (probabilistic), with no FF end-to-end root recovery. The F_p box side was verified end to end (39/39). Form-lattice success is an exact vector match, from which (x1 + x2, x1·x2) follow algebraically (sketched, not run).
- "Reach" here is the reach of Coppersmith-type box/shift lattices and of the form lattice. A different FF method, such as linearisation over the F_q-subspace or Weil-descent Gröbner, can reach 1/m, as in the known Gaudry/Diem results. That is exactly the redirection the kill rule names.
- The predecessor's thresholds/law/extrapolation.json and fig_threshold.png came from partial pair-test data; they are moved to results/v1/predecessor_* and superseded by results/v2_*.
- The resumed run was done by a different model from the original executor (see DEVIATIONS.md).

## Suggested lead-atlas update

Proposed LEAD-ICP-function-field-mirror: **killed (lattice lens)**. In F_q[t]/(π), with exact weak-Popov reduction and no carries, the planted-S3 small-root threshold is 0.1128 [0.1110, 0.1144], equal to 1/9, against the existence threshold 1/2; the S4 threshold is 0.0215, equal to 1/50, against 1/3. The F_p twin converges to the same values (residual gap 0.001 ± 0.003, a finite-size term ~0.6/n). The bottleneck is the form-lattice degree budget Σ_l deg c_l of S_{m+1} in x_R (9 for m = 2, 50 for m = 3), not the archimedean carry. Next action: redirect toward linear/Weil-descent structure over the F_q-subspace, as the prereg kill rule directs. Any future lattice proposal must reduce Σ_l deg c_l (for example with a different relation polynomial or coordinates) rather than the carry. Cross-reference SA-13 (the 1/9 crossing) and SA-08/SA-18 (the 1/6 wall).
