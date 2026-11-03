# Independent re-validation of the EXP-SEMAEV-93d5cc / -6e9dcf run records

- **Task:** TASK-20261103-f8f2d2 (validator; fresh independent session, zero scientific trials)
- **Review plan:** RP-BATCH-7c689b (`coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/review-plan.yaml`), joints J1–J6, controls PTM and VAC
- **Runs:** RUN-SEMAEV-9cab7b (icinv-m4), -3e69b6 (fib-004), -4be606 (fib-005), -894e27 (fib-decision), -2a8498 (mtic-007), -fcd67c (mtic-008) of EXP-SEMAEV-93d5cc, and RUN-SEMAEV-0e5876 (mtic-010b) of EXP-SEMAEV-6e9dcf
- **Machine-readable record:** `review.json` (per-run verdicts, findings, `review_attestation`); every number below comes from the committed check scripts and their `.out.json` outputs in this directory.

This report gives verdicts on the joints only. It decides no evidence strength and no hypothesis status; those belong to the Coordinator task TASK-20261103-2c99e6.

## Frozen inputs

| check | result |
|---|---|
| review-plan.yaml sha256 | `387679…dfc4`, equal to the handoff's `frozen_input_sha256` |
| blind-input-manifest.json sha256 | `3af6bd…f8ab`, equal to the handoff's `frozen_input_sha256` |
| manifest files rehashed | 408/408 match. The 101 archived EXP-FIB-001, EXP-MTIC-001 and EXP-ICINV-e0cd8f run files were outside the sparse checkout and were checked out before rehashing. |
| store-backed `RUN-SEMAEV-0e5876/arms.tar.gz` | hydrated with `tools/artifacts/artifacts.py pull`. Its sha256 `f682e693…974e` equals `.artifacts.json`, the original git blob at run commit 93280014b7, and the execution receipt. |

## Verdicts

| run | cell | J1 | J2 | J3 | J4 | J5 | J6 | PTM | VAC |
|---|---|---|---|---|---|---|---|---|---|
| RUN-SEMAEV-9cab7b | icinv-m4 | **breaks** (F1) | holds | holds | holds | holds | — | holds | holds |
| RUN-SEMAEV-3e69b6 | fib-004 | **breaks** (F1) | holds | holds | holds | holds | — | holds | inconclusive |
| RUN-SEMAEV-4be606 | fib-005 | **breaks** (F1) | holds | holds | holds | inconclusive | — | holds | inconclusive |
| RUN-SEMAEV-894e27 | fib-decision | holds | holds | holds | holds | inconclusive | — | holds | holds |
| RUN-SEMAEV-2a8498 | mtic-007 | **breaks** (F1) | holds | holds | holds | inconclusive | — | holds | inconclusive |
| RUN-SEMAEV-fcd67c | mtic-008 | **breaks** (F1) | holds | holds | holds | inconclusive | — | holds | inconclusive |
| RUN-SEMAEV-0e5876 | mtic-010b | holds | holds | holds | holds | inconclusive | holds | holds | inconclusive |

"—" means J6's claim names RUN-SEMAEV-0e5876 only, so it has no verdict on the other runs. Per-joint summary (attestation): J1 **breaks**; J2, J3, J4, J5 (over the plan's scope: ICINV curves and FIB C16-1 targets) and J6 **hold**; PTM holds; VAC is **inconclusive**.

![verdicts](verdicts.svg)

## Failed and inconclusive findings

**F1 (J1 breaks on five runs).** In RUN-SEMAEV-9cab7b, -3e69b6, -4be606, -2a8498 and -fcd67c, `manifest.yaml` `run.code.commit` is not the launch commit. `environment.json` and the execution receipt's `authority.commit` both record the launch commit. The manifest instead records the HEAD at the time it was written, which is a commit the supervising session made during the trial: either the previous trial's record commit or, for 9cab7b, the round-1 review-plan commit 28789aca.

| run | manifest commit | launch commit |
|---|---|---|
| 9cab7b | 28789aca | 13820fb0 |
| 3e69b6 | a34afc78 | 28789aca |
| 4be606 | ef0b7a83 | a34afc78 |
| 2a8498 | fec8cb0b | ef0b7a83 |
| fcd67c | f1bf275a | fec8cb0b |

All 20 pinned source hashes are identical at both commits, and no recorded value depends on this field. I score it *breaks* because the plan's frozen breaking artifact is "an inconsistent receipt field" across manifest, environment and receipt. Every other J1 check passed on all seven runs:

- receipt artifact hashes
- argv: the plan, `launch.json` and `command.txt` agree
- plan and spec sha256 at the launch commit
- source blobs at the launch commit
- every arms.tar.gz member against `arms-manifest.json`
- timing windows and statuses

**J5 inconclusive (five runs).** In fib-005, mtic-007, mtic-008 and mtic-010b every solve hit its cap. The arms therefore record no basis size or degree for an independent re-derivation to match. fib-decision does not call S4. Over the plan's own J5 scope, J5 holds (see below).

