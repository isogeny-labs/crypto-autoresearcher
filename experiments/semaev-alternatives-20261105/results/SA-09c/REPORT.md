# SA-09c REPORT: Heegner relations at conductor bounds up to 4000, 43a1 and 53a1, and rare-hit descent at p ~ 2^30

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary

**Verdict: KILL against the frozen criteria, with one flagged borderline in the descent primary run (below).**

Deciding numbers:
- **37a1, K = Q(sqrt-7).** Exact rank of the Kolyvagin norm-relation matrix gives rank/points = 7078/51513 = 0.1374 (B = 750), 12622/93317 = 0.1353 (1000), 26171/205217 = 0.1275 (1500), 45608/365969 = **0.1246 (B = 2000)**. Extra: 186954/1398715 = 0.1337 at B = 4000. Over every integer B in [750, 4000] (3251 values) the ratio stays in [0.1236, 0.1396]; 0 values are outside [0.12, 0.15]. Maximum 0.1396 (B = 753). SUCCESS (>= 1/2) is far away.
- **Second curves, same field.** 43a1 and 53a1 (43 and 53 both split in Q(sqrt-7), h = 1): rank/points = 0.1353 at B = 1000 and 0.1246 at B = 2000. This is identical to 37a1, because the rank depends only on class-group data (see Limitations). Below 0.15 at the largest B.
- **Descent at p ~ 2^30** (37a1, 49 Heegner points of conductors 1, 3, 5, 13, 15, three primes, all 13 relations verified on each prime): the primary run had 16 hits in 60000 targets against a control mean of 9.14 (exact expectation 9.04). An independent replication with 10 times more targets had 96 hits in 600000 against 91.2 (exact 90.4). Set sizes agree: |U| = 161799 for Heegner points against 161788 ± 13 for random sets on the first prime.
- **Descent flag.** The primary run alone is a 2-sigma upward fluctuation (one-sided Poisson p = 0.023, two-sided 0.046). Its one-sample 95% Garwood interval [9.145, 25.98] excludes the control mean 9.14 by 0.005 hits. The two-sample difference interval [-2.97, +16.7] hits includes 0. It was not reproduced in the replication (p = 0.29). The true hit rate is fixed by |U|/#E, which is equal for both sets to four digits.

## What was run

SA-09b's directory was read only; `arith.py`, `fpg.py` and `data37c.json` (exact Heegner data for 37a1, 800 digits) were copied.

