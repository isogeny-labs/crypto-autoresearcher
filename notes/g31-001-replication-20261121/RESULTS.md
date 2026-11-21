# G31-001 successor 1 — pre-registered replication of the x-window decomposition-rate signal

**Freeze timestamp: 2026-11-21T05:47:48Z** (written by `freeze.py` before any target was sampled and before any decomposition rate was computed). Config: `frozen_config.json`. Scratch dir: `/Volumes/SSD990/llm/tmp/opencode/g31-001-rep/`. Read-only use of `/Volumes/SSD990-2/crypto-autoresearcher` (pilot scripts copied, never modified).

## 0. Freeze

Frozen before measurement: 20 curves (10 per size class, distinct j-invariants, all of prime order), arms N3=⌊p^(1/3)⌋ and N2=⌊√p⌋, m ∈ {3,4}, 1000 targets per curve (shared across arms/m/nulls), 50 null draws per (curve, cell, null kind), statistic, testability rule, and decision threshold. Nothing below is retuned after results.

**Decision rule (frozen).** A cell's effect is `cell_z = mean_c(z_c)/(sd_c(z_c)/√10)` with `z_c = (r_x − mean_j r_j)/sd_j`, p from t₉. *Replicated* iff, in the Holm-corrected family of all 8 designed cells, ≥2 cells have |cell_z| ≥ 2.5, are Holm-significant at family α = 0.05, and each shows sign consistency ≥ 7/10. Saturated cells score p = 1 and cannot pass. Otherwise: *not replicated at this power*, with the achieved MDE reported.

**Two nulls, both frozen, primary pre-declared.** Primary = *negation-symmetric* random base (uniform over negation-closed b-subsets). B_G is provably negation-closed (x-window has both y-signs; cofactor multiplication is a homomorphism; O removed ⇒ |B_G| even), and a uniform set is not: for m = 4 a symmetric base's sumset factors as (B+B)+(B+B), whose count variance is strictly larger and whose coverage at equal tuple supply is therefore lower. The uniform null is thus confounded with a provable structural difference that is not the property under test. Secondary = uniform random base (the pilot's null, and the literal reading of the task), reported alongside.

### Setup (all curves prime order, so G = E(F_p) and B_G = B_raw is literally the x-window set)

