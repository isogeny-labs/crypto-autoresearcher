# Semaev decomposition certificate: fresh hosted machine result

This addendum records the result of the fresh run that was still pending when
the [independent fidelity review](technical-review.md) was written. It leaves
the sealed review reports and the review's scientific outcome unchanged.

## Exact run and artifact

- [Lean verification run 42446577502](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42446577502) completed successfully on source commit `e5569428e5e53145f123f3aeb36de00591ad72b6`.
- GitHub artifact `formal-verification-receipts` (ID `13603993525`) is 1,908,138 bytes. Its published SHA-256 and the independently downloaded ZIP's SHA-256 both equal `181433aeee8e030b0d33787e4d72e95d69ca9e59212abd6de864a48257cf3897`.
- The target receipt is `semaev-decomposition-certificate.json`, for `TASK-20260916-b55948` and `THM-SEMAEV-FALL1-LEMMA-3`. It names `CryptoResearch.Semaev.decidable_validDecomposition` in `CryptoResearch/Semaev/Certificate.lean` and reports `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, no forbidden constructs, and `semantic_review.status: pending`.
- The receipt binds the theorem file to SHA-256 `aa022e4829eefc2cbe9ac05cbeb39f81e9e3eaa8147e2e41e9d718f11976bd89`, target spec to `3a8dc16449c2615c85c93bc92a3137435f1a367fb97a18729e6da6304554d7e6`, and declared source to `11b61f4f4bdaed0c323ec852f19fc4c0a7ff3972715bfe637604fb675db7fee4`.
- `dependency-pins-before.json` and `dependency-pins-after.json` are byte-identical, with SHA-256 `a6aabda3c7d7ec70273d263c02bf8acead8cf3e6282f803b4c7a729c872114b8`. The log reports a full workspace build and a 1,313-theorem project axiom audit using only standard axioms; the target axiom audit passed. The pinned Lean version is 4.35.0.

The named typed theorem has fresh machine evidence on the pinned source and
toolchain. This run does not discharge the review independence checker failure,
the raw-coordinate supplemental lemma's separate controls, or the six bridges
needed to interpret and check a serialized producer record. The operational
gap is tracked in the [serialized-record bridge problem](../../../problems/semaev-certificate-serialized-record-bridge.md).
