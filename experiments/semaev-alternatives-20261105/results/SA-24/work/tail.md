
Per-delta slopes, A3: 0.7: -0.0025 [-0.029, 0.022]; 0.8: 0.0005 [-0.003, 0.004]; 0.9: -0.0001 [-0.0006, 0.0004]. Pooled: -0.0007 [-0.0096, 0.0076].

Why A2/A3 cannot show an excess: for a uniform element the split probability is exactly (number of reduced divisors supported on F)/#Jac. The measured/null ratio therefore only tests the sampler and the counting formula, and both agree to sampling noise (and exactly in the exhaustive runs). The factor base in Jac(C) gives no density advantage over the E1 hit set because the elements of interest, the R_j, are not uniform in Jac(C) but lie in the pullback subgroup of size about p.

## Flagged borderline readings (not resolved)
1. INCONCLUSIVE vs KILL rests on two unmeasurable cells and one per-delta slope (see Verdict). 4 of 26 powered A2 cells have a CI that excludes 1 (2^12/0.4 [1.000, 1.012], 2^12/0.7 [1.000, 1.001], 2^20/0.7 [1.001, 1.005], 2^24/0.5 [0.721, 0.979]); all ratios are within [0.8, 1.25] and 3 of 4 are within 0.6% of 1. With 41 powered cells, a few such CIs are expected by chance (CIs are percentile block-bootstrap intervals over 3 curves, which can be too narrow for cells with large weights).
2. Prediction "A1 alpha at least 1 under every B" is not met on 2^10..2^20: fixed-delta alphas 0.81 to 0.87 (CIs exclude 1); 10-24 they reach 0.88-0.93. Trials per relation-set are about 0.9-1.04 p at every size, so the slope below 1 comes from small-size overhead (+10 relations, tiny sizes, noise in the measured conversion ratios, 16-35 across batches) and from picking the minimum over noisy deltas. Not resolved.
3. Prediction "rho alpha = 0.50 +- 0.03" is not met: 0.34-0.45 depending on sizes, because DP-rho has size-independent overhead at small n1 (table build, restarts, fruitless trails). This favours the KILL comparison; the A1 minus rho gap (0.5 or more) is far larger than any such effect.
4. Timing floors: rho wall time is 21-25 microseconds for 2^10..2^14 (near the resolution of this harness) and the 2^10 and 2^12 A1 points are overhead-heavy; fits are reported with and without 2^10 and 2^12 and the verdict does not depend on them. The fits are on counted operations; wall time is secondary. Host load 2-5 throughout; the conversion ratios were measured under the load of each batch.
5. The optimum delta per size is flat and noisy (cost varies by less than about 10% over delta 0.4..0.95), so "optimum B about p^(2/3)" is not supported or refuted; there is no cost minimum to locate.

## Limitations
- Generic Cantor (22 E1-adds per Jacobian add) instead of explicit formulas; constant factor only.
- Rho is a plain DP implementation, not tuned; E1 additions use affine inversion for both rho and the Jacobian ratio.
- Cells with fewer than 50 expected hits are reported but cannot be judged (A2: 2 of 28; A3: 3 of 15).
- Slope CIs resample blocks within 3 curves per size, not curves; curve-to-curve variation of the null is only partly in the CI.
- The point at infinity of the odd model (x = r) is excluded from F; lower-weight divisors (probability about 1/p) are not sampled.
- Degree-3 covers (Frey-Kani) not tested (as frozen). Only bielliptic covers.
- Only the A1 sizes 2^10..2^24 were run; the 2^24 point scans 6 deltas.
- The kb/cairn knowledge servers did not connect in this session, so no prior-art query was made; no literature claim is made here. The repository was not touched and no `.resume` checkpoint was created (brief: work only in this directory); the main session stages results.

## Suggested lead-atlas line
SA-24 (Semaev-alternatives, round 6): factor base in Jac(C) for bielliptic genus-2 cover of E1 (and genus-3 splitting statistics), p = 2^10..2^24. Pullback exact; #Jac = #E1 #E2. Relations from pb(T) reduce to hits in the set {T in E1 : x(T) = small square}: A1 alpha = 0.87 [0.82, 0.92] (counted E1-add equivalents) vs rho 0.34 [0.29, 0.40]; splitting ratios measured/null = 1 within noise at both genera (pooled slope CI contains 0). Verdict INCONCLUSIVE only because two cells with expected count <= 1 cannot meet the "every cell in [0.5, 2]" clause; on powered cells it is a KILL. Cover Jacobians give no relation source beyond E1 itself. Artifacts: /home/user/semaev-runs/SA-24/results/.
