#set page(paper: "a4", margin: 2cm)
#set text(size: 9.5pt)
#set par(justify: false)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
#show heading.where(level: 3): set text(size: 10.5pt)
= Unconventional prime-field ECDLP leads: scouting round, 2026-11-01
<unconventional-prime-field-ecdlp-leads-scouting-round-2026-11-01>
#strong[Status.] Scouting note. Nothing here is a measurement, a proof,
or a change of research state. Every heuristic is numbered and unproven.
Every proposed disposition is a proposal for the Coordinator.

#strong[Question.] Which mechanisms for prime-field ECDLP, drawn from
fields outside elliptic-curve cryptography, are absent from the lead
atlas, and what first step would decide each one?

#strong[Outcome.] Three new lead rows, two proposed amendments to
existing rows, three quick kills recorded without rows, and nine
candidates that collided with existing leads. None of the new rows is
predicted to beat matched rho. Each one carries a discriminating first
step.

#figure(image("scouting-map.svg", width: 100%), caption: [Candidates from this round and the atlas leads they cite or collide with. Atlas at b64dbdc580. Diagram only, no measured values.])

== Method
<method>
- Read the atlas at `b64dbdc580` (`origin/main`, 2026-11-01), the
  known-results map, and the standing obstruction summary used in the
  program's lead-discovery prompt.
- Searched outside fields: diagrammatic algebra and counting complexity,
  coding theory, fine-grained complexity, additive combinatorics,
  exponential sums, quantum-circuit simulation.
- Ran novelty gates N1 (`tools/lead_atlas.py --match`) and N2
  (`tools/build_frontier_map.py --match`) with at least three phrasings
  per candidate. Raw output is in `novelty-gates.txt`. The match is
  lexical, so a miss proves nothing; the top hits were read for every
  run.
- Gate N3 (ledger index) was not run in this session. The local ledger
  copy used for validation is behind `main`, so the rows cite no ledger
  records.

== New lead rows
<new-lead-rows>
=== C1. Holant view of the decomposition-count network (`LEAD-EXO-holant-decomposition-count-network`)
<c1.-holant-view-of-the-decomposition-count-network-lead-exo-holant-decomposition-count-network>
The count of m-term decompositions of a target R is a closed tensor
network over the alphabet F\_p.~Each node is the ternary tensor
`T[x,y,z] = [S_3(x,y,z) = 0]`, and each leaf carries the indicator of
the factor base FB.

Contracting one leaf gives the transfer matrix

```
M[y, y'] = #{ x in FB : S_3(x, y, y') = 0 }
```

Up to multiplicity conventions, this is the quotient by negation of the
Cayley graph of E(F\_p) with connection set {+-F : x(F) in FB}. Its
eigenfunctions are the symmetrised characters chi\_j + chi\_(-j),
indexed by the discrete logarithm. A basis that diagonalises M therefore
already encodes the answer. The open question is whether any cheaper
basis lowers the tensor rank of T.

- #strong[H1.] Entry-access contraction is simulable in the generic
  group model at O(1) group operations per entry, like the x-oracle in
  `LEAD-EXO-augmented-oracle-ggm`. Algebraic manipulation of S\_3 is not
  covered.
- #strong[H2.] The Cai-Chen complex-weighted \#CSP dichotomy is stated
  for a fixed finite domain. Here the domain grows with p, so it does
  not close the lead.
- #strong[Not a duplicate of] `LEAD-ICE-gag-contraction-planner`, which
  asks which presentation is cheapest for a Groebner solver, or of
  `LEAD-EXO-hashed-factor-base-tensor-ecdl`, which contracts a Boolean
  encoding by \#SAT.
- #strong[First step.] Prove H1. At p \<= 2^10, check the spectrum of M
  and compare flattening ranks of T under bond-wise basis changes
  against a random-support null.

