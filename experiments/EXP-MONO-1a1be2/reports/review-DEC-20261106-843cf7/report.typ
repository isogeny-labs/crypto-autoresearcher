#set document(title: "Decision report DEC-20261106-843cf7", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#set figure(numbering: none)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)
#let s(x) = x

= Decision report: DEC-20261106-843cf7
GOAL-PATH-001 · RQ-MONO-001 · EXP-MONO-1a1be2 · composes the code review TASK-20261105-165da2 (snapshot TASK-20261105-49716d at 608902a44d; commit reviewed 72f51766a6, the TASK-20261105-ac5ad6 bytes snapshotted by TASK-20261105-7083a8) · declared successor of DEC-20261105-f0b7c7 NA-1 · composing task TASK-20261106-fdd5c2 · ledger archive TASK-20261106-0c8aee · checkpoints BATCH-8517aa, opens BATCH-69d9a2 · 2026-11-06

== Status
- *No run exists.* This act launched zero runs; no contract cell of EXP-MONO-1a1be2 has been counted, and every task in BATCH-69d9a2 is zero-run.
- *Nothing is approved.* The act approves no experiment, protocol, runbook or run. EXP-MONO-1a1be2 stays a review\_required draft; the specification is unedited (d81a85b3...c373). The standing user authorization (2026-09-06) is noted but not used: gate B8 failed, so no contract is approvable.
- *No evidence record is decided.* There is no EV-\* record, no RUN-\* id and no status move: H-MONO-23d347 stays proposed, and no knowledge entry is promoted (#s("knowledge_promotion.promoted: []")). No KAT value, mutant count or W10 count in this report is evidence about any prediction.
- The decision takes effect only when the ledger archive TASK-20261106-0c8aee verifies.
- This is not a performance measurement: no benchmarks/ entry and no index-calculus leaderboard regeneration apply.

== Decision
- *Decision:* #s("revise"). *Claim tier:* instrument review; no mathematics. *Evidence strength:* none assigned (a code review is not evidence; rationale R-6).
- *Scope (decision\_scope, condensed):* (1) composes the 165da2 code review: F-1 and N-1 to N-5 are fixed before approval, N-6 is a recorded limitation with a trigger; (2) under the owner's direction, DEV-1 is fixed before approval by running the m = 3 large-q check on a substitute non-contract cell (FX-16), not recorded as a limitation; (3) amends, before any approval and with zero runs, the approval-lock content of DEC-20261105-f0b7c7 (approval\_lock\_binding\_v2) and pins four specification additions V2-1 to V2-4 for the v2 amendment; (4) writes the BATCH-8517aa checkpoint and opens BATCH-69d9a2 with six tasks. #s("predictions_to_freeze") of DEC-20261105-f0b7c7 is unchanged in every value.
- *Composed verdict for B8:* B8 stays open. It clears when TASK-20261106-649ebb archives a TASK-20261106-7c2b01 report that finds every must-fix closed and no new blocking finding.
- *Records:* DEC-20261106-843cf7, DEC-20261105-f0b7c7, TASK-20261105-165da2, TASK-20261105-49716d, TASK-20261105-ac5ad6, TASK-20261105-7083a8, EXP-MONO-1a1be2, H-MONO-23d347, IDEA-20261023-f15270, BATCH-8517aa, BATCH-69d9a2, KN-OPEN-62c870.

== Observation
From the 165da2 review (code\_review.md, sha256 4c77c235...c101, verdict #s("failed") for B8 because F-1 is blocking; one validator session, zero experiment cells), findings as the reviewer recorded them:

#table(columns: (0.35fr, 0.55fr, 0.75fr, 3.2fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*CR*], [*severity*], [*finding (reviewer's words, condensed)*],
  [F-1], [CR-1], [*blocking*], [#s("The start-up known-answer gate (stopping rule 1) is neither bound nor recorded: tests/test_kat.py and the repository-level pytest configuration and conftest.py are outside code_sha256 and the lock; exit code 0 counts as pass in full; a hand-written or other-host receipt skips the suite; the run package records none of this.")],
  [N-1], [CR-3], [non-blocking], [#s("Mutant M5 (32-bit target index) survives all 316 KATs; it is active only where Q > 2^31 (arm-C n = 6, 7). The large-q arm-C KAT W10 compares all-zero vectors at every n >= 4. The committed kernel was checked correct on this path by a reviewer differential.")],
  [N-2], [CR-1, CR-6], [non-blocking], [#s("The invalidation and stopping rules (R1 recount VOID, group-law mismatch, F2 family stop) are not applied in the run package; a disagreeing recount is written status: completed, with no validity field.")],
  [N-3], [CR-6], [non-blocking], [#s("lambda uses the closed-form cancellation-free total (the P2(vi) expression); the counted total is recorded beside it and never compared.")],
  [N-4], [CR-4, CR-5], [non-blocking], [#s("KAT-mode arm-C packages still write lambda and the P2(vi) closed form (IM-3 hygiene only; files not retained, nothing asserted).")],
  [N-5], [CR-1, CR-6], [non-blocking], [#s("Gate and record hardening: execution_authorized and frozen not checked; lock approved_by not compared; --run-id unsanitized; cdf.json lacks the target seed; peak RSS excludes B1 workers; module shadowing route.")],
  [N-6], [CR-2], [non-blocking], [#s("A B2 cell reuses one tuple seed for both rung instances; unreachable in the regenerated plan (no instance above 10^4 subsets; max 8,515).")],
)
The executor deviation DEV-1 (from #s("dev1_decision.deviation"), recorded in kat-report-ac5ad6.md): KX-4 asked for the large-q E2 sampled-counter KAT at m in {2, 3} for every n = 2..7; the cell (32779, 2, m = 3) was not run (about 6e12 multisets, about 17 h, over the 8 h budget) and was checked at m = 2 only.

*What held* (code\_review.md "What held"): CR-1 every refusal condition refuses with no runs/ entry, and code\_sha256 covers every module and source a cell imports or compiles; CR-2 the plan regenerates byte-identically (twice) to 9ccbe614...fb4a, all 298 seed strings follow their rules; CR-3 the four n >= 4 mutants M1 to M4 are killed by widened KATs only; CR-4 residuals P2(vii) to (ix) match an independent recomputation on 33 of 33 KAT cases and KAT mode withholds them; CR-5 no KAT asserts a prediction, and the KAT refusal covers all 96 (pair, arm) combinations; CR-6 the sampler follows the rule, lambda is an exact Fraction, cdf.json carries all 22 IDEA keys.

*Recorded CR-3 values* (Figure 2): full-suite failures out of 316 are 92 (M1), 92 (M2), 56 (M3), 40 (M4) and 0 (M5, 316 passed: survives). Of the eleven W10 cells, two have sampled targets with a nonzero count, (32779, 2, m = 2) with 22 of 50 and (1033, 3, m = 3) with 8 of 50; the other nine have 0 of 50. In the reviewer differential, the committed kernel equals Python #s("target_index") on 300 random points per field, and M5 differs on 164 of 300 at (41, 6) and on 251 of 300 at (29, 7).

#figure(image("mutation-kill.svg", width: 100%), caption: [Figure 2. TASK-20261105-165da2 code\_review.md CR-3. Panel A: failing items in the full 316-item suite for mutants M1 to M5 (M5 survives). Panel B: the eleven W10 cells (q, n, m), number of the 50 sampled targets with a nonzero count; the nine all-zero cells are marked vacuous. The annotation gives the reviewer differential in words with its two recorded counts. Exact recorded counts, no sampling error drawn. KAT fields only, none a contract cell; no new computation. Data: figure-data.json; regenerate with figures.py.])

== Comparison
Reviewer severity against this act's disposition (#s("code_review_composition.findings")), under the stated reading rule: a finding is must-fix when, left alone, it lets a cell that violates the stopping or invalidation rules be recorded as valid, or lets an instrument defect reach a P-reading under F7 or F8, or when its fix costs less than its separate tracking; it is a recorded limitation only when no path the approved plan executes can reach it, and then carries a trigger.

#table(columns: (0.4fr, 0.8fr, 1.3fr, 0.7fr, 2.3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*reviewer*], [*this act*], [*re-review*], [*why (decision, condensed)*],
  [F-1], [blocking], [must-fix FX-2 to FX-6], [RR-2], [#s("Each of the gaps (a)-(e) alone lets a cell start without the full suite having passed. Reviewer's five-part repair adopted, plus: scrub PYTEST_ADDOPTS and PYTEST_PLUGINS and disable plugin autoload; a receipt that fails a check refuses the cell.")],
  [N-1], [non-blocking], [must-fix FX-7 (owner direction)], [RR-3], [#s("The start-up suite guards the executing host; arm-C n = 6, 7 is a third of arm C. The M5 mutant must fail a new item, confirmed independently by 7c2b01. W10 made non-vacuous at every n >= 3.")],
  [N-2], [non-blocking], [must-fix FX-8 (owner direction)], [RR-4], [#s("A launcher-side validity block and an enforced F2 stop remove a judgement the mechanical tier should not make; the analysis still recomputes validity and the stricter reading wins (V2-2).")],
  [N-3], [non-blocking], [must-fix FX-9], [RR-5], [#s("Couples P6 (F8) to P2(vi) (F7). The specification defines lambda from the cancellation-free total, so the counted value is the definition (V2-3).")],
  [N-4], [non-blocking], [must-fix FX-10], [RR-5], [#s("IM-3 says no derived statistic is recorded in KAT mode; the fix costs minutes.")],
  [N-5], [non-blocking], [must-fix FX-11 (owner direction)], [RR-4], [#s("Five small hardening items; cheap while the launcher is changing; one test per item that fails on the 72f51766a6 code.")],
  [N-6], [non-blocking], [recorded limitation L-2], [RR-1 (plan byte-identical; FX-12 no change)], [#s("Unreachable in this plan; changing seed derivation risks the plan's byte identity for no gain. Trigger: any successor plan with a B2 instance above 10^4 subsets.")],
  [DEV-1], [executor deviation], [must-fix FX-16 (substitute cell, owner direction)], [RR-5], [#s("Reverses the first draft, which accepted DEV-1 as a limitation (draft L-1, withdrawn).")],
)
Five of the six non-blocking findings are raised to must-fix; the blocking finding stays blocking; only N-6 becomes a limitation.

== Inference
*Owner direction*, quoted as relayed (#s("owner_direction.text_as_relayed;") the composing subagent did not see the user's message and records it as relayed, not as an approval of anything):
#vb[#s("All three items are to be FIXED before approval, not recorded as limitations. (1) DEV-1: the m = 3 large-q check must actually be run, either on a substitute non-contract large-q cell at m = 3 within a stated budget or with a one-off budget for (32779, 2) at m = 3, saying which and why, with zero contract cells. (2) N-1: a KAT that kills the 32-bit target-index mutant, for example a Q > 2^32 index test with nonzero large-q counts on a non-contract cell, confirmed killed by the re-review. (3) N-2 and N-5: fixed in the launcher before approval, with tests that fail on the old code. N-3, N-4 and N-6 are left to the Coordinator.")]

*Must-fix list:* F-1 (FX-2 to FX-6), N-1 (FX-7), N-2 (FX-8), N-3 (FX-9), N-4 (FX-10), N-5 (FX-11), DEV-1 (FX-16). FX-1 keeps fqn.py, curves.py, semaev.py, kernel.c, make\_trial\_plan.py and throughput\_calibration.py byte-identical (a fix needing them stops 4c4831); FX-12 makes no change for N-6.

*DEV-1 fixed by the FX-16 substitute.* A non-contract cell over #s("F_{q''^2}, q''") the least prime greater than 10,000 (computed by trial division in the test and checked disjoint from every contract pair), running the large-q E2 sampled-counter KAT at m = 3 on the line base with s = 50 targets, checked by an independent membership method in Python field arithmetic under the KX-4 rules. Budget 14,400 s wall and 16 GB inside 4c4831; the executor first records a measured projection and stops and reports if it exceeds the budget, never shrinking the cell silently. Substitute rather than budget (#s("why_substitute_not_budget")): it keeps degree 2, tuple size 3, depth-3 multiset enumeration in the compiled kernel, the same index-width class and nonzero counts on sampled targets, at about 1/30 of the multisets; the exact cell needs about 17 h in the kernel plus an independent method of hours with memory near the 16 GB cap; and no contract cell runs m = 3 at n = 2, so the check guards a code path, not a contract configuration.

*Approval lock v2* (#s("approval_lock_binding_v2"), supersedes the lock content and receipt clause of DEC-20261105-f0b7c7): approval.lock carries five fields, approved\_by, specification\_sha256 (v2 bytes), code\_sha256 (same seven CODE\_FILES, same definition), trial\_plan\_sha256 and the new test\_file\_sha256; check\_approval refuses a lock missing a field or mismatching a hash. The approval decision records the 5c1258 snapshot commit, per-file hashes, code\_sha256, EXPECTED\_KAT\_ITEMS and DESIGNED\_SKIPS; the 72f51766a6 bytes stay bound as history. Self-test receipts are written only by the launcher's selftest subcommand after the lock exists, into selftest-receipts/, binding code, test-file and lock hashes, an environment key and the junit XML hash.

*Specification additions for v2* (invalidation and reading rules, written before any data; not predictions):
- *V2-1* Stopping rule 1 made checkable: a cell is INVALID (infrastructure) unless its manifest carries a gate block with the approved hashes and a startup\_selftest block showing a full pass on the executing host (collected equal to EXPECTED\_KAT\_ITEMS, zero failures and errors, skips exactly DESIGNED\_SKIPS).
- *V2-2* A launcher-written validity block per manifest; the analysis recomputes validity from raw fields and the stricter status applies, the difference reported as an instrument finding.
- *V2-3* Arm-C lambda from the counted cancellation-free total; the P2(vi) closed form beside it with an equality flag per cell and base; inequality withholds that cell's P6 reading (INCONCLUSIVE) and is investigated under F7 first, never read as F8.
- *V2-4* The F2 family stop enforced by the launcher through a runs/STOP-F2.json sentinel that refuses every later arm-A cell; removing it requires a new implementation commit and a Coordinator decision.

Blockers after this act (#s("updated_blockers")): B1 open (narrowed), B2 open (determinism confirmed), B3 cleared, B4 open, B5 open, B6 open, B7 cleared, B8 open (failed once). Figure 1 (next page) draws the composition.

#page(flipped: true, margin: (x: 1.3cm, top: 1.1cm, bottom: 1.6cm))[
#figure(image("findings.svg", width: 90%), caption: [Figure 1. Composition of the TASK-20261105-165da2 code review by DEC-20261106-843cf7. Rows F-1, N-1 to N-6 and DEV-1: reviewer severity, the finding in words, this act's disposition (must-fix with its FX ids, or recorded limitation L-2 with its trigger; N-1, N-2, N-5 and DEV-1 under owner direction), and the TASK-20261106-7c2b01 re-review check that verifies it. Strip: blockers B1 to B8 after this act. Every edge is an instrument step, not evidence. Data: figure-data.json; regenerate with figures.py.])
]

== Limitation
- *L-2 (N-6):* B2 reuses its tuple seed across the two rung instances; unreachable in this plan; trigger to must-fix: any successor plan in which some B2 instance has more than 10^4 subsets (per-rung seeds then required before approval). No L-1 is recorded: draft L-1 for DEV-1 was withdrawn under the owner's direction, and FX-16 replaces it.
- *Session-only independence:* 165da2 and 7c2b01 are independent between sessions only, not between models (resolved model claude-opus-5-5, model\_verified false). This is not a rule-12 round, and nothing here triggers rule 12. 7c2b01's blindness is lifted deliberately: it reads the 165da2 report, not the fix producer's session.
- *KAT-field scope:* every mutant and residual check ran on KAT fields; behaviour at contract fields is inferred from identical code paths plus the regenerated identity fields. The FX-16 substitute likewise checks a code path, not a contract cell; the exact (32779, 2, m = 3) cell stays unrun (#s("residual_note"): a successor plan running m = 3 at n = 2 at contract size, or any configuration whose multiset count exceeds 2^32, needs a KAT at that scale before approval).
- From #s("scope_and_limitations"): the composing act ran no tool and computed no hash (merge state, PR numbers, commit ids and the TP-1 flag are as reported; 0c8aee re-checks what it can); 165da2 reproduced F-1 (b) on a scratch tree, not a full checkout (7c2b01 checks it in a full checkout, RR-2); receipts are not cryptographically authenticated (forgeable only by deliberate fabrication inside the experiment directory, checkable after the fact); toy tier throughout, with KN-OPEN-62c870 CS-D2 and CS-R7 binding every later citation.
- This report re-ran nothing: figure-data.json copies values by key or by section and table, and figures.py derives only layout and labels.

== Next actions
BATCH-69d9a2 (#s("coordination/goals/GOAL-PATH-001/batches/BATCH-69d9a2/dispatch_queue.json")), max\_concurrent 1, strictly in sequence, zero runs:
#table(columns: (0.25fr, 1.25fr, 0.75fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*\#*], [*task*], [*role*], [*work*],
  [1], [TASK-20261106-fdd5c2], [coordinator], [#s("This act: compose the 165da2 review, decide DEV-1, write the BATCH-8517aa checkpoint, open BATCH-69d9a2 (completed on writing; archived by 0c8aee).")],
  [2], [TASK-20261106-0c8aee], [coordinator], [#s("Ledger archive of this act, ALONE; closes lane BATCH-8517aa; pins the 4c4831 inputs; checks OC-1 to OC-6.")],
  [3], [TASK-20261106-4c4831], [executor], [#s("executor-implementation: FX-1 to FX-16, including the DEV-1 substitute cell; zero contract cells, zero runs; archived by 5c1258.")],
  [4], [TASK-20261106-5c1258], [coordinator], [#s("Snapshot of 4c4831, alone among commit tasks; re-binds code_sha256.")],
  [5], [TASK-20261106-7c2b01], [validator], [#s("review-adversarial, fresh independent session: focused re-review RR-1 to RR-8 on the 5c1258 commit; terminal B8 verdict; archived by 649ebb.")],
  [6], [TASK-20261106-649ebb], [coordinator], [#s("Snapshot of 7c2b01, alone among commit tasks.")],
)
- *NA-1* (coordinator, shell-holding top-level session; exactly one next action): commit the BATCH-69d9a2 queue alone, render it and open lane BATCH-69d9a2; render this report; run 0c8aee alone, push, refresh the ready-for-review PR with auto-merge, and close lane BATCH-8517aa; then dispatch 4c4831, with 5c1258, 7c2b01 and 649ebb following in queue order.
- *Declared successor* (after 649ebb verifies with B8 cleared; not an additional next action): a fresh Coordinator approval act writes the v2 amendment (predictions\_to\_freeze unchanged, V2-1 to V2-4), freezes protocol.json, sets watchdogs, compiles the runbook, writes the run handoff, approves only on approvable true, writes approval.lock per approval\_lock\_binding\_v2, and requires execution\_state ready and .resume/RESUME.md pushed before any run.
- If 7c2b01 finds a must-fix not closed or a new blocking finding, a fresh act (spare DEC-20261106-720ace) opens one further fix round; a second consecutive failed re-review, a fix needing a kernel or plan change, a regenerated plan differing from 9ccbe614...fb4a, or no approval by 2026-12-15 is a rerank trigger.

== Canonical graphs checked
None changes: no evidence record, status or knowledge entry moves. Checked and *left unchanged*:
- experiments/EXP-MONO-1a1be2/reports/review-DEC-20261105-f0b7c7/composition.svg and split-fraction.svg (and that report's PDF): the previous decision report on this experiment; its joints and split fractions are not touched by an instrument review.
- knowledge/frontiers/ecdlp/: README.md and its records; the frontier holds no SVG graph, and nothing here is a cost claim.
- docs/reports/2026-10-23-idea-f15270-rescope/convention-map.svg (and its report.pdf): not canonical, not edited.
- experiments/EXP-MONO-0e6e8f/reports/review-DEC-20261022-a0f165/monodromy-frequencies.svg: an earlier decision report on the same Semaev lineage; historical, not edited.

== Provenance and rendering
Figures: figures.py (matplotlib, Agg, svg.fonttype none, svg.hashsalt DEC-20261106-843cf7, metadata Date None) reads figure-data.json and writes findings.svg and mutation-kill.svg byte-identically on repeat. figure-data.json names, for every value, its source: the decision (ledger/decisions/DEC-20261106-843cf7.yaml, sha256 fd0debc2...c45d), code\_review.md sections "Result" and "CR-3" (sha256 4c77c235...c101, as at 608902a44d), and the RR and FX items of ledger/handoffs/TASK-20261106-7c2b01.yaml and TASK-20261106-4c4831.yaml. PDF compiled with the Typst Python wheel in a scratch virtualenv outside the repository, and every page inspected.
