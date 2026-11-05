#set page(paper: "a4", margin: 18mm, numbering: "1")
#set text(font: "DejaVu Sans", size: 10pt)
#set par(leading: 0.6em)
= LFD paper readiness
5 November 2026. Enough material for a focused manuscript draft; novelty and submission readiness remain unestablished.

The prime digit theorem shows that fixed quartic input degree does not keep last fall or the stated solving degree bounded as digit width grows. For the exact two-block Boolean restriction over a prime field, the written bound is
$ 4+floor(s/2) <= d_F <= "sd"_sigma(F) <= 2s+1. $
It requires s≥2, prime p≥2^s, a nonsingular curve and degree-compatible order. SAT and UNSAT are covered. This is a result about that input presentation, not every encoding or solving algorithm.

The raw binary two-S3 theorem proves Boolean UNSAT implies last fall at most 3ell+1, with every bit equation explicit. It is instantiated in Lean, including coefficient projections, normalization, support-aware localization and affine-fibre refutations. Auxiliary variable count does not occur in the bound at fixed ell. The degree proof can use exponentially many assignments and establishes no solver running time or discrete-log attack cost.

#image("readiness.svg", width: 100%, height: 115mm, fit: "contain")

The open growing binary lower bound need not block a paper scoped to these results. A complete Lean proof of the prime lower bound would strengthen its supplement, but a correct written theorem can be published without full mechanization. The paper must distinguish the two proof forms.

#pagebreak()
= Code and verification package
GitHub run41996349062 passed the complete workspace build and canonical discharged-target verification. Its archive contains120 machine-verified receipts. The five LFD receipts are preserved unchanged, and their source/specification/import/configuration hashes match this checkout. The run checked PR head69b20afa using synthetic merge0cfa6988; later delivery edits require their own CI. Earlier local timeout and out-of-memory receipts remain unchanged.

The new tools/verify_lfd_bundle.py exposes three distinct modes: file-integrity only, replay of retained CI evidence, and fresh canonical Lean verification. The integrity mode explicitly reports that proofs were not run. CI replay checks the actual requested theorem and transitive local source hashes. Fresh execution invokes the existing full build and axiom gate. Twelve unit tests check fail-closed handling and mode semantics; they are not mathematical proof evidence. Actual five-receipt replay also passed.

== What remains before submission
1. An exact novelty comparison. The selected primary sources establish context and reusable results; they do not certify novelty of our specific bounds.
2. A standalone manuscript with unified notation, complete theorem statements and proofs, related work, and an accurate description of formal coverage. The current report is a technical record.
3. Specialist review of the final manuscript and a frozen archival supplement/release. No venue or acceptance prediction is made.

A provisional title is “Degree bounds for Boolean encodings of Semaev systems.” Suggested contents: ordinary/Boolean closure; normalization; prime growing-family proof; binary supported-affine bound and raw descent; mechanization and reproducibility; limitations and related work.

== Primary-source checks
Caminata–Gorla, arXiv:2112.05579v2, Definitions1.1/1.5, Theorem3.1 and Section4: the solving-degree identity is prior work, and first fall is not a sufficient estimate.

Huang–Kosters–Yang–Yeo, arXiv:1505.02532, Theorem1.1 and Section6: the Weil-descent result has zero-dimensional, radicality and separating-projection hypotheses; its ECDLP limitations must be compared explicitly.

Kosters–Yeo, arXiv:1503.08001, Section4.2: characteristic-two trace structure and low-degree falls already challenge first-fall heuristics.

Kousidis–Wiemers, arXiv:1906.05594, Theorem3.2 and Section4: the proved first-fall bound and later regularity heuristic are distinct. Their specified binary Weil descent is not our prime-coefficient digit encoding.

Sources were retrieved and read; hashes and consulted sections are in literature-review.json. A broader polynomial-calculus/Boolean-degree and Semaev literature search remains necessary. No priority claim is made.

== Custody and status
The theorem files, reviews and old verification failures were preserved. The older derived report now includes the later CI outcome; lossless PDF compression preserves every page's text and pixels and satisfies the unchanged size policy. The new report and editable diagram are communication artifacts. No scientific state, signed PCC standing, external submission or attack-cost claim was changed.
