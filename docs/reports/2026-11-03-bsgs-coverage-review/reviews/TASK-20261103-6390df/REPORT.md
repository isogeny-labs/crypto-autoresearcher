# J2: named Lean coverage theorem and pinned machine evidence

**Verdict: holds for J2.** The exact named theorem matches the frozen formal target's arithmetic claim. The pinned GitHub receipt reports a successful build and named axiom audit, and the downloaded receipt matches the custody copy byte for byte. The toy-curve and Python execution bridges are separate obligations; this theorem has no curve, group, program, or operation-count terms.

## Claim and machine status

| Dimension | Finding |
| --- | --- |
| Machine status | **passed on the pinned hosted run** `41698891260`, head `70cdc0c5a12b49b7a0ef1bb3590c6e8d99a4d311`; named artifact `13264657224`. A fresh local core Lean compatibility check passed under 4.35.0-rc1. The exact 4.35.0 / Mathlib build was not repeated locally. |
| Fidelity | **faithful_scoped** to `formal/targets/runbook-example-bsgs-coverage.yaml` and the counting sentence in the README. |
| J2 outcome | **holds** for the exact type, source and verifier binding, declared dependency pins, named axiom audit, and boundary controls. |

The declaration is exactly:

```lean
CryptoResearch.Runbook.BsgsCoverage.coverage
  (m k : Nat) (hm : 0 < m) (hk : k < m * m) :
  k / m < m ∧ k % m < m ∧ k = k / m * m + k % m
```

The quantifiers range over all natural `m,k` satisfying both premises. The proof uses core `Nat` division and remainder lemmas. There is no hidden curve or algorithm premise in the elaborated type. The source has no `sorry`, custom `axiom`, `unsafe`, or native evaluation. Both the hosted named audit and my local `#print axioms` list `propext`, `Classical.choice`, and `Quot.sound` only.

## Binding checks

- The committed review input revision is `7c028ce9ccdec6c1ee7d4c2b3b60120ed3dcbd9e`. All 11 `input-bindings.json` tracked-input SHA-256 values match that Git tree, including source `867ce0f37099a30b34ce7d603549eb8b28f16b1c17183119657715108f79d9d0`, target `1dbdf3d94890283a35f6c494fbd7a2c7e06a8cbe18f29f7a09b274ffb41e083a`, toolchain `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c`, and manifest `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`.
- The same four hashes match the receipt's source commit `d3ce7758698c822e16feef174ecdac53c41e4568` and GitHub head `70cdc0c5a12b49b7a0ef1bb3590c6e8d99a4d311`. The source commit is a merge with the review input commit and GitHub head as parents.
- I fetched GitHub Actions artifact `13264657224` directly with `gh run download`. Its named receipt SHA-256 is `32224d224d2ab71c7e383907ba22e1e324a6794d54354442f75451b100754cca`, identical to the custody copy and binding. GitHub reports run success and successful proof-workspace build, target-check, and dependency-pin steps. The receipt reports Lean 4.35.0, exact named theorem, a 1,105-theorem standard-axiom audit, and a named target audit.
- Every one of the receipt's 10 `verifier_inputs` hashes matches the source-commit Git tree. Of 89 `workspace_inputs`, 88 are directly tracked matches. `CryptoResearch.lean` is generated and ignored by design; reconstructing it from the 71 tracked module names with the pinned `orchestration/formal/workspace.py` renderer gives its recorded hash `018f541980d339185edcf361f589a95ba21e925743518fa77dda019acb985327`. `raw-checks.json` retains the counts and hashes.
- The pre/post dependency-pin files are identical. All 10 declared package revisions agree with the frozen Lake manifest, the recorded installed revisions equal them, and `clean_sources` is true. The dependency checker hash `0bcb377242cede9cdbf393e966022adb6303ac8c2b9b64a93a3c37d123f301b7` matches the source-commit file. These are source/pin checks; there is no independent binary or kernel recheck, and pre/post hashes alone cannot exclude a transient concurrent edit.

The directly downloaded receipt plus GitHub run metadata are stronger custody evidence than an isolated JSON file, but they still do not independently authenticate what executed on the hosted runner. The local 4.35.0-rc1 check confirms the exact theorem and controls at a nearby compiler revision; it is not the frozen-pin Mathlib build.

## Boundary controls and semantic limit

`core-audit.lean` consists of the exact source bytes followed by `#check`, `#print axioms`, and two checked negations. Under local Lean 4.35.0-rc1 it exited 0. At `m=0,k=0`, the would-be digit bound is `0 < 0`, false. At `m=2,k=4=m*m`, the quotient bound is `2 < 2`, false. Both premises in the actual theorem are therefore material; the test rejects their removal at these concrete points. This was source-guided control work, not the J3 blind derivation.

The README's curve-wide consequence additionally needs the curve's point count and group structure, a nonidentity generator of prime order, `n ≤ m*m`, and the solver's actual loop semantics. The theorem proves the arithmetic decomposition only. It does not refine `solve.py` or `check.py`, certify an executed group-operation count, or authenticate a reported runtime. Those bridges belong to the other joints of the review.

## Evidence and remaining work

- `hosted_artifact/runbook-example-bsgs-coverage.json` and the two `dependency-pins-*.json` are the direct GitHub download. Other unrelated receipts in the artifact were discarded without inspection.
- `core-audit.lean` / `core-audit.log` are the local core Lean control and output; `raw-checks.json` is the independent hash comparison. `review_attestation.yaml` records the read inventory and mutual blindness.
- The review coordinator should combine J2 with J1's concrete curve/code checks and J3's blind derivation before deciding whether the full runbook validity sentence is supported.
