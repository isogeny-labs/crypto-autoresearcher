# launch_eks.sh v3 (main session, 2026-11-06T22:36:54Z)

v3 = v2 (2fa09e84..., the accepted duplicate-check fix) + a schema-valid manifest.yaml.
sha256 v3: 7dbe33eb56843daa47885e58df644371b86052c7c42e4f11bcf38c17bc9d386d
Patch orig->v3: launch_eks.patch; v2->v3: launch_eks.v2-to-v3.patch.

## Why
CI on PR #3105 (merge-hygiene, ledger) rejects runs/RUN-ICPERF-c7f69e/manifest.yaml: "run missing required field
'status' / 'code' / 'environment' / 'inputs' / 'timing'; run.code.commit missing; run.result.certificate.kind must be
one of discrete_log|decomposition|none". The v1/v2 wrapper writes a flat 10-line manifest. Every run of the new
session would fail the same way.

## Change (write_records only, plus t0/s0 clock and argv capture after arg parsing)
manifest.yaml is now JSON (a YAML subset) derived only from raw-result.json, the wrapper's clock and argv:
- status: failed_implementation if not submitted; completed_inconclusive if outcome_class job_completed;
  failed_infrastructure otherwise. valid: false always; invalid_reason says validity is judged by analyze-c1.sh
  in S03-verify (completed case) or names outcome/refusal. The wrapper never judges validity.
- code {commit: git rev-parse HEAD, dirty: tracked changes, command: argv JSON}; environment {file: environment.json}
  (no python key, so runbook.py's interpreter parity still reads environment.json); inputs {curve_id null, seed 0
  placeholder, parameters: job_name and request hashes}; timing {started_at, finished_at, wall_seconds};
  resources nulls; certificate {kind none, verified false}; artifacts {raw_result, job_dir, job_files}.
- raw-result.json, exit codes, outcome classes, the duplicate check and the submission are unchanged.

## Tests
- bash -n OK. Duplicate-check block byte-identical to v2, so F3 (fix-tests.log) carries over.
- write_records extracted and run for three synthetic outcomes (refusal, job_completed, deadline_hit) with the
  supervisor's companion files present: tools/validate_ledger.check_run reports no errors for all three.

## Stopped run RUN-ICPERF-c7f69e (PR #3105 CI)
Sealed run bytes unchanged. Superseding record experiments/EXP-ICPERF-127dbd/supersessions/RUN-ICPERF-c7f69e/
manifest_v2.yaml (sha256 5298e33a...), registered in tools/run_supersession_registry.yaml with
decision_id DEC-20261106-ecf261, kind additive_schema_completion, run.status failed_implementation,
receipt_status infrastructure_error. check_run, check_run_supersessions and check_new_run_supersessions: no errors.
Committed locally only; pushed with the approval archive so the registry never names a decision absent from main.
