# Round-3 validation report

Validator: independent session, Sonnet 5.5. Nothing in the repo was edited; every output went to the scratchpad.

**Validated commit:** `c104ec603dae36d126d1629ee4d2a791fa4ba8c9`, branch `ideas/hpseudo-symnull-20261104`.

* The checkout is sparse and shallow (no merge base with `origin/main`).
* The three report directories and the two lead files are byte-clean against HEAD.
* `git status` shows exactly one modified file, `docs/reports/quadphase-20261104/rows.jsonl`. That is another experiment's live output and out of scope.
* Frozen scripts were run only with `PYTHONDONTWRITEBYTECODE`, outputs to scratchpad.
* Environment here: Python 3.13.18, numpy 2.5.3.
* My scripts are in `/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/val/` and `.../i1/`, `.../h1/`.

Scope: none of the three studies is a cost claim, a cross-method ECDLP comparison or a discrete-log/relation/closure claim. The certificate, matched-rho, 5a band, m=83/ECC2K-130 rules are therefore not applicable. The independent-recomputation substitutes are listed per item.

## Dispositions

| item | frozen verdict | disposition | wording |
|:--|:--|:--|:--|
| 1 H-PSEUDO symnull | EXPLAINED | **validated** | corrections required to the interpretive text (below) |
| 2 weakclass-20261104 | I1 INVALID, I2 and I3 BLIND | **validated** | minor corrections |
| 3 weakclass-i1 | controls valid, all BLIND, overdispersion CALIBRATED | **validated** as frozen outputs | two interpretive claims are unsupported as written and need correcting |
| 4 README/lead text | | **partial** | list of required corrections at the end |

## Item 1: `docs/reports/hpseudo-symnull-20261104/` (EXPLAINED): CONFIRMED

| requirement | result | evidence |
|:--|:--|:--|
| `experiment_protocol.py validate protocol.json` | pass, 0 findings | run from repo root |
| protocol body hash = `freeze.protocol_sha256` (`cf0525…b135`) | pass, and identical at the draft commit `f9931a3e0`, the freeze commit `e518970c9` and HEAD | `protocol_hash()` on the three blobs |
| script hashes vs protocol | pass: `hpseudo_symnull.py` `191e6e00…`, `analyze_symnull.py` `edc43c2a…` | `sha256sum`; `git diff f9931a3e0 HEAD` on both scripts is empty |
| frozen before data | pass. Freeze 05:39:48Z; first data snapshot `96dfd77b4` 05:52:49 | commit times |
| `rows.jsonl.xz` vs `data.sha256` | pass: `4eb3df98…c65b` | decompressed sha256 |
| row inventory | 1358 = 56 EC_recorded + 1120 N_sym + 160 N_asym + 4 planted + 18 EC_replay | counted |
| duplicates | none. 1358 distinct (arm, instance, replicate); every one of the 56 instances has draws 0..19 exactly once; N in every N_sym row equals its instance's N | script `h1` checks |
| history | the 1300-row snapshot (`a65b02390`) and the 1301-row snapshot (`922389857`) are exact prefixes of the final file, so pool-phase rows were not altered. The 36 completion rows are lines 1301–1336 | `git show` and prefix compare |
| decisive set | pass. The 24 `out_of_sample` instances are exactly curve_index 8..19 at bits 20 and 22. The 32 `calibration` instances are exactly curve_index < 8 at the four rungs. The `sample` label equals (curve_index < 8) for all 56 | recomputed from the rows |
| calibration set = recorded R_mean set | pass. Mean C_EC over curve_index < 8 equals `per_rung.C_EC_mean` at all four rungs (to 1e-5) | `raw-result.json` |
| `EC_recorded` vs `raw-result.json` | pass. 56/56 equal on C, N, p, F_size | compared field by field |
| `raw-result.json` self-digest | pass: `22334cb0…` re-derived | sha256 of the canonical JSON |
| verdict recomputed | pass (below) | `h1_verdict.py` |
| 3 N_sym draws re-derived | pass, **exact** (below) | `h1_redraw.py` |
| `complete_run.py` deviation | pass (below) | |
| all four validity controls | pass | recomputed from rows |

