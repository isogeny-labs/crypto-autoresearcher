# SA-23 audit (main session, 2026-11-10/11)

An independent check of the executor's SA-23 report before its numbers are quoted anywhere. The verdict (KILL) stands. Two numbers behind it do not, and are replaced here by measurements; one anomaly is characterised further and stays open. Code in this directory is the main session's own (`lift2.py`, `count_sections.py`), not the executor's.

## 1. What was re-derived and holds

- **Gate A fit.** Refitting log2 S = alpha d + beta log2 p + gamma from the raw `results/cells.jsonl` gives alpha = 0.387 (executor: 0.387 [0.357, 0.413]). S is flat in p at fixed d (d = 12: 34, 34, 34, 34, 38, 38 at p = 47..131).
- **Enumeration correctness.** Two implementations (pure-Python scout, executor's C DFS) agree at every shared cell, and all 1,201 executor msolve lifts matched the enumeration tables. The d = 6 control (8 sections, rank 4, Gram determinant 16) is the A1^4 sublattice of E8 fixed by Frobenius for p = -1 mod 6: 8 roots, rank 4, determinant 2^4. Consistent.
- **Lift replication.** `lift2.py` (own system generator) at (47, 12): 0.048-0.096 s over 4 calls; executor median 0.053 s.

## 2. What does not hold

### 2a. The executor's u = 0.80 [0.76, 0.89] was not a measurement

All 22 d = 6 cells sit at the 4.6 ms msolve process-start floor (min 3.5 ms, max 13 ms across 880 calls). The fit of log2 T against U therefore has one informative point (U = 12) and a floor; the slope is an artefact. The only non-floor information above U = 12 in the executor's data is one call censored at 600 s.

**Measured here** (planted pull-back sections of the d = 6 surface under s = t^{d/6}, which exist in every cell; one msolve call each, `-t 1`, nice 10; host load recorded per call; 4 cores, at most 4 single-thread jobs at once):

| cell | U | S | wall time | note |
|---|---|---|---|---|
| (47, 12) | 12 | 34 | 0.05, 0.07, 0.06, 0.10 s | replication |
| (53, 18) | 17 | not enumerated | 329 s | elimination degree 11 |
| (71, 18) | 17 | not enumerated | 328 s, 796 s | two planted sections |
| (17, 18) | 17 | 240 | > 5,400 s | censored (executor: > 600 s) |
| (23, 24) | 22 | not enumerated | > 4,463 s | msolve killed by SIGKILL at 4,463 s; most likely memory on the 15 GB host (no dmesg access); lower bound |
| (29, 30) | 27 | not enumerated | > 3,099 s | same, lower bound |

Slope between U = 12 and U = 17 in the frozen family: log2(330/0.07)/5 = **2.4 bits per unknown** (2.7 with the 796 s call). The executor's 0.80 is replaced by u >= 2.4 on the measured range. Its censored (17, 18) point is consistent (u >= 2.6).

### 2b. Lift cost depends on the number of sections, not only on the number of unknowns

Same U = 12, same equations up to the field:

| cell | S | wall time of 7 calls |
|---|---|---|
| (47, 12) | 34 | 0.05-0.10 s |
| (37, 12) | 704 | 1.5, 27.9, 32.0, 260, 368, 374, 381 s |

A factor of 15 to 7,000 at the same U. This matters for the extrapolation: coverage of a group of size p needs S of order p, and every measured u comes from cells with S <= 240, so u is a lower bound on the slope in the covering regime. The executor's U-only cost model understates the lift there; the direction of the error strengthens the kill.

### 2c. The paper bound in the prereg (and the sentence in SUMMARY.md and the PR) misused the kissing-number constant

The prereg wrote "kissing number <= 2^{0.401 r}". The 0.401 is the Kabatiansky-Levenshtein asymptotic rate; at the ranks that matter here (7 to a few hundred) actual kissing numbers run 0.5 to 1 bit per dimension (kappa(8) = 240, kappa(24) = 196,560). The claim "even at the cap the exponent is >= 0.83" is therefore withdrawn. The corrected statement, with the measured u:

- Integral sections are minimal vectors (all fibres irreducible, height exactly 2 chi); disjoint 30-degree caps give kappa(r) <= C sqrt(r) 2^r, and r <= 12 chi - 4 = 2d - 4, so S < 2^{2d} up to lower-order terms: alpha < 2 for every surface in this class, whatever the prime.
- Covering p points then needs d >= (log2 p)/2 and U = 5d/6 + 2 >= 0.42 log2 p.
- With u >= 2.4 (measured, frozen family, and a lower bound by 2b), the total exponent is >= 0.42 x 2.4 = 1.0 > 0.5.

So the kill is independent of the surface family within this class, **conditional on one assumption: the lift solver's slope**. The only measured solver is msolve. A lift solver that is strongly sub-exponential in U on this structured system (one that uses the explicit lattice, say) is the single thing that could reopen it; none was tested.

Observed packing against the kissing cap: supersingular cells use 3-33% of kappa(r) (rank 7: 34/126; rank 16: 240/<=7,320); the ordinary rich cells pack near it (rank 8 at p = 109: 224/240; rank 12 at p = 37: 704/<=1,357).

## 3. The p = 37 anomaly: characterised, not explained

Ordinary cells at d = 12 (p = 1 mod 12), all by exhaustive enumeration:

| p | S | rank | (p-1)/d | 7 a square mod p |
|---|---|---|---|---|
| 13 | 8 | 3 | 1 | no |
| 37 | 704 | 12 | 3 | yes |
| 61 | 8 | 3 | 5 | no |
| 73 | 8 | - | 6 | no |
| 97 | 8 | - | 8 | no |
| 109 | 224 | 8 | 9 | yes |

Falsified: "p = 1 mod 36" (73 is 1 mod 36 and has 8), "p = 3d + 1" ((19, 6) has 8). Surviving, found by scanning about 20 quadratic, cubic, quartic and ninth-power characters of small integers, so it carries no evidential weight yet (about one false separator is expected by chance): the two rich primes are exactly those with 7 a square (equivalently, p = 1, 2, 4 mod 7). Prediction to test: (193, 12) rich, (157, 12) and (181, 12) poor. Each costs 3-8 h of exhaustive enumeration at 100 ns per leaf; not run. The anomaly does not bear on the verdict (Section 2c covers every prime).

## 4. Process notes

- The first audit chains were started with `nohup` from a tool shell and were killed when that turn ended; only two measurements survived. Everything above was re-run under the harness's persistent background mechanism (2 h cap per job), which is why U = 22 and 27 are bounds.
- The executor's end-to-end solves were on prime-order subgroups of order 3 to 29 (d | p + 1 makes p + 1 smooth); they verify the pipeline and say nothing about exponents.
- `lift2.jsonl` holds every call with t0, R, wall time, return code, elimination degree and host load; `enum_ordinary.log` the four new counts; `sections_109_12.txt` the 112 sections (up to sign) at p = 109; `count_sections.py` the scout enumerator and Gram code used for the rank at p = 109.
