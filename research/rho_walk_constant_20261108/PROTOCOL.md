# Protocol: walk-length constant of the r-adding negation-map rho walk versus jump count

Registered 2026-11-08, before any data. A smoke run of the simulator at 16 bits
and a few trials may precede registration as a gate; it is not a measurement
and is not reported as one. Every number in this directory is `[pcc:unverified]`.

Lead: `LEAD-RHO-matched-rho-calibration` (`knowledge/leads/ecdlp/generic/`).
Origin of the question: `isogeny-labs/isogeny-labs`
`research/ecdlp-prime-field-review-20261108.md` section 3.1, which recommended
raising the matched-rho jump table from 4 to 16 entries to 1,024 or more.
That recommendation is a claim under test here. It can be falsified.

## 1. Question

The matched rho in ecbench (`crypto` `src/cryptanalysis/ic_boundary.rs`,
`rho_jumps_for`: 4, 8, 16 jumps by size) measures 1.093 [1.033, 1.156] times
the floor sqrt(pi/4) at 32 to 48 bits, and its paired plain/negation ratio is
1.285 [1.177, 1.404] against an ideal sqrt(2) = 1.414. The lead asks whether the
excess is set-up cost or a real walk shortfall.

This study isolates the walk. It answers three separate things:

- Q1. With set-up and distinguished-point overhead excluded, how many group
  additions does an r-adding walk on the classes {P, -P} need per sqrt(n), as a
  function of r and of the 2-cycle policy?
- Q2. How much of the ecbench medium-tier constant is the walk and how much is
  elsewhere?
- Q3. Charging the table set-up as ecbench does, which r minimises total
  additions at each size, and how much cheaper is it than the r that
  `rho_jumps_for` selects? If the gain is under 2 percent at 32 to 64 bits, the
  review's recommendation to raise r is withdrawn.

## 2. Model

The group is Z_n, n prime, point s standing for s*G. Negation is s -> n - s,
the class of s is min(s, n - s), and N = (n + 1) / 2 classes. This is the exact
abstraction of a prime-order elliptic-curve walk for counting purposes: only
the group law and the negation automorphism enter, and a count is machine
independent. It says nothing about field arithmetic, canonicalisation or
hashing cost, which are the unpriced work of AGENTS.md section 5a and are not
measured here.

- Jumps: r values t_j drawn uniformly from [1, n - 1] at the start of each trial.
- Partition: j = (mix(class) >> 20) mod r, mix the splitmix64 finalizer.
- Step: u = c + t_j mod n; the next state is the class of u. The step is a
  negation step when u > n / 2.
- Walks: m = 256 independent walks from uniform random start classes, advanced
  round-robin. Start points are free (set-up excluded).
- Stop: the first time any walk reaches a class already visited by a different
  walk. Count: group additions executed by all walks up to and including that
  step. A same-walk revisit is not a collision.
- Cap: 64 sqrt(n) additions, as ecbench's `cap_multiple`. A capped trial is
  recorded as censored and counted at the cap; the censored fraction is
  reported per cell.

Arms (the 2-cycle policy):

- `plain`: no negation (state is s itself). Ideal constant sqrt(pi/2) = 1.2533.
- `neg0`: negation, no cycle handling.
- `neg1`: negation plus look-ahead: after a negation step to class q, if
  partition(q) equals the jump just used, redo the step with j + 1, up to 4
  tries; each attempted addition is counted (the rule of
  `ecc-challenges` `docs/negation-walk.md`).
- `neg2`: `neg1` plus cycle escape: each walk keeps its last 32 classes; when a
  new class equals one of them at distance L, advance to the cycle member of
  smallest class (L - 1 counted additions at most), then double it (one counted
  addition). The check itself is unpriced.
- `rm`: random-mapping control. The next class is a fresh hash-derived uniform
  class (r = n). Ideal constants as above with and without negation.

Ideal constants: neg 0.8862, plain 1.2533 (in additions per sqrt(n)).

