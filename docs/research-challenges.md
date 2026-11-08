# Open research challenges

Curvesmash's six registered targets are research objectives in the autoresearcher
harness. Discover a problem, inspect its exact contract, then carry it into the
existing question, proposal, design and execution lifecycle:

```sh
autoresearch research challenges
autoresearch research challenge secp256k1-ecdlp
autoresearch research template --challenge secp256k1-ecdlp > research.json
# Fill procedure and evidence_plan with the concrete proposed method.
autoresearch research validate research.json
autoresearch research brief research.json
```

The commands emit JSON to stdout without changing the ledger or starting work.
They work with the base installation; `python3 -m orchestration research ...`
is equivalent. Both a bare track and `curvesmash/<track>` identify a challenge.
An unknown track fails. The scaffold deliberately fails validation until its
procedure and method-specific evidence plan are filled. `--method` selects any
supported research method and defaults to `theoretical` for a challenge draft.

## Objectives

| Track | Research problem |
| --- | --- |
| `secp256k1-ecdlp` | Recover the scalar from a uniform secp256k1 point |
| `p256-ecdlp` | Recover the scalar from a uniform P-256 point |
| `bls12-381-g1-ecdlp-plain` | Recover the scalar from a uniform BLS G1 point without auxiliary powers |
| `bls12-381-g1-ecdlp` | Recover the scalar using its public G1 powers; score W(n) at n=2^20 |
| `bls12-381-fixed-g1-invert-g2` | Given P and z, return Q such that e(P,Q)=z |
| `bls12-381-fixed-g2-invert-g1` | Given Q and z, return P such that e(P,Q)=z |

Each entry gives the protected challenge distribution, allowed inputs, required
answer, exact solution predicate, scoring objective, success threshold,
normalization, source revision and file hashes. The implementation reads these
from the same source lock, profiles, verifier configurations and cost model used
by `autoresearch verify init-curvesmash`. It checks the protected source hashes
before discovery or scaffolding. Protected files are not edited or copied into
a competing problem definition.

`status: open` means available as a research objective. It does not report a
campaign's scientific state, current leaderboard, best known attack, submission
availability or an absence of prior results. Scores minimize total classical
computation within a track; reference units differ between tracks. Success must
be at least 0.39 under the selected distribution. Account for all preprocessing,
advice construction, failures, verification, amplification and processor work;
report memory separately. P-256's borrowed normalization is not a measured P-256
addition price. Both pairing tracks must retain the supplied per-instance
argument, and only the auxiliary-powers track has a scoring n.

## Use throughout the harness

1. **Discover and select** (`route`, `research-status`, `coordinate`). Read the
   catalog when selecting challenge work, preserve any named track, and inspect
   existing matching goals, questions, lead-atlas rows and prior evidence before
   opening new work. Rank a concrete next question under the existing portfolio
   and owner resource rules. The catalog itself creates no active goal or queue.
2. **Define and design** (`deep-research`, `propose-ideas`, `design-experiment`,
   `experiment-protocol`). Read the exact protected profile, rules and cost model.
   Attach the completed draft as `handoff.research`; its `extensions.challenge`
   carries the id, revision, source hashes and objective through task preparation,
   dispatch metadata and agent briefs. Bind those paths in task read scopes and
   frozen inputs. Supply the concrete mechanism, evidence plan, matched reference,
   test boundary and budgets through the ordinary lifecycle. A template or valid
   contract alone approves nothing.
3. **Implement and execute** (subject profiles and `run`). Use the selected track
   to define the actual input and output contract and accounting. Run existing
   prepared experiments through `run`; a challenge entry is not an executable.
   Discovery and catalog validation add no launch prerequisite. Preserve failures,
   tested scales, transfer assumptions and challenge identifiers in run records.
4. **Review and record** (`review-run`, `review-evidence`, `formal`, `sheriff`,
   `curate-knowledge`, `research-visuals`, `consolidate-lanes`). Keep observations,
   analytical bounds, exploratory verifier judgments and official scientific
   decisions distinct. Link the exact challenge contract in the relevant report
   or record. Small-instance success does not establish a production bound.
5. **Prepare challenge verification** when requested. Use the entry's
   `workspace_command` with a fresh output directory and follow
   [the verification guide](curvesmash-verification.md) for its separate trust
   domains. No skill treats exploratory acceptance as independent review or
   automatically submits to Yukon. Maintenance, messaging and infrastructure
   skills retain their normal scope and carry challenge pointers when relevant.

All canonical skills, Codex/OpenCode adapters and the plugin's generated `run`
adapters link this workflow. Existing role, spending, ownership, scientific
review and immutable-record contracts remain authoritative.

## Implementation source review

Sources checked for this software change (provenance: `internal`, read in the
implementation session): `orchestration/research_task.py`, `task_context.py`,
`verification.py`, `docs/general-research-tasks.md`, `docs/skill-routing.md`,
`docs/lab-contract.md` and the canonical lifecycle skills. These establish the
existing task extension point, adapter ownership and scientific authority.
The primary target definitions are the six protected profiles and configurations,
their rules, `classical-group-work-v2.json`, `docs/COST_MODEL.md` and
`source-lock.json` under `config/curvesmash/` (provenance: `retrieved` as recorded
by that import). Their pinned upstream source is
[Layr-Labs/curvesma.sh at 6423c27](https://github.com/Layr-Labs/curvesma.sh/tree/6423c2728dc03d5f2d647c7f22adf1dac0643a66).
The projection reuses those definitions rather than making a new cryptanalytic
claim. No live leaderboard or current upstream contract refresh was performed.
