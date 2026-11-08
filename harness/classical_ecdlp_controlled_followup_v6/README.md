# 96-domain controlled follow-up: source preparation

This additive version implements eight slots in each of four stages and three
unchanged field/order tiers: 96 domains, including 48 confirmation domains and
3,072 targets. It preserves 64 targets per confirmation domain, eight blindings,
all six decoder cells, all eight calibration arms, a separately charged generator,
and two actual solver processes. The original v5 and math source files remain
unchanged. These are workload specifications, not experimental outcomes.

| Planned work | Count |
| --- | ---: |
| Setups | 432 |
| Calibration singles | 691,200 |
| Traces and intent records, each | 73,728 |
| Confirmation decoder cells | 147,456 |
| BSGS target solves | 3,072 |

The field/order tiers remain 10/13/16 bits. Expanding the number of domains does
not establish scaling to larger groups, a new attack exponent, or a performance
advantage. The candidate equations and independently implemented reference math
are preserved. BSGS solver counters and diagnostic verification counters remain
separate; full-cost, primitive-replay and wall-clock qualification remain false.

## Check the source

From the repository root:

```sh
python3 -B harness/classical_ecdlp_controlled_followup_v6/prepare.py check
python3 -B harness/classical_ecdlp_controlled_followup_v6/build_source_manifest.py --repo-root "$PWD"
python3 -B harness/classical_ecdlp_controlled_followup_v6/test_v6.py
python3 -B harness/classical_ecdlp_controlled_followup_v6/test_contracts.py \
  --repo-root "$PWD" --contracts-root "$PWD" --control-root /tmp/v6-controls-UNIQUE
```

These controls use disclosed fixed software fixtures. They do not draw a fresh
cohort, authorize a scientific run or create a VM. The full static schedule can
be counted without drawing a curve or a nonce. Generated verification artifacts
are stored separately from the executable source lock.

## Bounded output

Production emits five logical JSONL streams as numbered parts of at most
128 MiB each, below the existing 2 GiB per-file ceiling. `streams.json` records
ordered membership, exact byte/record counts, part digests and the digest of the
logical concatenation. Rows never split between parts. Readers verify the full
physical membership and hashes before exposing the logical streams. The original
strict semantic JSON readers and public-equation checks still apply afterward.
Missing, reordered, extra, resized, tampered, partial-line and symlinked parts
are rejected. No stream is concatenated into a second large local copy.

Input reads support the declared 256 MiB ceiling; disclosed fixture defaults
remain smaller. The producer's file, tree, log, memory, watchdog and free-space
limits retain their own enforcement. Framing makes no worst-case fit guarantee.

## Budget access

`prepare.py budget --aws /path/to/aws --attempt-usd 15` issues only STS identity
and the three authorized `DescribeBudget` reads. It checks the expected account,
currency and finite values and reports conservative headroom. It always leaves
`execution_ready` false: lane reservations, placement and native admission are
separate requirements. USD15 is a proposed finite preparation allowance, not an
approved experiment budget or evidence of live funds.

The observed identity lacked an identity-based allow for `budgets:ViewBudget`.
`budget-reader-policy.json` is the exact three-resource read-only policy for the
authorized AWS operator to assess and attach. This implementation never attaches
policies, changes IAM, assumes another identity or submits work. Configure the
authorized profile through environment settings and rerun the read-only command;
keep credentials out of source files and chat.

## What remains before execution

The protected main synchronization encountered conflicts in the PCC journal and
schema-supersession registry. That merge was aborted; no protected record was
selected, rewritten or rechained. This source branch is based on the preserved
continuation and must not be called natively admitted. The fixed source-review
plan and exact remaining checklist are in `preparation/`.

After the protected synchronization is legitimately resolved, the Coordinator
can file the one fresh native experiment, freeze its protocol, bind exclusions
covering the prior inventory plus all exposed domains, and arrange independent
source review. A nonce must be drawn only after the scientific contract and
source are frozen. Freeze and publish the resulting inputs/configuration and
actual source revision before cloud work. New IDs, absolute deadlines, total
attempt allowance, live budget/lane reservations and isolated placement must be
real; the old completed/exhausted parents are not reused.

The native plan invokes `driver.py production` with the actual plan/trial/config
and fresh run directory. Execute that plan through `tools/experiment_execution.py`
with its real owner and epoch. The driver repeats native authorization before
generation; it has no `approved=true` shortcut. `prepare.py` does not submit work.

## Sources checked

SEC 1 v2 §2.2.1 was read directly for the prime-field group laws and subgroup
equations. Existing source contracts, frozen v5 protocol and independent math
reviews supplied the internal mechanism and accounting context. The official
HAC chapter download returned HTTP503; its Algorithm3.56 citation remains an
internal prior reference, not a claimed fresh primary-source read. No novelty
claim is made. See `preparation/scope-and-literature.md` for the full scope.
