# Held-out trap tasks

Suites in this directory are held out from tuning (proposal I5 of
`docs/autoresearcher-harness-review-20261110.md`).

Convention:

- Every task here sets `held_out: true` (the loader treats it as
  `split: held_out`; `run` and `compare` already skip that split by default).
- `tune-skill`, `coordination/skill-tuning/**` rounds and any agent producing a
  tuning proposal must not read, list, quote or run anything under this
  directory. Fixtures and graders here are not shown to producers.
- A held-out suite is run only to test whether a change generalised, and the
  run is reported next to the dev result, never folded into it.
- A task whose result informed a tuning decision is spent: move it to
  `evals/suites/` as `dev` and add a fresh replacement here.

No tasks are checked in yet. The harness-change gate
(`tools/check_harness_change_gate.py`) wants a committed baseline on the dev
suite first; a held-out suite is added once that baseline shows the dev suite
discriminates.
