#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Exact LFD three at the first no-wrap obstruction
2026-11-09. Symbolic theorem followed by one frozen finite verification.

For z=a6=1 and V=span(1,t,...,t^6), every irreducible modulus of degree n>24 yields the same Boolean coefficient system. Its exact last fall degree is3 in the stated strict-closure convention.

#image("closure-comparison.svg", width: 100%)

*Symbolic proof before execution:* Two irreducible cubic trace functionals isolate the two remaining q-coordinates on separate slices. Multiplying by their affine gates at cap3 derives b+c. Affine substitution removes two leading x-coordinates and reduces to the previously verified one-bit system. Its complete affine ideal is therefore in W3. The independently proved W2 obstruction gives equality.

*Computed verification:* The sole r6cap3 cell completed with all controls passing. Full derivation and closure replay gives rank468 in a470-dimensional space, eligible degree-at-most-two dimension104, affine dimension13, and no missing affine generators. A separate reviewer invocation reproduced the result. No unbounded-degree conclusion follows from this finite computation.

*Custody:* Exact source, proof and protocol were pushed before execution. One local attempt, no retries, CPU ceiling60seconds, wall ceiling90seconds, memory512MiB; no new cloud job. The retained source, derivation DAG, controls, manifest, result, process receipt and validated export support replay. Timings and hardware instruction counts were not measured as research outcomes.

*Evidence:* no-wrap-r6-exact-degree-three.md and independent review; attempt-1/r6-certificate.json; attempt-1/r6-result.json; no-wrap-r6-cap3-independent-replay.json. The computation corroborates an already reviewed symbolic proof. These are written proofs and checked finite certificates, not Lean kernel certification.
