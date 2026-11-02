# Adaptive batching formal review, 2026-11-02

## Scoped finding

The named Lean declaration `CryptoResearch.AttackCorpus.AdaptiveBatching.adaptive_rlc_cancellation` at proof head `8a9daca52daa3c121424bad54c0260cfaedb33b2` passed the hosted exact-merge workspace build and named verification. It proves (1) challenge-dependent cancellation `-ρ + ρ * 1 = 0` with a nonzero second error over every field, and (2) at most one cancelling challenge for a pair of coefficients fixed over a finite field and not both zero. This is the frozen scalar claim `ATTACK-BATCH-RLC-ADAPTIVE-CANCELLATION`, not a transcript or batching-protocol theorem.

| Dimension | Finding | Evidence |
| --- | --- | --- |
| Machine | `passed` on synthetic merge `4804be4e14a801ec1c27c95f6eec8d27ecec4530`, whose parents are main `63690685e9ea98bd84a9355dff44633f49fda381` and proof head `8a9daca52daa3c121424bad54c0260cfaedb33b2` | Hosted [run 41488317240](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41488317240); `attack-batch-rlc-adaptive.json`, SHA-256 `b3578ae3b13132337a79dd6300dce35e0ebe149814d59d9916c1aa330c5f19f4` |
| Named source | Theorem file SHA-256 `2d0526c1773dfdbcf348162a1df68cd2c7387ff596be6ab7c6292073a89ec76c`; frozen target SHA-256 `74c98067481b5a67087dffd1a3847ed02460c791468f8cfab4a5057d17c228a7` | Receipt provenance and source report agree |
| Axioms and pins | Named transitive axioms `[propext, Classical.choice, Quot.sound]`; 1,091 workspace theorems audited with standard axioms only; pre/post dependency pins byte-identical, SHA-256 `fb62d1952a368023bbf13dfb42f245d69e500693e11e5f631ed8a8a648e4caa7` | Named receipt, pin records, successful hosted job |
| Source fidelity | `faithful_scoped` for the two frozen field statements | Independent source report by `/root/mod_alias_source_review`, SHA-256 `30929b05a13e5920ad783f290dfcd0b1daaec7dc6791c19a050d8421fd1dd459` |
| Blind mathematics | Both field claims hold; zero pair, `F₂`, and `ZMod 4` boundary controls checked | Independent blind report by `/root/adaptive_blind_review`, SHA-256 `32fd23fd622f3b0800c79d362343de9da9a02648f48d28f43eec1c234aea89e7` |

The first producer head `4018237b567f1a565b3f7296c8c6175b3703cd2e` failed elaboration because the finite filter lacked a `DecidableEq` instance. The intermediate head `ce4e8b315cb5c2e4fce457f3699d4cec0d544d13` added that instance but had one missing `intro` binder; the source reviewer caught it. The final head above corrected both defects. Run 41488075988 at the intermediate head was canceled as stale. No failed head is represented as passing.

## Review process and controls

The review plan was written before dispatch and remains byte-identical at SHA-256 `399e4373e5a010728a87e8ac28b85b10d6daca9fd5e39243f6866645a44c4492`. Reviewer reports record their distinct actual reads and sibling-report exclusion. The first source reviewer hit a service usage limit before filing a report; a separate source reviewer completed the replacement review at the amended head. The blind reviewer read the statement and the permitted plan, and no producer proof or sibling report.

`python3 tools/check_review_independence.py --plan /var/tmp/adaptive-batching-review-plan-20261102.md --reports /var/tmp/adaptive-batching-source-review-20261102.md /var/tmp/adaptive-batching-blind-review-20261102.md` exited 2 with `/var/tmp/adaptive-batching-review-plan-20261102.md: no review_plan block`. The tool requires a structured YAML block, while this prewritten plan and the attestations are Markdown. This mechanical independence check is unresolved; its failure does not contradict the theorem's machine or mathematical results. A future round should use the structured plan and attestation contract from the outset rather than retroactively presenting a new YAML file as precommitted.

The zero pair has every field element as a root, so its exclusion matters. Over `ZMod 4`, the fixed nonzero pair `(2,2)` has two roots, so the field assumption matters for the repaired cardinality claim. Over `F₂`, the adaptive pair cancels for both challenges and each fixed nonzero pair has at most one root. These controls are mathematical derivations in the independent reports; they are not separately Lean-executed fixtures.

## Publication status and boundaries

The theorem PR [#2955](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2955) is open at the reviewed head. Its `harness-tests (1/4)` and aggregate `ledger-and-harness` checks failed on an existing DREG run supersession whose original manifest lacks canonical `run.id` and whose v2 replacement lacks an own-side pointer. Repair [PR #2973](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2973) proposes a new immutable v3 record and registry update. The theorem cannot be merged until all applicable current-head checks pass. This packet records machine `passed`, source fidelity `faithful_scoped`, and a release-review outcome of `needs_revision` while the CI and structured independence gates remain open. `source_status: STATED` and experiment/hypothesis statuses are unchanged.

The theorem contains no challenge distribution, binding commitment, Fiat–Shamir transcript, or protocol error-realizability model. The source's broader degree-`d` probability repair is outside this two-coefficient declaration. Lean/Lake dependency binaries were used at pinned versions but were not independently rechecked by a separate binary/kernel tool.

The adjacent `quantifier-boundary.svg` is the editable diagram source; `report.tex` embeds its PNG rendering. `report.pdf` was rendered as one page and visually inspected. `portfolio-inventory-4804be4e.json` records 108 frozen targets, 105 named source files, and 105 source/target byte pairs matching the exact hosted receipts on the tested merge; the three absent source files are the polynomial alias, Schnorr special-soundness, and subgroup-membership attack-corpus targets. This inventory does not supply independent semantic validation for the other targets. The earlier `portfolio-inventory-63690685.json` is retained as the pre-proof main snapshot.
