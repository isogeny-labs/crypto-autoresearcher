---
name: autoresearch
description: >-
  Carry out research through one entry point. Select and invoke coordinate,
  design-experiment, run, or review-evidence as needed; continue authorized
  full-cycle work through their handoffs. Use for /autoresearch, researching
  a goal, or continuing the research loop. Preserve explicit stage-only scope.
---

# Autoresearch

Use this as the single front door to the research workflow. Read `AGENTS.md`
and preserve the user's repository, question, named IDs, limits and stopping
point. The skills below remain the canonical implementations; load the selected
skill and follow it in this session rather than telling the user to invoke it.
This skill is an orchestrator, not a replacement for role authority, independent
review, committed handoffs, runner admission or archive verification.

## Bind scope and choose the next action

An explicit stage-only request ends at that stage's deliverables. “Run EXP-*”
uses `run` directly; do not add design, coordination, validation or review phases.
“Review”, “design only”, and “status” likewise retain their stated scope.
An unqualified `/autoresearch` or a request to keep a research loop going is
full-cycle: select ranked work with `coordinate`, invoke the next applicable
skill, and resume coordination after its deliverables are durable. A named goal
stays the filter at every step; an empty or impeded lane never widens the scope.

| Current request or required next action | Canonical skill to invoke |
| --- | --- |
| Rank work, resume a goal, approve a complete runnable protocol, archive or synthesize | `.claude/skills/coordinate/SKILL.md` |
| Turn a selected idea into an implemented, frozen experiment contract | `.claude/skills/design-experiment/SKILL.md` |
| Execute an existing prepared experiment, task, goal launcher or command | `plugins/crypto-autoresearcher-harness/skills/run/SKILL.md` |
| Review completed results, theorem fidelity or a proposed scientific conclusion | `.claude/skills/review-evidence/SKILL.md` |
| Read progress without changing records or launching work | `.claude/skills/research-status/SKILL.md` |
| Generate ideas, retrieve literature, or curate knowledge | The corresponding canonical skill in `docs/skill-routing.md` |

Load only the selected procedure and subject sources needed for it. The static
`tools/skill_catalog.py route --intent <intent> --topic <topic>` can locate a
procedure; it does not execute it and is not a required launch preflight.

## Continue through authorized handoffs

1. Complete the literature-first review required by `AGENTS.md`; reuse sources
   already checked in this session when they still cover the next task.
2. Invoke the selected canonical procedure. Keep Coordinator decisions with the
   Coordinator subagent and scientific trials with `run`. A router cannot
   approve its own protocol, replace an independent reviewer, or promote output.
3. For full-cycle work, inspect the actual returned artifacts and next action:
   design/preparation goes to `design-experiment`; an approved runnable launcher
   goes to `run`; completed evidence goes to `review-evidence`; its decision
   returns to `coordinate`. These are conditional handoffs, not a mandatory
   sequence. Existing completed stages are reused, never repeated by default.
4. A stage's instruction to stop at its boundary ends that stage. In full-cycle
   mode, return here and invoke the next skill without another user command.
   Stage-only requests still stop. A failed integrity/admission gate, missing
   approval, conflicting record or required independent review is a real stop
   for the dependent action; record the exact impediment and next check, and
   let the Coordinator rank other work only within the authorized scope.
5. Continue while there is a justified, executable next action within scope and
   owner limits. Do not spin on an unchanged blocker, duplicate another lane's
   live work, invent an experiment to fill a slot, or silently repeat trials.
   Checkpoint before a long run and when handing off, following `AGENTS.md`.
6. Finish at the requested stopping point, completed scoped deliverables, or a
   concrete impediment with no independent in-scope work. Report what was done,
   the evidence and publication paths, and one exact next action. Preserve each
   invoked skill's receipt and reporting requirements.

Examples: `/autoresearch run EXP-…` invokes only `run`;
`/autoresearch review EXP-…` invokes only `review-evidence`;
`/autoresearch design only IDEA-…` invokes only `design-experiment`;
`/autoresearch continue GOAL-…` coordinates that goal and calls the required
design, execution and review procedures without asking the user to switch skills.

Direct invocations of the helper skills remain supported. The `autoresearch`
CLI is a separate executable; this skill does not claim a new CLI subcommand.