=== C2. Elliptic-code decoding as a relation finder (`LEAD-ICP-elliptic-code-list-decoding`)
<c2.-elliptic-code-decoding-as-a-relation-finder-lead-icp-elliptic-code-list-decoding>
A minimum-weight codeword of the one-point code C\_L(FB, kO) vanishes at
exactly k factor-base points, and exists exactly when those points sum
to O. This is the subset-sum view behind Cheng's NP-hardness result for
elliptic code minimum distance. Zhang and Liu (KN-LIT-643) propose
finding such codewords by list decoding. The program holds the paper but
had no row for it.

- #strong[H1.] A minimum-weight codeword agrees with the zero word in
  exactly k coordinates. Guruswami-Sudan on a genus-1 code of length B
  and dimension k guarantees only agreement above about sqrt(B k), which
  exceeds k whenever B \> k. Any received-word strategy must supply the
  missing agreement, which predicts enumeration-level cost.
- #strong[First step.] Read the full Zhang-Liu text, then run it against
  k-subset enumeration at p near 2^16 with |FB| near 2^8.

=== C3. Low-degree query lower bound (`LEAD-EXO-low-degree-query-lower-bound`)
<c3.-low-degree-query-lower-bound-lead-exo-low-degree-query-lower-bound>
The generic group model closes named oracles one by one. Polynomial
tests on coordinates are oracles it cannot simulate. This lead proposes
one bound for the low-degree part of that class, with no auxiliary
variables.

- #strong[Scope.] Small-x membership `x(P) < B` has degree B in this
  model, so it enters only at D about B, where the bound is weaker than
  sqrt(N). The Legendre symbol of x has degree (p-1)/2. With auxiliary
  variables, small-x membership drops to degree 2 with about log B extra
  unknowns, and a bound would have to depend on their number. So this
  lead does not address index calculus on small-x bases. It targets
  genuinely low-degree statistics: low-degree curves through tuples of
  points, cross-ratios, and bounded-degree relations among coordinates
  of related points.

- #strong[Single-point case.] This is the counting behind
  `LEAD-ICP-algebraic-membership-factor-base`: a degree-d locus holds
  O(d) points. That lead was the top N1 hit for this candidate.

- #strong[H1 (conjecture).] With T queries, success probability is at
  most `O(T^2/N) + O(T D p^(-1/2) polylog p)`, so T is
  `Omega(min(sqrt N, sqrt p / D))` for D = p^(o(1)).

- #strong[Risk.] The single-point case follows from Weil-type point
  counts. Adaptive multi-point tuples need character sums along
  multiples of a point. The Kohel-Shparlinski reference for these is
  recalled, not verified.

- #strong[First step.] Write the single-test lemma, then attempt the
  multi-point reduction. In parallel, measure the maximum bias of
  degree-\<=D tests on pairs (P, kP) for p from 2^16 to 2^24 against D /
  sqrt(p).

== Proposed amendments to existing rows (not edited here)
<proposed-amendments-to-existing-rows-not-edited-here>
- #strong[A1, `LEAD-ICE-generic-oracle-arity-cost-floor`.] Its scope
  excludes oracles that read coordinates algebraically. A conditional
  fine-grained wall, from 3SUM-indexing or k-SUM with preprocessing,
  could extend it to RAM-model oracles. Two cautions. The k-SUM
  conjecture concerns explicit integer lists, while here the set is
  implicit and the operation is the group law. Kane, Lovett and Moran
  show k-SUM has near-linear linear-decision-tree complexity, so no
  query-model proof exists. Suggested step: a literature check of
  3SUM-indexing lower bounds (Golovnev et al., STOC 2020, recalled,
  verify) for implicitly given sets.
- #strong[A2, `LEAD-EXO-invertible-hint-subset`.] Lange and Winterhof
  (COCOON 2002, LNCS 2387, pp.~137-143; and a 2003 follow-up) prove
  degree lower bounds for polynomials interpolating the ECDL and ECDH
  maps. The exact bound was not read in this session. Suggested step:
  read it before measuring A(d). If it covers agreement on subsets of
  size at least n^alpha, it decides the algebraic model of that lead
  from the literature.

