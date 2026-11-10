# Results: walk-length constant of the r-adding negation-map walk versus jump count

Every number here is `[pcc:unverified]`: it comes from the committed simulator and
raw cells in this directory, and no independent validator has re-derived it.
Protocol: `PROTOCOL.md` (registered at the commit in `PROTOCOL.commit`, with
Amendments 1 and 2 recorded before any grid data). Counts only: no timing, no
field arithmetic. Lead: `LEAD-RHO-matched-rho-calibration`. This changes no lead
disposition and no ecbench bound.

## Verdict in six lines

1. Gates pass. G1 (the random-mapping null matches theory) holds in 10 of 10
   cells; G2 (A/A) holds in 177 of 190 cells (93.2 percent, threshold 90).
2. With 2-cycle look-ahead and cycle escape, an r = 16 walk costs
   R = 1.058 [1.038, 1.079] times an ideal random mapping at 32 and 36 bits.
   The excess falls to about 1.00 by r = 64 (R is 1.033 at r = 32, 1.006 at 64).
3. The ecbench medium-tier constant is 1.093 [1.033, 1.156] over the floor.
   The walk at r = 16 explains most of that: 5.8 of its 9.3 points. The remaining
   3 to 4 points are outside the walk (distinguished points, set-up, verification);
   the intervals overlap, so that split is approximate.
4. Charging table set-up as ecbench does, a larger table saves 4.1 percent at 32 bits
   (best r = 64) and 5.5 to 5.9 percent from 40 bits on (best r = 256, with r = 64
   to 1,024 indistinguishable at that size). At 24 bits r = 16 is already optimal.
5. Three of five registered predictions failed or are void; they are reported below,
   not adjusted. One failure (H4) is a defect in my own Amendment 1 text.
6. The effect is small. Against index-calculus gaps of 5.5x to 13.5x on the
   validated prime rows, a 5 to 6 percent change in the rho denominator does not
   change any ranking, and the validated rows (up to 23.4 bits) are unaffected.

## Registered hypotheses, as evaluated

| id | prediction | result |
|---|---|---|
| H1 | neg0, r = 4, b >= 24: R >= 1.30 | Holds, trivially. 99 to 100 percent of trials hit the cap, so R (about 72) is the cap and not a mean. What the cell shows is that without cycle handling an r = 4 walk is trapped at every size from 24 bits. |
| H2 | neg2, r >= 32, b >= 24: within 3 percent of 1 | **Fails**: 18 of 20 cells within. The two outside are r = 32 at b = 36 (1.050 [1.017, 1.084]) and r = 128 at b = 36 (1.032 [1.001, 1.066]); r = 32 is 1.030, 1.022, 1.016 at b = 24, 28, 32, so its true excess is about 2 to 3 percent and b = 36 has 1,000 trials only. |
| H3 | neg2, r = 16, b >= 32: R in [1.02, 1.10] | Holds. b = 32: 1.045 [1.021, 1.068]; b = 36: 1.085 [1.050, 1.119]; pooled 1.058 [1.038, 1.079]. |
| H4 | null-adjusted plain/neg2 at r = 16 at least 1.30 | **Void as specified; mechanically fails** (1.004 and 0.963). Amendment 1 defines the quantity as (plain/neg2) divided by (rm_plain/rm), which is 1.00 for ideal walks, then keeps a threshold of 1.30. My error. The raw ratio, which is what ecbench's P4 measures, is in H4' below. |
| H5 | best r saves at most 2 percent at 32 and 40 bits, against the review | **Fails**: the saving is 4.13 percent at 32 and 5.50 percent at 40. I expected the review's recommendation to be partly wrong; at this size it is supported. |

H4' (post hoc, not registered): raw plain/neg2 at r = 16 is 1.392 [1.361, 1.425] at
32 bits and 1.357 [1.314, 1.400] at 36 bits, against an ideal of 1.414. ecbench's
paired control measured 1.285 [1.177, 1.404]. The walk alone gives 1.36 to 1.39, which
sits inside ecbench's interval; the point estimate of 1.285 is lower, and this study
cannot say why.

## Q1: walk constant versus r (R = additions / matched random-mapping null)

`neg2` (look-ahead plus cycle escape), pooled over both seed families. "cap" is the
share of trials stopped at the 64 sqrt(n) cap.

