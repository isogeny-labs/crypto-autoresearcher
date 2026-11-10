#set document(title: "Decision report DEC-20261107-f46a40", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#set figure(numbering: none)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)
#let after(body) = block(stroke: (left: 2pt + rgb("#a86b00")), inset: (left: 6pt, y: 3pt), width: 100%)[*After this decision:* #body]
#let s(x) = x

= Decision report: DEC-20261107-f46a40
GOAL-PATH-001 · RQ-MONO-001 · EXP-MONO-1a1be2 · records the owner's answer to OQ-1 of DEC-20261106-24d2a2 (the DEV-1 allowance) · fresh act using the spare id reserved by DEC-20261106-24d2a2, triggered by the first #s("inconclusive_decision") event · composing task TASK-20261107-5b2b59 · ledger archive TASK-20261107-88b2fc · opens BATCH-342e48 · written 2026-11-07

== Status
- *No run exists.* This act launched zero runs. *DEV-1 is neither passed nor failed*; its re-attempt TASK-20261107-bc7a76 has not started.
- *Nothing is approved.* No experiment, protocol, runbook or run is approved. EXP-MONO-1a1be2 stays a review\_required draft and H-MONO-23d347 stays proposed. The standing user authorization (2026-09-06) is noted but not used: B1, B2, B4 to B6 and B8 are open.
- *OQ-1 is answered (A).* The answer grants resources for the DEV-1 instrument check and sets its scope; it is not an experiment approval.
- *bc7a76 stays blocked* until DEC-20261107-40200d dispositions every 7db1de RR-9 route and its revision moves bc7a76 to queued.
- *No evidence record is decided.* There is no EV-\* record, no RUN-\* id and no status move; no knowledge entry is promoted (#s("knowledge_promotion.promoted: []")). *No timing in this report is evidence about any prediction*; the timings are an infrastructure stop, caps and budgets.
- The decision takes effect only when the ledger archive TASK-20261107-88b2fc verifies. This is not a performance measurement: no benchmarks/ entry and no leaderboard regeneration apply.

== Decision
- *Decision:* #s("revise") (release structure of a run gate). *Claim tier:* a resource grant and a gate design; no mathematics. *Evidence strength:* none assigned (nothing was measured).
- *Scope:* (1) records the owner's answer (A) and the parts it does not cover; (2) states the bc7a76 caps: at most 2 attempts and a cumulative cap of 86,400 s for the card; (3) keeps bc7a76 blocked and splits its release off to DEC-20261107-40200d; (4) writes the B8-D DEV-1 verification TASK-20261107-af7359 (blocked) and its snapshot TASK-20261107-d279a7; (5) opens BATCH-342e48 for 5b2b59, 88b2fc, af7359 and d279a7.
- *Supersedes, in part and never in content:* DEC-20261106-24d2a2 #s("owner_questions OQ-1 on_each_answer.A") and its declared successor, only in that the act recording (A) was to move bc7a76 to queued. That move goes to DEC-20261107-40200d (#s("split_of_release")). No ordering rule changes.
- *Records:* DEC-20261107-f46a40, DEC-20261106-24d2a2, DEC-20261106-475620, TASK-20261107-5b2b59, TASK-20261107-88b2fc, TASK-20261107-af7359, TASK-20261107-d279a7, TASK-20261107-bc7a76, TASK-20261107-7db1de, TASK-20261107-971edf, TASK-20261107-eebc5b, EXP-MONO-1a1be2, H-MONO-23d347, BATCH-c077fd, BATCH-342e48.

The answer, option (A) as it was shown (#s("owner_answer.option_label_as_shown") and #s("option_text_as_shown")):
#vb[#s("(A) Re-run here (Recommended)") \
#s("Re-run here under a detached supervisor, with up to 2 attempts if restarts interrupt it: at most about 26 h of DEV-1 wall in all, or a lower cap you set. The Coordinator recommends this, falling back to (B) if both attempts are lost to restarts.")]
*The owner set no lower cap* (#s("lower_cap_set_by_owner: none")) and added no other notes.

== Observation
These are reported facts as the act records them (#s("reported_facts")); the act did not verify them.
- *RF-1, the answer as relayed:* at about 2026-11-07T02:20Z the top-level session sent OQ-1 to the owner word for word through the session's question tool, with options (A) to (D) as written in DEC-20261106-24d2a2. The owner chose (A). The composing subagent did not see the exchange and records the answer as relayed.
- *RF-2, a third restart:* the container restarted a third time during the session, adding to DEC-20261106-24d2a2 ENV-2 ("at least twice"). No restart rate is recorded.
- *7db1de running:* at the time of the act the hardening re-review TASK-20261107-7db1de was running in a fresh validator session, using the main checkout read-only as its full checkout (a recorded deviation). 971edf was queued behind it, bc7a76 blocked, eebc5b waiting on it.
- *RF-3:* two reported facts carry the same short sha, a640b9f1dd (the 7db1de claim and the merge of PR 3130); one is likely a copying slip. 88b2fc LA-2 records which commit each names. This changes nothing decided here.
- *Attempt 1 outcome word:* #s("stopped_infrastructure") (dev1-kat-log-96fee7.json #s("outcome")), unchanged since DEC-20261106-24d2a2.

#after[the hardening re-review TASK-20261107-7db1de completed with B8-H passed, and TASK-20261107-971edf archived it at commit 62361c815c (BATCH-c077fd #s("tasks_state_revisions"), 2026-11-07T03:49:45Z). Not read by this act; drawn nowhere in the figures.]

== Comparison
The original grant against the (A) bound, and the caps of the card (Figure 1). DEC-20261106-475620 encoded the owner's grant of about 10-12 h as a 43,200 s task budget for DEV-1. Attempt 1 used about 2.5 h of it (task start about 23:05Z to kill detection about 01:32Z, dev1-report-96fee7.md, about 8,820 s; approximate). Option (A) bounds DEV-1 at about 26 h in all. The card's own budget is 2 attempts of 43,200 s each (a projection of at most 1,200 s plus the 41,400 s watchdog, 42,600 s, plus 600 s of set-up); the act sets the cumulative cap at that budget, 86,400 s, so it raises and lowers nothing. With attempt 1, DEV-1 is then bounded at about 26.4 h (8,820 + 43,200 + 43,200 s = 95,220 s), which the decision reads as the "about 26 h" of (A): 2 × 42,600 s plus attempt 1 is about 26.2 h, and the rest is the per-attempt set-up margin. Both re-attempt ends (about 14.4 h and about 26.4 h) lie above the original grant.

#figure(image("dev1-allowance.svg", width: 100%), caption: [Figure 1. Cumulative DEV-1 wall under OQ-1 (A), in hours. Solid: attempt 1 (TASK-20261106-96fee7), about 2.5 h, approximate, from the task times in dev1-report-96fee7.md as DEC-20261106-24d2a2 #s("allowance_reading (a)") gives them. Dashed: the attempt 2 budget, 43,200 s (bc7a76 #s("budget.per_attempt_wall_clock_seconds")). Hatched: the attempt 3 budget, 43,200 s, allowed only after a C5 container restart ends attempt 2 (LD-8, LD-9). Dotted ticks: the 42,600 s projection-plus-watchdog limit inside each budget. Green band: the original grant of about 10-12 h (DEC-20261106-475620 #s("owner_direction")). Orange marker: "about 26 h", OQ-1 (A). Bracket: the cumulative cap of the card, 86,400 s (#s("bc7a76_caps.cumulative_cap_seconds_this_card")). A budget bound, not a measurement. Data: figure-data.json (sources by key); regenerate with figures.py.])

== Inference
These are the Coordinator's readings and design choices; none is a measurement.
- *Reading of (A):* DEV-1 may run again on this host under the bc7a76 detached supervisor, for at most two fresh attempts (attempts 2 and 3). Attempt 3 is allowed only after a container restart ends attempt 2 (C5). Not covered: option (B) itself (no dollar ceiling, CPU and RAM, deadline or retry allowance, and no runner configured); any stop other than a restart (stopped\_projection, watchdog, signalled, unexplained\_kill, crash, OOM, no\_checkpoint\_route), which gets no retry and goes to a fresh act; option (C), any code change and any change to the cell.
- *Caps (R-2):* set at the card's own budget. A cap below 86,400 s could refuse the second authorized attempt by the LD-9 rule (at least 42,600 s left) after a late restart cut the first short. Before attempt 3 at least 42,600 s of the 86,400 s must remain, counting every second attempt 2 spent. Claim TTL stays 1,560 minutes (BP-4).
- *Why bc7a76 stays blocked (R-3):* bc7a76 BP-2, on an immutable card, needs one committed and verified act to do five things. This act can do four (record the answer, name the card, state both caps, append the revision); it cannot do the fifth, "dispositions every 7db1de RR-9 route", because 7db1de had not finished and no RR-9 route existed. A disposition rule written in advance for unseen findings would not be a disposition. Moving bc7a76 to queued now would let the dispatcher list it as ready the moment 971edf completes, whatever B8-H says.
- *The split with DEC-20261107-40200d:* written after 971edf verifies, before bc7a76 is dispatched. If B8-H passed, no code/ change is requested and no RR-9 route needs a different launcher, it meets BP-2 in full (cites this act, names bc7a76, adopts the caps, dispositions every RR-9 route) and, once its own archive verifies, the BATCH-c077fd revision moves bc7a76 to queued. Otherwise it is the fresh composing act and cancels or supersedes bc7a76, eebc5b, af7359 and d279a7 as needed. No superseding card is needed for (A) itself.
- *Launch gates G-1 to G-7* (none added or relaxed): G-1 971edf verified with B8-H passed; G-2 no review finding requests a code/ change and HEAD's code/ equals the dfd0ed bytes (code\_sha256 5d5a607d...1464); G-3 40200d committed and verified, every RR-9 route dispositioned, none graded "blocks release" left unfixed, and the revision committed; G-4 bytes re-verified per attempt, before-record before the projection; G-5 RESUME filled, gate passed and pushed before every launch; G-6 an otherwise idle host; G-7 a setsid nohup launch from one short foreground command.
- *The B8-D task (R-4):* af7359 (validator, review-adversarial, fresh independent session, zero runs) carries TASK-20261106-941825 RR-5 verbatim as DV-0, with the bc7a76 file names substituted, and adds checks of attempts, the LD-8 class of each, the supervisor, the heartbeat, the cumulative cap and the SC-3 full-pass rate arithmetic. It reads the record on the eebc5b commit and never re-runs the cell. It is written blocked, and moves to queued mechanically only when the eebc5b receipt records DEV-1 outcome passed, SA-3 equal and SA-5 with no disagreement (DVP-2); any other record leaves it for the spare DEC-20261107-856d9b. B8-D clears when d279a7 archives an af7359 pass, unchanged from DEC-20261106-24d2a2 #s("b8_split.B8-D").
- *The new batch (R-5):* BATCH-c077fd changes only by archive blocks and state revisions, and tools/research\_dispatch.py refuses a depends\_on across queues, so the new tasks go in BATCH-342e48 (max\_concurrent 1). Links to 971edf and eebc5b are dispatch preconditions on the cards, and both lanes stay strictly serial.

== Limitation
- *Relayed answer:* the owner's answer reached the act as relayed text; its provenance is the top-level session's report of the question-tool exchange. The act ran no tool and computed no hash.
- *Restart rate unknown:* three restarts in one session make the chance that one attempt of about 11.8 h survives uncertain and perhaps low. No probability is stated.
- *(B) has no parameters:* the fallback needs the owner's dollar ceiling, CPU and RAM, deadline and retry allowance first; OQ-2 (optional, non-blocking) asks for them early.
- *Session-only independence:* af7359 and 7db1de are independent of the producers between sessions only, not between models. This is not a rule-12 round.
- *Scope:* toy tier throughout; KN-OPEN-62c870 CS-D2 and CS-R7 bind every later citation; L-2 (N-6) stands as in DEC-20261106-843cf7.
- *This report re-ran nothing:* figure-data.json copies values by key; its few sums (attempt 1 task wall, cumulative ends, grant band and the 26 h marker in seconds) are written out there with their derivation.

== Next actions
- *NA-1* (coordinator, shell-holding top-level session; exactly one): (1) commit the BATCH-342e48 queue alone, push, render it ready-only (`--ready-only`), open the lane and push RESUME; (2) when 7db1de releases, run 971edf alone, then render this report and run 88b2fc alone, push, and open or refresh the ready PR with auto-merge; (3) have DEC-20261107-40200d written from the committed 971edf receipt.
- *Declared successor* (not an additional next action): DEC-20261107-40200d. Then bc7a76 and eebc5b, then the af7359 revision, af7359 and d279a7, then the approval act with SC-1 to SC-5 (Figure 2). Spare DEC-20261107-856d9b is held for any non-passing bc7a76, eebc5b or af7359 outcome, including (B).
- *OQ-2* (open, optional, non-blocking): the (B) parameters, recorded only by a committed act.

#after[the release step for bc7a76 goes to DEC-20261107-40200d.]

Blockers after this act (#s("updated_blockers")): B1 open (the re-attempt has the allowance and waits on B8-H and the RR-9 disposition); B8 open, split into B8-H and B8-D, with B8-D now a written task (af7359); B2 to B7 as in DEC-20261106-24d2a2.

== Canonical graphs checked
None changes: no evidence record, status or knowledge entry moves. Checked and *left unchanged*:
- experiments/EXP-MONO-1a1be2/reports/review-DEC-20261106-24d2a2/dev1-attempt-timeline.svg and queue-and-gates.svg (and that report's PDF): the previous decision report; its panel B already drew the (A) bound as two 42,600 s attempts, and Figure 1 here adds the card's 43,200 s budgets and the cap.
- review-DEC-20261106-475620, review-DEC-20261106-843cf7 and review-DEC-20261105-f0b7c7 figures and PDFs: historical, not edited.
- knowledge/frontiers/ecdlp/: nothing here is a cost claim.

== Provenance and rendering
Figures: figures.py (matplotlib, Agg, svg.fonttype none, svg.hashsalt DEC-20261107-f46a40, metadata Date None) reads figure-data.json and writes dev1-allowance.svg and release-gates.svg byte-identically on repeat. figure-data.json names, for every value, its source file and key, and lists each source with its sha256 (the decision b22077df...e99f; DEC-20261106-24d2a2; DEC-20261106-475620; the 96fee7 report and kat log; both dispatch queues; the 5b2b59, 88b2fc, af7359, d279a7 and bc7a76 cards). PDF compiled with the Typst Python wheel in a scratch virtualenv outside the repository, and every page inspected. The PDF goes to the artifact store, not to git: report.pdf is pushed through tools/artifacts/artifacts.py push, run by the top-level session, with its manifest in .artifacts.json.

#page(flipped: true, margin: (x: 1.0cm, top: 0.8cm, bottom: 1.3cm))[
#figure(image("release-gates.svg", width: 100%), caption: [Figure 2. Release chain after DEC-20261107-f46a40, as at the decision. Row 1: 7db1de (running), 971edf [gate B8-H], 88b2fc (this act's archive), DEC-20261107-40200d [RR-9 disposition, then the bc7a76 revision], bc7a76 (blocked) [launch gates G-4 to G-7]. Row 2: eebc5b, the af7359 revision (eebc5b: passed, DVP-2), af7359 (blocked), d279a7 [gate B8-D], the approval act (SC-1 to SC-5). Side branches: from 971edf, "B8-H fail or code change -> 40200d as a fresh act"; from bc7a76, "both attempts C5 -> (B), with owner parameters (856d9b)" (#s("release_status.split_of_release"), #s("bc7a76_caps.fallback_on_retries_exhausted")). Every edge is labelled "instrument, not evidence". Data: figure-data.json; regenerate with figures.py.])
]
