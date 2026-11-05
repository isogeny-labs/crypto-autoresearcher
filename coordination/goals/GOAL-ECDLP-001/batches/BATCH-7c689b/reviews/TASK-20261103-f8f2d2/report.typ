#set page(paper: "a4", margin: 1.6cm)
#set text(size: 9.5pt)
#set par(justify: true)
#show heading: set block(above: 0.9em, below: 0.5em)
#show raw: set text(font: "Libertinus Serif", size: 1.05em)  // one embedded font family keeps the PDF under the 64 KiB data-file limit

= Independent re-validation: EXP-SEMAEV-93d5cc / -6e9dcf run records

*Task* TASK-20261103-f8f2d2 (validator, fresh independent session, zero scientific trials) ·
*Review plan* RP-BATCH-7c689b (joints J1–J6, controls PTM and VAC) · *Recorded* 2026-11-03 ·
*Runs* RUN-SEMAEV-9cab7b (icinv-m4), -3e69b6 (fib-004), -4be606 (fib-005), -894e27 (fib-decision),
-2a8498 (mtic-007), -fcd67c (mtic-008), -0e5876 (mtic-010b). Machine-readable record: `review.json`;
every number comes from the committed check scripts in this directory. This report gives per-joint verdicts only and
decides no evidence strength or hypothesis status (Coordinator task TASK-20261103-2c99e6).

== Frozen inputs
Review plan sha256 `387679…dfc4` and manifest sha256 `3af6bd…f8ab` equal the handoff values; all 408 manifest files
rehash equal. `RUN-SEMAEV-0e5876/arms.tar.gz` was hydrated from the artifact store; its sha256 `f682e693…974e` equals
`.artifacts.json`, the original git blob (run commit 93280014b7) and the execution receipt.

== Verdicts per joint per run
#figure(image("verdicts.svg", width: 92%), caption: [Verdicts per joint per run. J6's claim names RUN-SEMAEV-0e5876 only
("n/a" elsewhere). Per-joint summary: J1 breaks; J2–J6 hold (J5 over the plan's ICINV and FIB C16-1 scope); PTM holds; VAC inconclusive.])

== Failed and inconclusive findings
- *F1 — J1 breaks (9cab7b, 3e69b6, 4be606, 2a8498, fcd67c).* `manifest.yaml` `run.code.commit` records the HEAD at
  manifest-write time, which is a commit the supervising session made during the trial, not the launch commit that
  `environment.json` and the execution receipt record. Manifest/launch pairs: 28789aca/13820fb0, a34afc78/28789aca,
  ef0b7a83/a34afc78, fec8cb0b/ef0b7a83, f1bf275a/fec8cb0b. All 20 pinned sources are identical at both commits and no recorded value
  depends on the field. It is scored *breaks* because the plan's breaking artifact is an inconsistent receipt field.
  All other J1 checks pass on all runs: receipt hashes, argv, plan and spec at the launch commit, source blobs, arms members, timing.
- *J5 inconclusive (4be606, 2a8498, fcd67c, 0e5876, 894e27).* Every solve is capped (no basis value to match), or S4 is not called.
- *VAC inconclusive (3e69b6 C16-2, 4be606, 2a8498, fcd67c, 0e5876).* Legacy-vs-repaired equalities on S4-dependent outputs
  there are equalities of capped values. They cannot show the polynomials agree, and J5 shows they differ (227 vs 439 terms). Conclusion fields
  that move monotonically with the capped value (resource exhaustion, all-capped, K\* = ∞ and regime (i) from a T_desc lower bound) are unaffected.

== What holds
- *J2 (7/7).* Installed fingerprints equal the validator's derivation. Legacy: {x1,x2,x4}, 227 terms, degree 16, residue 47.
  Repaired: {x1..x4}, 439, 12, 0. FIB spawn-child logs carry one line per solve with the arm's own module and hash
  (275/275, 231/231, 90/90, 90/90). Each fib-decision arm read its own arm's FIB-004/005 outputs byte-identically.
- *J3 (7/7).* CTRL-LEGACY-REPRO, recomputed from the specification text with the validator's comparator, passes in every
  cell and agrees with the record. Every conclusion field is compared and none differs between archive and legacy.
- *J4 (7/7).* Every metric and conclusion field, recomputed from raw arm outputs and archived runs without compare.py,
  matches the recorded value (0 differences). This includes ρ_s for C16-1 (archive −0.0236, legacy −0.0969,
  repaired −0.3656) and K\*/regime for each accounting.
- *J5 (plan scope).* Own code built from the statement S4 = Res_t(S3(x1,x2,t), S3(x3,x4,t)), with the x3-dropping form
  Res_t(S3(x1,x2,t), S3(t,x4,t)), a sparse F_p engine cross-checked with Singular `resultant`, and Singular reduced degrevlex bases.
  ICINV: 552/552 records match for the repaired arm (exact), the legacy arm and the archive (x3-dropped). FIB C16-1: 200/200 targets agree on
  basis size, maximum degree and triviality for all three sources.
- *J6.* The run commit adds exactly the 16 handoff `artifact_paths`. No archived or parent path changed between launch and
  the commit, the 19 frozen inputs are unchanged at HEAD, and all 12 recorded dependency reads per arm are hash-checked.
- *PTM.* PTM-1: the repaired-vs-archive comparison breaks (0/552 equal). PTM-2: a perturbed legacy copy breaks the
  comparator in every run. PTM-3: censored equalities are listed and none is read as polynomial agreement.

#figure(image("j5.svg", width: 100%), caption: [Left and centre: J5 agreement counts (RUN-SEMAEV-9cab7b, 552 records;
RUN-SEMAEV-3e69b6, C16-1, 200 targets). Right: recomputed Spearman ρ_s(n_R, cost) for C16-1 (n = 200) per arm in
RUN-SEMAEV-894e27 against the |ρ_s| ≥ 0.4 gate. These values are timing-derived from one execution per arm (O5).])

== Observations (no verdict change)
O1: a second, failed execution (2026-10-30, c054500cff, `infrastructure_error`) was committed under RUN-SEMAEV-0e5876's id
on a side branch; merge b825ee6ea5 kept the original bytes. `check_run_immutability.py` flags only the sanctioned store move.
O2: 0e5876 ran on 2026-10-19 and was committed on 2026-10-24. O3: both FIB arms wrap `_worker` and load the arm inside the
capped child. O4: `median_cost_seconds` is the upper median, the archived convention. O5: timing-derived fields rest on one
execution per arm. O6: the fib-004 repaired arm reached 31 C16-2 targets against 75 (per-run cap). O7: mtic-010b ablation
T_desc is available only as a summary. O8: the successor specification's invalidation rule was copied from the parent. O9: specifications changed after launch only in status.

== Procedure deviations and independence check
(1) DEC-20261024-85695c and CORR-20261024-8df12c are in the manifest, but the "later record that cites" clause covers them;
they were not read, and J6 was judged against the plan's statement of the claim. (2) The same task owns J2, whose attack plan
refers to the implementation's pins, and the blind re-derivation. J5 code and outputs were completed first; `arms.py` and
`fib_child.py` (and excerpts of `worker.py` and `launch.py`) were read afterwards for J2. The vendored source and
`harness/semaev.py` were only hashed. `tools/check_review_independence.py` therefore exits 1 with exactly one problem,
"re-deriver read blind_from path experiments/EXP-SEMAEV-93d5cc/implementation/". The Coordinator decides whether the
recorded order suffices or whether a separate blind task should repeat J5. (3) `git --stat` output displayed one may_not_read
path name; no content of any may_not_read path was read.
