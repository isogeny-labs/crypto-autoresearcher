# J3 final additive review: hosted machine evidence and false-success controls

**Task:** TASK-20261109-115f30. **Joint:** J3 hosted machine evidence and false-success controls. **Verdict:** **holds** for the named machine-evidence joint, as of 2026-11-09 18:13 UTC. This adds to, and does not alter, the sealed provisional packet and chronology correction. It gives no independent semantic-fidelity verdict on the source interpretation.

## Authenticated run and artifact

[GitHub Actions run 42665763089](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42665763089) completed `success` on the `lean-verification` workflow; all three jobs, including `formal workspace (lake build + axiom audit)`, completed `success`. The run API identifies PR head `d25ed16abcaaa942857e5e3a6d72637aaf8aa5c5`. GitHub published `formal-verification-receipts` artifact ID `13699385811`, size **1,913,131 bytes**, digest `sha256:e081ab350fecd5394080b89f8d09a570a2a7c031e344d3b94a08195eb08faf81`, and associates it with that head. I downloaded that artifact through GitHub's artifact API; the downloaded ZIP's SHA-256 independently equals the published digest. The exact ZIP is retained at `artifact/formal-verification-receipts.zip` and its named records are retained under `artifact/extracted/`.

The receipt records checkout/source commit `3abcd77ef51d63a79fcf02fcfd172d7d283babc3`, which is the synthetic PR merge commit, with PR head `d25ed16abcaaa942857e5e3a6d72637aaf8aa5c5` as second parent. The merge tree and head have no differences in the reviewed source, target, theorem, toolchain, manifest, or formal verifier paths. I verified the receipt against the exact merge tree, not against a later worktree state.

## Named Semaev target and input closure

`semaev-frobenius-collapse.json` identifies task `TASK-20260916-a17f66`, claim `THM-SEMAEV-FALL1-LEMMA-1`, theorem file `CryptoResearch/Semaev/FrobeniusCollapse.lean`, and the exact declaration `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations`. It records `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, no forbidden constructs, and no blocking reason. Its build log includes the named module; its audit log contains `axiom audit: 1313 theorem(s), all standard axioms only`, the exact named-target pass line, the elaborated declaration type, and only `propext`, `Classical.choice`, and `Quot.sound` as transitive axioms. The receipt leaves semantic review `pending`, correctly separating machine status from source fidelity.

The following receipt hashes match the committed review plan and independently hashed bytes from the exact Git merge tree:

| Bound input | SHA-256 |
| --- | --- |
| Research source | `11b61f4f4bdaed0c323ec852f19fc4c0a7ff3972715bfe637604fb675db7fee4` |
| Target spec | `e2b083a617fadec962d855e8dde425fef1fe010a15ea1652098ae4e57096ce7c` |
| Lean theorem file | `f408877908fc156006c2b24cb38b26610461e03093ff88aadbf11d4bc2c2e398` |
| Lean toolchain file | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| Lake manifest | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |

The receipt records Lean 4.35.0. Its `workspace_inputs` map has **106** entries: **105** match tracked merge-tree files, and the sole generated `CryptoResearch.lean` matches a fresh deterministic rendering from all **88** tracked `CryptoResearch` modules in that tree. All **10** `verifier_inputs` hashes match the exact archived verifier at `3abcd77...`. Running that revision's `receipt_errors` on the actual receipt and exact input tree returned `[]`, including its named audit, identity, source and verifier closure checks.

Both `dependency-pins-before.json` and `dependency-pins-after.json` state `passed: true`, bind GitHub run ID `42665763089` and checkout SHA `3abcd77...`, and have the same manifest and checker hashes as the merge tree. Their 10 dependencies each have an installed revision equal to the manifest revision and `clean_sources: true`; the two records are byte-identical. Their SHA-256 is `50cd7ab054705afeb75ccb62ccce62feb2c9fc69d6d2e6eba36c1abeae94214f`. This checks installed Git source custody, not dependency binary integrity or an independent Lean kernel implementation.

## False-success controls and scope

I re-exercised the receipt consistency checker against the actual hosted receipt on the exact merge-tree input snapshot:

| Control | Result |
| --- | --- |
| Unchanged hosted receipt | `[]` errors |
| Wrong `verification.theorem_name` | `result identity` |
| Changed theorem SHA-256 | `theorem hash` |
| Removed exact named-target audit line | `named audit log` |
| Replaced build and audit logs with self-consistent fabricated success strings | `[]` errors |

The last control shows that JSON consistency does **not** authenticate execution. The separate GitHub run/job completion, artifact ID and published ZIP digest, matching downloaded archive, and matching run-bound dependency pin records provide the execution provenance for this J3 verdict. The usual trust boundary remains GitHub Actions, Lean/Lake, and cached dependency binaries. No local Lean build or new cloud job was run. No sibling reports or attestations were read.

**J3 outcome:** the hosted machine evidence for this exact named declaration **holds** on the pinned inputs. Source interpretation, the free-degree-fall corollary, and any solver/complexity inference remain for their assigned independent joints and later composition.