**VAC inconclusive (five runs).** In these runs some legacy-vs-repaired equalities on S4-dependent outputs are equalities of capped values:

- fib-004: C16-2 (legacy 75/75 capped, repaired 31/31 capped)
- fib-005: C20-1 and C20-2
- mtic-007: 16-bit
- mtic-008: 20-bit and 24-bit
- mtic-010b: every T_desc

Capped equality cannot show that the two S4 polynomials agree, and J5 shows they differ on every curve tested (227 vs 439 terms generically). Conclusion fields that move monotonically with the capped value are unaffected: `resource_exhaustion`, all-capped, and K\* = ∞ / regime (i), which follow from a lower bound on T_desc.

## What holds, and how it was checked

- **J2 arm provenance (7/7).** Both pinned sources hash-match. Every recorded installed fingerprint equals the one I derived independently: legacy has free symbols {x1,x2,x4}, 227 terms over Z, degree 16, residue 47 mod 101; repaired has {x1..x4}, 439, 12, 0. Every FIB spawn-child log line carries its own arm's module and hash, one per solve (fib-004: 275/275 and 231/231; fib-005: 90/90 and 90/90). In fib-decision, each arm read its own arm's FIB-004/005 `raw.json`, byte-identical. Arms differ only in `--arm`/`--out` and the bound `s4_expr`.
- **J3 legacy-reproduction control (7/7).** I recomputed CTRL-LEGACY-REPRO from the specification text with my own comparator, and it agrees with the recorded pass in every cell. The compared fields are listed per cell in `review.json`. Every conclusion field is compared between archive and legacy, and none differs. ICINV matches 552/552 records on (a, b, s4_support, singular-locus dim, degree, unit).
- **J4 independent extraction (7/7).** I recomputed every metric and conclusion field from raw arm outputs and archived runs without using compare.py. All match the recorded values, with 0 differences. This includes the ICINV distributions, the FIB counts, medians and basis histograms, the fib-decision gate chain, the MTIC counts and medians, and mtic-010b's K\*/regime for each accounting.
  - The fib-decision Spearman ρ_s is reproduced to full precision: archived −0.0236, legacy −0.0969, repaired −0.3656.
  - In every cell the conclusion fields are unchanged between repaired and archived and between repaired and legacy. ICINV is the exception: its `m4_s4_support_values` and `m4_singular_locus_dim_degree_values` change ({210, 225, 227}→{391, 439} and 2/60→2/39), and all 552 records differ between arms.
- **J5 blind re-derivation (plan scope holds).** I wrote my own code from the statement S4 = Res_t(S3(x1,x2,t), S3(x3,x4,t)). The x3-dropping substitution gives Res_t(S3(x1,x2,t), S3(t,x4,t)). It uses a sparse F_p polynomial engine plus Singular `resultant` as a second derivation, and Singular reduced degrevlex bases.
  - ICINV, all 552 records: the repaired arm equals my exact term count, and the legacy arm and the archive equal my x3-dropping count, with 0 mismatches. Values are {391, 439} and {210, 225, 227}.
  - FIB C16-1, all 200 targets: basis size, max degree and triviality agree 200/200 for the archive and the legacy arm (x3-dropped) and for the repaired arm (exact). I regenerated the instance with `driver/instances.py`, which imports only `harness.toycurve`. Its fingerprint equals `frozen-instances.yaml`.
- **J6 successor write conduct (holds).** Checks, all passing:
  - Run commit 93280014b7 adds exactly the 16 `artifact_paths` of TASK-20261019-212d85 and nothing else.
  - No commit between launch and the run commit touched an archived or parent path.
  - All 19 frozen plan inputs are unchanged at HEAD.
  - Every recorded dependency read is hash-checked: 12/12 per arm, against the plan hash and HEAD bytes, or against the parent arms-manifest member and the parent tar bytes.

  I evaluated J6 against the plan's statement of the claim; I did not read CORR-20261024-8df12c (see deviations).
- **PTM (holds).**
  - PTM-1: the comparator applied to repaired vs archive in ICINV reports 0/552 equal, so it breaks, as required.
  - PTM-2: a perturbed copy of a legacy output makes the comparator break in every run (ICINV degree +1; FIB basis size +1; one MTIC or FIB capped flag flipped; mtic-010b K\* set finite; fib-decision status flipped), while the unperturbed control passes.
  - PTM-3: the units where legacy-vs-repaired equality has zero common uncapped targets are listed, and none of them is read as polynomial agreement (see VAC).

## Observations (no verdict change)

- **O1 (RUN-SEMAEV-0e5876).** A second, different execution was committed under the same run id on 2026-10-30, on a side branch: c054500cff by executor-run-20261030-01a179ee, `infrastructure_error`, with arm exit codes 1/1. Merge b825ee6ea5 kept the original bytes. HEAD equals the run commit except for the store move. The colliding record remains in reachable history. Two other points on this run:
  - `tools/check_run_immutability.py 93280014b7 HEAD` exits 1 only because `arms.tar.gz` became a store pointer (b0036a4889, 13b81c737b). The bytes are proven identical.
  - The manifest's `code.command` names the parent launcher by design.
