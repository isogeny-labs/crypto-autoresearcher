---
name: audit-curve
description: Rigorously audit a specified elliptic curve, its twist, and reachable isogenous representatives for conventional ECDLP, transfer, and implementation weaknesses. Use when asked whether a named or supplied curve is weak, safe, or vulnerable through an isogeny.
---

# Audit a curve

Read `AGENTS.md` and the canonical workflow at
`.claude/skills/audit-curve/SKILL.md` in this checkout, then follow it exactly.
Use `$run` for any launch of an existing scientific experiment; this adapter
does not replace the repository's single public execution skill.

For research goals, follow the canonical skill's [default challenge research loop](../../../docs/challenge-research-loop.md), retaining problem, attempt and review pointers.

For goal-level boundary work, `autoresearch campaign frontier --goal <GOAL-ID>`
shows the fixed comparison domain, reviewed points, remaining gap and next test.
Carry those references; keep measured, modeled and unresolved claims distinct.
