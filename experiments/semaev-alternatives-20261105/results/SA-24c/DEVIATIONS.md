# SA-24c deviations from the frozen protocol

Part 1
1. **Targets above the minimum.** Expected unweighted events per cell (3 curves pooled) were set to about 200 (not 50), and about 1000 for the (2^24, 0.5) top-up (not 500), so the ratio CIs are about +-15%.
2. **(2^24, 0.3) partly shortened.** Curve 0 and curve 2 hit the 2 h background-chunk limit and were killed after 74 and 78 of 100 blocks; the completed blocks are independent samples and were used as they are (expected events scaled by completed trials). Curve 1 ran in full with a target of 20 events per curve instead of 67. Pooled: 96 observed vs 94 expected events (target >= 50 met).
3. **Genus-3 denominator subsample.** 2e8 unfiltered trials per curve instead of >= 1e9 (genus 2 used 1e9). The weight mean has relative error about 1e-4 at 2e8, far below the numerator error (about 7%). The denominators are used only to turn hits into the SA-24 weighted ratio.
4. **Filter details.** A bitset on c1 pre-screens before the hash lookup (same set, faster). Genus 3 uses D = 2e7 draws per c2.
5. **Validation 2 form.** 1e6 random drawn u's per cell plus every member of each per-c2 set and its c0+1 perturbation, checked against full root finding. (Random u's hit the set almost never at those cells, hence the added members check.)
6. **Weighted ratio kept.** The verdict uses SA-24's weighted observed/expected ratio (as the prereg says: same estimator); unweighted event counts are reported next to it.
7. **Slope CI.** Block bootstrap resamples blocks of both the SA-24 and the fresh samples and the denominator blocks, 2,000 resamples, seed 24; only the cells in the SA-24 grid enter the slopes (as in SA-24).

Part 2
8. **Linear algebra.** All sizes used one sparse (structured) elimination: every relation has exactly two factor-base unknowns plus k, so the elimination never fills in beyond two columns and the dense phase is empty. Multiply-adds are counted as executed. The frozen "dense if |F| <= 6000" branch was not used. A dense-accounting fit is reported as a sensitivity only; its scan is truncated by deviation 9 and it is not an optimum.
9. **Trial cap and skipped cells.** Cells whose expected trials (relations needed / exact stratum null) exceed 1.5e8 were skipped and logged: (2^18, 0.4), (2^20, 0.55), (2^22, 0.55), (2^22, 0.65) (36 runs). Grid at 2^20 and 2^22 was extended with 0.85 and 0.9 (frozen: 0.55, 0.65, 0.75) because 0.55 was skipped. A non-frozen extra scan at delta 0.95 was run for all sizes (results/p2x_*).
10. **Uniform X_i.** Uniform u, accept with probability w(u)/4, uniform v (square roots in F_p^2 by Tonelli-Shanks). Repeated-root u (probability about 1/p) are excluded. T_i = [n1]X_i by double-and-add (charged as Jacobian additions).
11. **Restart.** Fresh start = pullback(aP+bQ) followed by 4 random table steps (not 256-step sub-restarts of a separate random combination); restarts every 256 steps.
12. **Positive control** (2^10, 2^12): n1-component logs of all factor-base points by brute force (c * D = j * (c*G)); every relation checked against a + b k.
13. **Load.** p2 files for k = 10, 12 and k = 14 curve 0 ran while another process of mine also ran (before I saw that two SA-23b enum_r2 chunks were still active). Counts are unaffected; the conversion ratios are measured in-process under the recorded load. Later runs were one heavy process at a time while enum_r2 ran, and two after it finished.
14. **Outcome uses alpha against log2 p** (the frozen prediction's variable); alpha against log2 n1 is reported next to it.
