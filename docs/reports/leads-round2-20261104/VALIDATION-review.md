# Round-2 validation report (Validator)

Branch `ideas/leads-round2-20261104` of isogeny-labs/crypto-autoresearcher.
Validated commit: `be9a66b016a00c5249cc79231202c4cd577a4e1a` (== `origin/ideas/leads-round2-20261104`). Working tree clean (`git status --short` empty) before and after my work; I edited nothing in the repo (one `__pycache__` that my import created under `experiments/EXP-ECDLP-1ed445/` was git-ignored and removed; all later reruns used `PYTHONDONTWRITEBYTECODE=1` and a scratch cwd).
Environment of my recomputation: Python 3.13.18, numpy 2.5.3, no scipy. Scratch code and outputs are in `/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/{checks,anom,lowdeg,rerun}/`.
Note on scope: the "AGENTS.md sections" named in the dispatch (boundary/table/ratio, ecbench, m=83/ECC2K-130 rules) belong to the cryptanalysis repo and do not exist in this repo's AGENTS.md. I applied this repo's "Experiment protocol, export and review", "Artifact policy", "Data files live in the artifact store" and "Observe first" rules. None of the three items makes a discrete-log-solve, relation or closure claim, so the certificate rule is not triggered; the rank values (exact linear algebra) were nonetheless re-verified with independent code.

## Dispositions

| item | disposition | one line |
|:--|:--|:--|
| 1. anomalous-qtt | **validated** (verdict NULL confirmed) | all hashes bind; verdict, p, controls, pick and 4 replayed rows reproduce; two wording fixes |
| 2. lowdeg-rank | **validated** (verdict HOLDS confirmed) | fractions, controls and 5 independent rank cells reproduce; check-export passes; one explanatory claim is wrong (ap arm), export raw file is not in the artifact set |
| 3. checks D1-D3 | **reproduce byte-identically**; D1 inference **confirmed with caveats** | D2 and D3 summaries need precision fixes |
| 4. lead rows | **mostly supported; 3 overreaches** | H1 "false there", D2 "cause", and the "not curve structure" phrasing |

## Item 1: `docs/reports/anomalous-qtt-20261104/` -- CONFIRMED

Bindings
- `python3 tools/experiment_protocol.py validate protocol.json`: OK, 0 findings. `hash` reproduces `freeze.protocol_sha256` = `82703e7f...3ec84`.
- sha256 of `anomalous_qtt.py` (bffc9295...), `qtt_core.py` (3b467fe6...), `analyze_anomalous.py` (b17ce43b...) equal the protocol's pins. `qtt_core.py` is byte-identical (`cmp`) to `holant-step-b-qtt-20261104/qtt_rank.py`.
- `xz -dc rows.jsonl.xz` sha256 = `9846fd6a...` = `data.sha256`; `xz -dc export.json.xz` sha256 = `542024e4...` = `data.sha256`.
- Commit order: scripts+draft protocol `ef35b300` (03:18:16), frozen protocol `2289d192` (03:18:17), data+verdict `4c4ec8ec` (03:20:55). The only semantic difference between draft and frozen protocol.json is the `freeze` block (checked field by field). No script changed after the freeze. (Minor: `freeze.commit` names the draft commit `ef35b300`, not `2289d192` where the frozen file lives.)