| bits | slot | p | a, b | #E = n | j | \|D\| | arm | N | \|B_raw\| | b=|B_G| | pred frac m=3 | pred frac m=4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13 | 0 | 8237 | 1407, 2224 | 8167 | 7746 | 27907 | N3 | 20 | 22 | 22 | 0.195 | 0.697 |
| 13 | 0 | 8237 | 1407, 2224 | 8167 | 7746 | 27907 | N2 | 90 | 88 | 88 | 1.000 | 1.000 |
| 13 | 1 | 8231 | 6303, 676 | 8209 | 1965 | 32395 | N3 | 20 | 24 | 24 | 0.245 | 0.814 |
| 13 | 1 | 8231 | 6303, 676 | 8209 | 1965 | 32395 | N2 | 90 | 98 | 98 | 1.000 | 1.000 |
| 13 | 2 | 8219 | 912, 3439 | 8087 | 2339 | 15187 | N3 | 20 | 28 | 28 | 0.364 | 0.958 |
| 13 | 2 | 8219 | 912, 3439 | 8087 | 2339 | 15187 | N2 | 90 | 102 | 102 | 1.000 | 1.000 |
| 13 | 3 | 8263 | 1858, 2585 | 8219 | 4403 | 31027 | N3 | 20 | 24 | 24 | 0.244 | 0.814 |
| 13 | 3 | 8263 | 1858, 2585 | 8219 | 4403 | 31027 | N2 | 90 | 68 | 68 | 0.998 | 1.000 |
| 13 | 4 | 8219 | 6571, 632 | 8297 | 5932 | 26947 | N3 | 20 | 18 | 18 | 0.111 | 0.410 |
| 13 | 4 | 8219 | 6571, 632 | 8297 | 5932 | 26947 | N2 | 90 | 100 | 100 | 1.000 | 1.000 |
| 13 | 5 | 8287 | 3387, 4403 | 8467 | 879 | 123 | N3 | 20 | 26 | 26 | 0.292 | 0.894 |
| 13 | 5 | 8287 | 3387, 4403 | 8467 | 879 | 123 | N2 | 91 | 104 | 104 | 1.000 | 1.000 |
| 13 | 6 | 8209 | 3923, 2447 | 8233 | 3564 | 267 | N3 | 20 | 24 | 24 | 0.244 | 0.813 |
| 13 | 6 | 8209 | 3923, 2447 | 8233 | 3564 | 267 | N2 | 90 | 94 | 94 | 1.000 | 1.000 |
| 13 | 7 | 8219 | 5006, 7992 | 8081 | 7335 | 13555 | N3 | 20 | 18 | 18 | 0.113 | 0.418 |
| 13 | 7 | 8219 | 5006, 7992 | 8081 | 7335 | 13555 | N2 | 90 | 88 | 88 | 1.000 | 1.000 |
| 13 | 8 | 8263 | 4030, 3044 | 8179 | 3179 | 25827 | N3 | 20 | 14 | 14 | 0.054 | 0.178 |
| 13 | 8 | 8263 | 4030, 3044 | 8179 | 3179 | 25827 | N2 | 90 | 84 | 84 | 1.000 | 1.000 |
| 13 | 9 | 8263 | 5262, 1271 | 8219 | 5765 | 31027 | N3 | 20 | 24 | 24 | 0.244 | 0.814 |
| 13 | 9 | 8263 | 5262, 1271 | 8219 | 5765 | 31027 | N2 | 90 | 88 | 88 | 1.000 | 1.000 |
| 17 | 0 | 131437 | 114782, 84759 | 131231 | 14494 | 482899 | N3 | 51 | 40 | 40 | 0.078 | 0.556 |
| 17 | 0 | 131437 | 114782, 84759 | 131231 | 14494 | 482899 | N2 | 362 | 364 | 364 | 1.000 | 1.000 |
| 17 | 1 | 132863 | 111709, 132556 | 132661 | 108825 | 490243 | N3 | 51 | 38 | 38 | 0.067 | 0.481 |
| 17 | 1 | 132863 | 111709, 132556 | 132661 | 108825 | 490243 | N2 | 364 | 362 | 362 | 1.000 | 1.000 |
| 17 | 2 | 132589 | 116490, 53620 | 132911 | 78612 | 427315 | N3 | 51 | 46 | 46 | 0.115 | 0.754 |
| 17 | 2 | 132589 | 116490, 53620 | 132911 | 78612 | 427315 | N2 | 364 | 350 | 350 | 1.000 | 1.000 |
| 17 | 3 | 131671 | 25919, 32226 | 131477 | 43114 | 488659 | N3 | 51 | 44 | 44 | 0.102 | 0.695 |
| 17 | 3 | 131671 | 25919, 32226 | 131477 | 43114 | 488659 | N2 | 362 | 352 | 352 | 1.000 | 1.000 |
| 17 | 4 | 132833 | 130109, 130452 | 132709 | 113247 | 515707 | N3 | 51 | 54 | 54 | 0.179 | 0.931 |
| 17 | 4 | 132833 | 130109, 130452 | 132709 | 113247 | 515707 | N2 | 364 | 368 | 368 | 1.000 | 1.000 |
| 17 | 5 | 132851 | 49390, 14807 | 133379 | 3871 | 10147 | N3 | 51 | 40 | 40 | 0.077 | 0.551 |
| 17 | 5 | 132851 | 49390, 14807 | 133379 | 3871 | 10147 | N2 | 364 | 338 | 338 | 1.000 | 1.000 |
| 17 | 6 | 131701 | 118807, 11568 | 132169 | 71214 | 308715 | N3 | 51 | 58 | 58 | 0.218 | 0.972 |
| 17 | 6 | 131701 | 118807, 11568 | 132169 | 71214 | 308715 | N2 | 362 | 386 | 386 | 1.000 | 1.000 |
| 17 | 7 | 131581 | 121215, 3835 | 131909 | 85836 | 419395 | N3 | 51 | 50 | 50 | 0.146 | 0.861 |
| 17 | 7 | 131581 | 121215, 3835 | 131909 | 85836 | 419395 | N2 | 362 | 370 | 370 | 1.000 | 1.000 |
| 17 | 8 | 133073 | 3905, 130303 | 133183 | 73455 | 520411 | N3 | 51 | 48 | 48 | 0.129 | 0.810 |
| 17 | 8 | 133073 | 3905, 130303 | 133183 | 73455 | 520411 | N2 | 364 | 372 | 372 | 1.000 | 1.000 |
| 17 | 9 | 131371 | 14206, 80634 | 131839 | 100049 | 3795 | N3 | 51 | 46 | 46 | 0.116 | 0.757 |
| 17 | 9 | 131371 | 14206, 80634 | 131839 | 100049 | 3795 | N2 | 362 | 368 | 368 | 1.000 | 1.000 |

