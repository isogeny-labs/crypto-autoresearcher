# Checkpoint waiver for run-001

AGENTS.md ("Resume checkpoints in S3 before every run") requires a pushed S3
resume checkpoint before an experiment launches. This session had no upload
token (no AWS profile, no `CHECKPOINT_UPLOAD_TOKEN`, no token file), so
`scripts/checkpoint.sh gate` failed (`runs/run-001/checkpoint_gate.txt`,
`gate_rc=1`).

Before launch, the session asked the owner (Claude Code session
`session_01AXUKfV7Mndc73sHXKwAJNs`, 2026-11-01 UTC), quoting the frozen
protocol hash, that the run takes 1–2 minutes, and that everything needed to
resume is on the pushed branch. It offered three choices: waive for this run,
provide a token, or do not run. The owner chose **"Waive it for this run"**.

Scope of the waiver: run-001 of this study only. What it relaxes: the S3
checkpoint precondition. What it does not relax: the frozen protocol
(committed and pushed at `bfccbce57c` before the run), the run records, the
export check or the independent review. A later run of this study goes
through the gate again.

The prompt and answer live in that session's transcript. This record restates
them; it is not a copy of the transcript.
