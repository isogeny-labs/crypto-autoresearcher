# Galbraith MPKC v2 book-scale formalization is incomplete

- **Status:** `open`
- **Kind:** proof gap; resource limit; access/tool limit
- **Affected work:** `inputs/GALBRAITH-MPKC-2018/`,
  `formal/targets/galbraith-montgomery-reduction-20261101.yaml`
- **Next action owner:** unassigned formalization campaign coordinator
- **Last updated:** 2026-11-01

## Problem

We cannot yet claim a faithful Lean translation and proof of every mathematical
object in Galbraith's 696-page v2 book: 1,817 labelled objects require
per-statement semantic transcription and triage, many are definitions,
algorithms, examples, exercises, heuristics, or conjectures rather than proved
theorems, 119 theorem-like rows have no detected in-book proof, and the official
errata page contains corrections including statements described as false or
incorrect.

The original acceptance criterion is whole-book intake plus faithful Lean
statements and proofs, with false, underspecified, conjectural, and heuristic
material classified rather than asserted. The current tranche provides a
complete labelled-object catalog and one bounded formal target; it does not
satisfy that whole-book proof criterion.

## Evidence and uncertainty

- **Observed:** The hash-pinned extractor found 1,817 distinct labels with no
  duplicate kind/label keys: 189 theorems, 231 lemmas, 46 corollaries, 3
  propositions, 4 conjectures, 8 heuristics, 213 definitions, 9 notation
  blocks, 198 examples, 26 remarks, 29 algorithms, and 861 exercises. Printed
  proof signals classify as 259 complete, 33 complete sketches, 4 unbounded,
  53 citation-only, 1 partial/omitted, and 119 absent for theorem-like objects.
  The official page yielded 47 errata items. See `catalog-summary.json` and
  `official-errata.json`.
- **Derived or proved:** Only the scoped integer core of Lemma 2.5.3 has a Lean
  target in this tranche. Its machine-verification and semantic-review states
  are recorded separately in `formalization-map.yaml`.
- **Suspected explanation:** None. The remaining work is an enumerated review
  and formalization campaign, not an unexplained mathematical failure.
- **Missing capability:** Dedicated review/proof capacity for 1,816 remaining
  rows; formal models for broad parts of algebraic number theory, curves,
  pairings, lattices, and complexity; and an IAM principal able to write the
  PDF/full catalog to the configured immutable artifact and KB prefixes.
- **What this evidence does not establish:** Missing or sketchy book proofs do
  not show that claims are false. An errata section flag is not an exact match.
  Successful Lean checking of one restatement says nothing about other rows.
  S3 access denial says nothing about the mathematics.

## What would unblock it

- [ ] Every catalog row receives a human-reviewed semantic class and a binding
  to the exact source page; multi-block mathematics is transcribed from the page
  image rather than trusted from lossy text.
- [ ] Every theorem/lemma/corollary/proposition and proof-bearing exercise is
  either machine-verified under an explicit hypothesis delta, given a checked
  counterexample/correction, or recorded as a specific unresolved proof gap.
- [ ] Definitions, algorithms, examples, heuristics, and conjectures are encoded
  with appropriate Lean types/specifications and never promoted to theorems
  merely to obtain total coverage.
- [ ] Official errata are resolved against this exact v2 PDF, and each changed
  statement preserves both the printed and corrected identities.
- [ ] A write-capable role conditionally archives the exact PDF and full JSONL
  catalog, and remote verification produces immutable receipts.

These conditions are jointly necessary for the requested whole-book claim.
They are not satisfied by catalog extraction or a high aggregate build count.

## Next discriminating step

- **Action or proof obligation:** Review and formalize the remaining Chapter 2
  theorem-like rows in source order, beginning with Lemmas 2.5.1 and 2.5.4, and
  classify their asymptotic cost model before stating them in Lean.
- **Inputs and controls:** Pinned PDF hash, official errata snapshot, one target
  per source label, explicit hypothesis-delta table, forbidden-construct scan,
  `lake build`, project axiom audit, and independent statement-fidelity review.
- **Execution limits and stop condition:** One reviewable chapter tranche per
  PR; stop on an ambiguous source formula, missing definition, or unmodelled
  complexity convention and open a row-specific problem instead of weakening
  the theorem silently.
- **Outcomes and next actions:** A verified faithful target advances that row;
  a counterexample creates a correction target; a proof gap stays open; an
  infrastructure failure changes no mathematical status.
- **Recheck trigger:** Merge of a reviewed tranche, resolution of a row-specific
  dependency, or restoration of artifact-store write access.

## Resolution and history

Unresolved. Creating this record and the first Lean target does not establish a
whole-book formalization.
