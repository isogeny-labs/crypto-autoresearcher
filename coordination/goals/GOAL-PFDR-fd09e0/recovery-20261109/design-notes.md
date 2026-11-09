# PFDR prospective recovery design — 2026-11-09

This is a draft preparation record, not an approval, dispatch, scientific review or new result. The corresponding proposal is `experiments/EXP-PFDR-ada71b/amendments/recovery-20261109.proposal.json`. It preserves the original question, acceptance criteria and failed attempt.

## Evidence and sources checked

At base `dadfb1b2a5b6e8e6045f8547d26ec2b40d4ff81a`, read the original specification, trial plan, protocol, driver/checker, approval `DEC-20261101-cb3277`, both run receipts and the pilot launch/manifest. These are internal retrieved sources, not recalled scientific citations. This recovery changes custody metadata only; no new mathematical assertion or novelty claim is made. Scientific literature review must remain the original frozen protocol's review, and its exact relevant references must be read before a new scientific launch.

`git show` establishes that claim commit `715df5e6018a7e85b7849d708df9372ed1fa7838` is the immediate parent of `a8a4f7b0854c6a013670761a1d078552cd7b47bb`, which archives only the preceding selftest's eleven result files. No driver or scientific input changed in that diff. The pilot's launch authority retained the former hash while the driver emitted the latter from live HEAD after completing work. `tools/experiment_execution.py` requires the launch-authority identity in `run.code.commit`. This explains the invalid-output failure without assigning mathematical meaning to it.

`git log --all -- experiments/EXP-PFDR-ada71b` showed only original design, approval, selftest, failed pilot, report and artifact-storage changes. No recovery amendment was found; the tracked amendments directory contained only `.gitkeep`. This inspection covers fetched refs, not undiscovered unpushed work. Live lane/claim reconciliation remains necessary before dispatch.

## Smallest implementation and tests

Add a versioned driver copy, preserving the frozen original driver/checker. Candidate: `experiments/EXP-PFDR-ada71b/implementation/run_recovery_20261109.py` (SHA-256 `979ad0912bb6a9e67a3976ad4a8b11879dffac3e4c5ffd5b18b54120498da3b1`). Parent reports four passing focused regression tests and zero scientific runs; this worker did not rerun them. Before invoking any scientific computation, validate the run directory's `launch.json`: run ID, trial ID, plan hash and a nonempty correctly shaped authority commit must agree with this invocation. Use that launch commit for manifest `run.code.commit`; record observed HEAD separately, including disagreement, rather than falsifying source provenance. Preserve driver's scientific functions, constants, inputs and checker behavior.

Test the actual former failure: launch at commit A, archive unrelated prior output to commit B, then emit a manifest whose authority remains A and whose observed HEAD is B. The supervisor envelope must accept the correctly bound manifest. Also test absent/malformed launch metadata, mismatched plan hash, run ID and trial ID; each must fail before scientific code runs. These are correctness tests, not research trials.

The new five-trial plan omits selftest as a trial. Including it with its old run ID fails `trial_state`, since its receipt is bound to the old plan hash. Reuse its immutable `selftest.json` as a hash-bound input with its original validated receipt; explicitly verify that evidence before admission. New pilot has no intra-plan predecessor, then the original five-stage dependency chain continues. All five run IDs must be freshly allocated and checked. The old invalid pilot's design must not supply new census inputs.

## Bounded attempt accounting

Two of six original allowed attempts are consumed: one valid selftest and one invalid pilot. Four remain. A new pilot plus the four downstream stages requires five attempts. Full recovery therefore requires a prospective amendment authorizing exactly seven total attempts (two historical plus five new), including exactly one additional pilot attempt and no further retries. Calling the invalid pilot free or silently omitting the final analysis would misstate the original task.

Keep four workers, 4 GiB and one trial at a time. Original stage watchdogs sum to 108,000 seconds for the five proposed trials, at most 120 CPU-hours at four workers; this is a conservative protection ceiling, not a measured runtime or forecast. Use the existing host only; this draft authorizes no cloud instance, paid inference or cloud build. Checkpoint, host resources and ownership must pass before any attempt.

## Approval and execution route

Create an additive versioned specification directly under the experiment directory, such as `specification-recovery-20261109.yaml`: supervisor requires its parent directory name to equal the experiment ID. Bind a new frozen protocol and plan, a new executor handoff/queue, all source and input hashes, and full archive coverage. Do not overwrite original specification, protocol, plan, driver or run records. The new approval must name the original contract and the exact bounded change.

Before approval, exact prospective bytes must pass `experiment_preapproval.py`; after archive/publication, named selector readiness, ownership and checkpoint gates remain binding. Need a mechanical runbook/director task card if required by the current design workflow. A ready preparation record alone does not grant execution authority.

Native Coordinator provenance must be explicit. The default adapter resolves an Anthropic model, which was not this subagent's runtime. Existing `openai-gpt6` and `openai-gpt61` mappings offer Coordinator bindings for `gpt-6-sol` and `gpt-6.1-sol` at high effort. Select the one matching the actual session and verify its provenance; do not pretend an unknown inherited model matches either. No official decision or status transition was issued here.

Next action: implement and test the versioned custody wrapper, then assemble the exact prospective recovery packet and resolve Coordinator runtime identity. A linked problem record/index entry is required by AGENTS before handoff of this recurring defect; root session owns those paths outside this worker's scope.

Parent subsequently read its actual native session metadata as `gpt-6-astra`, medium effort. That inherited session is not the configured Coordinator binding. The planned approval session is a fresh `gpt-6-sol`/high Coordinator using the existing `openai-gpt6` mapping; this draft remains unapproved.
