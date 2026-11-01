#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)

= Independent NCP review synthesis

*Archive:* TASK-20261031-20ed91  \
*Producer:* PR #2417, exact head `f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f`  \
*Plan SHA-256:* `f5d4d26008bc3cf0ffe3fd26c7a36dbd93a57499c4aff6dc4e61a65a3bf13264`

The scoped source calculations survived independent review. J1 checked 2,115 finite point-encoding cases. J2 checked the companion witness in 15 modulus/translation cases and 55 point evaluations. J3 independently derived the shortest-word formula before reading producer code and checked 433 words and 146 state/sign comparisons. These controls are mathematical and source-level evidence, not fresh Lean elaboration.

#table(columns: (20%, 44%, 36%), inset: 5pt,
  [*Joint*], [*Scoped finding*], [*Formal status*],
  [J1], [Point action and canonical encoding match source; exact order is necessary.], [Source fidelity faithful_scoped; machine not_verified; outcome inconclusive.],
  [J2], [Squared negation-translation witness maps to zero in affine group algebra; augmentation is -1.], [Source fidelity faithful_scoped; fresh replay infrastructure_error; outcome inconclusive.],
  [J3], [Minimum length is sum of absolute counts plus penalty 0, 1, or 2 by sign and negative-coordinate condition.], [Independent derivation holds; machine not_verified; outcome inconclusive.])

#image("diagram.svg", width: 100%)

== Separate historical bridge finding

At modulus 3, a nonzero group-algebra combination of three translations and three translated reflections acts as the zero 3-by-3 point-operator matrix. Faithfulness of the affine group action does not make its group-algebra representation faithful. J2 supplies the exact coefficients and a concrete three-point elliptic-curve realization over F5. The submitted companion theorem targets the group algebra, so this does not refute it. The historical embedding sentence needs a new producer revision.

== Independence and next gate

All 118 copied reviewer files match their three published source commits by Git blob, with no missing or extra file. J3's blind derivation was frozen at `8b53f4c94b2b06f6cfdebfcd89b3ed2fd6ef6d9d` before any producer read. The original plan omitted a prospective sealed release rule; the complete-session attestation includes four later protected reads. The exact combined independence checker exits 1 with that single issue. No clean independence pass is claimed.

The next machine step is an owned, isolated exact-pin Lean build of each named declaration, elaborated type capture, transitive axiom audit, and full input hashes. Then correct the historical target-identification sentence and re-review the affected claim. A new blind round needs a prospective phased-release plan. This technical packet makes no official scientific transition.

*Evidence:* review.md in each of TASK-20261031-4b6d61, TASK-20261031-8a54e2, and TASK-20261031-f9c13a. Raw controls, attestations, and inspected reviewer PDFs are archived with those reports. Diagram is a logic map; no performance data were changed.
