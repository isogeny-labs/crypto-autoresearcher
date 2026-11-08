---
name: route
description: >-
  Choose skills and tools when asked what to use, where a technique lives, or
  which binary implements it. Use for repo orientation and skill selection.
  Explicit experiment execution goes directly to run.

---

# Choose a workflow

Read `docs/skill-routing.md` and `docs/skill-catalog.json`. Use `python3 tools/skill_catalog.py list` for the exact catalog; use `route --intent inspect --topic endo` to inspect a declared intent/topic pair. This selector performs no execution.

1. Preserve the user's named repo, goal, experiment, tool, artifact, and stopping point.
2. Route an explicit run request directly to `run`; do not insert this skill as a prerequisite.
3. Separate intent from subject. Choose one primary lifecycle skill and, where helpful, one subject profile. A subject profile never overrides execution or official review authority.
4. Consult `docs/skill-tool-inventory.json` for audited path ownership. Distinguish libraries, source entry points, installed console scripts, native sources, historical scripts, and pending PR code. Verify an actual binary or installed command in the current checkout before claiming availability.
5. Open the selected canonical SKILL.md, then only the sources needed for this task. Report the chosen skill, reason, exact entry point, and any missing implementation.

Use `skill_catalog.py check` when maintaining the catalog, not before a scientific run. A catalog entry is a navigation aid, never a mathematical or performance certificate.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.

## Curvesmash challenge context

Discover Curvesmash objectives with `autoresearch research challenges`; inspect `research challenge <track>` and use `research template --challenge <track>` for task preparation. Route by the requested lifecycle action; the challenges topic never turns discovery into execution.

See [the shared challenge workflow](../../../docs/research-challenges.md) for the lifecycle and evidence boundaries.
