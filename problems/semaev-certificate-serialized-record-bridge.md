# Semaev certificate serialized-record bridge

- **Status:** open
- **Kind:** experiment-to-theorem interpretation and execution gap
- **Affected work:** `THM-SEMAEV-FALL1-LEMMA-3`, [independent fidelity review](../docs/reports/2026-11-08-semaev-certificate-fidelity/technical-review.md), [fresh machine addendum](../docs/reports/2026-11-08-semaev-certificate-fidelity/fresh-machine-addendum.md), and [J2 source/type report](../docs/reports/2026-11-08-semaev-certificate-fidelity/reviews/TASK-20261108-f75797/report.md)
- **Next action owner:** Coordinator to freeze the interpretation contract; formal and verifier maintainers to implement and independently review it
- **Last updated:** 2026-11-08

## Problem and evidence

The named Lean theorem decides finite decomposition for already typed
`W.Point` inputs over the span of the supplied finite family. The reviewed
raw-coordinate predicate accepts already typed `K × K` coordinates under
`W.IsElliptic`. J1 independently reconstructed the mathematical predicate;
J2 found it faithful at those boundaries. The fresh hosted [Lean run
42446577502](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42446577502)
machine-verified the named typed theorem on the pinned source. These facts
support the scoped mathematical statement.

The theorem and its receipt do not show that a producer's serialized
certificate has been decoded into those exact arguments or checked. J2
identified six independently checkable bridges:

1. **B1, bytes to coordinates:** define one unambiguous record format and a sound decoder from bytes to field coordinates; reject malformed, truncated, ambiguous, and out-of-range encodings.
2. **B2, concrete fields:** bind the producer's modulus, extension representation, byte order, arithmetic, and base-field embedding to the Lean `F`, `K`, and `Algebra F K` instances, with operation-preservation checks.
3. **B3, curve:** bind the record's curve coefficients to `W` and establish `W.IsElliptic` for use of the raw-coordinate checker.
4. **B4, factor-base subspace:** bind the recorded finite family to the checker input and prove that its span is the intended `V`; prove independence only if a dimension or basis claim needs it.
5. **B5, tuple and target:** bind every summand, tuple length, challenge association, and target, including any infinity tag, to the checker's arguments.
6. **B6, execution or refinement:** run the instantiated Lean checker on the bound record with authenticated evidence, or check a native verifier refinement to the Lean predicate and state the compiler/evaluation trust boundary.

The review also found that its own frozen independence plan and attestations
do not pass `tools/check_review_independence.py`; the failed transcript remains
in the review packet. A new prospective round must preflight checker-compatible
joint names, a recognized attestation format, and a protected-path list before
any new reviewer starts. The archived verifier input map omits its imported
`orchestration/fast_yaml.py` helper and external YAML parser dependency;
software-input closure needs repair. None of these findings is a counterexample
to the scoped typed theorem.

## Exit criteria and next discriminating step

Freeze a versioned wire-to-Lean interpretation contract before trying a
producer record. Bind one immutable sample record and its source/run manifest;
test B1–B5 with positive and negative controls that mutate the field, curve,
family, tuple, target, and record encoding separately. Then satisfy B6 with a
source-bound checker execution or verified native refinement. Independently
replay the bound record and include the parser's transitive inputs in the
receipt. A new prospectively valid independence round must pass its composition
checker before a `validated_scoped` review outcome is assigned.

If decoding or parameter binding fails, retain the exact rejected case and
repair that bridge without changing the frozen record. If all bridges and the
independence gate pass, the specific bound record can be adjudicated; any other
record still needs its own binding and execution evidence. No new cloud trial
is needed to specify or test the decoder on the immutable sample.
