# Measuring research capability

A research-task contract says what can be assigned. A capability result says
which independently checked tasks the configured model and harness actually
solved, under stated limits. These are separate properties.

`autoresearch eval capability` adds a bounded campaign evaluation to the existing
executor evaluation. It uses the canonical coordinator, executor and validator
role contracts with fresh native Codex sessions. It does **not** exercise the
production dispatch queue, external retrieval, tool execution, lab experiments,
or open-ended discovery. Those need separate suites and domain-specific graders.

## Run the complete pipeline

From a checkout installed with `pip install -e ".[agent,capability]" (Python 3.11+):

```sh
autoresearch eval capability validate --spec examples/capability-campaign/smoke.json
autoresearch eval capability control --spec examples/capability-campaign/smoke.json --out /tmp/capability-positive
autoresearch eval capability control --negative --spec examples/capability-campaign/smoke.json --out /tmp/capability-negative
autoresearch eval capability replay /tmp/capability-positive
autoresearch eval capability replay /tmp/capability-negative
```

The module entry point (with the same installed dependencies) is equivalent:
`python -m orchestration.eval.capability_campaign ...`.
Use a fresh output directory each time. Existing directories are never overwritten
or resumed automatically. Interrupted directories retain completed stage records;
no capability claim should use an unsealed partial bundle.

The live transport uses `codex login status` and the existing login; it does not
require an API-key environment variable. Never put credentials in a campaign.
Each actor uses a fresh private temporary Codex home, containing only a copy of
the existing file-backed login, deleted when the session ends. Desktop databases
and configuration are not shared. Keyring-only logins are not supported by this
transport. Native Codex must support `exec --ignore-user-config --ephemeral --output-schema`.
A live run additionally requires a prospectively frozen `experiment.protocol/v1`
whose links bind the campaign digest and evaluator source hashes. The shipped
qualification protocol is a specific development panel, not a reusable permission
for a different experiment. Make and freeze a new protocol when changing inputs,
code, model, sample counts or limits.

```sh
autoresearch eval capability run \
  --spec examples/capability-campaign/qualification-v3.json \
  --protocol examples/capability-campaign/protocol-v3.json \
  --model gpt-6-astra --effort xhigh --max-sessions 15 \
  --out /tmp/capability-live
```

## What X, Y and Z mean

Each task family has generated public inputs and a deterministic evaluator-held
reference. The initial families are grouped numerical analysis, synthetic source
synthesis with citations and conflicting/missing evidence, and exhaustive finite
modular equations. A domain label is descriptive; changing it does not create
an assessment of that domain's expertise.

The arms are `single` (execute), `planned` (plan and execute), and `reviewed`
(plan, execute, independent-session review, revise). Every actor receives only
public inputs and the preceding artifacts. Review approval cannot pass the
external grader. No tool use is permitted. This is an orchestration qualification
surface, not an execution sandbox for untrusted programs.

Every arm receives the same instance and per-trial wall deadline. The session
ceiling must accommodate the selected stages. Actual sessions and tokens can
differ: this does not establish a benefit at equal token spend. Interleaved order
is deterministically randomized; separate dev/held_out seed namespaces prevent
accidental identical instances but are **not** a secrecy or contamination defense.
Freeze a fresh held-out panel before tuning and preserve its custody separately.

Software controls use an independent solver and fabricated answers through the
same pipeline. Their reports always say `software_control_only`. Live dev passes
can say `demonstrated_on_cases`; only a held-out panel with enough independent
instances and the configured success/false-success bounds can say
`meets_reliability_threshold`. That label is a statistical screen, not scientific
approval. Review provenance and held-out custody before using it externally.

Reports include all attempts, exact verified outcomes, false success claims,
interventions, elapsed time, usage when reported, and cost when known. A false
success is an actor's success claim for an incorrect answer; infrastructure failure
after a correct candidate is an incomplete trial, not a fabricated answer.
Repeated attempts on one instance form one cluster: every scheduled repeat must
pass for that instance to pass. The displayed 95% Wilson intervals are marginal
per matrix cell. Paired arm comparisons report exact discordance tests and
Bonferroni-adjusted p-values but never declare superiority automatically.

The native driver bounds local actor address space, CPU affinity, per-file storage
bytes, prompt bytes and trial wall time; it launches serial sessions without
campaign retries. The separate output-byte limit rejects oversized returned logs or answers; it
does not cap Codex internal database size. A byte cap is not a remote token cap. Subscription dollar
billing and remote inference resource usage are unavailable and remain null.
No dollar ceiling or equal compute budget is implied. EKS/cloud execution needs
the separate owner budget and publication checks.

## Durable evidence and extension

Each bundle contains the frozen spec, source hashes, exact public inputs, stage
inputs/results, CLI traces, per-trial outcomes, report JSON/Markdown, SVG graph
and SHA256 inventory. Live bundles also contain the protocol and shared
`experiment.export/v1`. Replay verifies the file inventory, regenerates inputs,
reconciles stage outputs and usage with trial records, reruns the exact grader,
and recomputes the report. A hash inventory detects changes against its recorded
values; publish the bundle hash externally for tamper-evident custody.

To add a new family, implement a public-input/reference generator and a grader
that recognizes valid alternative answers. Add an independently implemented
positive solver and adversarial negative controls. For qualitative or novel
research, use blinded independent expert assessment or exact downstream tests;
do not replace ground truth with producer self-assessment. Add representative
held-out tasks, failures and difficulty levels before asserting the new capability.

Source review: the existing `docs/measuring-the-harness.md` defines the narrower
executor evaluator. [Anthropic's agent-evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
supports scoring outcomes separately from transcripts.
[Codex non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode)
and host CLI help were checked for the structured-output transport. Neither source
supplies evidence that this implementation solves arbitrary research tasks.
