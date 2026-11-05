# Independently replayable quotient certificates, 2026-11-02

The quotient component now serializes a complete standard-structure unit for one actual elliptic curve, and a Python checker independently reconstructs its finite field, rational points, quotient cosets, charts and square-class relations. The checker imports no Rust arithmetic. EXP-PEXT-bf8f96 / H-PEXT-c3a11d remain the same unapproved review_required design; zero scientific census trials ran.

## Implemented certificate interface

`implementation/quotient_certificate.rs` emits the explicit field identity, actual K-model coefficients, complete canonical rational-point list, every rational E(K)/2E(K) representative and coset member with half-point witness P=R+2Q. Each representative binds its exact quotient polynomial and the entire ordered coefficient-Frobenius sequence. It records every geometric relation mask with its constant square-class flag, geometric/arithmetic ranks and nonsquare-constant indicator. Nonzero representatives additionally carry every source-point quartic image, including both infinity branches; T=O is explicitly the baseline cubic chart.

The public serializer can describe one supplied actual curve. Its command-line entry point is deliberately limited to named software fixtures; it is not a scientific cohort launcher. The serialized scope is `one-curve-standard-structure`, not every projective Fq structure.

## Independent arithmetic replay and static review

`implementation/check_quotient_certificate.py` computes with polynomial-basis arithmetic, verifies the monic field modulus is irreducible and validates the supplied primitive/log table rather than using it as its arithmetic implementation. External expected input binds prime, degree, modulus and actual curve coefficients. The checker recomputes the complete curve point set, doubled image, quotient partition and canonical representatives, and verifies every half-point witness.

For charts it independently enumerates the quartic rational points, checks the inverse equation and involution, demands unique images and complete coverage of source and destination points, and distinguishes the baseline cubic chart. For relations it multiplies the original polynomials and constructs a monic square root by descending coefficients; this is a different implementation from Rust support XOR. It recomputes all subset masks and scalar flags, exact ordered conjugates and both ranks. Original binary-quartic leading scalars and projective infinity parity remain represented.

The static review found no blocking source correctness issue within these declared interfaces. Source-side field/coordinate validation, external field-size and file-size ceilings, strict JSON keys, integer types and nonfinite-number rejection are present. A valid standard-structure unit is not a proof of all-curve/all-structure coverage, nor a Frobenius-descent certificate. Producer and checker implementations are separate; these software checks do not constitute independent scientific review or an official mathematical promotion.

The expected-input file intentionally does not pin a particular primitive/log ordering or a separate T representative. The certificate supplies an internally validated ordering and includes all its canonical quotient representatives. Future frozen census inputs must bind exact field representation and expected curve/T identities wherever reproducible canonical ordering is required. This caveat does not change the stated single-unit checks.

## Actual software checks

The source-bound `software-tests.txt` records rustc1.99.1 and Python3.9.25 with exact commands, source hashes and exit statuses. Four Rust test groups and six Python test methods pass, zero failures. Python tests cover five fixed curve certificates (F3 characteristic-three, F5 odd-order, F5 split, embedded F9 and embedded F125), eleven malformed-coverage/witness/chart/conjugate/relation/rank/coset mutation variants, field and expected-input rejection, scalar/projective relation controls, strict duplicate-key/NaN/Infinity/size rejection, and CLI acceptance plus expected-input-mismatch rejection. The harmless Rust unused-reexports warning remains in the raw log.

Fixed fixture expected point/coset counts are respectively6/2,9/1,4/4,12/4,108/4. These counts exercise known software fixtures and are not measurements from the planned scientific census. No new cohort minima, transfer, descent, novelty or performance conclusions are drawn.

## Remaining work and next implementation step

Next, connect the serializer/checker to full actual-curve and projective-structure iteration while preserving transformed binary-form scalars, frozen field/T identities and stabilizer/coverage certificates. Then implement Frobenius-lift/descent certification, Type2 predicate checks, original full-cohort geometric P3 and descriptive q13 H1 analysis, controlled exports/checkpoints and the exact frozen trial plan/queue/handoff. The original experiment remains unapproved until its prospective packet is approvable and its execution route/lane is lawful.

## Sources and custody

The applicable primary mathematics remains the source-bound design review: Iijima-Momose-Chao, ePrint2015/805 sections3.1-3.3, https://eprint.iacr.org/2015/805.pdf ; Chao ECC2007 slides25-26, https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf . The current work is implementation and finite software validation of a specified interface, not a fresh literature/novelty result.

The editable flow diagram marks implemented producers/checks and outstanding census/descent interfaces. Canonical lead-graph scientific edges remain unchanged: no validated all-cohort genus/descent result has been produced. This fresh source/report snapshot is assigned archive TASK-20261102-dfd547; original design and implementation reports/archives retain their bytes and receipts.
