# Sheriff sweep SHF-20261106-a114e7

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: False
- started 2026-11-06T02:39:20.510946+00:00, finished 2026-11-06T02:41:41.093966+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `da442739db82` | `d39dfde801a8` | claude/sheriff-reaudit-20261106 | True | 1 | yes (44841) |
| crypto | `3a7a0f98af47` | `cb3a43d52a41` | main | True | 0 | yes (262790) |
| cryptanalysis | `5bdfb496df46` | `f327bb4d4ceb` | main | True | 0 | yes (10) |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 1 | 26 | 0 | 0 |
| B3 Lean and formal proofs | 13 | 34 | 185 | 207 | 0 |
| B7 provenance, integrity and reproducibility | 0 | 0 | 0 | 0 | 408 |
| B8 prose, papers and numbers | 0 | 0 | 0 | 880 | 22 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |

## Blockers (13)

- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/nested/Nested.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/tools/lean/Fixture.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/shared-gate/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/attribute-custom-axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/indented-dependency-axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/sorry/CryptoResearch/Test.lean:2`: `sorry`: the statement is assumed, not proved

## Major (35)

- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:coordination/formal-reviews/ncp-pr2417-20261031/reviews/TASK-20261031-4b6d61/raw/inputs/f4330e1a29feb8fdea9f1eab7131ae5cde2e2b6f/formal`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:coordination/formal-reviews/ncp-pr2417-20261031/reviews/TASK-20261031-8a54e2/raw/inputs`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/nested`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/runtime-sources/formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/cli/formal`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/shared-gate/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/attribute-custom-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/data-name`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/empty-project-audit`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/fake-project-evidence`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/indented-dependency-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/omitted-module-bad`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/omitted-module-good`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/positive`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/sorry`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/transitive-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/wrong-name`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.unpinned** (lead) `crypto-autoresearcher:analysis/rigorous-lfd-solving-20261105/affine-refutation/AffineFibreRefutation.lean`: 92 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **lean.no_axiom_audit** (lead) `cryptanalysis:verification/pqc-assay/lean`: standalone Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen

## Minor findings and leads (806 listed in sweep.json)

- `crypto-autoresearcher:lean.metaprogram`: 200
- `crypto:prose.strong_claim`: 200
- `cryptanalysis:prose.strong_claim`: 102
- `crypto-autoresearcher:prose.strong_claim`: 87
- `cryptanalysis:lean.no_ci`: 81
- `crypto-autoresearcher:lean.no_ci`: 73
- `crypto-autoresearcher:lean.vacuous`: 29
- `crypto-autoresearcher:zk.proof_language`: 22
- `crypto:lean.metaprogram`: 2
- `crypto:lean.no_ci`: 2
- `crypto:zk.proof_language`: 2
- `cryptanalysis:lean.native_decide`: 2
- `cryptanalysis:zk.proof_language`: 2
- `cryptanalysis:lean.axiom`: 1
- `cryptanalysis:lean.sorry`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
