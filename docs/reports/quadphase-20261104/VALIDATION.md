# Validation report: QUADPHASE-20261104 (lead N2, quadratic-phase leakage of the small-x factor base)

Validator: independent re-implementation, no edits to the repo.
Validated from: commit `6e367d4f9a24c47f43fe4734fba75af913b3c94b`, branch `ideas/hpseudo-symnull-20261104`, working tree clean before and after (`git status --porcelain` empty, HEAD unchanged).
Artifact set: `/home/user/crypto-autoresearcher/docs/reports/quadphase-20261104/`.
Tools: Python 3.13.18, numpy 2.5.3. My code: `/tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/mine/` (`indep.py`, `bulk.py`, `bulk_rest14.py`, `verdict_indep.py`, `curves.py`, `aggregate.py`, `power.py`, `check3.py`).

## Disposition: validated (NULL, controls valid), with two required wording corrections (C1, C2) and four minor ones

The measurement and the frozen verdict reproduce exactly. The claims text overreaches in two places (C1, C2).

## Item 1. Protocol, hashes, data: PASS

| Check | Result | Evidence |
|---|---|---|
| `python3 tools/experiment_protocol.py validate protocol.json` | `OK ... (0 finding(s))` | validator also recomputes `freeze.protocol_sha256` over the canonical body (line 326): matches `6a44309417a9...` |
| protocol hash identical in draft commit 2d6c661a and freeze commit 7be877dbf | yes, both `6a44309417a905167606a10754a6fad66de617a16c81feed73cd9cace0a02efb` | `git show` + `protocol_hash()` |
| `quadphase.py` sha256 | `a26745b1...787f`, equals protocol `arms[*].instrument.flags.script_sha256`; identical to the blob at 2d6c661a | `sha256sum` |
| `analyze_quadphase.py` sha256 | `7d03cb87...962b`, equals `analysis_plan.script.sha256`; identical to the blob at 2d6c661a | `sha256sum` |
| `xz -dc rows.jsonl.xz` sha256 | `bc57ac50...8822`, equals `data.sha256` | `sha256sum` |
| rows complete | 385 rows = 9 curves x (1 EC + 40 N_sym + 1 planted) + 1 x (1 + 5 + 1); replicates 0..39 (0..4 at 2^16) contiguous | own count |
| frozen before data | freeze commit 05:49:12Z; first rows commit 96dfd77b4 at 05:52:49 (empty files), 07df91c77 (41 rows) at 07:01; those 41 rows are an exact prefix of the final 385 | `git log`, own diff |
| curves not cherry-picked | I redrew all 10 curves from `derive_seed(sha,'curve',L,0)` with my own Euler-criterion point counter; (p,a,b,n,curve_index) identical for all 10; p = 4093, 8191, 16381, 65521 are the largest primes below 2^L | `mine/curves.py` |

Reproducibility-binding gaps (do not affect the verdict; I reproduce every value on a different host and numpy):
- `measurement.record` promises `python_version`, `numpy_version`, `script_sha256`, but no row or log carries them. `run.log` is only `done` / `exit=0`. The README does not name the tool versions.
- `instrument.commit` is `null`; dirty-tree state of the run is not recorded. `execution.placement.cpus` is 1 while `threads` is 3 (the README discloses the shared cores).
- No `experiment.export/v1` bundle (AGENTS.md "Experiment protocol, export and review"). The sibling studies in `docs/reports/` lack one as well.
- README says "frozen ... commit 2d6c661a". That is `freeze.commit` (the scripts commit). The frozen protocol file itself was committed one second later in 7be877dbf. Same body hash, so only the wording differs.

## Item 2. Frozen verdict recomputed from rows: PASS

