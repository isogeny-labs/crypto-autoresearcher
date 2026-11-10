# J3 hosted named machine evidence and controls

Task: `TASK-20261109-0c1322` (Conductor T-2007)  
Joint: J3 only  
Verdict: **holds**, for the existing hosted machine evidence at the exact named target and inputs. This is not a semantic-fidelity or serialized-record verdict.

## Authenticated run and artifact

- The pinned plan at `docs/reports/2026-11-09-semaev-raw-coordinate-fidelity/review-plan.yaml` hashes to `0cbbc5e36a720afa830e67211da86062bbf62fc501b8da31e13e79e96e7fc16a`.
- GitHub Actions [run 42666660822](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42666660822) is a completed, successful `lean-verification` pull-request run, attempt 1, with reported head `6670f72b65a405206702abc394efb2b0f0e82394`. Its successful formal-workspace job is `129332146057`; successful kernel-controls job is `129332146078`.
- The checkout log shows Actions fetched and checked out PR 3209 merge commit `6c84716cd2fae8a022482faf0727969a8d61e1dc`, with parents `36ee18fa3d0e6d527e1b36e3e2a09180c5fcf055` and the reported head `6670f72b65a405206702abc394efb2b0f0e82394`. The receipt's `source_commit` and both dependency-pin records name this actual checkout commit. This resolves the apparent head/receipt SHA difference.
- GitHub artifact metadata binds `formal-verification-receipts` ID `13699530877` to that run and head. The privately downloaded ZIP is 1,923,813 bytes and hashes to GitHub's published `sha256:5759faf4faf1d2bd295cfe95e7f9674cce512be48546ed0bb84f74c56f337b01`. It contains the exact `semaev-raw-coordinate-certificate.json` receipt. The job log records upload and finalization of that same artifact ID.

## Exact named verification

The named receipt states `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, no forbidden constructs, no infrastructure failure, and pending semantic review. Its task ID is `TASK-20260916-b55948`, claim ID is `THM-SEMAEV-FALL1-LEMMA-3-RAW-COORDINATES`, and its theorem name/file are `CryptoResearch.Semaev.validRawDecomposition_iff_curve_span_sum` and `CryptoResearch/Semaev/Certificate.lean`.

The build log ends with successful workspace build (`9147 jobs`) and explicit target-module build (`2059 jobs`). The project audit reports 1,313 theorems with only allowed standard axioms. The separate target audit prints the exact elaborated declaration and `#print axioms`; its dependency list is `propext`, `Classical.choice`, `Quot.sound`. The target-audit implementation requires `.thmInfo`, invokes `Lean.collectAxioms`, rejects anything outside those three names, and only then emits `target axiom audit passed: CryptoResearch.Semaev.validRawDecomposition_iff_curve_span_sum`. The generated root imports `CryptoResearch.Semaev.Certificate`; the gate also explicitly builds that module. The hosted gate reports 126 verified targets, zero not verified, zero infrastructure failures and zero undischarged targets; J3's claim is limited to the named target.

## Input and pin closure

`artifact/closure-check.json` compares the receipt with the GitHub checkout merge tree and requested head tree. The plan's claim-source, target, theorem, Lean toolchain and Lake-manifest SHA-256 values all match both trees and the named receipt. The toolchain is `leanprover/lean4:v4.35.0`; the hosted log reports Lean 4.35.0. The receipt's complete local-source snapshot matches all 106 relevant formal files in the merge tree, including the deterministic generated root. Its direct-verifier snapshot matches all 10 `orchestration/formal/*.py` files. There are no missing, extra or mismatched entries. The target YAML is independently bound by its `task_spec_sha256`; the research source is independently bound by `declared_source_sha256`.

The outer CI workflow, gate script, root generator and dependency-pin checker are not entries in the direct verifier map. I inspected their bytes from the same merge tree and bound their execution by the hosted checkout and job log. The dependency checker byte hash is `0bcb377242cede9cdbf393e966022adb6303ac8c2b9b64a93a3c37d123f301b7`, matching the before/after records. Both records report the same pinned manifest hash, ten expected installed Git revisions, clean dependency sources and `passed: true`. They explicitly state `binary_or_independent_kernel_recheck: false`; dependency binaries and Lean/Lake remain the ordinary compiler trust boundary.

## False-success controls and authentication boundary

The same hosted run's `lean-controls` artifact ID `13696168701` matches its published ZIP digest `e91be2ceb4b1bfc632841ade216b82fc52abf1a6f170090e3333ebbc475c41fa`. Its JUnit record has 455 tests, zero failures, zero errors and zero skips. Specific passing live-Lean controls reject a false theorem, absent declaration, non-theorem definition and a hidden `sorryAx` dependency. Other passing controls cover named target auditing, changed imported inputs, stale helpers, altered receipt fields, wrong named audit, failed audit diagnostics and wrong/dirty dependency pins.

I additionally used the pinned receipt-consistency implementation on a private snapshot of the checkout. The unmodified named receipt passed. Six focused mutations were rejected: wrong declaration, wrong named-audit line, an added axiom-failure diagnostic, stale workspace hash, stale verifier hash and empty build log. A seventh mutation replacing both build and audit logs with plausible invented success strings passed consistency (`artifact/mutation-check.json`). This is expected: receipt validation checks JSON against current inputs but cannot prove that Lean ran. For this target, execution evidence comes from the authenticated GitHub job, its step outcomes, checkout log and published artifact digest together, with the receipt giving detailed named Lean output. None of these alone authenticates a producer's serialized certificate or an experiment result.

## Scope and limits

No new Lean build, EKS job or cloud experiment was launched. I did not read J1/J2 reports or outputs, edit the repository, or perform an independent kernel/binary recheck. J3 supports the existing hosted named machine verification and the described controls at the merge tree above. J1 owns algebraic counterexamples; J2 owns source-to-Lean fidelity and the B1–B6 serialized-record boundary. Composition and any official status change belong to the Coordinator after independent reports are sealed.
