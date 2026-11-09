# J3 hosted machine evidence and false-success controls — provisional

**Task:** TASK-20261109-115f30. **Joint:** J3 hosted machine evidence and false-success controls. **Verdict:** inconclusive as of 2026-11-09 17:58:08 UTC. This report makes no machine-passed claim for the named Semaev declaration.

## Immutable inputs and hosted identity

The prospective review plan is committed at `36ee18fa3d0e6d527e1b36e3e2a09180c5fcf055`. I independently hashed the exact Git-tree bytes of its source, target, theorem, toolchain and manifest. They match the plan:

| Input | SHA-256 |
| --- | --- |
| `research/THM_SEMAEV_FALL1.md` | `11b61f4f4bdaed0c323ec852f19fc4c0a7ff3972715bfe637604fb675db7fee4` |
| `formal/targets/semaev-frobenius-collapse.yaml` | `e2b083a617fadec962d855e8dde425fef1fe010a15ea1652098ae4e57096ce7c` |
| `formal/CryptoResearch/Semaev/FrobeniusCollapse.lean` | `f408877908fc156006c2b24cb38b26610461e03093ff88aadbf11d4bc2c2e398` |
| `formal/lean-toolchain` | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lake-manifest.json` | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |

The fresh run is [GitHub Actions run 42665763089](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42665763089), event `pull_request`, head `d25ed16abcaaa942857e5e3a6d72637aaf8aa5c5`, workflow `lean-verification`, run number 3812. A Git diff from the plan commit to that head has no changes in the five pinned inputs. The plan names `CryptoResearch.Semaev.pow_q_eq_frobeniusTwist_mod_fieldEquations`; the target spec names the same declaration and source file.

At 17:58:08 UTC GitHub's run/job APIs reported the formal-workspace job `in_progress`, with `Machine-check every discharged formal target` still running. `Verify actual installed dependency source pins before proof checks` and `Build the workspace` had completed successfully. The post-proof dependency check and artifact upload were pending. Artifact API listed only `lean-controls` (artifact ID `13696462093`, GitHub digest `sha256:361dd147c794c80a877182ebd05a05973e86f6872c46f227250b7bd969ef7046`, size 5190 bytes), which is the separate smoke/control job. There was no `formal-verification-receipts` artifact from the fresh run. Its actual archive digest, named-target receipt, axiom audit, source/verifier input maps and installed dependency pin receipts therefore remain unexamined. A successful workspace build alone does not establish the named declaration audit.

The exact-head workflow is configured to materialize target source documents, generate the root module, fetch pinned Lean/Mathlib dependencies, run `tools/check_lean_dependency_pins.py` before and after proof checks, run `lake build`, then `tools/verify_formal_targets.py --artifact-dir formal-receipts --min-verified 66`, and upload `formal-receipts`. The pin checker compares every manifest Git revision with the installed checkout and rejects dirty/untracked dependency sources; it explicitly does not recheck dependency binaries or the Lean kernel. These are code-path observations, not substitutes for the pending hosted receipts.

## False-success controls

I exercised `orchestration.formal.receipts.receipt_errors` with the exact target and local input hashes in the isolated review checkout. A self-consistent **fabricated** JSON with fabricated nonempty build/audit log strings yielded no consistency errors. This demonstrates that the function authenticates neither a Lean execution nor the origin of logs. Mutating that same object produced:

| Mutation | Consistency errors |
| --- | --- |
| Wrong `verification.theorem_name` | `result identity` |
| Changed `provenance.theorem_sha256` | `theorem hash` |
| Removed exact named audit line | `named audit log` |

These controls validate the consistency interface only. They are not Lean runs or mathematical counterexamples. The fresh GitHub-hosted run and its artifact binding are needed to authenticate that the named audit actually executed. No local heavy Lean build or cloud job was launched.

## Continuation required

On completion of **the same run 42665763089**, fetch its authoritative conclusion and `formal-verification-receipts` artifact metadata, download the actual archive, hash its bytes against GitHub's published digest, and inspect `semaev-frobenius-collapse.json` plus `dependency-pins-before.json` and `dependency-pins-after.json`. Check the receipt's task/result identities, exact named audit line, nonempty project audit, no negative diagnostics or forbidden constructs, build status and logs, `workspace_inputs`/`verifier_inputs` closure, five pinned hashes, exact head/source revision, Lean version, manifest hash and all installed dependency revisions/clean flags. Run consistency validation against the exact reviewed verifier revision. Any final machine verdict must cite those actual bytes and the hosted run conclusion. No sibling reviewer reports or attestations were read.