**Verdict recomputation.** I used my own code: per-curve R_sym = C_EC / mean of its 20 N_sym draws, then the per-rung mean, and my own bootstrap (seed 987654321, 20000 resamples).

| set | n | mean R_sym | my 95% CI | frozen CI |
|:--|--:|--:|:--|:--|
| 2^20 OOS | 12 | 1.0403 | [0.9992, 1.0915] | [0.9991, 1.0924] |
| 2^22 OOS | 12 | 0.9932 | [0.9725, 1.0167] | [0.9722, 1.0170] |
| calibration 2^20 | 8 | 1.0118 | [0.961, 1.061] | |
| calibration 2^22 | 8 | 0.9866 | [0.954, 1.033] | |
| calibration 2^24 | 8 | 0.9745 | [0.948, 0.9997] | |
| calibration 2^26 | 8 | 1.0087 | [0.990, 1.036] | |

* The frozen EXPLAINED rule is met at both decisive rungs.
* Re-running the frozen `analyze_symnull.py` gives a `verdict.json` byte-identical to the committed one.
* The 2^20 verdict is not an artefact of the percentile bootstrap. The t-interval is [0.986, 1.095], also containing 1.
* Validity values:
  * V1: 0.06%, 0.18%, 0.81%, 0.94% (limit 2%).
  * V2: planted C = sqrt(512) = 22.63, which is 3.98, 3.78, 3.54, 3.73 times the rung's largest symmetric draw (limit 3).
  * V3: max relative replay error 1.04e-7, 18/18 negation-closed.
  * V4: 1.67%, 0.99%, 0.28%, 0.37% (limit 2%).

**N_sym re-derivation (exact).** I wrote my own draw code from the docstring and `derive_seed(protocol_sha, "N_sym", str(instance), draw)`. It does not import the producer's `job()`.

| instance (bits, curve_index, N) | draw | recomputed C | recorded C | result |
|:--|--:|:--|:--|:--|
| 13 (20, 13, 111751) | 0 | 4.359721744006891 | 4.359721744006891 | exact; a non-FFT direct sum differs by 0 |
| 9 (20, 9, 111893) | 7 | 4.079413849179094 | 4.079413849179094 | exact; direct sum differs by 1.8e-15 |
| 10 (20, 10, 112129) | 19 | 4.122322195927521 | 4.122322195927521 | exact; direct sum differs by 0 |

**A completion-phase row, N = 33,570,083.** I evaluated this row by an independent route that stays under 1 GB.

* The row is instance 50 (bits 26, curve 2), draw 3, file line 1304.
* I computed the statistic from a cosine table and 256 gathers per frequency, with no FFT.
* Recomputed C = 5.247426857275353; recorded 5.247426857275352; relative difference 2.2e-16.
* So the completion rows are the values the frozen `job()` produces from the frozen seeds.

**Independent replay of all 24 decisive curves.**

* The study's own replay covered only 18 *calibration* curves (curve_index < 8, plus the smallest-N curves at 2^24 and 2^26). It covered none of the decisive curves.
* I replayed all 24 decisive curves with my own elliptic-curve code (`h1_replay.py`), not the producer's `run_character_sum_ladder`.
* The method: enumerate the multiples of G, take the 512 smallest (x, y), compute the logs, and take the FFT maximum.
* Result: every C_EC matches the record (relative error at most 1.2e-7, which is the 6-decimal rounding of the record).
* Every one of the 24 factor bases is negation-closed. This closes a gap in the study. The negation-closure premise that justifies the symmetric null is now verified directly on the decisive set.
* Reasoning also holds structurally: all N are odd, so there are no 2-torsion points and the (x, y)-sorted prefix of even length 512 cannot split a ±y pair.

**`complete_run.py` deviation.**

