# The pcc ledger cannot be committed once it passes the artifact size gate

- **Status:** open
- **Kind:** conflict between two repository rules
- **Affected work:** [docs/pcc.md](../docs/pcc.md) ("Commit the ledger with the work"; "Never edit or rewrite `pcc/ledger.jsonl`"), [AGENTS.md "Data files live in the artifact store"](../AGENTS.md#data-files-live-in-the-artifact-store) (any `.jsonl` over 64 KiB goes to S3), `.claude/hooks/checkpoint-hook.sh`, and the `artifacts` and `size` checks
- **Next action owner:** maintainer of `tools/pcc/pcc.py` and the artifact policy
- **Last updated:** 2026-11-06
- **Raised by:** sheriff case [SHF-20261106-a114e7](../research/sheriff/SHF-20261106-a114e7/REPORT.md), PR #3071

## Problem

`checkpoint-hook.sh` appends a `bypass` entry to `pcc/ledger.jsonl` for every
command run with `CHECKPOINT_SKIP=<reason>`. Each entry embeds the full
command text. `docs/pcc.md` requires the ledger to be committed with the
work.

During one audit session, the hook appended 248 entries, about 239 KB. That
put `pcc/ledger.jsonl` over the 64 KiB `.jsonl` threshold, and both `artifacts`
and `size` failed on PR #3071 head `ef52d97e64` (run 42162055693, jobs
127709794795 and 127709794615).

The two fixes the rules offer conflict:

- Moving the file to the store (`artifacts.py push`) replaces it with a pointer.
  `pcc ledger verify --base origin/main` then has no ledger to prefix-check.
- Committing it under the `large-file-ok` label bypasses the size policy.

PR #3071 therefore restored the branch's ledger to origin/main's content, in a
new commit with no history rewrite. The session's 253-line local ledger, whose
chain verified, was not committed. Its bypass entries are not on GitHub.

## Evidence and uncertainty

- **Observed:** the check logs above name only `pcc/ledger.jsonl`, at 239,169 bytes.
- **Observed:** before the restore, `pcc ledger verify --base origin/main` reported `253 entries, chain ok`.
- **Not established:** how other long sessions have handled this. On main the ledger had 4 entries on 2026-11-06, so most sessions' bypass entries are probably not being committed.

## What would unblock it

- [ ] Choose one rule. Options:
  - exempt `pcc/ledger.jsonl` from the artifact policy;
  - shard the ledger into append-only per-session files, each small and hash-linked;
  - have the hook record a command digest instead of the full text.
- [ ] Make `pcc ledger verify` and `artifacts check` agree on that choice, with a test that a 1,000-entry ledger passes both.

## Next discriminating step

Run a long session that bypasses about 300 times, then check that both
`artifacts check` and `pcc ledger verify --base origin/main` pass on its PR.

## Resolution and history

2026-11-06 UTC: opened from PR #3071. Nothing repaired.
