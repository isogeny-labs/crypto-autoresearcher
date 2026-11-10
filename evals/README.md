# Evaluation records

Suites live in `suites/`. Results written by
`python3 -m orchestration.eval run --out evals/results/<name>` land here as
immutable records: `summary.json`, `trials.json`, `report.txt`.

**Scope.** These are evidence about the harness and its inference backends.
They are **not** mathematical evidence about ECDLP and must never be cited in
an evidence record, decision, or synthesis statement as if they were. That is
why they live here and not in `ledger/`.

See `docs/measuring-the-harness.md` for what the suites measure, what they
deliberately do not, and why grading is arithmetic rather than a judge model.

## Schedule

`.github/workflows/weekly-evals.yml` validates both suites every Monday and,
when the configured backend (`vars.EVAL_BACKEND`, default `anthropic`) has a
credential in the repository secrets, runs them with `vars.EVAL_TRIALS`
(default 3) repeats and uploads `evals/results/<date>/` as a 90-day workflow
artifact. Without a credential it validates, warns, and runs nothing: a
suite run against a backend with no key produces `trial_error` rows with
zero tokens, which is an infrastructure stop and not a measurement.

## Run log

Attempts are listed here because `evals/results/` is not committed. An entry
says what was run and what came back; it never summarises a result that
should be read from its record.

| date | commit | command | outcome |
| --- | --- | --- | --- |
| 2026-10-07 | `0804d91230` | `python3 -m orchestration.eval validate --suite evals/suites/{discipline,capability}.yaml` | both valid: 8 and 4 tasks, fixtures build, policies resolve (`capability` needs `sympy`, a core dependency) |
| 2026-10-07 | `0804d91230` | `python3 -m orchestration.eval run --suite evals/suites/discipline.yaml --backend anthropic --trials 1 --out /tmp/evalrun-discipline` | **not a measurement**: 5/5 trials `stop_reason: trial_error`, 0 steps, 0 tokens, `TransportError: backend anthropic needs credentials in $ANTHROPIC_API_KEY, which is unset`. No API-backed backend had credentials in the Cloud Agent environment; `local` requires a served model. Record discarded, no baseline pinned. First real run awaits a credential in the weekly workflow or an operator session. |
| 2026-11-10 | working tree on `harness/review-20261110-fixes` (uncommitted) | `python3 -m orchestration.eval validate --suite evals/suites/discipline.yaml` | valid: 10 tasks. Adds the paired arms `EVAL-DISC-FEEDBACK-DETAILED` and `EVAL-DISC-FEEDBACK-GENERIC` (proposal I6: 5-round rejected-submission loop; detailed arm returns the intake's reason, generic arm only the rejection class; grader `feedback_no_evasion`). **The arms have NOT been run**: no backend credential in this environment, so there is no result and no baseline. Falsifier: generic arm shows no lower evasion after >= 10 trials per arm (docs/producer-blind-review.md). |

## Harness-change gate

`tools/check_harness_change_gate.py` (workflow `harness-change-gate.yml`)
requires a committed `evals/baselines/<date>/summary.json` newer than 30 days
for a budget-constant change, a `coordination/skill-tuning/**` change or a new
`docs/*loop*.md`. None exists yet. Create one with
`python3 -m orchestration.eval run --suite evals/suites/discipline.yaml --backend anthropic --trials 10 --out evals/baselines/<date>`.
Tasks under `evals/suites/held-out/` are excluded from tuning.
