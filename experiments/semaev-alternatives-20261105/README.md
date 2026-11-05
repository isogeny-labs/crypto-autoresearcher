# Campaign: alternatives to Semaev summation polynomials (prime-field ECDLP)

Opened 2026-11-05. Owner request: pursue all 18 directions of the campaign report in parallel, with one Sonnet subagent per direction, after registering the experiments in git.

## Contents

- `report/semaev_alternatives_report.md`: the campaign report. It holds the closure map, the structural diagnosis, the 18 directions and the bibliography. The rendered PDF and the Section 6 figure are binaries, so they are not in git (the `artifacts` policy keeps data files in the S3 store, and this session had no store credentials). Regenerate the figure with `report/calibration/fig.py`; the PDF was delivered to the owner directly.
- `report/calibration/`: the scripts and data behind the report's Section 6.
- `prereg/SA-01.md` … `prereg/SA-18.md`: one frozen pre-registration per direction. Each holds the mechanism, prediction, protocol, success and kill criteria, and the lead-atlas row it advances or proposes.
- `registry.tsv`: id, kind, lead and the SHA-256 of each pre-registration as committed. A later edit to a pre-registration is detectable against this file.
- `results/SA-NN/`: written by the executors, landed in a follow-up PR.

## What this registration is and is not

This registers predictions and kill criteria before any run, so the results cannot move the goalposts. It does **not** mint ledger hypotheses, `EXP-*` contracts, `protocol.json` files or pre-approval packets under `.claude/skills/design-experiment` (that path designs one ECC experiment per session and needs Coordinator approval). The owner asked for all 18 at once. Results from this campaign are therefore exploratory evidence. Any direction that reports SUCCESS must be redesigned as a full contract and replicated before it changes a lead's disposition or reaches a leaderboard.

## Execution limits

The executor host has 4 CPU cores and 15 GB RAM shared by 18 executors. Each executor is capped at about 3 wall-clock hours and one core's worth of sustained load, so every run is toy scale (primes up to roughly 2^64 unless the pre-registration says otherwise). A criterion that cannot be decided at that scale is reported as INCONCLUSIVE with the scale reached, never as a kill.

## Lead-atlas mapping

Eight directions advance existing leads; ten propose new leads (named in each pre-registration as `NEW (proposed …)`). Lead files are filed with the results, not before, so that a direction killed at first contact does not leave an empty lead.
