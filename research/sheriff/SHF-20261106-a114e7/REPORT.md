# Sheriff case SHF-20261106-a114e7: independent re-audit of current main

This is an audit record. It changes no research state and repairs nothing.
Verdicts are in `findings.yaml`, which passes `tools/sheriff.py check-case` and
is composed by `scripts/compose.py` from the eight reader files plus
`scripts/session.yaml`.

Heads audited, all origin/main and clean:
- crypto-autoresearcher `da442739db`;
- isogeny-labs/crypto `3a7a0f98a`;
- isogeny-labs/cryptanalysis `5bdfb496d`.

Auditing session: `session_01TCbLH84PotMkHyFGFE4ifE`. It was commissioned by
`session_016SURwTvgaQmnMnhpa1SLXQ`; see **Independence** before citing anything
here.

## Prior

From `prior.md`, written before any producer artifact was read. I expected:
- loaders and refusals to land narrowly, with run-manifest errors recurring;
- a zk test that does not isolate its check;
- residual "descends" prose;
- an overstated PFDR replay;
- ICPERF wording sliding into speed, latency or n=83, with a §5a fork;
- the n=83 band to hold, with no rank-finder port;
- CI enforcement still missing, with `pull_request_target` the riskiest change.

How the prior fared:

| Expectation | Outcome |
| --- | --- |
| Loaders land narrowly | **Confirmed.** Duplicate-key refusal covers two registries and driver manifests only (LGX-1). `complete_manifest` still publishes driver seed and parameters unchecked (LGX-2). |
| Run-manifest errors recur | **Refuted.** validate_ledger is down from 67 new errors to 1. |
| Non-isolating zk test | **Confirmed.** See ZKX-1 and ZKX-2. |
| Residual "descends" prose | **Confirmed.** It survives only in crypto's paper catalogue (LNX-1). |
| Overstated PFDR replay | **Confirmed, minor.** See PFX-1. |
| ICPERF speed or n=83 language | **Refuted** for the ledger, reports and knowledge. One derived export does it (ICR-1). |
| §5a fork | **Partly confirmed.** See ICR-2. |
| Band holds, no port | **Confirmed.** |
| CI enforcement missing | **Confirmed** (CIX-1). The `pull_request_target` change runs no PR code, but it masks pre-merge state (CIX-2). |

## Verdicts

The case has 146 claims, inventoried in the producers' words by eight readers
and the session:

| Verdict | Claims |
| --- | --- |
| upheld | 45 |
| upheld_scoped | 59 |
| overclaimed | 32 |
| unsupported | 5 |
| broken | 2 |
| not_covered | 3 |

There are 52 findings: **no blocker, 11 major, 41 minor.**

The two `broken` claims:
- **SES/C-CI-MERGE**, the AGENTS.md merge rule as practised: PRs merge with
  applicable checks pending or failed (CIX-1, CIX-2).
- **pfdr/PFX-C-EV-apbound**, the label-AP size bound in EV-PFDR-07d608: it was
  invalid below 4 labels (PFX-6), and CORR-20261029-1aaef6 has since
  withdrawn it. The correction is additive and accurate; one later record
  restates the bound (PFX-5).

## Blockers

None.

## Major findings