* The script's sha256 is `92cf24b4…`. It imports the frozen `hpseudo_symnull` and calls `H.job((sha, "N_sym", i, N, d))` on exactly the (instance, draw) tuples that are missing from the file.
* The 36 missing tuples are instance 50 draws 0–19 and instance 51 draws 0–15. The 4 survivors of the pool phase are instance 51 draws 16–19 (file lines 59–62).
* The lost tasks all belong to two bits-26 *calibration* curves (N = 33,570,083 and 33,563,609, both prime). The decisive data (bits 20/22 OOS) was complete before the hang, so the hang cannot have steered the verdict.
* The planted and replay blocks are textually identical to `main()` apart from one comment and added `out.flush()` calls (diff checked).
* Planted and replay rows occur exactly once, after the completion rows.
* The final file has no duplicates (see the table above).
* Not verifiable by me: the `dmesg` OOM claim (about 5 GB per worker). The structural facts are consistent with it.

**Corrections required for item 1.**

1. README: "reproduces the recorded C_null_mean to within 0.9%". The maximum is 0.935% (rung 26). Write 0.94%, or "within 1%".
2. README results table: the column "mean u_sym" mixes populations.
   * Rungs 20 and 22 average 20 curves (8 calibration + 12 OOS). Rungs 24 and 26 average 8 curves.
   * Split values: rung 20: 0.550 (calibration), 0.663 (OOS); rung 22: 0.356 (calibration), 0.467 (OOS).
   * Label the column or split it.
3. Overreach in the headline and the lead.
   * Statements affected: "R is 1 within about 0.04 at every rung", "no constant offset", "the small-x factor base **is** a random negation-closed set".
   * The frozen rule is a non-rejection rule. The 2^20 OOS interval is [0.999, 1.092] and does not exclude +9%.
   * The 2^24 calibration interval [0.948, 0.9995] lies below 1.
   * Dropping the single high curve (index 17, R = 1.27) moves the 2^20 OOS mean to 1.020. The pooled 56 curves give 1.005, SE 0.008. Pooled OOS (24 curves) is 1.017, SE 0.014.
   * Suggested wording: "consistent with R = 1; upper 95% bound 1.09 at 2^20 OOS and 1.02 at 2^22 OOS; statistic is the B = 512 maximum character sum of the small-x set only."
   * The README does already carry the 2^20 caveat in its Results bullets. The headline, the lead and the Consequence section do not.
4. The README cites "commit f9931a3e" as the freeze. That is the draft commit and the parent of the freeze commit `e518970c9`. This matches the protocol's `freeze.commit` field, so it is cosmetic.
5. Binding gaps (low risk because the values reproduce bit-for-bit here):
   * The protocol records no hash for `raw-result.json` (`e590e48d…`) or for `run_character_sum_ladder.py` (`d63c9023…`).
   * The protocol declares `measurement.record = [python_version, numpy_version, script_sha256]`. No row, verdict or log in any of the three studies contains a python or numpy version. This applies to all three studies.
6. The "no S3 checkpoint / owner approval" statement cannot be verified from the artifacts. Cite where the approval is recorded.

## Item 2: `docs/reports/weakclass-20261104/` (I2, I3 BLIND; I1 INVALID): CONFIRMED

| requirement | result |
|:--|:--|
| protocol validate | pass, 0 findings |
| protocol hash `472123ac…` | pass |
| script hashes | `weakclass.py` `ad46671e…`, `weak_curves.py` `5477558a…`, `qtt_core.py` `3b467fe6…`, `analyze_weakclass.py` `f4deef80…` all match the protocol |
| frozen before data | freeze 05:52:20Z; first (empty) snapshot 05:52:49 |
| frozen analysis recomputed from `rows.jsonl` | pass; running the frozen analyzer reproduces `verdict.json` byte-identically |

My own implementation of the cell rule gives:

* I1: INVALID ×3. The A/A gate fails on 5 of 54 curves (>5%), maximum 8.9%, median 2.3%, 95th percentile 6.6%. This matches the README.
* I2: BLIND ×3.
* I3: BLIND ×3.
* Positive controls: 54/54 for I1 (u = 1.00) and I2 (u = 0.00), 18/18 for I3 (u = 0.00).
* Mean u values match the README to 2 decimals: I1 0.61, 0.41, 0.12; I2 0.56, 0.44, 0.64; I3 0.36, 0.44, 0.60.
* Had the gate been ignored, I1 class C would have returned DETECTS (low at L = 10 and L = 14). The README says so in substance.
* The gate was ill-posed by construction. With 20 + 20 draws the per-curve relative sd of the mean difference is about 3%, so about 11% of curves exceed 5%. This is the README's argument and the data agree.