| b / r | 4 | 8 | 16 | 32 | 64 | 128 | 256 | 1024 |
|---|---|---|---|---|---|---|---|---|
| 28 | 1.696 [1.664, 1.728] | 1.168 [1.146, 1.191] | 1.069 [1.049, 1.089] | 1.022 [1.003, 1.041] | 1.008 [0.990, 1.025] | 1.004 [0.986, 1.022] | 1.003 [0.984, 1.022] | 1.001 [0.983, 1.021] |
| 32 | 2.618 [2.407, 2.832] (cap 1%) | 1.159 [1.133, 1.185] | 1.045 [1.021, 1.068] | 1.016 [0.993, 1.040] | 0.999 [0.977, 1.023] | 0.993 [0.971, 1.016] | 0.998 [0.975, 1.021] | 0.995 [0.973, 1.017] |
| 36 | 26.705 [25.185, 28.242] (cap 35%) | 1.200 [1.161, 1.239] | 1.085 [1.050, 1.119] | 1.050 [1.017, 1.084] | 1.012 [0.979, 1.045] | 1.032 [1.001, 1.066] | 1.005 [0.974, 1.037] | 1.017 [0.986, 1.051] |

Pooled over b = 32 and 36: r = 8: 1.179, r = 16: 1.065, r = 32: 1.033, r = 64: 1.006,
r = 128: 1.013, r = 256: 1.002, r = 1,024: 1.006. Above r = 64 the differences are
within noise (about 1 to 2 percent per cell).

`plain` (no negation): R is 1.23 (b = 20) rising to 1.36 (b = 32) at r = 4, 1.05 to
1.10 at r = 8, 1.04 to 1.05 at r = 16 and 0.99 to 1.03 from r = 64. The plain walk has no
cycle problem but the same r-dependence, so the excess is partly the r-adding walk
itself and not only fruitless cycles.

`neg1` (look-ahead without escape) is trapped well past r = 16 at larger sizes:
68 percent of trials capped at r = 16 and 0 percent at r = 32 for b = 32, and
65 percent at r = 32 for b = 36. Look-ahead alone does not remove traps; the escape
is needed, and the neg2 cells show it works from r = 8 up. Even neg2 is trapped at
r = 4, and increasingly with size: 1 percent of trials capped at 32 bits and 35 percent
at 36 bits (R = 26.7 at b = 36).

## Q2: how much of ecbench's medium constant is the walk

R16 = 1.058 [1.038, 1.079] against M = 1.093 [1.033, 1.156]. Registered rule: not
below 1.04 and not above M, so the verdict is `walk_explains_most`. Reading: the
r = 16 walk costs about 5.8 percent more than an ideal walk, and ecbench's medium
constant is about 9.3 percent over the floor. The walk accounts for most of it, and
the remainder is not measured here.

## Q3: total additions with table set-up charged

Walk = R_neg2(r) x 0.8862 sqrt(n); set-up = r x A(r), small-coefficient
A = 1.5 x clamp(3 log2 r, 6, 12) as in ecbench's `jump_coefficient_bits`;
`rho_jumps_for` selects r = 16 for b >= 23.

Small-coefficient jumps:

| b | best r | saving vs r = 16 |
|---|---|---|
| 24 | 16 | 0.00% |
| 32 | 64 | 4.13% |
| 40 | 256 | 5.50% |
| 48 | 256 | 5.91% |
| 56 | 256 | 5.94% |
| 64 | 256 | 5.94% |

Full-width jumps (set-up 1.5 b per jump, as in `ecc-challenges`):

| b | best r | saving vs r = 16 |
|---|---|---|
| 24 | 16 | 0.00% |
| 32 | 64 | 1.80% |
| 40 | 64 | 5.25% |
| 48 | 256 | 5.83% |
| 56 | 256 | 5.93% |
| 64 | 256 | 5.94% |

The set-up term is negligible from 40 bits on, so the saving there is the walk
excess itself, about 5.9 percent, and the best r is any value from 64 up.

## Corrections to the 2026-11-08 review

The review (`isogeny-labs/isogeny-labs`, `research/ecdlp-prime-field-review-20261108.md`
section 3.1) said the matched rho is "about 10 to 15 percent too small" and
recommended 1,024 to 2,048 jumps. This study supports a smaller claim:

