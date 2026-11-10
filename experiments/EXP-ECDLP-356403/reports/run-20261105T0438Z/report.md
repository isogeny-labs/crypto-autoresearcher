# Full0438 retained native run report

# Same-cohort recovery: operational stop

{
  "schema": "classical.ecdlp.closed-recovery-mini/v1",
  "run_id": "RUN-ECDLP-52de64",
  "native_status": "infrastructure_error",
  "candidate_resource_stop": "free_byte_reserve",
  "baseline_resource_stop": "free_byte_reserve",
  "actual_outer_seconds": 708.5941677360024,
  "first_attempt_outer_seconds_separate": 239.00964503300202,
  "counts_only": {
    "attempted_native_trials": 1,
    "native_output_validated_trials": 0,
    "generated_curve_entries": 48
  },
  "complete_jsonl_prefix_rows": {
    "cells": 73236,
    "intents": 36783,
    "setups": 216,
    "singles": 345600,
    "traces": 36782
  },
  "partial_tail_flags": {
    "cells": false,
    "intents": false,
    "setups": false,
    "singles": false,
    "traces": false
  },
  "baseline_BSGS_output": "absent, not a zero success measurement",
  "independent_checker": "not run",
  "prefix_self_reported_recovery_records": "UNVALIDATED; not accepted recovery evidence",
  "cohort_and_job_hash_match": true,
  "logical_raw_files": 61,
  "logical_raw_bytes": 2447366254,
  "harvest_input_sha256": "0c2623f925cc78a35cc363496e63754773f93976ec48dcc2e5c5111f17c432be",
  "closed_native_receipt": {
    "bytes": 1549,
    "sha256": "dc8f03ea4871bb1401e302b3e70569ba074a991a9c0114acdb73c789b4633eb7"
  },
  "actual_outer_wait_record": {
    "bytes": 2085,
    "path": "/workspace/classical-ecdlp-endpoint-reuse/fresh48-20261105-root/native-recovery-full48.json",
    "sha256": "4ebbc2968cbb3c2c45ae10b6a8c5b58afe9bc6072f17c2e4fd5196d14ddcd637"
  },
  "benchmark_record_status": "INVALID/censored operational stop; no measured solverperformance",
  "next_attempt_authorized": false
}

All partial candidate statuses are unvalidated selfreports; no mathematical/performance inference or thirdattempt approval. Records-first publication and actual f3 terminal preservation precede this full report.


Exact native argv:

```json
["python3", "-B", "harness/classical_ecdlp_controlled_followup_v5/driver.py", "production", "--repo-root", "/workspace/classical-ecdlp-validation-ready", "--out", "/workspace/classical-ecdlp-validation-ready/experiments/EXP-ECDLP-356403/runs/RUN-ECDLP-52de64", "--trial-plan", "experiments/EXP-ECDLP-356403/trial-plan.json", "--trial-id", "recovery-full48", "--config", "experiments/EXP-ECDLP-356403/recovery-v2/production-config.json"]

```

Host/environment: {"host": {"cpu": "INTEL(R) XEON(R) PLATINUM 8573C", "cpus_online": 5, "hostname": "bed07a19751a", "isolation": "unstated", "platform": "Linux-6.18.57-x86_64-with-glibc2.41"}, "python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]", "platform": "linux", "launch_commit": "3d54c4a5061da97d9867a3b92e05a921ff15a508"}

Missing outputs: ["execution/baseline/result/analytical-reference.json", "execution/baseline/result/bsgs.json", "execution/baseline/result/verification.json", "execution/candidate/result/raw/engine-completion.json", "execution/candidate/result/raw/engine-summary.json", "manifest.yaml", "raw-result.json", "root-custody.json", "root-custody/seal.json", "shared/generator/barrier-ready.json", "typed-export/export.json", "typed-export/export.validation.json"]

160 selfreported anycell recovered targets remain UNVALIDATED. Two physical solver processes,48 unique public curves across all attempts; methods/blindings/cells are dependent views. No rates, stats, S, runtime comparison, novelty or mathematical conclusion. First239.00964503300202s and second708.5941677360024s are separate unqualified costs.
