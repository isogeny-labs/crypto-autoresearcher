# SA-09 REPORT: Heegner points and Euler-system norm relations as a free-relation source

(Saved by the main session verbatim from the resumed executor's final message; the harness refused the executor's own write. This replaces the pre-resume REPORT.md, whose large-B extrapolation came from a bug.)

## Summary

**Verdict: INCONCLUSIVE against the frozen criteria. The SUCCESS criterion clearly fails, the KILL criterion as written is not met, and the preregistered prediction ("genuine but rank-deficient free-relation source") holds.**

Deciding numbers:
- **Measured ratio.** rank/points = 45/189 = 0.238 at the largest scale reached (conductors {1,5,7,35}); 0.133 at {1,5,7}. Both far below the 1/2 threshold.
- **Extrapolation.** The character-count extrapolation over all inert-prime conductors up to B, corrected on resume, gives 0.159 at B = 35, 0.0755 at B = 10^3, 0.0723 at 10^4 and 0.0697 at 10^6. The ratio settles near 0.07: neither growing nor reaching 1/2.
- **Why not KILL.** The kill criterion is "rank/points -> 0, or no admissible p below 2^28". The ratio levels off at a positive constant of about 0.07, and admissible primes are plentiful: the smallest prime splitting completely in K[35] is 28211, and there are 482 below 2^21.
- **Why INCONCLUSIVE.** The frozen criteria have no outcome for a ratio that stays away from both 0 and 1/2. In practice the result is negative: the relations are exact, but they cannot replace the relation phase.

Other findings:
- **Exact verification mod p.** All 48 reduced norm relations at conductors {1,5,7,35} hold exactly in E(F_p) for each of 3 primes near 2^19 (144 of 144 checks). All 189 points are distinct.
- **Controls.** The wrong-embedding and random-subset controls fail, as they should.
- **No hidden relations.** LLL on the 189 complex Heegner points finds exactly 45 short relations and nothing else. At this scale the Kolyvagin norm relations are the complete small-coefficient relation module.

## What was run

**Setup.**
- Curve E = 36a1: y^2 = x^3 + 1, conductor 36, modular degree 1, so X_0(36) = E and phi(tau) = sum a_n q^n / n.
- Field K = Q(sqrt(-23)), class number h = 3. 2 and 3 split, so the Heegner hypothesis holds; beta = 11.
- 5 and 7 are inert in K, with a_5 = 0 and a_7 = -4. E has CM by Q(sqrt(-3)), so a_l = 0 for every l ≡ 2 mod 3.

Pipeline (scripts in this directory):
1. **Heegner points (`heeg.gp`).** For each conductor m, all h(O_m) Heegner forms and CM points tau, then phi(tau) via ellan and ellztopoint. h_m = 3, 18, 24, 144 for m = 1, 5, 7, 35.
2. **Norm relations in C (`nb_struct.py`, `build.py`).** The l+1 neighbours l·tau and (tau+j)/l of each level-n point are exactly the level-nl points, and their fibres partition that level. Each fibre sum equals a_l·phi(tau) modulo the period lattice. Residuals 1e-126 at 120 digits, 1e-700 at 700 digits, 1e-1616 for conductor-35 fibres at 1600 digits.
3. **Algebraisation (replaces ellheegner).** Points labelled by Pic(O_m); Lagrange interpolants f_d with f_d(x_e) = x_d; coefficients recognised in K with bestappr. Levels 1, 5, 7 at 400 digits (`data_157.json`); level 35 at 1600 digits (`build35b.py`, `data_35.json`): max error 1e-1558 with at most 446 digits vs a bestappr bound of 10^533. Restriction maps H_{n<-m} recognised the same way (5<-35 and 7<-35: error ~1e-1571, at most 433 digits).
4. **Reduction mod p (`fp.py`, `analyze.py`, `analyze35.py`).** p splits completely in K[35] iff 4p = X^2 + 23·35^2·Y^2; primes used 530251, 535481, 539009. A root of the level-35 class polynomial mod p is pushed down to levels 5 and 7 through H, then to level 1; both routes agree and each image is a root of the lower class polynomial. All 189 points evaluated; every relation checked with an independent integer group law.
5. **Relation rank (`nb_struct.py`).** Rank over Q of the relation matrix, computed mod a 61-bit prime from the exact neighbour lists.
6. **Char-0 hidden-relation control (`lll_rel.py`).** LLL (fpylll) on lattice coordinates of all points at 260 digits.
7. **Density and extrapolation.** `density.py`; `theory_table_v2.py` (supersedes `theory_table.py`; DEVIATIONS item 10).

## Results

### Table 1. Exact verification in E(F_p), levels 1,5,7 (`res_157.json`)

| p | #E(F_p) | on curve | distinct | 1>5 | 1>7 | wrong embedding (level 7, 12 tests) | random signed 8-subsets (20000; chance ~0.04) |
|---|---|---|---|---|---|---|---|
| 530251 | 528804 | yes | 45/45 | 3/3 | 3/3 | 0 pass | 1 pass |
| 535481 | 535482 | yes | 45/45 | 3/3 | 3/3 | 0 pass | 0 pass |
| 539009 | 539010 | yes | 45/45 | 3/3 | 3/3 | 0 pass | 0 pass |

### Table 1b. Exact verification in E(F_p), levels 1,5,7,35 (`res_35.json`, `analyze35.log`; added on resume)

