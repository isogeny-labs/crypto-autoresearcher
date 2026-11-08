---
name: ic
description: >-
  Inspect index-calculus artifacts: factor bases, relation quality,
  decomposition metrics, Frobenius phases and independent-rank accounting.
  Use for IC review or experiment design support on synthetic examples; use
  solver for linear algebra and run for trials.

---

# Relation analysis

Read `src/crypto_autoresearcher/index_calculus/README.md` and the selected frozen contract. The package CLI lives in `src/crypto_autoresearcher/index_calculus/__main__.py`; its prime-field implementation is not the binary Koblitz pipeline.

1. Bind the exact curve, subgroup, field model, enumerated factor-base digest, signs/orbit convention and workload. Keep binary and prime-field assumptions distinct.
2. Trace construction, decomposition, harvest, verification, rank updates, final linear algebra and reconstruction through the selected sources. Inspect artifacts before proposing a new engine.
3. Assess total cost per new independent verified relation: include setup, misses, timeouts, duplicates, conversion, verification and rank updates. Report zero-rank outcomes without dividing by zero.
4. Retain relative Frobenius phases/signs and compatibility obligations in quotient presentations. Small input degree, compact representatives or orbit collapse alone do not establish cheaper decomposition.
5. State the parameter scope and transport/scaling assumptions. Keep solver-stage, relation-stage and complete-problem gains separate.
6. Return a stage table, certificate/receipt references, missing costs and the concrete implementation or design change. Use design-experiment for a new trial contract, solver for its algebra, bench for comparisons, and run for execution. Do not synthesize an autonomous production-target attack.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.

## Default challenge research loop

Research goals use [the default challenge research loop](../../../docs/challenge-research-loop.md). Preserve the frozen problem, candidate, evidence and review pointers relevant to this skill. Work within its existing role; findings guide the next attempt, and a worker completion alone is not scientific acceptance.

For goal-level boundary work, `autoresearch campaign frontier --goal <GOAL-ID>`
shows the fixed comparison domain, reviewed points, remaining gap and next test.
Carry those references; keep measured, modeled and unresolved claims distinct.
