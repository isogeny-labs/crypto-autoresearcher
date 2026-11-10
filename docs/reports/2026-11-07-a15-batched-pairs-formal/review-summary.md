# A15 batched-pair algebra: technical review summary

This is a scoped proof review of `CryptoResearch.PrimeField.BatchedPairs.a15_algebraic_joints` at producer commit `bafd5233baef85efa1afa5a385fe3d5cc5d3235f`. It does not change an official experiment or hypothesis status.

| Claim joint | Machine status | Independent review | Outcome |
| --- | --- | --- | --- |
| Child inverses from one inverse of `x*y`, with `x ≠ 0` and `y ≠ 0` | Passed named Lean build and axiom audit | Blind symbolic derivation and 208 finite input pairs; source mapping to `batch_query.py:36-49` | `validated_scoped` for the field identity |
| Four signed affine candidate outputs from two slopes | Passed named Lean build and axiom audit | Blind symbolic derivation and 17,764 finite formula tuples; source mapping to `pairbuild15.py:99-126` and emitted order | `validated_scoped` for the formula identity and inspected local source correspondence |
| Complete product tree, uint64 implementation, curve addition, scalar parity, and retained A15 run | No theorem or machine audit of these bridges in this target | Source reviewer identifies each missing bridge; equal-x controls disprove a widened geometric reading | `not_reviewed` or `needs_revision` if attributed to this theorem |

The full verifier retry passed on the pinned workspace with `build_passed=true`, `axiom_audit_passed=true`, `forbidden_constructs=[]`, and axioms `propext`, `Classical.choice`, `Quot.sound`. The earlier 120-second build timeout is preserved. The source reviewer independently matched all 104 workspace hashes and 10 verifier hashes in the passing receipt. The reviewer's fresh Lean command failed before elaboration because its toolchain was absent, so that session supplies no additional machine pass.

The precommitted `review-plan.md` transcribed the Lean file SHA-256 without its final `e`: it says `a25ec80d038925424f377eec7a5caa55a92f9dc756893edfd07df0bccda94e9`; the actual file and both verifier receipts say `a25ec80d038925424f377eec7a5caa55a92f9dc756893edfd07df0bccda94e9e`. The plan is retained unchanged; this addendum and the source report correct the transcription. The target and Python source hashes in that plan match.

The blind reviewer read only the assigned isolated packet with SHA-256 `940de8dd1b0be02aa7f0e4349b1f1ccf066420d919fdc9ad427ff00a4aff9145`, and neither reviewer read the sibling report before filing. Both reports record their controls and access attestations. `independence-check.txt` records a PASS from `check_review_independence.py` over the two reviewer-authored YAML sidecars. The checker verifies declared consistency, not actual session isolation. The machine-readable plan was transcribed after review from the precommitted Markdown plan; it cannot establish prospective timing by itself. The immutable plan, isolated packet, report hashes and reviewer attestations supply that process evidence. A future review round should use the tool's structured schema before dispatch.

The checked canonical progress graphs in `docs/benchmarks/progress/` track experiment results, not pure algebraic proof scope. No measured value or official decision changed in this packet, so those graphs are left unchanged. The accompanying `diagram.svg` and inspected `report.pdf` show the theorem's exact local joints and open bridges.
