# Semaev decomposition certificate: prospective independent review

**Reviewed claim:** `THM-SEMAEV-FALL1-LEMMA-3`, target
`formal/targets/semaev-decomposition-certificate.yaml`, named theorem
`CryptoResearch.Semaev.decidable_validDecomposition`. The [prospective
plan](../review-plan.yaml) was published at commit
`8a7434f59f3795d2f803ddaafc665e917aaf44c0` before J1, J2, or J3 began.
The claim source, target, theorem, Lean toolchain and Lake manifest retain
their [pinned hashes](../review-plan.yaml) on the reviewed main commit
`3444ed998838e097134bd8e5a7fbd1035a90f9a1`.

## Scoped result

| Claim boundary | Machine evidence | Independent semantic evidence | Review outcome |
| --- | --- | --- | --- |
| Finite decomposition decision for already typed nonsingular `W.Point` summands and a supplied finite span family | Hosted named target passed a full workspace build and axiom audit | J1 derived the predicate and worked F5 controls blind; J2 matched the source to the theorem's declared curve, span and point sum; the prior source review checked the pinned Mathlib point model | **`validated_scoped`** for this typed mathematical predicate, with the supplied family defining `V` |
| Raw `K × K` coordinate lemma under `W.IsElliptic` | Its module compiled, but this run did not name or print a separate axiom audit for the raw lemma | J2 inspected its equation/span/sum statement; J1 derived the corresponding raw predicate | **`inconclusive`** pending a named raw-theorem type and axiom check |
| Checking a producer's serialized certificate or native verifier result | No source-bound record execution or checked native refinement | J2 found the byte, field, curve, span, tuple/target and execution bridges absent | **`needs_revision`** for that operational extension |

The [evidence-boundary diagram](evidence-boundary.svg) shows the exact boundary.
No experiment, performance claim, hypothesis status or official evidence
decision changes in this technical packet.

## Machine and source checks

- J1's [source-blind report](../reviews/TASK-20261109-f0444b/report.md) derives a finite coefficient enumeration and exact iff. Its F5 controls distinguish empty tuple, empty span, on-curve and off-curve input, identity summand, and wrong target. Its sole input was the isolated [blind card](../blind-card.md), SHA-256 `16aea5ff762f1c4436da2321a3cd9f8942a166c3e858d50aad6535370744e800`.
- J2's [source/type report](../reviews/TASK-20261109-14bd43/report.md) matched source, target and theorem SHA-256 values and found the typed decision faithful at its declared-span boundary. It could not inspect a local copy of the pinned Mathlib point source in this round; the [prior pinned review](../../2026-11-08-semaev-certificate-fidelity/reviews/TASK-20261108-f75797/report.md) inspected that source separately. J2's operational verdict is `breaks` because the reviewed module never binds a serialized producer record to its arguments.
- J3's [machine report](../reviews/TASK-20261109-bcd27d/report.md) authenticated [run 42446577502](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42446577502), formal job `128626693105`, artifact `13603993525`, and ZIP SHA-256 `181433aeee8e030b0d33787e4d72e95d69ca9e59212abd6de864a48257cf3897`. The named receipt reports `machine_verified`, a successful build, 1,313 standard-axiom-only theorem audits, a passing target axiom audit, and no forbidden constructs. Source/spec/theorem/toolchain/manifest hashes and before/after dependency pins agree. There was no separate binary/kernel recheck.
- J3's [negative controls](../reviews/TASK-20261109-bcd27d/controls-results.json) reject a wrong theorem name and changed source or theorem hashes. A self-consistent synthetic success log is accepted by receipt-consistency checking, so the GitHub run/job and artifact digest are essential execution evidence; the receipt alone would not authenticate an execution.

## Independence and custody

The three reviewers worked in separate sessions and did not read sibling
reports. J1 received only one isolated card; J2 read pinned source and proof;
J3 read pinned run and verifier inputs. Their original outputs, corrections,
seals and control files are preserved byte for byte in
[`review-source-packets/`](../review-source-packets/). The directly browsable
[`reviews/`](../reviews/) copies contain the final report and attestation
bytes used by the composition checker.

The first J1 and J2 attestations used YAML shapes the checker did not discover;
J1 also initially represented `sources_read` as a mapping rather than path
strings. The reviewers issued formatting-only additive corrections with
unchanged reports, verdicts and source reads. The [initial failure
transcript](initial-independence-check.txt) and every original seal are retained.
The exact published plan SHA-256 is
`cdd84e056697a38fcd0df3e3bc6a785dde82761cbd9c6f84e02681d6bc06a01e`.
The [final checker transcript](independence-check.txt) reports three reports,
every joint owned and attested, blindness respected, and controls declared.
This is a structural independence check; its truth still rests on the
reviewers' source-read attestations and isolated inputs.

## Next construction

The [serialized-record bridge problem](../../../../problems/semaev-certificate-serialized-record-bridge.md)
specifies B1–B6. Freeze a wire-to-Lean interpretation contract, bind one
immutable producer record and its run manifest, and test independent mutations
of field, curve, family, tuple, target and encoding before executing the
instantiated decision. Separately name and axiom-audit
`validRawDecomposition_iff_curve_span_sum` on exact pins. A passing bound
record would establish that record's check, not all historical certificates.

The [editable diagram](evidence-boundary.svg) and [inspected PDF](report.pdf)
summarize this review. Scientific graphs and the performance dashboard are
unchanged by this proof review because it adds no measurement or decision.
