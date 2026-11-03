# J3 named machine receipt and proof boundary

Reviewer task: `TASK-20261103-a1d703`. Conductor scope: `T-1532`.
Frozen review plan: `b806841cef6ad73e80c5d49ca9a51845e5cf2eb6`.
Joint verdict: **holds**, for the archived named receipt, exact input binding,
and stated proof boundary. This verdict does not assert a new independent Lean
kernel execution. Sibling reports were not read.

The independently downloaded odd-torsion receipt matches the precommitted
SHA-256 exactly:
`63419f85fb756ca00a9772fb5c7454a605aed73f53b1fad2b355de3c7ba15403`.
Its theorem is
`ScopedObstructions.AdditiveModel.odd_translation_outside_kernel`.
The complete six-file workspace map and ten-file verifier map match the Git
tree at its recorded source revision, the frozen source revision, and the
review-plan revision. The source note, target YAML, and theorem hashes also
match at all three revisions. These are positive, checked component results.

## Evidence dimensions

| Dimension | Finding | Evidence and scope |
| --- | --- | --- |
| Receipt consistency | passed | Exact bound receipt SHA, target identity, version, successful flags, named and nonempty audit evidence, full workspace/verifier maps; archived checker baseline returns no errors. |
| Hosted execution provenance | passed, archived run | GitHub run `41494797344`, attempt 1, completed successfully; formal job `125447031153` records named verification and artifact upload; separate kernel-controls job succeeded. |
| Named theorem build and audit | passed in archived hosted execution | Receipt builds `ScopedObstructions.Torsion`; archived worker explicitly invokes `lake build +ScopedObstructions.Torsion`; exact declaration is required to be theorem information and is printed and audited. |
| Independent kernel recheck by J3 | not_verified | No Lean build, local kernel execution, or `lean4checker --fresh` was performed. This is an explicit scope constraint and outstanding obligation for any claim requiring fresh independent execution. |
| Current-head hosted formal result | pending at observation | Run `41718285530`, head `53b7f9813c8037818d5db8b42df9eee5cd1e0f12`, formal workspace job still running; kernel-controls succeeded. No duplicate build was launched. |
| Semantic fidelity | assigned to J2 | J3 checked the printed declaration identity and proof boundary, and supplies no independent J2 verdict. |

## Source identity and hosted checkout

The receipt records source revision
`d0b766449942b04bf3316d005624b3ce83f0c5f4`. The frozen review inputs name
`004355570fa983535696439b1781cb762dae3607`. Both have the same relevant
workspace and verifier bytes. The plan revision also has those same bytes.
The receipt therefore remains consistent for the reviewed inputs despite the
different repository revision names.

GitHub's run API reports `head_sha`
`deb2473f2f87cfda16dc07efa584c20971879408`, an event of
`pull_request_target`, and the originating branch
`codex/attack-corpus-five-lean-20261101`. The formal job's checkout log explicitly
fetches and prints `d0b766449942b04bf3316d005624b3ce83f0c5f4` as checked-out
`origin/main`. The recorded receipt source matches that actual checkout.
The API head SHA must not be substituted for the execution checkout SHA.
The complete run log and API response are retained under `raw/`.

The artifact API reports artifact `13167622662`, name
`formal-verification-receipts`, size 1,378,456 bytes, creation time
2026-11-02T18:18:08Z, and archive digest
`sha256:55ab1f6a151156f4456e2b8ee3361962b55ca9a981d8b540cd9c2b71c5301672`.
The archive digest is API metadata; J3 independently checked the extracted
bound receipt's digest, not the compressed archive digest.

## Pins, coverage, and axiom audit

The workspace is `formal/scoped-obstructions`. Its full map contains
`AxiomAudit.lean`, `ScopedObstructions.lean`,
`ScopedObstructions/Torsion.lean`, `lake-manifest.json`, `lakefile.toml`, and
`lean-toolchain`. The root imports `ScopedObstructions.Torsion`; no project
theorem source is silently omitted by the default target here. The worker also
builds the requested source module explicitly. The ten Python files in
`orchestration/formal/` are all present in the verifier map, with exact matching
hashes. That map binds the core verifier modules; the workflow and wrapper
scripts remain separately inspected source, not additional receipt map entries.