`mine/verdict_indep.py` (own code, not the producer's analysis) gives, per curve, u (mid-rank percentile among N_sym draws), above-max, planted ratio, argmax-alpha test, even/odd means. Every value equals `verdict.json` to 1e-12.

| size | N | u | Q_EC above null max | planted / null max | planted argmax alpha in {a0, N-a0} |
|---|---|---|---|---|---|
| 2^12 | 4133 / 3989 / 4007 | 0.650 / 0.700 / 0.850 | no / no / no | 4.854 / 4.700 / 4.787 | yes (3/3) |
| 2^13 | 8231 / 8081 / 8167 | 0.375 / 0.375 / 0.175 | no | 5.190 / 4.357 / 4.596 | yes |
| 2^14 | 16417 / 16273 / 16427 | 0.350 / 0.625 / 0.125 | no | 4.026 / 3.837 / 4.525 | yes |
| 2^16 (descriptive) | 65167 | 1.000 (5 draws) | yes (4.7249 vs 4.7079) | 4.815 | yes |

- Validity: planted ratio min 3.837 (>= 3) and argmax alpha OK on all 10 curves. A/A, pooled per decisive size as the frozen rule defines it: 2^12 1.49%, 2^13 2.23%, 2^14 0.51% (2^16: 1.63%), all <= 3%.
- NULL rule: 9 of 9 decisive curves have u in [0.05, 0.95]. SIGNAL rule: 0 sizes have >= 2 of 3 curves above the null max. Verdict NULL, matching the stored verdict.
- README table: all 10 rows regenerated from the rows (Q_EC, null mean/max, u, planted ratio, rounded as printed): 0 mismatches.
- Extra descriptive recomputation (not part of the frozen rule): mean u over the 9 decisive curves is 0.469 (z = -0.32 against uniform). Q_EC z-scores against each curve's own null range from -1.12 to +1.18, the 2^16 curve being +1.18 (5-draw sd 0.098).
- Observation: per-curve A/A reaches 3.98% (instance 4, N=8081, 2.5 s.e.) and 3.04% (instance 2). The frozen rule pools per size, so it passes (see C3).

## Item 3. Independent Q recomputation: PASS (all 385 rows, not just 3)

Implementation (`mine/indep.py`): the statistic is evaluated by explicit matrix product, F(alpha,beta) = sum_l e((alpha l^2 - beta l)/N) as a (chunk x |S|) by (|S| x N) complex product, with no FFT. It uses the symmetry |F(alpha,beta)| = |F(-alpha,-beta)| to scan only alpha in [1,(N-1)/2]. I cross-checked the half range against an FFT-over-beta evaluation over all alpha in [1,N-1] (`Q_fft`) on the EC row. Points use Fermat inverses. Curve facts are checked per curve: 4a^3+27b^2 != 0, brute-force Euler-criterion point count == n, n prime, n != p, n*G = O.

The three requested rows (instance 1, N=3989, p=4093, a=3447, b=207):

| Row | My Q | Stored Q | abs diff | argmax |
|---|---|---|---|---|
| EC | 4.144042680567 | 4.144042680567 | 8.9e-16 | alpha 252 both; beta stored 525, mine 3464 = N-525 |
| N_sym draw 0 | 4.265375581158 | 4.265375581158 | 8.9e-16 | (1602, 172) both |
| N_sym draw 17 | 3.971803359793 | 3.971803359793 | 4.4e-16 | (1633, 1041) both |
| planted | 21.818850250822 | 21.818850250822 | 3.6e-15 | alpha 546 = alpha0 (also derived from the seed by me) |

- EC log set rebuilt from the row's (p,a,b,n). Generator G = (1, 419): smallest x with a y in 1..p-1, first such y. First 512 points sorted by (x,y), logs of kG.
- The 512 logs are distinct and negation-closed: `set(logs) == {n - l}`. The reason is structural: n is an odd prime, so there is no 2-torsion. Every x has 0 or 2 points, (x,y) and (x,p-y) are adjacent in the sort, and the cut at 512 is even. I confirmed adjacent pairs for instance 1 and set-closure for all 10 curves.
- The beta difference is an exact tie: a negation-closed S gives F(alpha,beta) = F(alpha,-beta). The FFT full-range evaluation returns (252, 525).

Full coverage (`mine/aggregate.py`): all 385 rows recomputed (10/10 EC, 10/10 planted, 365/365 N_sym; size and negation closure of every set checked).

| L | rows | max abs diff in Q | alpha argmax equal to stored (mod +-alpha) |
|---|---|---|---|
| 12 | 126 | 4.0e-15 | 126/126 |
| 13 | 126 | 7.1e-15 | 126/126 |
| 14 | 126 | 3.6e-15 | 126/126 |
| 16 | 7 | 3.6e-15 | 7/7 |

My own Q values reproduce every u and every planted ratio in the table above. In particular the 2^16 comparison holds: Q_EC = 4.724867 against a 5-draw null max of 4.707879.

N_sym and planted sets come from the documented seed rule (`SEED_DOMAIN` + sha, arm, instance, replicate), re-implemented in my code. Their Q values match the stored ones, which confirms the run used these sets and the frozen sha.

No discrete-log solve, relation or closure is claimed, so no certificate gate applies. The EC log table, the one computed discrete-log object, was independently rebuilt and verified (nG = O, point count = n).

## Item 4. Claims in README and lead row

Supported (verified):
- Table, "9 of 9 decisive curves inside the band (u 0.125 to 0.85)", "planted 3.8 to 5.2x the null max, always at alpha0", "A/A at most 2.3%" (pooled, see C3), 2^16 "Q 4.725 against max 4.708".
- "probability 1/6 under the null" for 5 draws: correct under exchangeability.
- "About 4.5 core-hours" for a 40-draw 2^16 rerun: 40 x 395 s = 4.4 h. Only 35 more draws are needed.
- The 2^16 curve is clearly labelled descriptive and uninterpreted.
- Lead row: `best_measured` numbers (9/9; 3.8 to 5.2x) are correct. The new evidence entry and note are accurate. `disposition: open_next_step` stays open, which is consistent. `forecloses` is a re-proposal keyword list, not a claim, and is unchanged. The `lead_atlas.py --check` errors (18) are ledger_ref items unrelated to this lead (sparse checkout).

Corrections:

**C1 (required, scope of "closes degree-2 phase leakage at toy scale").** AGENTS.md core rule 6: negative evidence closes only the exact tested scope. The README verdict paragraph and the PDF say the result "closes degree-2 phase leakage of the small-x predicate at toy scale". What was tested:
- one statistic, the single maximum over (alpha, beta) of one quadratic-phase character sum. It has no power against multi-peak or diffuse leakage, nor against Gowers-U3 structure such as bracket or nil-sequence correlation (the lead title mentions U^3);
- B = 512 at N = 4k to 16k, 3 curves per size, one generator rule;
- a positive control that is full coherence only (planted set 100% structured, Q about 22, ratio about 4.6x on average). The protocol never states a minimum detectable effect.

Validator sensitivity probe (mine/power.py, not evidence of the study): at N = 4133 and N = 4007, 3 trials per level, a fraction f of the 256 negation pairs is drawn from the planted set and the rest random.
- Q is at or below the null max (4.51 and 4.79) in nearly every trial for f <= 0.125.
- At f = 0.19 to 0.25 it is above the null max in 9 of 12 trials, but its argmax is at alpha0 in only 5 of 12.
- It is above the null max in 3 of 3 trials, with argmax at alpha0, for f >= 0.375.

So the frozen NULL excludes a coherent quadratic-phase fraction of roughly >= 0.3 of the 512 logs at one (alpha, beta). It cannot see a smaller one, which is the 1/polylog caveat the README already names, now with a number. Suggested wording: "finds no quadratic-phase peak above the negation-closed null on 9 curves at N about 2^12 to 2^14 (B = 512); a peak carrying roughly 30% or more of the factor base would have been seen (validator probe); weaker or multi-peak leakage is untested." Replace "closes degree-2 phase leakage" accordingly, in the README verdict paragraph and `report.typ` / PDF.

**C2 (required, lead row and README "discriminator is met").** The lead's `discriminates` field still reads: "Q inside the symmetric null's 5-95% band on at least 5 of 6 curves", at N in {2^14, 2^16}, 3 curves each. The executed frozen rule is different: 8 of 9 curves at 2^12 to 2^14, with 2^16 reduced to one descriptive curve and 5 draws. That 2^16 curve is outside the 5-95% band (u = 1.0). The original discriminator was never run, so "The lead's discriminator is met on the NULL side" (README "Consequence") is not literally true. What was met is the amended frozen rule QUADPHASE-20261104. The protocol discloses the size reduction in `links.note`, but neither the README Consequence nor the lead's `discriminates` field does. Fix both: state that the amended rule was met, that 2^14 and 2^16 with 3 curves each (the original plan) was not run, and update `discriminates` to the frozen rule.

Minor:
- **C3.** "A/A even/odd difference is at most 2.3%": this is pooled per size (frozen rule). Per-curve differences reach 3.98% (instance 4) and 3.04% (instance 2). Say "pooled per size".
- **C4.** "no size has a curve above the null maximum": true for the decisive sizes only; the 2^16 curve is above its 5 draws (stated one bullet later). Say "no decisive size".
- **C5.** Planted sets are not |S| = 512 (474 to 592). The protocol and `quadphase.py` say "~B", but the README Design bullet does not. Q is normalised by sqrt|S|, so the control stays valid. Add one clause.
- **C6.** Cosmetic: pandoc renders "N ≈ 2^12–2^14" in the PDF as a garbled superscript ("2^{12–2}14"). Write it as "2^12 to 2^14". The figure label "pass >= 3x" overlaps the bars. I regenerated `quadphase.svg` with `figures.py` under matplotlib 3.11.2; it is not byte-identical, and I did not diff the data layer beyond checking the committed figure's markers against the table.

## Requirement summary

| Requirement | Pass / fail | Evidence |
|---|---|---|
| Frozen, committed artifact set; commit recorded | pass | commit 6e367d4f9; clean tree |
| Protocol validates; script and data hashes bind | pass | validator output; three sha256 matches |
| Frozen before data; rows prefix-consistent | pass | git log; 41-row prefix check |
| Verdict recomputed | pass (NULL) | `mine/verdict_indep.py`; 385/385 rows reproduced |
| Controls: null, positive, A/A | pass | planted min 3.84x, alpha ok 10/10; A/A pooled <= 2.23% |
| Controls: sensitivity floor stated | fail (disclosure only) | C1 |
| Certificate discipline | not applicable (no DL solve or relation claimed); EC log table rebuilt independently | Item 3 |
| Reporting contract (one unit, ratios, controls priced) | pass; m=83 / ECC2K-130 rules not engaged | README |
| Claims match evidence | partial | C1, C2 required; C3 to C6 minor |
| Reproducibility bindings | partial (versions and export bundle missing; non-blocking) | Item 1 gaps |
