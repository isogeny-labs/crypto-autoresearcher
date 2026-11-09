#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(justify: false)
= Certified representation and partial-slope pruning
#text(size: 11pt)[Source-only mathematical designs; both independently reviewed]

#image("diagram.svg", width: 100%)

== Euler aliases remove an unnecessary domain prerequisite
Full k-bit wires map surjectively to the prime field modulo p. Every bit solution gives the intended field computation; every valid projected pair has a canonical bit extension. Thus aliases preserve the projected set. The existing adapter accepts the full auxiliary cube and deduplicates projected models. Per-wire canonical ranges are optional, correcting the earlier dependency while preserving its frozen record.

For fixed invalid x, checked linear nodes obey E_j = G_j + Z_b E_a + c_a E_b. The final identity 1 = A/2 − (W−2)E_W/2 gives a degree-two PC derivation with retained circuit variables. A specialized checker can verify these local identities in O(Kk²) field-term operations without expanding ancestor multipliers. Parsing, masks, bit arithmetic, authentication, storage, coverage and witness costs remain charged. A new authenticated arm/wrapper and DAG verifier are still required.

Membership depends on the curve and coordinate, not the target. After factor-base membership filtering it rejects no additional coordinate. This is a representation/proof design, not new relation-dependent pruning.

== A target-dependent trace filter
In the exact finite-target constant-B k2 chart, the source rows give A0 = b−aq, u1 = a−q² and u0 = alpha+a²+a q²−2bq. The remaining norm row is the target curve equation. For interval roots t+d1 and t+d2, counted with multiplicity, Vieta implies
#align(center)[q² = a+2t+z, where 0 ≤ z ≤ 2B−2 and B = 2^s.]
The necessary slope set T has at most min(p,4B−2) elements. A certificate covers every offset with zero, both checked square roots, or an independently checked nonsquare Euler value. The verifier derives T and its LSB trie. Missing paths certify rejection before all slope bits are assigned.

At depth d ≤ floor(log2 p), at least max(0,2^d−(4B−2)) canonical-completable prefixes are empty. If s+3 ≤ k−1, depth s+3 rejects at least 4B+2 of 8B prefixes, leaving at least one slope bit free. No distribution premise is needed. Empty depth-d cylinders need not be distinct minimal clauses; a free bit need not give two canonical completions.

== Boundaries and next step
This applies to transformed q-first k2 modes, not the original A0-first projection or other chart strata. A semantic certificate verifier must bind the exact rows, interval theorem and complete table; the old flat-PC checker does not accept a trie automatically. Remaining candidates still need all chart/sign/witness checks. Setup and root extraction are charged and must be compared against direct O(B)-scale interval point enumeration.

No candidate execution, implementation, new slot or retry occurred. The 106+6/five-lead scope remains. Publish the reviewed designs, then specify the new checker interfaces; no runtime or degree-of-regularity claim follows.

#text(size: 8pt)[Sources: design-v2.md and independent-review.md (alias/DAG); ../prime-k2-trace-prefix-20261108/design-v1.md, prefix-count-addendum-v1.md and independent-review.md (trace). Exact source hashes are in each source-bindings.json. Adapter full-cube/projection semantics; transform.py literal k2 rows and projection; composition.py interval idempotents/nilpotence. Prior frozen documents remain unchanged.]

#text(size: 8pt)[Literature: #link("https://ocw.mit.edu/courses/18-783-elliptic-curves-spring-2021/b6d0aef71278ad8c1d8b5144c4138cb7_MIT18_783S21_notes3.pdf")[MIT18.783 (2021), Lecture3, sections3.10/3.13]: randomized root finding and verifiable outputs; root cost remains explicit. Eurocrypt2014 PDF fetch returned403 as reported by root; no full-text review or novelty clearance.]
