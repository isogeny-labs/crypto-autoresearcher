# PEXT all-degree-two census lacks coefficient-aware executable coverage

- Status: open
- Kind: implementation and interface gap; not a mathematical obstruction
- Goal: GOAL-PEXT-4a1d6b
- Hypothesis: H-PEXT-c3a11d
- Experiment: EXP-PEXT-bf8f96 (review_required; no approval)
- Owner: Coordinator design lane
- Raised: 2026-11-02

The proposed all-map genus census cannot be admitted from the old x-line launcher. Its exact missing obligations are same-curve T-class enumeration, projective exceptional charts, full coefficient square relations and connectedness, descent certificates, full-cohort identity/stabilizer coverage, independent checker, analysis/export, frozen input/source hashes and an actual trial plan/queue/handoff.

The derived quartic identity in [design notes](../experiments/EXP-PEXT-bf8f96/design-obligations.md) is one construction component; it does not discharge those census obligations. Primary sources are accessible and read; their coefficient and hyperellipticity conditions sharpen the implementation requirement. Existing abstract-only knowledge records are not silently upgraded.

Exit criteria: preserve full cohorts, implement and independently check every named obligation, resolve lawful PEXT lane capacity with failed outcomes and continuation preserved, verify exact permitted Executor runtime, freeze the final analysis/protocol/source/input bytes and receive approvable:true from the prospective packet checker. Then publish approval and archives before separate /run.

Next test: complete the same-curve quotient/projective and square-class checker first; use the symbolic identity replay and existing T=O fixtures as instrument tests. No scientific census before freeze. Missing or failing admission is an operational fact, not evidence against P1-P4.

Recheck: actual completed implementation/archive or exact runtime/lane capability change, not periodic no-change polling. The active goal remains active; no official scientific status changes.

## Implementation progress, 2026-11-02

[The native quotient component](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now implements rational points and the general group law, witnessed E(K)/2E(K)
partitions, both projective quotient charts, reproducible field identity, and
geometric/arithmetic square-class relations retaining nonsquare constants.
[Four fixed software tests pass](../experiments/EXP-PEXT-bf8f96/reports/implementation-20261102/software-tests.txt),
including characteristic-three and extension-field fixtures. These replace the
initial absence of those construction components; they do not constitute a
full-cohort census or independent scientific verification.

The remaining implementation path is certificate serialization and an independent
checker, exhaustive actual-curve/structure iteration with scalar-aware transforms,
Frobenius-descent certificates, full-cohort analysis and launch/export bindings.
The original exit criteria and admission requirements remain in force. See the
[implementation report](../experiments/EXP-PEXT-bf8f96/reports/implementation-20261102/report.md).

## Certificate replay progress, 2026-11-02

[The serializer](../experiments/EXP-PEXT-bf8f96/implementation/quotient_certificate.rs)
now emits one actual-curve standard-structure unit, including full point/coset
witnesses, chart images, exact Frobenius conjugates and complete square-class
relations. [The Python checker](../experiments/EXP-PEXT-bf8f96/implementation/check_quotient_certificate.py)
recomputes those finite objects with separate polynomial-basis arithmetic and
requires an external expected field/model. The source-bound software log records
four Rust test groups and six Python methods passing, including five fixed units,
eleven mutation variants, field/scalar/JSON controls and CLI expected-input checks.
This completes the serialization and per-unit checker components within their
stated standard-structure scope; it does not establish full-cohort coverage,
Frobenius descent or independent scientific review.

Next implement exhaustive actual-curve/projective-structure iteration, retaining
binary-form scalar bookkeeping, external frozen field/T identities and exact
coverage/stabilizer certificates. Descent/lift and Type2 checks, original geometric
P3 cohorts and descriptive q13 H1 output, analysis/export/checkpoint and frozen
launch bindings remain required. The original admission/exit criteria and active
goal status remain unchanged. See the fresh
[certificate report](../experiments/EXP-PEXT-bf8f96/reports/certificates-20261102/report.md).

## Projective-structure progress, 2026-11-02

The [core API](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now exposes complete bounded left-coset traversal, normalized coordinate cocycles
and literal scalar-preserving binary-form transport. The
[structure checker](../experiments/EXP-PEXT-bf8f96/implementation/check_structure_certificate.py)
checks distinct cocycles and the exact group index, which certifies complete left
PGL2(Fq) coset coverage, and independently recomputes every transformed coefficient.
The source-bound software log records5Rust,6quotientPython and5structurePython
test groups passing, including the full fixed F27 partition19,656=819*24 and
orientation/scalar controls. This completes the group/coordinate component at its
stated scope; it is no all-curve census or covering-descent certificate.

The present whole-JSON checker is capped at16MiB/100,000structures. Next implement
streaming coverage/partition receipts and full actual-curve/T/projective-structure
joins with exact external identities and scalar bookkeeping, preserving original
cohorts. Frobenius-lift/descent and Type2 checks, geometric P3/descriptive q13 H1
analysis, exports/checkpoints and frozen launch bindings remain required. See the
[fresh structures report](../experiments/EXP-PEXT-bf8f96/reports/structures-20261102/report.md).
Original exit/admission criteria remain; scientific and goal statuses do not change.
