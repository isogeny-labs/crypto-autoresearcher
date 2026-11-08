# J3: Semaev certificate machine evidence

Reviewer task `TASK-20261108-5ef48a`, Conductor `T-1937`. Review source:
`6a0eb9665191e35690b4ff5ebd91c63561e09ec4`. Reviewed joint: J3 only.

**Verdict: inconclusive for fresh exact-target verification; the archived
execution and input-consistency checks hold at their stated scope.** No Lean
process was launched by this reviewer. The coordinator has launched forced
workflow run `42446577502`; its recorded status is pending at this seal and its
outcome must be reconciled separately. No J1 or J2 report was read.

## Checks completed

The six files in `input-bindings.json` match their pinned byte counts and
SHA-256 values. The current target source is
`formal/CryptoResearch/Semaev/Certificate.lean`, SHA-256
`aa022e4829eefc2cbe9ac05cbeb39f81e9e3eaa8147e2e41e9d718f11976bd89`.
The frozen name is a theorem,
`CryptoResearch.Semaev.decidable_validDecomposition`; the executable instance
has the distinct name `instDecidableValidDecomposition`. The theorem establishes
that `decide (validDecomposition ...) = true` iff each summand is a finite
point satisfying the curve equation and declared span condition and the sum
equals the target. Its recorded elaborated type quantifies over fields `F,K`,
`[Fintype F]`, `[DecidableEq K]`, `[Algebra F K]`, all basis and tuple sizes,
curve, spanning family, points and target. It is not a one-fixture theorem.

The archived 2026-10-21 printout reports standard axioms
`propext`, `Classical.choice`, `Quot.sound` for both the named theorem and
`validRawDecomposition_iff_curve_span_sum`. Its Lean 4.35.0-rc1 build is
historical evidence; the current pin is Lean 4.35.0 and Mathlib commit
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.

Fresh GitHub API readback confirms hosted run `42423957020` completed
successfully and its actual formal-workspace job executed the build, target
sweep, and before/after dependency checks. The downloaded artifact
`13595234243`, 1,908,276 bytes, has SHA-256
`fbe58eb9ab507da11078d7c91912e5ef162b95275df2c1d92c9ba3b9edef40e0`, exactly
matching GitHub's recorded digest. Its three relevant files equal the local
receipt and dependency-pin files byte for byte. See `raw/artifact-readback.json`
and the archived GitHub metadata.

The Semaev receipt names actual checkout
`8f63ad373ea30b7a74230e4a589d1a8807291c5f`. It reports:

- Lean 4.35.0 and the exact target/spec/source/toolchain/manifest hashes;
- the explicit `CryptoResearch.Semaev.Certificate` target build, 2,059 jobs,
  after the project build;
- a project audit of 1,313 theorems and a successful exact-name audit;
- the exact named theorem type and only the three standard axioms;
- `machine_verified`, no forbidden constructs, and semantic review pending.

All 106 recorded workspace inputs and ten recorded verifier inputs match
both the hosted checkout and the review source commit. The generated root was
reconstructed from pinned source inventory. Together with the six review
bindings, this gives 122 matching rows in `input-audit.json`. The equal
dependency receipts report ten clean installed source revisions. Their own
stated limit is source custody: dependency binaries were not independently
rechecked. This reviewer also performed no independent binary/kernel recheck.

## False-success controls and scope

`receipt_controls.py` freshly exercised the pinned receipt validator using the
archived verifier revision explicitly. Its baseline has no errors. All 13
negative controls reject: wrong result theorem, wrong named audit marker,
stale declared-source hash, stale theorem hash, unapproved-axiom diagnostic,
recorded forbidden construct, empty build log, empty audit log, zero theorem
project audit, absent workspace input map, absent verifier input map, wrong
Lean version, and wrong archived source revision. Results are in
`receipt-controls-with-git-context.json`; these are Python consistency tests.

The labeled synthetic control preserves consistent identity/hash fields and
supplies invented nonempty build/audit logs. The validator accepts it. This is
the documented boundary: successful receipt validation does not authenticate
execution. The synthetic object was kept in memory; no fabricated theorem
receipt is presented as real execution evidence.

