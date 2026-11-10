#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
#set par(justify: false)
= Coordinate scalar certificates
#text(size: 11pt)[Reviewed coverage obstruction and bounded next design]

Independent written review found no substantive algebraic defect in the coordinate classification. Source-static mathematics; no runtime validation or official promotion.

#image("diagram.svg", width: 100%)

== A precise coverage obstruction
For M = 2^s coordinate values, a scalar quartic restriction covers at most four projected pairs, or two under the x-first prefix format for s ≥ 2. Fixing either coordinate leaves a genuinely quadratic polynomial, or a genuinely linear one at the target coordinate. Four distinct remaining coordinate values therefore cannot all give one scalar value.

Each x-fiber has at most two roots. Covering all invalid pairs solely by these scalar certificates requires at least ceil((M² − 2M)/4) arbitrary-subcube clauses or ceil((M² − 2M)/2) prefix clauses. This restricted-family count excludes arbitrary PC/SAT proofs, membership, auxiliary-domain reasoning and separate coefficient charts.

== Exact lift transport
Let C = 2t, H = xy − r(x+y) − 2r² − a and S = x+y+r. The lifted originals are g1 = L² − S and g2 = CL − H. Neither becomes scalar from projected assignments alone. But

#align(center)[E = H² − C²S = C²g1 − (CL+H)g2]

is exactly the existing quartic. If its restriction is c ≠ 0, multipliers C²/c and −(CL+H)/c certify rejection without fixing auxiliary bits. Product degree is at most four, or two after fixing a whole coordinate. The same coverage limit applies; these are conditional certificate bounds, not regularity estimates.

== A structurally different next construction
Membership at an invalid x rejects all M partner choices. A support-local Möbius table gives the same indicator as the current full-block table. The next source-only design uses Q = x³+ax+b, W = Q^((p−1)/2), and W(W−1) = 0, allowing zero and squares while excluding nonsquares. A fixed invalid coordinate permits degree-two PC propagation in extended circuit variables; flat expanded certificates can grow.

Canonical range checking for every wire is not supported by the current single-suffix adapter. Naive forbidden-value clauses may be large. Domain verification, certificate representation and full construction/checking costs remain explicit design obligations. No implementation or experiment is admitted.

== Scope and sources
The engine schedules only {0,s,2s,n}, omitting 2s−1 for s > 1, and fallback fixes all n bits. Complete projection coverage and EC witness reconstruction remain separate checks. Administrative scope retains 106+6 cells and five leads; no retry or budget reset.

#text(size: 8pt)[Sources: mathematical-note-v2.md; independent-review.md; source-bindings.json; euler-membership-design-v1.md and euler-independent-review.md (accepted source-only construction). Exact source: research/prime_sat_followup_20261029/encoding.py:36–97; research/prime_sat_prefix_adapter_20261030/adapter.py:110–200; research/prime_sat_transform_integration_20261103/engine_counted.py:213–275,442–449. These findings classify the coordinate chart, not the six coefficient charts.]
