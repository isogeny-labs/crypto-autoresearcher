# Versioned BSGS example correction

`solve_v2.py` and `check_v2.py` repair the identity-point serialization and checking path. `known-k=0` now writes `Q: null`, returns `k_found: 0`, and passes the independent checker. The driver rejects noncanonical `known-k` scalars outside `0 <= k < n`, including negatives that would not terminate in the original double-and-add loop.

The v1 source files, frozen runbook, and reference session retain their original SHA-256 bindings. The v2 files are direct-call examples until a separately frozen runbook session adopts them. They do not retroactively change the 14 historical outcomes.

`baby_steps` counts table positions and `giant_steps` counts lookup rounds, including the successful lookup. The legacy `group_ops` field sums these logical work units; it is not an executed-addition count. `setup_ops` is the deterministic double-and-add call count for computing `m*G`, which v2 checks. The checker validates result consistency and cannot prove that a solver ran. Use runbook audit replay for execution evidence.

For a direct identity test:

```sh
mkdir -p /tmp/bsgs-v2-zero
python3 examples/runbooks/toy-ecdlp-bsgs/solve_v2.py --trial-id zero --mode known-k --k 0 --curve examples/runbooks/toy-ecdlp-bsgs/curve.json --run-dir /tmp/bsgs-v2-zero
python3 examples/runbooks/toy-ecdlp-bsgs/check_v2.py /tmp/bsgs-v2-zero examples/runbooks/toy-ecdlp-bsgs/curve.json known-k 0
```

The [independent review packet](../../../docs/reports/2026-11-03-bsgs-coverage-review/README.md) gives the pinned theorem, curve count, source failure, and custody details.
