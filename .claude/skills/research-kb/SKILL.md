---
name: research-kb
description: Pointer to the canonical research-kb procedure owned by crypto. Use before prior-art, negative-result, open-problem, exact-theorem or cross-repository lead work, and before a subagent handoff. The full query recipes, field reading, receipt format and fallback are in crypto:.agents/skills/research-kb/SKILL.md; the shared rule is docs/lab-contract.md section 11.
---

# research-kb

The canonical procedure is owned by `crypto` at
`.agents/skills/research-kb/SKILL.md` (commit `bc10008055`). Read it from the
sibling `crypto` checkout and follow it; this file is a pointer, not a second
copy.

The shared `research-kb` MCP server is the cross-repository retrieval layer.
This repository's local `kb/` / `crypto-kb` server remains its derived index.
Use the same triggers, source-ID receipt and score caveats as the canonical
procedure; record the KB `source_id` and `repo:path` in the session log or task
notes.

## Default challenge research loop

Research goals use [the default challenge research loop](../../../docs/challenge-research-loop.md). Preserve the frozen problem, candidate, evidence and review pointers relevant to this skill. Work within its existing role; findings guide the next attempt, and a worker completion alone is not scientific acceptance.

For goal-level boundary work, `autoresearch campaign frontier --goal <GOAL-ID>`
shows the fixed comparison domain, reviewed points, remaining gap and next test.
Carry those references; keep measured, modeled and unresolved claims distinct.
