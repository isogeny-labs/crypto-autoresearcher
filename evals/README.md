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

## Pairwise ratings (`rate`)

`python3 -m orchestration.eval rate evals/results/<a> evals/results/<b> ... --out ratings.json`
turns existing run records into a Bradley-Terry leaderboard, after
<https://agentduel.com/leaderboard/methodology>. It is offline and spends nothing.
Implementation and the full mapping: `orchestration/eval/duel.py`.

- **Battle**: two records with the same suite, task, trial index and
  `seed_offset` (so the same generated fixture and graders). Higher grader
  score wins; equal scores tie at ½. `run`/`compare` now write `seed_offset`
  to `summary.json`; older records need `--assume-seed`.
- **Fit**: MAP on the Elo scale, P(A beats B) = 1/(1+10^((B-A)/400)),
  N(1000, 400²) prior.
- **Excluded** (counted, never awarded): either side `trial_error`, zero
  recorded tokens, incomplete row, duplicate key, unrecorded seed.
- **Uncertainty**: task-cluster bootstrap (B=1000) → percentile intervals,
  rank likelihoods (tied ranks split), KDE ridgelines with
  h = max(2, 1.06·s·B^-1/5); centred Laplace credible intervals; pairwise
  contrasts; `design_effect` = (bootstrap SD / Laplace SD)².
- **Pareto** frontier over Elo vs median/mean tokens or wall seconds.

Two deliberate departures from the source:

1. Per-contestant "95% posterior credible intervals" are reported for the
   **centred** ratings. The likelihood identifies only differences; the common
   shift is pinned by the prior alone, so the uncentred interval is mostly
   prior. Measured: with it, design effects came out ≈0.01 and coverage was
   trivially 100%.
2. The cluster is the **task**, the analogue of the leaderboard's developer.

Calibration (synthetic, 4 backends, 3 trials/task, task×backend random effect
τ Elo, 300 replicates per cell, B=200; coverage of the large-sample BT value,
nominal 0.95):

| τ | tasks | Laplace (centred) | cluster bootstrap | median design effect |
|---|---|---|---|---|
| 0 | 12 | 0.963 | 0.898 | 0.83 |
| 0 | 40 | 0.951 | 0.929 | 0.90 |
| 200 | 12 | 0.896 | 0.895 | 1.26 |
| 200 | 40 | 0.911 | 0.938 | 1.33 |
| 500 | 12 | 0.835 | 0.917 | 1.93 |
| 500 | 40 | 0.833 | 0.932 | 1.98 |

Read: when trials within a task are correlated the posterior interval
under-covers and does not improve with more tasks; the cluster bootstrap holds.
At the current suite sizes (8 and 4 tasks) neither reaches nominal, which is
why `rate` warns below 20 clusters. A design effect well above 1 on real
records is the signal to trust the bootstrap column.

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