Testable cells (predicted coverage ≤ 0.995): 13/N3/m=3, 13/N3/m=4, 17/N3/m=3, 17/N3/m=4. All N2 cells are saturated by the dimension count, so the decision family has 4 informative cells and 4 auto-failing saturated cells.

---

<!-- results appended 2026-11-21T05:51:02Z -->

## 1. What ran, and the checks that ran before the decision

Frozen at 2026-11-21T05:47:48Z; measurement 2026-11-21T05:49:13Z to 2026-11-21T05:51:02Z; analysis afterwards. 20 curves (10 per size class, all prime order, distinct j), 2 arms, m ∈ {3,4}, 1000 targets per curve shared by every arm/m/null draw, 50 symmetric + 50 uniform null draws per cell. Total ≈5 minutes of compute.

Two counting engines were implemented and cross-checked: (A) the primary discrete-log/cyclic-convolution engine (a point g^k gets index k, ordered m-tuple sums become sums mod n, counts via FFT), and (B) the pilot's group-law pair-sum table (`pilot_run.Ctx`). They share no code path after the log table is built. On the real frozen curves, bases, targets and null bases (40 curve-arm blocks × 6 configurations: {m=3, m=4} × {x-window base, one symmetric null base, one uniform null base}) **every per-target count is identical (1000 targets per x-window cell, 120 per null-base cell): max |difference| = 0**, every witness re-summed correctly (bad = 0), and total mass = |B|^m exactly (FFT rounding ≤ 4.9e-10). A brute-force enumeration over B^m agrees too (smoke.py).

Other pre-decision checks, all PASS: point counts exact (BSGS order in the Hasse window + independent naive O(p) count, 20/20); curves regenerate bit-identically from the frozen seeds; all 40 bases are even-sized, negation-closed, contain no O and no 2-torsion point, and match the frozen |B_G|; no curve is supersingular (prime order forces t ≠ 0) and there is no small subgroup (G = E(F_p), order prime). Targets: 1000 uniform draws per curve, of which 928-998 distinct (repeats kept as frozen). Curve selection looks only at #E's factorisation: 3-50 (a,b) attempts per slot before a prime-order curve appeared (density ≈ 1/log p), no slot needed a j-collision retry, and no decomposition statistic existed at freeze time.

**One disclosed deviation between frozen text and code.** The frozen arm definition says N3 = ⌊p^(1/3)⌋; the code followed the pilot's convention N3 = round(p^(1/3)). These differ on 6 of the 20 curves (p ≈ 2^17, where the fractional part exceeds 0.5), changing |B_G| by 0 or 2 points on 2 curves. `sens.py` re-runs the two affected cells under the literal floor definition with the frozen targets and fresh 50-draw matched nulls: 17/N3/m=3 cell_z = +0.24 (5/5 signs), 17/N3/m=4 cell_z = +0.12 (5/5), against +0.36 and +0.04 in the main run. The verdict is unchanged. The main run is reported as executed, not patched.

## 2. Results

Setup (curves, arms, bases): see §0 — per curve p, a, b, #E = n (all prime), j, \|D\|, t and b/N.

