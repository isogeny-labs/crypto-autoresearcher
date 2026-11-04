# Xedni: Sadek explicit local-test cutoff needs a complete repair

- **Status:** open
- **Kind:** proof gap; independent verification outstanding
- **Affected work:** RQ-XEDN-3bfe2e; H-XEDN-292264; [audit](../docs/reports/xedni-sadek-20261101/README.md); #1985
- **Next action owner:** Coordinator to assign independent reviewer; no reviewer dispatched
- **Last updated:** 2026-11-01

## Problem

The displayed prime cutoff cannot be justified by the audited proof step,
because |n|<=C and prime ell|n do not imply ell<=sqrt(C).
This blocks use of that cutoff as a dependency certificate for supplied
rational data, not the underlying local-to-global principle.

## Evidence and uncertainty

- Observed: imported earlier command/output in the linked audit; no harness RUN.
- Derived: n=ell=C=3 refutes the inference; in rank one the height formula gives C=|n|.
- Derived conditionally: the larger integer expression M_star dominates the
  degree expression when ell<=B and k<=K. This does not prove those hypotheses.
- Suspected explanation: possible normalization/typographical issue, unverified.
- Missing capability: independent audit of Kummer fields, integer k and zero/unit cases.
- Not established: theorem falsity, complete replacement cutoff, arbitrary-target
  lifting, dependency discovery, or measured construction cost.

## What would unblock it

- [ ] Independently check the source definitions and prime-divisor inference.
- [ ] Supply admissible integer field exponents and justify their uniform bound.
- [ ] Handle zero/unit coefficients and empty index sets explicitly.
- [ ] Prove the complete test-prime set suffices, with every theorem hypothesis.
- [ ] Verify a certificate/recovery interface and charge all construction/search costs
  before using the result in a lifting pipeline.

The first four items would qualify a repaired supplied-data cutoff. They would
not construct compatible dependent lifts; that original requirement stays open.

## Next discriminating step

Audit H-XEDN-292264 independently. The report proposes a fixed exact-integer
grid and equality/invalid-domain controls, not a launched scientific run.
Any valid-domain counterexample rejects the implemented domination; a clean
grid leaves the number-theoretic bridge open. An infrastructure failure is
recorded separately. Recheck on an author erratum or an independent proof.

## Resolution and history

2026-11-01: additive tracking snapshot. Unresolved. No historical evidence,
research status or frozen protocol is changed. Merging this PR resolves none
of the mathematical exit conditions.