- **O2.** RUN-SEMAEV-0e5876 ran on 2026-10-19 from 01:57 to 02:22Z and was committed on 2026-10-24 at 19:18Z.
- **O3.** In both FIB arms, `driver.decompcost._worker` is replaced by `fib_child.solve`. That wrapper hashes and loads the arm module inside the 20 s capped window. This is not an arm difference, but it adds a small constant to each child's time relative to the archive.
- **O4.** `median_cost_seconds` is the upper median (`sorted[n//2]`), which is the archived pipeline's convention. The archived predictor ratio 8.618669826845604e-06 reproduces exactly with it. The mean-of-middle-two median differs by less than 0.1%.
- **O5.** Timing-derived fields rest on one execution per arm.
  - The repaired C16-1 ρ_s = −0.366 (p < 0.001) sits against the |ρ_s| ≥ 0.4 gate.
  - The archive-vs-legacy A/A difference of 0.073 in ρ_s comes from timing alone.
  - Predictor-cost ratios for C16-1 are 8.62e-6 (archive), 4.16e-6 (legacy) and 6.5e-8 (repaired). All are ≤ 0.1.
- **O6.** In fib-004 the repaired arm measured 31 C16-2 targets against 75 in the other arms. It stopped at `per_run_wall_cap_1800s` because its C16-1 solves took a median of 3.68 s against 0.058 s.
- **O7.** In mtic-010b, the ablation T_desc values exist only as run_mtic's per-base summary.
- **O8.** The successor specification's invalidation rule was copied verbatim from the parent and names only `experiments/EXP-SEMAEV-93d5cc/` as writable. The handoff `write_scope` governs, and the run respected it.
- **O9.** Both specifications changed after launch only in their `status` field (approved → analyzed).

![J5 and O5](j5.svg)

## Procedure deviations

1. **Blindness conflict.** DEC-20261024-85695c and CORR-20261024-8df12c are listed in the frozen manifest, but they cite EV-SEMAEV-593b7a, DEC-20261018-3b4a32 or CORR-20261018-d51221. The may_not_read clause "any later record that cites" therefore covers them, and I did not read them; I only ran a grep count of the cited ids.
2. **One task owns both J2 and the blind re-derivation.** J2's attack plan refers to the pins "in the implementation", while `blind_from` includes `experiments/EXP-SEMAEV-93d5cc/implementation/`.
   - J5's code and outputs were finished first.
   - Only afterwards, for J2, did I read `arms.py` and `fib_child.py` in full and `worker.py` and `launch.py` as grep excerpts.
   - I never opened `compare.py`, `check.py`, `launch_successor.py`, the vendored legacy source or `harness/semaev.py`; I only hashed the last two.
   - Result: `tools/check_review_independence.py` reports this read as a blind_from intersection. The plan has no `phased_release` contract, so the checker compares the union of all reads.
   - The tool-call order is recorded in this session's transcript.
3. **Path names from may_not_read.** `git show --stat 28789aca` displayed a path name from the may_not_read list (`experiments/EXP-SEMAEV-93d5cc/reviews/review-plan.yaml`), and commit subjects naming TASK-20261018-83a561 appeared in git log output. I read no content from any may_not_read path.

## Independence check (as run)

```
python3 tools/check_review_independence.py --plan coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b/review-plan.yaml \
  --batch coordination/goals/GOAL-ECDLP-001/batches/BATCH-7c689b --reports <this directory>/review.json
FAIL: ...review.json: re-deriver TASK-20261103-f8f2d2 read 1 blind_from path(s) -- experiments/EXP-SEMAEV-93d5cc/implementation/;
      the re-derivation is not independent of the implementation it was meant to check
1 independence problem(s) across 1 report(s)   (exit 1)
```

This is the only problem the checker reports. Its cause is deviation 2. The Coordinator decides whether the recorded order, with J5 completed before the reads, is acceptable. If it is not, a separate blind task can re-run J5 from the statement.

## Reproduce

All scripts are in this directory. Pass `<arms_root>` as a directory holding the seven extracted `arms.tar.gz` trees, laid out as `<run6>/arms/...`.

```
python3 j5_rederive.py <repo> j5_rederive.out.json        # needs Singular (/opt/conda-sage/envs/sage/bin/Singular)
python3 j5_full.py <repo> <arms_root> j5_full.out.json
python3 j1_integrity.py <repo> <hydrated 0e5876 arms.tar.gz> j1_integrity.out.json
python3 j2_provenance.py <repo> <arms_root> j2_provenance.out.json
python3 j6_conduct.py <repo> <arms_root>/0e5876 j6_conduct.out.json
python3 j34_extract.py <repo> <arms_root> j34_extract.out.json
python3 ptm_extra.py <repo> <arms_root> ptm_extra.out.json
python3 build_review.py .                                  # review.json and the SVG figures (matplotlib)
```
