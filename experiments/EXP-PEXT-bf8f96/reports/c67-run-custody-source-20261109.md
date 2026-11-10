# Prospective C6/C7 run custody source stage

Implemented a run custody component for the published prospective schedule at
`inputs/c67-control-schedule-prospective.json`. It binds the schedule to the
existing `n3core`, `n3ext`, and `n5` supervisor trials, their exact run IDs, the
approved trial-plan bytes, current live supervisor authority, and declared
artifact coverage. It adds no trial. The source component creates no C6
transport, C7 draw, scientific cohort row, benchmark, or cloud job.

The published schedule requests 20 C6 selected units with 320 coordinate slots
and 40 C7 strata with 640 forms. These are prospective design counts. The
component enumerates 30 batch result files in `n3core`, 15 in `n3ext`, and 15
in `n5`, together with a custody admission and readback in each existing run.

`c67_run_custody.prepare` exclusively creates `c67-custody.json` before creating
`c67-results`. Existing result data prevents prospective preparation. A partial
admission survives an interrupted attempt and cannot be overwritten.
`write_result` rechecks the approved supervisor binding, permits only the exact
schedule-declared path, checks batch identity and retained-count structure,
wraps the supplied payload with run/plan/schedule/admission identity, and creates
it exclusively. It rejects duplicate writes, arbitrary paths, undeclared
existing files, and writes after sealing. The component never generates the
payload.

`readback` requires the exact expected result file set, refuses symlinked result
files or the result directory, rechecks every wrapper and C6 slot/C7 draw
identity, records byte counts and SHA-256 hashes, and exclusively writes the
readback. Subsequent calls compare the existing sealed bytes. A changed payload
with unchanged counts still changes the sealed digest and is rejected. A C7
draw-cap result retains the requested 16 forms and actual selected count, and
sets `coverage_complete: false` when fewer than 16 were retained. It cannot
silently shrink the request or replace an exhausted attempt.
Every retained input and output is capped at 8 MiB before loading or writing;
the fixed tests include oversized-file refusal.

This is a custody check. Its readback status explicitly leaves arithmetic and
seed validation pending. Future integration must invoke the existing independent
C6 and C7 checkers before claiming a checked control result. In particular,
`compare_results` checks the structure and identity of supplied payloads; it
does not establish that their matrices, forms, geometry, or deterministic draw
stream are correct.

The ordinary `experiment_execution.load_plan`/`authorize` path remains the
admission authority. `input_sha256` is an additional explicit future trial-plan
requirement enforced here: it must bind the exact prospective schedule and each
stage's published join plans. The ordinary loader does not currently inspect
that map. The future plan must also bind this module in `source_sha256` and
include `expected_artifacts(schedule, stage)` in the existing trial artifacts.
These conditions leave the incomplete launcher/protocol admission unresolved;
this source stage does not freeze, approve, or dispatch the experiment.

The six watchdog values remain `(7200, 3600, 21600, 28800, 21600, 3600)`, summing
to 24 hours. Each trial remains capped at 4096 MiB in this component's shape
check. The original six-run, 4 GiB, 24 CPU-hour, 24-hour, zero-cloud-dollar,
no-retry limits and original P1-P4/C0-C7/H1 q13 criteria are unchanged. Custody
creates no extra execution allowance; accounting and all remaining supervisor
budget checks still belong to the future approved launcher and handoff.

Sources checked before implementation: repository `AGENTS.md`, the
`design-experiment` skill, the published prospective schedule,
`c67_control_schedule.py`, `c6_coordinate_control.py`, `c7_matched_random.py`,
`c7_seed_replay.py`, `candidate_stage.py`, `c5_preview_stage.py`,
`stage_router.py`, and `tools/experiment_execution.py`. These established the
existing batch formats, source selection, exact supervisor claim gate and
write-once component conventions. Python's official
[filesystem documentation](https://docs.python.org/3/library/os.html#os.open)
and [path API documentation](https://docs.python.org/3/library/pathlib.html#pathlib.Path.open)
were retrieved for exclusive creation and durable file flushing. No scientific
novelty or prior mathematical result is claimed by this source stage.

Ten fixed software fixtures in `test_c67_run_custody.py` cover published schedule
enumeration, changed counts and duplicate strata, prospective preparation,
exclusive wrapped writes, traversal/absolute/undeclared path refusal, run and
schedule substitution, duplicate C6 slots and C7 draws, missing/extra/symlink
outputs, changed retained bytes, and exhausted-draw coverage. Their C6 matrices
and C7 forms are explicit synthetic placeholders; no sampler or arithmetic
checker is invoked. The Coordinator subagent did not run these tests: root owns
validation under the delegated role boundary. Root verified them with Python
3.11 and PyYAML; the host's default Python 3.9 lacks the `hashlib.file_digest`
used by the existing supervisor. The validation command is:

```sh
cd /home/ec2-user/crypto-pext-radical-20261105/experiments/EXP-PEXT-bf8f96/implementation
uv run --no-project --python 3.11 --with pyyaml python -m unittest -v test_c67_run_custody
```

No specification, protocol, problem record, ledger, receipt, committed revision,
or publication state was changed by this component task.
