# CLAUDE.md

Read [AGENTS.md](AGENTS.md), the only normative contract for every runtime,
Claude Code included; its rules "ECC comes first", "Goals are never paused",
"Resume checkpoints in S3 before every run" and the
[persistent scientific research loop](AGENTS.md#persistent-scientific-research-loop)
bind here. Long form, loop and the previous text of this file:
[docs/claude-code-runtime.md](docs/claude-code-runtime.md).

## Claude Code specifics

- `.claude/agents/` wraps `agents/*.md`; roles, model pins and effort live in
  `orchestration/roles.yaml` and `orchestration/model-policies.yaml`, checked
  by `tools/check_runtime_bindings.py`. Keep `model: inherit` except declared
  `runtime_model_pins` roles; never hand-edit model or effort. The session
  defaults to `claude-opus-5-5`.
- Research enters through `.claude/skills/autoresearch/`; only `run` executes
  trials. Each skill writes a session receipt.
- `.mcp.json` starts the read-only, derived `kb/` server; query the shared
  layer per AGENTS.md "Knowledge retrieval" (skill `research-kb`).
