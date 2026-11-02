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
