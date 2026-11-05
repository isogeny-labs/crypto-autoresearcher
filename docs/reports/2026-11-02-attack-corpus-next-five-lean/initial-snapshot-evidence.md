# Initial producer snapshot: exact failure and independent review seal

This file preserves the result for the immutable producer snapshot before any
repair.  It is intentionally not a success receipt.

## Bound identities

- Producer commit: `674b3248a8b007748a2cf4f10e5063e7de123be4`
- Review-plan commit: `fbb6c5d6f8bbae160e51404172996c837efb0a07`
- Review-plan SHA-256:
  `7a55598bad9dddb2f6b462fa981d6f4afb7e17871c417174692f1c3201f1f77f`
- Pinned toolchain: `leanprover/lean4:v4.35.0`
- Hosted run:
  [`41503944712`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41503944712)
- Formal job:
  [`125478457720`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41503944712/job/125478457720)
- Run conclusion: `failure`
- Formal job interval: 2026-11-02 18:48:17Z--19:10:17Z

The dependency pins were checked before the proof build.  `lake build` then
failed, so the target verifier, named-declaration axiom audit, and post-proof
dependency check were skipped.  The successful `kernel-controls` job is a
harness control; it does not discharge these five targets.

## Exact module outcome

| Module | Result on producer snapshot | First decisive diagnostic |
| --- | --- | --- |
| `OneShotHistory.lean` | failed | line 117: unknown `Finset.sum_le_sum` under the selected imports |
| `CubicEvalRank.lean` | built | the build log records `Built CryptoResearch.AttackCorpus.CubicEvalRank` |
| `CofactorPushforward.lean` | failed | line 86: equality orientation mismatch, followed by concrete-control proof failures |
| `FiatShamirZeroHash.lean` | failed | line 32: invalid lambda token `⇒`; subsequent `ZMod 5` field-instance failures |
| `PedersenRelationKernel.lean` | failed | line 123: untyped pairs led elaboration to require `Field ℕ` |

GitHub retained two artifacts from the failed run:

| Artifact | ID | Size | Expires |
| --- | ---: | ---: | --- |
| `formal-verification-receipts` | `13172220589` | 956 bytes | 2027-01-31 |
| `lean-controls` | `13170371785` | 4,889 bytes | 2027-01-31 |

The artifact download redirected to the Actions Azure blob endpoint and
returned `Forbidden` in this environment.  This packet therefore cites the
immutable run, job, step, and artifact metadata and does not claim a local hash
of either ZIP.

## Independent review outcome

Reviewers were assigned before the run result, worked without sibling reports,
and did not edit producer sources.  The blind reviewer received only the four
allowlisted inputs in the clean temporary tree identified in its attestation.

| Joint | Independent result on the submitted artifact |
| --- | --- |
| A: one-shot/history | `breaks` as a formal target; scoped mathematics holds |
| B: cubic evaluation rank | source-level `holds`; coordinator-reported module build only |
| C: cofactor pushforward | source-level `holds`; machine status remained pending in that sealed review |
| D: constant-hash Fiat--Shamir algebra | `breaks` as a formal target; scoped mathematics holds |
| E: Pedersen relation kernel | `breaks` as a formal target; scoped mathematics holds |
| F: blind rederivation of all five | `holds` for independent hand derivations only |

The machine failure does not reverse the mathematical derivations; it means the
submitted Lean bytes did not prove them.  Conversely, the hand derivations do
not substitute for a successful exact build and axiom audit.

After reviewer-owned schema normalization, the prospective-plan check passed:

```text
PASS: 6 report(s), every joint owned and attested, blindness respected, controls declared
```

Command:

```sh
python3 tools/check_review_independence.py \
  --plan docs/reports/2026-11-02-attack-corpus-next-five-lean/review-plan.yaml \
  --expected-plan-sha256 7a55598bad9dddb2f6b462fa981d6f4afb7e17871c417174692f1c3201f1f77f \
  --reports docs/reports/2026-11-02-attack-corpus-next-five-lean/reviewers
```

## Repair protocol

The reviews above stay bound to the failed producer bytes.  Corrections must be
made in a new commit, checked by a fresh exact run, and covered by a separate
correction review plan.  A later success must not rewrite or erase this failed
snapshot.
