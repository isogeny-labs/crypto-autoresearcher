#set document(title: "EXP-PEXT-0b2c75 run report 2026-11-15T19:02Z")
#set page(width: 21cm, height: 29.7cm, margin: 1.7cm, numbering: "1")
#set text(size: 10pt, font: "New Computer Modern")
#set par(justify: false, leading: 0.55em)
#show heading: set text(size: 13pt)
#set heading(numbering: none)

#align(center)[
  #text(size: 17pt, weight: "bold")[EXP-PEXT-0b2c75 run report]
  #text(size: 11pt)[Session 2026-11-15T19:02Z (UTC)]
]

#v(0.4em)
#table(
  columns: (4.2cm, 1fr),
  stroke: none,
  inset: 2pt,
  [Experiment], [EXP-PEXT-0b2c75 (six-trial frozen plan)],
  [Hypothesis], [H-PEXT-ad0073],
  [Goal / question], [GOAL-PEXT-4a1d6b / RQ-PEXT-7c3e91],
  [Executor task / lane], [TASK-20261031-73799d / BATCH-a4886a],
  [Approval], [DEC-20261031-dcfdee],
  [Claim], [epoch 1, owner `opencode-run-20261115-9f2c`],
  [Branch], [`run/harness-20261114`],
)

= What ran

The frozen plan `experiments/EXP-PEXT-0b2c75/trial-plan.json`
(plan sha256 `085bf4f3d98cecd5484e0318f64dc22675b846d4ab0b7c8f0fa0ca8b1441b37c`)
was launched from commit `8a8a8680c6` (`code.dirty: false` in every manifest)
with:

```sh
python3 tools/experiment_execution.py run \
  --plan experiments/EXP-PEXT-0b2c75/trial-plan.json \
  --owner opencode-run-20261115-9f2c --epoch 1
```

Host: macOS 27.2 arm64, Apple M4 Pro, 14 processors, 48 GiB RAM, CPython
3.12.8, rustc 1.93.1. Plan defaults: seed 20261101, 4 threads, 1000 negative
configs. The working tree also carried one unrelated modified ledger checkpoint
and an untracked earlier run directory (`experiments/EXP-IC-b75e3a/runs/`) from
another session; neither is under this experiment's write scope and neither was
touched.

All six trials were launched in dependency order and every one finished with
`check.py` exit 0 and status `output_validated`. No trial timed out, crashed or
was interrupted; the plan's per-trial watchdogs (3600–28800 s) were not
approached by any trial except `n5ext`, which used 6156 s of its 28800 s.

#table(
  columns: (2.2cm, 3.2cm, 3.1cm, 4.7cm, 1.9cm, 1.9cm),
  stroke: 0.4pt,
  inset: 2pt,
  align: (left, left, left, left, right, right),
  table.header([Trial], [Run ID], [Status], [Recorded result], [Wall], [CPU]),
  [regression], [`RUN-PEXT-8c15bf`], [`output_validated`], [9 fixture/spectrum/AA checks, `failures []`], [5.2 s], [4.6 s],
  [n5core], [`RUN-PEXT-ff55f2`], [`output_validated`], [7 arms q = 5…19, 2,204 units, 0/0 mismatch], [66.2 s], [180.8 s],
  [n7], [`RUN-PEXT-e4ce49`], [`output_validated`], [19 arms, 51,602 units, 0/0 mismatch], [2,498.9 s], [7,440.7 s],
  [negative], [`RUN-PEXT-a19d45`], [`output_validated`], [5 off-family arms × 1,000 pairs, discriminates], [13.6 s], [44.1 s],
  [n5ext], [`RUN-PEXT-c0fbcd`], [`output_validated`], [5 arms q = 23…31, 7,380 units, 0/0 mismatch], [6,155.7 s], [22,327.8 s],
  [analyze], [`RUN-PEXT-87ac49`], [`output_validated`], [`headline SUPPORT_SCOPED`, `valid true`], [0.5 s], [0.6 s],
)

Session wall from first trial launch to `analyze` receipt: 2 h 26 m 46 s
(19:02:01Z → 21:28:47Z). Sum of the six run walls: 8,740.2 s. Sum of recorded
CPU seconds: 29,998.5 s (8.3 CPU-hours), consistent with 4-thread arms.

#figure(
  image("trials.svg", width: 100%),
  caption: [Wall time per run directory, measured from each
    `execution-receipt.json`. Axis is logarithmic; all six receipts record
    `output_validated`.],
)

= Measured values (supervisor-validated)

These are the values the runner recorded and its `check.py` re-derived from
`instances[]`; they are observations at the tested toy parameters and carry no
verdict.

