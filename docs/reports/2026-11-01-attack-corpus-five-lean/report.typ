#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 8.8pt)
#set heading(numbering: "1.")
#set par(justify: true, leading: 0.58em)

= Five cryptographic-assumption boundaries in Lean

_Review opened 2026-11-01; correction round completed 2026-11-02._

#block(fill: rgb("#eef3fa"), stroke: rgb("#34527a"), radius: 4pt,
  inset: 8pt, width: 100%)[
  *Scoped result.* Five finite countermodels/controls and their repaired
  premises are present in Lean. Five separately assigned semantic reviewers
  attest `holds`; four first-round audit findings were corrected and
  re-reviewed. Corrected head `0e096a9d98` passed the exact Lean 4.35 full
  workspace build, all-target named-declaration verifier, project axiom audit,
  forbidden-construct checks, and dependency-pin checks (Actions run
  `41365419446`).
]

#figure(
  image("proof-boundary.svg", width: 100%),
  caption: [Each red inference is too broad; blue is the finite control,
  green is the repaired mathematical premise, and amber is the implementation
  or security bridge that remains unproved.],
)

== What Lean establishes

#table(
  columns: (25mm, 1fr, 1.08fr),
  inset: 4pt,
  stroke: rgb("#cbd5e1"),
  table.header([*Joint*], [*Countermodel / control*], [*Repair*]),
  [`MOD-ALIAS`], [Distinct naturals `0,q` alias in `ZMod q`.],
    [Both natural representatives are `< q`; sharp boundary is `0 < q`.],
  [`BATCH-RLC`], [`e0(rho)=-rho`, `e1(rho)=1` cancel for every challenge.],
    [A fixed nonzero coefficient pair accepts at most one field challenge.],
  [`POLY-FUNCTION`], [`X^2-X != 0` over `F_2`, yet evaluates to zero.],
    [Univariate `natDegree P < |F|` plus pointwise zero implies `P=0`.],
  [`SUBGROUP`], [`(1,0)` lies outside the image `(0,s)` and has order two.],
    [Image membership supplies a scalar; nonzero image points have order three.],
  [`SCHNORR-SS`], [Equal challenges give no extraction; a nonzero composite-ring difference may be a nonunit.],
    [Same commitment, distinct challenges, and prime scalar field give the quotient extractor.],
)

The theorem types do not mention a circuit, curve decoder, commitment scheme,
random oracle, extractor runtime, or security game. Consequently no named
implementation vulnerability, ECDLP attack, or hardness conclusion follows
without a separate checked refinement.

#pagebreak()

== Evidence and adversarial review

The initial producer is `f5a8f8ac8c`; corrected producer
`37cc75cfebb`; correction plan `0e096a9d98`. Specs were not edited. The
workspace pins Lean `v4.35.0` and Mathlib
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.

The 4.34.1 compatibility proxy elaborated the five final modules. Final focused
target/verifier tests pass 340/340; all five specs validate; the generated
root is current; forbidden-construct scans are clean. The proxy is explicitly
not the pinned machine receipt. The exact run's formal-workspace job and
receipt-upload step both completed successfully; the accompanying machine
record binds run, job, artifact, source hashes, and trust limits.

Five separate reviewers first derived their assigned mathematics from the
frozen spec and matching source subsection, then inspected only that proof.
All return `holds`. Their attacks exposed and the correction round resolved:

- non-tight modular scope (`2 <= q` versus the sharp `0 < q`);
- batching and polynomial repairs adjacent to, not inside, the audited name;
- a composite-ring Schnorr control that had not stated `0 != 2` explicitly.

Procedure limit: reviewers were separate collaboration sessions, not durable
`TASK-*` handoffs; the Markdown plan is not accepted by the mechanical
independence checker; all sessions use one model family. This packet changes
no official ledger, hypothesis, experiment, or goal status.

== JKSST and hardness boundaries

This tranche does not supply an exact Mordell--Weil height-ball count from
rank/radius/minimum, prove the selected-lift height/discriminant comparison,
prove Lang's conjecture, or turn “approximately `(2 C2)^r/p`” into a theorem.
Those need distinct statements and interfaces. A marginal one-shot bound also
does not imply independent or geometric repetition.

DLP, CDH, q-SDH, ROM, AGM, and QROM are open computational assumptions or
model-relative statements, not unconditional propositions refuted by these
finite controls. The rigorous skeptical task is to formalize their games,
reductions, encodings, and loss factors.

== Recommended next five

1. `ONE-SHOT-HISTORY`: correlated-trial countermodels; repair with a uniform
   conditional-hazard recurrence. This is the direct JKSST priority.
2. `CUBIC-EVAL-RANK`: ten collinear points do not give ten independent cubic
   conditions; repair with a full-rank evaluation-matrix premise.
3. `COFACTOR-PUSHFORWARD`: exact image/fiber/uniform-pushforward counts under
   a proved group decomposition and scalar actions.
4. `FS-ZERO-HASH`: constant-zero Fiat--Shamir countermodel, explicitly short
   of a ROM/QROM forking theorem.
5. `PEDERSEN-RELATION-KERNEL`: alternate openings from a known generator
   relation; computational binding remains an assumption/game theorem.

Full statements, hashes, review reports, missing bridges, and links to proof
sources are in the accompanying `README.md`.
