# Independent source review: binding a freshly verified LFD certificate

Date: 2026-11-09. Source-only review of `attach_verified_lfd.py` and `test_attach_verified_lfd.py`. No tests, certificate replay, production artifact, or scientific execution by this reviewer.

**The binding layer closes the mathematical artifact-link gap without trusting producer result flags or a claimed exact degree. No soundness defect was identified.**

The function first reconstructs and checks the original retained finite-selector maps and every literal S3 coordinate equation through the independently reviewed join. It then requires the certificate's exact variable count and entire equation list to match those parsed original rows, including coordinate-row order and normalized term ordering. A certificate for another ideal-equivalent or merely similarly sized system is not substituted for this presentation.

Only after that equality check does the function call the independent certificate verifier afresh. Exact degree is taken exclusively from its successful return. The verifier's strict schema and integer/mask validation still apply; equality checks alone do not allow malformed Boolean-as-integer masks to pass. No producer status or claimed exact degree is an input to this function.

On successful verification, exact/lower/upper all receive the freshly established degree, including the valid value zero. On verifier budget exhaustion, exact and lower remain null, certificate_verified and bound_labels_admission are false, and only the already justified universal upper bound from the exact polynomial join is retained. Format, equation, or proof failures raise rejection rather than manufacturing an unverified exact label.

The CLI bounds certificate bytes before parsing, rejects duplicate JSON keys, uses exclusive result creation, and binds original parameter bytes, retained artifact bytes, certificate bytes, and implementation/proof source hashes. The declared verification budget excludes loading and original-equation reconstruction, consistently with the actual call sequence.

Dataset admission, group/point lifts, authenticated producer provenance, native instruction counts, and training-cost eligibility remain excluded. Freshly proving a mathematical property of supplied equations is not evidence that the supplied artifact came from a particular production run.

The six fixed controls test the successful synthetic binding, a valid certificate for a different system, a matching equation list with corrupted derivation, verifier exhaustion, altered retained maps, and CLI hash/non-overwrite/duplicate-key handling. I inspected those tests without rerunning their reported passes. No actual production artifact is claimed to have passed by this review.
