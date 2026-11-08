# One research entry point

Invoke `/autoresearch` (or `$autoresearch` in Codex) to carry out research
without choosing each lifecycle skill manually. Its canonical body is
`.claude/skills/autoresearch/SKILL.md`; `.agents/skills/autoresearch/SKILL.md`
points to the same procedure. The skill invokes existing skills in the current
session; no new CLI command, model runtime or scientific authority is added.

| Request | Behavior |
| --- | --- |
| `/autoresearch continue GOAL-…` | Coordinate that goal and invoke its justified design, run and review stages as needed |
| `/autoresearch run EXP-…` | Run existing prepared inputs and report; stop before scientific review |
| `/autoresearch review EXP-…` | Review that evidence through the existing review procedure, including the formal branch when applicable |
| `/autoresearch design only IDEA-…` | Complete the scoped design procedure and stop |
| `/autoresearch status GOAL-…` | Read-only progress snapshot |

Full-cycle handoffs are conditional on actual artifacts and readiness. The
router resumes after a helper finishes its stage, so coordinate's execution
boundary no longer requires another user command in full-cycle mode. Direct
helper commands keep their existing stopping points. Failed gates still stop
dependent work; an empty queue never expands a named goal to the whole portfolio.

## Sources and validation

The change follows the user request of 2026-11-07. Sources read: `AGENTS.md`
(entry points and role authority), `docs/lab-contract.md` section 3 (one
canonical skill body and matching host surfaces), `docs/skill-routing.md`,
`tools/skill_catalog.py`, and the canonical `coordinate`, `run`,
`design-experiment`, `route` and `review-evidence` procedures. These are internal
retrieved sources. Their existing stage contracts are reused rather than copied
into a new implementation. This is a workflow change; no mathematical novelty
or performance claim is made.

The focused catalog suite and metadata check verify routing and matching
canonical/adaptor entries. An additional static forward-read checked run,
review, design-only, status, full-cycle goal continuation, direct coordinate,
missing custody, no ready tasks and Lean review. That inspection is not a live
research run or independent scientific review. Whole-ledger validation refused
the sparse checkout; no override or scientific-state change was made.

The accompanying evidence-readiness pass found the retained native snapshot for
`EXP-PFIVE-e26798` incomplete. Its additive report and existing linked problem
preserve the custody requirement; the new router cannot bypass it.

The pre-push benchmark gate reports four existing missing `analysis.json`
validation paths for the A11–A14 prime-field benchmark records. Their source
roots were materialized before reporting this; the referenced files are absent
from `origin/main`, and neither those records nor the gate was changed here.
No benchmark ran during this task. These defects remain visible for CI/review.

## Delivery follow-up, 2026-11-08

Full CI on the first PR head passed the ledger, benchmark-record, harness,
runtime, formal and other checks, but both artifact checks rejected the
100,474-byte PDF. The opt-in artifact migration workflow stopped at its missing
push-token check; the label was removed rather than relaxing storage policy.
The renderer now joins a vector Graphviz page to the report and embeds one
font face. The PDF is 47,838 bytes, within the existing Git policy. Extracted
report prose matches the original, and the diagram was rendered and inspected.
The report's scientific content, input pins and custody limitation are unchanged.
