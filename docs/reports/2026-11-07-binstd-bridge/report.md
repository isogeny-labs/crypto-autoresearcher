# BINSTD n=17 mask-to-polynomial proof

The new Lean decoder proves that the archived field-modulus mask `131081`
denotes `X^17 + X^3 + 1` over `ZMod 2`, and that masks `3`, `313`, and `471`
denote the three polynomials in the existing factorization theorem. Two nearby
reducible-control masks decode to different polynomials. This is an exact
encoding bridge for `EXP-BINSTD-8bdf86`; the frozen experiment was not rerun.

## Sources and statement

- Authoring base: `5b81052e11a7eb671c423e989cc1ef82c445313c`;
  rebased onto main `598f4c6a4fb7fa405ad3a0800fc7456170f0a380` before publication.
- Archived replay evidence: `research/binstd_end_to_end_20261026/evidence.json`,
  SHA-256 `66a5a699ab47f37968b7936015e354d9ac04a587581d802de92bbedbbcce91c6`.
  It records modulus `131081`, factor masks `[3, 313, 471]`, and the
  structural dimension set `[0, 1, 8, 9, 16, 17]`.
- [Lean source](../../../formal/CryptoResearch/Binstd/EncodedPolynomial.lean)
  uses 18 Horner steps: each step takes `mask % 2` as the constant term and
  shifts the remaining mask right by one bit. The bound includes all bits of
  the four archived masks. The [target](../../../formal/targets/binstd-encoded-polynomial.yaml)
  binds the theorem to the archived evidence hash.
- The original checker in the archived pinned source uses bit `i` for the
  coefficient of `X^i`; the source-fidelity reviewer compared that convention
  with the Lean decoder and existing factor declarations.
- Prior work checked before this patch: the existing
  `Factorization.lean`, `EncodedDivisors.lean`, `CanonicalFrobenius.lean`,
  and the open-problem record, plus Mathlib's pinned polynomial source. The
  finite divisor certificate already checked encoded arithmetic but explicitly
  lacked a polynomial-decoding theorem. This patch fills that named gap; it
  makes no novelty claim about finite-field theory.

## Checks

The exact workspace pin is Lean **4.35.0**, Mathlib
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`, and CryptoLean
`60952c696ded7f3da4f4517006d9af6482662487`. The inherited handoff note
said `4.35.0-rc1`; attempting Mathlib's cache helper with that older release
failed in `Cache/Requests.lean` because its Lake API differs. The repository's
current `lean-toolchain` was read back before the successful check; the failed
rc1 setup is an environment mismatch, not a theorem verdict.

`lake build CryptoResearch.Binstd.EncodedPolynomial` passed (3,139 jobs in
the dependency graph); see [target-build.log](target-build.log). The three
theorem axiom queries passed and reported only `propext`, `Classical.choice`,
and `Quot.sound`; see [axioms.log](axioms.log). The target YAML parsed through
the repository's `task_from_spec` loader. The module and target contain no
`sorry`, `admit`, custom `axiom`, or `unsafe` declaration.

Two separate read-only reviews checked the theorem statement. A blind
arithmetic reviewer expanded the masks independently and found all equalities
and the 18-bit bound correct, with no hidden premise. A source-fidelity
reviewer matched the evidence file hash, the original checker convention, and
the existing factor definitions. Both reviews passed at the precise
mask-decoding scope. The control theorem was added after those reviews and
checked by Lean; its arithmetic is `131073=2^17+1` and `257=2^8+1`.

The full repository verifier was started, then stopped before completion when
its unconstrained Lake build launched many Lean workers. The host check still
showed 106 GiB available, but a safe peak and exclusive memory budget for
hundreds of jobs could not be established. There was no OOM. The full workspace
axiom audit and target receipt are therefore **pending**, and hosted current-head
CI must supply those gates before merge. The focused build is the local machine
verification recorded here.

## Claim boundary and next proof step

This theorem identifies exact integer masks with exact polynomials. It does
not establish that the encoded XOR remainder equals Euclidean remainder,
that `X^17 + X^3 + 1` is irreducible, that the runner's polynomial-basis
field is equivalent to canonical `GaloisField 2 17`, or that every
Frobenius-invariant subspace has a dimension in the archived set. Those
obligations remain in the [open problem](../../../problems/binstd-frobenius-invariant-dimension-lean-bridge.md).
The next formal construction is a field-isomorphism and Frobenius-action
bridge, followed by the factor-kernel subspace classification.

The [scope diagram](scope.svg) records this proof boundary. Because this is a
structural proof step with no new performance measurement, the archived yield
plots and live performance dashboards retain their values.
