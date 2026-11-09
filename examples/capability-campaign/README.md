# Cross-domain capability qualification, 2026-11-07

The final native qualification verified all six submitted answers: one generated
instance each of grouped numerical analysis, synthetic source synthesis and
finite modular mathematics, evaluated with both a single executor and a
plan/execute/review/revise sequence. All 15 native sessions completed; no tool
violations or false success claims were recorded. The exact grader and bundle
replay passed. This is a development qualification of the bounded supplied-input
campaign, not an estimate of arbitrary research capability.

| Record | Trials | Verified | False success claims detected | Native sessions |
| --- | ---: | ---: | ---: | ---: |
| [Positive software control](records/positive/report.md) | 18 | 18 | 0 | 0 |
| [Negative software control](records/negative/report.md) | 18 | 0 | 18 | 0 |
| [First native attempt](records/native-qualification/report.md) | 6 | 0 | 0 | 6 |
| [Isolated-home attempt](records/native-qualification-v2/report.md) | 6 | 0 | 0 | 6 |
| [Final native qualification](records/native-qualification-v3/report.md) | 6 | 6 | 0 | 15 |

The software controls contain scripted answers and are never counted as model
capability. The first two live attempts each ended with `SIGXFSZ` (return code
`-25`) under a process-wide 1 MiB file-size ceiling before producing answers.
The first shared the desktop's native state; the second isolated that state but
still failed during native startup. The final transport uses a private temporary
Codex home and separates a 64 MiB per-file internal storage ceiling from the
1 MiB returned-output acceptance limit. These are implementation corrections;
all earlier failures and their frozen protocols remain published.

The final panel recorded 120.81065196298005 summed trial wall seconds and 200,784
input-plus-output tokens. Wall time is descriptive on this shared host, not a
performance comparison. Earlier failed attempts have missing token usage;
whole-development token usage and subscription dollar cost are unknown. Across
all three panels, 27 sessions were attempted within the combined 30-session
ceiling. No EKS jobs or new cloud compute were submitted. An earlier Python
launch failed to import PyYAML before any trial directory or model session;
the launch environment was corrected without changing the first protocol.

There is one independent instance per task family and arm in the final panel.
The marginal 95% Wilson success interval is [0.2065, 1.0] in each cell. Its status
is `demonstrated_on_cases`, not `meets_reliability_threshold`. No advantage of
reviewed over single execution is inferred. The sample and returned artifacts
are supplied-input fixtures; they do not test retrieval, novel discovery, physical
experiments or the production dispatch queue.

## Reproduce the checks

Install the repository with Python 3.11+ and `pip install -e ".[agent,capability]"`.
From its root:

```sh
autoresearch eval capability replay examples/capability-campaign/records/positive
autoresearch eval capability replay examples/capability-campaign/records/negative
autoresearch eval capability replay examples/capability-campaign/records/native-qualification
autoresearch eval capability replay examples/capability-campaign/records/native-qualification-v2
autoresearch eval capability replay examples/capability-campaign/records/native-qualification-v3
python tools/experiment_protocol.py check-export \
  examples/capability-campaign/records/native-qualification-v3/export.json \
  --protocol examples/capability-campaign/protocol-v3.json --verify-files
```

Each live bundle has its protocol, stage transcripts, exact input/answer records,
standard `experiment.export/v1`, source hashes, report, SVG and SHA256 inventory.
The [machine summary](qualification-summary.json) aggregates the saved rows.
Publication receipts bind the implementation before each live attempt:
[original](publication-receipt.json), [v2](publication-receipt-v2.json),
[v3](publication-receipt-v3.json). Original source is recoverable at those Git
revisions. Do not rerun historical panels into their existing directories.

PDFs are separate from sealed run bundles:
[positive control](reports/positive.pdf), [negative control](reports/negative.pdf),
[first attempt](reports/native-qualification.pdf),
[isolated-home attempt](reports/native-qualification-v2.pdf), and
[final qualification](reports/native-qualification-v3.pdf).
`render_report.py` is the rendering source; it uses the saved report values and
requires ReportLab. PDFs were rendered and checked for readable content/layout.

Software verification: 298 focused tests and 64 subtests passed, including 21
campaign tests for exact grading, false-success detection, failure accounting,
matched scheduling, dev/held-out separation, clustered repeats, native transport,
output limits, immutable directories, protocol/export binding and replay/tamper
checks. Runtime bindings and instruction budgets passed. See
[capability-campaign documentation](../../docs/capability-campaigns.md) for limits,
reliability gates and extension to new task families.
