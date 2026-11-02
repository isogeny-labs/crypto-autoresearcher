# Scoped validation: modulus alias and canonical-range repair

Claim: `ATTACK-MOD-ALIAS-BOUNDED-REPAIR`. The reviewed theorem is `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair` in [proof PR #2942](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2942), producer head `288d5612b599501119f6c0d130a56241b7e2c9b4`, merged as `6471915dbbc5157c06586443f5c2971678a2b256`.

## Evidence and separate verdicts

| Dimension | Finding | Bound evidence |
| --- | --- | --- |
| Machine | `passed` | [GitHub Actions run 41363039408](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41363039408), `formal workspace (lake build + axiom audit)` success at PR head `288d561`; archived `machine/attack-mod-alias.json` reports `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, and no forbidden constructs. |
| Source fidelity | `faithful_scoped` | Independent `source-review.md` binds the frozen target and theorem source, including both strict bounds and the missing-import repair. |
| Blind mathematical check | `supports` | Independent `blind-review.md` derives the collision and injectivity and attacks weaker bound variants without reading producer code. |
| Combined technical review | `validated_scoped` | The three dimensions above jointly support only the exact natural-cast statement for `2 ≤ q`. This is a technical evidence verdict, not an official hypothesis or experiment status transition. |

The elaborated type in the machine audit is `(q : ℕ) (hq : 2 ≤ q) : 0 ≠ q ∧ 0 = ↑q ∧ ∀ (x y : ℕ), x < q → y < q → ↑x = ↑y → x = y`. The named theorem's transitive axiom list is `[propext, Quot.sound]`. The run checked 1,080 theorems with its standard-axiom policy; the downloaded formal artifact contains 103 individual `machine_verified` receipts. Four declared targets still had no theorem file in that run and are not counted as verified.

The receipt's `source_commit` is GitHub's PR merge tree `8ba7e88cf87c53e62249fe3480fdf0d8556aeb51`, with parents `b64dbdc58011992defdfb1c3c78ce6dc33917277` and producer head `288d5612b599501119f6c0d130a56241b7e2c9b4`. The final merge tree `6471915dbbc5157c06586443f5c2971678a2b256` has the same tracked bytes under `formal/**`, `orchestration/formal/**`, and `tools/verify_formal_targets.py` as that tested tree. The theorem blob SHA-256 in the receipt is `62ebbc6c75c51ba72bfb7bb64a4128527428e1d8ec71776ff9ccc71c66481bae`, matching the source review.

The installed dependency-pin records before and after the verifier are identical and report `passed: true`. Their recorded trust limit is Git source custody with Lean/Lake binary trust; this review did not run an independent binary or kernel rechecker. The machine receipt retains `semantic_review.status: pending` because the verifier does not perform semantic review; the two independent reports provide that separate assessment here. They do not establish a claim about a concrete circuit, encoding, proof system, exploit, or runtime cost.

## Archived hashes

| Artifact | SHA-256 |
| --- | --- |
| `machine/attack-mod-alias.json` | `b84f80c453e028177a1d556a6633fdbf960be147259f8b15e3c2e75d668cf50a` |
| `machine/dependency-pins-before.json` | `d8e465b733166a7c29f4c69969440aa86121ddc6638a270a87c6eb662359a3f2` |
| `machine/dependency-pins-after.json` | `d8e465b733166a7c29f4c69969440aa86121ddc6638a270a87c6eb662359a3f2` |
| `source-review.md` | `775bfd9eeeaae217459f9b5ad16ddec4f7bb0d6e4d14b9eba5576257b8195280` |
| `blind-review.md` | `21e24b885437483b7f5aff2f07b5eb932ac8ccc93e5b79429af8e244ba5f5dbb` |

The formal target remains `source_status: STATED`. An authorized Coordinator transition, if any, requires its own record; no target, hypothesis, experiment, or graph status is changed by this review.
