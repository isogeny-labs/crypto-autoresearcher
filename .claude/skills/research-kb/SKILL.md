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

## Curvesmash challenge context

For work linked to a Curvesmash objective, use [the shared challenge workflow](../../../docs/research-challenges.md) and preserve the track id and pinned source references. Apply this skill only within its existing role and the user's named scope.