| Id | Area | Summary |
| --- | --- | --- |
| CIX-1 | CI | `ledger-and-harness` and `merge-hygiene` still do not gate merge. #3065 merged at 02:20:55Z with ledger, merge-hygiene, ledger-and-harness, static-checks and records still running on its head (run 42149688322). |
| CIX-2 | CI | Post-merge `pull_request_target` (closed) runs post success on the PR head SHA and mask the pre-merge state. #3056 merged with lab-parity failed (run 42137487481); a green run on the same SHA appeared 4 s after merge (run 42149730300). |
| SES-INDEP | Independence | The commissioning session, which will also merge this PR, produced the ICPERF and PFDR records under audit (91 commits on main). The auditing session produced nothing in scope. |
| ZKX-1 | zk | Deleting only the FRI last-layer fold comparison (`crypto:src/zk/stark.rs:625-631`) fails no test, yet the check is soundness-critical. A modelled constant-final-layer forgery passes that mutant. This is what remains of S2N-1. |
| ZKX-2 | zk | `rejects_tampered_evaluations` tampers two evaluations per forgery, so deleting any single PLONK evaluation comparison (`plonk.rs:360-365`) leaves every test green. That includes the `Z(ζω)` check that was the S2N-10 defect. |
| ZKX-3 | zk | The PLONK Fiat–Shamir transcript absorbs only the proof's polynomials, never the circuit or a public input (`plonk.rs:315-325`; re-checked by the session). In the model, a proof made first and then fitted with a solved `q_C` is accepted for an unsatisfiable circuit. The module's Schwartz–Zippel / Fiat–Shamir sentence overclaims. No claim in scope cites PLONK. |
| LGX-2 | Ledger | `complete_manifest` publishes run-level seed and parameters unchecked: a driver's `run.seed: 99` sits beside the supervisor's `inputs.seed: 1`. |
| LGX-3 | Ledger | The runbook replay tolerance is declared and recorded, but has no upper bound (`tools/runbook.py:1062-1085`; re-checked). At `rel_tol=1`, a 1000x change replays as matched and the audit is clean. |
| ICR-1 | ICPERF | `tools/progress_metrics.py:277-281` exports EXP-ICPERF-284bc4's assumed and planted constants (370 and 371) as "nanoseconds per probe", and EXP-ICPERF-283a70's synthetic draws as "probes per target" (re-checked). The relabel ordered by DEC-20261105-8a9984 NA-2 is not done. |
| LNX-2 | Lean | The #2670 target review attests independence, but its commit carries the same session id as both commits that wrote the theorem. It has no review_plan and no blind re-derivation, and `check_review_independence.py` exits 2. Its `validated_scoped` outcome is not admissible. The receipts correctly keep `semantic_review: pending`. |
| LNX-3 | Lean | The reader judged this case self-audited because its commits carry the producer's `Claude-Session` trailer. The session answers this under SES-INDEP: the trailer was requested by the commissioner, and the auditing session is a different one. The finding stands as written. |

## Per change area

### 1. Ledger and tooling (readers/ledger.yaml)

**validate_ledger.** On main, 1 new error out of 1,211, with 1,210
grandfathered. The one error is RUN-BINSTD-f7ca97, which was already among the
prior case's 67.
- The reader's recount at `b7d5e65b9f` reproduces those 67 line for line.
- 66 were resolved: by run and schema supersessions, by registry
  de-duplication (#2609), and by the AUXIN and review-plan rules.
- It was run on a materialised tree, because the sparse checkout makes the
  validator refuse.

**#2659 (duplicate keys, contradictions, empty manifest, PR-scoped check).**
- Duplicate-key refusal is upheld for the two registries and driver manifests
  only (LGX-1).
- The empty-manifest gate rejects all 13 variants tried.
- The PR-scoped `check_run` is upheld, except for runs whose only manifest is
  `manifest_v2.yaml` (LGX-5).
- Contradiction refusal is **overclaimed** (LGX-2).

**#2663.** The completion sources (20 of 20 keys), CORR-20261028-1e1ff4 (141
and 124 recounted) and CORR-20261028-a02dba are upheld.

**#2671 and #2674.** The four session audits are upheld, scoped. The rulings
DEC-20261029-9bc3ff, -22e05b and -5554ee and CORR-20261029-892bca have true
premises.

**#2686 (session-bytes guard).** It refuses modified, deleted and spliced
files. It misses unrecorded extra files, non-merge commits under `--absolute`,
and session directories outside `experiments/` and `examples/` (LGX-4).

**#2689 and #3059 (runbook).**
- Float tolerance is **overclaimed** (LGX-3).
- Interpreter parity, the session-id collision guard and the multi-journal
  audit are upheld, scoped.
- A session with zero valid units audits clean with nothing replayed, and the
  parity docs are stale (LGX-8).

### 2. STARK/PLONK, crypto #2747 (readers/stark.yaml)

`cargo test --release --lib zk::` was **not run**: executing crypto code was
refused. Every "would fail if deleted" statement is from code reading, backed
by two independent models in `scripts/readers/stark/` (FRI over Goldilocks,
and PLONK with a byte-copied transcript).
- **Fixed:** S2N-2 (depth gate isolated), S2N-3, -4, -5, -7, -8 and -11.
- **Partially fixed:** S2N-1 (see ZKX-1), S2N-6 (stale text, ZKX-4), S2N-9
  (Groth16 still has no negative test) and S2N-10 (the code is fixed, but no
  regression test pins it: ZKX-2).