## 3. Grid and sample sizes

- Sizes b in {20, 24, 28, 32, 36}: n the largest prime below 2^b.
- r in {2, 4, 8, 16, 32, 64, 128, 256, 1024}.
- Arms: `plain`, `neg0`, `neg1`, `neg2` at every (b, r); `rm` and `rm_plain` at every b.
- Trials per cell: 4000, 4000, 3000, 2000, 1000 for b = 20 .. 36. The standard
  deviation of the first-collision time is about 0.52 of its mean, so the
  standard error of a cell mean is about 0.8 to 1.6 percent.
- A/A: every cell is run under two disjoint seed families (A and B). Seeds are
  derived as splitmix64(base, arm, b, r, trial, family). Cells are independent
  functions of their seeds, so arm order and host load do not enter.
- Statistic: c = mean additions / sqrt(n), with a 95 percent bootstrap interval
  (2000 resamples over trials). Family A and B are pooled only after the A/A
  gate passes.

## 4. Gates, controls and predictions (fixed before data)

Gates. If a gate fails, the simulator is wrong and nothing else is read.

- G1 (instrument unbiased): `rm` mean c is within 2 percent of the ideal for
  negation (0.8862) and for plain (1.2533) at every size, and the 95 percent
  interval contains the ideal in at least 80 percent of the 10 cells.
- G2 (A/A): the ratio of family A to family B contains 1 at 95 percent in at
  least 90 percent of cells.

Positive control (the detector can see an effect). `neg0` at r = 2 and 4 is
trapped by fruitless 2-cycles (probability about 1/(2r) per step), so its c is
far above the ideal; the instrument must show it.

Predictions, one per hypothesis; each is wrong if its condition fails:

- H1. `neg0`, r = 4, b >= 24: c >= 1.30 x 0.8862 = 1.15.
- H2. `neg2`, r >= 32, b >= 24: c within 3 percent of 0.8862.
- H3. `neg2`, r = 16, b >= 32: walk excess c / 0.8862 in [1.02, 1.10].
- H4. Walk-only ratio c(plain) / c(neg2) at r = 16, b >= 32 is at least 1.30.
- H5 (against the review). The best r in Q3 is no more than 2 percent cheaper
  than `rho_jumps_for` at b = 32 and 40; it exceeds 2 percent only at some
  b >= 44, if at all. I expect the review's blanket recommendation to be
  partly wrong at medium sizes.

## 5. Decision rules

Let R16 = c(neg2, r = 16) / 0.8862 pooled over b >= 32, and M = 1.093
[1.033, 1.156] the ecbench medium constant.

- Q2 verdict `walk_near_ideal`: upper end of R16 interval <= 1.04. The excess
  in M is outside the walk (distinguished points, set-up, verification, the
  collision-resolution tail); a larger table does not shrink it.
- `walk_explains_most`: 1.04 < R16 <= M. Part of the excess is the walk.
- `walk_shortfall`: lower end of R16 interval > 1.12. Larger r is the fix.
- Q3 verdict from the Q3 table: total additions = c_neg2(r) sqrt(n) + S(r),
  S(r) = r x A(r), with A(r) = 1.5 x clamp(3 log2 r, 6, 12) additions per jump
  (a joint double-and-add of `jump_coefficient_bits(r)` bits, as in
  `ic_boundary.rs` `joint_mul`), c taken from the measured b = 36 value for
  larger sizes, and a separate row with full-width jumps (A = 1.5 b) as in
  `ecc-challenges`. Report the argmin r and the saving over `rho_jumps_for`
  for b = 24, 32, 40, 48, 56, 64.

## 6. Limits stated in advance

- Counts only. No timing, no field arithmetic, no cache or memory behaviour.
- Distinguished-point overhead, collision-resolution tail and verification are
  excluded. The model does not reproduce ecbench's S; it bounds the walk part.
- The partition hash is an ideal mixer. Real partitions use coordinate bits;
  a biased partition is a separate question.
