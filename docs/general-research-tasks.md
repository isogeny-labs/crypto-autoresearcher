# Research tasks across domains

The harness can describe research in any domain without requiring a curve, attack,
benchmark, or empirical hypothesis. It carries method-specific requirements through
existing task preparation, dispatch validation, workspace metadata and agent briefs.
It does not supply every domain's instruments, datasets or expertise: those remain
explicit dependencies, and a contract's structural validity is not scientific approval.

## Create and inspect a contract

```sh
autoresearch research methods
autoresearch research template --domain ecology --method literature \
  --question 'Which observations support this ecological mechanism?' > research.json
# Fill every empty procedure, evidence-plan and acceptance-criteria entry.
autoresearch research validate research.json
autoresearch research brief research.json
```

The template is intentionally invalid until filled. Commands print to stdout and
never launch a model, run a study, approve work or modify the ledger. JSON and YAML
inputs are accepted. `python3 -m orchestration research ...` works without installing
the console entry point.

Place the completed object under `handoff.research` in an existing task card. The
usual role, objective, inputs, constraints, deliverables, artifact paths, completion
gate, inference policy, budget, and scopes still apply. `research` is not allowed
at the outer queue-task level. Existing handoffs without it remain unchanged.
`autoresearch agent plan --task <handoff>` uses the existing planning path; execution
still follows the existing authorized workflow and runtime capability checks.

## Contract

`schema` is `autoresearch.research-task/v1`. Required fields are:

- `domains`: non-empty list of arbitrary domain names; multidisciplinary tasks can
  name several. Domain names do not select code, grant permissions or impose ECC priority.
- `question`: the scoped question being addressed.
- `method`: one of the families below.
- `procedure`: non-empty list of steps appropriate to this method.
- `evidence_plan`: named requirements with non-empty descriptions. Additional keys
  are allowed for domain-specific evidence.
- `acceptance_criteria`: non-empty list of checkable deliverable criteria. These
  supplement the handoff's completion gate; neither silently overrides the other.
- `limitations`: list of scope limits, assumptions, and unresolved dependencies
  (may be empty when none is known).
- `required_capabilities`: list of capability names from `orchestration/roles.yaml`
  (may be empty). Preparation rejects capabilities outside the role's guaranteed
  capabilities. The existing resolver also checks runtime support. Optional tools
  are not guaranteed; select an appropriate role/runtime or record the dependency.

`extensions` is an optional JSON object for domain-specific metadata. Unknown
core fields are rejected to catch misspellings. Non-finite and non-JSON values are
rejected. A custom method requires both its justification and verification plan;
additional keys can describe archival analysis, interviews, fieldwork, mixed
methods or a new method without modifying the runtime. Split mixed workflows
into separate handoffs when they need different roles, controls or approvals.

| Method | Required evidence-plan keys |
| --- | --- |
| literature | search_strategy, source_selection, source_provenance, synthesis |
| theoretical | assumptions, derivation, verification |
| computational | inputs, reference, verification, reproducibility |
| empirical | sampling, controls, analysis, reproducibility |
| engineering | requirements, baseline, verification |
| replication | original_claim, original_artifacts, comparison, deviations |
| synthesis | source_provenance, conflicting_evidence, inference_rules |
| custom | method_justification, verification |

Evidence-plan entries describe what will be checked, not a claim that it has passed.
Where a control or reference is inapplicable, explain why and how the conclusion
will be checked. Experimental work still needs the existing frozen protocol; a
non-empty string does not establish adequate controls. Research contracts cannot
relax approval, evidence, immutability, spending, role or file-scope rules.
Explicitly assigned non-ECC work is not redirected to the default ECC portfolio.

## Compatibility and validation

The opt-in contract leaves historical handoffs and immutable records untouched.
It is included in context manifests and the api_direct brief (also emitted by
`agent plan` for native runtimes). Dispatch validates its shape before readiness;
task preparation checks declared capabilities before workspace/runtime work.
No domain strings are interpreted as executable commands or import names.

The fixtures in `examples/research-tasks/` illustrate contracts only, not approved
studies or results. `tests/test_research_task.py` covers every method, unfamiliar
domains, invalid contracts, legacy compatibility, capability refusal, CLI errors
and manifest preservation; agent and dispatcher tests cover their integration.

Implementation source review: `orchestration/task_context.py`,
`orchestration/agent/runner.py`, `orchestration/roles.yaml`,
`tools/research_dispatch.py`, and `docs/agent-runtime-core.md` establish the existing
scope and authority boundaries. Python's official
[argparse documentation](https://docs.python.org/3/library/argparse.html) and
[JSON documentation](https://docs.python.org/3/library/json.html) inform CLI
subcommands and strict JSON serialization. This is a software extension, with no
claim to introduce a new scientific method or to validate the fixture research.