**Curve properties (all 54 curves).**

| class | property | result |
|:--|:--|:--|
| A | n = p | 9/9 |
| B | n prime, ord_n(p) <= 6 | 9/9; orders 6,4,3,5,5,6,5,6,4 (so k = 3 to 6 as stated) |
| C | a = 0, p ≡ 1 mod 3, b ≠ 0, n prime, n ≠ p | 9/9 |
| D | a ≠ 0, b ≠ 0, n prime, n ≠ p, ord_n(p) > 6 | 27/27 |
| all | each D shares its p with its weak partner and has a different order; p in [2^(L-1), 2^L); discriminant nonzero; Hasse bound | all hold |

**Independent point counts.** I counted points by the Euler criterion (no lookup tables). All 18 curves at L = 10 and 3 at L = 14 (A and B) match the recorded n. For each, n·P = O holds for a point P. Zero mismatches.

**Full recomputation of 16 curves.** I rebuilt the discrete-log table, the factor base (including the zeta-orbit rule for class C), the maximum character sum by a direct non-FFT sum, the m = 2 sumset by Python sets, and the 40-draw nulls from `derive_seed`.

* Instances covered: 0, 1, 8, 10, 12, 14, 18, 24, 30, 36, 38, 42, 44, 47, 49, 53, across A, B, C, D and L = 10, 12, 14.
* I1 and I2 agree to 9 digits and u agrees exactly, on all 16.
* I3 (QTT) values were **not** recomputed. Each matrix needs about 2.4 s, with 41 matrices per curve.

**Descriptive claims in the README.**

* The j = 0 pattern "u = 0, 0, 0 at L = 10 and 0, 0.05, 0.03 at L = 14" is confirmed.
* The statement "about 10 of 27 ordinary curves at the marks" is confirmed (10 at u <= 0.05 or >= 0.95; 5 strictly beyond).

**Corrections.**

1. "against about 12% expected": with 40 draws and a mid-rank u, the exact two-sided null rate at these marks is 6/41 = 14.6%. That gives 3.95 expected of 27, and P(X >= 10) = 0.0035, not 0.0007.
2. I3: 8 of the 18 L = 10 curves have a degenerate null. The curve's statistic equals the null constant, so u = 0.5 comes from the tie rule alone.
   * Per class (class curves): A 1/3, B 1/3, C 2/3; the paired ordinary curves are 1/3, 1/3, 2/3.
   * The I3 "mean u" values are therefore tie-dominated, and the instrument is at its rank ceiling at p ≈ 2^10 for random labellings.
   * BLIND stands: any weak curve below the ceiling would have scored u = 0 and could have triggered DETECTS. But the README should state the saturation and that I3 is a single size (L = 10) with 3 curves per class.
3. Observation 1 attributes the C-low shift to zeta-closure ("not the DLP's ease"). The rerun (item 3) shows the paired ordinary curves are equally low, so the class-specific reading is unsupported.

## Item 3: `docs/reports/weakclass-i1-20261104/` (all BLIND, CALIBRATED): FROZEN OUTPUTS CONFIRMED, interpretive text needs correction

| requirement | result |
|:--|:--|
| protocol validate; hash `dd559662…` | pass |
| scripts | `weakclass_i1.py` `3fcdbe8c…`, `analyze_i1.py` `6b1f2957…` match the protocol. `weakclass.py`, `weak_curves.py`, `qtt_core.py` are byte-identical to the first-run files and match the protocol hashes |
| frozen before data | freeze 06:20:27Z; `run.log` written 06:20:53 |
| `rows-r3.jsonl.xz` | decompressed sha256 `e69fec18…` equals `data.sha256` |
| full-precision rows | **not archived**. I re-ran the frozen script: 24 s on one core, 144 rows, sha256 `23884f55…` equals the recorded hash **bit-for-bit** |
| rounded vs full | `rows-r3` equals the 3-decimal rounding of the full null in all 144 rows, with every other field identical |
| analyzer output | on both the rounded and the full-precision rows it gives a `verdict.json` byte-identical to the committed one |
| composition | 144 = 54 picked (A, B, C = 9 each, D = 27) + 90 extra ordinary (class E) |
| class properties | all 144 curves satisfy their class definitions |

