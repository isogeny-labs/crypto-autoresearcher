#set page(paper: "a4", margin: 17mm, numbering: "1")
#set text(size: 9pt)
#set heading(numbering: "1.")

= ECDLP lead pursuit audit

_160-lead reconciled atlas · current disposition 2026-11-02_

#image("diagram.svg", width: 100%)

== Decision

The 159-row ECDLP atlas at `crypto-autoresearcher@7072741f712c` was reviewed family by family against `crypto@b6ffdca53494`. The review also added one missing live split-graph/secant successor, so the reconciled atlas has *160 leads*. The 2026-11-01 audit recorded *21 scoped obstructions / 139 pursued*. The confirmed 2026-11-02 arity/oracle correction makes the current accounting *20 `closed_obstructed` / 140 pursued*.

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
  [IC engines], [20], [1], [19],
  [Prime-field IC], [27], [3], [24],
  [Generic, transfer, structure, exotic], [90], [14], [76],
  [*Total*], [*160*], [*20*], [*140*],
)

== Exact suppressed scopes

#set text(size: 8pt)

- Binary IC: `generic-table-oracle`; linear/subspace scope of `frobenius-orbit-factor-base`.
- IC engines: generic-fibre census of `semaev-cover-monodromy`.
- Prime IC: `generic-table-decomposition`; generic equality-filter scope of `representation-subset-sum`; `self-pairing-prime-order`.
- Generic: `generic-sqrt-lower-bound`; generic auxiliary-power acquisition in `cheon-aux-acquisition`.
- Transfer: the twelve fixed-arity mechanisms in `cm-canonical-lift-heights`; `one-point-self-pairing`; homomorphic scope of `padic-canonical-section`; class-invariant scope of `prime-field-isogeny-to-weak`; homomorphic scope of `second-torsion-direction`.
- Structure: generic scopes of `endo-scalar-action-generic`, `isogeny-class-generic-invariance`, and `isogeny-transport-preprocessing`; class-invariant weaknesses in `isogeny-walk-weak-neighbour`; scalar/generic scopes of `p192-class-cm-relations` and `secp256k1-cm-class-audit`.
- Exotic: the named GGM-simulable scope of `augmented-oracle-ggm`.

#set text(size: 9pt)

== Load-bearing corrections

The binary SAT/enumeration measurements do not test symmetric Groebner systems at `ell=6..8`, high-arity closure, or the GG14 `m=4` presentation. The Semaev chain identity assumes rather than measures topology-independent closure degree. Finite volcano, endomorphism, factor-base, and residual-relation panels do not prove absence beyond their tested regimes. Proofs for homomorphic, bounded-degree, generically Galois, or full-Jacobian routes do not close explicitly non-homomorphic, growing-degree, non-Galois, or projected successors.

Load-bearing cross-checks are `crypto:research/factor_base_arity_review_20261024/README.md`, `crypto:research/prime_factor_base_degree_20261031/parallel_20261031/RESULTS.md`, `crypto:problems/ghs-higher-magic-descent-not-executable.md`, and every atlas row's obstruction, foreclosure, revisit, evidence, and related fields.

No validated leaderboard, cryptographic-scale, or asymptotic performance is claimed. The bounded local full-solve evidence added below is labelled explicitly; this remains a scoped-evidence and queue audit.

== Xedni correction

The later primary-source and kernel-checked review at `crypto@34caae22581045ec59fe779d86f8bf2d495cc14a` found that two xedni rows exceeded JKSST's theorem. Theorem 4.1 says "under certain plausible assumptions"; Lemma 4.1 assumes the selected-lift height/discriminant comparison and Lang, while reduction, useful-relation, cofactor, and adaptive-hazard bridges remain explicit premises.

`LEAD-TRF-global-lift-small-height` and `LEAD-ICP-char0-lifting-xedni-smoothness` are therefore `open_next_step`. Their exact and finite negatives remain recorded. `KR-IC-cd159a` now states the conditional theorem, and `LEAD-EXO-global-lift-height` pursues both the function-field timing and characteristic-zero bridge-composition branches.

The CM row stays suppressed only inside corrected L9: ordinary prime-field Serre--Tate/global CM models, fixed arity 2..9, absolute `C0`, and twelve enumerated mechanisms. Target-dependent arbitrary sections, growing arity or `C0`, and unenumerated families remain outside. At that stage, the 21/139 totals were unchanged because `closed_known` rows were already pursued.

Primary JKSST PDF SHA-256: `981bf955f7aecc5df4f271837f6653bd7666e5026f59df44196609d4a1dd6bc7`; checked at Section 4, Lemma 4.1, Theorem 4.1, Sections 5--6, and notes 7--8. The sibling proof map is `research/jksst_xedni_audit_20261101/PROOF_MAP.md`.

== Arity/oracle correction · 2026-11-02

`LEAD-ICE-generic-oracle-arity-cost-floor` is now `open_next_step`. Its exact fixed-arity negative remains: `EV-SEMBIN-b6d042` has zero in-domain sub-rho cells for `ENUM`, `MITM`, and `MITM_CAPPED` in the frozen model; the reviewed Lean declaration `mitm_never_sub_generic` proves `costAll(m,beta,k) > 1/2` for `m >= 2`, `beta > 0`, and `k >= m/2`.