| cell | b range | pred frac | r_x | null_S | sd_S | z_S | cell_z(S) | p_Holm8 | signs S | d (pp) | 95% CI (pp) | null_U | cell_z(U) | p_Holm8 | signs U |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 13/N2/m=3 | 68–104 | 1.000 | 1.0000 | 0.9998 | 0.0002 | +0.11 | +1.00 | 1.0000 | 1/0 | +0.02 | [-0.02, +0.06] | 0.9999 | +1.00 | 1.0000 | 1/0 |
| 13/N2/m=4 | 68–104 | 1.000 | 1.0000 | 1.0000 | 0.0000 | +0.00 | +0.00 | 1.0000 | 0/0 | +0.00 | [+0.00, +0.00] | 1.0000 | +0.00 | 1.0000 | 0/0 |
| 13/N3/m=3 | 14–28 | 0.211 | 0.2177 | 0.2142 | 0.0155 | +0.11 | +0.43 | 1.0000 | 5/5 | +0.35 | [-0.56, +1.25] | 0.2365 | -5.66 | 0.0024 | 0/10 |
| 13/N3/m=4 | 14–28 | 0.681 | 0.7160 | 0.6937 | 0.0348 | +0.60 | +2.22 | 0.4251 | 9/1 | +2.23 | [+0.01, +4.45] | 0.7550 | -3.98 | 0.0191 | 0/10 |
| 17/N2/m=3 | 338–386 | 1.000 | 1.0000 | 1.0000 | 0.0000 | +0.00 | +0.00 | 1.0000 | 0/0 | +0.00 | [+0.00, +0.00] | 1.0000 | +0.00 | 1.0000 | 0/0 |
| 17/N2/m=4 | 338–386 | 1.000 | 1.0000 | 1.0000 | 0.0000 | +0.00 | +0.00 | 1.0000 | 0/0 | +0.00 | [+0.00, +0.00] | 1.0000 | +0.00 | 1.0000 | 0/0 |
| 17/N3/m=3 | 38–58 | 0.123 | 0.1239 | 0.1235 | 0.0106 | +0.08 | +0.36 | 1.0000 | 5/5 | +0.04 | [-0.46, +0.54] | 0.1305 | -2.68 | 0.1254 | 3/7 |
| 17/N3/m=4 | 38–58 | 0.737 | 0.7426 | 0.7410 | 0.0169 | +0.01 | +0.04 | 1.0000 | 5/5 | +0.16 | [-1.24, +1.56] | 0.7757 | -5.68 | 0.0024 | 0/10 |

