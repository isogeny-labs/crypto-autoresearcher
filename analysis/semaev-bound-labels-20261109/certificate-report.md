# All-cap certificates and original-system dual separators

2026-11-09. Software validation and symbolic proof continuation.


## Independently checked all-cap certificates

The exact-LFD CLI now accepts --certificate-output NEW-CERTIFICATE.json. A complete run emits every cap's basis with a derivation for each row: eligible literal input or prior-row variable product, followed by XORs of prior rows. The certificate binds the exact input equations. Trace storage is budgeted and capped at200000 entries; exhaustion emits neither a partial certificate nor an exact label. The result binds the separately written certificate by SHA256.

`python3 verify_boolean_lfd_certificate.py CERTIFICATE.json --operation-limit 1000000 --output NEW-RESULT.json` uses no producer imports. It recomputes every derivation, validates degree-first independent pivots, checks all input containment and all eligible basis-variable products, and independently computes zero assignments and evaluation ranks. Every cap is required. Invalid proofs fail; budget exhaustion returns verified:false and exact_lfd:null. Wire input is capped at16MiB and N<=12. This verifies the supplied normalized mathematical system; its linkage to original curve/group data remains a separate exact join.

Thirty-five software controls pass, including altered rows, forward references, missing caps, unsaturated bases, invalid domains, budget exhaustion and an actual two-CLI certificate/hash roundtrip. The new hand-fixture certificate independently verifies LFD4 and four code solutions with68441 verifier accounting units. The earlier set-span cross-check failure remains unchanged; this is a new proof-carrying implementation, not a retry of that script or a production scientific sample.

The parallel proof eliminates epsilon exactly, obtaining an original trace-slice linear pencil in x for each t. A degree-c polynomial dual separator in t gives a direct original cap c+2 refutation. Explicit linear conditions characterize affine t-only separators and hence this particular cap-three refutation construction. Their solvability for an infinite family remains open, and their failure would not exclude arbitrary W3 refutations.

Sources checked: exact-boolean-lfd-criterion-review.md; generic-strict-closure-operation-bound.md; exact-boolean-certificate-source-review.md; epsilon-elimination-dual-pencil.md and review. This continues the retained definition/literature audit without a novelty priority claim. No native build, new scientific trial or cloud job occurred.