- **Blind re-derivations match:** the FRI fold, the layer count log2 n + 1, the
  quotient (gate + α·perm + α²·L₁(Z−1)), the disjoint cosets 1, 2, 3, and
  ε_field = 2^-217.6.

### 3. Lean (readers/lean.yaml; scripts/lean/)

**TranslationDescent.**
- `lake build CryptoResearch.Quotient.TranslationDescent` succeeded (631 jobs,
  Lean v4.35.0, pinned Mathlib).
- `#print axioms translation_commutes_iff_two_torsion` gives `[propext]`.
- The proves-too-much control (the same proof on `3 • T`) fails as it must.
- Statement fidelity is upheld. Kernel `decide` tests pass on `ZMod 4` and on
  `ZMod 2 × ZMod 4`. The commutation-to-descent step stays prose, as the file
  says.

**L-N9 rename.** Complete in live text. The old name survives only in dated or
immutable records. `crypto:papers/ecdlp-index-calculus-program/sections/companion_catalogue.tex:317`
still says "Proved (Lean-formalized) that only 2-torsion translations
descend" (LNX-1).

**#2670 target review.** Its fidelity conclusion reproduces, but its
independence is unsupported (LNX-2).

**Full workspace.** Not covered (claim SES/C-LEAN-WS).
- 9,141 of 9,142 jobs built without a Lean error.
- `CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` was
  out-of-memory killed twice (exit 137) on this 15 GB host. That is an
  impediment, not evidence.
- Without it, `CryptoResearch.olean` was never produced, so `AxiomAudit.lean`
  did not run.

### 4. PFDR evidence review (readers/pfdr.yaml)

The core reading of EV-PFDR-07d608 is upheld.
- 53 of 53 receipt files re-hash, and the calibration reproduces.
- Controls behave: the plant is flagged in 44 of 44 cells, and the A/A null
  reads null.
- Preregistration holds, no threshold moved, and no execution proof is
  claimed.

**The 3.11 replay claim is upheld, scoped.** The producers' exact replay ran
on a different build of CPython 3.11.15 and covered 4 of the 5 runs, not the
census run. The reader repeated those four under 3.11.18 and every output file
is byte-identical. The census under 3.11 is not covered here. A 3.13.17 control reproduces the recorded drift
exactly: 2 summary leaves (416 and 402 ulps) and 479 analysis leaves. What a
replay is (it bounds fabrication and is not reproduction), and what the audit
instrument can see, are findings:
- PFX-1: the "reproduced four ways" wording.
- PFX-3: the bb0d26 audit compares three summary integers. It cannot see
  per-cell values or detect a full reseal.

**Overclaimed:** the "strong" grade (one run set, no fresh-curve census;
PFX-2), and KN-FIND-c81e5b's use sentence, which is wider than the tested
object (PFX-4).

**CORR-20261029-1aaef6** is additive and correct. A later record,
DEC-20261029-8d9b43 FR-3, restates the withdrawn bound (PFX-5).

### 5. ICPERF v2 chain (readers/icperf-receipts.yaml, readers/icperf-interpretation.yaml)

**Re-derivations.** Both readers derived the quantities blind from the spec
text, then matched all 9 raw rows exactly.
- **925/4** = c_probe·c_state·bl_den/(bl_num·c_step²) = 7,770,000/33,600. It
  is a ratio of two modelled online times, not an observation; r, A and states
  cancel out.
- **2943/289567/28** are the sum, the sum of squares and the 32nd-smallest of
  64 chained xorshift32 draws from seed 20261017.

**Controls fail as declared.** The negative controls give 1855/8 and 185/42
for 284bc4, and 2938/290138/29 and 2879/283745/27 for 283a70; wrong prices
and samplers fail. But the ratio and CON-1/CON-2 checks can fail only through a
code bug: states = 11 still gives 925/4. Neither experiment declares a positive
control. Both points are disclosed (ICV-5).

**Preregistration, receipts, immutability.**
- The v2 specs were frozen in `cb48b111d7`, an ancestor of both raw-output
  commits.
- N equals the plan: 6 of 6 and 3 of 3, with no failures.
- Every hash matches, and every file was written once.
- Approvals re-check `approvable: true`. The lane stayed within its cap of 3.

