#set document(title: "Decision report DEC-20261106-475620", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#set figure(numbering: none)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)
#let s(x) = x

= Decision report: DEC-20261106-475620
GOAL-PATH-001 · RQ-MONO-001 · EXP-MONO-1a1be2 · composes the focused re-review TASK-20261106-7c2b01 (fix\_review.md, sha256 52198231...2e1a, snapshot TASK-20261106-649ebb at 573356f303; commit reviewed 9a0b5955146a, the TASK-20261106-4c4831 fixes snapshotted by TASK-20261106-5c1258) · declared successor of DEC-20261106-843cf7 #s("batch.focus.inconclusive_decision") · composing task TASK-20261106-d5063d · ledger archive TASK-20261106-779e02 · checkpoints BATCH-69d9a2, opens BATCH-a8825c · 2026-11-06

== Status
- *No run exists.* This act launched zero runs; no contract cell of EXP-MONO-1a1be2 has been counted, and every task in BATCH-a8825c is zero-run. The DEV-1 cell it schedules is a non-contract KAT cell, not an experiment run.
- *Nothing is approved.* The act approves no experiment, protocol, runbook or run. EXP-MONO-1a1be2 stays a review\_required draft; the specification is unedited (d81a85b3...c373). The standing user authorization (2026-09-06) is noted but not used: B8 failed, so no contract is approvable ("Approval is bounded by execution").
- *No evidence record is decided.* There is no EV-\* record, no RUN-\* id and no status move: H-MONO-23d347 stays proposed, no hypothesis, idea or goal status changes, and no knowledge entry is promoted (#s("knowledge_promotion.promoted: []")). No KAT value, mutant count or timing in this report is evidence about any prediction.
- The decision takes effect only when the ledger archive TASK-20261106-779e02 verifies.
- This is not a performance measurement: no benchmarks/ entry and no index-calculus leaderboard regeneration apply.

== Decision
- *Decision:* #s("revise"). *Claim tier:* instrument re-review; no mathematics. *Evidence strength:* none assigned (a code review is not evidence; rationale R-7).
- *Scope (decision\_scope, condensed):* (1) composes the 7c2b01 re-review: N-5 item 5 and NF-1 (graded blocking) are fixed by one code-tree hardening item; NF-2 to NF-7 are all must-fix; the five closed items stay closed. (2) Under the owner's direction, DEV-1 is fixed by running the unchanged FX-16 cell with a 12 h budget, after the fixes, on the fixed bytes. (3) Pins two further invalidation rules for the v2 amendment (V2-5, V2-6) and amends the approval records to the new snapshot, before any data. (4) Records the SF-1 rate correction to DEC-20261106-843cf7 #s("dev1_decision"). (5) Writes the BATCH-69d9a2 checkpoint and opens BATCH-a8825c with seven tasks. #s("predictions_to_freeze") of DEC-20261105-f0b7c7 is unchanged in every value.
- *Composed verdict for B8:* B8 stays *open* (failed once at 165da2 and once at 7c2b01). It clears when TASK-20261106-afbe9b archives a TASK-20261106-941825 report that finds every must-fix of this act and of DEC-20261106-843cf7 closed (including DEV-1, and M6 killed by the reviewer's own run) and no new blocking finding.
- *Records:* DEC-20261106-475620, DEC-20261106-843cf7, DEC-20261105-f0b7c7, TASK-20261106-7c2b01, TASK-20261106-4c4831, TASK-20261106-5c1258, TASK-20261106-649ebb, EXP-MONO-1a1be2, H-MONO-23d347, IDEA-20261023-f15270, BATCH-69d9a2, BATCH-a8825c, KN-OPEN-62c870.

== Observation
From the 7c2b01 re-review (fix\_review.md "Result"; validator, review-adversarial, fresh session; zero experiment cells; terminal verdict #s("failed") for B8), as the reviewer recorded them.

*Must-fix items of DEC-20261106-843cf7:* 5 closed (F-1, N-1, N-2, N-3, N-4) and 2 not closed (N-5 item 5, DEV-1).

#table(columns: (0.45fr, 0.55fr, 0.8fr, 3.2fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*item*], [*fixes*], [*status*], [*evidence (reviewer's words, condensed)*],
  [F-1], [FX-2 to FX-6], [closed], [#s("Gaps (a) to (e) closed; all 15 165da2 CR-1 scenarios and every RR-2 attack refuse with no runs/ entry; the full-checkout self-test collects 379 = EXPECTED_KAT_ITEMS. Caveat: the F-1 failure mode is reachable again through planted bytecode, classified under N-5 (5) and NF-1.")],
  [N-1], [FX-7], [closed], [#s("M5, applied by the reviewer, fails 8 items of the 379-item suite, all new or strengthened; the vacuity guards were recounted independently by brute force; the M3 control is still killed (58 of 379).")],
  [N-2], [FX-8], [closed], [#s("All 11 FX-8 items fail on the old code except the designed negative control, and pass on the new; the reviewer's own attacks void or refuse as specified, with the gaps opened as NF-2 to NF-4.")],
  [N-3], [FX-9], [closed], [#s("On a real arm-C KAT cell with a fabricated counted-total offset, lambda follows the counted definition and the P6 reading is withheld.")],
  [N-4], [FX-10], [closed], [#s("The KAT-mode arm-C package carries none of the derived keys.")],
  [N-5], [FX-11], [*not closed*: item (5)], [#s("Items (1) to (4) closed. Item (5): a sourceless code/yaml.pyc lets a cell pass the gate against the unapproved specification (repro N5-Y), and a code/pytest.pyc makes the gate record a full self-test pass for a suite that never ran (N5-P); the .py-only check returns [].")],
  [DEV-1], [FX-16], [*not closed*], [#s("test_kat_extended.py meets every card check, but the cell was not run in full: the producer stopped it on a projection of about 33,800 s against the 14,400 s budget (SF-1). The reviewer's reduced check (2,500-point sub-base, 15 targets) agrees 15 of 15 but is not the FX-16 cell.")],
)

*New findings:* 1 blocking (NF-1) and 6 non-blocking (NF-2 to NF-7), plus three observations.

#table(columns: (0.55fr, 0.8fr, 3.6fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*severity*], [*finding (reviewer's words, condensed)*],
  [NF-1], [*blocking*], [#s("Bytecode in code/__pycache__/ whose header carries the source's mtime and size is executed instead of the hashed .py; the stray check skips that directory by design. The executed code then differs from the approved build while code_sha256 equals the approved value. The same holds, by inspection, for pytest's rewrite cache and test_file_sha256.")],
  [NF-2], [non-blocking], [#s("The raw/summary check compares only per-base cdf.json keys; the top-level N, s, q, n, seed, curve_id and cell_id are never compared. A writer defect in N or s leaves validity valid.")],
  [NF-3], [non-blocking], [#s("With one convention's recount deleted (recount[\"S\"]), the cell stays valid.")],
  [NF-4], [non-blocking], [#s("F2 enforcement edges: (a) sentinel checked only in cmd_cell; (b) arm-A cells completed before the sentinel keep valid; (c) a broken-symlink sentinel is ignored; (d) run id STOP-F2.json is accepted and would swallow a true F2 write.")],
  [NF-5], [non-blocking], [#s("The large-Q arm-C S-set path has no non-vacuous KAT. Mutant M6 (uint32 truncation of S_idx in counters.arm_c_cell) is non-equivalent (O count 14 committed against 0 under M6 at (41, 6) and (29, 7), m = 2) and survives all 379 items.")],
  [NF-6], [non-blocking], [#s("A GateResult built with the module's own _GATE_TOKEN and fake hashes yields validity valid; a symlinked runs/ sends packages outside the experiment directory.")],
  [NF-7], [non-blocking], [#s("In ran mode, peak_rss_kb_children includes the start-up suite and gcc, not only the cell's workers (58,212 kB children against 46,112 kB self in a KAT B2 cell).")],
  [obs.], [observation], [#s("Valid with reasons occurs only on the P6-withheld path (V2-3, by design). cdf.json carries no m (recoverable). Two selftest runs within one second collide on the receipt directory and exit with a traceback (refusal direction).")],
)

*Recorded RR-3 and RR-5 values* (Figure 2). Full-suite failures out of 379 at 9a0b5955: M3 (control) 58, M5 8, M6 0 (379 passed: survives). DEV-1 wall time: old cell budget 14,400 s; producer projection about 33,800 s (fix-report-4c4831.md FX-16; about 4.8e6 multisets/s); reviewer projections 32,394 s (sub-base 200, 4.97e6/s) and 34,727 s (sub-base 2,500, 4.64e6/s), both on a loaded host. The cell enumerates C(B+2, 3) = 161,080,269,536 multisets at B = 9,886 whatever the number of targets.

#figure(image("mutation-kill.svg", width: 100%), caption: [Figure 2. Panel A: failing items in the full 379-item suite at 9a0b5955 for mutants M3 (control), M5 and M6 (fix\_review.md RR-3 run table); M6 survives and is the subject of HX-6. Panel B: DEV-1 cell wall time in seconds: the old cell budget, the producer projection (fix-report-4c4831.md FX-16), the two reviewer projections (fix\_review.md RR-5), and this decision's go threshold and task budget (#s("dev1_decision_v2")), with the 41,400 s cell watchdog marked. Recorded values only; KAT fields only; no new computation; timings are host measurements, not evidence. Data: figure-data.json; regenerate with figures.py.])

== Comparison
Reviewer severity against this act's disposition (#s("re_review_composition.findings")), under the reading rule unchanged from DEC-20261106-843cf7: a finding is must-fix when, left alone, it lets a cell that violates the stopping or invalidation rules be recorded as valid, or lets an instrument defect reach a P-reading under F7 or F8, or when its fix costs less than its separate tracking. Under the owner direction, no invalidation or hardening finding is recorded as a limitation in this round.

#table(columns: (0.55fr, 0.85fr, 1.15fr, 0.6fr, 2.6fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*reviewer*], [*this act*], [*941825*], [*why (decision, condensed)*],
  [N-5 (5)], [not closed], [must-fix HX-2], [RR-2], [#s("The .py-only refusal was implemented as specified; the specification was too narrow. N5-P passes V2-1 after the fact, so the F-1 failure mode is reachable again. The fix closes the class (any entry in code/ that is not a committed file), not the next suffix.")],
  [NF-1], [blocking], [*blocking kept*; must-fix HX-2], [RR-2], [#s("Considered re-grading it non-blocking because it needs a deliberately planted file; not done, for three reasons: the reading rule turns on whether an invalid cell can be recorded valid, not on intent; the forgeable-receipt limitation was accepted only because forgery is checkable after the fact, and this route is not; and the fix is launcher-only and cheap.")],
  [NF-2], [non-blocking], [must-fix HX-3 (owner direction)], [RR-4], [#s("N - |S| is the lambda denominator and s the sample size of every P6 reading: an invalidation gap on the arm-C path P6 rests on. Also adds m to cdf.json.")],
  [NF-3], [non-blocking], [must-fix HX-4 (owner direction)], [RR-4], [#s("A missing recount for one convention leaves the R1 check silently partial; one expected-set check fixes it.")],
  [NF-4], [non-blocking], [must-fix HX-5 (owner direction)], [RR-4], [#s("Edges (a), (c) and (d) defeat the launcher's F2 enforcement (V2-4); edge (b) is a reading rule, applied by the analysis under V2-5.")],
  [NF-5], [non-blocking], [must-fix HX-6 (owner direction)], [RR-3], [#s("Owner direction names the surviving mutant. S_counts and m_S feed exceptional_targets and lambda, so P6. The fix is a KAT, and the reviewer's M6 run is its acceptance test.")],
  [NF-6], [non-blocking], [must-fix HX-7 (owner direction)], [RR-4], [#s("A launcher validity of valid on a forged GateResult contradicts V2-1, and a symlinked runs/ moves packages where no archive finds them; both cheap to close.")],
  [NF-7], [non-blocking], [must-fix HX-8 (owner direction)], [RR-4], [#s("The 16 GB cap and the memory metric are read from these keys; a measurement-honesty item (AGENTS.md Artifact policy).")],
  [receipt clash], [observation], [must-fix HX-9 (cheap)], [RR-4], [#s("The mechanical tier could hit it; a unique receipt id with exclusive create costs one line and one test.")],
  [valid with reasons], [observation], [no action], [n/a], [#s("By design (V2-3); a consumer honours readings_withheld.")],
  [DEV-1], [not closed], [owner direction: unchanged cell, 43,200 s (96fee7)], [RR-5], [#s("No smaller substitute field and no limitation is considered (dev1_decision_v2).")],
)
The closed items F-1, N-1, N-2, N-3 and N-4 are held (#s("closed_items_held")); F-1 with the caveat that the bytecode route reopens its failure mode, fixed under HX-2 and re-checked in 941825 RR-2. The review's procedure deviations PD-1 to PD-4 are accepted; PD-3 (the reduced DEV-1 check) is not counted as closing DEV-1. Six of the seven new findings were graded non-blocking by the reviewer; under the owner direction this act makes all of them must-fix, keeps NF-1 blocking, and records no new limitation.

== Inference
*Owner direction*, quoted as relayed (#s("owner_direction.text_as_relayed;") the composing subagent did not see the user's message and records it as relayed, not as an approval of anything):
#vb[#s("DEV-1: keep the planned substitute cell F_{10007^2} at m = 3 (as specified in DEC-20261106-843cf7 FX-16) and GRANT it a larger budget of about 10-12 h wall time (16 GB). Earlier owner direction stands: DEV-1, the surviving mutant, and the invalidation/hardening findings are to be FIXED, not recorded as limitations.")]

*Fix list HX-1 to HX-10* (TASK-20261106-2b7223; authoritative text in ledger/handoffs/TASK-20261106-2b7223.yaml, summarized in the BATCH-a8825c queue):
- *HX-1* Declared paths only; fqn.py, curves.py, semaev.py, counters.py, kernel.c, make\_trial\_plan.py, throughput\_calibration.py, tests/test\_kat\_extended.py, the specification and every existing implementation/ file stay byte-identical to 9a0b5955146a; a fix needing one stops the task (scope finding SF-n; spare DEC-20261106-24d2a2).
- *HX-2* (N-5 item 5, NF-1) Executed-code integrity: a CODE\_TREE\_ALLOWLIST of every committed file under code/, refusing any other entry at any depth (lstat semantics); bytecode writing off and a fresh pycache prefix outside code/ before any local import; third-party imports before code/ goes on the path, with module\_origins recorded; the self-test run with -B -P and cwd outside code/; a code\_tree block with a post-cell scan.
- *HX-3* (NF-2) Every top-level cdf.json key compared, plus a new key m. *HX-4* (NF-3) Per-arm expected recount conventions. *HX-5* (NF-4) F2 edges (a) to (d). *HX-6* (NF-5) An S-set KAT at (41, 6) and (29, 7), m = 2 and 3, line and matched\_random bases, against a kernel-free membership count; M6 must fail at least one item, M5 and M3 stay killed. *HX-7* (NF-6) Validity recomputed against the on-disk gate inputs and a full self-test pass; runs/ and selftest-receipts/ must be real directories inside the experiment. *HX-8* (NF-7) Three memory keys separating self, pre-cell children and cell children. *HX-9* Unique receipt id with exclusive create. *HX-10* Regression and records: full suite passes, EXPECTED\_KAT\_ITEMS updated, all earlier refusals hold, the plan regenerates to 9ccbe614...fb4a, and every new test is shown failing on the old launcher (or, for HX-6, killing M6).

*Specification additions pinned now* (invalidation and reading rules, written before any data; not predictions; copied verbatim into the v2 amendment with V2-1 to V2-4):
- *V2-5* #s("Stopping rule 2, applied by the analysis. When runs/STOP-F2.json exists, every arm-A cell of the stopped family is VOID for every P-reading, whatever its own manifest validity says. That includes the cells completed before the sentinel, which the sentinel lists in family_runs_at_stop. The launcher never rewrites an earlier manifest.")
- *V2-6* #s("Executed-code integrity. A cell is INVALID (infrastructure) unless its manifest carries a code_tree block showing three things. (a) A pre-gate and a post-cell scan of code/ found no entry outside CODE_TREE_ALLOWLIST: no __pycache__, .pyc, .so, symlink, hidden or other file at any depth. (b) Every allow-listed file re-hashed after the cell equals its value at the gate. (c) Each third-party module the launcher imported (at least numpy, yaml and pytest's location for the self-test) resolved outside code/.")
- *Approval records v2.1:* the approval decision records the TASK-20261106-dfd0ed snapshot commit instead of 5c1258, with the per-file sha256 of the seven CODE\_FILES and both test files, code\_sha256, the sha256 of CODE\_TREE\_ALLOWLIST, EXPECTED\_KAT\_ITEMS and DESIGNED\_SKIPS. The five-field lock and the code\_sha256 definition are unchanged; the 72f51766a6 and 9a0b5955 bytes stay history.

*DEV-1 budget and placement* (#s("dev1_decision_v2")). The cell is exactly the FX-16 cell in tests/test\_kat\_extended.py at 9a0b5955 (sha256 79894702...06b5), unmodified: #s("F_{q''^2}") with q'' = 10,007, KAT curve seed #s("kat|large|10007|2|m3"), line base (B = 9,886), m = 3, s = 50, a kernel-free pair-sum membership method, guard of 25 or more of 50 nonzero; non-contract, KAT mode. Budget 43,200 s wall and 16 GB; go threshold a measured projection of at most 39,600 s; the projection step limited to 1,200 s; the cell watchdog fires 41,400 s after the full cell starts (1,200 + 41,400 = 42,600 s, within 43,200 s). It runs as a separate executor task (96fee7) after the fix task 2b7223 and on its final bytes, on an otherwise idle host, and before the single snapshot dfd0ed that binds the fixed code and the DEV-1 record. Outcomes: passed (all 50 pairs equal, guard met, multiset count equals C(B+2, 3)); mismatch (an instrument finding on the kernel's m = 3 large-q path, recorded verbatim, never re-run; B1 reopens; the queue stops after dfd0ed); stopped or infrastructure (DEV-1 stays open; the queue stops after dfd0ed; the cell is never shrunk).

*Rate correction* (#s("dev1_rate_correction")). DEC-20261106-843cf7 put the exact (32779, 2, m = 3) cell at about 6e12 multisets and about 17 h, implying about 1e8 multisets/s, and the substitute at well under 4 h. Neither agrees with the arm-C calibration that record cited: throughput-calibration.json armC (n = 2, m = 2) records 537,739,615 multisets in 78.65 s, about 6.8e6/s, and the measured m = 3 rates (4c4831 SF-1 about 4.8e6/s; 7c2b01 4.6e6 to 5.0e6/s) fit it. *The error was the predecessor Coordinator act's arithmetic, not a calibration or kernel defect.* The 14,400 s FX-16 stop is therefore a budget-setting error and an infrastructure outcome, not a KAT failure and not evidence. At the measured rate the exact cell is about 1.2e6 s and stays unrun. The approval act compares the DEV-1 measured (n = 2, m = 3) rate with the arm-C model before setting the arm-C watchdogs (SC-3); B7 stays cleared.

Blockers after this act (#s("updated_blockers")): B1 open (narrowed: FX-16 cell not run; no KAT kills M6), B2 open (determinism confirmed again), B3 cleared, B4 open, B5 open, B6 open, B7 cleared, B8 open (failed twice). Figure 1 (last page) draws the composition.


== Limitation
- *L-2 (N-6):* stands as written in DEC-20261106-843cf7, with its trigger (a successor plan with a B2 instance above 10^4 subsets). Unreachable in this plan; not an invalidation or hardening finding of the 7c2b01 round. No other limitation is recorded in this round.
- *Session-only independence:* 7c2b01 and 941825 are independent between sessions only, not between models (resolved model claude-opus-5-5, model\_verified false). This is not a rule-12 round and nothing here triggers rule 12. 941825's blindness is lifted deliberately for the 165da2 code\_review.md and the 7c2b01 fix\_review.md; it reads neither attestation and no producer session.
- *KAT-field scope:* every mutant, attack and DEV-1 check runs on KAT fields; contract-scale behaviour is inferred from identical code paths. The DEV-1 cell checks a code path, not a contract configuration; the exact (32779, 2, m = 3) cell stays unrun.
- *Receipts not authenticated:* receipts and the code\_tree block are not cryptographically authenticated. A fully self-consistent forgery inside the experiment directory remains possible by deliberate fabrication; it is checkable after the fact, because receipt, junit and code\_tree bytes are archived with every cell. A file planted in code/ after the pre-gate scan and removed before the post-cell scan is outside what a launcher can see (residual scope, not a finding).
- From #s("scope_and_limitations"): the composing act ran no tool and computed no hash (merge state, PR numbers, commit ids and the reviewer's measurements are as reported; 779e02 re-checks what it can); toy tier throughout, with KN-OPEN-62c870 CS-D2 and CS-R7 binding every later citation.
- This report re-ran nothing: figure-data.json copies values by key or by section and table, and figures.py derives only layout and labels.

== Next actions
BATCH-a8825c (#s("coordination/goals/GOAL-PATH-001/batches/BATCH-a8825c/dispatch_queue.json")), max\_concurrent 1, strictly in sequence, zero runs:
#table(columns: (0.25fr, 1.25fr, 0.75fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*\#*], [*task*], [*role*], [*work*],
  [1], [TASK-20261106-d5063d], [coordinator], [#s("This act (completed on writing; archived by 779e02).")],
  [2], [TASK-20261106-779e02], [coordinator], [#s("Ledger archive of this act, ALONE; closes lane BATCH-69d9a2; pins the 2b7223 and 96fee7 inputs; checks OC-1 to OC-6.")],
  [3], [TASK-20261106-2b7223], [executor], [#s("executor-implementation: HX-1 to HX-10; launcher.py, tests/test_kat.py and README.md only; tests that fail on the 9a0b5955 code; M6 killed; zero contract cells, zero runs; archived by dfd0ed.")],
  [4], [TASK-20261106-96fee7], [executor], [#s("executor-implementation: the DEV-1 FX-16 cell, unchanged, on the 2b7223 bytes; 43,200 s and 16 GB; KAT mode, non-contract; host otherwise idle; zero runs; archived by dfd0ed.")],
  [5], [TASK-20261106-dfd0ed], [coordinator], [#s("ONE snapshot of 2b7223 and 96fee7, alone among commit tasks; re-binds code_sha256. If the DEV-1 outcome is not passed, the queue stops here.")],
  [6], [TASK-20261106-941825], [validator], [#s("review-adversarial, fresh independent session: focused re-review RR-1 to RR-8 on the dfd0ed commit; re-runs the .pyc and __pycache__ attacks; kills M6 by its own run; kernel-free membership check on at least 10 logged DEV-1 targets; archived by afbe9b.")],
  [7], [TASK-20261106-afbe9b], [coordinator], [#s("Snapshot of 941825, alone among commit tasks.")],
)
- *NA-1* (coordinator, shell-holding top-level session; exactly one next action): commit the BATCH-a8825c queue alone, render it and open lane BATCH-a8825c; render this report and push report.pdf to the artifact store; run 779e02 alone, push, refresh the ready-for-review PR with auto-merge, and close lane BATCH-69d9a2; then dispatch 2b7223, with 96fee7, dfd0ed, 941825 and afbe9b following in queue order.
- *Declared successor* (after afbe9b verifies with B8 cleared; not an additional next action): a fresh Coordinator approval act as DEC-20261106-843cf7 NA-1 declared, with SC-1 (the v2 amendment carries V2-1 to V2-6), SC-2 (approval\_records\_v2\_1 names the dfd0ed commit and its hashes) and SC-3 (compare the DEV-1 measured rate with the arm-C model; if the model is optimistic by more than 1.5x, scale the arm-C watchdogs by the measured ratio). The runbook's first step stays the launcher selftest, with a check that code/ is clean before every cell; .resume/RESUME.md is filled and pushed before any run.
- *Rerank trigger:* 941825 fails B8; a fix requires a frozen file; the regenerated plan differs from 9ccbe614...fb4a; the DEV-1 cell mismatches; or EXP-MONO-1a1be2 is not approved by 2026-12-15. A fresh act (spare DEC-20261106-24d2a2) then composes and reranks before any third fix round. The decision reads the predecessor's "two consecutive failed re-reviews" trigger as not yet fired (165da2 was the original review).

== Canonical graphs checked
None changes: no evidence record, status or knowledge entry moves. Checked and *left unchanged*:
- experiments/EXP-MONO-1a1be2/reports/review-DEC-20261106-843cf7/findings.svg and mutation-kill.svg (and that report's PDF): the previous decision report on this experiment; this report supersedes none of its values.
- experiments/EXP-MONO-1a1be2/reports/review-DEC-20261105-f0b7c7/composition.svg and split-fraction.svg (and that report's PDF): its joints and split fractions are not touched by an instrument re-review.
- knowledge/frontiers/ecdlp/: README.md and its records; the frontier holds no SVG graph, and nothing here is a cost claim.
- docs/reports/2026-10-23-idea-f15270-rescope/convention-map.svg (and its report.pdf): not canonical, not edited.
- experiments/EXP-MONO-0e6e8f/reports/review-DEC-20261022-a0f165/monodromy-frequencies.svg: an earlier decision report on the same Semaev lineage; historical, not edited.

== Provenance and rendering
Figures: figures.py (matplotlib, Agg, svg.fonttype none, svg.hashsalt DEC-20261106-475620, metadata Date None) reads figure-data.json and writes findings.svg and mutation-kill.svg byte-identically on repeat. figure-data.json names, for every value, its source: the decision (ledger/decisions/DEC-20261106-475620.yaml, sha256 d1616253...ea56), fix\_review.md sections "Result", "RR-3" and "RR-5" (sha256 52198231...2e1a, as at 573356f303), fix-report-4c4831.md section "FX-16" (sha256 8ef65bec...b282), and the HX and RR items of ledger/handoffs/TASK-20261106-2b7223.yaml and TASK-20261106-941825.yaml. PDF compiled with the Typst Python wheel in a scratch virtualenv outside the repository, and every page inspected. The PDF goes to the artifact store (tools/artifacts/artifacts.py push), not to git.

#page(flipped: true, margin: (x: 1.0cm, top: 0.8cm, bottom: 1.3cm))[
#figure(image("findings.svg", height: 16.4cm), caption: [Figure 1. Composition of the TASK-20261106-7c2b01 re-review by DEC-20261106-475620. Rows F-1, N-1 to N-5 and DEV-1 (the DEC-20261106-843cf7 must-fixes), then NF-1 to NF-7 and the receipt-clash observation: 7c2b01 status, the item in words, this act's disposition (closed and held, or must-fix with its HX id; DEV-1 by the unchanged cell under the owner's budget), and the TASK-20261106-941825 check that verifies it. Strip: blockers B1 to B8 after this act. Every edge is an instrument step, not evidence. Data: figure-data.json; regenerate with figures.py.])
]
