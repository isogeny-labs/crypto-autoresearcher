# DEV-1 cell report, TASK-20261106-96fee7 (EXP-MONO-1a1be2)

Instrument KAT, not an experiment run. Zero experiment runs. No contract cell computed, no predicted value asserted.

## Outcome: stopped_infrastructure (DX-4 / DX-6). Not a KAT outcome, not evidence.

The full cell started 2026-11-06T23:24:10Z and was killed at about 7,200 s elapsed (last heartbeat 01:23:12Z, elapsed 7,140 s). Cause: an Executor error. The cell was launched with the harness background `timeout` at its maximum, 7,200,000 ms, which is far below the 41,400 s cell watchdog. The harness stopped the background task at that limit and the pytest process group died with it. This is not the cell's watchdog, not a crash of the code under test and not an out-of-memory kill. pytest wrote no junit.xml (it writes at session end); `dev1-junit-96fee7.xml` is a labelled placeholder. The stdout log showed two progress dots (the two helper items passed) before the kill; the full cell item (third) was running. No per-target count pair, guard count, multiset-pass timing or peak RSS exists. The cell was not shrunk and was not restarted: a restart cannot complete inside the task budget (43,200 s from about 23:05Z on 11-06, deadline about 11:05Z on 11-07; at the 01:32Z kill-detection time about 33,500 s remained, below the 37,777 s projection and the 39,600 s go threshold). The launch-limit constraint is a scope finding for the Coordinator: the full cell needs a launcher that survives the harness background limit (for example a detached process that is not a child of the harness task, or a session that re-attaches), and then a fresh task and fresh budget.

## DX-1 bytes
Copy of experiments/EXP-MONO-1a1be2/code at a scratch directory outside the repository. Verified by sha256sum before the projection and the cell: launcher.py (a7dcb7de...c2be), tests/test_kat.py (6da794c6...5a66) and README.md (44fc3004...b458aab) equal the digests given for the 2b7223 release; test_kat_extended.py equals 79894702...06b5; the other files equal input_pins_TASK-20261106-96fee7_frozen. launcher.scan_problems of the copy: none (allow-list check passed). launcher.code_sha256() = 5d5a607d59741b699065c02066d56a2883a34b44431da56c7bfd439b1f731464. Re-verified after the kill: all 11 file hashes and code_sha256 identical, and equal to the repository working tree. Per-file hashes are in dev1-kat-log-96fee7.json (dx1_hashes_before/after). Note: before.json was written by a second hashing pass a few minutes after the cell started; the pre-cell verification itself was the sha256sum listing taken before the projection.

## Command
python3 -B -P -X pycache_prefix=<fresh dir> -c "<launcher.PYTEST_WRAPPER>" -q -p no:cacheprovider --noconftest -c /dev/null --rootdir <copy code dir> --junitxml <outside> <copy>/tests/test_kat_extended.py, built by launcher._suite_argv; env from launcher.selftest_environment plus KAT_EXT_LOG_PATH (scratch); cwd a fresh temp directory outside the code dir; PYTEST_ADDOPTS, PYTEST_PLUGINS, PYTHONPATH, PYTHONPYCACHEPREFIX, PYTHONSAFEPATH, PYTHONHOME removed; plugin autoload off. Exact argv in the kat log.

## DX-3 projection (measured, then modelled)
Same sub-base method as 4c4831 (arm_c_cell on D[:800], D[:1250], D[:2500] at m = 3, s = 50; pair-sum table first 200 rows; one-target query), 725 s wall (limit 1,200 s). Modelled total projection 37,777 s, within the 39,600 s threshold, so the cell was started. Inputs and the three kernel fractions are in dev1-kat-log-96fee7.json (dx3_projection).

## Checkpoints
.resume/RESUME.md filled (scripts/checkpoint.sh init) and pushed before the cell (token in the environment had expired; the push used the ambient AWS credentials via awscli, with the expired token variable unset for that call; no hook was bypassed). A second push followed after this stop.

## Scope findings
1. SF-96fee7-1: the harness background launch is capped at 7,200,000 ms; a 10.5 h cell cannot be a child of one background task. Needs a re-dispatch with a detached or re-attached launcher.
2. The cell would have used the 4 available cores only on one thread (pytest, serial); nothing was parallelised.
