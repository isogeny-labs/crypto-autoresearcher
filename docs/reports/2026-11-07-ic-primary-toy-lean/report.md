# Primary n=13 IC toy-curve Lean certificate: technical review

2026-11-07 UTC. Claim `IC-PRIMARY-N13-ENCODED-SCALARS-20261107`;
Conductor producer T-1863. Producer input commit `83d750c7a0`, with a
pre-review addendum and result-blind input frozen at `849ece7240`.

## Finding at the encoded-computation scope

Lean 4.35.0 checks the closed theorem
`CryptoResearch.IC.PrimaryToyCurve.primary_archive_certificate`: the
polynomial mask equals 8231, G=(2995,1571) satisfies the encoded equation,
`scale 2003 G = none`, and the three recorded scalar-to-point equalities hold.
The theorem rejects three adjacent scalars and one altered coordinate. The
named theorem and helpers report only Lean's standard `propext` axiom.

| Archived scalar | Independently derived encoded point | Workload |
| ---: | --- | --- |
| 1046 | (2659,1282) | `026858681e66` |
| 606 | (6749,6034) | `398002869ca3` |
| 861 | (4412,6211) | `aa4b90819f2f` |

The source-fidelity review at `reviews/fidelity.md` checked cryptanalysis
commit `612427ead3d47565b92da3e663739d5c17ce71ed`, source hashes, the
elaborated statement, definitions and negative controls. The separately coded
algebra review at `reviews/algebra.md` recomputed the finite arithmetic and
also exhaustively checked the inversion exponent for all 8191 nonzero field
encodings. Its frozen outputs match the three workloads and controls.

The first algebra reviewer read the full prospective Markdown plan, whose
favorable Coordinator prior exceeded the plan's narrower read allowance.
The independent computation remains a cross-check, but its result blindness
was weakened. `blind_addendum.md` discloses the deviation and freezes a
minimal input with no expected target coordinates for an additional review.
The third reviewer froze `reviews/strict-blind.md` before seeing any expected
outputs. Repeated addition and a separate binary double-and-add schedule
agreed for ten scalars. Their independently derived outputs are identical to
the three target rows and all adjacent controls above; the altered point's
curve residual is 2658. The strict report SHA-256 is
`3e64d272a1106128872ec657e6b5350223fb00a18e39cc2295f3bc717c5a3833`.
Conductor T-1868 shows `cancelled` after the report was frozen and the claim
released; the report and its hash remain the technical evidence, while that
administrative task state is retained as a limitation of the workflow record.

| Dimension | Scoped result |
| --- | --- |
| Machine status | `passed` for exact local Lean 4.35.0 declaration and named axiom audit; full hosted workspace gate pending at publication time |
| Fidelity | `faithful_scoped` for fixed encoded source constants and closed target equalities |
| Review outcome | `validated_scoped` for these finite computations after strict blind comparison; generic field, group-law, implementation and historical-run claims remain unreviewed here |

## Verification and custody

- Formal source: `formal/CryptoResearch/IC/PrimaryToyCurve.lean` SHA-256
  `a03b27a49db206f14dc6be74b0624ebb48e9270c6708b8cd70452d82bf5cd187`.
- Target spec: `formal/targets/ic-primary-toy-curve-20261107.yaml` SHA-256
  `6bad93d3952b537f7d53faca796ee4ea2c12310ef18781d5aa5d823eb37c9137`.
- Archived primary source: `experiments/ic-bench/baseline/primary.jsonl`
  SHA-256 `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973`;
  the three workload hashes and exact source-to-theorem mapping are in
  `source.md` and the independent fidelity report.
- `machine-check.json` preserves the exact direct Lean 4.35.0 commands,
  exits, output and hashes. The hosted full Lake workspace gate is required
  before merge.
- `reviews/algebra.md` SHA-256
  `e2c75e21f8c7b97377017ab819dcc77c661b59ccb7c2351290901e79857eee4b`;
  `reviews/fidelity.md` SHA-256
  `4cc7c5985f05b62c99aafeeb82704af6b8b5313782ea8095f196a6fe0f5adcde`.

`tools/check_review_independence.py` returned exit 2, `no review_plan block`,
because the precommitted plan and signed-off reports are Markdown while the
checker requires YAML `review_plan` and `review_attestation` blocks with
`TASK-*` IDs. Actual Conductor IDs are `T-*`. The check is **not passed**;
the precommitted plan, reviewer read lists, report hashes and task receipts
are retained for manual review. No translated YAML is represented as a
prospective plan.

## Claim boundaries and next obligations

This is a finite certificate for the defined 13-bit arithmetic and affine
formulas. It does not prove the polynomial irreducible in Lean, the point
formulas form a group law for every point, exact generator order 2003, or
extensional equivalence to the historical cryptanalysis implementation.
It does not authenticate the nine process executions or wall-clock and
operation-count measurements. Those require distinct source and receipt
reviews before a broader historical or performance claim.

![Source-to-certificate claim boundary](proof-flow.svg)

The figure displays the source, encoded model, Lean certificate and separate
evidence obligations. It is a proof-flow diagram, not a performance plot.
