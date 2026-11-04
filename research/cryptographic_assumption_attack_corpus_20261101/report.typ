#set page(paper: "a4", margin: 17mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt)
#set heading(numbering: "1.")
#show table: set text(size: 7.8pt)

= Cryptographic assumption attack corpus

#text(fill: rgb("526079"))[Prioritized formal-audit plan · 2026-11-01]

== Outcome

This search converts recurring ECC and proof-system slogans into exact
counterexamples, conditional repair theorems, model boundaries, or explicit
interface gaps. Five high-leverage finite targets are frozen now. Their Lean
files do not yet exist, so they are *undischarged pointers*, not verified
proofs, vulnerabilities, or security conclusions.

#figure(
  image("diagram.svg", width: 100%),
  caption: [Claim-to-premise triage. Red marks false universal wording; amber
  marks required hypotheses; green marks the repair that is actually
  available. Model-relative and open-hardness layers remain separately named.],
)

== Classification rule

#table(
  columns: (28%, 72%),
  inset: 5pt,
  stroke: rgb("d7dde7"),
  [*Status*], [*Meaning*],
  [false-as-stated], [A concrete model satisfies the premises and falsifies the conclusion.],
  [conditionally proved], [The conclusion follows only after the theorem type exposes every algebraic, order, distributional, encoding, or timing premise.],
  [model-relative], [The theorem lives in a named GGM, ROM, AGM, or QROM model; the qualifier cannot be erased.],
  [open computational assumption], [Lean may verify reductions and finite controls, but does not settle the real-world unbounded hardness assumption.],
  [unconnected interface], [The abstract theorem and implementation endpoint exist, but no checked refinement connects them.],
)

#pagebreak()

== Frozen first tranche

#table(
  columns: (17%, 25%, 29%, 29%),
  inset: 4pt,
  stroke: rgb("d7dde7"),
  [*Target*], [*Countermodel*], [*Conditional repair*], [*Boundary*],
  [MOD-ALIAS], [`0` and `q` are distinct naturals but equal in `ZMod q`.], [Casting is injective for representatives strictly below positive `q`.], [A circuit claim still needs a range/encoding refinement.],
  [SUBGROUP], [`ZMod 2 × ZMod 3` contains ambient elements outside the designated order-three factor.], [Supply exact-order and membership witnesses; require nonidentity when the protocol does.], [This is not yet an elliptic-curve decoder or invalid-curve theorem.],
  [BATCH-RLC], [After seeing `rho`, choose `e0=-rho`, `e1=1`; the combination vanishes identically.], [Fix a nonzero error polynomial before an independent uniform field challenge and apply its degree/root bound.], [Fiat--Shamir transcript binding is a separate theorem.],
  [POLY-FUNCTION], [`X^q-X` is formally nonzero and zero as a function on `F_q`.], [A univariate polynomial of degree below `|F|` that vanishes everywhere is zero.], [Commitment degree, SRS, quotient, and evaluation-domain interfaces remain.],
  [SCHNORR-SS], [Equal challenges reveal nothing; a nonzero difference in `ZMod 4` may be a nonunit.], [Same commitment, distinct challenges, exact prime-order subgroup, and injective scalar encoding give extraction.], [Special soundness is not Fiat--Shamir, ROM/QROM, or proof-of-knowledge security.],
)

The five task specifications live under `formal/targets/attack-*.yaml`. A
green theorem build will still require independent semantic-fidelity review.

== What to pursue next

*Priority 0 composition controls.* Cofactor projection and pushforward;
constant-hash Fiat--Shamir; Pedersen/IPA relation kernels; zero knowledge
versus soundness and proof of knowledge; correlated repetition; correct DLP,
CDH, and DDH reduction directions.

*Priority 1 protocol interfaces.* Exceptional EC formulas; invalid-curve and
twist decoding; injective transcript serialization and domain separation; KZG
known-`tau`, degree, subgroup, and batching boundaries; PLONK lookup and
permutation denominators; circuit-to-native EC refinement; subgroup-scoped
random self-reducibility; Pollard-rho random-map assumptions; RFC 9380 suite,
uniformity, and cofactor contracts; concrete query and multi-user losses.

*Priority 2 foundations.* A finite game/oracle framework; exact forking loss;
generic-group random encodings; ROM, AGM, KEA, q-SDH, and QROM boundaries;
separate SNARK security definitions; then full KZG, Groth16, and PLONK.

== Ninety-day sequence

1. *Days 0--30:* discharge the five finite targets with countermodel and
   repair in the same module; axiom-audit them and review statement fidelity.
2. *Days 31--60:* formalize cofactor, Fiat--Shamir zero-hash, Pedersen,
   ZK/soundness, repetition, and KZG toxic-waste algebraic controls.
3. *Days 61--90:* implement a minimal finite transcript/oracle semantics,
   then prove one batching game and one two-fork extraction game before
   attempting a generic-group or commitment-security result.

== Source and scope boundary

Primary boundaries were checked against JKSST, Shoup, Pointcheval--Stern,
Bellare--Garay--Rabin, KZG, SEC 1, RFC 9380, the AGM paper, Groth16, and PLONK.
Repository inputs include `docs/reports/xedni-sadek-20261101/`,
`problems/xedni-sadek-explicit-cutoff.md`, `H-XEDN-292264`, and
`KN-LIT-c9e59d` on `GAG_q`. Existing STARK semantic reviews already record
the modular-alias warning and the `X^2-X` finite-field example; this corpus
targets their Lean formalization, not novelty. Full provenance and
theorem-shaped statements are in `README.md` beside this report.

Lean can refute universal mathematical statements and verify reductions under
named hypotheses. It cannot prove or disprove an unformalized real-world DLP,
CDH, q-SDH, KEA, or knowledge-soundness assumption, and it cannot establish
that deployed code matches an abstract model without a refinement proof.