The reviewed `target_audit_source` requires `.thmInfo`, calls
`Lean.collectAxioms`, rejects axioms outside the standard list, and performs
`#check` plus `#print axioms` on the exact name. `LeanWorker` explicitly builds
the requested module, even when a generated root could omit it. The current
source has no forbidden constructs under its text scanner. The module's raw
predicate requires each explicit curve equation before accepting the sum;
the invalid-coordinate-to-zero fallback in `pointOfRaw` does not erase that
conjunct. Rejection of the concrete F5 raw-coordinate controls was inspected
at source level here; fresh Lean execution of those cases remains required.

The existing real-Lean test source includes absent name, definition-as-theorem,
false theorem, and a hidden `sorryAx` dependency with an empty project audit,
plus stale-source and receipt tampering controls. A live current-head hosted
kernel-controls job (`128624995013`, run `42446001280`) reports **452 passed in
31.33 seconds**. It used the separate smoke pin Lean **4.22.0**. This is
authenticated hosted instrument evidence, not a Semaev proof on Lean 4.35.0.

That run's green formal-workspace job (`128624995033`, PR #3173 head
`5e0b064e262ac89037cd4f8b8e79f716f9930e40`) is a **scope no-op**: its scope-excluded
step succeeded, while checkout, toolchain, build, target verification and pins
were skipped. Its green label cannot discharge the fresh Semaev requirement.
The exact job metadata and logs are retained under `raw/current-head-*`.

One binding limitation remains: the ten-entry `verifier_inputs` map enumerates
`orchestration/formal/*.py`; its target parser imports
`orchestration/fast_yaml.py`, which is outside that map. This helper was read
at the archived revision and separately hashed in `parser-helper-binding.json`.
Thus the ten-entry map must not be described as the complete transitive verifier
software closure. The hosted dependency checker is separately source-bound by
its own receipt. No demonstrated false acceptance of the named theorem follows
from this omission, but a complete software-input claim needs the helper and
external parser dependency addressed.

## Remaining fresh check and execution feasibility

The required next evidence is a fresh, authenticated Lean 4.35.0 execution
on immutable pinned inputs: explicit Semaev module build, exact declaration
and transitive axiom audit, supplemental raw-lemma type/axioms, and the known
false raw-coordinate cases. Confirm actual executed steps and source/input
hashes in forced run `42446577502` on coordinator-reported revision
`e5569428e5e53145f123f3aeb36de00591ad72b6`; submission alone is pending evidence.
Keep failed attempts and compare installed dependency source pins. The normal
Lean/Lake binary trust boundary remains unless an independent rechecker is run.

The local snapshot showed 118,070,554,624 MemAvailable bytes and approximately
21 GiB disk available. The required 16 GiB host reserve is compatible with a
bounded job in that snapshot, but no exclusive execution ownership was granted,
no dependency-cache readiness was established, and no local build was started.
The parent explicitly owns the next execution. Do not duplicate it.

Reproduction of the lightweight controls uses Python 3.11, PyYAML 6.0.3 and
the recorded Git objects:

```sh
PYTHONPATH=reviews/TASK-20261108-5ef48a/python-deps \
  python3.11 reviews/TASK-20261108-5ef48a/receipt_controls.py
```

The script preserves result paths with exclusive creation; use a new review
copy for replay. The initial host-Python-3.9 failure, absent parser helper,
missing PyYAML, wrong nested Git path context, and GitHub escape-sequence log
refusal are retained in `raw/` and the initial `receipt-controls.json`.
The nested Git-context failure was a replay setup issue; the later run uses
the same archived validator with an explicit snapshot worktree context.

## Review integrity

Primary sources were the pinned theorem/target/claim, archived statement and
axiom logs, the exact verifier and control sources, workflow, live GitHub job
metadata/logs/artifact, and pin receipts. The exhaustive programmatic read list
is in `input-audit.json`, incorporated into the attestation. Historical memory
was used only for orientation and the rule to keep certificate scope precise;
all reported source and hosted facts above were checked in this session.

Conductor task `T-1937` remains claimed in the captured readback. This report
does not mark work merged, change scientific status, modify producer source,
or compose a verdict for J1/J2. Fresh execution and final composition are
coordinator obligations. The associated attestation reports J3 inconclusive
and gives the completed subchecks separately.
