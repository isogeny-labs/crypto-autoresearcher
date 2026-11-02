# Semaev D4 quotient equality and D5 refutation witnesses

- **Status:** investigating
- **Kind:** proof and verification gap
- **Affected work:** [degree-five quotient construction](../analysis/semaev-degree-five-quotient-lift/README.md), [n51 terminal attempt](../analysis/semaev-degree-five-quotient-lift/reports/n51-poly01-d5-stream-001/terminal-report.md), [proof bridge](../analysis/semaev-degree-five-quotient-lift/reports/n51-poly01-d5-stream-001/proof-bridge.md)
- **Next action owner:** Semaev fall-degree research lane
- **Last updated:** 2026-11-02

## Problem

The independent D4 checker proves `W_4(F) ⊆ ker(pi_4)` but does not prove equality. Thus a D5 quotient run that kills one cannot yet prove `1 ∈ W_5(F)` or an LFD upper bound, even on a zero-solution input.

## Evidence and uncertainty

- **Observed:** The completed n47 polynomial-00 and polynomial-03 D5 quotient jobs returned `projection_kills_one` after accepted D4 seeds and fresh zero counts. The n48 polynomial-04 local run did likewise. The frozen n51 polynomial-01 stream Job failed before a D5 output; its D4 seed recheck and zero count remain verified.
- **Derived:** If `ker(pi_4)=W_4(F)` and the quotient construction is correctly executed to a fixed point, its final kernel equals `W_5(F)`; see the proof bridge. This is a conditional algebraic statement, not a checked result for the named inputs.
- **Suspected explanation:** None is needed for the equality gap. The cause of the n51 pod failure is unknown because the retained Job status and log API do not identify it.
- **Missing capability:** The independent D4 rank match is now complete for n47 random00 only. That input still needs a checked D5 refutation transcript or primal witness. Other named inputs require their own D4 equality checks before applying the bridge.
- **What this evidence does not establish:** Neither `projection_kills_one` nor the interrupted n51 stream gives a degree-six lower bound or a degree-five upper bound on its own.

## What would unblock it

- [ ] On a fixed named instance, independently generate or verify `dim(B_4)-codim(pi_4)` linearly independent D4 closure rows with valid Macaulay/mutant provenance, and match their rank to the accepted quotient map.
- [ ] Independently verify the D5 relation sequence or a direct refutation witness when `projection_kills_one` occurs.

Together these conditions would prove `1 ∈ W_5(F)` for such an instance. With an already accepted `1 ∉ W_4(F)` certificate and zero count, that would give exact refutation degree five. A degree-six lower bound instead requires a positive, independently checked D5 dual certificate (or equivalent direct nonmembership proof), with codimension above the exact solution count.

## Next discriminating step

- **Action or proof obligation:** For n47 random00, independently verify a D5 primal relation that derives the constant from legal degree-five generators rooted in its now exact D4 kernel. For other killed-constant inputs, freeze separate D4 equality checks first. Implementation B previously reproduced R35a's exact D4 rank 61,425, as recorded in `results/verification.md`.
- **Inputs and controls:** Bind the n47 instance and accepted seed certificate hashes; compare B's exact rank with `dim(B_4)-codim(pi_4)`. Retain the R35a reference and a changed input rejection; independently check the declared instance and output parsing.
- **Execution limits and stop condition:** Freeze a separate resource-bounded protocol before a large run; do not repurpose the failed n51 request or launch a duplicate Job.
- **Outcomes and next actions:** A matching checked rank establishes D4 equality; a smaller rank or refused resource gate leaves equality open. A valid D5 refutation witness after equality supports an upper bound; a positive D5 dual certificate supports a lower bound only with the exact-count bridge.
- **Recheck trigger:** Completion of the independent D4 rank witness or a new D5 certificate.

## Resolution and history

Unresolved. Sources checked for this analysis: the repo's theorem dossier (Propositions 1.4–1.5), original `verify/cert_check.py`, `verify/indep_verify.py`, `results/verification.md`, `lfdclose2_rref_export.c`, quotient-lift soundness argument, and retained n47/n48/n51 result records. This record asserts no literature novelty; the dossier notes that full readings of HKY 2015 and Kousidis–Wiemers 2019 remain pending.

On 2026-11-02 the [n47 random00 independent rank replay](../analysis/semaev-degree-five-quotient-lift/reports/n47-rand00-d4-rank-equality-20261102/report.md) returned exact W4 rank 151,857 in 213,053 columns with the constant absent. The accepted D4 quotient has codimension 61,196, so its kernel dimension is also 151,857. Its checker already proved W4 containment; hence `U4=W4` for that named input. Archived output digests, frozen source/request/seed hashes, the original checker transcript and seed header were rechecked. This completes the first checklist condition for **n47 random00**, not for polynomial00/03, n48 polynomial04 or other instances. The D5 witness condition remains unmet. The earlier native `projection_kills_one` status is still not an exact upper bound.
