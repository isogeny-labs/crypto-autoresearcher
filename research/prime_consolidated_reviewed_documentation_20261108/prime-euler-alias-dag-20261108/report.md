# Certified representation and target-dependent coefficient pruning

Both the alias/DAG construction and the separately frozen trace-filter design, including its early-prefix count, received independent written acceptance as source-only mathematics; no substantive algebraic or counting defects were found.

## Corrected Euler dependency
Canonical bit representatives are unnecessary for Euler field wires. With k=ceil(log2p) bits, reduction modulo p maps the full bit cube onto F_p. Any Boolean circuit solution gives the intended field computation, and every valid projected pair has a canonical bit extension. Aliases therefore preserve exactly the projected solution set. The actual adapter's full-cube mode and projected-model deduplication support this semantics. A new authenticated arm/wrapper is still required; old arm semantics remain frozen.

For fixed invalid x, checked linear error nodes E_j=Z_j-c_j satisfy E_j=G_j+Z_b E_a+c_a E_b. The final identity1=A/2−(W−2)E_W/2 yields a degree2 conditional PC derivation. A specialized DAG checker can verify local polynomial equalities using O(Kk²) field-term operations without expanding all ancestor multipliers. Parsing, masks, field bit complexity, source authentication, storage, model/witness checking and full coverage remain separately charged. This corrects the earlier product-domain requirement, not a measured performance result. Membership is target-independent; it adds no coordinate pruning once the factor base is already membership-filtered.

## Target-dependent k2 trace design
For the exact finite-target constant-B k2 chart, source rows imply A0=b−aq, u1=a−q² and u0=alpha+a²+a q²−2bq. The remaining norm constant is precisely the target curve equation. Support discriminant is Delta(q)=q⁴−6a q²+8bq−3a²−4alpha.

If support roots lie in t+[0,B−1] modulo p, counted with multiplicity, Vieta forces q²=a+2t+z with0<=z<=2B−2. The necessary slope set T has at most min(p,4B−2) elements. For every z, a complete certificate lists zero, both verified square roots, or a verified nonsquare Euler value. The verifier constructs T and its LSB trie itself; missing prefix paths reject partial slopes before all q bits are assigned.

At depth d<=floor(log2p), at least max(0,2^d−(4B−2)) canonical-completable prefixes are empty. If s+3<=k−1 and B=2^s, depth d=s+3 rejects at least4B+2 of8B prefixes while leaving at least one slope bit free. No distribution assumption is used. These are empty depth-d cylinders, not necessarily distinct minimal clauses. Minimal missing-child prefixes can cover their union; one remaining bit does not guarantee two canonical field completions.

This applies directly only to transformed q-first k2 modes. The original A0-first projection, other strata and arities remain outside the construction. Per-z completeness, exact source authentication and a new semantic rejection verifier are necessary; the old flat-PC checker does not accept a trie automatically. Candidate slopes still require all support/sign/chart/witness checks.

Setup is O(B)-scale with charged square-root extraction and Euler verification, and must be compared to direct interval point enumeration. No complete attack, runtime advantage or degree-of-regularity reduction is inferred. Both proposals retain all106+6/five-lead downstream obligations and all existing budgets; no imports, implementation, trials or retries occurred.

Sources and review inputs: design-v2.md, independent-review.md and source-bindings.json in this packet; ../prime-k2-trace-prefix-20261108/design-v1.md, prefix-count-addendum-v1.md, source-bindings.json and its independent-review.md. Frozen prior Euler documents remain unchanged; the dependency correction is additive.

Literature: MIT18.783 Spring2021 Lecture3, sections3.10 and3.13, discusses randomized finite-field root finding and verifiable outputs; square-root cost is retained explicitly, not assumed universally deterministic polylogarithmic. [Primary lecture PDF](https://ocw.mit.edu/courses/18-783-elliptic-curves-spring-2021/b6d0aef71278ad8c1d8b5144c4138cb7_MIT18_783S21_notes3.pdf). Root reported a403 fetching the Eurocrypt2014 Symmetrized Summation Polynomials PDF; no full-text review or novelty clearance is claimed.
