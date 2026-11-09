# EXP-PFDR-fa915a director compile blocker

Status: no runbook or mechanical task card produced. No scientific execution or external API call was made. `model_provenance` is `operator-supplied`; `verified_model` is `false` in the supplied resolver receipt. This report makes no model verification claim.

## Frozen execution requirement

The prospective specification's `experiment.budget` and `experiment.stopping_rules` require the new five-stage supervisor to run through `experiments/EXP-PFDR-fa915a/launch-recovery.sh` inside one verified systemd user scope with `MemoryMax=4G`, `CPUQuota=400%`, `RuntimeMaxSec=107570`, `TimeoutStopSec=30`, and `KillSignal=SIGINT`; the aggregate hard ceiling is 107600 seconds. The prospective handoff says “Launch only with” that committed launcher. The frozen trial plan binds its SHA-256 `3dd7a870d4475473ca93e9e0c578b2a0e75b08866385478faee7ff02d781afad`.

`tools/runbook.py` cannot express that execution route. For an `EXP-*` trials step, lint accepts only `engine: supervisor` (`_lint_trials`, lines 829-838). `_supervise` then constructs and runs `python3 tools/experiment_execution.py run --plan ... --owner ... --epoch ...` directly (lines 1605-1613), without calling the launcher or entering its whole-batch scope. The `command` step kind is restricted to probe, coordination, or verification; it cannot be used to launch scientific trials. A runbook that passes current lint would therefore fail the frozen resource-scope requirement. Adding a runbook assertion about the scope would not put the supervisor inside it.

There is a second independent lint blocker: `_lint_supervisor_queue` (lines 987-991) requires the executor task's `write_scope` to include the runbook session directory. The committed queue task `TASK-20261109-5f9d41` currently has only `experiments/EXP-PFDR-fa915a/runs/` in `write_scope`. It contains no `experiments/EXP-PFDR-fa915a/runbook-sessions/` path. The queue and handoff are outside the director's exclusive write scope.

The existing `executor-implementation` route remains the applicable route. A mechanical route would require a versioned runbook supervisor that invokes the frozen launcher under the exact whole-batch guard, a queue that authorizes its session artifacts, and a new Coordinator approval of the resulting exact runbook SHA-256. No scientific parameter, validity assertion, or retry allowance should change to make lint pass.

## Read-only binding check

| File | SHA-256 |
| --- | --- |
| `experiments/EXP-PFDR-fa915a/protocol.json` | `edc4b13f36b12cfde1497e850c40dea60e4d5ef0bb486932452874b25eaee355` |
| `experiments/EXP-PFDR-fa915a/trial-plan.json` | `73cc480d6400c7e9caa18fc0b9a674344ee389d614b6865c1f6451516b665617` |
| `experiments/EXP-PFDR-fa915a/launch-recovery.sh` | `3dd7a870d4475473ca93e9e0c578b2a0e75b08866385478faee7ff02d781afad` |
| `experiments/EXP-PFDR-fa915a/implementation/run.py` | `bf586c0f6affb4329fb046df1e4110374695d78c20180e30e8a73424ef6a80f0` |
| `experiments/EXP-PFDR-fa915a/implementation/check.py` | `064db8505c9531cc05aeab025b48e6022027a818fe38b33508b2ec0d0c2e62f1` |
| `experiments/EXP-PFDR-fa915a/implementation/paircount.c` | `0d8e943fabbbeefa3e7796f833957c17f12a09ca056dc11974002f2745fac696` |
| `experiments/EXP-PFDR-fa915a/implementation/vendor/curve.py` | `fcca2beb699b4785c25820df1d949b757be7a273efd2f4f015625d7aa13c67fa` |
| `coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-839760/dispatch_queue.json` | `ded3202bf26ae3a69246290c78b42602b6d33bcfdc2e5d6696370307e4039c33` |
| `ledger/handoffs/TASK-20261109-5f9d41.yaml` | `c27472bef345f3738301fb18e4f61b3939258bb5955f9eacf9e81995d2b9a4c1` |

Commands: `sha256sum` on the named files; `jq '.tasks[0] | {id,role,write_scope,artifact_paths_count:(.artifact_paths|length)}'` on the committed queue. Queue output: `id=TASK-20261109-5f9d41`, `role=executor`, `write_scope=["experiments/EXP-PFDR-fa915a/runs/"]`, `artifact_paths_count=58`.

Runbook lint: not run, because a runbook satisfying the frozen launcher and current runbook schema cannot be written. Card lint: not run, because there is no runbook/card to lint. No `LINT OK` or `CARD OK` claim is made.
