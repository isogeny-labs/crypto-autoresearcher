#set page(paper: "a4", margin: 17mm, numbering: "1")
#set text(size: 9pt)
#set heading(numbering: "1.")

= ECDLP lead pursuit audit

_160-lead reconciled atlas · 2026-11-01_

#image("diagram.svg", width: 100%)

== Decision

The 159-row ECDLP atlas at `crypto-autoresearcher@7072741f712c` was reviewed family by family against `crypto@b6ffdca53494`. The review also added one missing live split-graph/secant successor, so the reconciled atlas has *160 leads*. Exactly *21 narrowly scoped mechanisms* have mechanism-wide obstruction evidence under their stated assumptions. The other *139 leads remain pursued* through a next action or explicit revisit trigger.

This is a scope decision. Each stopped row is stopped only for the exact mechanism in its obstruction. A different presentation, locus, oracle, statistic, or stated escape remains live.

== Queue invariant

Only `closed_obstructed` leaves the pursuit queue. `closed_known`, `closed_dominated`, and `exhausted_at_scale` remain queued through their revisit triggers. Timeouts, OOMs, missing infrastructure, unavailable sources, finite nulls, and finite measured cost disadvantages are not mechanism-wide disproof. A complete lower bound inside an explicitly named model obstructs only that model.

When a row combined a proved negative subcase with an untested escape, the audit preserved the obstruction as evidence and restored the row to `open_next_step` using its existing `revisit_when`. Twenty-six overbroad closures were corrected this way.

== Family accounting

#table(
  columns: (2.6fr, 1fr, 1fr, 1fr),
  inset: 5pt,
  align: (left, right, right, right),
  [*Family*], [*Reviewed*], [*Obstructed*], [*Pursued*],
  [Binary-field IC], [23], [2], [21],
  [IC engines], [20], [2], [18],
  [Prime-field IC], [27], [3], [24],
  [Generic, transfer, structure, exotic], [90], [14], [76],
  [*Total*], [*160*], [*21*], [*139*],
)

== Exact suppressed scopes

#set text(size: 8pt)

- Binary IC: `generic-table-oracle`; linear/subspace scope of `frobenius-orbit-factor-base`.
- IC engines: coordinate-blind scope of `generic-oracle-arity-cost-floor`; generic-fibre census of `semaev-cover-monodromy`.
- Prime IC: `generic-table-decomposition`; generic equality-filter scope of `representation-subset-sum`; `self-pairing-prime-order`.
- Generic: `generic-sqrt-lower-bound`; generic auxiliary-power acquisition in `cheon-aux-acquisition`.
- Transfer: `cm-canonical-lift-heights`; `one-point-self-pairing`; homomorphic scope of `padic-canonical-section`; class-invariant scope of `prime-field-isogeny-to-weak`; homomorphic scope of `second-torsion-direction`.
- Structure: generic scopes of `endo-scalar-action-generic`, `isogeny-class-generic-invariance`, and `isogeny-transport-preprocessing`; class-invariant weaknesses in `isogeny-walk-weak-neighbour`; scalar/generic scopes of `p192-class-cm-relations` and `secp256k1-cm-class-audit`.
- Exotic: the named GGM-simulable scope of `augmented-oracle-ggm`.

#set text(size: 9pt)

== Load-bearing corrections

The binary SAT/enumeration measurements do not test symmetric Groebner systems at `ell=6..8`, high-arity closure, or the GG14 `m=4` presentation. The Semaev chain identity assumes rather than measures topology-independent closure degree. Finite volcano, endomorphism, factor-base, and residual-relation panels do not prove absence beyond their tested regimes. Proofs for homomorphic, bounded-degree, generically Galois, or full-Jacobian routes do not close explicitly non-homomorphic, growing-degree, non-Galois, or projected successors.

Load-bearing cross-checks are `crypto:research/factor_base_arity_review_20261024/README.md`, `crypto:research/prime_factor_base_degree_20261031/parallel_20261031/RESULTS.md`, `crypto:problems/ghs-higher-magic-descent-not-executable.md`, and every atlas row's obstruction, foreclosure, revisit, evidence, and related fields.

No performance result is introduced. This report records disposition and queue semantics only.

== Review boundary

The Conductor command was unavailable and no `.conductor/WORKFLOW.md` was present. The global review stamp remains unchanged: the cryptanalysis base ref was unreachable and the configured `ecc-challenges` checkout was absent, so a whole-universe freshness claim would be unsupported. The 159 pre-existing rows, the added live successor, and the cited crypto snapshot are reconciled; the unavailable repositories must be reconciled before advancing the canonical stamp.
