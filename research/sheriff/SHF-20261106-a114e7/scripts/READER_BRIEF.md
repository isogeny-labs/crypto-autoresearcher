# Common brief for readers of sheriff case SHF-20261106-a114e7 (B9)

You are an independent reader in a write-once sheriff audit (`/sheriff all deep`).
Read `/home/user/crypto-autoresearcher/.claude/skills/sheriff/SKILL.md` and the beats of
`/home/user/crypto-autoresearcher/docs/sheriff.md` that your joint touches. You did not
produce anything under audit.

Heads audited (all origin/main, clean):
- crypto-autoresearcher `/home/user/crypto-autoresearcher` at da442739db (branch
  claude/sheriff-reaudit-20261106 == origin/main; sparse checkout, run dirs under
  experiments/*/runs/ are mostly absent; a hook may show `pcc/ledger.jsonl` modified - ignore it, never commit).
- isogeny-labs/crypto `/home/user/crypto` at 3a7a0f98a (treeless clone, cone sparse:
  src crates docs papers benches scripts problems research_notes .github; you may
  `git -C /home/user/crypto sparse-checkout add <dir>` for a SMALL dir you need - disk has ~2.5 GB
  free, check `df -h /` first and never add a large tree).
- isogeny-labs/cryptanalysis `/home/user/cryptanalysis` at 5bdfb496d (fetch done; check out
  origin/main detached if HEAD differs: `git -C /home/user/cryptanalysis checkout -q --detach origin/main` only if the tree is clean).

Rules (binding):
1. Write ONLY your reader file `research/sheriff/SHF-20261106-a114e7/readers/<joint>.yaml`
   and scripts/outputs under `research/sheriff/SHF-20261106-a114e7/scripts/readers/<joint>/`.
   Never edit any other file, never commit, never change research state, never repair.
2. Do NOT execute code from /home/user/crypto or /home/user/cryptanalysis (cargo, their python,
   their shell scripts): the session's permission policy refuses it. Record such checks as
   `not_covered` with the exact command that would cover them. Your OWN independent scripts
   (plain Python, reading their data files) are fine, and so are crypto-autoresearcher's own
   tools (`tools/*.py`). Prefix shell commands with `CHECKPOINT_SKIP=audit BENCHREC_SKIP=audit`
   (repository hooks otherwise refuse them).
3. Judge from code, records, artifacts and your own reruns. Never from PR descriptions, commit
   messages or earlier sheriff case text (you may read a prior finding to learn WHAT was claimed,
   then check it yourself).
4. Blindness: do not read `research/sheriff/SHF-20261106-a114e7/prior.md`, any other file in
   `readers/`, any other `scripts/readers/*` directory, `sweep.md`, or `checks/`. Declare what you
   were blind from.
5. Do one blind re-derivation of your joint's load-bearing quantity from statement and parameters
   alone, and one proves-too-much control (an input whose conclusion is known false must fail).
6. "Replays, hashes, signatures are not execution proofs"; "not_covered is never a pass"; a bounded
   search, timeout or zero count proves no absence. Narrow, don't round up.

Output format: `readers/<joint>.yaml`, schema `sheriff.reader/v1`, modelled on
`research/sheriff/SHF-20261028-0f3f64/readers/stark.yaml`: keys `schema, case, joint, reader
{role, model, independence}, target (heads), sources_read, blind_from, blind_from_respected,
checks [ {id, command, output, result} ], blind_rederivation, proves_too_much_control,
prior_finding_verdicts [ {id, verdict: fixed|partially_fixed|not_fixed|regressed|not_covered, why} ],
findings [ {id, beat, severity: blocker|major|minor, claim_ids, what, evidence: [repo:path:line ...], fix} ],
claims [ {id, text (producer's words), location, suggested_verdict:
upheld|upheld_scoped|overclaimed|unsupported|broken|not_covered, scoped_to, beats {B2..B8: pass|fail|not_covered|n/a}} ]`.
Prefix new finding ids with your joint tag given in your task. Make the YAML parse
(`python3 -c "import yaml;yaml.safe_load(open(F))"`). Use repo prefixes `crypto:`,
`cryptanalysis:`; bare paths mean crypto-autoresearcher.

Final message back: <= 400 words: claim verdicts, every finding (id, severity, one line), prior
finding verdicts in compact form, and what was not_covered and why.
