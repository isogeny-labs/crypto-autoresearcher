# A15 batched-pair algebra: review plan

Prepared before independent reviewer dispatch. Producer base: crypto-autoresearcher main `d4cf45f012a0208b179d947052cb47b82f06ee09`. Source: `research/prime_field_a15_execution_20261107/pairbuild15.py` SHA-256 `c8cbe4ab864157ff4c4c4f0b0414950847e7de0355585199629778c50280f55a`, and imported `research/prime_field_a12_execution_20261106/batch_query.py` SHA-256 `30f20fc9c8c276d2c2f90881b48f8a33ca6d32d9b67ec60a70580a241b30f72b`. Draft theorem `formal/CryptoResearch/PrimeField/BatchedPairs.lean` SHA-256 `a25ec80d038925424f377eec7a5caa55a92f9dc756893edfd07df0bccda94e9`; target SHA-256 `dc1239267fbd3f0f70b25252ed4335613df64ec5d771fdab3512574db3c2b37a`.

## Claim and prior

The producer claims exact finite scalar/batched parity for the retained A15 pair construction, including product-tree inversion and sign reuse. My expected algebraic identities are sound over a field with nonzero child values. I do not infer that this theorem authenticates the NumPy implementation, curve geometry, counts, or the original run. The independent review must decide the precise correspondence.

## Joints and attacks

1. **Machine theorem and hypotheses — source reviewer.** Recheck the named declaration, pins, axiom log and proof source. Attack by dropping a nonzero child hypothesis: with `x = 1, y = 0`, the left-child identity would assert `0 = 1`; with `x = 0, y = 1`, the right-child identity would assert `0 = 1`. Check that those assumptions remain in the elaborated type.
2. **Code-to-formula bridge — source reviewer.** Compare `batch_query.py:36-49` and `pairbuild15.py:99-126` to the theorem's two inverse identities, slope formula and output order. Attack with an equal-x pair, a zero product-tree input, a sign-order swap, and overflow at the largest allowed modulus. Separate algebraic formula validity from point-on-curve and uint64 execution.
3. **Independent algebra — blind reviewer.** From the supplied definitions and requested statement alone, rederive the inverse propagation and sign-reuse identities without reading the producer Lean, Python, target, receipts or source review. Find a concrete zero-input or equal-x counterexample to any overbroad interpretation. State which statements hold in an arbitrary field and which require curve assumptions.

Known-false controls are the dropped nonzero assumptions above and any claim that the candidate pair formula is a geometric curve sum when `xj = xk`. A proof of a formula at equal x would prove too much about geometry. The exact finite A15 run and operation counts remain outside this review. [pcc:unverified]

## Independence and inputs

Source reviewer may read the producer files and machine receipts, but not the blind report before filing. Blind reviewer receives only `blind-input.md` in an isolated packet and may not read the repository, source files, proof text, target spec, logs or sibling report before filing. Each reviewer records actual reads, joint ownership, attestation, controls and a `holds | breaks | inconclusive` verdict. Reports remain separate until both are filed. [pcc:unverified]

## Machine evidence and next gates

Pinned toolchain: Lean 4.35.0, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`. Direct module build and `#print axioms` passed with only `propext`, `Classical.choice`, `Quot.sound`. First full verifier timed out in a large existing Semaev build; its receipt is preserved as an infrastructure failure. Cached retry passed the full build and named axiom audit; receipt says `machine_verified` and `needs_semantic_review=true`. The reviewer reports, independence check, source-to-claim table, rendered report and current-head CI are required before this packet can claim `validated_scoped`.
