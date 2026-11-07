#set page(paper: "a4", margin: 22mm)
#set text(font: "Liberation Sans", size: 10pt)
#heading(level: 1)[Endosweep batch 7: discriminant certificate fidelity]
#text(size: 9pt)[Reviewed base 23c5aeca09f8f512d90755193660c1b2aa509714; plan d549627b2; task T-1739.]

The recorded brainpoolP512r1 integers pass the named hosted Lean arithmetic certificate and an independent blind exact-integer rederivation. The factor product, candidate discriminant, and degree bound agree. The Lean theorem makes fundamentality conditional on two large factors being prime; this review did not independently discharge that premise. The named-curve trace and endomorphism-ring interpretation remain separate open bridges.

#image("review-boundary.svg", width: 100%)

== Evidence

- Hosted formal run 42260198392 reports a successful build and axiom audit for `CryptoResearch.Endosweep.DkExactBatch7.exact_discriminants`. Target/source hashes match the reviewed commit; standard axioms only are listed. See machine-evidence.md.
- The blind review independently recomputed the integer equalities and L=512, d>=2^510. Its factor-digit mutation failed the product check. Its coprime composite-base counterexample passed the arithmetic but was not fundamental. See reviews/blind/report.md.
- The source review passed 53 lightweight checks and all 13 data-manifest hashes. Lean generation was byte-identical; the archived factor/snapshot chain and the pinned upstream Brainpool parameter record agree. Historical PARI proof custody was not independently confirmed. See reviews/source/report.md.

== Review outcome and next checks

The numeric arithmetic claim is independently corroborated at its recorded-integer scope. Overall named-curve interpretation and unconditional fundamentality are inconclusive. Correct the target's unconditional squarefree wording in a new version, enforce and hash the std-curves input pin for future builds, retain checkable large-factor primality evidence, then prove or independently verify the curve-to-order bridge.

The plan was committed before dispatch, but its Markdown format does not satisfy the automated structured independence checker. Reports carry individual read attestations; this procedural deviation is retained. No experiment measurement or performance claim changed, so historical batch graphs remain unchanged.
