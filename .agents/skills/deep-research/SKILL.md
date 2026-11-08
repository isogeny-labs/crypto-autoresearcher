---
name: deep-research
description: "Deeply analyze the whole research portfolio -- ledger, knowledge corpus, and literature -- and produce a ranked, justified shortlist of what experiments to run next. Dispatches idea-generator for fresh divergent candidates and the coordinator for portfolio-wide prioritization, with an optional red-team stress-test of the shortlist. Read-only: writes no ledger record and changes no status. Use when the user asks what to work on next, wants a research roadmap or priority ranking, a goal's next_action needs deeper justification than the mechanical fallback order, or before opening a new campaign against an open question."
---

# deep-research

Read `.claude/skills/deep-research/SKILL.md` from this checkout and follow it. Resolve references and assets relative to that canonical directory. Preserve its authority and execution boundaries; this adapter adds no runtime role.

For research goals, follow the canonical skill's [default challenge research loop](../../../docs/challenge-research-loop.md), retaining problem, attempt and review pointers.

For goal-level boundary work, `autoresearch campaign frontier --goal <GOAL-ID>`
shows the fixed comparison domain, reviewed points, remaining gap and next test.
Carry those references; keep measured, modeled and unresolved claims distinct.
