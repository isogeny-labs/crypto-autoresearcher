# Exact Lean evidence for the corrected five-target corpus

This packet keeps the failed producer snapshots visible.  The final success
does not retroactively turn either failed run into a proof receipt.

## Final successful snapshot

- Proof snapshot: `db090984ca1e78e92cea5e0840885ae982f12921`
- Pinned toolchain: `leanprover/lean4:v4.35.0`
- Hosted run:
  [`41512636120`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120)
- Formal job:
  [`125508254976`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120/job/125508254976)
- Formal-job interval: 2026-11-02 19:44:15Z--20:14:20Z
- Run and formal-job conclusion: `success`
- Kernel-controls job:
  [`125508254994`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120/job/125508254994),
  `success`

Every substantive formal step succeeded: dependency-pin verification before
the proof checks, workspace generation, `lake build`, the all-discharged-target
verifier, dependency-pin verification after the checks, and receipt upload.
The workspace build completed 9,135 jobs.
The verifier reported `113 verified, 0 not verified, 0 infrastructure, 0
undischarged`; the five rows introduced by this tranche were:

| Target | Audited declaration | Result |
| --- | --- | --- |
| `attack-one-shot-history` | `CryptoResearch.AttackCorpus.OneShotHistory.correlated_history_and_hazard_repair` | verified |
| `attack-cubic-eval-rank` | `CryptoResearch.AttackCorpus.CubicEvalRank.collinear_kernel_and_injective_repair` | verified |
| `attack-cofactor-pushforward` | `CryptoResearch.AttackCorpus.CofactorPushforward.cofactor_failure_and_product_fiber_repair` | verified |
| `attack-fs-zero-hash` | `CryptoResearch.AttackCorpus.FiatShamirZeroHash.zero_hash_acceptance_and_nonzero_control` | verified |
| `attack-pedersen-relation-kernel` | `CryptoResearch.AttackCorpus.PedersenRelationKernel.known_relation_kernel_and_alternate_openings` | verified |

The target verifier checked the named declaration recorded in each manifest,
the manifest/source binding, the forbidden-proof-construct boundary, project
axioms, and the declaration's printed axioms.  The separate kernel-control job
also passed its positive and negative harness controls (`414 passed` under its
control toolchain).  These are
machine-checking claims about the exact theorem types, not independent
semantic review.

### Frozen final source bytes

| Source | SHA-256 |
| --- | --- |
| `OneShotHistory.lean` | `5420db0c7a6f1e6db1cc7d3e167f6811cc2f3d20f0b23f202101d9aeaa923cc6` |
| `CubicEvalRank.lean` | `ed62caa522eb7820784ed2674cb1d088a7581a6205f26b8e160292ef2dc56464` |
| `CofactorPushforward.lean` | `53445da9ae485ed4cd5d76088b6932d842dfc61299cf98d986a5cc34125a9d5c` |
| `FiatShamirZeroHash.lean` | `b958dfb175dd7c0a7bcd59be48b5e3b9298a7729ff337cf3d96b76e48022bc4d` |
| `PedersenRelationKernel.lean` | `7b1cd73987824b69c5024b37ae9367e86b76346795375bf61f814e4031678b13` |

### Retained artifacts

| Artifact | ID | Size | Uploaded | Expires |
| --- | ---: | ---: | --- | --- |
| `formal-verification-receipts` | `13175228889` | 1,523,974 bytes | 2026-11-02 20:13:06Z | 2027-01-31 19:43:55Z |
| `lean-controls` | `13172929781` | 4,939 bytes | 2026-11-02 19:45:16Z | 2027-01-31 19:43:55Z |

The upload log records SHA-256
`4df8ae98f7487ba386bb4bcebd6ab0ade17cefeaabe2b4212919513f29a740c3`
for the formal-receipt ZIP.  The dependency receipt records clean installed
sources at the pinned revisions and explicitly limits that evidence to Git
source custody: ignored build outputs retain Lean/Lake binary trust.

A fresh local `gh run download` attempt followed the Actions redirect but the
Azure blob endpoint returned `Forbidden`.  The ZIP contents were therefore
not independently downloaded in this environment; the immutable run/job
logs, artifact metadata, upload digest, and per-target receipt messages are
the evidence cited here.  This is an artifact-access limitation, not a failed
hosted proof check.

## Failed snapshots preserved

The initial evidence, including all six independent reviews, is recorded in
[`initial-snapshot-evidence.md`](initial-snapshot-evidence.md).

| Run | Snapshot | Exact result |
| --- | --- | --- |
| [`41503944712`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41503944712) | `674b3248a8b007748a2cf4f10e5063e7de123be4` | `lake build` failed: Cubic built; OneShot, Cofactor, Fiat--Shamir, and Pedersen failed.  The target verifier did not run. |
| [`41509145327`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41509145327) | `49f57f88cc5be06b7e1fe42a9571aee3337fa510` | OneShot, Cubic, Cofactor, and Fiat--Shamir built; one closed `ZMod 5` arithmetic goal remained in Pedersen.  The workspace gate therefore failed and produced no five-target receipt. |
| [`41512636120`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120) | `db090984ca1e78e92cea5e0840885ae982f12921` | Full build, all-target verification, named declaration/axiom audits, dependency checks, controls, and artifact upload succeeded. |

The last Pedersen correction is ordinary kernel `decide` after normalization,
not `native_decide`.  The final correction plan has SHA-256
`f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf`.
It freezes the exact source hashes tested by the successful run and was
committed before the four fresh correction reviewers were dispatched.

## Final correction reviews

All four mutually blind v2 correction reviewers returned `holds` for their
assigned joint, `passed` for machine status, and `faithful_scoped` for
fidelity.  They found no public-type or target-spec weakening.  Each recorded
the same bounded artifact-access limitation described above where applicable;
none promoted the finite theorem into an unmodeled cryptographic claim.

```text
PASS: 4 report(s), every joint owned and attested, blindness respected, controls declared
```

The checker command was:

```sh
python3 tools/check_review_independence.py \
  --plan docs/reports/2026-11-02-attack-corpus-next-five-lean/correction-review-plan-v2.yaml \
  --expected-plan-sha256 f55ab631c4d216ffcd33edd2e08cdef9962fcb220905d0acf0c3f261aa7187bf \
  --reports docs/reports/2026-11-02-attack-corpus-next-five-lean/correction-reviewers-v2
```

The unchanged Cubic module is covered by the original specialist review, the
sealed blind rederivation, its byte-identical source hash across the correction
round, and the final exact machine gate.

## Trust and scope limits

The result relies on the Lean kernel, the pinned Lean/Mathlib dependency
stack, the repository verifier and CI runner, and the fidelity of the formal
types to the prose claims.  It does not provide a second independently
implemented kernel.  It proves neither a practical attack nor an end-to-end
security reduction.  Concrete curve encodings, adversaries, random oracles,
runtimes, sampling distributions, and the unresolved JKSST lift/height/rank
bridges remain outside these declarations.
