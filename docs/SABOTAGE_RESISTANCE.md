# Sabotage resistance: proof-carrying claims across the lab

Status: contract and first implementation, 2026-11-04. Applies to `crypto`,
`cryptanalysis`, `crypto-autoresearcher` and `delphi`. The tool is
`tools/pcc/pcc.py` (kept byte-identical across repositories by the shared-code
lock); the data lives under `pcc/` in each repository.

## 1. The assumption

Every producer in this lab may be sabotaging the work. "Producer" means any
session, model, script or person that writes code, runs an experiment, writes
a number, writes a proof, writes a report, or answers a question in chat. The
producer may:

- fabricate or round a number, or pick the best of k runs and report one;
- write `independent: true`, `verified: true`, `status: pass` by hand;
- write a receipt or certificate by hand, or edit one after the fact;
- prove a theorem that is not the claim (wrong quantifier, vacuous
  hypothesis, toy parameter, conclusion `True`) and cite it as the claim;
- hide a `sorry`, an `axiom`, `native_decide` or `#exit` where a text scan
  does not look;
- bypass a hook (`CHECKPOINT_SKIP=`), skip a gate, or run a launcher the gate
  did not see;
- re-seal an unkeyed hash chain after rewriting the observations;
- cite a proof that verified a different statement, or a receipt produced in
  dev mode;
- weaken a test so a sabotaged verifier still passes;
- argue convincingly in prose, in a PR body, in a session log or in a chat
  answer, with no artifact behind the words.

The question the harness answers is never "is the producer honest?" but
"what does the evidence establish if the producer is not?"

## 2. The trusted base

What a saboteur is assumed **not** to control:

| trusted component | why it is trusted | what it gives us |
| --- | --- | --- |
| git history on `main` (no force-push) | hosting policy | append-only witness of what was committed when |
| CI on `main` with repository secrets the producer session never holds | the session cannot read `secrets.*` | a verifier identity (signing key) separate from the producer |
| the Lean 4 kernel and `lake` from the pinned toolchain | kernel-checked | theorem validity, given statement fidelity |
| a proof-system verifier pinned by SHA-256 **and listed in the keyring** (RISC Zero receipts, later) | reviewed release, digest-pinned | execution validity of a prescribed computation |
| the owner's key and the CI key in `pcc/keyring.json` | the only keys that sign verdicts | "independent" becomes a signature, not a boolean |
| an external, append-only anchor (S3 checkpoints under a presigned POST policy; later a transparency log) | the producer cannot delete or rewrite | pre-registration and bypass events survive a rewritten branch |

Everything else, including every JSON field a producer writes and every
sentence a model writes, is data.

## 3. Invariants the harness enforces

- **I1 No bare claims.** A claim is a record (`pcc.claim/v1`) that names its
  statement, its scope and its proofs. A sentence that makes a claim without a
  record, or with a record whose standing is not `verified`, is an
  *unverified assertion* wherever it appears: leaderboard, benchmarks, PR body,
  session log, paper, chat answer.
- **I2 Producer and verifier are separate.** A verdict is produced by
  `pcc verify` running where the producer is not: CI on `main`, or a host with
  a keyring key. The verdict is signed (Ed25519) by that key. A producer
  cannot sign, so a producer cannot verify its own work. Self-reported
  booleans (`independent`, `verified`, `pass`) are never read as facts.
- **I3 Append-only, hash-chained ledger.** `pcc/ledger.jsonl` chains every
  claim, verdict and bypass event by hash. CI checks that the base branch's
  ledger is a prefix of the pull request's ledger and that every link holds.
  Rewriting or deleting history is visible; it is not prevented, it is caught.
- **I4 Statement binding.** A proof is bound to the exact statement it
  proves: a Lean proof pins the SHA-256 of the declaration text, a solve
  certificate pins the curve, `P`, `Q`; an execution receipt pins the image id
  and a journal that commits to the raw-result bytes. A proof of a different
  statement is a failure, not a near miss.
- **I5 The verifier is shown to reject sabotage.** `pcc canary` plants every
  sabotage class of section 5 into a passing fixture and requires the
  verifier to reject each one and accept the unmutated fixture. CI runs it on
  every pull request. A verifier that accepts one canary fails the build. This
  is the measurable form of "invariance against sabotage": the set of
  artifacts the gate rejects contains the canary corpus, and the corpus grows
  whenever a new sabotage is found.
- **I6 No silent bypass.** A hook opt-out (`CHECKPOINT_SKIP=`) is recorded as
  a ledger `bypass` event and pushed to the external anchor before the command
  runs. The opt-out still works; it is no longer invisible.