Recomputation from raw rows (own code `checks/val_anom.py`, not the producer's)
- 12,827 rows = 127 curves x 101 (X, LOG, 99 N); 63 anomalous, 63 ordinary, 1 motivating; each curve has draws 0..98 exactly once; `r_max` and `log2_params` agree with the stored rank vectors on every row.
- Mid-rank percentile u_X, stratified (within-prime) permutation, one-sided, statistic = mean u(ord) - mean u(anom):
  - mean u_X anomalous 0.5343, ordinary 0.4826, statistic -0.05171: identical to `verdict.json`.
  - p_perm: mine 0.8376 +/- 0.0012 (seed 777, B=100,000) and 0.8362 +/- 0.0006 (seed 424242, B=400,000); committed 0.8311 (B=9,999, SE 0.0037). Difference 1.4-1.7 sigma, within Monte Carlo error. Normal approximation from the exact permutation variance: p = 0.837 (z = -0.98).
  - r_max: mine 0.6186/0.6174, committed 0.6196. Controls: mean u_LOG 0.000/0.000, pooled A/A 0.5058 (r_max 0.4990): valid.
  - Running the committed `analyze_anomalous.py` on the decompressed rows reproduces `verdict.json` exactly (JSON-identical).
- Extra: both ECDFs are consistent with uniform (KS D 0.113 and 0.109, approx p 0.37 and 0.42). The one-sided 95% upper bound on the hypothesised shift (ordinary - anomalous) is about +0.035 in percentile units, so the NULL is informative (shifts above ~0.04 are excluded), though not an exclusion of anything smaller.

Pick and exclusion (own code `checks/val_anom_pick.py`)
- Enumerated all (a,b) isomorphism classes at the 20 primes 37..127 by brute-force point counting, replicated the preregistered `default_rng(sha256(protocol_sha|pick|p))` selection: it reproduces the stored test set at all 20 primes (63 + 63). Pool sizes (anomalous, ordinary-prime classes) per prime are in the script output; anomalous pools are <= 6, so the cap of 4 truncates the pool at 6 of 20 primes (pool > 4) and the other 14 primes contribute their whole pool.
- Motivating curve (61,21,57): #E = 61, class representative (6,14), the class has 30 (a,b) members. None of the 8 p=61 test curves is in it, (61,21,57) is not in the test set, and all 126 test curves lie in distinct classes. The 4 anomalous classes at p=61 other than the motivating one are all in the test (pool 4, cap 4), as designed.
- Independent #E for every test curve equals the stored `n`; anomalous have #E = p; ordinary #E prime and != p.

Spot replay by recomputation (own curve code, own S_3 matrix, own **exact** rank over GF(2^61-1), not SVD with a tolerance) -- all four rank vectors equal the stored ones, `r_max` and `log2_params` agree:
1. (109,4,24) arm X (anomalous, p=109, the u=0.030 curve): r_max 91, log2_params 47.929859.
2. (97,5,40) arm N draw 57 (ordinary, the u=0.000 curve), permutation from `default_rng(sha256(PSHA|anull|97|5|40|57)[:8])`: r_max 72, 45.264663.
3. (61,21,57) arm LOG (motivating): r_max 25, 24.457637.
4. (127,3,52) arm LOG (anomalous, p=127): r_max 33, 34.416596.

Findings / required corrections (none changes the verdict)
- README "values that low occur in both families at about the rate chance predicts" (motivating u = 0.025): at u <= 0.0253 there are 4 ordinary curves and **0** anomalous (the lowest anomalous is 0.030, curve (109,4,24)); 4/126 against 3.2 expected is the correct pooled statement. Reword.
- Disclosed and confirmed: `check-export` on the anomalous export FAILS with 12,962 findings (null draws not encoded as replicates, seed formula mismatch, motivating arm outside the arm list). Counts match (12,827 runs).
- The export's declared raw file `anom_compact.jsonl` (sha 66ef75f5..., 2,580,413 B) is not in the committed artifact set (see item 2 for the same pattern); `export.source.commit/dirty` and host fields are null, and python/numpy versions (protocol `measurement.record`) are not recorded anywhere. My replays agree under numpy 2.5.3, so the practical risk is low, but the binding is incomplete.

## Item 2: `docs/reports/lowdeg-rank-20261104/` -- CONFIRMED (HOLDS), one wrong explanation

Bindings
- `validate protocol.json`: OK, 0 findings; `hash` = `bbcdab31...6737756` = `freeze.protocol_sha256`. `lowdeg_rank.py` (1b7a30b7...), `modrank.py` (f1e0ed19...), `analyze_lowdeg.py` (e8f5a75b...) equal the protocol pins.
- rows.jsonl.xz -> sha `4e912361...` and export.json.xz -> `36b7695c...`, both equal `data.sha256`. `verdict.json` sha equals the export's recorded `8560cc7b...`.
- Order: draft `3edaed22` (03:26:59), freeze `c1bfc741` (03:27:00), in-progress rows snapshots `9a23c9f2` (287 rows) and `23fb1d75` (318 rows); both snapshots are byte-prefixes of the final 444-row file, so no already-seen row was altered. (287 rows by 03:28:18 is plausible only because instances 0-22 are the small L=8/9 ones.)
- `check-export --protocol protocol.json <export.json>` on the uncompressed export: **OK, 0 findings** (as the README says). All 444 export runs agree with rows (run_id, seed, replicate, counted `deficit` = expected_generic - rank).

Recomputed verdict (own code `checks/val_lowdeg_analysis.py`)
- Decisive cells (rand, monomials/candidates >= 1.5): 12, 12, 12, 3 at L = 8, 9, 10, 11 (total 39; ratio range 1.70-2.22). Full-rank fraction = 1.00 at every size (39/39), matching `verdict.json`. HOLDS rule (>= 0.9 at every size) met.
- Controls: null 111/111 full; shift 111/111 within 3Dt+1 (max rank/bound = 0.995, so the bound is tight; no shift cell is full); no structural inconsistencies in any of 444 rows (monomials = C(2t+D,D), candidates re-derived per arm, `full` flag, primality of p and n, p = largest prime < 2^L, rand multipliers in [2,n-2]).
- Post-data table reproduces: rand deficit mean 68.4 (max 288) at L=10 in the 0.75-1.5 band; ap full in 36/39.

Independent rank re-verification (own code `checks/val_lowdeg_rank.py`: own curve arithmetic, own scalar-multiple table, multipliers regenerated from the checker's `derive_seed`, own monomial construction, and a different algorithm, Gauss-Jordan row insertion into a reduced basis over F_p). All stored ranks match:

| cell | p, D, t | candidates / monomials (ratio) | my rank | stored | note |
|:--|:--|:--|--:|--:|:--|
| 26-rand-0 | 1021, 2, 32 | 1048 / 2145 (2.05) | 1048 | 1048 | decisive, full |
| 29-rand-1 | 1021, 3, 11 | 1048 / 2300 (2.19) | 1048 | 1048 | decisive, full |
| 36-rand-0 | 2039, 3, 13 | 2010 / 3654 (1.82) | 2010 | 2010 | decisive, full |
| 27-shift-1 | 1021, 3, 6 | 1042 / 455 | 54 | 54 | <= 3Dt+1 = 55 |
| 31-rand-0 | 1021, 2, 22 | 1038 / 1035 (1.00) | 941 | 941 | deficit cell |
| 5-rand-0, 5-shift-1, 7-rand-0 | 251 | -- | match | match | warm-up cells |

In every case the regenerated multipliers equal the stored ones, and the regenerated candidate counts equal the stored ones.

Findings / required corrections
1. **Wrong explanation for the ap arm (README "Small multipliers" bullet, `report.typ` line 49).** It says "With b_i <= 3t, sum b_i^2 is already about 9t^3, far above N, so the pulled-back degree is not limiting; large multipliers are not required". The data say otherwise: all three non-full ap cells (11-ap-0, 23-ap-0, 36-ap-0; deficits 3, 11, 109) are replicate 0, multipliers b_i = 1..t, D = 3, where sum b_i^2 = 91, 204, 819, i.e. 0.34-0.41 N (sum b^2 is about t^3/3 for rep 0, not 9t^3). Every other ap cell (rep 1 and 2, and all D=2 cells) is full with sum b^2 / N from 2.1 to 200. The honest statement is "ap is full in 36/39; the 3 failures are exactly the small-multiplier cases (sum b^2 < N/2, D=3); 4 of 7 such D=3 rep-0 cells are still full".
2. **Declared raw file missing.** The export declares `files[0] = ld_rows.jsonl`, sha `e2af7271...`, 191,416 B. This file is not in the repo and is not `rows.jsonl` (155,621 B, sha `4e912361...`). With the export placed beside `verdict.json` and `analyze_lowdeg.py` (both verify), `check-export --verify-files` fails ("file missing: ld_rows.jsonl"; if rows.jsonl is copied under that name: "file changed since export"). Content equivalence is verified (444/444 runs), but the artifact hash cannot be reproduced from the committed set. Fix: push the derived file through the artifact store and add it to `data.sha256`, or record the conversion command.
3. Reproducibility record: export `source.commit`, `dirty`, `host.*`, producer model and session are null; python/numpy versions are not recorded although the protocol's `measurement.record` lists them.
4. The 23 of 39 decisive rand cells that contain a two-term multiplier relation (including exact repeats b_i = b_j, which `rng.integers(2, n-1, t)` allows) are all full rank. This supports "relations do not affect the decisive band". It is a useful number to add.

## Item 3: `docs/reports/leads-round2-20261104/checks/`

Reruns (scratch cwd, `PYTHONDONTWRITEBYTECODE=1`, scripts unmodified): `d1.json`, `d2.json`, `d3.json` are **JSON-identical** to the committed files (d1 18.7 s, d2 4.5 s, d3 25 s).

**D1 critical assessment** (own checks `val_d1_closure.py`, `val_d1_matched.py`, plus an analytic extreme-value calculation)
- Factor base is negation-closed with signed logs: **yes**. `build_dl_table` iterates Q <- Q + G for N steps and keys by (x,y), so P and -P both appear with logs i and N-i. `build_factor_base` sorts by (x,y) and takes the first B; with B = 512 even and N odd (no 2-torsion), every x has exactly two points, so F is 256 complete +-pairs. Verified on the actual recorded rung-20 curves 0 and 1 (p = 671681): |F| = 512, 512 distinct logs, closed under l -> N-l, no self-negating log, 256/256 x-values with two y's, and the recomputed C_EC (4.30703, 4.371099) equals the recorded values to 6 digits.
- Null asymmetric: **yes**. `generate_null_subset` draws a uniform B-subset of Z_N by SHA-256 rejection; the fraction of elements whose negative is also in the set is 0.0000 and 0.0078 on two draws (chance level). So S_k is complex for the null (|S|^2/B ~ Exp(1), C_null = sqrt(ln M + gamma), recorded to 0.05%) and real for F (S_k/sqrt(B) ~ N(0,1)), which gives R -> sqrt 2 slowly. The mechanism is correct.
- "Against a symmetric null the recorded 2^20 value becomes R ~ 1.02": **numerically confirmed, but not as derived.**
  - The number 1.02 is in no committed artifact. `d1.json` holds only the sym/null ratios. It equals recorded R_mean 1.334 (raw-result.json, rung bits=20) divided by D1's 1.306.
  - Parameter mismatch: the recorded "2^20" rung has p = 671681 (2^19.4), N_representative = 223667 (2^17.8), per-curve N from 134,219 to 672,629, B = 512, C_EC_mean = 4.6616 (first 8 curves), C_null_mean = 3.4949. D1's 1.306 comes from N = 1,048,573 and B = 1022 (the 1.29 point from N = 131,071, B = 362).
  - At the recorded parameters: analytic E[C_sym] = 4.557 gives implied R = **1.023**; Monte Carlo (B = 512, N = 223,667, 100 draws, seed 20261104) E[C_sym] = 4.507 +/- 0.023 gives **1.034**; using each curve's own N: **1.006** (analytic) / **1.011** (MC). The 8-curve sampling SE is 0.02-0.026. So R ~ 1.02 +/- 0.03: the stated value stands, with an uncertainty the README omits.
  - Across all four rungs (analytic, N_rep): implied R vs a symmetric null = 1.023, 0.970, 0.956, 1.012 for bits 20, 22, 24, 26 (per-curve N: 1.006, 0.982, 0.974, 0.999; SE 0.015-0.026). All within about 2 SE of 1. This is stronger than the single-rung statement and should be quoted.
- Conclusion "the measured excess is a null mismatch, not curve structure": supported **to within about +/-0.03-0.05** (no curve-specific excess is detected; a few-percent excess cannot be excluded). It does not by itself change EV-ECDLP-f83a17's alpha_resid conclusion (a near-constant factor of 1.29-1.33 across N does not alter the growth exponent).

**D2** (p = 211, 227; D = 3, 4; t = 3): fresh triples exact 44/50 and 44/50 (p = 211), 45/50 and 45/50 (p = 227): 88-90% as stated; 0 deficient triples without a relation of size <= 2; both original p = 211 triples carry a relation (b2 = -2 b3, b2 = 2 b3). **But the summary is imprecise.** The relation is necessary, not sufficient: of 21 relation-bearing fresh triples (p = 211 and 227 together), the 10 whose shortest relation involves three multipliers (nnz = 3) all have deficit 0, while every two-term relation (11 triples) gives a deficit (b_i = +-2 b_j: 4 at D=3 and 27 at D=4; b_i = +-b_j: 48 and 129). The correct mechanism statement is "a two-term relation c_i b_i + c_j b_j = 0, |c| <= 2". Also, D2 only tested t = 3 at p = 211 and 227.

**D3**: L = 8, 9, 10 numbers reproduce (log-AP r_max(M_LOG) 12, 18, 16; small-x 55, 71, 120; random-log 47-57, 73-78, 109-120). **Model fidelity checked independently** (`val_d3_model.py`): for the same three curves, the E-block of the real LOG-labelled transfer matrix (built from S_3 on the curve) equals the matrix built from the factor base's log set alone, entry for entry (0 differing entries at all three sizes). That supports "M is Toeplitz-plus-Hankel in the log set of FB". Corrections: the README range "55-120 for small-x and random-log factor bases" should read **47-120**; D3 models the E-block only (m = (n-1)/2), not the twist block of the padded 2^L matrix used in step (b), so "rank comes from the log set, not the group law" is established for the E-block; one curve per size; both missed predictions are correctly disclosed.

## Item 4: lead rows (`git diff origin/main -- knowledge/leads`, 7 files)

Supported as stated
- holant row: "63 anomalous vs 63 ordinary over 37..127, stratified permutation p = 0.83" (confirmed, 0.836 +/- 0.001); the D3 sentence on AP log sets (12-18) is accurate for the E-block; "A Coordinator could file ... closed_dominated" is a proposal, not a status change.
- ICE and invertible-hint rows: A1/A2 notes match `amendments-literature.md` (which itself separates full-text-verified Golovnev et al. from abstract-only Lange-Winterhof); I did not re-fetch the literature (network blocked for those hosts). Theorem 1 as quoted (S = O~(N^(2-d)), T = O~(N^(3d)), S^3 T = O~(N^6)) does refute S = N^(2-e), T = N^(1-e) for e < 1/4.
- character-sum row: the offset-explained-by-symmetry claim, "R = 1.29 / 1.31" (d1.json: 1.293 / 1.306), and the `revisit_when` ("inflates R by about 1.3") are supported.
- new rows `quadratic-phase-small-x-leakage` (`best_measured: null`; "factor base is negation-closed, so g is even" is verified by D1) and `weak-class-instrument-calibration` (`best_measured` = the anomalous NULL, correct) make no unsupported measurement claims; the exploitation path is labelled a numbered heuristic.

Required corrections
1. **low-degree row, "so the interpolation attack's condition holds at toy size and H1 as stated is false there."** The experiment establishes the rank premise at toy size only. H1 is an asymptotic query bound, T = Omega(min(sqrt N, sqrt p / D)), and at p <= 2039 it is vacuous (T^2/N >= 1 for any T >= sqrt N). The attack's own cost at the tested points (t = 11-32 multipliers, each [b_i]Q costing about 1.5 log2 N group operations, plus log2 N tests) is about 180-490 group operations against sqrt N = 32-45 and sqrt p / D = 11-16, so no toy-size violation of H1's query bound is exhibited. By my rough accounting (t ~ (2 D! N)^(1/D)/2) the attack drops below sqrt N / D only for D >= 3 and N of order 2^28 (D=5) to 2^48 (D=3), and never for D = 2 (t ~ sqrt N). Reword to: "the rank premise of the desk refutation of H1 holds at toy size (exact, 39/39); the refutation itself is asymptotic and rests on the rank condition persisting at t ~ N^(1/D) for D >= 3, which was not tested."
2. **low-degree row, `discriminates`: "Short multiplier relations (sum c_i b_i = 0 mod N, |c| <= 2) cause the rank deficits seen below ratio 1.5 (D2)."** D2 does not support "cause" for these cells. D2 covers t = 3 only, 3-term relations give no deficit, and applied to the real rand rows (`checks/val_pair_relations.py`): in the 0.75-1.5 band 15 of 21 deficient cells have a two-term relation with |c| <= 2 and 6 do not (2 of 17 relation-bearing cells are not deficient); below 0.75, 10 of 14 deficient cells have one and 4 do not. Say "two-term relations account for most (about 70%) of the observed deficits; the rest are unexplained", and drop "cause". The README's hedged wording ("confounds") is closer to the evidence than the row.
3. **character-sum row: "the recorded 2^20 value becomes R ~ 1.02, so the measured excess is a null mismatch, not curve structure."** Add the source and precision: rung bits=20 means p = 671681, N_rep = 223667, B = 512; implied R vs a negation-closed null is 1.01-1.03 (SE about 0.02-0.03), and 0.96-1.02 across all four rungs; replace "not curve structure" with "no curve-specific excess is detected within about +/-0.04". Also commit the arithmetic (it is not in `d1.json`).
4. low-degree README and `report.typ`: fix the ap-arm explanation (item 2, finding 1). leads README D2 row: "Every deficient triple has a relation" is true, but add that only two-term relations produce deficits. leads README D3 row: 47-120, E-block only. anomalous README: the "both families" sentence (item 1).
5. Minor: the weak-class row's first sentence ("never been shown a curve whose discrete logarithm is known to be easy") is contradicted two sentences later by the measured QTT x anomalous cell; qualify as "no instrument except the QTT rank has been shown one".

## Summary of numbers the report should carry
- anomalous: p_perm 0.836 +/- 0.001 (committed 0.831), NULL, controls valid, replay 4/4.
- lowdeg: 39/39 full, fractions 1.00 at L = 8, 9, 10, 11, independent ranks 5/5 (+3 small), check-export 0 findings (without `--verify-files`).
- D1: recorded R at the 2^20 rung 1.334; symmetric-null-implied R 1.02 +/- 0.03; across rungs 0.96-1.02.
