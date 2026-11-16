#set document(title: "EXP-PEXT-212d5c run report 2026-11-15T04:26Z")
#set page(width: 21cm, height: 29.7cm, margin: 1.7cm, numbering: "1")
#set text(size: 10pt, font: "New Computer Modern")
#set par(justify: false, leading: 0.55em)
#show heading: set text(size: 13pt)
#set heading(numbering: none)

#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-PEXT-212d5c run report]
  #text(size: 11pt)[Session 2026-11-15T04:26Z (UTC)]
]

#v(0.4em)
#table(
  columns: (4.2cm, 1fr),
  stroke: none,
  inset: 2pt,
  [Experiment], [EXP-PEXT-212d5c (six-trial frozen plan)],
  [Hypothesis], [H-PEXT-d536a1],
  [Goal / question], [GOAL-PEXT-4a1d6b / RQ-PEXT-7c3e91],
  [Executor task / lane], [TASK-20261024-672126 / BATCH-21339c],
  [Approval], [DEC-20261024-992998],
  [Claim], [epoch 7, owner `opencode-run-20261114-a7c3`, released as `failed`],
  [Branch], [`run/harness-20261114`],
)

= What ran

The frozen plan `experiments/EXP-PEXT-212d5c/trial-plan.json`
(plan sha256 `5572ee66a37407147099b82542b6f1a2252969986665a8b21bf141c8df2759b0`)
was launched from commit `973caae767` with:

```sh
python3 tools/experiment_execution.py run \
  --plan experiments/EXP-PEXT-212d5c/trial-plan.json \
  --owner opencode-run-20261114-a7c3 --epoch 7
```

Host: macOS 27.2 arm64, Apple M4 Pro, 14 processors, 48 GiB RAM, CPython
3.12.8, rustc 1.93.1. Plan defaults: seed 20261012, 4 threads. The working
tree also carried one unrelated modified ledger checkpoint and an untracked
earlier run directory (`experiments/EXP-IC-b75e3a/runs/`) from another
session; neither is under this experiment's write scope and neither was
touched.

#table(
  columns: (3.0cm, 4.2cm, 2.8cm, 4.0cm, 2.0cm),
  stroke: 0.4pt,
  inset: 2pt,
  align: (left, left, left, left, right),
  table.header([Trial], [Run ID], [Status], [Recorded result], [Wall]),
  [regression], [`RUN-PEXT-63ca6a`], [`output_validated`], [`check.py`: 10 checks, none failed], [167 s],
  [construct], [`RUN-PEXT-056770`], [`output_validated`], [j-genus-7 counts, `configs other 0`], [13 s],
  [char2], [`RUN-PEXT-708f11`], [`output_validated`], [m-histograms, `prediction match True` (l = 1, 2, 3)], [25 s],
  [census], [`RUN-PEXT-3fd19f`], [`interrupted`], [214-model enumeration; 8 models recorded before stop], [1251 s],
  [lean], [`RUN-PEXT-2723eb`], [not launched], [dependency on nothing, reached after census], [—],
  [analyze], [`RUN-PEXT-422517`], [not launched], [waits on census], [—],
)

#figure(
  image("trials.svg", width: 100%),
  caption: [Wall time per run directory this session wrote, measured from each
    `execution-receipt.json`. The census bar is the interrupted segment only,
    not a completed measurement; `lean` and `analyze` produced no run directory.],
)

= Measured values (supervisor-validated)

These are the values the runner recorded and its `check.py` accepted. They are
observations at the tested toy parameters; they carry no verdict.

#table(
  columns: (2.6cm, 1fr),
  stroke: none,
  inset: 2pt,
  [construct], [q = 3: j_genus7 147 of 365; q = 5: 1253 of 13021; q = 7: 4782 of 137258; `configs other` 0 in all three],
  [char2], [l = 1: m-histogram {1: 1, 4: 28, 7: 98}; l = 2: {1: 3, 4: 504, 7: 15876}; l = 3: {1: 7, 4: 8176, 7: 2088968}; `prediction match True` in all three],
  [regression], [10 fixture/spectrum checks, `failed []`],
)

= The census interruption

The census trial (`RUN-PEXT-3fd19f`) enumerates 214 models of 435,847,959
structures each. Its own progress log records the first eight models at
392.4–535.2 s per batch of four, i.e. 8 models in about 16 minutes of the
session. The dispatch supervisor stops a trial when the claim expires
(`tools/experiment_execution.py`, `claim_expired`), and the claim taken for
this session was 240 minutes, while the handoff's advisory
`budget.wall_clock_seconds` is 192600 (53.5 h). A completion inside the claim
would have required roughly 7 h at the recorded rate (derived: 214 models ÷ 4
per batch × the slowest recorded batch, 535 s, ≈ 7.9 h; ≈ 7 h at the faster
recorded batch); the session therefore stopped the run at 20.8 min rather than
let it be killed at the claim boundary. The attempt directory is preserved
with status `interrupted`; it is not a measurement and not a refutation.

The plan assigns fixed run ids and the supervisor never reuses a run
directory, so this experiment cannot retry `census` by re-running the same
frozen plan: the attempt now requires Coordinator reconciliation and a new
dispatch (plan amendment with fresh run ids) sized to the plan's watchdog.

= Files

#table(
  columns: (1fr, 1fr),
  stroke: none,
  inset: 2pt,
  [`RUN-PEXT-63ca6a/`], [regression: launch, command, environment, logs, `regression.json`, four `R-*.jsonl`, manifest, receipt],
  [`RUN-PEXT-056770/`], [construct: same envelope plus `construct-q{3,5,7}.jsonl`],
  [`RUN-PEXT-708f11/`], [char2: same envelope plus its histogram file],
  [`RUN-PEXT-3fd19f/`], [census: launch, command, environment, logs, partial `census-n7-q3.jsonl`, `census-progress.log`, receipt `interrupted`],
)

The claim release record is
`coordination/goals/GOAL-PEXT-4a1d6b/batches/BATCH-21339c/claims/TASK-20261024-672126.7.release.json`.
Nothing here is evidence for or against H-PEXT-d536a1; no support, weaken or
reject decision is made or implied.