| p | on curve | distinct | 1>5 | 1>7 | 5>35 (l=7, a=-4) | 7>35 (l=5, a=0) | wrong embedding (5>35, 108 tests) | random 8-subsets vs -4·y_5 (20000) |
|---|---|---|---|---|---|---|---|---|
| 530251 | yes | 189/189 | 3/3 | 3/3 | 18/18 | 24/24 | 0 pass | 0 pass |
| 535481 | yes | 189/189 | 3/3 | 3/3 | 18/18 | 24/24 | 0 pass | 0 pass |
| 539009 | yes | 189/189 | 3/3 | 3/3 | 18/18 | 24/24 | 0 pass | 0 pass |

The wrong-embedding control must run on an edge with a_l != 0. Relations with a_l = 0 read "fibre sum = O"; a wrong embedding only permutes fibres, so those hold under any embedding. A first version of `analyze35.py` used the 7>35 edge (a_5 = 0) and passed 144/144, exactly this effect; it was moved to the 5>35 edge.

### Table 2. Relation count and rank (`rank_table_comb.json`)

| conductor bound | levels | points N | relations | rank r | r/N |
|---|---|---|---|---|---|
| 1 | {1} | 3 | 0 | 0 | 0.000 |
| 5 | {1,5} | 21 | 3 | 3 | 0.143 |
| 7 | {1,5,7} | 45 | 6 | 6 | 0.133 |
| 35 | {1,5,7,35} | 189 | 48 | 45 | 0.238 |

The three dependencies at conductor 35 come from the diamond 1 -> 5 -> 35 versus 1 -> 7 -> 35. Figure: `fig_rank_ratio.png`.

### Table 3. Char-0 hidden-relation control (LLL; `lll_157.json`, `lll_full.json`)

| point set | points | short relations (norm < 10) | next vector norm |
|---|---|---|---|
| levels 1,5,7 | 45 | 6 | ~1e12 |
| levels 1,5,7,35 | 189 | 45 | ~3.9e4 |

The short vectors have the shapes of the Kolyvagin rows (norm 2.45 support 6; 4.69 support 14; 4.90 support 9), and their number equals the combinatorial rank 45.

### Table 4. Admissible primes (primes below 2^21 splitting completely in K[m]; `density.json`)

| m | h(O_m) | count / 155608 | observed | predicted 1/(2h) | smallest p |
|---|---|---|---|---|---|
| 1 | 3 | 25926 | 0.1666 | 0.1667 | 59 |
| 5 | 18 | 4291 | 0.02758 | 0.02778 | 719 |
| 7 | 24 | 3212 | 0.02064 | 0.02083 | 1163 |
| 35 | 144 | 482 | 0.00310 | 0.00347 | 28211 |

### Table 5. Extrapolation of rank/points (`theory_table_v2.json`)

N(B) = sum of h_m = 3·prod_{q|m}(q+1) over squarefree m <= B with all prime factors inert in K; R(B) = N(B) − sum 3m.

| B | 35 | 100 | 200 | 10^3 | 10^4 | 10^5 | 10^6 |
|---|---|---|---|---|---|---|---|
| levels | 7 | 20 | 34 | 148 | 1275 | 11281 | 102708 |
| R/N | 0.159 | 0.098 | 0.074 | 0.0755 | 0.0723 | 0.0703 | 0.0697 |

These are conjectural beyond the verified range: the count assumes the Euler-system relations exhaust the kernel and that every ring-class character component of the Heegner points is nonzero. The count agrees exactly with measured ranks at B = 5, 7 and with {1,5,7,35} (189 − 144 = 45), where LLL confirms it. Both sums are Selberg–Delange sums with main term of order B^2 (log B)^{-1/2}, so their ratio tends to a positive constant near 0.07 (sketched). The pre-resume table drifted to 0.149 at B = 10^6 because of an enumeration bug (only inert primes below 400 were used).

## Verdict reasoning

**SUCCESS** requires rank/points >= 1/2 and growing with the conductor bound. Measured 0.133–0.238; extrapolated values flatten at ~0.07. Not met.

**KILL** requires rank/points -> 0, or no admissible p below 2^28. Neither holds.

Without reinterpreting the criteria the verdict is INCONCLUSIVE, with this substantive reading:
- Obstruction (ii), tree-shaped relation graph: confirmed quantitatively; about 92% of points are never tied down by a relation.
- Obstruction (i), admissible-prime density: confirmed; density matches 1/(2h) within 10%.
- Obstruction (iii), generic target descent: not tested.

The prereg's "publishable curiosity" is achieved: nontrivial reduced Kolyvagin norm relations, including all 42 conductor-35 relations, were verified exactly in E(F_p).

## Limitations

- Toy CM curve 36a1 with X_0(36) = E; a_l = 0 for half the primes. y^2 = x^3 + 7 (conductor 1728) not run.
- One field K = Q(sqrt(-23)), conductors {1,5,7,35} only; larger B only via the conjectural character count.
- Recognition is numerical (bestappr at 400 and 1600 digits), not a proof; the exact F_p checks with failing controls make an error very unlikely.
- Conductor-35 neighbour lists come from 120 digits, spot-checked at 1600 digits and validated by every F_p check.
- The LLL control excludes only relations with coefficient norm up to ~10^4.
- No discrete-log consequence measured.
- Interrupted and resumed by a different model (DEVIATIONS 9).

## Suggested lead-atlas update

LEAD-ICP-heegner-norm-free-relations: "closed negative for the relation phase; verified curiosity", next_action none. Deciding number: rank/points = 45/189 = 0.238 at conductors {1,5,7,35}; the inert-conductor character count flattens at ~0.07 (0.0697 at B = 10^6) against the 1/2 threshold. All 48 norm relations up to conductor 35 verified exactly in E(F_p) for 3 primes near 2^19, with controls failing (0/108 and 0/60000). Caveat: CM toy curve; the non-CM, large-conductor case is untested.