My own 144-row recomputation (before the independent KS and binomial checks):

* Positive control: u >= 0.95 on 100% of curves.
* Class mean u: A 0.458, B 0.437, C 0.276.
* No class extreme at any size, so BLIND ×3.
* Overdispersion: 11 extreme (2 low, 9 high) among 90.
* Nine independently recomputed rows (A, B, C, D, E at L = 10, 12, 14) reproduce I1 and u exactly, and all 200 rounded null draws match.

**KS routine against a reference I wrote.**

* The D statistic equals mine on all 144 curves (difference 0).
* Reference p-value: exact two-sample distribution for n = m = 100 by lattice-path DP, no ties. The routine's p differs from it by at most 0.027.
* The routine is the asymptotic Kolmogorov law with Stephens' correction. It is mildly liberal at D = 0.19: p = 0.047 where the exact value is 0.0539. Its false-rejection rate on continuous data is therefore 5.4%. My simulation gives 5.3%; the README says 6.0%.
* Power against a 0.5 SD shift: 86.7%, matching the README's 87%.
* Of the 7 A/A rejections, **5 sit at exactly D = 0.19**. Under the exact test the count would be 2. So the gate conclusion is conservative: it would pass more easily under the exact test.
* The README says the KS routine "was checked on synthetic data before the freeze". There is no artifact for that check, so it is unauditable. My independent figures are above.

**Binomial computations.**

* Binomial(144, 0.05) 99th percentile = 14: CDF(13) = 0.9865, CDF(14) = 0.9941. The gate allowance of 14 is correct, and 7 passes.
* P(Bin(90, 0.10) >= 11) = 0.28749, matching the README's 0.29.
* With the exact discrete null rate of 22/201 = 0.1095 (200 draws), expected extremes are 9.85, not 9, and the tail is 0.397. This leaves the verdict unchanged.
* Direction split 2 low / 9 high: sign test p = 0.065.
* Power of the frozen rule: it flags only X >= 17 of 90 (18.9%). Power is 19% at a true extreme rate of 0.15 and 65% at 0.20.

**Overlap with the first run.**

* By (p, a, b): **0** of the 54 picked curves coincide.
* By (p, order): 4 of 54 coincide, all class B (L = 10: (601, 577) and (577, 601); L = 12: (2917, 2971); L = 14: (12211, 12101)). Same field and same order means isogenous, but not the same curve.
* 8 of 54 share a prime with the first run.
* The 90 extra curves share no (p, a, b) or (p, order) with the first run, but 4 share a prime.
* So the README's "only 4 of 54 coincide" is true at the (p, order) level and is in fact 0 at the curve level. Say which.

**Unreported feature (not in the README).** The 27 paired ordinary curves of the *same rerun* are not calibrated.

| set | n | mean u | z vs U(0,1) | detail |
|:--|--:|--:|--:|:--|
| rerun, paired ordinary (D) | 27 | **0.276** | **-4.0** | 17/27 below 0.25 (6.8 expected, P = 3e-5); KS vs uniform p = 1.4e-4 |
| rerun, D paired with A | 9 | 0.120 | -3.95 | |
| rerun, D paired with C | 9 | 0.277 | -2.3 | equal to class C itself (0.276) |
| rerun, 90 extra ordinary (E) | 90 | 0.526 | +0.87 | KS vs uniform p = 0.25 |
| first run, paired ordinary (D) | 27 | 0.413 | -1.6 | D paired with A: 0.292 (z = -2.2) |

* In the rerun D is skewed to n > p+1 (19/27); E is not (41/90).
* Among D, u is low mainly for n > p+1 (mean 0.208 vs 0.440). Among E it is not (0.504 vs 0.546).
* The selection of D differs from E: D shares primes with the weak classes. I did not find the cause.
* This does not change any frozen cell verdict. Each cell compares a class to the null band and only requires the paired ordinary curves not to be all extreme.
* It does contradict a clean "calibrated" reading.