The independent semantic review rejects the bundled blanket-attainment and literal pointwise-threshold wording. The model does not supply an executable algorithm, actual oracle output/useful-rank semantics, required yield hypotheses, or a uniform model-to-algorithm theorem. The `FREE` control has 7,850 sub-VOW model cells; free oracles, growing arity, and coordinate-reading constructions remain outside the exact negative. Those branches stay pursued.

This additive correction changes IC engines from 2/18 to *1 obstructed / 19 pursued* and the atlas from 21/139 to *20 / 140*. It preserves the original dated 26-row statement and the later Xedni narrative. Sources: `docs/reports/2026-11-01-ic-arity-oracle-review/synthesis/report.md`, `ledger/proposals/IDEA-20261024-a2b05d.yaml`, and `ledger/decisions/DEC-20261101-8adb11.yaml`.

== Coordinate-visible Wagner filter · 2026-11-02

The exact ECCp-131 study at `crypto@b825c0c0d535215a6b01571350fa5b54a05ea0fd` evaluated 3,450 frozen simple 1--8-bit coordinate configurations in each of six small-x/random-base cells at `B=64,128,256`. Every recorded held-out Wilson lower enrichment ratio was below one (0.6093--0.7783). The two positive small-x point estimates were post-add predicates that first require all $Theta(B^2)$ pair sums. Exact-width F4/F5 was unavailable and unmeasured; local clocks and performance claims remain invalid.

This rejects only that finite predicate family. Learned multibit hashes, algebraic buckets, larger bases, other curves, and any coordinate-visible filter with a proved subquadratic pair generator remain live under `LEAD-EXO-four-list-ktree-join`. The generic representation-subset-sum obstruction is now explicitly limited to group-operation/equality-only filters. Counts remain *160 total / 140 pursued / 20 scoped obstructions*.

Q5 at `crypto@20e19b9fcbd790f86bf66be41d3b25e5cc3ceced` ran msolve F4 on 6,486 frozen `m=2` toy systems with zero failures/timeouts: A2/B matrix cells matched 16/16 and registered coordinate improvement was 0/16. This forecloses only that toy family. Its carrier cards remain `open_next_step` / `open_blocked`; `m>=4`, larger primes/scales, other engines/orders, relation collection, useful rank, linear algebra, and end-to-end cost remain open. Counts do not change.

== Curve25519 PKM whole solve and guess depth · 2026-11-02

At `crypto@8491be7ed89642fa2f3715f8d5452839d26c384a`, one `k=20` Curve25519 miniature (`p=1048573`, `r=131203`) supplied six full `m=2`, isogeny-tower `t=6`, `G=4` solves. The candidate was behind proj-a by *2.58x / 1.35e5x / 8.17e5x* and rho-neg by *18.2x / 9.55e5x / 5.85e6x* at `w=0 / 0.1 / 1`. Session 1 had 24/24 verified records and eight identical replays, but it is local L0 with no second host or validator. The one-target `G=0` control ranks nothing because its replay differs in phase counts.

The companion `m=2` guess-depth panel fell to the edge `G=t-1` in every successful series, falsifying its registered interior U-shape. Its best modelled cell (`k=20,t=10,G=9`) has no common-unit whole solve or matched rho. The committed files contain 32 successful rows and 35 statuses despite stale 27/30 prose. The `k=28,t=14` cells remain unmeasured after allocation failure, timeout and the `G<=12` code cap.

This rejects only those finite predictions. It supplies no theorem or exponent. The edge-cell whole solve, `m>=4`, other forms, curves and scales, useful rank, replay repair and independent validation remain pursued. `LEAD-ICP-pkm-tower-algebraic-oracle` stays `open_blocked`; `LEAD-ICE-charged-toy-ic-exponent-vs-rho` stays pursued at `exhausted_at_scale`; counts stay *160 / 140 / 20*.

== JV cover line-search review · 2026-11-02

At `crypto@434d356433b2118dfd5a916db222e2181bd7462d`, independent validation reproduces a *1.705x* charged best-of-65,536 factor-base-line gain on nine weak-class Nagao-only cells (`p=1301,1451,1601`). It is a finite constant factor, not an exponent change. In like-for-like F_p multiplications the arm remains *1.900 / 1.585 / 1.318x rho*; U1 omits cover additions and is an unrankable lower bound. The same-class JV sieve is *83--100x cheaper* (21--25x against S+), so the Nagao card stays `closed_dominated` and pursued.

The frozen successor applies line selection to the sieve at `p in {1009,1511,1823}`, seeds 17--32, with search, native counters and isogeny walk charged in `bitop/v1` against matched strong rho. The red-team `n=4096` pilot (*1.42x [1.18,1.73]*) is exploratory/unfrozen non-evidence and `n=65536` is a *0.92x* net loss. Large-prime, exhaustive-table and other-subline routes remain open; the sieve card stays `open_next_step` and counts stay *160 / 140 / 20*.

== Review boundary

The Conductor command was unavailable and no `.conductor/WORKFLOW.md` was present. The global review stamp remains unchanged: the cryptanalysis base ref was unreachable and the configured `ecc-challenges` checkout was absent, so a whole-universe freshness claim would be unsupported. The 159 pre-existing rows, the added live successor, and the cited crypto snapshot are reconciled; the unavailable repositories must be reconciled before advancing the canonical stamp.