- The abstraction is exact for counting in a cyclic group with a negation
  automorphism and a random jump table. It does not cover automorphism groups
  larger than {1, -1}, so it says nothing about j = 0 or j = 1728 curves.
- No claim here changes a lead disposition, an ecbench bound or a leaderboard
  row. The ecbench reseal remains a separate replayed study.

## 7. Amendment 1 (2026-11-08, before any data; found while writing the simulator)

No simulator output existed when this was written. The registered commit of
sections 1 to 6 is recorded in `PROTOCOL.commit`.

Defect in section 2. With m = 256 free start points, the starts are a large
share of all points at small sizes (256 of about 1,000 at 20 bits). They sit in
the visited table at no cost, so the first repeat arrives earlier and the
instrument would read low by construction. The gate G1 could not pass at 20 bits.

Changes:

- m = 16 walks, not 256. Starts are drawn distinct (a duplicate start is redrawn).
- The ideal for additions is corrected for the free starts. Let
  I(b, arm) = sqrt(pi N / 2) + 2/3 - m, with N = (n + 1) / 2 for negation arms
  and N = n for plain arms (the birthday expectation counts the m starts as
  points). The statistic used in every hypothesis, gate and rule is
  R = (mean additions) / I(b, arm). At 32 bits and above the correction is
  below 0.03 percent.
- Wherever sections 4 and 5 use c / 0.8862 or c / 1.2533, read R. The numeric
  thresholds are unchanged. `R16` of section 5 is R for `neg2` at r = 16.
- G1 uses R in place of c for the `rm` arms: within 2 percent of 1.

No prediction, threshold or decision rule is changed.

## 8. Amendment 2 (2026-11-08, before any grid data)

Disclosure of what was seen first. The smoke gate at 16 bits (300 trials per
arm, seed family 9, not the grid) printed mean additions of 221.5 (`rm`), 327.4
(`rm_plain`), 317.4 (`plain`, r = 16), 232.7 (`neg2`, r = 16) and 13,135.9
(`neg0`, r = 4, 240 of 300 censored). A second design check then ran the two
null arms only, at 20, 24 and 28 bits with several m (family 7). No grid arm
other than those one-off 16-bit lines was run.

Finding. The `rm` null reads 2 to 5 percent above the plain birthday value
with m = 16. Two design effects, both predictable, explain it: the free start
points lower the count (the m starts are points), and same-walk repeats are not
collisions, so about 1 in m colliding pairs is discarded, which raises the
count by about 1 / (2m). The corrected null
I''(b, arm, m) = (sqrt(pi N / 2) + 2/3 - m) / sqrt(1 - 1/m)
matched the `rm` and `rm_plain` means within 1.7 percent in all 14 checked
cells (standard error about 1 percent each).

Changes (supersede the corresponding lines of sections 2 and 7):

- m = 64 walks at every size.
- Primary statistic R(arm, b, r) = mean additions of the arm divided by the
  mean additions of its matched random-mapping null at the same b and m
  (`rm` for `neg0`, `neg1`, `neg2`; `rm_plain` for `plain`), pooled over seed
  families after the A/A gate. Design effects cancel in this ratio. The
  confidence interval resamples trials in both the arm and the null.
- G1 becomes: each `rm` and `rm_plain` mean is within 3 percent of I'' at every
  size, and its 95 percent interval contains I'' in at least 80 percent of the
  10 cells.
- Every threshold in sections 4 and 5 keeps its number and is read on R.
  R16 is R for `neg2`, r = 16, pooled over b >= 32. The ratio
  c(plain) / c(neg2) of H4 is R-adjusted: R_plain_ratio = (mean_plain /
  mean_neg2) divided by (mean_rm_plain / mean_rm), which equals 1.414 when both
  arms are ideal in the large-m limit.
- The comparison with the ecbench constant M in Q2 is approximate: ecbench's M
  is measured against the large-m floor, and this study's R is against a
  finite-m null. At m = 64 the two differ by under 1 percent for b >= 28.