- The walk-only excess at r = 16 is about 6 percent, not 10 to 15 percent.
- The optimum is r = 64 at 32 bits and r = 64 to 1,024 from 40 bits; 1,024 or more is
  not needed, and at 32 bits it costs more than it saves.
- The saving at 24 bits and below is zero, so the validated Table B prime rows
  (up to 23.4 bits) do not change.

## Controls and checks

- Null arm (`rm`, `rm_plain`): within 3 percent of the corrected ideal in 10 of 10
  cells, interval contains it in 10 of 10 (G1).
- A/A: 177 of 190 cells have family 1 over family 2 containing 1 (G2). On the
  partial grid (before b = 36 finished) the same gate read 102 of 114 and 140 of 152;
  a post-hoc check of those partial results showed z-scores with mean -0.03 and
  standard deviation 1.05, consistent with noise. The gate is evaluated on the full grid.
- Positive control: neg0 at r = 2 and 4, and neg1 at small r, are strongly
  trapped (cap shares up to 100 percent), so the instrument sees a large effect.
- Independent implementation: `crosscheck.py` re-implements the walk rules in Python
  from the protocol text. With the same partition hash it agrees with the C simulator
  in all eight cells tried (`crosscheck.out.txt`; z between -1.3 and +1.9). With a
  deliberately weak partition hash the neg1 trap rate at r = 4 doubled (mean 759
  against 381), a post-hoc contrast showing that trapping depends on partition
  structure.

## Limits

- Counts only. No timing, field arithmetic, canonicalisation or hashing, which
  are the unpriced work of AGENTS.md section 5a.
- Distinguished-point overhead, the collision-resolution tail and verification are
  excluded; the model bounds the walk part of ecbench's cost, not its total.
- The partition is an ideal mixer. Real partitions use coordinate bits; the weak-hash
  contrast shows this can matter for trapping in the arms without full cycle handling.
- Jumps are modelled as uniform random group elements. ecbench builds jumps as
  `[a_j]P + [b_j]Q` from small coefficient vectors (read from `ic_boundary.rs`,
  `joint_mul` and `jump_coefficient_bits`, not tested here). For a random target
  that is a uniformly random element, as modelled; the small coefficients exist to
  avoid integer relations between the vectors, which the model excludes by
  construction and which are not measured.
- The cost model uses the measured walk constant for sizes above 36 bits and assumes
  it is flat in b. Across b = 28, 32, 36 it is flat within noise for r >= 64; for
  r = 16 it ranges 1.045 to 1.085.
- No claim here changes a lead disposition, an ecbench bound or a leaderboard row. A
  sealed ecbench reseal at 32 to 48 bits with replay remains the registered next step.

## Run log

- Grid: 380 cells, 2 seed families, 5 sizes, started 2026-11-08T23:48:48Z, completed
  2026-11-10T03:50:02Z.
- The worker process restarted during the run. 359 of 380 cells were complete; the
  four half-written cells were discarded and all missing cells re-run with the same
  binary and seeds (a trial's seed depends only on arm, size, r, trial and family),
  so the resumed run equals an uninterrupted one. Every cell was then checked to
  contain exactly its registered number of trials, numbered 0 to n - 1.
- Raw cells are not committed. The repository's artifact policy
  (`docs/artifacts.md`) puts data-suffixed files over 64 KiB in the object store, and
  this session has no store credentials; CI rejected the first commit that carried them
  as tarballs (`artifacts` and `size` checks), and the tarballs were removed from the PR.
  What is committed instead: `cell_digests.sha256` (sha256 of all 380 raw cell files,
  checked against the files this analysis read), `cells_summary.csv` (trials, mean,
  standard deviation and censored count per cell, enough to recompute every mean and
  every interval except the bootstrap ones), `analysis_output.md` and `results.json`.
  The raw cells are exactly regenerable, because every seed is a function of
  (arm, size, r, trial, family): about an hour on four cores, then
  `sha256sum -c` against the manifest. If the raw cells should be kept, they can go to
  the store with `tools/artifacts/artifacts.py push` or the `artifact-autofix` label,
  which is a maintainer decision.
- Reproduce: `gcc -O2 -o rho_walk_sim rho_walk_sim.c -lm`,
  `./run.sh ./rho_walk_sim RAW_DIR 4`, `(cd RAW_DIR && sha256sum -c ../cell_digests.sha256)`,
  `python3 analyze.py RAW_DIR --json results.json`.