**Audit replay.** Audit replay (fresh nonce): 67df7d is clean, 3 of 3. 8cdc92
is still flagged 0 of 6, only because `tools/runbook.py:2525` counts pointers
missing on both sides as mismatches. The fix ordered by DEC-20261105-6e2616
NA-1(b) is not on main (ICV-1). The full documents are identical in 27 of 27
replays under CPython 3.11, 3.12 and 3.13.

**Supported status.** H-ICPERF-2f52d1 and H-ICPERF-5adc9b are supported only
as instrument validation.
- The frozen exact-equality rules were committed before the runs, have no
  margin, and are met.
- Every null object fails both rules.
- The decision for 284bc4 is invariant to any assumed n=83 ratio (2x, 235x or
  2000x), so `supported` says nothing about n=83.

**Overclaim search.** No ledger record, report, PDF or knowledge entry asserts
latency, speed, n=83 or an end-to-end gain. One derived export does (ICR-1).
- "No latency effect" and the "measured" labels on 283a70 remain uncorrected
  (ICR-3, ICV-4).
- "Out-of-sample" describes integers computed by running the v1 runner at
  design time (ICR-6).
- The red team's "2.1x faster" is an overclaim (ICR-7).
- A knowledge lead lists both hypotheses under a "measured" clause they do not
  support (ICR-9).

**§5a.**
- "Not applicable" is **correct for 283a70**.
- For 284bc4 the ruling's reason ("no rho arm") is **overclaimed** (ICR-2).
  §5a covers every cross-method ratio, including IC online over BL online.
  Priced at 0, 0.1 and 1 GAE, the order flips inside the band ([0.119, 1.905]
  at the corners). So the result is unresolved, and the decision's "no ranking
  either way" stands.
- No `claims/*.json` is required: nothing claims a speedup or an attack-cost
  gain.

**CORR-20261106-243c4d** only adds files, and its line references are correct.
It and CORR-20261105-1d848a both close NA-1 without citing each other (ICR-4).

### 6. cryptanalysis #1077 n=83 band (readers/cryptanalysis.yaml)

Every band cell, interval and quoted number re-derives digit for digit from the
raw counters under the frozen PROTOCOL.md:

| Arm | 0 GAE | 0.1 GAE | 1 GAE |
| --- | --- | --- | --- |
| S | 0.01138 | 29.00 | 115.5 |
| P | 0.01141 | 43.93 | 175.0 |

- All 62 answers satisfy [k]G = Q in the reader's own GF(2^83) arithmetic.
- IC beats rho only below w* = 0.0029 GAE (S) and 0.0019 GAE (P). The band
  straddles rho, so the comparison is **unresolved, no improvement**.
- **Distance remaining to matched rho at 0.1 GAE: 29x (S), 44x (P)**, as a
  lower bound (CAN-2).
- No byte of the band changed since #1077.

**Rank-finder port: not done.** The field-ops row replaced it on 2026-11-04.
Both rows say "Not computable", and no counted port exists on main or any
branch.

New minor findings:
- CAX-1: baselines.json open[5] and BASELINES.pdf still call the rank-finder
  row current, and the PDF is stale.
- CAX-2: unpriced field ops (7.2e9 for S) are not shown. Charged, they give
  96.4 and 384 for S.
- CAX-3: the claimed second byte-identical run has no artifact.

CAN-1 to CAN-5 are all still not fixed.

### 7. CI and gating (session; checks/ci/merge_timings.yaml)

**Enforcement.** `ledger-and-harness` and `merge-hygiene` are still not
enforced (CIX-1).
- #3065's timeline is consistent with exactly the three required contexts in
  `problems/pr-merge-checks-not-enforced.md`: progress-fidelity, artifacts and
  formal workspace.
- #3058 and #3059 did wait for their checks.
- The ruleset itself could not be read here.

**#2805.** The post-merge validate run checks out trusted base-branch code with
`contents: read`, so the privileged trigger runs no PR code. That part holds.
But:
- It gates nothing.
- Its result lands on the PR head SHA (CIX-2).
- It does not check that `HEAD^2` is the PR head (CIX-3, latent).

**Problem records.** `problems/pr-merge-checks-not-enforced.md` was last
updated 2026-10-28 and is still open. This case opens
`problems/post-merge-checks-mask-pre-merge-state.md`.