1. **Rank pipeline to B = 4000** (`arith2.py`, `gen_rows.py`, `rank_sparse.cpp`, `table.py`).
   - Fibres of Pic(O_{nl}) -> Pic(O_n) come from binary quadratic forms (SA-09b's validated `project`). The reduced-form enumeration is vectorised in numpy; it gives identical output to the old routine on 7 test discriminants, and the class number matches PARI qfbclassno at m = 1995.
   - Relation rows: sum of fibre points − a_l·P(n, class) = 0, for every conductor n and every inert prime l with nl <= B.
   - Rank by exact sparse Gaussian elimination mod the prime 2147483629 in C++ (leading column = highest level). Rows are added in increasing level, so one pass gives the rank for every B. This replaces SA-09b's random projection. Memory under 200 MB, generation 100 s, elimination under 2 s.
   - Reproduces SA-09b exactly: 12 (B = 15), 99 (65), 233 (130), 1566 (300), 3050 (500).
   - Runs: 37a1 to B = 2000 and B = 4000; 43a1 ([0,1,1,0,0]) and 53a1 ([1,-1,1,0,0]) to B = 2000, all with K = Q(sqrt-7).
2. **Controls for the rank code** (B up to 500). Random nonzero a_l gives the identical rank (3050). Randomly shuffled fibres give rank 1639 at B = 300 and 3162 at B = 500, against 1566 and 3050, so the computation is sensitive to the fibre structure.
3. **Descent** (`pts30.py`, `descent30.py`, `analyze_descent.py`).
   - Primes satisfy 4p = X^2 + 7·195^2·Y^2, so they split completely in the ring class field of conductor 195. Five were found in [2^30, 2^30 + 2^28]: 1073785189, 1073805769, 1073816251, 1073820199, 1073904259.
   - E(F_p) is cyclic only for the middle three, which were used. The other two have group Z/4 × Z/268447888 and Z/6 × Z/178974144 and would handicap the Heegner set. The choice used group structure alone, before any hit was computed.
   - The 49 points of conductors {1, 3, 5, 13, 15} were reduced mod p. On each prime they are on the curve, all 49 are distinct, and all 13 norm relations hold (39/39). The points generate E(F_p).
   - A hit means the target R is a signed sum of at most 3 elements of S, repeats allowed. U(S) is the set of all such sums (about 1.6e5 elements), and hit <=> R in U(S).
   - **Primary (frozen design):** 20000 uniform random targets per prime, 3 primes (60000 targets). Control = 100 random sets of 49 points of E(F_p) per prime, on the same targets.
   - **Replication (added, see DEVIATIONS):** 200000 fresh targets per prime (600000 total), 40 control sets per prime.
   - **Exact-rate comparison:** targets are uniform, so the expected hit rate is |U(S)|/#E, compared for the Heegner set and the 100 control sets per prime.

## Results

### Table 1. rank/points, K = Q(sqrt-7) (`results_rank_ratio_table.csv`, `rank_*.json`)

| B | points N | relations | rank | rank/N | character count N − sum m | 43a1 and 53a1 rank |
|---|---|---|---|---|---|---|
| 500 | 22813 | 3204 | 3050 | 0.1337 | 3050 | 3050 |
| 750 | 51513 | 7429 | 7078 | 0.1374 | 7078 | 7078 |
| 1000 | 93317 | 13174 | 12622 | 0.1353 | 12622 | 12622 |
| 1250 | 146625 | 20231 | 19361 | 0.1320 | 19361 | 19361 |
| 1500 | 205217 | 27266 | 26171 | 0.1275 | 26171 | 26171 |
| 1750 | 278855 | 36807 | 35317 | 0.1267 | 35317 | 35317 |
| 2000 | 365969 | 47379 | 45608 | 0.1246 | 45608 | 45608 |
| 2500 | 530827 | 70374 | 67855 | 0.1278 | 67855 | (not run) |
| 3000 | 770063 | 101046 | 97397 | 0.1265 | 97397 | (not run) |
| 3500 | 1055433 | 143543 | 137924 | 0.1307 | 137924 | (not run) |
| 4000 | 1398715 | 194692 | 186954 | 0.1337 | 186954 | (not run) |

The rank equals the character count N − h_K·sum(m) at all 44 (curve, B) values computed. Scan over all integer B in [750, 4000]: min 0.1236 (B = 2281), max 0.1396 (B = 753). The saw-tooth continues within the predicted band. The relation count stays at 13–14% of N, so most points are unrelated.

Controls (B = 300 / 500): random nonzero a_l gives 1566 / 3050 (unchanged); shuffled fibres give 1639 / 3162.

### Table 2. Descent at p ~ 2^30, 37a1 (`descent30_*.json`, `descent30rep_*.json`, `descent30_summary.json`)

| run | targets | Heegner hits (per prime) | control mean hits | exact expectation | 95% interval for Heegner hits (Garwood) | difference (hits), 95% normal | p one-sided vs exact |
|---|---|---|---|---|---|---|---|
| primary | 60000 | 16 (5, 3, 8) | 9.14 | 9.04 | [9.15, 25.98] | +6.9, [-3.0, +16.7] | 0.023 |
| replication | 600000 | 96 (38, 35, 23) | 91.2 | 90.4 | [77.8, 117.2] | +4.8, [-22.0, +31.6] | 0.29 |
| combined | 660000 | 112 | 100.3 | 99.4 | rate [1.40e-4, 2.04e-4] | | 0.115 |

Control sets with a hit count at least as large as Heegner's (pooled over primes): 1.9% (primary), 30% (replication).

| p | #E | \|U\| Heegner | \|U\| control mean ± sd (100 sets) | fraction of controls with \|U\| at least Heegner's |
|---|---|---|---|---|
| 1073805769 | 1073788990 | 161799 | 161788 ± 13 | 0.51 |
| 1073816251 | 1073809588 | 161779 | 161775 ± 82 | 0.81 |
| 1073820199 | 1073781160 | 161799 | 161791 ± 11 | 0.60 |

161799 is the largest |U| seen in any set, Heegner or control; the Heegner set reaches it on two primes, so the 13 known relations create essentially no collisions among sums of at most 3 points. Not proved to be the all-distinct maximum.

Figure: `fig_09c.png` (left: rank/N vs B to 4000 with prediction band and the 0.15 line; right: descent hit rates).

## Verdict reasoning

- **SUCCESS** needs rank/points >= 1/2 at some B >= 750, or a descent hit rate above control with a 95% CI excluding equality. The rank maximum over 3251 values of B is 0.1396. For the descent, the primary run is borderline under one interval convention (flag); the replication and the exact-rate comparison show no difference. Not met.
- **KILL** needs (a) rank/points < 0.15 at every B >= 750 on 37a1: max 0.1396 for all integer B up to 4000; (b) rank/points < 0.15 at the largest B on the second curve: 0.1246 at B = 2000 on both 43a1 and 53a1; (c) descent not above control: 112 hits against 99.4 expected on the pooled 660000 targets (p = 0.115), and |U| equal within 0.01%. All met.
- **Flag.** On the primary 60000 targets alone, the one-sample Garwood interval excludes the control mean (lower end 9.145 vs 9.14), p = 0.046 two-sided. The two-sample difference interval, which also counts the control's noise, includes 0. The executor read the criterion with the two-sample interval plus the replication; a one-sample reading of the primary run alone would satisfy SUCCESS's descent clause. The excess did not replicate, and the expected hit rate |U(S)|/#E is equal for Heegner and control within 1e-4 relative.
- The prediction (rank/points in [0.12, 0.15] for B >= 750; descent equal to control) held.

## Limitations

- The rank is of the Euler-system norm-relation matrix built from class-group fibres, not of the full relation module among the actual points. SA-09b validated the fibres against complex-analytic Hecke neighbours (17/17 edges, conductors up to 65). Exact F_p verification covers conductors up to 15 only (here at p ~ 2^30 on three primes, 39/39).
- Rank mod a 31-bit prime is at most the rank over Q; it matched the character count at all 44 tested values, with no characteristic-0 certificate.
- 43a1 and 53a1 give exactly the same ranks as 37a1: the rank depends only on class groups and on whether a_l is zero. They add no independent evidence about different Heegner points; no Heegner points of 43a1 or 53a1 were computed. The prereg's second-curve clause is met only for the ranking quantity.
- Descent used only the 49 points of conductors up to 15. A larger verified set would reach more targets (|U| grows like |S|³/6), but the hit rate is still |U|/#E by uniformity.
- The test cannot detect an advantage smaller than about 40% in hits at 60000 targets, and about 15% at 600000.
- Only sums of at most 3 points were tested. No discrete-log consequence was measured.

## Suggested lead-atlas update

LEAD-ICP-heegner-norm-free-relations: stay "closed negative", next_action none. Conductor bound for the non-CM curve pushed from 500 to 4000; 43a1 and 53a1 covered in the same field. Deciding numbers: 37a1 rank/points = 0.1246 at B = 2000 and 0.1337 at B = 4000; in [0.1236, 0.1396] for every integer B in [750, 4000]; equals the character count at all 44 points tested. Rare-hit descent at p ~ 2^30: 112 hits in 660000 targets against 99.4 expected; |U| = 161799 against 161788 ± 13. The primary 60000-target run alone was a nominal 2-sigma excess (p = 0.046) that did not replicate. Untested: exact verification and descent with Heegner points of conductor above 15.