== Quick kills, recorded without rows
<quick-kills-recorded-without-rows>
- #strong[Stabilizer-rank classical simulation of Shor's ECDLP circuit.]
  Bravyi-Gosset sampling costs about 2^(0.228 t) for t T-gates.
  Published 256-bit circuits need T or Toffoli counts in the hundreds of
  millions or more, so the cost is far beyond rho. Related:
  `LEAD-EXO-quantum-ecdlp-resources`.
- #strong[Shared summation polynomials across a quadratic twist.] A
  relation on E maps to its twist by scaling x. This helps only when
  logs on both curves are wanted, so it is Tier I at most.
- #strong[Comparison or ordering oracle on x.] Dropped. Ordering by x is
  interval membership, which the existing small-x factor bases already
  use, so it is not a new oracle.

== Collisions with existing leads
<collisions-with-existing-leads>
#figure(
  align(center)[#table(
    columns: (50%, 50%),
    align: (left,left,),
    table.header([candidate], [existing lead],),
    table.hline(),
    [GAG presentation planning], [`LEAD-ICE-gag-contraction-planner`],
    [X\_1(N) diamond-operator
    recast], [`LEAD-STR-level-structure-torsor`],
    [pseudo-Mersenne digit lifts to a number
    ring], [`LEAD-TRF-global-lift-small-height`],
    [CM transport through the canonical
    lift], [`LEAD-STR-class-group-ecdlp-bridge`,
    `LEAD-TRF-cm-canonical-lift-heights`],
    [additive energy of window
    bases], [`LEAD-ICP-coincidence-harvest-structured-base`],
    [x-only isogeny-hopping
    walks], [`LEAD-STR-isogeny-class-generic-invariance`],
    [split-Jacobian projection of factor
    bases], [`LEAD-EXO-split-jacobian-projection`],
    [Eisenstein lattice for the secp256k1 GLV
    box], [`LEAD-STR-endo-scalar-action-generic`],
    [spectral / Jennrich decomposition of group
    tables], [`LEAD-RHO-generic-sqrt-lower-bound`],
  )]
  , kind: table
  )

== Limitations and gaps
<limitations-and-gaps>
- No IDEA records were filed. The propose-ideas flow, ledger-index dedup
  (N3) and object-frame check (N4) remain for the Coordinator.
- Cheng, Cai-Chen, Lange-Winterhof, Kohel-Shparlinski and the
  3SUM-indexing papers have no KN-LIT records yet. Their statements here
  are recalled or read from abstracts and must be verified before any
  row relies on them.
- The Conductor coordination server timed out through its MCP tool. The
  CLI check, run outside the sandbox, returned "Clear".

== Sources
<sources>
- Gao, Shaikh, Kissinger, Graphical Algebraic Geometry, arXiv 2605.13993
  (KN-LIT-c9e59d).
- Q. Cheng, Hard Problems of Algebraic Geometry Codes, arXiv cs/0507026.
- F. Zhang, S. Liu, Solving ECDLP via List Decoding, ePrint 2018/795
  (KN-LIT-643).
- J.-Y. Cai, X. Chen, Complexity of Counting CSP with Complex Weights,
  arXiv 1111.2384.
- T. Chan, M. Lewenstein, Clustered Integer 3SUM via Additive
  Combinatorics, arXiv 1502.05204.
- T. Lange, A. Winterhof, Polynomial interpolation of the elliptic curve
  and XTR discrete logarithm, COCOON 2002.
- S. Bravyi, D. Gosset, Improved classical simulation of quantum
  circuits dominated by Clifford gates, PRL 116 (2016).

== Files
<files>
- `README.md`: this note.
- `novelty-gates.txt`: raw N1 and N2 gate output.
- `figures.py`, `scouting-map.svg`: the candidate-to-lead map.
- `build_pdf.sh`, `report.typ`, `report.pdf`: rendered report. The
  script compresses the PDF with Ghostscript so it stays under the
  artifact-store data threshold and remains in Git.
