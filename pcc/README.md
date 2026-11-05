# pcc: proof-carrying claims data

Data for `tools/pcc/pcc.py`; the contract is
[`docs/SABOTAGE_RESISTANCE.md`](../docs/SABOTAGE_RESISTANCE.md).

- `keyring.json`: public keys that may sign verdicts, and the SHA-256 of every
  execution-proof verifier the gate may run. Only the owner edits it.
- `ledger.jsonl`: append-only, hash-chained record of claims, verdicts and
  hook bypasses. CI checks that the base branch's ledger is a prefix of this one.
- `claims/`: one `pcc.claim/v1` record per claim (created with `pcc claim new`).
