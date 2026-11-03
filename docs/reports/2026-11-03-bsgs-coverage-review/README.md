# BSGS runbook coverage: independent formal review

The exact Lean coverage theorem holds at the frozen target's arithmetic scope. Three independent reviews checked its named hosted receipt, derived the quotient and remainder bounds, and counted the toy curve independently. The source-to-code bridge breaks for the identity input: `solve.py --mode known-k --k 0` raises `TypeError` before producing a result. The checker also accepts a synthetic record from a directory where the solver never ran. These findings do not alter the 14 frozen runbook outcomes, which all pass their pinned checks.

## Bound inputs and review method

- Source tree: `7c028ce9ccdec6c1ee7d4c2b3b60120ed3dcbd9e`; theorem SHA-256 `867ce0f37099a30b34ce7d603549eb8b28f16b1c17183119657715108f79d9d0`; target SHA-256 `1dbdf3d94890283a35f6c494fbd7a2c7e06a8cbe18f29f7a09b274ffb41e083a`.
- The prospective [plan](review-plan.yaml), [input bindings](input-bindings.json), and separate [handoffs](handoffs/) were committed before reviewer dispatch. J3 used a detached, statement-only snapshot; its original output and checksum are retained under [its review directory](reviews/TASK-20261103-016b84/).
- The named GitHub Lean receipt came from run `41698891260`, artifact `13264657224`, SHA-256 `32224d224d2ab71c7e383907ba22e1e324a6794d54354442f75451b100754cca`. J2 checked all 11 bound inputs, 89 workspace inputs, 10 verifier inputs and 10 dependency pins. Lean 4.35.0 hosted build and named axiom audit passed; the local nearby 4.35.0-rc1 check reproduced the type and listed only `propext`, `Classical.choice`, `Quot.sound`. This is pinned receipt and source consistency, not independent runner execution authentication.
- The three first verdicts were frozen before comparison. `tools/check_review_independence.py` passed on their attestations. J3's original YAML had an unquoted colon in a prose `sources_read` item. [The checked copy](reviews/TASK-20261103-016b84/review_attestation.checked.yaml) only quotes that item to preserve its string type; the original and its checksum remain unchanged.
- J1's original report had two Markdown hard-break trailing spaces, which repository whitespace admission rejects. The exact frozen bytes (SHA-256 `a6b4115e73d22fa34e356db10dc2930cae7f313351221b61204281c09f815ab6`) are preserved as [REPORT.frozen.md.gz](reviews/TASK-20261103-594c2a/REPORT.frozen.md.gz); the readable report removes only those two spaces, and its manifest was recalculated. No verdict or substantive text changed.

## Findings by joint

| Joint | Result | Evidence |
| --- | --- | --- |
| J2 named theorem | Holds at arithmetic scope | For `m>0` and `k<m*m`, quotient and remainder are below `m` and reconstruct `k`; false-boundary controls at `m=0` and `k=m*m`; [report](reviews/TASK-20261103-6390df/REPORT.md). |
| J3 blind derivation | Holds at mathematical curve scope | Independent character sum gives `#E(F_1048571)=1047689`, prime; nonidentity `G` generates the curve; `1024²≥n`, while width `1023` misses 1160 points; [report](reviews/TASK-20261103-016b84/REPORT.md). |
| J1 source and code bridge | Breaks for all-point and executed-count claims | Frozen 14 units pass, but `known-k=0` crashes; a fabricated raw result and arbitrary `setup_ops` pass the checker; actual addition calls 1156 versus reported `group_ops+setup_ops=1157` on the positive control; [report](reviews/TASK-20261103-594c2a/REPORT.md). |

The statement covers natural exponents `0≤k<m²`; it does not state a solver postcondition or an operation-count guarantee. The curve premises connect arithmetic coverage to all curve points mathematically. The implementation needs a consistent identity encoding and an independently verified execution trace before a curve-wide solver or executed-count statement can be attached. The existing frozen runbook results remain historical records.

The [evidence diagram](evidence-flow.svg) distinguishes those paths. [Report PDF](report.pdf) was generated from [LaTeX source](report.tex) and inspected. No scientific ledger status is changed by this technical review.
