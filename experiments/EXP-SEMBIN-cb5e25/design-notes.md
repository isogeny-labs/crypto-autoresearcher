# EXP-SEMBIN-cb5e25: design notes, order of operations and shell commands

Status: DRAFT instructions from the Coordinator (no shell) under DEC-20261106-36e212.
Nothing here approves anything. EXP-SEMBIN-cb5e25 is `review_required`, H-SEMBIN-e5b2db is
`specified`, DEC-20261106-e7576f (approval) is reserved and unwritten, and DEC-20261106-c897df
is reserved and unwritten. Rulings referred to as RUL-n are in DEC-20261106-36e212.

Branch: `claude/sembin-true-dF-search`. All paths are repo-relative. Run from the repo root.

## 0. Identifiers

| Id | Role |
| --- | --- |
| BATCH-501c2f | the new lane |
| TASK-20261106-9da2e3 | executor task (runbook session) |
| TASK-20261106-c5d001 | run snapshot archive (the executor's `archived_by`), runs alone after the session |
| DEC-20261106-36e212 | this design and lane ruling |
| DEC-20261106-e7576f | approval, NOT written yet |
| DEC-20261106-c897df | reserved, stays unwritten |
| `$DA` | design archive task id, to be allocated in step 0.5 (kind ledger, carries the lane files, the goal-head edit, the design artifacts) |
| `$AA` | approval archive task id, to be allocated in step 0.5 |
| RBS-SEMBIN-19ce78 | runbook session id as drafted by the director; keep unless a journal for it already exists on any ref |
| RUN-SEMBIN-d1204f | the one shared run directory every trial of pass 1 appends to |
| `$PH` | frozen protocol hash, `freeze.protocol_sha256` of protocol.json, known after step 3 |
| `$S_R` / `$S_A` | sha256 of the review_required specification bytes / of the approved-bytes preview, known after step 4 |

## 1. STOP conditions (any one ends the design; report, do not improvise)

- A lane listing across all refs shows a third open SEMBIN lane (step 0.2). RUL-1 then does not hold.
- A live claim on BATCH-e0a0c1's queue (step 0.3).
- `git merge origin/main` conflicts. Never resolve by editing a record; stop and create a superseding record.
- The optional RLIMIT confirmation (step 2.4), if run, shows a kill inside the closure child recorded as an invalid
  trial rather than a row with status error and a check_trial warning.
- Any edit of an earlier item in step 2 to 7 after a later one has been hashed: redo everything after it.
- The observation-collision search finds a replication, an existing counterexample or a corroboration that
  reframes the contract (RUL-12 gate 1): the experiment returns to design.

## 2. Order of operations

### Step 0. Preflight (writes nothing except the two id tokens)

0.1 `git fetch origin && git merge origin/main` (merge, never rebase). `git status --short` shows only the
    Coordinator drafts of this task: DEC-20261106-36e212, TASK-20261106-9da2e3 (untracked, see 8.3),
    BATCH-501c2f.yaml, this file, and the director's draft files.
0.2 `python3 tools/goal_lanes.py lanes GOAL-SEMBIN-fcb7a2`   (all refs; expect cbb416 open, e0a0c1 open, nothing else)
0.3 `python3 tools/goal_lanes.py claims coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/dispatch_queue.json`
    (expect no live claim) and the same for `.../BATCH-cbb416/dispatch_queue.json` (informational, RUL-2).
0.4 `python3 tools/allocate_id.py --check BATCH-501c2f`  (expect free)
0.5 `python3 tools/allocate_id.py --next handoff --date 20261106`  twice; `--check` each. Call them `$DA` and `$AA`.
    Replace the token in the decision (still uncommitted):
    `sed -i 's/ALLOCATE-DESIGN-ARCHIVE-TASK-ID/'"$DA"'/' ledger/decisions/DEC-20261106-36e212.yaml`
    BATCH-501c2f.yaml is write-once and reads "pending allocation" for the design archive; it is not edited.
    The archive receipt of `$DA` names the id.

### Step 1. Lane (RUL-1)

1.1 Record the late closure of BATCH-e0a0c1 (no --publish; the design archive commits it):
```
python3 tools/goal_lanes.py close-lane GOAL-SEMBIN-fcb7a2 BATCH-e0a0c1 \
  --as coordinator-sembin-501c2f \
  --outcome "archived; late-recorded under DEC-20261106-36e212" \
  --decision DEC-20260916-87fc5c \
  --ledger-commit 80242e204f9c393ec4353ad9dde5409c930c1665
```
1.2 Open the new lane:
```
python3 tools/goal_lanes.py open-lane GOAL-SEMBIN-fcb7a2 BATCH-501c2f \
  --queue coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json \
  --decision DEC-20261106-36e212 \
  --objective "Pass 1 of EXP-SEMBIN-cb5e25 (H-SEMBIN-e5b2db): a counterexample search against the degree-4 mutant closure of coset-shifted EQS4 systems (Nagao 2015/984 binary chain), through one runbook session, then its run archive. Pass 2 (SR-6, SR-7, raised certificate guard) is added by a later additive queue revision under its own approval. Observations only; it cannot refute Proposition 5 by itself and moves no status." \
  --as coordinator-sembin-501c2f --branch claude/sembin-true-dF-search
```
1.3 `python3 tools/goal_lanes.py lanes GOAL-SEMBIN-fcb7a2 --local-only`  must show e0a0c1 closed, cbb416 open,
    501c2f open: 2 open, equal to the cap of 2.

### Step 2. Code clean (before any hash that covers it)

2.1 `python3 -m pytest experiments/EXP-SEMBIN-cb5e25/code/tests -q`  (expect the 76 tests to pass)
    `python3 -m pytest experiments/EXP-SEMBIN-cb5e25/review/checker -q`
2.2 If any file under `experiments/EXP-SEMBIN-cb5e25/code/` changed: commit the code first, then regenerate:
    `python3 experiments/EXP-SEMBIN-cb5e25/code/provenance.py` then commit `code/CODE_SHA256.json`.
2.3 `python3 experiments/EXP-SEMBIN-cb5e25/code/provenance.py --check`  must exit 0 on a clean tree
    (`git status --short experiments/EXP-SEMBIN-cb5e25/code` empty, `__pycache__` not staged).
2.4 OPTIONAL confirmation of RUL-3(a), scratch directory outside the repo, nothing kept as an observation. The
    Coordinator read the code paths but ran nothing. Try descending virtual ceilings (kB) on the trivial cell m3n03 until
    the closure child, not interpreter start-up, hits the limit; a fixtures.json stub is needed because check_trial
    requires one in the shared directory:
```
for V in 3000000 2000000 1500000 1000000; do
  S=$(mktemp -d); mkdir -p $S/r $S/shared
  echo '{"sr1_all_pass": true, "fixtures": []}' > $S/shared/fixtures.json
  ( ulimit -v $V; python3 experiments/EXP-SEMBIN-cb5e25/code/adapter.py --run-dir $S/r --shared-run-dir $S/shared \
    --kind trial --cell m3n03 --arm EQS4 --r 0 --protocol-sha256 $(printf '0%.0s' $(seq 64)) ); echo "V=$V exit=$?"
  python3 experiments/EXP-SEMBIN-cb5e25/code/check_trial.py $S/r --shared-run-dir $S/shared
done
```
    Expected where the child is killed by the ceiling: a trial record with a row `status: error` and `M1.contained: failed`,
    adapter exit 0, check_trial `"valid": true` with a warning. Report what each V shows. A run that dies before any record
    (interpreter or import failure) says nothing about the child path and is not a failure of the ruling.

### Step 3. Protocol edit and freeze (RUL-8, RUL-11)

3.1 Coordinator edits `experiments/EXP-SEMBIN-cb5e25/protocol.json` (it is a draft: `freeze.status` draft):
    a. `analysis_plan.script.sha256` = `sha256sum experiments/EXP-SEMBIN-cb5e25/code/analyze.py`
       (path stays as it is; if `validate` cannot resolve it relative to the protocol directory, the runbook
       bind of analyze.py still carries the hash, and the freeze lint only checks it when the file resolves).
    b. `analysis_plan.frozen_before_data` = `true`.
    c. `execution.placement.memory_enforcement` =
       `"resident-set watchdog (VmRSS, 10 GiB) in code/run.py is the binding memory limit; the supervisor's mandatory RLIMIT_AS is a loose 32768 MB virtual ceiling that is not a resource cap, and a kill at it is an infrastructure failure under SR-7 (DEC-20261106-36e212 RUL-3)"`
       Leave `execution.placement.memory_mb` at 10240 and `execution.timeout_seconds` at 43200.
3.2 `python3 tools/experiment_protocol.py validate experiments/EXP-SEMBIN-cb5e25/protocol.json`  (no findings)
3.3 Commit the pre-freeze edit, then freeze (`--commit auto` records HEAD):
```
git add experiments/EXP-SEMBIN-cb5e25/protocol.json && git commit -m "protocol: pre-freeze edit for EXP-SEMBIN-cb5e25"
python3 tools/experiment_protocol.py freeze experiments/EXP-SEMBIN-cb5e25/protocol.json --commit auto --filed-before-affected-data
python3 tools/experiment_protocol.py validate experiments/EXP-SEMBIN-cb5e25/protocol.json
```
3.4 `PH=$(python3 -c "import json;print(json.load(open('experiments/EXP-SEMBIN-cb5e25/protocol.json'))['freeze']['protocol_sha256'])")`
    `PF=$(sha256sum experiments/EXP-SEMBIN-cb5e25/protocol.json | cut -d' ' -f1)`   (the FILE hash: plan input_sha256, runbook bind)
    Never edit protocol.json again. The old placeholder bb174a51b5d9... is void.

### Step 4. Specification revision, once (Coordinator edit), then the approved-bytes preview

4.1 Edit `experiments/EXP-SEMBIN-cb5e25/specification.yaml` (still review_required, frozen false):
    - `design_revision`: add revision 3 with DR-11, DR-12 and DR-13 (text in section 5).
    - `budget.memory_enforcement`: append the DR-11 sentence (section 5).
    - `execution_plan.protocol_hashes`: `{experiments/EXP-SEMBIN-cb5e25/protocol.json: <PH>}` (the canonical hash,
      the form EXP-PFDR-ada71b uses).
    - `execution_plan.trial_plan`: `experiments/EXP-SEMBIN-cb5e25/trial-plan.json`; `execution_plan.runbook`:
      `experiments/EXP-SEMBIN-cb5e25/runbook.yaml`; rewrite `execution_plan.reason`; update `readiness.blockers` to what
      remains (collision search, probe, approval decision, resume checkpoint). Do not touch status, frozen,
      approved_by, execution_authorized.
    - Do NOT change `parameter_grid`, criteria, controls, budget numbers or stopping rules.
4.2 `S_R=$(sha256sum experiments/EXP-SEMBIN-cb5e25/specification.yaml | cut -d' ' -f1)`; commit the edit.
4.3 Build the approved-bytes preview (a byte copy of the file with exactly four lines changed):
```
D=coordination/design/$DA/EXP-SEMBIN-cb5e25; mkdir -p $D
python3 - <<'PY'
import pathlib
src = pathlib.Path('experiments/EXP-SEMBIN-cb5e25/specification.yaml').read_text()
for a, b in [("\n  status: review_required\n", "\n  status: approved\n"),
             ("\n  frozen: false\n", "\n  frozen: true\n"),
             ("\n  approved_by: null\n", "\n  approved_by: DEC-20261106-e7576f\n"),
             ("\n  execution_authorized: false\n", "\n  execution_authorized: true\n")]:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
pathlib.Path(__import__('os').environ['D'] + '/specification.preview.yaml').write_text(src)
PY
S_A=$(sha256sum $D/specification.preview.yaml | cut -d' ' -f1)
```
    (`export D` before the heredoc. The assert fails if any of the four lines is not unique at two-space indent.)

### Step 5. Collision search (RUL-12 gate 1; runs in parallel with 2 to 4, gates step 11)

    Use the `research-kb` skill and the greps named in the specification's `observation_collision_search`.
    Commit the record at `experiments/EXP-SEMBIN-cb5e25/collision-search.json` (queries, hits, who read it, date).
    It is a bound input of the runbook (step 6) and is copied into the run directory by a runbook step.

### Step 6. Plan and runbook regeneration (experiment-director, compile mode)

6.1 Dispatch `experiment-director` (compile) with the values in section 6 below. It regenerates
    `experiments/EXP-SEMBIN-cb5e25/trial-plan.json`, `runbook.yaml` and `task-cards/CARD-EXP-SEMBIN-cb5e25-01.yaml`
    and must COMMIT its generator beside the design artifacts
    (`$D/build_plan_and_runbook.py`); the draft came from an uncommitted scratchpad script.
6.2 `python3 tools/runbook.py lint experiments/EXP-SEMBIN-cb5e25/runbook.yaml | tee experiments/EXP-SEMBIN-cb5e25/runbook-lint.txt`
    Require the last line `LINT OK ... sha256 <R_PRE>`. A finding goes back to the director.
6.3 `T=$(sha256sum experiments/EXP-SEMBIN-cb5e25/trial-plan.json | cut -d' ' -f1)`;
    `python3 -c "import json;print(len(json.load(open('experiments/EXP-SEMBIN-cb5e25/trial-plan.json'))['trials']))"`
    must equal the handoff template's `budget.maximum_runs` (587 expected). If it differs, edit that one number in the
    uncommitted template before step 8.

### Step 7. Commit the code, protocol, specification, plan, runbook (still not approved)

    `git add` by exact path: protocol.json, specification.yaml, trial-plan.json, runbook.yaml, runbook-lint.txt,
    collision-search.json, task-cards/, code/CODE_SHA256.json (if changed), $D/build_plan_and_runbook.py,
    $D/specification.preview.yaml. `git commit`. Then `git push -u origin claude/sembin-true-dF-search`.
    The probe needs these bytes at `source_ref`.

### Step 8. Queue, handoff preview, packet

8.1 Save the builder in section 7 as
    `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/build_queue.py` and run:
    `python3 coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/build_queue.py --design-dir $D`
    It writes `dispatch_queue.json` and `$D/handoff.preview.yaml` (tokens spliced from the final plan).
8.2 `python3 tools/research_dispatch.py coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json --ready-only`
    must validate the queue (it calls validate_queue, the same check the probe runs). A refusal goes back to step 6 or 8.
    (Embedded task `handoff` blocks are validated against inputs that may need to be committed; run it again after the
    step 7 push if it names an uncommitted input.)
8.3 The ledger copy `ledger/handoffs/TASK-20261106-9da2e3.yaml` stays UNTRACKED in the design archive (it is a
    template with two tokens, and a handoff record of an unapproved task is not committed). At approval it is
    replaced by a byte copy of `$D/handoff.preview.yaml`, the bytes the probe hashed.
8.4 Write the packet `$D/packet.json`:
```
{"approval_decision_id": "DEC-20261106-e7576f",
 "execution_route": {"kind": "runbook", "lint_receipt": "experiments/EXP-SEMBIN-cb5e25/runbook-lint.txt",
                     "lint_receipt_sha256": "<sha256 of runbook-lint.txt>"},
 "experiment_id": "EXP-SEMBIN-cb5e25",
 "handoff": "ledger/handoffs/TASK-20261106-9da2e3.yaml",
 "lane_id": "BATCH-501c2f",
 "preview": {"handoff": "coordination/design/<DA>/EXP-SEMBIN-cb5e25/handoff.preview.yaml",
             "queue": "coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json",
             "specification": "coordination/design/<DA>/EXP-SEMBIN-cb5e25/specification.preview.yaml",
             "trial_plan": "experiments/EXP-SEMBIN-cb5e25/trial-plan.json"},
 "queue": "coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json",
 "schema": "crypto.autoresearch.preapproval_packet.v1",
 "source_ref": "origin/main",
 "specification": "experiments/EXP-SEMBIN-cb5e25/specification.yaml",
 "trial_plan": "experiments/EXP-SEMBIN-cb5e25/trial-plan.json"}
```

### Step 9. Goal head and design archive (kind ledger, runs alone), PR A

9.1 Goal-head edit (additive, inside the design archive only), `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`:
    - `open_batches`: for the BATCH-e0a0c1 entry change `status: open` to `status: closed` and add
      `closed_at: '2026-09-21'`, `closed_by_record: coordination/goals/GOAL-SEMBIN-fcb7a2/lanes/BATCH-e0a0c1.closed.json`,
      `closed_note: "Recorded late under DEC-20261106-36e212 (defect ND-1 of TASK-20260916-d4fb62)."`.
      Append an entry: `id: BATCH-501c2f, opened_at '2026-11-06', opening_decision_id DEC-20261106-36e212, status open,
      checkpoint ledger/goals/GOAL-SEMBIN-fcb7a2/checkpoints/BATCH-501c2f.yaml, dispatch_queue
      coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json, experiment_id EXP-SEMBIN-cb5e25,
      hypothesis_id H-SEMBIN-e5b2db, max_concurrent 1, added_by_lane BATCH-501c2f, what: <one sentence>`.
    - `next_action`: prefix one paragraph "AMENDED ADDITIVELY 2026-11-06 UNDER DEC-20261106-36e212 ..." stating that
      BATCH-501c2f carries the design and pass 1 of EXP-SEMBIN-cb5e25, that BATCH-cbb416 still holds the operative
      next action and `current_batch_id`, and that nothing is approved. Keep every earlier paragraph verbatim.
    - `amendment_history`: prepend one entry; `updated_at` 2026-11-06, `updated_by` DEC-20261106-36e212.
    - `campaign_budget` is NOT edited. `max_concurrent` stays 2.
9.2 Validate: `python3 tools/validate_ledger.py`; `python3 tools/ecc_priority.py --classify GOAL-SEMBIN-fcb7a2`;
    `python3 tools/ecc_priority.py --budget-violations`; the design-rate guard of
    `orchestration/research-priority.yaml`. No new error on any staged path.
9.3 Stage by exact path (nothing else), one commit, the archive receipt for `$DA`:
    - `ledger/decisions/DEC-20261106-36e212.yaml`
    - `ledger/goals/GOAL-SEMBIN-fcb7a2/checkpoints/BATCH-501c2f.yaml`
    - `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`
    - `coordination/goals/GOAL-SEMBIN-fcb7a2/lanes/BATCH-501c2f.lane.json`
    - `coordination/goals/GOAL-SEMBIN-fcb7a2/lanes/BATCH-e0a0c1.closed.json`
    - `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json`
    - `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/build_queue.py`
    - `experiments/EXP-SEMBIN-cb5e25/design-notes.md`
    - everything under `$D` except `preapproval-report.json` (not yet produced)
    - the step 7 files if they were not committed there
    - the archive receipt `coordination/design/$DA/ledger-receipt.json`
9.4 `git push -u origin claude/sembin-true-dF-search`. Open or refresh the PR against `main` titled
    `experiment: EXP-SEMBIN-cb5e25 design archive (lane, rulings, plan)` naming BATCH-501c2f, DEC-20261106-36e212,
    TASK-20261106-9da2e3, TASK-20261106-c5d001 and `$DA`; then `gh pr merge <n> --auto --merge`
    (only where `gh auth status` succeeds; otherwise report the pushed branch and stop).

### Step 10. Probe at origin/main (after PR A merges)

10.1 `git fetch origin && git merge origin/main`.
10.2 `python3 tools/experiment_preapproval.py --packet $D/packet.json | tee $D/preapproval-report.json`
     Require `approvable: true`, `blockers: []`. Any blocker: the experiment stays review_required, record the exact
     blockers in a new BATCH-501c2f checkpoint file (write-once), and stop. (A diagnostic run with
     `"source_ref": "origin/claude/sembin-true-dF-search"` before the merge is allowed; it is not the gate.)

### Step 11. Approval decision (Coordinator, new task) and approval archive `$AA`, PR B

11.1 Gates: probe approvable true; collision search read and clear (step 5); resume checkpoint filled and pushed
     (`scripts/checkpoint.sh init`, CLAUDE.md); the dispatch preconditions of section 9 understood.
11.2 On a scratch copy compute the approval-time bytes: apply `$D/specification.preview.yaml` as
     `experiments/EXP-SEMBIN-cb5e25/specification.yaml`; set the runbook bind of that file from `$S_R` to `$S_A`;
     `python3 tools/runbook.py lint` -> new `runbook_sha256` `$R_A`; regenerate the card with `$R_A`.
11.3 Coordinator writes `ledger/decisions/DEC-20261106-e7576f.yaml` on the DEC-20261029-ca33b3 model: decision approve,
     `runbook_sha256: $R_A`, `runbook_path`, `runbook_session_id: RBS-SEMBIN-19ce78`, the probe report path and
     source_ref, `approved_bytes` for specification ($S_A), trial plan ($T), runbook ($R_A), implementation hashes,
     handoff, queue, `status_transitions` (EXP-SEMBIN-cb5e25 review_required to approved; H-SEMBIN-e5b2db specified to
     approved), `dispatch.gate` as in DEC-20261106-36e212, `opened_tasks [$AA]`.
11.4 Approval archive `$AA` stages by exact path: the decision; `specification.yaml` (byte copy of the preview);
     `runbook.yaml`, `runbook-lint.txt`, the card; `ledger/handoffs/TASK-20261106-9da2e3.yaml` (byte copy of
     `$D/handoff.preview.yaml`); `ledger/hypotheses/H-SEMBIN-e5b2db.yaml` (status approved with a status_note); the
     preapproval report moved to `coordination/design/$AA/EXP-SEMBIN-cb5e25/preapproval-report.json`; the
     queue unchanged. Verify every sha256 equals the decision's approved_bytes; if any differs, the archive stops and
     nothing takes effect.
11.5 After the commit: `python3 tools/runbook.py lint experiments/EXP-SEMBIN-cb5e25/runbook.yaml` prints `LINT OK`
     with `$R_A`; `python3 tools/task_card.py lint experiments/EXP-SEMBIN-cb5e25/task-cards/CARD-EXP-SEMBIN-cb5e25-01.yaml`
     prints `CARD OK`. Push, open PR B, `gh pr merge <n> --auto --merge`.

### Step 12. Readiness

     After PR B merges: `python3 tools/newest_experiments.py --experiment EXP-SEMBIN-cb5e25 --json` reports
     `execution_state: ready`. A mismatch stops dispatch and needs an additive correction.

### Step 13. Session receipt

     `python3 tools/session_receipt.py --skill design-experiment --role coordinator --outcome <approved|review_required> --created EXP-SEMBIN-cb5e25,H-SEMBIN-e5b2db,TASK-20261106-9da2e3`

## 3. What each archive may contain (one archival task per card)

- `$DA` (ledger kind, alone): design records and lane files, no run.
- `$AA` (ledger kind, alone): the approval and the byte swaps.
- `TASK-20261106-c5d001` (snapshot kind, alone, before any independent review): the pass-1 session and run
  records, its `read_scope` covers `experiments/EXP-SEMBIN-cb5e25/runs`, `runbook-sessions` and `reports`; its
  `snapshot.json` enumerates every committed file of the shared run directory at archive time (stored forms per
  tools/artifact_store.py). A later ledger archive after review carries the evidence decision.

## 4. Rulings in one place (full text in DEC-20261106-36e212)

| Item | Ruling |
| --- | --- |
| Lane | close BATCH-e0a0c1 by its own record (late), open BATCH-501c2f; 2 open = cap 2; cap not raised |
| I-4 memory | trial memory_mb 32768 (RLIMIT_AS virtual), handoff memory_gb 32, real cap = run.py VmRSS 10 GiB; declared deviation |
| A-3 | on_invalid stop kept; undecided PC-TRI is a warning and the C-PC gate does not hold |
| I-7 | replay exempt accepted for pass 1; no contained-side evidence decision before an archived nonce-sampled scratch replay |
| A-4 | S03 3600 s, S05 43200 s (claim ttl 750 min), S06 1800 s, others 60 s or 120 s; handoff wall 50400 s; SR-8 clock starts at the first trial |
| A-1 | certify cells m3n12, m3n13, m3n14, m4n08, m4n09 |
| A-2 | the real frozen protocol hash everywhere |
| I-5 / SR-6 / SR-7 | pass 1 static; pass 2 (SR-6, SR-7, raised guard) separate plan, runbook, session, approval |
| I-6 disk | CRYPTO_AR_BLOBSTORE set and round trip passes; S01 asserts disk_free >= 6 GiB and MemAvailable >= 11 GiB |
| I-8 | protocol frozen before any dependent hash |
| Validity assertions | raw-result.json only, against the adapter's keys; no JSON assertion on manifest.yaml |

## 5. Text for the specification and protocol edits

Specification `design_revision`, revision 3, 2026-11-06, by coordinator, scope "draft only; no frozen record touched":

- DR-11 (memory enforcement). Finding: tools/experiment_execution.py applies RLIMIT_AS = memory_mb to every supervised
  trial and requires memory_mb, so the plan cannot avoid RLIMIT_AS. Ruling: the binding limit stays the resident-set
  watchdog in code/run.py (VmRSS, 10 GiB). The supervisor's RLIMIT_AS is set to a loose virtual ceiling of 32768 MB that
  is not a resource cap and decides nothing; a kill at it is an infrastructure failure under SR-7, never a censored M-1
  or negative evidence. This is a declared deviation from the letter of "never RLIMIT_AS", faithful to its intent
  (a tight RLIMIT_AS fires on virtual size and mimics a result). DEC-20261106-36e212 RUL-3.
- DR-12 (SR-8 clock). The 43200 s total is charged from the first trial (code/adapter.py session_start.json). The time of
  step S03 fixtures (timeout 3600 s) is outside it and recorded in the session journal. RUL-6.
- DR-13 (passes, replay, undecided controls). Pass 1 runs the static grid and the five certify passes. SR-6 re-runs of
  non-contained instances, the SR-7 infrastructure retry and a raised certificate size guard are pass 2 (run 2 of
  maximum_runs 3), separately approved; no seed or null is re-drawn. Replay of the trials step is not covered in pass 1
  (shared run directory); no contained-side evidence decision rests on pass-1 data before a nonce-sampled scratch replay
  is archived. An undecided PC-TRI instance is a warning, and the C-PC gate then does not hold for its cell. RUL-4, RUL-5,
  RUL-9.

Specification `budget.memory_enforcement`: append the sentence of DR-11.

## 6. Values for the experiment-director's regenerated plan and runbook

Trial plan (`crypto.autoresearch.trial_plan.v1`), keep the schema, `frozen: true`, `stop_on_invalid_output: true`:

- `task_id`: TASK-20261106-9da2e3
- `approved_by`: DEC-20261106-e7576f
- `queue`: coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/dispatch_queue.json
- `specification`: experiments/EXP-SEMBIN-cb5e25/specification.yaml; `specification_sha256`: `$S_A` (the approved-bytes preview,
  NOT `$S_R`)
- `input_sha256`: protocol.json FILE hash `$PF`
- `source_sha256`: every file any argv or check_argv names, including code/adapter.py and code/check_trial.py (absent
  from the draft), code/CODE_SHA256.json, tools/artifact_store.py; keep the engine and tools files already listed
- every trial: `memory_mb` 32768; no `watchdog_seconds` (RUL-6); `artifacts` [manifest.yaml, raw-result.json];
  `run_id` unique random-suffix `RUN-SEMBIN-xxxxxx` (new values are fine); `depends_on` earlier trials only
- every trial `argv` (adapter, not run.py directly), for example
  `python3 experiments/EXP-SEMBIN-cb5e25/code/adapter.py --run-dir {run_dir} --shared-run-dir experiments/EXP-SEMBIN-cb5e25/runs/RUN-SEMBIN-d1204f --kind trial --cell <cell> --arm <arm> --r <r> --protocol-sha256 <PH> --wdag auto --total-seconds 43200 --reserve-seconds 1200`
  plus `--aa-source EQS4|EQS4-U` for EQS4-AA (the adapter derives the trial id `<cell>__EQS4-AA__r<r>__<source>`); the five
  certify trials use `--kind certify --cell <cell>` for m3n12, m3n13, m3n14, m4n08, m4n09, each after that cell's trials;
  read code/adapter.py lines 4-25 and 103-122 for the exact CLI
- every trial `check_argv`:
  `python3 experiments/EXP-SEMBIN-cb5e25/code/check_trial.py {run_dir} --shared-run-dir experiments/EXP-SEMBIN-cb5e25/runs/RUN-SEMBIN-d1204f`
- plan order exactly as `code/plan.py` emits it (the draft's 582 + 5 certify = 587 trials); the grid and arms per tier are
  code/cells.py and are not changed

Runbook (`crypto.autoresearch.runbook.v1`), session id RBS-SEMBIN-19ce78, `approval: {mode: decision_record}`:

- binds: add code/adapter.py, code/check_trial.py, experiments/EXP-SEMBIN-cb5e25/collision-search.json,
  tools/artifact_store.py (already bound); specification bind = `$S_R` (review_required bytes; the approval archive rebinds
  to `$S_A`); protocol bind = `$PF`; trial-plan bind = `$T`
- spec_bindings: keep the existing ones; add `protocol.json /freeze/status equals frozen` and
  `protocol.json /freeze/protocol_sha256 equals <PH>`
- S01 probe: assert `/disk_free` min 6442450944; read MemAvailable (not MemTotal) and assert `/mem_kb` min 11534336; record
  `os.environ.get('CRYPTO_AR_BLOBSTORE')` and assert it matches `^(s3://|file:///)`
- new step after S01 (purpose probe, 120 s): blob store round trip with tools/artifact_store.py `store_from_env()` put and
  get of a fixed small byte string, assert the bytes match
- S02 create run directory (60 s); new step (purpose coordination, 60 s) copying
  experiments/EXP-SEMBIN-cb5e25/collision-search.json to the run directory before the first measurement
- S03 fixtures: timeout 3600, argv with `--protocol-sha256 <PH>`, retry only on timeout (max 2), exit 1 stop
- S05 trials: `engine: supervisor`, `timeout_seconds` 43200, `claim.ttl_minutes` 750, `on_invalid: stop`, replay `exempt` with
  the reason that trials append to one shared directory by a literal path and the instrument refuses to overwrite a finished
  trial (reported not_covered), `on_failure` timed_out class resource_exhaustion action stop
- validity per trial on raw-result.json only (RUL-13); no manifest.yaml json assertion; nothing that predicts an outcome
- S06 analysis timeout 1800, S07 60
- metrics and report blocks as drafted, regenerated for the new trial ids
- hand back: `LINT OK` output, the card, and the generator script

## 7. Builder script (save as coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-501c2f/build_queue.py)

```python
#!/usr/bin/env python3
"""Builds dispatch_queue.json for BATCH-501c2f and the final handoff preview from the final trial plan.
Run from the repo root: build_queue.py --design-dir coordination/design/<DA>/EXP-SEMBIN-cb5e25
Reads the trial plan and the template ledger/handoffs/TASK-20261106-9da2e3.yaml; writes the queue and
<design-dir>/handoff.preview.yaml. Launches nothing, changes no record."""
import argparse, hashlib, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from experiment_execution import GENERATED  # noqa: E402

EXP, GOAL, BATCH = "EXP-SEMBIN-cb5e25", "GOAL-SEMBIN-fcb7a2", "BATCH-501c2f"
EXEC, ARCH, DEC = "TASK-20261106-9da2e3", "TASK-20261106-c5d001", "DEC-20261106-e7576f"
TOKEN = "TRIAL-PLAN-SHA256-TOKEN"
EMBED = ("artifact_paths", "budget", "completion_gate", "constraints", "deliverables", "execution",
         "from", "id", "inference", "inputs", "objective", "to", "uncertainty_reduced")

ap = argparse.ArgumentParser()
ap.add_argument("--design-dir", required=True)
args = ap.parse_args()
design = ROOT / args.design_dir

plan_path = ROOT / f"experiments/{EXP}/trial-plan.json"
plan_bytes = plan_path.read_bytes()
plan = json.loads(plan_bytes)
plan_sha = hashlib.sha256(plan_bytes).hexdigest()
assert plan["task_id"] == EXEC and plan["approved_by"] == DEC, "plan task_id or approved_by wrong"
assert plan["queue"] == f"coordination/goals/{GOAL}/batches/{BATCH}/dispatch_queue.json"

per_trial = [f"experiments/{EXP}/runs/{t['run_id']}/{n}" for t in plan["trials"] for n in (*GENERATED, *t["artifacts"])]
text = (ROOT / f"ledger/handoffs/{EXEC}.yaml").read_text()
text = (f"# {EXEC}: prospective executor handoff for {EXP} (preview; canonical path "
        f"ledger/handoffs/{EXEC}.yaml after approval).\n") + text[text.index("handoff:\n"):]
text, n = re.subn(r"  # PER-TRIAL-ARTIFACT-PATHS-MARKER.*\n(?:  # .*\n)*",
                  lambda m: "".join(f"  - {p}\n" for p in per_trial), text, count=1)
assert n == 1 and TOKEN in text, "template markers missing"
text = text.replace(TOKEN, plan_sha)
handoff = yaml.safe_load(text)["handoff"]
if handoff["budget"]["maximum_runs"] != len(plan["trials"]):
    print(f"WARNING: handoff maximum_runs {handoff['budget']['maximum_runs']} != {len(plan['trials'])} trials; fix the template", file=sys.stderr)
design.mkdir(parents=True, exist_ok=True)
(design / "handoff.preview.yaml").write_text(text)

embedded = {k: handoff[k] for k in EMBED}
queue = {
    "batch_id": BATCH, "goal_id": GOAL, "max_concurrent": 1,
    "max_concurrent_basis": "One executor at a time. Machine headroom, not a research cap: the run holds up to 10 GiB resident on a 15 GB host.",
    "notes": ["Written under DEC-20261106-36e212. It launches nothing. Queued tasks have no execution authority until the approval decision is archived and execution_state is ready."],
    "objective": "Admit pass 1 of EXP-SEMBIN-cb5e25 as one runbook session, then its run archive.",
    "schema": "crypto.autoresearch.dispatch_queue.v1",
    "tasks": [
        {"archived_by": ARCH, "artifact_paths": handoff["artifact_paths"], "depends_on": [], "handoff": embedded, "id": EXEC,
         "priority": 10, "review_required": False, "role": "executor", "state": "queued",
         "title": "Run EXP-SEMBIN-cb5e25 pass 1 runbook session RBS-SEMBIN-19ce78",
         "read_scope": [f"experiments/{EXP}", "experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py", "src/crypto_autoresearcher/gf2",
                        "src/semaev_tree.py", "tools", "ledger/hypotheses/H-SEMBIN-e5b2db.yaml", f"ledger/decisions/{DEC}.yaml",
                        f"ledger/handoffs/{EXEC}.yaml"],
         "write_scope": [f"experiments/{EXP}/runs", f"experiments/{EXP}/runbook-sessions", f"experiments/{EXP}/reports"]},
        {"archive": {"binding_mode": "commit", "commit_sha": None, "kind": "snapshot", "parent_sha": None, "path_sha256": {},
                     "record_ids": ["H-SEMBIN-e5b2db", EXP, DEC, EXEC, ARCH], "source_task_ids": [EXEC]},
         "artifact_paths": [f"coordination/design/{ARCH}/snapshot.json"], "depends_on": [EXEC],
         "handoff": {"budget": {"maximum_runs": 0},
                     "completion_gate": ["snapshot.json names the commit holding every run and session file"],
                     "constraints": ["Do not launch a trial."],
                     "deliverables": [f"coordination/design/{ARCH}/snapshot.json"],
                     "from": "coordinator", "id": ARCH, "inputs": [f"ledger/handoffs/{EXEC}.yaml"],
                     "objective": f"Archive the run and session records of {EXP}. Run nothing.", "to": "coordinator",
                     "uncertainty_reduced": "Whether the session and run records have a single commit."},
         "id": ARCH, "priority": 20, "review_required": False, "role": "coordinator", "state": "queued",
         "title": f"Archive {EXP} pass-1 run records",
         "read_scope": [f"experiments/{EXP}/runs", f"experiments/{EXP}/runbook-sessions", f"experiments/{EXP}/reports",
                        f"experiments/{EXP}", "ledger/hypotheses/H-SEMBIN-e5b2db.yaml", f"ledger/decisions/{DEC}.yaml",
                        f"ledger/handoffs/{EXEC}.yaml"],
         "write_scope": [f"coordination/design/{ARCH}"]},
    ],
}
qpath = ROOT / plan["queue"]
qpath.parent.mkdir(parents=True, exist_ok=True)
qpath.write_text(json.dumps(queue, indent=2, sort_keys=True) + "\n")
print("trial_plan_sha256", plan_sha)
print("queue_sha256", hashlib.sha256(qpath.read_bytes()).hexdigest())
print("handoff_preview_sha256", hashlib.sha256((design / "handoff.preview.yaml").read_bytes()).hexdigest())
print("per_trial_paths", len(per_trial), "trials", len(plan["trials"]))
```

If `research_dispatch.py` refuses an embedded key, compare with `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-38f344/dispatch_queue.json`
(lines 12 to 301) and adjust the builder, not the plan.

## 8. Dispatch preconditions (all must hold; none is waived by success elsewhere)

1. DEC-20261106-e7576f committed and merged; `newest_experiments.py` reports `execution_state: ready`.
2. Resume checkpoint filled and pushed (`scripts/checkpoint.sh init`; CLAUDE.md).
3. `CRYPTO_AR_BLOBSTORE` set; the round trip of the new runbook step passes; `df -B1 experiments` shows at least 6 GiB free
   (S01 asserts it).
4. No live claim on any other queue of GOAL-SEMBIN-fcb7a2 (`python3 tools/goal_lanes.py claims <queue>`), RUL-2.
5. Declared inputs committed and pushed; a lane claim through the runbook's supervisor (the engine claims
   `TASK-20261106-9da2e3` with ttl 750 minutes).
6. Dispatch the executor with `executor-mechanical`; relay the card verbatim; read only the last line of step S05.

## 9. Not decided here

- Pass 2: whether SR-8 is per pass or cumulative; the pass-2 shared run directory and clock (the adapter's
  `session_start.json` is never overwritten); the pass-2 disk floor with a 4 GiB certificate guard. Decided in the pass-2
  design decision from measured pass-1 time.
- Whether 32768 MB suffices for the wdag at N = 26 and the N = 40 closure: unmeasured. Measure the virtual size of the
  largest unit in a scratch run if one can be done without peeking at target outcomes, otherwise leave as stated.
- Measured timings for the revision 2 additions: advisory; if measured, only on fixtures, never on target cells.
- Whether another ref holds a third SEMBIN lane: answered by step 0.2.
- The blob store location: an environment fact (S3 bucket and credentials, or a file store on another volume).
