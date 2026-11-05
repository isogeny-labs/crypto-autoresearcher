# Validation report: HOLANT-STEPB-QTT-20261104 (holant step b', QTT rank of the transfer matrix)

Validator: independent session (Sonnet 5.5). Date: 2026-11-04.

## Disposition: `validated` (primary verdict NULL, controls valid), with one required documentation correction (F1) and several non-blocking findings

Validated from: repo `/home/user/crypto-autoresearcher`, branch `ideas/holant-step-b-qtt-20261104`, **commit `ed7b80994dd96b6aa0ec4bdd27b504dd853125f8`**, `git status --porcelain` empty at the end of the work.

Binding note. I started at `c2ce575b` with a dirty tree: the results (`rows.jsonl.gz`, verdicts, `data.sha256`, `export.json.gz`, figures) were untracked and a stale 1255-row `rows.jsonl` was still the tracked file. The producer committed the set as `ed7b8099` (02:20:09) while I was working. I took a sha256 snapshot of all 17 files in the study directory before I used any of them (`/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/work/hashes_start.txt`). Every file's blob at `ed7b8099` equals its start snapshot, and the end snapshot (`hashes_end.txt`) equals the start. So everything below was computed on exactly the committed bytes, and nothing moved.

Environment of my recomputation: Python 3.13.18, numpy 2.5.3, 4-core container, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1` for replays, all scripts run with `python3 -I`, outputs only in the scratchpad. I edited nothing in the repo.

## Item 1: hashes and protocol re-validation: CONFIRMED

| check | expected | observed | result |
|---|---|---|---|
| `qtt_rank.py` sha256 vs `arms[*].instrument.flags.script_sha256` | `3b467fe6cab15a8432f430c42bf6d271afd0f8d01ee34116d06e898fa2b765d7` | identical, in worktree, at HEAD, at `4970366b` and at `100dd358` | pass |
| `analyze.py` sha256 vs `analysis_plan.script.sha256` | `1930766809509912d2983e5bc255251e4f14c889b99831e37a3addf9a608d0a3` | identical in all four places | pass |
| uncompressed `rows.jsonl.gz` vs `data.sha256` | `c15ee3e4709746d46fd5fa823956d330c5f0de94790287baa61f7b43028f5bdb` | identical, 1530 lines | pass |
| uncompressed `export.json.gz` vs `data.sha256` | `2ee1df1ba643e76357b4e3f035441fd71439b14474a288c41a1e00389bd121ce` | identical | pass |
| `tools/experiment_protocol.py validate protocol.json` | 0 findings | `OK ... (0 finding(s))`, exit 0 | pass |
| `tools/experiment_protocol.py hash protocol.json` vs `freeze.protocol_sha256` | `bdba447e899094f553eb43b857230191e0b5f8d494988d9cf9c4d6b577b34cd3` | identical | pass |

Freeze ordering: scripts landed in `4970366b` (01:57:18), frozen `protocol.json` in `100dd358` (01:57:18, a metadata-only change from the draft: `freeze` block only, verified by semantic diff), first data snapshot `16b1acdb` (01:59:02). Script hashes are the same before and after the data. `filed_before_affected_data: true` is consistent with history. Minor: `freeze.commit` is `4970366b`, whose `protocol.json` is still the draft (`status: draft`, `protocol_sha256: null`). The frozen file first exists at `100dd358`. Not a blocker.

Bit-level reproduction of the whole run (extra): I reran the unmodified `qtt_rank.py --protocol-sha bdba447e... --out <scratchpad>/replay_full.jsonl` (about 19 min on 1 core). The 1530-row output is **byte-identical** to the committed rows (sha256 `c15ee3e4...`). This also shows the seeds are fully determined by the protocol hash.

## Item 2: decision rule recomputed from raw rows: CONFIRMED (NULL, controls valid, 9/9 inside null 90%)

Code: `/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/work/v2_decision.py` (own code, does not import `analyze.py`; uses `np.percentile` linear, as in the rule text).

Structure check on the rows: 15 cells (5 sizes x 3 curves), each with 1 X, 1 LOG, 1 SH and 99 N (draws 0..98, `stream == draw % 2`); every row has 2L-1 cut ranks and `r_max == max(ranks)`.

Interleaved `r_max` for the 9 curves with L >= 8 (all numbers recomputed):

| L | curve | p | #E | X | null min | q5 | median | q95 | null max | LOG | A/A median diff | pooled IQR |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 8 | 0 | 251 | 263 | 256 | 252 | 254.0 | 256 | 256 | 256 | 49 | 0 | 1 |
| 8 | 1 | 251 | 257 | 256 | 253 | 254.0 | 256 | 256 | 256 | 44 | 0 | 1 |
| 8 | 2 | 251 | 271 | 256 | 254 | 255.0 | 256 | 256 | 256 | 57 | 0 | 1 |
| 9 | 0 | 509 | 479 | 512 | 511 | 511.9 | 512 | 512 | 512 | 76 | 0 | 0 |
| 9 | 1 | 509 | 487 | 512 | 509 | 511.9 | 512 | 512 | 512 | 77 | 0 | 0 |
| 9 | 2 | 509 | 523 | 512 | 510 | 511.9 | 512 | 512 | 512 | 78 | 0 | 0 |
| 10 | 0 | 1021 | 1031 | 1024 | 1023 | 1024 | 1024 | 1024 | 1024 | 121 | 0 | 0 |
| 10 | 1 | 1021 | 1049 | 1024 | 1023 | 1024 | 1024 | 1024 | 1024 | 109 | 0 | 0 |
| 10 | 2 | 1021 | 1049 | 1024 | 1024 | 1024 | 1024 | 1024 | 1024 | 112 | 0 | 0 |

- Validity, positive control: LOG < null min on 9/9 (margins 197..914 ranks; LOG/null median 0.106..0.223). Pass.
- Validity, A/A: `|median(s0)-median(s1)| <= pooled IQR` on 9/9 (0 <= 0 on the L >= 9 curves). Pass. Note: with a saturated null (IQR 0) this check is satisfied vacuously by equality and has little power at L >= 9.
- SIGNAL: needs X < null min on all 9. X equals the null max on every curve (X = 2^L, the maximum possible rank). SIGNAL false.
- NULL: X inside [q5, q95] on **9/9** (>= 7 needed). Robust to the percentile definition (lower, higher, nearest, inverted_cdf, midpoint all give 9/9).
- Verdict recomputed: **NULL**, same as `verdict.json`. All 210 numeric fields of `verdict.json` `per_curve` match my values. Re-running the frozen `analyze.py` on the unpacked rows into the scratchpad gives `verdict.json` and `verdict_blocked.json` byte-identical to the committed ones.
- Reading of the result: X sits at the maximum possible rank 2^L (in fact at the maximum possible rank at every cut: interleaved profile `[2,4,...,2^L,...,4,2]`) on all 9 curves, so the NULL is not a borderline call.

Supporting data (informational, not decision inputs): sizes L = 6, 7 give X inside the null 90% on 4 of 6 curves for interleaved `r_max` (outside the rule by design). Of the two outside, L = 6 curve 0 is low (X = 48 < q5 = 49, one-sided p = 0.05; see F7) and L = 6 curve 2 is high (X = 64 > q95 = 63.1, p = 1.0). The README mentions only the first. Also verified: on all 9 curves with L >= 8, X's interleaved rank list equals the maximum possible `min(2^c, 2^(2L-c))` at every cut.

## Item 3: spot replay: CONFIRMED (exact match, stored rank lists identical)

Seed chosen and stated: `random.Random(20261104)`; pick A = random N row at L = 10, pick B = random LOG row, pick C = random from the rest. Picks: **(L=10, curve 1, N, draw 8)**, **(L=7, curve 2, LOG)**, **(L=8, curve 1, N, draw 43)**. I added three more: (L=10, curve 1, LOG), (L=10, curve 2, X), (L=9, curve 0, X).

Method: **my own reimplementation; I did not call `qtt_rank.py` functions** (the only use of the producer's script was the separate full byte-for-byte rerun above). Code: `.../scratchpad/work/v3_replay.py`, log `.../scratchpad/work/spot_replay.log`. Independent pieces:
- curve search from the protocol-hash stream (re-derives (a, b, #E) and asserts equality with the row), point enumeration, group law, discrete logs;
- M from my own Semaev S_3 transcription **and** from the group law alone (M[x(Q), x(P+-Q)] for x in FB); the two matrices are asserted equal;
- LOG labelling cross-checked against a pure mod-n construction of the Toeplitz-plus-Hankel pattern (no group law, no S_3);
- null permutation from `default_rng(sha256(protocol_sha|null|L|curve|draw)[:8])`, applied by gather instead of scatter;
- unfolding by explicit digit/bit index arithmetic on the nonzero entries (not reshape/transpose);
- rank by SVD with the protocol tolerance, **and** exact rank over GF(2^31-1) and GF(2147483629) (both prime).

Result: 6/6 rows match, both orders, full 2L-1 rank lists identical to the stored lists, and the exact modular ranks equal the numeric ranks at every cut (so the 1e-12 tolerance rule does not misclassify any cut on these rows). Examples: N L=10 c1 d8 interleaved `[2,4,8,16,32,64,128,256,512,1024,512,...,2]` (r_max 1024), blocked r_max 524; LOG L=7 c2 interleaved `[1,1,2,4,8,15,26,31,27,15,8,4,2]` (31), blocked 53; LOG L=10 c1 interleaved r_max 109; X L=10 c2 1024. The full-run byte-identical rerun covers the other 1524 rows.

Certificate discipline: this run makes no discrete-log solve or relation claim, so no solver certificate is required. The nearest thing is the S_3-versus-group-law identity and the LOG labelling, both verified independently above on every replayed curve.

## Item 4: "blocked r_max is uninformative": CONFIRMED (with a precision)

From the rows (`.../scratchpad/work/v4_blocked.py`):
- On all 15 curves, blocked `r_max` is **identical across X, LOG and all 99 N draws** (null min = null max = X = LOG). It equals **(#E - 1)/2** on every curve (30, 33, 33, 56, 69, 53, 131, 128, 135, 239, 243, 261, 515, 524, 524) and the middle-cut value `ranks[L-1]` equals `r_max` in every one of the 1515 X/LOG/N rows. SH (a permutation matrix) gives p at the middle cut, so the blocked order cannot see even the shift.
- Argument. Every labelling used (X, LOG, N) is a simultaneous row/column permutation of the same M: M' = P M P^T, followed by zero-padding. In blocked order (y bits, then z bits) the cut c = L separates all y digits from all z digits, so its unfolding is exactly the padded 2^L x 2^L matrix, and its rank is rank(M') = rank(M), invariant under P. I also checked that the support of M lies inside Ex x Ex (Ex = the (n-1)/2 x-coordinates of E(F_p)) with 0 entries outside on 5 curves, and rank(M) = |Ex| = (n-1)/2, i.e. M has full rank on its support, so the invariant is just the number of x-coordinates on the curve.
- Precision. "The max is attained at the middle cut" is a theorem only when rank(M) >= 2^(L-1) (then every cut c != L is capped by 2^(L-1) <= rank(M)). That holds for all three curves at L = 10 and at L = 8, for L = 9 curve 2 (261), L = 7 curve 1 (69) and L = 6 curves 1, 2 (33). For the other curves (L = 6 curve 0: 30 < 32; L = 7 curves 0, 2: 56, 53 < 64; L = 9 curves 0, 1: 239, 243 < 256) a neighbouring cut could in principle exceed the middle one under some relabelling. It never does in the 1515 rows. So the invariance of blocked `r_max` is verified for these data, and the argument is complete for all six curves at L = 8 and L = 10, and empirical for L = 9 curves 0 and 1. This does not change the conclusion that the blocked metric cannot discriminate labellings. The full blocked profiles do differ across labellings (80 to 101 distinct profiles per 101 rows), so a different blocked statistic would not be degenerate, but none was preregistered.
- `verdict_blocked.json` = INVALID_CONTROLS is therefore the correct output of the frozen rule (LOG = null min, not below it). It does not affect the primary verdict.

## Item 5: invariance of flattening ranks: CONFIRMED

Argument. Let T be p x p x p and A, B, C invertible p x p. The transformed tensor T'[i,j,k] = sum A[i,i'] B[j,j'] C[k,k'] T[i',j',k'] has mode-1 flattening T'_(1) = A T_(1) (B (x) C)^T. A is invertible, and B (x) C is invertible (determinant det(B)^p det(C)^p), so rank T'_(1) = rank T_(1). Modes 2 and 3 are the same after permuting roles. The CP rank is invariant too: the map A (x) B (x) C is a linear bijection that sends rank-one tensors to rank-one tensors and so does its inverse, so minimal decomposition lengths are preserved (border rank likewise). Only non-invertible maps can lower a flattening rank, and then trivially (an r x p map leaves rank <= r), which is the Legendre-projection value 2. Measures that are not GL-invariant (support/sparsity, norms, and the QTT rank, which depends on the binary-digit factorization of the index space and is invariant only under per-digit GL_2 and digit-preserving permutations) are not covered, so reformulating step (b) as a labelling-dependent QTT measure is consistent with the invariance claim.

Numerical confirmation:
- `python3 -I invariance.py` rerun gives `invariance.json` **byte-identical** (`T`, `fourier`, `mult_chars`, `random` all `[61,61,61]`; Legendre projection rank 2).
- My own exact check (`.../scratchpad/work/v5_invariance.py`): T for (p, a, b) = (61, 4, 1), 3685 nonzeros, ranks over GF(2^31-1): `[61,61,61]`; after three independent random invertible A, B, C (independent per mode, unlike `invariance.py` which uses the same matrix on each bond): `[61,61,61]` in all 3 trials; non-invertible 1 x p, 2 x p, 5 x p maps give 1, 2, 5. The identity flat_1(T x A x B x C) = A flat_1(T) (B (x) C)^T holds numerically (allclose) on a random 5 x 6 x 7 tensor.
- Remark: the flattening ranks of T are already the maximum possible p in every mode, so the original step (b) could not discriminate even before the invariance argument.

## Controls and reporting contract

- Null (N, 99 draws/curve, matched on curve/FB/spectrum/nnz/padding/rank code), positive control (LOG), detector sanity (SH, r_max 5 everywhere), A/A: all present, all run, all priced in the same unit (rank). Present and checked.
- The cheaper baseline and the external fastest implementation do not apply: no cost is claimed. The protocol lists "reading a SIGNAL as an attack-cost claim" as inadmissible, and the README states that no rho comparison is made. The AGENTS.md section "The rule: boundary, table, ratio" (one table, one unit, ratio vs matched reference, section 5a pricing band), the validation gate for leaderboard rows, and the m=83 / ECC2K-130 gate (section 8a, binary curves) are **not triggered**: prime-field toy curves with p <= 1021, a structure statistic, no leaderboard or benchmark row, no transfer claim. The README's results table is one table in one unit and gives X, null range, LOG and SH.
- Claim scope: the verdict is limited to p <= 2^10 (3 curves per size), the x-coordinate labelling and the stated FB rule. It does not extend to other labellings, other FB rules, or larger p.

## Findings (none changes the verdict)

**F1 (wrong number in README.md, report.typ and report.pdf; correction required).** The text says: "The secondary parameter count Σ log2 rank also equals its maximum L² (64, 81, 100 bits) for X **and every null draw**." Recomputed: X equals L² exactly on all 9 curves, but **118 of 891** null draws at L >= 8 are below L² (98/297 at L=8, 15/297 at L=9, 5/297 at L=10; minimum 63.977, 80.992, 99.999). The same draws have `r_max` < 2^L (the README's own table shows null min 252, 509, 1023). The sentence "X and the null both sit at the rank ceiling" is true of X and of the null median, not of every draw. Correct wording: X is at the ceiling on all 9 curves and equals the null maximum; the null median is at the ceiling; 13% of the null draws at L >= 8 fall below it. Evidence: `rows.jsonl.gz` `interleaved.log2_params`.

**F2 (positive-control interpretation, caveat).** README: "the discrete-log labelling has rank 2.6 to 9.4 times below the ceiling." Part of that is generic. In my exploratory run (`v6_explore.py`, validator's own seed 2026, one curve each at L = 8, 9, 10, not frozen data), packing the support Ex into the low indices in *random* order already gives interleaved r_max = 2^(L-1) (128, 256, 512), against LOG 49, 77, 112 on the same curves. So about a factor 2 comes from support packing and the discrete-log order adds a further 2.6x to 4.6x. The validity check (LOG < null min) passes either way, and the NULL verdict does not depend on this, but the control shows "the detector sees a labelling-induced reduction", not specifically "digit structure from discrete logs".

**F3 (post-data observation 2 overreaches).** "Even the ideal labelling has rank of order √p ... This bounds what any labelling-based route through this network can gain." Only three labellings were measured (X, N, one LOG), and no lower bound over all labellings is given, so LOG is not shown to be ideal and nothing is bounded. LOG r_max/√p is 3.2 (L=6), 2.2 to 3.2 (L=7), 2.8 to 3.6 (L=8), 3.4 (L=9), 3.4 to 3.8 (L=10), so "roughly 3.6√p" holds only at the top size. The mechanism "its QTT rank grows with |FB|" is untested in the frozen design (|FB| = ⌊√p⌋ is confounded with p). My exploratory check at L=9 curve 0 (p = 509), varying |FB| at fixed p: LOG r_max = 32, 55, 57, 76, 79, 81 for |FB| = 4, 8, 11, 22, 44, 88, i.e. it saturates near 3.5√p rather than growing with |FB|, consistent with a generic Toeplitz-plus-Hankel QTT ceiling of order √p. Also "the same scale as rho" compares a rank (a dimension) with an operation count and prices nothing; keep it labelled as an interpretation. These are labelled post-data in the README, but the "ideal"/"bounds any route" wording should be softened.

**F4 (amendment A1 is not a filed amendment).** `protocol.json` has `amendments: []` and version 1; A1 exists only as README text. `check-export` on the unpacked `export.json` gives 1547 findings: 1530 "execution cell is outside the protocol-derived seed table", 15 "arm N ... measured 99 replicates, expected 1", 1 "1530 measured rows; protocol plans 60", and 1 "analysis.script.sha256 is missing". The README attributes the findings to the `sample_size` and seed-table encodings; the last one (the export's `analysis.script` is null) is a separate omission in the export. The export's `runs[*].measurements.counted` r_max (both orders) and `log2_params` (= the interleaved value only, while the protocol defines it as interleaved plus blocked) match the rows exactly (0 mismatches over 1530 runs), so the export is accurate but not protocol-conformant.

**F5 (reproducibility record incomplete).** The export has `source.commit: null`, `source.dirty: null`, an all-null `host`, `producer.model/session: null`, and no `python_version` / `numpy_version`, although `measurement.record` and `variable_ledger.host` promise them. `run.log` holds no command line or versions. The run command exists only in the README ("Reproduce"). Mitigation: my rerun on Python 3.13.18 / numpy 2.5.3 reproduces all 1530 rows byte-for-byte, so the result does not depend on the producer's environment. The export also lists `rows_compact.jsonl` (sha256 `37d46e1c...`), which is not in the directory.

**F6 (process deviations, unverifiable claim).** README: "With the owner's approval, the pushed branch served as the resume record" in place of the S3 resume checkpoint. I have no artifact showing the approval and cannot verify it; an agent message would not count as approval. The data-store rule: `rows.jsonl` (569 KB) and `export.json` (1.6 MB) were replaced by `.gz` files under the 64 KiB threshold (31,814 and 40,969 bytes), which complies by size, but the uncompressed in-progress `rows.jsonl` snapshots (326,644 bytes at `16b1acdb`, 455,645 bytes at `c2ce575b`, both above the 64 KiB data-suffix threshold) remain in history.

**F7 (uncovered datum, exploratory only).** The only curve with X below the null 5th percentile is L = 6 curve 0, which has #E = 61 = p (an anomalous curve, trace 1). It is the only n = p curve among the 15, it lies outside the decision set, and the README describes it only by its p-value. One curve at p = 0.05 among six small curves is what chance gives, so this is not evidence of structure; it is worth knowing that the anomalous case was included, not excluded.

**F8 (non-preregistered secondary, informational).** `log2_params` is a declared secondary metric but neither verdict file analyses it. Recomputed here for information only: interleaved, X inside [q5, q95] on 9/9 curves with L >= 8; blocked, 8/9 (L = 10 curve 1: 97.988 against null range 97.917 to 98.186, below q5). One of nine outside a 90% band is within chance and agrees with the primary verdict. The figure (`qtt-rank.svg`) regenerates from `verdict.json` up to matplotlib's embedded date and random clip-path ids (cosmetic; the `Deterministic` docstring is true of the data, not of the SVG bytes).

## Requirement ledger

| requirement | status | evidence |
|---|---|---|
| frozen, committed artifact set; record commit | verified (`ed7b8099`, clean; start/end/commit hashes identical) | `git`, `hashes_start.txt`, `hashes_end.txt` |
| script and data hashes; protocol re-validates | verified | item 1 |
| decision rule recomputed independently | verified, NULL | `v2_decision.py` |
| spot replay (3 random + 3 extra) with own reimplementation, exact ranks | verified, 6/6 | `v3_replay.py`, `spot_replay.log` |
| whole-run reproduction | verified byte-identical | `replay_full.jsonl` sha256 `c15ee3e4...` |
| blocked metric uninformative | verified (data) and argued (complete for L = 10 only) | `v4_blocked.py` |
| flattening-rank invariance | verified (argument, rerun identical, own exact check) | `v5_invariance.py`, `invariance.json` |
| controls (null, positive, A/A, SH) | present and valid; positive control has the F2 caveat | item 2, F2 |
| numbers in README/PDF supported by artifacts | **one unsupported statement (F1)**; others supported | F1, F3 |
| cost/ratio/rho/m=83 reporting rules | not applicable (structure statistic, no cost claim) | protocol `inadmissible`, README |

## Scripts and logs (all in `/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/work/`)

`v2_decision.py`, `v3_replay.py`, `v4_blocked.py`, `v5_invariance.py`, `v6_explore.py` (exploratory, outside the frozen design), `spot_replay.log`, `replay_full.jsonl`, `check_export.txt`, `verdict_rerun.json`, `verdict_blocked_rerun.json`, `invariance_rerun.json`, `hashes_start.txt`, `hashes_end.txt`.
