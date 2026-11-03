# Odd-torsion translation: independent formal review

Frozen source revision: `004355570fa983535696439b1781cb762dae3607`. Review plan: `b806841cef6ad73e80c5d49ca9a51845e5cf2eb6`. Target: `SCOPED-ODD-TORSION-TRANSLATION`, `ScopedObstructions.AdditiveModel.odd_translation_outside_kernel`.

## Checked result

The mathematical claim holds under the source's additive laws. If `r=k+k+1`, `rP=0`, and `T+T=0`, repeated-addition distributivity gives `r(P+T)=rP+rT=T`. When `T≠0`, the translated element lies outside the zero-kernel of multiplication by `r`. J1 derived this without the producer proof and supplied a nonvacuous `Z/6Z` model `(r,P,T)=(3,2,3)`, an even-scalar countermodel `(6,2,3)`, and a zero-`T` control `(3,2,0)`.

J2 checked the exact source note, target, and Lean file hashes. The source has **two data fields and four law fields** (`zero_add`, `add_zero`, `assoc`, `comm`); the frozen plan's phrase “five additive-law fields” was a counting error and is retained as such. The Lean `odd_translation` theorem supplies the equality; `odd_translation_outside_kernel` adds `T≠0` and supplies exclusion. Its assumptions are satisfiable in the XOR model. This fidelity verdict is scoped to abstract additive structures.

J3 independently downloaded hosted run `41494797344` and matched the named receipt SHA-256 `63419f85fb756ca00a9772fb5c7454a605aed73f53b1fad2b355de3c7ba15403`. The explicit Torsion module build, theorem type, and zero-axiom project audit passed at execution checkout `d0b766449942b04bf3316d005624b3ce83f0c5f4`. Complete six-file workspace and ten-file verifier input maps match that checkout, the frozen source revision, and the plan revision. Eleven hostile receipt mutations were rejected; a separately retrieved hosted control artifact reports 399 tests with zero errors, failures, or skips.

| Dimension | Current review finding |
| --- | --- |
| Machine evidence | **Passed for the archived named run and a fresh hosted formal run** on byte-identical reviewed source. Run `41718285530` completed successfully after the J3 freeze; its named receipt and metadata passed the coordinator's 19 exact checks in `fresh-hosted-41718285530/checks.json`. |
| Semantic fidelity | **faithful_scoped** for the conditional additive-law statement and its two conclusions. |
| Review outcome | **validated_scoped** for the conditional additive-law theorem and the exact source claim. The concrete curve and factor-base bridges remain outside this outcome. |
| Independent binary/kernel recheck | **not_verified**; the hosted runner and Lean binary remain within the trust boundary. |

J2's supplied older `2026-10-31` receipt was a different run and has SHA-256 `c4ae843196160e477aa13de229c825ca3cf15452baa02c3db1019c3f20adfb52`, not the frozen run's receipt. It was used only as a matching printed-type comparison, never as the pinned receipt. J2's attempted fresh direct Lean elaboration reached a 45-second timeout without a compiler diagnostic; this is recorded as `infrastructure_error`, not a theorem failure.

After the three reviewers froze their reports, the coordinator downloaded the newly completed formal artifact from [run 41718285530](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41718285530), artifact ID `13272842471`. Its odd-torsion receipt SHA-256 is `5246d01c4a35fea1896f6b40a182deef1859171b4916abc5256d899aacedb45e`. The task, target, theorem, toolchain/manifest hashes, complete six-file workspace map, and ten-file verifier map match the independently reviewed archived receipt; the new receipt's execution checkout is `62d80a49f59cc097acc4369a99034a853e9e4de8`, whose GitHub parents include PR #3007 head `53b7f9813c8037818d5db8b42df9eee5cd1e0f12`. Its named build and zero-axiom audit passed, the forbidden-construct list is empty, and pre/post dependency pin files are identical at SHA-256 `289330f9eaa7070f9091336059f7c031804dc452e16de96f7000a2d87b933a73`. `fresh-hosted-41718285530/check_fresh.py` passed all 19 recorded checks. This is a post-freeze coordinator supplement; it does not alter any independent reviewer report or claim an independent binary/kernel recheck.

## Review custody and remaining bridge

The three independent reports and original attestations are under `reviews/`. J1 read only `blind-statement.md`; J2 and J3 did not read sibling reports before freezing. The J1 attestation used a flat YAML shape. `normalize_j1_attestation.py` derives a checker-compatible wrapper from its sealed SHA-verified bytes and explicit blind-access flags, preserving the original file unchanged. The independence checker then passed for all three joints, blind derivation, and controls. This wrapper is a format adapter, not added reviewer evidence.

The source deliberately makes no concrete elliptic-curve, rational torsion, subgroup, factor-base membership, mixed-domain closure, or point-arithmetic claim. Those connections require separate refinement and closure proofs. The existing imported advisory claim keeps its prior status. This technical packet changes no official scientific decision. No performance quantity was measured or changed; the diagram `proof-boundary.svg` and inspected `report.pdf` show the proof and implementation boundary, while existing performance dashboard graphs remain unaffected.