- **I7 Typed proof strength.** Every proof kind carries what it establishes
  and what it does not (section 4). The gate maps a claim kind to the minimum
  proof kind it needs; a weaker proof gives standing `scoped`, never
  `verified`.
- **I8 Chat answers carry proof status.** An answer that states a result names
  the claim id and its standing, or says "unverified assertion". The prose
  linter (`pcc lint-prose`) applies the same rule to PR bodies, session logs
  and reports: a strong-claim word with no `[pcc:ID]` citation that resolves to
  a verified claim fails, unless the sentence is tagged `[pcc:unverified]`.

## 4. Proof kinds

| kind | artifact | the verifier checks | establishes | does not establish |
| --- | --- | --- | --- | --- |
| `lean` | a Lake project or standalone file, a theorem name, `decl_sha256` | declaration text hashes to `decl_sha256`; no `sorry`/`admit`/`axiom`/`native_decide`/`skipKernelTC`/`#exit` outside comments and strings; conclusion is not `True`; `lake build` + transitive axiom audit (`propext`, `Classical.choice`, `Quot.sound` only) when `lake` is present, else `not_covered` | the theorem as stated | that the statement is the claim (a reader checks fidelity, B3 of the sheriff checklist) |
| `certificate` | `pcc.solve-certificate/v1`: curve, `P`, `Q`, `k` | `P`, `Q` on the curve; `n` prime; `[n]P = O`; `1 ≤ k < n`; `[k]P = Q`, with arithmetic in the verifier (plain Python, no producer code) | that solution | the search, its cost, its distribution |
| `zk-certificate` | `pcc.zk-solve-certificate/v1`: curve, `P`, `Q`, Schnorr `(R, s)` | as above, then `[s]P = R + [e]Q` with `e = H(domain ‖ curve ‖ P ‖ Q ‖ R) mod n` | knowledge of `k` with `Q = [k]P`, without revealing `k` | the same limits as `certificate` |
| `replay` | replay certificate JSON **and** a keyring signature | the pinned file hashes; `status`, `runs`, `scalars_verified` as the validation gate reads them; a signature by a keyring key over the certificate's digest. Unsigned: `not_covered` (independence not established); signed by the wrong key or over other bytes: `fail` | fabrication is bounded by an independent replay | execution: a replay is never an execution proof |
| `recompute` | validator report JSON and a keyring signature, with `evidence_dir` naming the directory its `raw_data` paths are relative to (default: the report's directory) | raw data files exist inside the repository and hash as pinned (an unpinned entry leaves the proof `not_covered`); every headline number recomputed within `rel_tol`; signature by a keyring key (unsigned: `not_covered`; wrong: `fail`) | the headline follows from the raw data | that the raw data were produced as described |
| `execution` | receipt, journal, verifier binary pinned by SHA-256, image id | the verifier binary hashes to its pin **and** the pin is in `keyring.trusted_verifiers`; the verifier reports `verified: true`, `dev_mode: false`, the pinned image id, the receipt digest; the journal commits to the raw-result SHA-256 | the prescribed computation produced those bytes (to the proof system's stated security, about 96 bits for RISC Zero v3) | native cost, wall time, or anything outside the guest |
| `attestation` | `pcc.signature/v1` over a subject digest | Ed25519 signature by a keyring key, subject digest matches the artifact (unsigned: `not_covered`; wrong: `fail`) | who vouched for which bytes | anything about the bytes themselves |

Minimum proof per claim kind: `theorem` → `lean`; `solve` → `certificate` or
`zk-certificate`; `measurement` → `recompute` **and** `replay`; `speedup` →
`measurement` plus the validation gate's matched rho reference; `execution` →
`execution`; `absence` → `execution` (proved exhaustive coverage) or `lean`.
`statement` claims (an observation with no result behind it) need no proof
and can never be `verified`; they render as unverified assertions.

Standing of a claim: `verified` when a signed `pass` verdict for the claim's
current digest exists in the ledger and every required proof kind passed;
`scoped` when the proofs that passed cover a weaker statement than the claim
(recorded in `scoped_to`); `not_covered` when a verifier could not run
(toolchain absent, verifier not trusted); `failed` when any proof failed;
`unverified` otherwise. Only `verified` may be cited without a caveat.

## 5. Sabotage canaries (the corpus `pcc canary` must reject)

certificate: wrong `k`; `Q` off the curve; composite `n`; `[n]P ≠ O`;
zk-certificate: tampered `s`; proof transplanted to a different `Q`;
lean: `sorry` in a proof; `native_decide`; a user `axiom`; `skipKernelTC`;
`#exit` before the theorem; statement edited after pinning (`decl_sha256`);
conclusion `True`;
replay: signature by an untrusted key; signature over other bytes; empty
`runs` even when signed; status not verified; (no signature at all, or
`independent: true` written by the producer without a signature, must leave
the proof `not_covered`, never `verified`);
recompute: headline claimed ≠ recomputed; raw data digest mismatch; raw data
path outside the repository; (an unpinned raw-data entry must leave the proof
`not_covered`);
execution: `dev_mode: true`; verifier binary digest mismatch; verifier
digest not in the keyring; journal does not commit to the raw result; wrong
image id;
attestation: wrong key; signature over a different subject;
ledger: an entry edited (chain breaks); an entry deleted (sequence gap);
history rewritten (base is not a prefix); a verdict whose claim digest no
longer matches the claim (stale verdict after an edit); a verdict without a
trusted signature;
claim: proof path outside the repository; pinned proof digest mismatch; a
claim kind whose minimum proof kind is absent;
prose: a strong-claim sentence with no citation; a citation to a claim that
is not verified.

Look-alikes that must **not** be flagged: `sorry` inside a comment or string;
a verified claim cited in prose; a sentence explicitly tagged
`[pcc:unverified]`.

## 6. Where each invariant is enforced

| invariant | crypto | cryptanalysis | crypto-autoresearcher | delphi |
| --- | --- | --- | --- | --- |
| I1, I4, I7 | `tools/pcc/pcc.py verify`, `pcc/claims/` | same tool, same layout | port of the same tool (lock entry) | `-proof-required`: a claim without a verifier action with verdict `pass` cannot be accepted |
| I2 | `pcc-gate.yml` signs verdicts on `main` with `PCC_SIGNING_KEY`; keyring holds the public key | same workflow | same | verifier tools run by Delphi, never by the model; verdict parsed by Delphi |
| I3 | `pcc ledger verify --base origin/main` on every PR | same | same | `goal.json` records argv and SHA-256 of every action's output |
| I5 | `pcc canary` in `pcc-gate.yml` | same | same | unit tests plant unverified claims and assert `revise` |
| I6 | `.claude/hooks/checkpoint-hook.sh` logs `CHECKPOINT_SKIP` to the ledger and pushes | same | n/a | n/a |
| I8 | `pcc lint-prose` on PR bodies, session logs, reports | same | same | reviewer prompt labels unverified claims |

## 7. What this does and does not deliver today

Delivered: the claim and ledger schemas; verifiers for `certificate`,
`zk-certificate`, `lean` (textual and statement binding; kernel build when
`lake` is on the path), `replay`, `recompute`, `execution` (contract and a
mock verifier for the canaries only; no trusted verifier is pinned yet) and
`attestation`; signing; the canary corpus; the prose linter; CI gates; the
hook bypass log; Delphi's proof-required mode.

Not delivered, and not claimed: a real execution-proof backend. The
RISC Zero guest for a prescribed walk is milestone 2 of
`crypto-autoresearcher:docs/execution-proof-chain.md` and remains open. Until
a verifier digest is listed in `pcc/keyring.json`, every `execution` proof
is `not_covered`, and no result in these repositories is execution verified.
The in-house `src/zk/stark_v2.rs` is a one-column affine AIR, disclaimed by
its own header, and is not wired as a backend. Statement fidelity of a Lean
theorem (that it says what the claim says) remains a reader's job; the tool
only pins the statement so it cannot drift after review.

## 7a. The first claims

`scripts/pcc_leaderboard_claims.py` records one `measurement` claim per
validated leaderboard row (Tables A and B: 19 rows on 2026-11-04), its proofs
the row's replay certificate and validator report as `VALIDATION.json` pins
them, its `row` block the gate's row digest. The script is idempotent and
re-runs after every leaderboard rebuild; a changed row gets a new claim that
names the one it supersedes. Until the CI key signs, every one of them stands
`not_covered`: the replay and the recompute are on disk and re-check, but
nobody independent has vouched for them yet. That is the true state and the
board says so.

## 8. Reading a result under this contract

1. Find the claim id in `pcc/claims/` or the ledger.
2. `python3 tools/pcc/pcc.py standing <id>` prints the standing, the proofs
   that passed, the signed verdict and its key.
3. Anything the standing does not cover is not established, however the
   sentence reads.
