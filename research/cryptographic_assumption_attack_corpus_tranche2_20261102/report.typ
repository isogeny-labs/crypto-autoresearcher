#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 8.7pt)
#set heading(numbering: "1.")
#set par(justify: true, leading: 0.58em)

= Cryptographic assumption attack corpus: tranche two

_Statements frozen 2026-11-02; source snapshot `1b9810d54c5b11ed8030b489a5c7a5909e9864b0`._

#block(fill: rgb("#eef3fa"), stroke: rgb("#34527a"), radius: 4pt,
  inset: 8pt, width: 100%)[
  *Scope.* This packet records five exact finite countermodels or controls and
  the hypotheses that repair their overbroad inferences. At this snapshot the
  statements and formal target specifications are frozen; Lean proofs,
  machine receipts, and independent semantic reviews are separate
  deliverables. No protocol vulnerability, ECDLP algorithm, or refutation of
  a cited primary source is claimed.
]

== Five frozen boundaries

#table(
  columns: (30mm, 1.13fr, 1fr),
  inset: 4pt,
  stroke: rgb("#cbd5e1"),
  table.header([*Target*], [*Finite obstruction / control*], [*Explicit repair*]),
  [`ONE-SHOT-HISTORY`],
    [Equal one-shot marginals can have correlated or complementary histories and different survival.],
    [Supply a history-uniform survival recurrence; separately connect it to conditional events and expectations.],
  [`CUBIC-EVAL-RANK`],
    [At the ten distinct collinear points `(i,0,1)`, the nonzero cubic `Y Z^2` vanishes.],
    [A nonzero determinant, equivalently injective square evaluation map, forces zero coefficients.],
  [`COFACTOR-PUSHFORWARD`],
    [Multiplication by two collapses `ZMod 2 x ZMod 2`; the word “cofactor” supplies no uniformity.],
    [If `h` kills `K` and permutes `S`, the image in `K x S` is `{0} x S` with fibre size `|K|`.],
  [`FS-ZERO-HASH`],
    [A known constant challenge `c` accepts the constructed commitment `R=sG-cX` for every public key.],
    [Nonzero challenge gives only fixed-equation uniqueness; extraction still needs a distinct-challenge fork.],
  [`PEDERSEN-RELATION-KERNEL`],
    [If `H=alpha G`, then `(alpha,-1)` is a nonzero commitment-kernel vector.],
    [Different-message collisions reveal `alpha`; binding remains a computational hidden-relation claim.],
)

The target types deliberately stop before samplers, transcript encodings,
adversary runtimes, curve implementations, or security games. A successful
finite proof can certify only the displayed algebraic or recurrence boundary.

#pagebreak()

== Dependency map

#figure(
  image("proof-boundary.svg", width: 100%),
  caption: [Red records the overbroad inference or finite obstruction; green
  records the exact algebraic/recurrence repair; amber records a missing
  implementation or security bridge. Blue marks the JKSST source-fidelity
  correction: the paper already requires matrix rank.],
)

== Primary-source fidelity

- *JKSST.* Theorem 4.1 is a conditional one-attempt statement. A marginal
  bound alone does not establish a geometric history law. Section 3.2 already
  requires the evaluation matrix to have rank `r` for `2 <= r <= 9`; the
  ten-point collinear example is therefore a guardrail, not an erratum.
- *RFC 9380.* `clear_cofactor` places points in a target subgroup, while the
  document distinguishes nonuniform `encode_to_curve` from the complete
  near-uniform `hash_to_curve` construction and permits `h_eff != h`. The
  finite product-group count does not refute a suite.
- *Pointcheval–Stern.* The forking argument assumes a random oracle and tracks
  queries, replay, random tape/oracle prefixes, successful forks, and distinct
  challenges. A constant hash is outside that model.
- *Pedersen.* The binding boundary is already computational: setup hides the
  discrete-log relation, and different openings expose it. Literal linear
  independence of two elements in one cyclic group is not the premise.

The retrieved-source SHA-256 values and exact passages checked are recorded in
the accompanying `README.md`. This visual packet adds no independent source
attestation beyond that bound note.

#pagebreak()

== What remains outside this tranche

The finite statements do not provide:

- the JKSST selected-lift height/discriminant comparison, Lang’s conjecture,
  an exact Mordell–Weil height-ball count, or the exact probability theorem
  replacing “approximately `(2 C2)^r / p`”;
- a theorem deriving the survival recurrence from a specified adaptive
  probability space or equating its tail sum with expected waiting time;
- a concrete elliptic-curve decomposition, implementation refinement, or RFC
  suite proof for cofactor clearing;
- a ROM/QROM Fiat–Shamir theorem, forking probability, transcript parser, or
  proof-of-knowledge extractor; or
- a formal DLP reduction, adversary, runtime, or success bound for Pedersen
  computational binding.

== Bound artifacts

The source note and five target specifications are the immutable statement
inputs at commit `1b9810d54c`. Their SHA-256 values are:

#table(
  columns: (39mm, 1fr), inset: 3.5pt, stroke: rgb("#cbd5e1"),
  table.header([*Artifact*], [*SHA-256*]),
  [`README.md`], [`4834787c796eec875c33ca16ad75801c99102b31bbc565e0694311cc63b70a68`],
  [`ONE-SHOT-HISTORY`], [`454e43192383e8e38c465eca5b2d9827c844e1d3a3edef6207918bfcda9c037e`],
  [`CUBIC-EVAL-RANK`], [`23f3b80c1fce11658c833cc612620c35ea8ca65323d29e1022855344ba4acd3c`],
  [`COFACTOR-PUSHFORWARD`], [`4313d96609a4335cdab3da50a5bf3bb07cac3727f80652e312a80b26d8109ff4`],
  [`FS-ZERO-HASH`], [`212f836682b853cb679bab80583a8df748a2c25a5aa2a2b28448e6bc04944017`],
  [`PEDERSEN-RELATION-KERNEL`], [`73f3d6e4cf64f14906a113176614dcbad26431cd08d5598a70644b8f9797538d`],
)

Later proof or review packets must bind their exact Lean source hashes,
toolchain/dependency pins, named-declaration audits, axiom evidence, controls,
and hypothesis-delta tables. This source packet itself changes no ledger,
hypothesis, experiment, or goal status.