The toolchain pin is `leanprover/lean4:v4.22.0`. The receipt identifies Lean
4.22.0, release commit `ba2cbbf09d4978f416e0ebd1fceeebc2c4138c05`.
The scoped Lake manifest contains an empty `packages` list, so this theorem
does not import Mathlib or CryptoLean dependencies. The broader formal CI job
also emitted before/after dependency-source pin checks; those broader checks
are separate from the scoped dependency-free theorem. They explicitly retain
Lean/Lake binary trust and report no independent binary/kernel recheck.

The project audit checks four declarations: `odd_translation`,
`odd_translation_outside_kernel`, `even_scalar_control`, and `positive_control`.
It demands an empty transitive axiom list for every one. The harness separately
checks that the exact requested declaration is a theorem, collects its
transitive axioms, prints its type, and runs `#print axioms`. Although the
generic harness allows the three standard axioms, this project audit rejects
all axioms, and the named receipt explicitly says this theorem depends on none.
The receipt records no forbidden constructs and no infrastructure failure.

The printed type quantifies over an `AdditiveModel`, natural `r`, and `P,T`,
with explicit odd witness, annihilation of P, two-torsion of T, and nonzero T;
its conclusion is the nonzero translated scalar multiple. The stronger
equality is the separately project-audited `odd_translation` theorem. The
source supplies explicit XOR positive and even-scalar controls. This evidence
does not instantiate a concrete curve representation, point arithmetic,
rational two-torsion certificate, or factor-base membership checker.

## Controls and trust boundary

J3 executed the archived `receipt_errors` function against an isolated input
snapshot extracted from the exact Git revision. The baseline returned `[]`.
Eleven hostile receipt modifications were each rejected: wrong result theorem,
false build flag, false audit flag, forbidden construct, empty audit, empty
build, stale theorem hash, missing workspace input, missing verifier input,
wrong Lean version, and contradictory audit error. The exact error lists are
in `raw/checks.json`, and `check_j3.py` reproduces them without running Lean.
These tests establish checker behavior; they are not mathematical countermodels.

J3 separately downloaded the hosted `lean-controls` artifact. Its JUnit record
has 399 tests, zero errors, zero failures, and zero skips. The real-Lean tests
include a valid proof, a false proposition, a missing theorem, a definition
used as a theorem, a hidden `sorryAx`, sharing a project audit while checking
each requested theorem, and changed/created/deleted imported helper inputs.
The archived source for those tests was inspected to identify what they check.
The project's mathematical positive/even controls are also explicitly included
in its zero-axiom audit. The J1 mathematical countermodel review remains
independent of these harness controls.

A consistent fabricated JSON could carry matching-looking hashes and logs.
Receipt consistency therefore authenticates no execution by itself. The
separately retrieved GitHub run, checkout log, named verification log line,
uploaded artifact identity, and completed job metadata supply archived hosted
execution provenance under GitHub/runner trust. None is an independent
rechecking kernel. The `review-evidence` Lean workflow requires fresh Lean
checks for full review validation; J3's archived receipt audit does not fulfill
that stronger requirement. An eventual passing current-head hosted job can
supply fresh hosted execution at its stated checkout, with the same distinction
between hosted execution and an independent rechecking kernel.

## Reproduction and scope

Primary sources used were the frozen plan and bindings, target and source note,
the exact scoped workspace, core verifier code, Lean live-control test source,
and GitHub run/artifact metadata and logs. This is an artifact review with no
new mathematical novelty or performance claim, so it requires no invented
experimental comparison or literature result.

Run `python3 check_j3.py /var/tmp/autoresearcher-odd-torsion-review-20261103` to
repeat the byte/map/checker checks. `raw/checks.json` records all observations;
`raw/archived-input-snapshot` retains the reviewed scoped source and verifier
bytes. `REPRODUCE.sh` records independent download/read commands. No producer
repository edits, cloud submissions, proof builds, push, or merge were made.
The coordinator owns the combined review, diagram, PDF, and independence gate.
