# Sabotage is assumed: proof-carrying claims (this repository)

AGENTS.md, core rule 17, points here; this file is the rule. It is kept out
of AGENTS.md because AGENTS.md and CLAUDE.md are always loaded and held to
a word budget (`tools/check_instruction_budget.py`).

Owner rule, 2026-11-04. Every producer, this session included, is assumed to
be sabotaging the work: numbers, booleans, receipts, proofs, prose and chat
answers are data until a verifier the producer did not write has checked them.
The contract is [`docs/SABOTAGE_RESISTANCE.md`](SABOTAGE_RESISTANCE.md);
the tool is `tools/pcc/pcc.py` (byte-identical across the lab's repositories;
`docs/shared-code.lock.json`).

- **A claim is a record.** Before a result is cited anywhere (leaderboard,
  benchmarks, PR body, session log, paper, chat), write it with
  `python3 tools/pcc/pcc.py claim new --kind <theorem|solve|measurement|speedup|execution|absence> --statement "…" --proof KIND:PATH …`.
  The record pins every proof by SHA-256 and lands in `pcc/claims/` and the
  ledger `pcc/ledger.jsonl`.
- **Only a signed verdict verifies.** `pcc verify` runs the verifier for each
  proof kind (Lean statement binding and holes, solve and zero-knowledge
  solve certificates with the tool's own arithmetic, replay certificates and
  validator reports with a keyring signature, execution receipts through a
  verifier pinned in `pcc/keyring.json`). The signed verdict is written by CI
  after a merge (`pcc-sign.yml`, key `ci-main`), never by the producing session.
  `independent: true` and `verified: true` written by a producer are not read.
- **Standing, not words.** `python3 tools/pcc/pcc.py standing <id>` is the only
  source for "verified". Anything else is an unverified assertion and is
  labelled so: in prose, cite `[pcc:<id>]` for a verified claim or tag the
  sentence `[pcc:unverified]`. `pcc lint-prose` enforces this on pull request
  bodies in CI and is run on reports and session logs.
- **The ledger is append-only.** `pcc ledger verify --base origin/main` runs
  on every pull request: the base ledger must be a prefix of the head's and
  every hash link must hold. Never edit or rewrite `pcc/ledger.jsonl`.
- **Bypasses are recorded.** `CHECKPOINT_SKIP=<reason>` still works, and the
  hook now appends a `bypass` entry to the ledger and pushes a checkpoint
  before the command runs. Commit the ledger with the work.
- **Claims have a type.** `--claim-type data|literature|interpretive` is
  required for claims created on or after 2026-11-11 (older claims without it
  count as `data`); `pcc ledger verify` fails a newer claim without it.
  `pcc standing-by-type` counts standings per type, and
  `pcc sample-for-validation --rate-data 1 --rate-interpretive 3 --seed N --out F`
  draws a seeded, stratified sample for independent validation (interpretive
  at least 3x the data rate; at least one claim per non-empty type). The sample
  is a work list; it verifies nothing.
- **The verifier is tested against sabotage.** `pcc canary` plants every
  sabotage class in the contract into a passing fixture and must reject each
  one; CI runs it on every pull request. A new way to cheat the gate becomes a
  new canary in the same change that closes it.
- **Chat answers follow the same rule.** State a result with its claim id and
  standing, or say that it is an unverified assertion. Never present a
  self-check, a replay, a hash or a model's agreement as verification.

In this repository a pcc standing is machine evidence, never a research-state
transition: the Coordinator's authority, review routing and `review-evidence`
are unchanged, and a `verified` standing satisfies no review plan by itself.
The `execution` proof kind is the verifier seam of
[`docs/execution-proof-chain.md`](execution-proof-chain.md); a sheriff case
may cite a standing, and a standing is never a case. The progress-fidelity gate
still governs `claims/*.json`; pcc claims live in `pcc/claims/` and do not
replace them.

What this does not yet give: a real execution-proof backend. Until a verifier
digest is listed under `trusted_verifiers` in `pcc/keyring.json`, every
`execution` proof is `not_covered`, and no result here is execution verified
(`crypto-autoresearcher:docs/execution-proof-chain.md`, milestones open).