#table(
  columns: (2.4cm, 1fr),
  stroke: none,
  inset: 2pt,
  [P1], [n = 5, q = 7, 11, 19, 23, 27, 31: 5,512 units, `units_E4_ne_8` = 0 (CONFIRMED)],
  [P2], [n = 5, q = 5, 9, 13, 17, 25, 29: 4,072 units, 2,036 pairs, `mismatch` = 0; each pair has exactly one E4 = 4 member (CONFIRMED)],
  [P3], [n = 7, S = (0,2,3,4), q = 3, 5, 7, 9: 19,672 units, `mismatch` = 0 (CONFIRMED)],
  [P4], [n = 7, five other words × q = 3, 5, 7: 15 arms, 31,930 units, per-arm mismatch 0 (CONFIRMED)],
  [P5], [sign formula (4.2): 0 observed signs differ from the bit expression, all decisive arms (CONFIRMED)],
  [P6], [(m, r, genus): (4,5,5) at n = 5; (3,7,7) for S = (0,2,3,4); (6,7,49) for the genus-49 words; `mismatch_arms` = [] (CONFIRMED)],
  [N2], [off-family random quartics: q = 5/9/13 `eps = +1` share 0.499/0.492/0.518 of pairs with a c = 1 member at E4 = 4; q = 7/11 `eps = -1` share E4 ≠ 8 = 0.240/0.245; E4 = 16 seen (265, 239, 259 of 1,000 pairs) — DISCRIMINATES],
  [H1], [12 n5 arms, chi-square df = 3: min 0.1436 (q = 19), max 6.4414 (q = 17), p = 0.092–0.986; non-gating],
  [Coverage], [each (t, b1 b2) cell of each eps class has ≥ 20 units over the decisive arms (MET)],
)

The analysis headline recorded in `RUN-PEXT-87ac49/analysis.json` is
`SUPPORT_SCOPED: zero decisive-cell contradictions of the candidate law on the
tested cells; a pass does not establish the theorem, novelty, or anything
beyond the tested cells`, with `valid: true` and no invalid reasons.

#figure(
  image("law.svg", width: 100%),
  caption: [Recorded `e4_hist` composition of every n = 5 arm (q = 5…31) and the
    n = 7 primary word (q = 3…9); bar height is the share of that arm's units,
    `u` is the recorded unit count. Zero E4 and zero sign mismatches in every
    arm. The 15 other n = 7 arms are tabulated in `law-table.md`.],
)

= Recorded structure

The 31 arms total 61,186 units. At n = 5 the `eps = -1` arms (q = 7, 11, 19, 23,
27, 31) are a single histogram bucket, |E(K)[4]| = 8 on 5,512 units, while the
`eps = +1` arms split between 4, 8 and 16 exactly per pair as P2 states. At
n = 7 the primary word reproduces the (7.2) count on 19,672 units and the other
five words reproduce the generic (3.1)+(4.2) predictor on 15 arms. `negative`
shows the instrument can see off-family violations: random quartics produce
E4 = 16 and E4 = 4 in the `eps = +1` class and E4 ≠ 8 in the `eps = -1` class at
rates far above the family arms' zero mismatches.

The `regression` trial re-derived the published q = 3 genus-5 records, the
sibling family counts, the negative fixtures, the (m, r, genus) of every S word,
the bitalgebra self-check and an A/A rebuild (byte-identical), all 9 checks
`identical: true`.

#table(
  columns: (3.4cm, 1fr),
  stroke: none,
  inset: 2pt,
  [n = 5, eps = -1], [q = 7, 11, 19, 23, 27, 31: 100/244/724/1060/1460/1924 units, all E4 = 8],
  [n = 5, eps = +1], [q = 5, 9, 13, 17, 25, 29: histograms 4/8/16 = 26/16/10, 82/32/50, 170/80/90, 290/160/130, 626/320/306, 842/400/442],
  [n = 7, primary], [q = 3: 56/126, q = 5: 651/504/147, q = 7: 1248/3654, q = 9: 6643/5040/1603 (buckets 4/8/16)],
)

= Anomaly in the recorded resource block

Each manifest's `resources.peak_rss_bytes` reads 1.67×10^11 to 1.67×10^12 bytes
(157–1,557 GiB) on a 48 GiB host, which is not a possible resident set; the
runner's RSS unit is therefore not usable in this environment. Wall seconds and
CPU seconds are used above; no memory claim is made. This is noted for whoever
owns the resource recorder; it did not affect admission, validity or the
recorded counts.

= Files

#table(
  columns: (4.4cm, 1fr),
  stroke: none,
  inset: 2pt,
  [`RUN-PEXT-8c15bf/`], [regression: launch, command, environment, logs, `regression.json`, two `R-*.jsonl`, manifest, receipt],
  [`RUN-PEXT-ff55f2/`], [n5core: same envelope plus `n5-core.jsonl.gz`],
  [`RUN-PEXT-e4ce49/`], [n7: same envelope plus `n7.jsonl.gz`],
  [`RUN-PEXT-a19d45/`], [negative: same envelope plus `negative.jsonl.gz`],
  [`RUN-PEXT-c0fbcd/`], [n5ext: same envelope plus `n5-ext.jsonl.gz`],
  [`RUN-PEXT-87ac49/`], [analyze: same envelope plus `analysis.json`, `law-table.md`],
)

The claim release record is
`coordination/goals/GOAL-PEXT-4a1d6b/batches/BATCH-a4886a/claims/TASK-20261031-73799d.1.release.json`.

= Scope

The derivation under test is an unreviewed candidate (hypothesis-record
obligations 1–7 are "not discharged"). This run reports exact group counts on
the tested cells only. It claims no theorem, no novelty, no class-level share,
no cost against rho and no statement at cryptographic parameters, and it does
not by itself support, weaken or reject H-PEXT-ad0073; that decision belongs to
independent review after the ledger archive.
