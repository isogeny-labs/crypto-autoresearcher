#set document(title: "Decision report DEC-20261105-f0b7c7", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 1.8cm, y: 1.8cm), numbering: "1 / 1")
#set text(size: 9pt)
#set par(justify: false, leading: 0.58em)
#show heading.where(level: 2): set text(size: 10.5pt)
#set figure(numbering: none)
#let vb(body) = block(fill: luma(244), inset: 6pt, radius: 3pt, width: 100%, body)
#let s(x) = x

= Decision report: DEC-20261105-f0b7c7
GOAL-PATH-001 · RQ-MONO-001 · EXP-MONO-1a1be2 · composes REVIEW-PATH-20261029-3ac467 (TASK-20261029-3ac467, snapshot TASK-20261029-fe6c9d at 618e0c81d5) · composing task TASK-20261105-18a59d · ledger archive TASK-20261105-c0d167 · opens BATCH-8517aa · 2026-11-05

== Status
- *No run exists.* This act launched zero runs; no contract cell of EXP-MONO-1a1be2 has been counted.
- *No evidence record is decided.* There is no EV-\* record, no RUN-\* id and no status move: H-MONO-23d347 stays proposed, EXP-MONO-1a1be2 stays a review\_required draft, and no knowledge entry is promoted (#s("knowledge_promotion.promoted: []")).
- The decision takes effect only when the ledger archive TASK-20261105-c0d167 verifies. It approves no experiment, protocol, runbook or run.
- This is not a performance measurement: no benchmarks/ entry and no index-calculus leaderboard regeneration apply.

== Decision
- *Decision:* #s("revise"). Option (b): keep EXP-MONO-1a1be2 review\_required with the updated blocker list, and open BATCH-8517aa with six tasks.
- *Claim tier:* derivation, toy corroboration. *Evidence strength:* none assigned (a composition of a derivation review is not evidence; rationale R-6).
- *Scope (decision\_scope, condensed):* (1) composes REVIEW-PATH-20261029-3ac467: every joint holds, J2, J3 and J4 with refinements, none broken, so B3 clears without a version-2 amendment for a broken joint; (2) pins the predictions to freeze: P1 to P8 unchanged in value, plus three exact identities and three reported quantities, written before any contract cell exists; (3) F-1: requires a pre-approval KAT extension; (4) F-2: requires a measured throughput on non-contract proxy cells (a compiled B1 port only under TP-1); (5) chooses option (b); (6) writes the BATCH-c53152 checkpoint and closes that lane after c0d167 verifies. The committed specification is not edited (v1 draft, sha256 d81a85b3...c373, bound at 26a72871e7).
- *Records:* DEC-20261105-f0b7c7, DEC-20261029-71d757, REVIEW-PATH-20261029-3ac467, TASK-20261029-3ac467, TASK-20261029-fe6c9d (618e0c81d5), TASK-20261029-02a714 (f4a5347a84), EXP-MONO-1a1be2, H-MONO-23d347, IDEA-20261023-f15270, BATCH-c53152, BATCH-8517aa, KN-OPEN-62c870.

== Observation
The blind re-derivation TASK-20261029-3ac467 (one validator session, zero experiment runs, corroboration in computations.json, step ids in brackets) re-derived the producer's lemmas L1 to L6 and L8 as joints J1 to J5. Per-joint statements and the composed verdict, from the decision's #s("composition.joints"):

#table(columns: (0.35fr, 1.6fr, 2.3fr, 0.8fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*joint*], [*producer statement*], [*re-derived statement*], [*composed*],
  [J1], [#s("L1 sum over R of T_A = B^n; L2 ratio B^n/C(B+n-1,n) = n!/prod(1+i/B), bracketed in [n! exp(-n(n-1)/(2B)), n!]; multinomial form of T_A; baseline slice C(q+n-1,n)/q^n.")], [#s("Identical statements, including the bracket and the multinomial form. Also derived: the expansion n!(1 - n(n-1)/(2B) + O(n^4/B^2)), the lower bound n!(1+(n-1)/B)^(-(n-1)), and that B = q is the card's specialisation, not an identity.") \[q1\_conservation\]], [holds],
  [J2], [#s("L3 T_S(R) = sum over ordered tuples with sum R of 2^j for 2R != O; L4 T_M - T_X supported where x(R) is a multiple root; n = 2 counts at O; cancellation-free count.")], [#s("The same statements and values, plus (a) T_S(R) = sum 2^t(P) at every target in the sign-vector convention (class count halves on G[2]); (b) T_M - T_X = sum (a(Xi,R) - 1)_+ exactly, at most sum (mult - 1)_+, equality on simple Xi; (c) at n = 2 with 2R != O, T_M(R) = T_X(R).") \[q2\_counts\]], [holds, refined (a to c)],
  [J3], [#s("L5 c <= min(1, mu_M), c >= mu^2/E[T^2]; no base exceeds rate C(B+n-1,n)/N; Poisson-null ceilings 0.346, 0.119, 0.030, 0.006 (n = 2..5).")], [#s("The same bounds and the same four ceilings to three decimals, plus (a) every symmetric base obeys the strictly lower ceiling c <= min(1, mu_sym); (b) the Poisson table is a large-B model; at small B random symmetric bases fall below 1 - exp(-mu).") \[q3\_coverage\]], [holds, refined (a, b)],
  [J4], [#s("L6 generic complete-split probability 2^(1-n)(1 + O(n/sqrt Q)); 1 on the factor-base locus; exact over proxy 2^(n-1).")], [#s("Leading value 2^(1-n); exactly 1 on the locus. Exact form P_split = 2^(1-n)(1 + eta) - (t/Q)^n + delta, relative error O(n^2/Q) + O(n^2 2^n/Q^2); M_n = (p_+ + p_0)^n + (p_- + p_0)^n - p_0^n; a mixed nondegenerate tuple never splits; exact over proxy (1 - zeta)/P_split, leading value 2^(n-1).") \[q4\_split, q4b\_mixed\]], [holds, refined (sharper error term; zeta correction)],
  [J5], [#s("L8 2^(n-1) = q^Theta(1) forces n = Theta(log q); the gain changes log_q(1/rate) by the relative amount ln 2/(ln n - 1) -> 0.")], [#s("log_q(n!) = Theta(log log q), log_q(2^(n-1)) -> c; relative change -ln 2/(ln n - 1)(1 + o(1)) -> 0; the exponent class and its leading constant c/ln 2 are unchanged.") \[q5\_asymptotics\]], [holds (sign is a convention)],
)

Proves-too-much objects (#s("composition.proves_too_much")):
- *O1 passes.* The cap allows coverage up to min(1, mu); a non-symmetric base attained mu. A greedy symmetric base beat matched random bases, at 1.116 and 1.243, while staying below its ceiling.
- *O2 passes.* The locus split probability is 1, not the generic value.
- *O3 passes.* For D' (one point per pair), T\_S depends only on X and differs from T\_A'. The T\_M - T\_X identity is stated to need D = -D.
- *O4 passes.* Every factor is 1 at n = 1.

Figure 1 (page 3, landscape) draws this composition. Figure 2 (below) plots the recorded generic split fractions behind J4: all 22 rows of computations.json step q4\_split Part A, copied by key into figure-data.json (row ids A0 to A21 are the Part A list indices). In every row the split fraction equals the recorded all-equal fraction plus the recorded delta; in every exhaustive row the all-equal fraction equals the recorded exact M\_n; every row with t = 0 records delta = 0; every row records 0 Frobenius-rule failures. The two n = 4 exhaustive rows in the Q4 table of blind\_rederivation.md (F\_13, 28,561 tuples; F\_(5^2), 390,625 tuples) come from step q4b\_mixed, not from Part A, and are not plotted.

#figure(image("split-fraction.svg", width: 100%), caption: [Figure 2. TASK-20261029-3ac467 q4\_split, Part A, all 22 rows: measured complete-split fraction of the fibre for generic tuples (blue: all nonzero chi equal; orange stack: measured delta, labelled where nonzero), against the recorded exact M\_n (diamond) and the leading value 2^(1-n) (bar). Error bars: one binomial standard error on sampled rows, derived for display from the recorded fraction and tuple count; exhaustive rows carry none. Toy fields: Q <= 529 in Part A, at most 1,953,125 tuples per row (the decision's caption specification writes "Q <= 1,953,125", the largest tuple count); none is a contract cell; no new computation.])

#page(flipped: true, margin: (x: 1.4cm, y: 1.4cm))[
#figure(image("composition.svg", width: 100%), caption: [Figure 1. Composition of REVIEW-PATH-20261029-3ac467 by DEC-20261105-f0b7c7. Rows J1 to J5: producer lemma (short label, no formula), blind re-derivation step Q1 to Q5 with its computations.json step ids, composed verdict (blue: holds; orange: holds, refined, with the refinement named). The proves-too-much objects O1 to O4 all pass. The side box lists the three predictions added before any data: P2(vii) and P2(viii) from J2, P2(ix) from J3. Every edge is a derivation (re-derived), not a measurement. Data: figure-data.json; regenerate with figures.py.])
]

== Comparison
Against the recorded prior (#s("composition.verdict_against_prior")):
#vb[#s("This concurs with the recorded prior (about 0.6 that every joint holds as stated; about 0.85 that no joint breaks in a way that changes a provisional value). No provisional value changes. The prior's most likely break did not occur, and its specific expectation for J4 was met. A concurrence with a written prior informs less than an overturn would, but it is recorded as such, not as a vote.")]
- *J2:* the prior named L4 as the most likely break in the round (about 0.75). It did not break.
- *J4:* the prior expected exactly the sharper error term, O(n^2/Q) relative, as a refinement, not a break. The leading value is the same; the zeta correction is O(1/|X|).

== Inference
*B3 clears* when TASK-20261105-c0d167 verifies. No version-2 amendment is needed for a broken joint; the final specification still differs from v1 by the additions below, which the approval act writes as a protocol\_amendment.

*Predictions to freeze* (recorded before any contract cell exists; first recorded in the decision; never changed after a run):
- Unchanged in value and tolerance: P1, P2 (i) to (vi), P3, P4, P5 (a) to (c), P6, P7, P8.
- Provenance upgrade: P2 now cites IDEA-20261023-f15270 L1 to L4 as independently re-derived by TASK-20261029-3ac467; P5 adds the L6 leading value and conditional comparator re-derived in Q4.

#table(columns: (0.55fr, 2.4fr, 1.2fr, 1.1fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*prediction*], [*source*], [*decisive*],
  [P2(vii)], [#s("T_S(R) (code convention) equals the sum over ordered point tuples with sum R of 2^t(P) at every target, including O and E[2]; reported as the count of skipped targets with nonzero residual; predicted 0.")], [TASK-20261029-3ac467 Q2], [yes (C-identities; failure in a valid cell is F7)],
  [P2(viii)], [#s("n = 2 exhaustive cells, every target with 2R != O: T_M(R) = T_X(R); count of exceptions predicted 0.")], [Q2 corollary], [yes (C-identities; F7)],
  [P2(ix)], [#s("Per exhaustive cell and base (line, matched_random, half_twin): number of targets with T_M >= 1 is at most min(N, C_sym), C_sym = [z^n](1+z)^(|X|-1)(1-z)^(-(B-t2)/2-1) with the base's own B, t2, |X|; predicted no excess.")], [Q3 item 4], [yes, as an exact bound; an excess is read under F7, never as F1],
)
Reported, not decisive: RQ-1 (per arm-A cell, min(1, C\_sym/N) over the matched-random coverage, beside P3); RQ-2 (per B1 cell, the fractions of zero, degree-deficient, non-squarefree and any-chi-zero tuples, as the scale of the P5(b) conditioning gap); RQ-3 (the J4 factor (1 - zeta)/P\_split is measured by no arm and is cited only as a derivation). Not adopted: the unconditional split fraction against M\_n + delta (R-5), and tightening F1 to min(1, mu\_sym).

*F-1 and F-2.* F-1: a pre-approval KAT extension (TASK-20261105-ac5ad6 KX-1 to KX-5) on cells disjoint from every contract cell, with IM-3 widened. F-2: a timing-only throughput measurement on non-contract proxy cells (TP-0); if one B1 cell of 10^6 tuples projects past 24 h, the approval act opens a compiled-B1-port task instead (TP-1); otherwise every per-arm watchdog is 3x the measured projection (minimum 1 h).

Updated blockers (#s("choice.updated_blockers")):
#table(columns: (0.3fr, 0.8fr, 2.2fr, 2.2fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*id*], [*status*], [*text*], [*clears when*],
  [B1], [open (narrowed)], [#s("Instrument exists (02a714; 177 KATs after #2707). Remaining: F-1 widened KATs and the composition residuals (P2(vii)-(ix)).")], [#s("TASK-20261105-7083a8 verifies with the full KAT suite passing, and TASK-20261105-49716d verifies with no unresolved blocking finding from TASK-20261105-165da2")],
  [B2], [open (narrowed)], [#s("Launcher and generator exist; the regenerated plan must be byte-identical to, or a recorded successor of, the 9ccbe614...fb4a preview.")], [#s("the approval act binds trial_plan_sha256 of the plan regenerated from the 7083a8 code")],
  [B3], [cleared], [#s("Composed here: every joint holds, three refined; additions pinned in predictions_to_freeze.")], [#s("TASK-20261105-c0d167 verifies")],
  [B4], [open], [#s("protocol.json not written")], [#s("approval act: validate and freeze, hash bound in execution_plan.protocol_hashes")],
  [B5], [open], [#s("no runbook or mechanical card")], [#s("approval act: experiment-director compile, LINT OK, then CARD OK")],
  [B6], [open], [#s("no preapproval packet or run handoff")], [#s("approvable true on the exact prospective bytes; after the approval archive, execution_state ready")],
  [B7], [open (new)], [#s("throughput measured, watchdogs set (F-2)")], [#s("throughput-calibration.json in the 7083a8 snapshot, and TP-1 not triggered")],
  [B8], [open (new)], [#s("independent code review of the final code")], [#s("the 165da2 report is archived by 49716d with no blocking finding left unresolved")],
)

== Limitation
From #s("composition.limitations_of_the_round"):
- PD-2: one re-deriver owned all five joints and the control. There is no second reviewer.
- PD-1: the blind-history check is UNCHECKABLE, never passed. Hygiene is attested by the reviewer and by the commit messages of the archives.
- Independence is between sessions only, not between models: the producer, the re-deriver (self-reported claude-opus-5-5, model\_verified false) and the composing session share one model id. This was not a rule-12 round, and nothing here triggers rule 12.
- Corroboration covers toy fields only (counting up to Q = 961, splitting up to Q = 1,953,125, n <= 4 computed). Semaev's theorem was not read. The T1 transfer of KN-FIND-4f0d84 is corroborated over F\_(p^2) and F\_(p^3) at small p, not at contract scale.
- Convention note: the card's T\_S counts sign classes with sums in {R, -R}, the code's T\_S counts sign vectors with sum R; they agree on 2R != O and differ by exactly a factor of 2 at R in E[2]. T\_X is the same in both.
- P2(iv)'s multiple-root clause is not tested by arm A, which builds no fibre at n >= 3; it rests on J2 (10,011 multiplicity checks) and the arm-B group-law cross-checks.
From the decision's #s("scope_and_limitations"): the composing act ran no tool and computed no hash; computations.json was not re-run; toy tier throughout, with KN-OPEN-62c870 CS-D2 and CS-R7 binding every later citation. This report likewise re-ran nothing: figure-data.json copies values by key, and the only derived display quantity is the binomial standard error in Figure 2.

== Next actions
BATCH-8517aa (#s("coordination/goals/GOAL-PATH-001/batches/BATCH-8517aa/dispatch_queue.json")), max\_concurrent 1, strictly in sequence, zero runs in every card:
#table(columns: (0.25fr, 1.25fr, 0.75fr, 3fr), stroke: 0.4pt + luma(200), inset: 3.5pt,
  [*\#*], [*task*], [*role*], [*work*],
  [1], [TASK-20261105-18a59d], [coordinator], [#s("This act: compose REVIEW-PATH-20261029-3ac467, decide F-1/F-2, pin predictions, open BATCH-8517aa, checkpoint BATCH-c53152 (completed on writing).")],
  [2], [TASK-20261105-c0d167], [coordinator], [#s("Ledger archive of this act, ALONE, checking OC-1 to OC-6; then close lane BATCH-c53152.")],
  [3], [TASK-20261105-ac5ad6], [executor], [#s("Widen KATs to n = 4..7 and large-q fields, add composition residuals P2(vii)-(ix), arm-C KAT refusal, timing-only throughput calibration.")],
  [4], [TASK-20261105-7083a8], [coordinator], [#s("Snapshot of ac5ad6, alone among commit tasks; records code_sha256 for the approval lock.")],
  [5], [TASK-20261105-165da2], [validator], [#s("Independent code review (review-adversarial, fresh session) of the 7083a8 bytes, CR-1 to CR-7.")],
  [6], [TASK-20261105-49716d], [coordinator], [#s("Snapshot of the 165da2 review, alone among commit tasks.")],
)
- *NA-1* (coordinator, shell-holding top-level session): commit the BATCH-8517aa queue alone and open its lane; render this report; run c0d167 alone, push, open or refresh the ready-for-review PR, and close lane BATCH-c53152; then dispatch ac5ad6.
- *Declared successor* (after 49716d verifies; not an additional next action): a fresh Coordinator approval act applies TP-1, writes the v2 amendment and preview with the predictions to freeze, freezes protocol.json, compiles the runbook, writes the run handoff, approves only on approvable: true, writes approval.lock, and requires execution\_state ready and .resume/RESUME.md pushed before any run.
- Spare id DEC-20261105-c7974d is kept for a fresh act if OC-1 to OC-6 fail or a snapshot stops on an expected-path mismatch.

== Canonical graphs checked
None changes: no evidence record, status or knowledge entry moves. Checked and *left unchanged*:
- knowledge/frontiers/ecdlp/: README.md and the records that mention Semaev or summation polynomials (KR-RHO-53c89f; KR-IC-310345, KR-IC-139da0, KR-IC-aaf521, KR-IC-58213c, KR-IC-889857, KR-IC-1fcdbc, KR-IC-5a43e5, KR-IC-5765d2). The frontier holds no SVG graph; nothing here is a cost claim.
- docs/reports/2026-10-23-idea-f15270-rescope/convention-map.svg (and its report.pdf): not canonical, not edited.
- experiments/EXP-MONO-0e6e8f/reports/review-DEC-20261022-a0f165/monodromy-frequencies.svg: an earlier decision report on the same Semaev lineage; historical, not edited.
- experiments/EXP-MONO-1a1be2/ had no earlier report directory; this is its first.

== Provenance and rendering
Figures: figures.py (matplotlib, Agg, svg.fonttype none, svg.hashsalt DEC-20261105-f0b7c7, metadata Date None) reads figure-data.json and writes composition.svg and split-fraction.svg byte-identically on repeat. figure-data.json names, for every value, its source key: #s("steps[id=q4_split].raw_output.A_generic[i]") of computations.json (sha256 4bd25ec6...3832; q4\_split raw\_output sha256 862cb19c...c1d7), or the decision path in ledger/decisions/DEC-20261105-f0b7c7.yaml. PDF compiled with the Typst Python wheel in a scratch virtualenv outside the repository, and every page inspected.