**Corrections required for item 3.**

1. The sentence "the first run's apparent overdispersion ... came from its coarse 40-draw percentiles and chance" is not supported.
   * Coarse percentiles raise the expected rate to 14.6% (3.95 of 27), and 10/27 is still P = 0.0035.
   * The two runs disagree: 10/27 vs 11/90 gives Fisher p = 0.008.
   * Pooled, 21/117 are extreme against 13.8 expected (z = 2.07).
   * Supported wording: "not reproduced out of sample (11/90, frozen rule CALIBRATED, which flags only >= 17/90); the first-run excess is unexplained."
2. "The I1 null ... is calibrated for small-x log sets at n <= 2^14" holds for the 90 E curves only.
   * State that the 27 paired ordinary curves of the same rerun sit low (mean u 0.28), and give the numbers above.
3. "The first run's 'j = 0 extreme low at two sizes' did not replicate" is true for the cell rule. The direction partly replicates: class C mean u = 0.276 (z = -2.3). The paired ordinary curves are equally low, so the shift is not class-specific.
4. "against 9 expected": the exact expectation is 9.85. Cosmetic.
5. The 6.0% false-rejection figure: see the KS section above. The exact value is 5.4%.

## Item 4: README claims and lead rows

Branch-only lead changes are exactly two files, in commit `c104ec603`: `LEAD-EXO-dl-character-sum-pseudorandom.yaml` and `LEAD-EXO-weak-class-instrument-calibration.yaml`.

* `git diff origin/main -- knowledge/leads` also shows 6 other files "deleted". These are main-side additions from after this branch's base (the branch is behind `origin/main`). They are not branch changes, but the branch needs a merge or rebase before a PR.
* The artifact gate `tools/artifacts/artifacts.py check origin/main HEAD` reports "no data files committed". `rows.jsonl.xz` is 13,996 B and `rows-r3.jsonl.xz` is 54,880 B, both under 64 KiB.
* Earlier commits hold `.jsonl` snapshots above 64 KiB (73,790 B, 165,296 B, 165,420 B). The gate is a tree diff, so this does not trip it.

**H-PSEUDO row.**

* Numbers confirmed: 1.040 [0.999, 1.092]; 0.993 [0.972, 1.017]; 0.974–1.012 on the R_mean curves; "0.97–1.04" as a range of point estimates.
* Required corrections:
  1. The obstruction statement still opens with "against a matched random null ... R flat at 1.28–1.34". It then says the null was mismatched. Change the opening to "asymmetric random null (not negation-matched)".
  2. "no constant offset" and "behaves as a random negation-closed set": see item 1 correction 3. Give the interval and scope the claim to the B = 512 maximum character-sum statistic of the small-x set.
  3. `best_measured` gives a range of point estimates with no interval.
  4. README "disposition ... if anything, strengthened": nothing in the evidence strengthens exhaustion. The re-read removes an anomalous excess. Say "unchanged".

**Weak-class row.**

* Confirmed: I2 and I3 BLIND, I1 BLIND on the rerun, controls valid, the number of cells (9).
* Required corrections:
  1. "all three numeric instruments are BLIND ... at p <= 2^14". The QTT instrument was run at p ≈ 2^10 only. The row states that parenthetically; make it prominent, and note I3's rank-ceiling saturation (8/18 degenerate nulls).
  2. "The I1 null ... is calibrated on 90 fresh ordinary curves": restrict to E and report the D anomaly.
  3. The proposed scope note "blind to Smart- and MOV-weak classes" should carry the actual coverage: 3 curves per class per size, p <= 2^14, cell rule needs all 3 curves beyond 5–95%. "No detection at these sizes" is what the evidence shows; "blind" is a label of the frozen rule.

## What I could not verify

* The `dmesg` OOM report and the owner's approval of the no-S3-checkpoint deviation.
* The pre-freeze synthetic KS check (no artifact).
* The I3 (QTT) statistic values: only the stored u and the positive-control rows were analysed.
* I did not recompute the 36 completion rows other than one (instance 50, draw 3). The other 35 are at N ≈ 33.6M and are covered by the identical `job()` code path and seeds.
