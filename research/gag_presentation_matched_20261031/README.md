# GAG presentation matched study (2026-10-31)

This study asks whether msolve's F4 does a different amount of counted work on
the Weil-descended Gaudry/Diem decomposition system at n = m = 3 over F_{p^3}.
It compares three presentations of the same Semaev network: `chain` (the
default), `tree` and `monolithic` (S_4). The A/A arm is `chain` with another
separating form. The study is the next step of
`knowledge/leads/ecdlp/ic-engine/LEAD-ICE-gag-contraction-planner.yaml`.

| file | what |
|---|---|
| `protocol.json` | `experiment.protocol/v1`, frozen sha256 `609c701c…`, committed and pushed in `bfccbce57c` before any study data |
| `design.json` | primes, instance, form and order rules; its hash is bound in the protocol |
| `driver.py`, `analyze.py` | runner, and analysis frozen by hash |
| `runs/run-001/` | rows (gz), raw msolve output (gz per file, `raw.sha256`), `analysis.json`, `export.json` (check-export clean), environment and logs |
| `reports/run-20261101T1755Z/` | run report (Typst source, PDF, SVG and its script) |
| `reports/run-20261101T1755Z.correction-1.md` | corrects two statements of the report |
| `reviews/REV-20261101T180217Z-c184b3.json` | independent `review-run` (validator), recommendation `replicate` |
| `checkpoint-waiver-run-001.md` | owner's waiver of the S3 checkpoint for run-001 |

**Run-001 outcome.** These are protocol verdicts, descriptive, and decide no
hypothesis.

- **C1 holds.** All 30 instances give identical verified relations on every
  arm, and the planted relation is always found.
- **C-mono: `supported_within_scope`.** The monolithic presentation used 0.110
  times chain's F4 matrix cells at every prime.
- **C-tree: `inconclusive`.** Tree used 1.095 times chain's cells. The p = 1009
  A/A floor was set by one charged retry.

Wall time was not isolated and decides nothing.

Reproduce:

```sh
PYTHONPATH=src python3 research/gag_presentation_matched_20261031/driver.py --protocol research/gag_presentation_matched_20261031/protocol.json --out research/gag_presentation_matched_20261031/runs/run-NNN
```