**CI1** (workflows disabled) is partially fixed. The gates are active, but 13
workflows remain `disabled_manually`, including `sync-branches`, which AGENTS.md
says runs every six hours.

## Prior findings, current state

All 83 findings of SHF-20261016-3caa6f, SHF-20261017-e4d7f6 and
SHF-20261028-0f3f64 were re-checked against main by the reader that owns each
joint (`findings.yaml: prior_finding_verdicts`). Where two readers disagreed,
the more conservative verdict is shown, except LGN-9: the ledger reader checked
all four sessions, and the PFDR reader agrees.

| Verdict | Count | Findings |
| --- | --- | --- |
| fixed | 62 | all others |
| partially_fixed | 15 | V1, S2N-1, S2N-6, S2N-9, S2N-10, M2, M2-R, LGN-2, LGN-8, K2, K-N1, L-N7, PPN-3, PPN-6, CI1 |
| not_fixed | 6 | CAN-1, CAN-2, CAN-3, CAN-4, CAN-5, SES-1 |

## Independence

- **Who ran it.** This case was run in session `01TCbLH84PotMkHyFGFE4ifE`. No
  commit on any audited main carries that id.
- **Who commissioned it.** Session `016SURwTvgaQmnMnhpa1SLXQ` commissioned it,
  and also asked that the commits carry its `Claude-Session` trailer and that
  it merge the PR. That session authored 91 commits on main, among them:
  - the ICPERF v2 approvals and lane;
  - the ICPERF evidence review (#3044), CORR-20261106-243c4d and #3059;
  - the PFDR review EV-PFDR-07d608, DEC-20261029-01405d, KN-FIND-c81e5b and
    CORR-20261029-1aaef6.
- **What this means.** The skill's refusal condition (this session produced
  the result) is not met. But the party that commissions and merges this audit
  produced much of what it audits (SES-INDEP).
- **Trailers.** Commits from 2026-11-06 add an `Audit-Session` trailer.
- **Readers.** All eight are fresh subagent contexts, blind to `prior.md`,
  `sweep.md` and each other. Two disclosed partial exposures:
  - the stark reader read the prior case's `readers/stark.yaml` as its format
    model;
  - several readers saw sibling file names in `git status`.

## Not covered, and what would cover it

| Item | Command or condition |
| --- | --- |
| zk tests and Rust mutants | `cargo test --release --lib zk::` and the mutants of ZKX-1/2/3, in isogeny-labs/crypto. A harness loading `scripts/readers/stark/plonk_model.json` covers ZKX-3 against the real `verify`. |
| Full formal workspace and AxiomAudit | `cd formal && lake build && lake env lean AxiomAudit.lean`, on a host with more than 15 GB RAM; then `python3 tools/verify_formal_targets.py` |
| Crypto and cryptanalysis Lean projects | `tools/lean/proof-gate.sh`, `tools/lean/selftest/run.sh` (external code) |
| ecbench verify, bounds, challenges; fb-archive verify, refs check | the sibling checkers of `tools/sheriff.py sweep --deep` with the siblings attached |
| Paper builds | `make -C papers/<paper> check` |
| `analyze_v2.py` and the store-only bytes | in the cryptanalysis checkout; `tools/artifacts/artifacts.py pull` |
| Main ruleset contents | `gh api repos/isogeny-labs/crypto-autoresearcher/rulesets` |
| ca5e01 full replay | stopped at 30 min; its 34 completed jobs were identical |
| Outside-sparse roots, and info-level strong-word and number leads | full checkouts; lead-by-lead reading |

## What this case does not establish

- **No execution verification.** Nothing here is execution verified: the
  execution-proof milestones remain open. Replays and hashes bound
  fabrication; they prove nothing about execution.
- **Reading, not running.** zk soundness verdicts rest on code reading and
  independent models, not on the producer's tests. The cryptanalysis and PFDR
  verdicts rest on independent re-implementation and nonce-sampled replays.
- **Lean.** A Lean build proves the Lean statement under its axioms. The formal
  lane's `semantic_review` for TranslationDescent stays pending.
- **CI.** The merge-timing observations cover the PRs read (#3056, #3058,
  #3059, #3065), not every merge. A clean PR does not show enforcement.
- **Bounded searches.** A bounded strong-word or number scan proves no absence.