*Cell_z(S) is the frozen statistic against the primary, negation-matched null; cell_z(U) is the same against the uniform random-set null (the pilot's, and the literal task null). p_Holm8 is Holm over all 8 designed cells; the 4 saturated N2 cells score p = 1 and cannot pass. "signs" counts curves with r_x above/below the null mean.*

## 3. Verdict under the frozen rule: NOT REPLICATED

No cell reaches the frozen bar against the primary null. The largest |cell_z(S)| is **2.22** (13/N3/m=4) against a bar of 2.5, and its Holm-adjusted p is 0.43; the smallest adjusted p in the whole family is 0.43. Pooled over the four informative cells (40 curve-cells) the effect is mean z = +0.20, pooled z = +1.45 (p = 0.16), with 24/40 curves positive (sign test p = 0.27). The 4 saturated N2 cells give r = 1.0000 for x and for both nulls, z = 0.

The one near-miss, reported and **not** upgraded: 13/N3/m=4 has r_x = 0.7160 vs symmetric null 0.6937, i.e. d = +2.23 pp (95% CI [+0.01, +4.45]), 9/10 curves positive (sign test p = 0.022), cell_z = +2.22. Its MDE is 4.35 pp, so an effect of the observed size is not distinguishable from noise at this design. It is the single observation a larger study should target.

## 4. The pilot's phenomenon: it reproduces, and it is negation symmetry

Against the **uniform** null every informative cell deviates, in one direction, at both sizes and both m:

| cell | cell_z(U) | Holm-8 p | signs | gap: uniform-null minus symmetric-null (pp) |
|---|---|---|---|---|
| 13/N3/m=3 | -5.66 | 0.0024 | 0/10 | +2.23 |
| 13/N3/m=4 | -3.98 | 0.0191 | 0/10 | +6.13 |
| 17/N3/m=3 | -2.68 | 0.1254 | 3/7 | +0.70 |
| 17/N3/m=4 | -5.68 | 0.0024 | 0/10 | +3.46 |

Pooled: z = -7.50 (p = 4e-09), 37/40 curves negative. So the pilot's headline phenomenon is real and highly significant — but the direction is **always** "x-window covers *less* than a same-size uniform generic set", never both directions, and 3 of the 4 cells survive Holm over the 8-cell family (the fourth has adjusted p = 0.125).

It vanishes against the negation-matched null: residual d = +0.35, +2.23, +0.04, +0.16 pp for 13/3, 13/4, 17/3, 17/4 (cell_z +0.43, +2.22, +0.36, +0.04). The uniform-vs-symmetric gap that the uniform null was measuring is 0.7-6.1 pp, i.e. most or all of the "effect".

**Mechanism, measured rather than assumed.** B_G is provably negation-closed (the x-window contains both y-signs; cofactor multiplication is a homomorphism; O is removed, so |B_G| is even — checked 40/40). A negation-closed base carries a forced atom: the pairs (P, −P) all sum to O, so the ordered pair-count at O is exactly b, against ≈ b²/n for a random set (measured: exactly b for the x-window base and for every negation-closed null base, 0.00-0.10 for uniform null bases; four cells, 20 draws each). Convolving, every element of B+B receives at least b tuples at m = 4 (and every R ∈ B at least b triples at m = 3), so mass is concentrated and the support — hence coverage at fixed tuple supply — is strictly smaller. Measured on the 20 informative curves (this sharpens the rationale recorded at freeze time, which said "squared measure"; both point the same way):

* |2B|: uniform null minus symmetric null = +15.7 (+3.17% of the symmetric support), sign +20/20;
* |4B|: +2584 (+8.43%), sign +20/20;
* x-window vs symmetric null: |2B| +0.22% (sd 1.13, 12/20 positive), |4B| +0.98% (sd 3.35, 12/20 positive).

The x-window base has the sumset structure of a *typical* negation-closed set; the uniform null does not, by exactly the margin that lowers coverage. The pilot's conclusion "a same-size generic set is not an exchangeable null" is therefore correct but trivial: exchangeability requires matching the provable symmetry. Once matched, no residual x-geometry effect is detectable at this power.

## 5. Achieved power and minimum detectable effect

| cell | per-curve sd_r(S) | SE of cell mean | MDE (80%, Holm-8) | MDE / null rate | power at observed |
|---|---|---|---|---|---|
| 13/N3/m=3 | 1.55 pp | 0.49 pp | 1.77 pp | 8.3% | 0.02 |
| 13/N3/m=4 | 3.48 pp | 1.10 pp | 4.35 pp | 6.3% | 0.18 |
| 17/N3/m=3 | 1.06 pp | 0.33 pp | 0.98 pp | 7.9% | 0.01 |
| 17/N3/m=4 | 1.69 pp | 0.54 pp | 2.74 pp | 3.7% | 0.01 |

Empirical calibration of the frozen cell statistic (80 pseudo-cells, each built by replacing the x-window base with a fresh random negation-closed base and rerunning the frozen pipeline): sd(cell_z) = 1.15, P(|cell_z| ≥ 2.5) = 0.025, P(|cell_z| ≥ 3.55) = 0/80. The bar is calibrated (slightly conservative) and the Holm threshold is severe.

* MDE at 80% power under the frozen Holm-8 rule: **1.40 per-curve null-sd** on the cell mean, which in fraction units is 1.0-4.4 pp (3.7-8.3% of the null rate) depending on the cell.
* Power at the observed effects: 0.01-0.18.
* What that buys, cell by cell: for the two m=3 cells (sparse, null rate 0.12-0.21) effects above 1.0-1.8 pp are excluded and the observed effects are 0.04-0.35 pp — a clean null. For the two m=4 cells the design only excludes effects above 2.7-4.4 pp, and the observed 13/N3/m=4 effect is 2.2 pp: **that cell is not excluded**, it is simply not significant.

## 6. Direct re-measurement of the pilot's own cells (post-freeze addendum, outside the decision family)

Same curves (reproduced through the pilot's own generator), same bases, fresh 1000-target sets, 50+50 nulls:

| p | c | b | m | pilot r (nT) | replication r (1000) | Poisson | null_S | z_S | null_U | z_U |
|---|---|---|---|---|---|---|---|---|---|---|
| 8219 | 1 | 20 | 3 | 0.1425 (1200) | 0.1440 | 0.1514 | 0.1498 | -0.40 | 0.1717 | -2.60 |
| 8219 | 1 | 20 | 4 | 0.5725 (1200) | 0.6050 | 0.5599 | 0.5709 | +0.70 | 0.6595 | -2.49 |
| 131671 | 2 | 58 | 3 | 0.3781 (320) | 0.4110 | 0.3891 | 0.3901 | +1.09 | 0.4113 | -0.02 |
| 131671 | 2 | 58 | 4 | 1.0000 (320) | 0.9990 | 0.9992 | 0.9992 | -0.14 | 0.9996 | -0.94 |
| 265987 | 1 | 52 | 3 | 0.0844 (320) | 0.0900 | 0.0842 | 0.0833 | +0.74 | 0.0885 | +0.19 |
| 265987 | 1 | 52 | 4 | 0.6813 (320) | 0.7080 | 0.6812 | 0.6867 | +1.23 | 0.7223 | -1.15 |
| 1060981 | 3 | 120 | 3 | 0.6281 (320) | 0.5500 | 0.5570 | 0.5600 | -0.61 | 0.5652 | -0.94 |
| 1060981 | 3 | 120 | 4 | 1.0000 (320) | 1.0000 | 1.0000 | 1.0000 | +0.00 | 1.0000 | +0.00 |

The two cells the pilot used as its headline:

* **p = 8219, m = 4** ("below all 10 uniform draws, z ≈ −7.5"): still far below the uniform null (z = −2.49) but at/above the symmetric null (z = +0.70). The −7.5 was inflated twice over: the pilot's 10-draw sd came out 1.16 pp where 200 draws give 2.12 pp (1.8× too small), and its target draw sat low. At the correct scale the effect is ≈ −2.5 to −4 sd, and it is the symmetry gap: on the pilot's own target set the x-window rate (0.5725) is essentially the symmetric-null mean (0.5784, 200 draws), while at my target set it is 0.6050 against 0.5709.
* **p = 1060981, m = 3** ("above all 20 generic draws, z ≈ +3.6 / +2.5"): **does not reproduce**. With fresh targets r = 0.5500 vs symmetric 0.5600 (z = −0.61) and uniform 0.5652 (z = −0.94). Diagnostic on that curve: over 40 fresh 320-target sets the x-window rate has mean 0.5662 and sd 2.82 pp (pure binomial-type target noise), and 0.6281 — the pilot's value — is the **maximum of all 40**. The pilot's single target draw sat 2.2σ high; its uniform null sd (1.78 pp) was also low (200 draws: 2.86 pp).

So the pilot's "both directions" decomposes exactly as: every cell pushed negative by the non-exchangeable null, plus one cell pushed positive by a target-set fluctuation at 320 targets. Neither half is an x-geometry effect.

## 7. Descriptive characterisation (no role in the verdict)

(a) **Cofactor / base size.** All 20 curves have prime order, so the cofactor is 1, B_G = B_raw is literally the x-window set, and there is no cofactor effect to estimate. b/N ∈ [0.70, 1.40] at N3, the spread being just how many of the N x-values lie on the curve. Within-cell Spearman of z on b: +0.51 (p = 0.13), +0.16, −0.14, −0.28 for 13/m3, 13/m4, 17/m3, 17/m4 — no consistent or significant dependence.

(b) **CM.** Over F_p every curve has CM by an order in Q(√(t²−4p)), so "CM vs non-CM" is not a dichotomy here; the variable is |D_K| (t and |D| are in the setup table, |D_K| from 123 to 520411). No curve has j ∈ {0, 1728}, so the genuinely special j-invariants are absent by construction (they were not selected against; they simply did not occur among the 20 prime-order curves). Within-cell Spearman(z, log|D_K|) = −0.04, +0.63, −0.08, −0.28 — inconsistent in sign, no usable signal. The two smallest-discriminant curves (|D| = 123, 267 at p ≈ 8200) sit inside the bulk (z = +0.45/+0.79 and +1.46/+0.89).

(c) **Set structure.**

| bits/slot | b | j | \|D\| | \|2B\| (x; S,U) | \|4B\| (x; S,U) | b(b+1)/2 | z3 | z4 |
|---|---|---|---|---|---|---|---|---|
| 13/0 | 22 | 7746 | 27907 | 243 (236, 250) | 6065 (5944, 6438) | 253 | -0.84 | +0.40 |
| 13/1 | 24 | 1965 | 32395 | 283 (285, 295) | 7089 (6847, 7256) | 300 | -0.24 | +1.26 |
| 13/2 | 28 | 2339 | 15187 | 379 (385, 398) | 7763 (7806, 7931) | 406 | -0.07 | +0.19 |
| 13/3 | 24 | 4403 | 31027 | 289 (285, 296) | 7279 (6877, 7272) | 300 | +0.66 | +1.44 |
| 13/4 | 18 | 5932 | 26947 | 163 (162, 169) | 3721 (3459, 4312) | 171 | +0.09 | +1.00 |
| 13/5 | 26 | 879 | 123 | 339 (331, 344) | 7911 (7666, 7943) | 351 | +0.45 | +0.79 |
| 13/6 | 24 | 3564 | 267 | 287 (285, 295) | 7079 (6946, 7245) | 300 | +1.46 | +0.89 |
| 13/7 | 18 | 7335 | 13555 | 159 (162, 170) | 3259 (3491, 4238) | 171 | -0.95 | -1.55 |
| 13/8 | 14 | 3179 | 25827 | 99 (98, 104) | 1593 (1557, 2033) | 105 | -0.69 | +0.45 |
| 13/9 | 24 | 5765 | 31027 | 285 (285, 295) | 7033 (6713, 7264) | 300 | +1.29 | +1.14 |
| 17/0 | 40 | 14494 | 482899 | 801 (799, 818) | 74925 (73496, 80005) | 820 | +0.77 | +1.34 |
| 17/1 | 38 | 108825 | 490243 | 713 (721, 739) | 62457 (64437, 70701) | 741 | -0.35 | -0.80 |
| 17/2 | 46 | 78612 | 427315 | 1059 (1056, 1077) | 98597 (101092, 105752) | 1081 | -0.44 | +0.18 |
| 17/3 | 44 | 43114 | 488659 | 969 (967, 987) | 92513 (91604, 97675) | 990 | -0.89 | +1.29 |
| 17/4 | 54 | 113247 | 515707 | 1453 (1453, 1478) | 122219 (123146, 126139) | 1485 | +0.31 | +0.11 |
| 17/5 | 40 | 3871 | 10147 | 801 (800, 818) | 75617 (73675, 80326) | 820 | +1.21 | -0.08 |
| 17/6 | 58 | 71214 | 308715 | 1683 (1678, 1700) | 128267 (128315, 129652) | 1711 | -0.26 | -0.71 |
| 17/7 | 50 | 85836 | 419395 | 1239 (1246, 1269) | 111663 (113937, 117473) | 1275 | -0.74 | -1.50 |
| 17/8 | 48 | 73455 | 520411 | 1147 (1150, 1171) | 106819 (109467, 112925) | 1176 | +0.81 | -1.22 |
| 17/9 | 46 | 100049 | 3795 | 1053 (1053, 1078) | 100905 (100032, 105606) | 1081 | +0.40 | +1.50 |

|B+B| is far below the no-collision reference b(b+1)/2 only because the reference counts pairs, not values: e.g. b = 50 gives |2B| = 1239 against b²/2 = 1250, i.e. almost no collisions, as expected for a set of size b in a group of order ≈ b². The x-window values track the symmetric null to +0.2% and sit 3.2% below the uniform null (|2B|), +1.0% / 8.4% for |4B|. The one notable correlation — z(m=4) vs |4B|_x/|4B|_sym, pooled ρ = +0.68 (p = 0.001), within-cell +0.84 at 13/m4 — is largely mechanical: the statistic is a coverage statistic and |4B| is essentially its support denominator. Recorded as description, not as a law.

## 8. Findings about the pilot (and its code)

1. **Not a counting bug.** Two independent engines agree exactly, and my engine reproduces the pilot's own published fractions to 4 decimals on the pilot's own target sets (0.6281 and 0.5725). The counting code is sound.
2. **The null was not exchangeable.** The pilot compared a negation-closed base with uniform (non-closed) sets. The resulting gap is 0.7-6.1 pp, systematic in sign (37/40 curves, 20/20 on sumset support), and is the whole of the pilot's non-symmetric effect. The pilot partly noticed this (its symmetric null) but headlined the uniform comparison anyway.
3. **"Both directions" does not survive.** Re-measured with fresh targets and 50 draws, all four informative cells deviate in the same direction vs the uniform null, and the one cell that went the other way (p = 1060981, m = 3) is a 2.2σ target fluctuation that does not reproduce.
4. **Reported |z| values were over-stated by noisily estimated null sds.** The pilot's sds came from 10 draws; in the two quoted cells the 10-draw uniform sd was 1.8× and 1.6× smaller than the 200-draw value, turning ≈ −4σ and ≈ +2.4σ effects into −7.5 and +3.6.
5. **Latent code defects, documented, unreachable in this setting.** (i) `make_generic(..., 'symmetric')` returns b+1 points when b is odd — it cannot fire, because a negation-closed subset of a group of odd order has even cardinality and |B_G| is therefore always even (40/40 checked). (ii) `Ctx.add_many` uses λ = (3x²+a)/(2y) on the doubling branch, so a 2-torsion point (y = 0) yields a wrong key instead of O; unreachable, because B_G ⊂ G has odd prime order and contains no 2-torsion (0/40 bases), and cofactor clearing removes 2-torsion when the cofactor is even. Neither affects any number in this report or in the pilot's.
6. **The pilot's tuple-supply claim holds.** mean_r/(b^m/n) = 0.998-1.050 and r_x/Poisson = 1.008-1.051 across all cells; the dimension count is right and the x-window deviation is in coverage, not supply, exactly as the pilot said.

## 9. What this does and does not establish

**The pilot signal did not survive.** Stated precisely: the pilot's conclusion "x-window decomposition rates leave a same-size generic-set null band, in both directions" is not replicated. Against the only exchangeable null (matched negation symmetry) the largest cell effect is +2.22 sd (frozen bar 2.5; Holm-adjusted p 0.43) and the pooled effect over 4 cells / 40 curves is +0.20 sd (p 0.16; 24/40 positive). At 80% power the design would have detected a per-curve mean effect of 1.40 null-sd (1.0-4.4 pp, 3.7-8.3% relative).

Establishes:
1. The one systematic x-window effect that does exist is **negation symmetry**, not x-geometry: coverage is 0.7-6.1 pp below a same-size *uniform* set in every informative cell (37/40 curves; pooled z −7.5), and this is fully accounted for by the sumset-support gap (|2B| +3.2%, |4B| +8.4%, 20/20 each). Against a random negation-closed set of the same size the x-window base is ordinary: residual +0.2% (|2B|) and +1.0% (|4B|), 12/20 signs each way.
2. Counting and the dimension count are correct at this tier: two independent engines agree exactly; mean tuple supply matches b^m/n to 0.2-5%; coverage matches the m!-corrected Poisson prediction to 0.8-5%.
3. The uniform random-set null is **not** a valid null for an x-window base at any size tested, and the size of the invalidity (up to 6 pp of fraction) exceeds the effect sizes the pilot was chasing. This is the reusable methodological result.

Does not establish:
1. Nothing above p ≈ 2^17, and nothing at N = ⌊√p⌋ (all four such cells are saturated: r = 1 for every target and every base, by the dimension count, predicted at freeze time).
2. It does **not** exclude a small x-geometry effect in the m=4 cells: the MDE there is 2.7-4.4 pp and the observed 13/N3/m=4 effect is 2.2 pp with 9/10 sign consistency (sign test p = 0.022). For the m=3 cells, effects above 1.0-1.8 pp are excluded and the observed ones are ≤ 0.35 pp.
3. No evidence either way about larger p, where x-window and uniform nulls might separate differently. The pilot's p = 2^20 cell that did so is explained by a target fluctuation and is not evidence.
4. Nothing about attack relevance: effects are ≤ 6 pp in a coverage rate at toy size with m ≤ 4 and none in tuple supply.

What a decisive follow-up needs: more informative cells (N = ⌊p^(1/4)⌋ in addition to ⌊p^(1/3)⌋; ⌊√p⌋ is uninformative below p ≈ 2^24), ≥ 25-30 curves per cell, ≥ 2000 targets per curve, the negation-matched null as primary, and 13/N3/m=4 (m = 4, p ≈ 2^13, sparse-to-mid coverage) as the specific hypothesis. Nothing in this report should be read as evidence for the Terracini/secant-rank dictionary producing an algorithmic advantage; that claim was not tested here.

---

Artifacts in this directory: `frozen_config.json` (freeze), `freeze.py`, `replib.py` (both engines' core), `verify.py` → `verify.json`, `run_replication.py` → `results.json` + `run.log`, `analyze.py` → `analysis.json` + `analysis.txt`, `structure.py` → `structure.json`, `nullcal.py` → `nullcal.json`, `addendum.py` → `addendum.json`, `sens.py` → `sensitivity.json`, `tables.py`, `mkreport.py`, `smoke.py`; pilot files copied read-only as `ec.py` and `pilot_run.py`.
